"""
WHISPER v1.3.1 — Compare Sol-link magnet vs pressure field.

Compares:
- v1.3.0 sol_link_magnetic_hop_by_hop
- v1.3.1 sol_link_pressure_hop_by_hop

The goal is to test whether the pressure field improves routing stability:
- better transport delivery ratio
- fewer loops
- fewer dead ends
- lower relay reuse
- lower exposure
- same layer blindness invariants
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Set, Tuple

from compare_sol_link_magnetic_v01 import (
    DEFAULT_CONDITIONS,
    build_degradation_scores,
    build_known_neighbors,
    build_logical_relays,
    build_node_scores,
    compromised_nodes_for_condition,
    evaluate_path_exposure,
    graph_nodes,
)
from sol_link_magnetic_policy_v01 import (
    route_sol_link_magnetic_hop_by_hop,
    deterministic_unit_interval,
)
from sol_link_pressure_policy_v01 import route_sol_link_pressure_hop_by_hop
from topology_v01 import generate_topology


DEFAULT_MAGNET_STRENGTHS = [4.0, 6.0, 8.0]
DEFAULT_WANDERING_STRENGTHS = [0.5, 1.0, 2.0]


def _source_for_seed(nodes: List[str], seed: str) -> str:
    return nodes[int(deterministic_unit_interval(seed, "source") * len(nodes)) % len(nodes)]


def _magnetic_metrics(
    result: Dict[str, Any],
    compromised: Set[str],
) -> Dict[str, Any]:
    transport_results = result["transport_results"]
    attempts = len(transport_results)
    successes = sum(1 for item in transport_results if item["delivered"])
    failures = attempts - successes

    exposure = evaluate_path_exposure(result["path"], compromised)

    return {
        "policy": "v1.3.0_magnet_raw",
        "transport_attempts": attempts,
        "successful_transport_attempts": successes,
        "transport_failures": failures,
        "transport_delivery_ratio": successes / attempts if attempts else 0.0,
        "transport_success": attempts > 0 and successes == attempts,
        "loop_detected": result["loop_detected"],
        "dead_end": False,
        "relay_reuse_count": len(result["path"]) - len(set(result["path"])),
        "mean_candidate_count": None,
        "hop_count": result["hop_count"],
        "path_len": len(result["path"]),
        "compromised_relays": exposure["compromised_relays"],
        "clean_path": exposure["clean_path"],
        "path_compromise_rate": exposure["compromise_rate"],
        "reticulum_graph_visible": result["reticulum_graph_visible"],
        "voxmesh_knows_reticulum_identity": result["voxmesh_knows_reticulum_identity"],
        "reticulum_knows_whisper_payload": result["reticulum_knows_whisper_payload"],
    }


def _pressure_metrics(
    result: Dict[str, Any],
    compromised: Set[str],
) -> Dict[str, Any]:
    exposure = evaluate_path_exposure(result["path"], compromised)

    return {
        "policy": "v1.3.1_pressure_field",
        "transport_attempts": result["transport_attempts"],
        "successful_transport_attempts": result["successful_transport_attempts"],
        "transport_failures": result["transport_attempts"] - result["successful_transport_attempts"],
        "transport_delivery_ratio": result["transport_delivery_ratio"],
        "transport_success": result["transport_success"],
        "loop_detected": result["loop_detected"],
        "dead_end": result["dead_end"],
        "relay_reuse_count": result["relay_reuse_count"],
        "mean_candidate_count": result["mean_candidate_count"],
        "hop_count": result["hop_count"],
        "path_len": len(result["path"]),
        "compromised_relays": exposure["compromised_relays"],
        "clean_path": exposure["clean_path"],
        "path_compromise_rate": exposure["compromise_rate"],
        "reticulum_graph_visible": result["reticulum_graph_visible"],
        "voxmesh_knows_reticulum_identity": result["voxmesh_knows_reticulum_identity"],
        "reticulum_knows_whisper_payload": result["reticulum_knows_whisper_payload"],
    }


def compare_sol_link_pressure(
    config: Dict[str, Any],
    seed: str,
    condition: str = "random",
    compromise_fraction: float = 0.20,
    magnet_strengths: List[float] | None = None,
    wandering_strengths: List[float] | None = None,
    hop_budget: int = 12,
) -> Dict[str, Any]:
    if magnet_strengths is None:
        magnet_strengths = DEFAULT_MAGNET_STRENGTHS

    if wandering_strengths is None:
        wandering_strengths = DEFAULT_WANDERING_STRENGTHS

    graph = generate_topology(config, seed)
    nodes = graph_nodes(graph)
    known_neighbors = build_known_neighbors(graph)
    relays = build_logical_relays(nodes, condition, seed)

    source = _source_for_seed(nodes, seed)

    compromised = compromised_nodes_for_condition(
        nodes=nodes,
        known_neighbors=known_neighbors,
        condition=condition,
        fraction=compromise_fraction,
        seed=seed,
    )

    node_scores = build_node_scores(nodes, seed)
    degradation_scores = build_degradation_scores(known_neighbors, condition, seed)

    rows = []

    for magnet_strength in magnet_strengths:
        magnetic = route_sol_link_magnetic_hop_by_hop(
            source_relay=source,
            relays=relays,
            known_neighbors=known_neighbors,
            local_ephemeral_material=f"local:{seed}",
            remote_ephemeral_material=f"remote:{seed}",
            sol_id=f"sol:{seed}",
            epoch="1",
            session_nonce=f"nonce:{seed}",
            opaque_whisper_capsule=f"opaque-whisper-fragment:{seed}",
            node_scores=node_scores,
            degradation_scores=degradation_scores,
            seed=f"{seed}:magnetic:{magnet_strength}",
            hop_budget=hop_budget,
            magnet_strength=magnet_strength,
        )

        row = _magnetic_metrics(magnetic, compromised)
        row["magnet_strength"] = magnet_strength
        row["wandering_strength"] = None
        rows.append(row)

        for wandering_strength in wandering_strengths:
            pressure = route_sol_link_pressure_hop_by_hop(
                source_relay=source,
                relays=relays,
                known_neighbors=known_neighbors,
                local_ephemeral_material=f"local:{seed}",
                remote_ephemeral_material=f"remote:{seed}",
                sol_id=f"sol:{seed}",
                epoch="1",
                session_nonce=f"nonce:{seed}",
                opaque_whisper_capsule=f"opaque-whisper-fragment:{seed}",
                node_scores=node_scores,
                degradation_scores=degradation_scores,
                seed=f"{seed}:pressure:{magnet_strength}:{wandering_strength}",
                hop_budget=hop_budget,
                magnet_strength=magnet_strength,
                wandering_strength=wandering_strength,
            )

            row = _pressure_metrics(pressure, compromised)
            row["magnet_strength"] = magnet_strength
            row["wandering_strength"] = wandering_strength
            rows.append(row)

    return {
        "schema_version": "1.3.1",
        "experiment": "sol-link-pressure-field-comparison",
        "seed": seed,
        "condition": condition,
        "compromise_fraction": compromise_fraction,
        "node_count": len(nodes),
        "known_logical_edge_count": sum(len(v) for v in known_neighbors.values()),
        "compromised_node_count": len(compromised),
        "source_relay": source,
        "hop_budget": hop_budget,
        "magnet_strengths": magnet_strengths,
        "wandering_strengths": wandering_strengths,
        "results": rows,
        "invariants": {
            "reticulum_graph_visible": False,
            "voxmesh_knows_reticulum_identity": False,
            "reticulum_knows_whisper_payload": False,
        },
    }


def flatten_result(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    base = {
        "schema_version": result["schema_version"],
        "experiment": result["experiment"],
        "seed": result["seed"],
        "condition": result["condition"],
        "compromise_fraction": result["compromise_fraction"],
        "node_count": result["node_count"],
        "known_logical_edge_count": result["known_logical_edge_count"],
        "compromised_node_count": result["compromised_node_count"],
        "source_relay": result["source_relay"],
        "hop_budget": result["hop_budget"],
    }

    rows = []

    for row in result["results"]:
        out = dict(base)
        out.update(row)
        rows.append(out)

    return rows


def run_sol_link_pressure_suite(
    config_path: str,
    seeds: List[str],
    conditions: List[str] | None = None,
    compromise_fractions: List[float] | None = None,
    magnet_strengths: List[float] | None = None,
    wandering_strengths: List[float] | None = None,
    hop_budget: int = 12,
    csv_path: str = "outputs/compare_sol_link_pressure_v01.csv",
    json_path: str = "outputs/compare_sol_link_pressure_v01.json",
) -> None:
    config = json.loads(Path(config_path).read_text())

    if conditions is None:
        conditions = DEFAULT_CONDITIONS

    if compromise_fractions is None:
        compromise_fractions = [0.20]

    if magnet_strengths is None:
        magnet_strengths = DEFAULT_MAGNET_STRENGTHS

    if wandering_strengths is None:
        wandering_strengths = DEFAULT_WANDERING_STRENGTHS

    results = []
    rows = []

    for seed in seeds:
        for condition in conditions:
            for fraction in compromise_fractions:
                result = compare_sol_link_pressure(
                    config=config,
                    seed=seed,
                    condition=condition,
                    compromise_fraction=fraction,
                    magnet_strengths=magnet_strengths,
                    wandering_strengths=wandering_strengths,
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
        "schema_version": "1.3.1",
        "experiment": "sol-link-pressure-field-comparison",
        "results": results,
    }, indent=2, sort_keys=True))

    print(f"Wrote {csv_out}")
    print(f"Wrote {json_out}")
    print(f"Total experiment conditions: {len(results)}")
    print(f"Total CSV rows: {len(rows)}")


if __name__ == "__main__":
    run_sol_link_pressure_suite(
        config_path="experiments/example.json",
        seeds=["run-001", "run-002", "run-003"],
        conditions=DEFAULT_CONDITIONS,
        compromise_fractions=[0.20],
        magnet_strengths=DEFAULT_MAGNET_STRENGTHS,
        wandering_strengths=DEFAULT_WANDERING_STRENGTHS,
        hop_budget=12,
    )
