from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from metrics_v01 import summarize_paths
from path_sampler_v01 import candidate_paths, select_source_target
from topology_v01 import TopologyGraph, generate_topology


def topology_to_dict(graph: TopologyGraph) -> Dict[str, Any]:
    return {
        "type": graph.topology_type,
        "node_count": graph.node_count,
        "edge_count": graph.edge_count,
        "nodes": graph.nodes,
        "edges": [{"source": a, "target": b} for a, b in graph.edges],
    }


def run_simulation(config: Dict[str, Any], seed: str) -> Dict[str, Any]:
    graph = generate_topology(config, seed)
    source, target = select_source_target(graph, f"{seed}:source-target")

    policy = config.get("policy", {})
    route_count = int(policy.get("route_count", 3))

    paths = candidate_paths(
        graph=graph,
        source=source,
        target=target,
        seed=f"{seed}:paths",
        k=route_count,
    )

    metrics = summarize_paths(paths)

    return {
        "schema_version": "0.6.0",
        "metadata": {
            "experiment_id": config.get("experiment_id", "unknown"),
            "seed": seed,
            "whisper_version": config.get("whisper_version", "v0.6.0"),
        },
        "topology": topology_to_dict(graph),
        "policy": {
            "type": policy.get("type", "whisper_structural_divergence"),
            "route_count": route_count,
            "fractal_count": int(policy.get("fractal_count", 36)),
        },
        "source_target": {
            "source": source,
            "target": target,
        },
        "paths": paths,
        "results": metrics,
        "limitations": [
            "v0.6.0 simulator has no adversary model",
            "v0.6.0 simulator has no state-to-path mapping",
            "v0.6.0 simulator has no baselines",
            "v0.6.0 metrics are preliminary and do not support security claims"
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="WHISPER v0.6.0 minimum viable simulator")
    parser.add_argument("--config", required=True, help="Path to experiment JSON config")
    parser.add_argument("--seed", required=True, help="Deterministic run seed")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    config_path = Path(args.config)
    output_path = Path(args.output)

    with config_path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    result = run_simulation(config, args.seed)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)

    print(f"Wrote {output_path}")
    print(f"topology: {result['topology']['type']}")
    print(f"nodes:    {result['topology']['node_count']}")
    print(f"edges:    {result['topology']['edge_count']}")
    print(f"paths:    {result['results']['path_count']}")
    print(f"unique:   {result['results']['unique_path_ratio']:.3f}")
    print(f"overlap:  {result['results']['path_overlap']:.3f}")


if __name__ == "__main__":
    main()
