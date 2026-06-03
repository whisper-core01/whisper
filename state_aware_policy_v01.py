from __future__ import annotations

import hashlib
from typing import List

from metrics_v01 import path_edges, summarize_paths
from state_mapping_v01 import normalized_state_distance, path_distance


NodePath = List[str]


def path_state_material(path: NodePath, index: int, seed: str, fractal_id: int = 36) -> str:
    """
    Derive deterministic simulated state material from path structure.

    This is not cryptographic key material.
    It is only used to test state-aware path selection.
    """
    edges = sorted(path_edges(path))
    edge_repr = "|".join(f"{a}->{b}" for a, b in edges)
    raw = f"{seed}:{fractal_id}:{index}:{edge_repr}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def mean_state_distance(candidate_state: str, selected_states: List[str]) -> float:
    if not selected_states:
        return 1.0

    return sum(
        normalized_state_distance(candidate_state, state)
        for state in selected_states
    ) / len(selected_states)


def mean_path_distance(candidate_path: NodePath, selected_paths: List[NodePath]) -> float:
    if not selected_paths:
        return 1.0

    return sum(
        path_distance(candidate_path, path)
        for path in selected_paths
    ) / len(selected_paths)


def score_candidate(
    candidate_path: NodePath,
    candidate_state: str,
    selected_paths: List[NodePath],
    selected_states: List[str],
    alpha: float = 0.5,
    beta: float = 0.5,
) -> float:
    """
    Hybrid WHISPER score.

    alpha weights state divergence.
    beta weights path divergence.
    """
    state_score = mean_state_distance(candidate_state, selected_states)
    path_score = mean_path_distance(candidate_path, selected_paths)

    return (alpha * state_score) + (beta * path_score)


def select_greedy_diverse(
    candidates: List[NodePath],
    route_count: int,
    seed: str,
    fractal_id: int = 36,
    alpha: float = 0.5,
    beta: float = 0.5,
) -> dict:
    """
    Greedy state-aware path selection.

    Selects paths that maximize combined state divergence and path divergence.
    """
    if route_count < 1:
        raise ValueError("route_count must be >= 1")

    if not candidates:
        return {
            "policy": "state_aware_whisper",
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

            score = score_candidate(
                candidate_path=candidate,
                candidate_state=candidate_state,
                selected_paths=selected_paths,
                selected_states=selected_states,
                alpha=alpha,
                beta=beta,
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
        "policy": "state_aware_whisper",
        "selected_paths": selected_paths,
        "selected_states": selected_states,
        "scores": scores,
        "results": summarize_paths(selected_paths),
        "parameters": {
            "route_count": route_count,
            "fractal_id": fractal_id,
            "alpha": alpha,
            "beta": beta,
        },
        "limitations": [
            "state-aware selection is simulated",
            "path_state_material is deterministic diagnostic material",
            "not cryptographic key material",
            "no security or resilience claim"
        ],
    }
