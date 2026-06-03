from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from metrics_v01 import summarize_paths
from path_sampler_v01 import shortest_path
from simulation_runner_v01 import run_simulation
from topology_v01 import generate_topology


NodePath = List[str]


def single_path_baseline(config: Dict[str, Any], seed: str) -> Dict[str, Any]:
    """
    Minimal baseline: reuse the same shortest path route_count times.

    This is not Tor, not I2P, not a mixnet.
    It is a simple baseline to avoid comparing WHISPER to nothing.
    """
    graph = generate_topology(config, seed)

    whisper_result = run_simulation(config, seed)
    source = whisper_result["source_target"]["source"]
    target = whisper_result["source_target"]["target"]
    route_count = int(whisper_result["policy"]["route_count"])

    path = shortest_path(graph, source, target)
    paths: List[NodePath] = []

    if path is not None:
        paths = [path for _ in range(route_count)]

    return {
        "policy": "single_path",
        "seed": seed,
        "source": source,
        "target": target,
        "paths": paths,
        "results": summarize_paths(paths),
        "limitations": [
            "single_path is a minimal baseline",
            "not a Tor, I2P, mixnet, or libp2p model",
            "used only to compare against path diversity metrics"
        ],
    }


def compare_whisper_vs_single_path(config: Dict[str, Any], seed: str) -> Dict[str, Any]:
    whisper = run_simulation(config, seed)
    baseline = single_path_baseline(config, seed)

    return {
        "schema_version": "0.7.0",
        "experiment_id": config.get("experiment_id", "unknown"),
        "seed": seed,
        "comparison": [
            {
                "policy": "whisper_candidate_paths",
                "path_count": whisper["results"]["path_count"],
                "unique_path_ratio": whisper["results"]["unique_path_ratio"],
                "path_overlap": whisper["results"]["path_overlap"],
            },
            {
                "policy": "single_path",
                "path_count": baseline["results"]["path_count"],
                "unique_path_ratio": baseline["results"]["unique_path_ratio"],
                "path_overlap": baseline["results"]["path_overlap"],
            },
        ],
        "limitations": [
            "baseline comparison is preliminary",
            "single_path is intentionally minimal",
            "no adversary model",
            "no statistical significance claim",
            "no security or resilience claim"
        ],
    }


def write_baseline_comparison(config_path: str, seeds: list[str], csv_path: str, json_path: str) -> None:
    import csv

    config = json.loads(Path(config_path).read_text())

    rows = []
    comparisons = []

    for seed in seeds:
        result = compare_whisper_vs_single_path(config, seed)
        comparisons.append(result)

        for row in result["comparison"]:
            rows.append({
                "seed": seed,
                "policy": row["policy"],
                "path_count": row["path_count"],
                "unique_path_ratio": row["unique_path_ratio"],
                "path_overlap": row["path_overlap"],
            })

    csv_out = Path(csv_path)
    json_out = Path(json_path)
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.parent.mkdir(parents=True, exist_ok=True)

    with csv_out.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["seed", "policy", "path_count", "unique_path_ratio", "path_overlap"],
        )
        writer.writeheader()
        writer.writerows(rows)

    json_out.write_text(json.dumps({
        "schema_version": "0.7.0",
        "comparisons": comparisons,
    }, indent=2, sort_keys=True))

    print(f"Wrote {csv_out}")
    print(f"Wrote {json_out}")


if __name__ == "__main__":
    write_baseline_comparison(
        config_path="experiments/example.json",
        seeds=["run-001", "run-002", "run-003"],
        csv_path="outputs/baseline_comparison.csv",
        json_path="outputs/baseline_comparison.json",
    )
