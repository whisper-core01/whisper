"""
WHISPER v1.0.0: Lemonade-triggered continuity break policy.

Implements three reset-based path selection policies:
1. random_multipath_reset
2. state_aware_reset
3. lemonade_reset (state + path + pre_alarm_distance)

Tests whether post-reset path selection reduces continuity with pre-alarm paths.
"""

from __future__ import annotations

from typing import Dict, List

from metrics_v01 import path_edges, summarize_paths
from state_mapping_v01 import normalized_state_distance, path_distance
from state_aware_policy_v01 import path_state_material


NodePath = List[str]


def mean_path_distance_to_set(candidate: NodePath, path_set: List[NodePath]) -> float:
    """
    Mean distance from candidate to all paths in set.
    
    Used for pre_alarm_avoidance metric.
    """
    if not path_set:
        return 1.0
    
    distances = [path_distance(candidate, p) for p in path_set]
    return sum(distances) / len(distances)


def score_lemonade_reset_candidate(
    candidate_path: NodePath,
    candidate_state: str,
    selected_paths: List[NodePath],
    selected_states: List[str],
    pre_alarm_paths: List[NodePath],
    alpha: float = 0.35,
    beta: float = 0.35,
    gamma: float = 0.30,
) -> float:
    """
    Lemonade-reset hybrid score.
    
    score = alpha * state_divergence
          + beta * path_divergence
          + gamma * pre_alarm_path_distance
    
    All three components maximize divergence.
    """
    from state_aware_policy_v01 import (
        mean_path_distance,
        mean_state_distance,
    )
    
    state_score = mean_state_distance(candidate_state, selected_states) if selected_states else 1.0
    path_score = mean_path_distance(candidate_path, selected_paths) if selected_paths else 1.0
    pre_alarm_score = mean_path_distance_to_set(candidate_path, pre_alarm_paths) if pre_alarm_paths else 1.0
    
    return (alpha * state_score) + (beta * path_score) + (gamma * pre_alarm_score)


def select_lemonade_reset_paths(
    candidates: List[NodePath],
    route_count: int,
    seed: str,
    pre_alarm_paths: List[NodePath],
    fractal_id: int = 36,
    alpha: float = 0.35,
    beta: float = 0.35,
    gamma: float = 0.30,
) -> Dict:
    """
    Greedy lemonade_reset path selection.
    
    Selects paths that maximize state divergence, path divergence, 
    and distance from pre-alarm paths.
    """
    if route_count < 1:
        raise ValueError("route_count must be >= 1")
    
    if not candidates:
        return {
            "policy": "lemonade_reset",
            "selected_paths": [],
            "selected_states": [],
            "scores": [],
            "results": summarize_paths([]),
        }
    
    remaining = list(candidates)
    selected_paths: List[NodePath] = []
    selected_states: List[str] = []
    scores = []
    
    while remaining and len(selected_paths) < route_count:
        best_idx = 0
        best_score = -1.0
        best_state = ""
        
        for idx, candidate in enumerate(remaining):
            candidate_state = path_state_material(
                path=candidate,
                index=idx,
                seed=seed,
                fractal_id=fractal_id,
            )
            
            score = score_lemonade_reset_candidate(
                candidate_path=candidate,
                candidate_state=candidate_state,
                selected_paths=selected_paths,
                selected_states=selected_states,
                pre_alarm_paths=pre_alarm_paths,
                alpha=alpha,
                beta=beta,
                gamma=gamma,
            )
            
            if score > best_score:
                best_score = score
                best_idx = idx
                best_state = candidate_state
        
        selected = remaining.pop(best_idx)
        selected_paths.append(selected)
        selected_states.append(best_state)
        scores.append(best_score)
    
    return {
        "policy": "lemonade_reset",
        "selected_paths": selected_paths,
        "selected_states": selected_states,
        "scores": scores,
        "results": summarize_paths(selected_paths),
        "parameters": {
            "route_count": route_count,
            "fractal_id": fractal_id,
            "alpha": alpha,
            "beta": beta,
            "gamma": gamma,
        },
    }


def state_break_distance(
    pre_alarm_states: List[str],
    post_reset_states: List[str],
) -> float:
    """
    Measure state continuity break.
    
    state_break_distance = mean(normalized_hamming_distance(pre[i], post[i]))
    
    Range: [0, 1], where 1.0 = completely different.
    """
    if not pre_alarm_states or not post_reset_states:
        return 0.0
    
    if len(pre_alarm_states) != len(post_reset_states):
        raise ValueError("State count mismatch: pre-alarm vs post-reset")
    
    distances = [
        normalized_state_distance(pre_alarm_states[i], post_reset_states[i])
        for i in range(len(pre_alarm_states))
    ]
    
    return sum(distances) / len(distances)


def post_reset_path_distance_from_pre_alarm(
    post_reset_paths: List[NodePath],
    pre_alarm_paths: List[NodePath],
) -> float:
    """
    Measure path continuity break.
    
    post_reset_path_distance_from_pre_alarm = 
      mean(min_distance(post_path_i, pre_alarm_paths))
    
    For each post-reset path, find distance to nearest pre-alarm path.
    Then take mean across all post-reset paths.
    
    Higher = more distant = more broken continuity.
    """
    if not post_reset_paths or not pre_alarm_paths:
        return 0.0
    
    distances = []
    for post_path in post_reset_paths:
        min_dist = min(path_distance(post_path, pre_path) for pre_path in pre_alarm_paths)
        distances.append(min_dist)
    
    return sum(distances) / len(distances)


if __name__ == "__main__":
    # Quick smoke test
    test_candidates = [
        ["a", "b", "c"],
        ["a", "d", "c"],
        ["a", "e", "c"],
    ]
    test_pre_alarm = [["a", "b", "c"], ["a", "f", "c"]]
    
    result = select_lemonade_reset_paths(
        candidates=test_candidates,
        route_count=2,
        seed="test",
        pre_alarm_paths=test_pre_alarm,
    )
    
    print(f"Policy: {result['policy']}")
    print(f"Selected paths: {result['selected_paths']}")
    print(f"Scores: {result['scores']}")
    print(f"Results: {result['results']}")
