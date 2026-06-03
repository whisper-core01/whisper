from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List

from adversary_v01 import evaluate_policy_exposure, random_compromise
from baseline_v01 import random_multipath_baseline
from metrics_v01 import summarize_paths
from path_sampler_v01 import candidate_paths, select_source_target
from simulation_runner_v01 import run_simulation
from state_aware_policy_v01 import select_greedy_diverse
from state_mapping_v01 import lane_collapse_rate, state_to_path_correlation, state_material
from topology_v01 import generate_topology


NodePath = List[str]


def _state_correlation_for_paths(paths: List[NodePath], seed: str, policy: str, fractal_id: int) -> float:
    states = [
        state_material(seed=seed, policy=policy, fragment_id=i, fractal_id=fractal_id)
        for i in range(len(paths))
    ]

    return state_to_path_correlation(states, paths)


def compare_state_aware(config: Dict[str, Any], seed: str, compromise_fraction: float = 0.20) -> Dict[str, Any]:
    graph = generate_topology(config, seed)
    source, target = select_source_target(graph, f"{seed}:pair")

    policy = config.get("policy", {})
    route_count = int(policy.get("route_count", 3))
    fractal_id = int(policy.get("fractal_count", 36))

    candidate_pool_size = max(route_count * 4, 12)
    candidates = candidate_paths(
        graph=graph,
        source=source,
        target=target,
        seed=f"{seed}:state-aware-candidates",
        k=candidate_pool_size,
    )

    whisper = run_simulation(config, seed)
    random_multi = random_multipath_baseline(config, seed)
    state_aware = select_greedy_diverse(
        candidates=candidates,
        route_count=route_count,
        seed=seed,
        fractal_id=fractal_id,
        alpha=0.5,
        beta=0.5,
    )

    compromised = random_compromise(graph.node_count, compromise_fraction, seed)

    policies = [
        ("whisper_candidate_paths", whisper["paths"]),
        ("random_multipath", random_multi["paths"]),
        ("state_aware_whisper", state_aware["selected_paths"]),
    ]

    rows = []

    for policy_name, paths in policies:
        summary = summarize_paths(paths)
        exposure = evaluate_policy_exposure(paths, compromised)

        rows.append({
            "policy": policy_name,
            "path_count": summary["path_count"],
            "unique_path_ratio": summary["unique_path_ratio"],
            "path_overlap": summary["path_overlap"],
            "clean_path_ratio": exposure["clean_path_ratio"],
            "path_compromise_rate": exposure["path_compromise_rate"],
            "mean_compromised_nodes_per_path": exposure["mean_compromised_nodes_per_path"],
            "state_to_path_correlation": _state_correlation_for_paths(
                paths=paths,
                seed=seed,
                policy=policy_name,
                fractal_id=fractal_id,
            ),
            "lane_collapse_rate": lane_collapse_rate(paths),
        })

    return {
        "schema_version": "0.9.0",
        "seed": seed,
        "source": source,
        "target": target,
        "topology": {
            "type": graph.topology_type,
            "node_count": graph.node_count,
            "edge_count": graph.edge_count,
        },
        "compromise": {
            "type": "random_node_compromise",
            "compromise_fraction": compromise_fraction,
            "compromised_node_count": len(compromised),
        },
        "candidate_pool_size": len(candidates),
        "comparison": rows,
        "limitations": [
            "state-aware path selection is simulated",
            "state material is diagnostic and not cryptographic",
            "only random compromise is modeled",
            "only three seeds are reported",
            "no security or resilience claim"
        ],
    }


def write_state_aware_comparison(
    config_path: str,
    seeds: List[str],
    csv_path: str,
    json_path: str,
    compromise_fraction: float = 0.20,
) -> None:
    config = json.loads(Path(config_path).read_text())

    results = [
        compare_state_aware(config, seed, compromise_fraction=compromise_fraction)
        for seed in seeds
    ]

    csv_out = Path(csv_path)
    json_out = Path(json_path)
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    for result in results:
        for row in result["comparison"]:
            rows.append({
                "seed": result["seed"],
                "policy": row["policy"],
                "path_count": row["path_count"],
                "unique_path_ratio": row["unique_path_ratio"],
                "path_overlap": row["path_overlap"],
                "clean_path_ratio": row["clean_path_ratio"],
                "path_compromise_rate": row["path_compromise_rate"],
                "mean_compromised_nodes_per_path": row["mean_compromised_nodes_per_path"],
                "state_to_path_correlation": row["state_to_path_correlation"],
                "lane_collapse_rate": row["lane_collapse_rate"],
            })

    with csv_out.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "seed",
                "policy",
                "path_count",
                "unique_path_ratio",
                "path_overlap",
                "clean_path_ratio",
                "path_compromise_rate",
                "mean_compromised_nodes_per_path",
                "state_to_path_correlation",
                "lane_collapse_rate",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    json_out.write_text(json.dumps({
        "schema_version": "0.9.0",
        "results": results,
    }, indent=2, sort_keys=True))

    print(f"Wrote {csv_out}")
    print(f"Wrote {json_out}")


if __name__ == "__main__":
    write_state_aware_comparison(
        config_path="experiments/example.json",
        seeds=["run-001", "run-002", "run-003"],
        csv_path="outputs/state_aware_comparison.csv",
        json_path="outputs/state_aware_comparison.json",
        compromise_fraction=0.20,
    )
