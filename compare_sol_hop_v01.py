"""
WHISPER v1.3.0b — Compare Sol-anchored hop-by-hop cascade strengths.

This comparator measures whether increasing directional cascade strength
improves delivery for the hop-by-hop fountain prototype.

Primary metrics:
- delivery_success_rate
- loop_rate
- mean_hop_count
- mean_path_overlap_vs_shortest_proxy

This is a routing-mechanics comparator, not an adversarial-security claim.
"""

from __future__ import annotations

import csv
import json
from collections import deque
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional

from compare_node_score_reset_v01 import build_pre_reset_flv_scores
from path_sampler_v01 import select_source_target
from sol_anchored_hop_policy_v01 import (
    graph_neighbors,
    path_overlap_ratio,
    route_sol_anchored_hop_by_hop,
)
from topology_v01 import generate_topology


DEFAULT_CASCADE_STRENGTHS = [0.0, 1.0, 2.0, 4.0]


def shortest_path_proxy(
    graph: Any,
    source: str,
    target: str,
    max_depth: int = 64,
) -> Optional[List[str]]:
    if source == target:
        return [source]

    q = deque([(source, [source])])
    visited = {source}

    while q:
        node, path = q.popleft()

        if len(path) > max_depth:
            continue

        for neighbor in graph_neighbors(graph, node):
            if neighbor in visited:
                continue

            new_path = path + [neighbor]
            if neighbor == target:
                return new_path

            visited.add(neighbor)
            q.append((neighbor, new_path))

    return None


def compare_sol_hop(
    config: Dict[str, Any],
    seed: str,
    cascade_strengths: List[float] | None = None,
    hop_budget: int = 12,
) -> Dict[str, Any]:
    if cascade_strengths is None:
        cascade_strengths = DEFAULT_CASCADE_STRENGTHS

    graph = generate_topology(config, seed)
    source, target = select_source_target(graph, f"{seed}:pair")

    policy_cfg = config.get("policy", {})
    route_count = int(policy_cfg.get("route_count", 3))
    fractal_id = int(policy_cfg.get("fractal_count", 36))

    flv = build_pre_reset_flv_scores(
        graph=graph,
        source=source,
        target=target,
        route_count=route_count,
        fractal_id=fractal_id,
        seed=seed,
        pre_reset_epochs=5,
    )

    shortest = shortest_path_proxy(graph, source, target)
    shortest_len = None if shortest is None else len(shortest) - 1

    rows = []

    for strength in cascade_strengths:
        result = route_sol_anchored_hop_by_hop(
            graph=graph,
            source=source,
            target=target,
            receiver_ephemeral_id=f"receiver:{target}:ephemeral",
            sol_id=f"sol:{seed}",
            epoch="1",
            session_nonce=f"nonce:{seed}",
            node_scores=flv["node_scores"],
            seed=f"{seed}:cascade:{strength}",
            hop_budget=hop_budget,
            use_directional_cascade=strength > 0.0,
            cascade_strength=strength,
        )

        overlap = (
            path_overlap_ratio(result["path"], shortest)
            if shortest is not None
            else 0.0
        )

        rows.append({
            "policy": "sol_anchored_hop_by_hop",
            "cascade_strength": strength,
            "delivered": result["delivered"],
            "hop_count": result["hop_count"],
            "hop_budget": result["hop_budget"],
            "loop_detected": result["loop_detected"],
            "path_len": len(result["path"]),
            "path_overlap_vs_shortest_proxy": overlap,
            "shortest_proxy_hops": shortest_len,
        })

    return {
        "schema_version": "1.3.0b",
        "experiment": "sol-anchored-hop-by-hop-cascade",
        "seed": seed,
        "source": source,
        "target": target,
        "hop_budget": hop_budget,
        "cascade_strengths": cascade_strengths,
        "shortest_proxy_path": shortest,
        "results": rows,
    }


def flatten_result(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []

    base = {
        "schema_version": result["schema_version"],
        "experiment": result["experiment"],
        "seed": result["seed"],
        "source": result["source"],
        "target": result["target"],
        "hop_budget": result["hop_budget"],
    }

    for row in result["results"]:
        item = dict(base)
        item.update(row)
        out.append(item)

    return out


def run_sol_hop_suite(
    config_path: str,
    seeds: List[str],
    cascade_strengths: List[float] | None = None,
    hop_budget: int = 12,
    csv_path: str = "outputs/compare_sol_hop_v01.csv",
    json_path: str = "outputs/compare_sol_hop_v01.json",
) -> None:
    config = json.loads(Path(config_path).read_text())

    if cascade_strengths is None:
        cascade_strengths = DEFAULT_CASCADE_STRENGTHS

    results = []
    rows = []

    for seed in seeds:
        result = compare_sol_hop(
            config=config,
            seed=seed,
            cascade_strengths=cascade_strengths,
            hop_budget=hop_budget,
        )
        results.append(result)
        rows.extend(flatten_result(result))

    csv_out = Path(csv_path)
    json_out = Path(json_path)
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.parent.mkdir(parents=True, exist_ok=True)

    if rows:
        with csv_out.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    json_out.write_text(json.dumps({
        "schema_version": "1.3.0b",
        "experiment": "sol-anchored-hop-by-hop-cascade",
        "results": results,
    }, indent=2, sort_keys=True))

    print(f"Wrote {csv_out}")
    print(f"Wrote {json_out}")
    print(f"Total seeds: {len(seeds)}")
    print(f"Total CSV rows: {len(rows)}")


if __name__ == "__main__":
    run_sol_hop_suite(
        config_path="experiments/example.json",
        seeds=["run-001", "run-002", "run-003"],
        cascade_strengths=DEFAULT_CASCADE_STRENGTHS,
        hop_budget=12,
    )
