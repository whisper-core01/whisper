from __future__ import annotations

import csv
import hashlib
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Set

from baseline_v01 import random_multipath_baseline, single_path_baseline
from simulation_runner_v01 import run_simulation
from topology_v01 import generate_topology


NodePath = List[str]


def random_compromise(node_count: int, compromise_fraction: float, seed: str) -> Set[str]:
    """
    Randomly compromise compromise_fraction of nodes.

    Deterministic given seed.
    """
    if node_count < 1:
        raise ValueError("node_count must be >= 1")

    if not 0.0 <= compromise_fraction <= 1.0:
        raise ValueError("compromise_fraction must be between 0.0 and 1.0")

    hash_base = hashlib.sha256(f"{seed}:compromise".encode()).hexdigest()
    rng_seed = int(hash_base[:16], 16)
    rng = random.Random(rng_seed)

    all_nodes = [f"n{i}" for i in range(node_count)]
    compromise_count = int(node_count * compromise_fraction)

    if compromise_fraction > 0.0:
        compromise_count = max(1, compromise_count)

    compromise_count = min(node_count, compromise_count)

    return set(rng.sample(all_nodes, compromise_count))


def evaluate_policy_exposure(paths: List[NodePath], compromised_nodes: Set[str]) -> Dict[str, Any]:
    """
    Measure how many paths touch compromised nodes.
    """
    path_count = len(paths)

    if path_count == 0:
        return {
            "path_count": 0,
            "compromised_path_count": 0,
            "path_compromise_rate": 0.0,
            "fully_compromised_count": 0,
            "fully_compromised_path_rate": 0.0,
            "mean_compromised_nodes_per_path": 0.0,
            "clean_path_ratio": 0.0,
        }

    touched = 0
    fully_compromised = 0
    compromised_node_hits = []

    for path in paths:
        path_nodes = set(path)
        compromised_in_path = path_nodes & compromised_nodes

        if compromised_in_path:
            touched += 1

        if path_nodes and path_nodes <= compromised_nodes:
            fully_compromised += 1

        compromised_node_hits.append(len(compromised_in_path))

    return {
        "path_count": path_count,
        "compromised_path_count": touched,
        "path_compromise_rate": touched / path_count,
        "fully_compromised_count": fully_compromised,
        "fully_compromised_path_rate": fully_compromised / path_count,
        "mean_compromised_nodes_per_path": sum(compromised_node_hits) / path_count,
        "clean_path_ratio": (path_count - touched) / path_count,
    }


def compare_under_adversary(
    config: Dict[str, Any],
    seed: str,
    compromise_fraction: float = 0.20,
) -> Dict[str, Any]:
    """
    Compare WHISPER, single-path, and random-multipath exposure
    under random node compromise.
    """
    graph = generate_topology(config, seed)
    compromised = random_compromise(graph.node_count, compromise_fraction, seed)

    whisper = run_simulation(config, seed)
    single = single_path_baseline(config, seed)
    random_multi = random_multipath_baseline(config, seed)

    policies = [
        ("whisper_candidate_paths", whisper["paths"]),
        ("single_path", single["paths"]),
        ("random_multipath", random_multi["paths"]),
    ]

    exposure_rows = []

    for policy, paths in policies:
        exposure = evaluate_policy_exposure(paths, compromised)
        exposure_rows.append({
            "policy": policy,
            **exposure,
        })

    return {
        "schema_version": "0.7.3",
        "experiment_id": config.get("experiment_id", "unknown"),
        "seed": seed,
        "topology": {
            "type": graph.topology_type,
            "node_count": graph.node_count,
            "edge_count": graph.edge_count,
        },
        "compromise": {
            "type": "random_node_compromise",
            "compromise_fraction": compromise_fraction,
            "compromised_node_count": len(compromised),
            "compromised_nodes": sorted(compromised),
        },
        "exposure": exposure_rows,
        "limitations": [
            "adversarial exposure is preliminary",
            "random compromise only, not targeted",
            "no active adversary behavior",
            "no state-to-path mapping",
            "no lane collapse model",
            "no security or resilience claim"
        ],
    }


def write_adversary_comparison(
    config_path: str,
    seeds: List[str],
    compromise_fraction: float,
    csv_path: str,
    json_path: str,
) -> None:
    config = json.loads(Path(config_path).read_text())

    results = []
    rows = []

    for seed in seeds:
        result = compare_under_adversary(
            config=config,
            seed=seed,
            compromise_fraction=compromise_fraction,
        )
        results.append(result)

        for row in result["exposure"]:
            rows.append({
                "seed": seed,
                "policy": row["policy"],
                "path_count": row["path_count"],
                "compromised_path_count": row["compromised_path_count"],
                "path_compromise_rate": row["path_compromise_rate"],
                "fully_compromised_count": row["fully_compromised_count"],
                "fully_compromised_path_rate": row["fully_compromised_path_rate"],
                "mean_compromised_nodes_per_path": row["mean_compromised_nodes_per_path"],
                "clean_path_ratio": row["clean_path_ratio"],
            })

    csv_out = Path(csv_path)
    json_out = Path(json_path)
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.parent.mkdir(parents=True, exist_ok=True)

    with csv_out.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "seed",
                "policy",
                "path_count",
                "compromised_path_count",
                "path_compromise_rate",
                "fully_compromised_count",
                "fully_compromised_path_rate",
                "mean_compromised_nodes_per_path",
                "clean_path_ratio",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    json_out.write_text(json.dumps({
        "schema_version": "0.7.3",
        "results": results,
    }, indent=2, sort_keys=True))

    print(f"Wrote {csv_out}")
    print(f"Wrote {json_out}")


if __name__ == "__main__":
    write_adversary_comparison(
        config_path="experiments/example.json",
        seeds=["run-001", "run-002", "run-003"],
        compromise_fraction=0.20,
        csv_path="outputs/adversary_comparison.csv",
        json_path="outputs/adversary_comparison.json",
    )
