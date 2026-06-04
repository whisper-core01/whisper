"""
WHISPER v1.1.0 — Local FLV node-score-aware path selection.

This module implements the deterministic synthetic FLV load model and
node-score-aware Lemonade reselection policy.

Scope:
- local selector-side FLV only
- no distributed consensus
- no gossip
- no harassment detection
- no revocation ladder
- no oracle compromise knowledge

Node score is a local load/homeostasis signal, not a trust score and not
a compromise indicator.
"""

from __future__ import annotations

from typing import Dict, List, Any

from lemonade_reset_policy_v01 import mean_path_distance_to_set
from metrics_v01 import summarize_paths
from state_aware_policy_v01 import path_state_material
from state_mapping_v01 import normalized_state_distance, path_distance


NodePath = List[str]
NodeScoreTable = Dict[str, float]


MIN_NODE_SCORE = -1.0
MAX_NODE_SCORE = 5.0

HEALTHY_MIN = 0.0
HEALTHY_MAX = 1.0

DEFAULT_PRE_RESET_EPOCHS = 5
DEFAULT_SELECTED_INCREMENT = 0.5
DEFAULT_INACTIVE_DECAY = 0.1


def clamp(value: float, lower: float, upper: float) -> float:
    """
    Clamp value into [lower, upper].
    """
    return max(lower, min(upper, value))


def node_score_risk(score: float) -> float:
    """
    Convert a FLV node score into risk.

    Bands:
    - watch zone: -1.0 <= score < 0.0
    - healthy:     0.0 <= score <= 1.0
    - loaded:      1.0 < score <= 3.0
    - overloaded:  3.0 < score <= 5.0

    Risk:
    - negative scores are risk proportional to abs(score)
    - healthy band has risk 0.0
    - positive load above 1.0 scales to 1.0 at score 5.0
    """
    score = clamp(score, MIN_NODE_SCORE, MAX_NODE_SCORE)

    if score < 0.0:
        return clamp(abs(score), 0.0, 1.0)

    if 0.0 <= score <= 1.0:
        return 0.0

    return clamp((score - 1.0) / 4.0, 0.0, 1.0)


def node_score_safety(score: float) -> float:
    """
    Safety is inverse risk.
    """
    return 1.0 - node_score_risk(score)


def path_node_score_risk(path: NodePath, node_scores: NodeScoreTable) -> float:
    """
    Mean node-score risk over a path.

    Missing nodes default to 0.0, the neutral initial score.
    """
    if not path:
        return 1.0

    values = [
        node_score_risk(node_scores.get(node, 0.0))
        for node in path
    ]

    return sum(values) / len(values)


def path_node_score_safety(path: NodePath, node_scores: NodeScoreTable) -> float:
    """
    Mean node-score safety over a path.
    """
    return 1.0 - path_node_score_risk(path, node_scores)


def mean_state_distance(candidate_state: str, selected_states: List[str]) -> float:
    """
    Mean normalized state distance from already selected states.

    Empty selected set returns 1.0 to allow the first candidate.
    """
    if not selected_states:
        return 1.0

    values = [
        normalized_state_distance(candidate_state, state)
        for state in selected_states
    ]

    return sum(values) / len(values)


def mean_path_distance(candidate_path: NodePath, selected_paths: List[NodePath]) -> float:
    """
    Mean path distance from already selected paths.

    Empty selected set returns 1.0 to allow the first candidate.
    """
    if not selected_paths:
        return 1.0

    values = [
        path_distance(candidate_path, path)
        for path in selected_paths
    ]

    return sum(values) / len(values)


def continuity_component(
    candidate_path: NodePath,
    candidate_state: str,
    selected_paths: List[NodePath],
    selected_states: List[str],
    pre_alarm_paths: List[NodePath],
) -> float:
    """
    Continuity-break component used by v1.1.0.

    0.40 * pre_alarm_path_distance
    0.30 * state_divergence
    0.30 * path_divergence
    """
    pre_alarm_distance = mean_path_distance_to_set(candidate_path, pre_alarm_paths)
    state_divergence = mean_state_distance(candidate_state, selected_states)
    path_divergence = mean_path_distance(candidate_path, selected_paths)

    return (
        0.40 * pre_alarm_distance
        + 0.30 * state_divergence
        + 0.30 * path_divergence
    )


def score_node_score_aware_candidate(
    candidate_path: NodePath,
    candidate_state: str,
    selected_paths: List[NodePath],
    selected_states: List[str],
    pre_alarm_paths: List[NodePath],
    node_scores: NodeScoreTable,
    delta: float,
) -> float:
    """
    Score candidate using continuity break and local FLV node-score safety.

    final_score =
      delta * continuity_component
    + (1 - delta) * node_score_safety
    """
    if not 0.0 <= delta <= 1.0:
        raise ValueError("delta must be in [0.0, 1.0]")

    c = continuity_component(
        candidate_path=candidate_path,
        candidate_state=candidate_state,
        selected_paths=selected_paths,
        selected_states=selected_states,
        pre_alarm_paths=pre_alarm_paths,
    )

    safety = path_node_score_safety(candidate_path, node_scores)

    return clamp(delta * c + (1.0 - delta) * safety, 0.0, 1.0)


