from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, List

from metrics_v01 import path_edges
from simulation_runner_v01 import run_simulation


NodePath = List[str]


def state_material(seed: str, policy: str, fragment_id: int, fractal_id: int = 36) -> str:
    """
    Derive deterministic state material for a simulated fragment.

    This is not cryptographic key material.
    It is only used as deterministic simulation input.
    """
    raw = f"{seed}:{policy}:{fragment_id}:{fractal_id}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def hamming_distance_hex(a: str, b: str) -> int:
    """
    Hamming distance between two equal-length hex strings at bit level.
    """
    if len(a) != len(b):
        raise ValueError("hex strings must have equal length")

    return sum(
        bin(int(x, 16) ^ int(y, 16)).count("1")
        for x, y in zip(a, b)
    )


def normalized_state_distance(a: str, b: str) -> float:
    """
    Return normalized bit distance between two state hex strings.
    """
    if not a and not b:
        return 0.0

    max_bits = len(a) * 4
    if max_bits == 0:
        return 0.0

    return hamming_distance_hex(a, b) / max_bits


def path_distance(path_a: NodePath, path_b: NodePath) -> float:
    """
    Return edge-based path distance.

    0.0 means identical edge set.
    1.0 means no shared edges.
    """
    edges_a = path_edges(path_a)
    edges_b = path_edges(path_b)

    if not edges_a and not edges_b:
        return 0.0

    union = edges_a | edges_b
    if not union:
        return 0.0

    shared = edges_a & edges_b
    return 1.0 - (len(shared) / len(union))


def pearson_correlation(xs: List[float], ys: List[float]) -> float:
    """
    Minimal Pearson correlation implementation.

    Returns 0.0 when variance is zero or sample size is too small.
    """
    if len(xs) != len(ys):
        raise ValueError("xs and ys must have same length")

    if len(xs) < 2:
        return 0.0

    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)

    dx = [x - mean_x for x in xs]
    dy = [y - mean_y for y in ys]

    var_x = sum(x * x for x in dx)
    var_y = sum(y * y for y in dy)

    if var_x == 0.0 or var_y == 0.0:
        return 0.0

    cov = sum(x * y for x, y in zip(dx, dy))
    return cov / math.sqrt(var_x * var_y)


def state_to_path_correlation(states: List[str], paths: List[NodePath]) -> float:
    """
    Compare pairwise state distances with pairwise path distances.
    """
    if len(states) != len(paths):
        raise ValueError("states and paths must have same length")

    state_distances: List[float] = []
    path_distances: List[float] = []

    for i in range(len(states)):
        for j in range(i + 1, len(states)):
            state_distances.append(normalized_state_distance(states[i], states[j]))
            path_distances.append(path_distance(paths[i], paths[j]))

    return pearson_correlation(state_distances, path_distances)


def lane_collapse_rate(paths: List[NodePath], collapse_threshold: float = 0.20) -> float:
    """
    Measure how often lanes collapse into very similar paths.

    A pair is considered collapsed if path_distance <= collapse_threshold.
    """
    if len(paths) < 2:
        return 0.0

    total_pairs = 0
    collapsed_pairs = 0

    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            total_pairs += 1
            if path_distance(paths[i], paths[j]) <= collapse_threshold:
                collapsed_pairs += 1

    return collapsed_pairs / total_pairs if total_pairs else 0.0


def analyze_state_mapping(config: Dict[str, Any], seed: str) -> Dict[str, Any]:
    """
    Analyze whether deterministic simulated state diversity maps to path diversity.

    In v0.8.0, state material does not yet influence path selection.
    Therefore this analysis is expected to be weak or inconclusive.

    For this diagnostic, route_count is doubled from the experiment default
    to increase the number of pairwise comparisons.
    """
    analysis_config = json.loads(json.dumps(config))
    original_route_count = int(analysis_config.get("policy", {}).get("route_count", 3))
    analysis_config.setdefault("policy", {})
    analysis_config["policy"]["route_count"] = original_route_count * 2

    result = run_simulation(analysis_config, seed)
    paths = result["paths"]
    policy = result["policy"]["type"]

    states = [
        state_material(seed=seed, policy=policy, fragment_id=i, fractal_id=result["policy"]["fractal_count"])
        for i in range(len(paths))
    ]

    pairwise = []
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            pairwise.append({
                "i": i,
                "j": j,
                "state_distance": normalized_state_distance(states[i], states[j]),
                "path_distance": path_distance(paths[i], paths[j]),
            })

    return {
        "schema_version": "0.8.0",
        "seed": seed,
        "policy": policy,
        "original_route_count": original_route_count,
        "analysis_route_count": result["policy"]["route_count"],
        "path_count": len(paths),
        "states": states,
        "paths": paths,
        "state_to_path_correlation": state_to_path_correlation(states, paths),
        "lane_collapse_rate": lane_collapse_rate(paths),
        "pairwise": pairwise,
        "limitations": [
            "state material does not yet influence path selection",
            "state-to-path correlation is diagnostic only",
            "lane collapse uses edge-distance threshold",
            "no security or resilience claim"
        ],
    }


def write_state_mapping_report(
    config_path: str,
    seeds: List[str],
    json_path: str,
    csv_path: str,
) -> None:
    config = json.loads(Path(config_path).read_text())

    analyses = [analyze_state_mapping(config, seed) for seed in seeds]

    json_out = Path(json_path)
    csv_out = Path(csv_path)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    csv_out.parent.mkdir(parents=True, exist_ok=True)

    json_out.write_text(json.dumps({
        "schema_version": "0.8.0",
        "analyses": analyses,
    }, indent=2, sort_keys=True))

    with csv_out.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "seed",
                "policy",
                "original_route_count",
                "analysis_route_count",
                "path_count",
                "state_to_path_correlation",
                "lane_collapse_rate",
            ],
        )
        writer.writeheader()
        for row in analyses:
            writer.writerow({
                "seed": row["seed"],
                "policy": row["policy"],
                "original_route_count": row["original_route_count"],
                "analysis_route_count": row["analysis_route_count"],
                "path_count": row["path_count"],
                "state_to_path_correlation": row["state_to_path_correlation"],
                "lane_collapse_rate": row["lane_collapse_rate"],
            })

    print(f"Wrote {json_out}")
    print(f"Wrote {csv_out}")


if __name__ == "__main__":
    write_state_mapping_report(
        config_path="experiments/example.json",
        seeds=["run-001", "run-002", "run-003"],
        json_path="outputs/state_mapping_report.json",
        csv_path="outputs/state_mapping_report.csv",
    )
