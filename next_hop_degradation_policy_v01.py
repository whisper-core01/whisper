"""
WHISPER v1.2.0 — Local Degradation-Aware Reselection.

This module implements relationship-scoped next-hop degradation scoring.

Scope:
- local selector-side degradation table
- directed next-hop relations: observer -> next_hop
- deterministic synthetic behavioral signal
- non-oracle: independent from compromise labels
- no gossip
- no distributed consensus
- no revocation
- no harassment detection

Key invariant:
v1.2.0 does not score degraded nodes.
It scores degraded next-hop relationships.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Tuple

from flv_node_score_policy_v01 import (
    NodeScoreTable,
    continuity_component,
    node_score_risk,
    path_node_score_safety,
)
from metrics_v01 import summarize_paths
from state_aware_policy_v01 import path_state_material


NodePath = List[str]
Relation = Tuple[str, str]
DegradationTable = Dict[Relation, float]


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def deterministic_unit_interval(*parts: str) -> float:
    """
    Deterministically map string parts to a float in [0.0, 1.0].
    """
    digest = hashlib.sha256("::".join(parts).encode("utf-8")).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def synthetic_behavioral_signal(observer: str, next_hop: str, seed: str) -> float:
    """
    Relationship-scoped synthetic behavioral signal.

    This does not use compromise labels.

    Components:
    - timeout risk
    - latency risk
    - forwarding failure risk
    """
    timeout_risk = deterministic_unit_interval(seed, observer, next_hop, "timeout")
    latency_risk = deterministic_unit_interval(seed, observer, next_hop, "latency")
    forwarding_failure_risk = deterministic_unit_interval(
        seed,
        observer,
        next_hop,
        "forwarding",
    )

    return clamp(
        0.40 * timeout_risk
        + 0.30 * latency_risk
        + 0.30 * forwarding_failure_risk
    )


def effective_degradation(
    observer: str,
    next_hop: str,
    node_scores: NodeScoreTable,
    seed: str,
) -> float:
    """
    Effective next-hop degradation for relation observer -> next_hop.

    effective_degradation =
      0.70 * synthetic_behavioral_signal(observer, next_hop)
    + 0.30 * node_score_risk(next_hop)

    Node-score risk reinforces the behavioral signal but does not dominate it.
    """
    behavioral = synthetic_behavioral_signal(observer, next_hop, seed)
    flv_risk = node_score_risk(node_scores.get(next_hop, 0.0))

    return clamp(0.70 * behavioral + 0.30 * flv_risk)


def build_degradation_table(
    candidates: List[NodePath],
    node_scores: NodeScoreTable,
    seed: str,
) -> DegradationTable:
    """
    Build relation-scoped degradation table for all directed edges in candidates.
    """
    table: DegradationTable = {}

    for path in candidates:
        for index in range(len(path) - 1):
            observer = path[index]
            next_hop = path[index + 1]
            relation = (observer, next_hop)

            if relation not in table:
                table[relation] = effective_degradation(
                    observer=observer,
                    next_hop=next_hop,
                    node_scores=node_scores,
                    seed=seed,
                )

    return table


def path_degradation_risk(
    path: NodePath,
    degradation_table: DegradationTable,
) -> float:
    """
    Mean degradation risk over directed next-hop relations in a path.

    Missing relations default to 0.0 degradation.
    """
    if len(path) < 2:
        return 0.0

    risks = []

    for index in range(len(path) - 1):
        relation = (path[index], path[index + 1])
        risks.append(degradation_table.get(relation, 0.0))

    return sum(risks) / len(risks)


def path_degradation_safety(
    path: NodePath,
    degradation_table: DegradationTable,
) -> float:
    return 1.0 - path_degradation_risk(path, degradation_table)


def path_health_component(
    path: NodePath,
    node_scores: NodeScoreTable,
    degradation_table: DegradationTable,
) -> float:
    """
    v1.2.0 path-health component.

    path_health_component =
      0.50 * node_score_safety
    + 0.50 * next_hop_degradation_safety
    """
    node_safety = path_node_score_safety(path, node_scores)
    degradation_safety = path_degradation_safety(path, degradation_table)

    return clamp(0.50 * node_safety + 0.50 * degradation_safety)


def score_degradation_aware_candidate(
    candidate_path: NodePath,
    candidate_state: str,
    selected_paths: List[NodePath],
    selected_states: List[str],
    pre_alarm_paths: List[NodePath],
    node_scores: NodeScoreTable,
    degradation_table: DegradationTable,
    delta: float,
) -> float:
    """
    v1.2.0 final score.

    final_score =
      delta * continuity_component
    + (1 - delta) * path_health_component
    """
    if not 0.0 <= delta <= 1.0:
        raise ValueError("delta must be in [0.0, 1.0]")

    continuity = continuity_component(
        candidate_path=candidate_path,
        candidate_state=candidate_state,
        selected_paths=selected_paths,
        selected_states=selected_states,
        pre_alarm_paths=pre_alarm_paths,
    )

    health = path_health_component(
        path=candidate_path,
        node_scores=node_scores,
        degradation_table=degradation_table,
    )

    return clamp(delta * continuity + (1.0 - delta) * health)


def select_degradation_aware_paths(
    candidates: List[NodePath],
    route_count: int,
    seed: str,
    pre_alarm_paths: List[NodePath],
    node_scores: NodeScoreTable,
    delta: float,
    fractal_id: int = 36,
) -> Dict[str, Any]:
    """
    Greedy v1.2.0 degradation-aware Lemonade reselection.

    Scoring is local to the selector. Relay nodes still only learn next hop.
    """
    if route_count < 1:
        raise ValueError("route_count must be >= 1")

    degradation_table = build_degradation_table(
        candidates=candidates,
        node_scores=node_scores,
        seed=seed,
    )

    if not candidates:
        return {
            "policy": "degradation_aware_lemonade_reset",
            "selected_paths": [],
            "selected_states": [],
            "scores": [],
            "degradation_table": degradation_table,
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

            score = score_degradation_aware_candidate(
                candidate_path=candidate,
                candidate_state=candidate_state,
                selected_paths=selected_paths,
                selected_states=selected_states,
                pre_alarm_paths=pre_alarm_paths,
                node_scores=node_scores,
                degradation_table=degradation_table,
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
        "policy": "degradation_aware_lemonade_reset",
        "selected_paths": selected_paths,
        "selected_states": selected_states,
        "scores": selected_scores,
        "degradation_table": degradation_table,
        "results": summarize_paths(selected_paths),
        "delta": delta,
    }


def mean_degradation_risk_per_path(
    paths: List[NodePath],
    degradation_table: DegradationTable,
) -> float:
    """
    Mean path degradation risk across selected paths.
    """
    if not paths:
        return 0.0

    values = [
        path_degradation_risk(path, degradation_table)
        for path in paths
    ]

    return sum(values) / len(values)


if __name__ == "__main__":
    candidates = [
        ["a", "b", "c"],
        ["a", "d", "c"],
        ["a", "e", "c"],
        ["a", "f", "c"],
    ]

    node_scores = {
        "a": 0.0,
        "b": 5.0,
        "c": 0.0,
        "d": 0.5,
        "e": 0.0,
        "f": -0.5,
    }

    result = select_degradation_aware_paths(
        candidates=candidates,
        route_count=2,
        seed="demo",
        pre_alarm_paths=[["a", "b", "c"]],
        node_scores=node_scores,
        delta=0.90,
        fractal_id=36,
    )

    print("Policy:", result["policy"])
    print("Delta:", result["delta"])
    print("Selected paths:", result["selected_paths"])
    print("Scores:", result["scores"])
    print("Mean degradation risk:", mean_degradation_risk_per_path(
        result["selected_paths"],
        result["degradation_table"],
    ))