def generate_synthetic_flv_scores(
    all_nodes: List[str],
    selected_paths_by_epoch: List[List[NodePath]],
    selected_increment: float = DEFAULT_SELECTED_INCREMENT,
    inactive_decay: float = DEFAULT_INACTIVE_DECAY,
    min_score: float = MIN_NODE_SCORE,
    max_score: float = MAX_NODE_SCORE,
) -> NodeScoreTable:
    """
    Generate deterministic synthetic FLV scores from pre-reset path usage.

    All nodes start at score 0.0.

    For each epoch:
    - each node appearing in selected paths receives +selected_increment
    - each node not appearing in selected paths receives -inactive_decay
    - scores are clamped to [min_score, max_score]

    The caller supplies selected_paths_by_epoch, so determinism comes from
    the deterministic pre-reset path selection process.
    """
    scores: NodeScoreTable = {node: 0.0 for node in all_nodes}

    for epoch_paths in selected_paths_by_epoch:
        active_nodes = set()
        for path in epoch_paths:
            active_nodes.update(path)

        for node in all_nodes:
            if node in active_nodes:
                scores[node] = clamp(
                    scores[node] + selected_increment,
                    min_score,
                    max_score,
                )
            else:
                scores[node] = clamp(
                    scores[node] - inactive_decay,
                    min_score,
                    max_score,
                )

    return scores


def select_node_score_aware_paths(
    candidates: List[NodePath],
    route_count: int,
    seed: str,
    pre_alarm_paths: List[NodePath],
    node_scores: NodeScoreTable,
    delta: float,
    fractal_id: int = 36,
) -> Dict[str, Any]:
    """
    Greedy node-score-aware Lemonade reselection.

    The first selected candidate is the best according to:
    - continuity against pre-alarm paths
    - state/path divergence against already selected paths
    - local FLV node-score safety

    Relay nodes do not receive global path knowledge. This policy is a
    selector-side candidate evaluation mechanism.
    """
    if route_count < 1:
        raise ValueError("route_count must be >= 1")

    if not candidates:
        return {
            "policy": "node_score_aware_lemonade_reset",
            "selected_paths": [],
            "selected_states": [],
            "scores": [],
            "results": summarize_paths([]),
            "delta": delta,
        }

    selected_paths: List[NodePath] = []
    selected_states: List[str] = []
    selected_scores: List[float] = []
    remaining = list(candidates)

    while remaining and len(selected_paths) < route_count:
        best_index = 0
        best_score = -1.0
        best_state = ""

        for index, candidate in enumerate(remaining):
            candidate_state = path_state_material(
                path=candidate,
                index=len(selected_paths),
                seed=seed,
                fractal_id=fractal_id,
            )

            score = score_node_score_aware_candidate(
                candidate_path=candidate,
                candidate_state=candidate_state,
                selected_paths=selected_paths,
                selected_states=selected_states,
                pre_alarm_paths=pre_alarm_paths,
                node_scores=node_scores,
                delta=delta,
            )

            if score > best_score:
                best_index = index
                best_score = score
                best_state = candidate_state

        selected = remaining.pop(best_index)
        selected_paths.append(selected)
        selected_states.append(best_state)
        selected_scores.append(best_score)

    return {
        "policy": "node_score_aware_lemonade_reset",
        "selected_paths": selected_paths,
        "selected_states": selected_states,
        "scores": selected_scores,
        "results": summarize_paths(selected_paths),
        "delta": delta,
    }


def mean_node_score_risk_per_path(paths: List[NodePath], node_scores: NodeScoreTable) -> float:
    """
    Mean path_node_score_risk across selected paths.
    """
    if not paths:
        return 1.0

    values = [
        path_node_score_risk(path, node_scores)
        for path in paths
    ]

    return sum(values) / len(values)


def mean_raw_node_score_per_path(paths: List[NodePath], node_scores: NodeScoreTable) -> float:
    """
    Mean raw node score across selected paths.
    """
    nodes = []
    for path in paths:
        nodes.extend(path)

    if not nodes:
        return 0.0

    return sum(node_scores.get(node, 0.0) for node in nodes) / len(nodes)


def healthy_node_ratio(paths: List[NodePath], node_scores: NodeScoreTable) -> float:
    """
    Fraction of path node occurrences in healthy band [0.0, 1.0].
    """
    nodes = []
    for path in paths:
        nodes.extend(path)

    if not nodes:
        return 0.0

    healthy = 0
    for node in nodes:
        score = node_scores.get(node, 0.0)
        if 0.0 <= score <= 1.0:
            healthy += 1

    return healthy / len(nodes)


if __name__ == "__main__":
    candidates = [
        ["a", "b", "c"],
        ["a", "d", "c"],
        ["a", "e", "c"],
        ["a", "f", "c"],
    ]

    pre_alarm_paths = [["a", "b", "c"]]

    all_nodes = ["a", "b", "c", "d", "e", "f"]
    selected_by_epoch = [
        [["a", "b", "c"]],
        [["a", "b", "c"]],
        [["a", "d", "c"]],
        [["a", "e", "c"]],
        [["a", "f", "c"]],
    ]

    scores = generate_synthetic_flv_scores(all_nodes, selected_by_epoch)

    result = select_node_score_aware_paths(
        candidates=candidates,
        route_count=2,
        seed="demo",
        pre_alarm_paths=pre_alarm_paths,
        node_scores=scores,
        delta=0.75,
    )

    print("Policy:", result["policy"])
    print("Delta:", result["delta"])
    print("Node scores:", scores)
    print("Selected paths:", result["selected_paths"])
    print("Scores:", result["scores"])
    print("Mean node score risk:", mean_node_score_risk_per_path(result["selected_paths"], scores))
