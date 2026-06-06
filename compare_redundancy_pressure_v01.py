"""
WHISPER v1.3.2 — Redundancy-compensated pressure routing.

Tests whether a small redundancy overhead compensates v1.3.1 pressure-field
delivery loss while preserving exposure benefits.

Corrected model:
- fragments are not treated as lost merely because a full end-to-end route did not complete
- successful hop-by-hop progress creates relay custody
- custody allows local retry / continuation
- message reconstruction is based on custody-adjusted useful fragments

Primary message-level metrics:
- message_reconstruction_success
- effective_reconstruction_ratio
- mean_compromised_relays_per_message
- clean_reconstruction_ratio
- bandwidth_overhead
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Set

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
from redundancy_compensation_v01 import (
    build_redundancy_plan,
    summarize_fragment_delivery,
)
from sol_link_magnetic_policy_v01 import deterministic_unit_interval
from sol_link_pressure_policy_v01 import route_sol_link_pressure_hop_by_hop
from topology_v01 import generate_topology


DEFAULT_REDUNDANCY_FACTORS = [1.00, 1.05, 1.10, 1.15, 1.25]
DEFAULT_MAGNET_STRENGTHS = [6.0]
DEFAULT_WANDERING_STRENGTHS = [0.5]
DEFAULT_REQUIRED_FRAGMENTS = 100
DEFAULT_CUSTODY_ROUNDS = 3


def _source_for_fragment(nodes: List[str], seed: str, fragment_index: int) -> str:
    x = deterministic_unit_interval(seed, str(fragment_index), "fragment-source")
    return nodes[int(x * len(nodes)) % len(nodes)]


def custody_adjusted_delivery_probability(
    transport_delivery_ratio: float,
    custody_rounds: int,
) -> float:
    """
    Persistent hop-by-hop custody model.

    A fragment that makes partial progress is not immediately lost.
    Each successful handoff can persist the fragment at a WHISPER relay,
    allowing local continuation/retry.

    This converts per-run transport progress into a custody-adjusted
    probability that the fragment remains useful for reconstruction.
    """
    if custody_rounds < 1:
        raise ValueError("custody_rounds must be >= 1")

    ratio = max(0.0, min(1.0, transport_delivery_ratio))
    return 1.0 - ((1.0 - ratio) ** custody_rounds)


def custody_adjusted_fragment_delivered(
    seed: str,
    fragment_index: int,
    transport_delivery_ratio: float,
    custody_rounds: int,
) -> bool:
    probability = custody_adjusted_delivery_probability(
        transport_delivery_ratio=transport_delivery_ratio,
        custody_rounds=custody_rounds,
    )

    draw = deterministic_unit_interval(
        seed,
        str(fragment_index),
        "custody-adjusted-delivery",
    )

    return draw <= probability


def simulate_redundant_message(
    config: Dict[str, Any],
    seed: str,
    condition: str,
    compromise_fraction: float,
    required_fragments: int,
    redundancy_factor: float,
    magnet_strength: float,
    wandering_strength: float,
    hop_budget: int,
    custody_rounds: int = DEFAULT_CUSTODY_ROUNDS,
) -> Dict[str, Any]:
    graph = generate_topology(config, seed)
    nodes = graph_nodes(graph)
    known_neighbors = build_known_neighbors(graph)
    relays = build_logical_relays(nodes, condition, seed)

    compromised = compromised_nodes_for_condition(
        nodes=nodes,
        known_neighbors=known_neighbors,
        condition=condition,
        fraction=compromise_fraction,
        seed=seed,
    )

    node_scores = build_node_scores(nodes, seed)
    degradation_scores = build_degradation_scores(known_neighbors, condition, seed)

    plan = build_redundancy_plan(
        required_fragments=required_fragments,
        redundancy_factor=redundancy_factor,
    )

    delivered_by_index: Dict[int, bool] = {}
    compromised_by_index: Dict[int, bool] = {}
    hop_counts = []
    delivery_ratios = []
    loop_count = 0
    dead_end_count = 0
    total_compromised_relays = 0
    total_paths = 0

    for index in range(plan.emitted_fragments):
        source = _source_for_fragment(nodes, seed, index)

        result = route_sol_link_pressure_hop_by_hop(
            source_relay=source,
            relays=relays,
            known_neighbors=known_neighbors,
            local_ephemeral_material=f"local:{seed}:{index}",
            remote_ephemeral_material=f"remote:{seed}:{index}",
            sol_id=f"sol:{seed}",
            epoch="1",
            session_nonce=f"nonce:{seed}:{index}",
            opaque_whisper_capsule=f"opaque-fragment:{seed}:{index}",
            node_scores=node_scores,
            degradation_scores=degradation_scores,
            seed=f"{seed}:fragment:{index}:pressure",
            hop_budget=hop_budget,
            magnet_strength=magnet_strength,
            wandering_strength=wandering_strength,
        )

        transport_delivery_ratio = float(result["transport_delivery_ratio"])

        delivered = custody_adjusted_fragment_delivered(
            seed=seed,
            fragment_index=index,
            transport_delivery_ratio=transport_delivery_ratio,
            custody_rounds=custody_rounds,
        )

        delivered_by_index[index] = delivered

        exposure = evaluate_path_exposure(result["path"], compromised)
        compromised_path = bool(exposure["compromised_relays"] > 0)
        compromised_by_index[index] = compromised_path

        total_compromised_relays += int(exposure["compromised_relays"])
        total_paths += 1

        hop_counts.append(int(result["hop_count"]))
        delivery_ratios.append(float(result["transport_delivery_ratio"]))

        if result["loop_detected"]:
            loop_count += 1

        if result["dead_end"]:
            dead_end_count += 1

    summary = summarize_fragment_delivery(delivered_by_index, plan)

    delivered_indices = [
        index for index, ok in delivered_by_index.items()
        if ok
    ]

    delivered_compromised_paths = [
        index for index in delivered_indices
        if compromised_by_index.get(index, False)
    ]

    clean_reconstruction = (
        summary["message_reconstructed"]
        and len(delivered_compromised_paths) == 0
    )

    return {
        "schema_version": "1.3.2",
        "experiment": "redundancy-compensated-pressure-routing",
        "seed": seed,
        "condition": condition,
        "compromise_fraction": compromise_fraction,
        "required_fragments": plan.required_fragments,
        "emitted_fragments": plan.emitted_fragments,
        "recovery_fragments": plan.recovery_fragments,
        "redundancy_factor": plan.redundancy_factor,
        "bandwidth_overhead": plan.emitted_fragments / plan.required_fragments,
        "magnet_strength": magnet_strength,
        "wandering_strength": wandering_strength,
        "hop_budget": hop_budget,
        "custody_rounds": custody_rounds,
        "message_reconstructed": summary["message_reconstructed"],
        "effective_reconstruction_ratio": summary["effective_reconstruction_ratio"],
        "reconstruction_margin": summary["reconstruction_margin"],
        "delivered_total": summary["delivered_total"],
        "primary_delivered": summary["primary_delivered"],
        "recovery_delivered": summary["recovery_delivered"],
        "clean_reconstruction": clean_reconstruction,
        "delivered_compromised_fragments": len(delivered_compromised_paths),
        "mean_hop_count": mean(hop_counts) if hop_counts else 0.0,
        "mean_transport_delivery_ratio": mean(delivery_ratios) if delivery_ratios else 0.0,
        "loop_rate": loop_count / plan.emitted_fragments,
        "dead_end_rate": dead_end_count / plan.emitted_fragments,
        "mean_compromised_relays_per_fragment": total_compromised_relays / max(total_paths, 1),
        "reticulum_graph_visible": False,
        "voxmesh_knows_reticulum_identity": False,
        "reticulum_knows_whisper_payload": False,
    }


def run_redundancy_pressure_suite(
    config_path: str,
    seeds: List[str],
    conditions: List[str] | None = None,
    compromise_fractions: List[float] | None = None,
    redundancy_factors: List[float] | None = None,
    magnet_strengths: List[float] | None = None,
    wandering_strengths: List[float] | None = None,
    required_fragments: int = DEFAULT_REQUIRED_FRAGMENTS,
    hop_budget: int = 12,
    custody_rounds: int = DEFAULT_CUSTODY_ROUNDS,
    csv_path: str = "outputs/compare_redundancy_pressure_v01.csv",
    json_path: str = "outputs/compare_redundancy_pressure_v01.json",
) -> None:
    config = json.loads(Path(config_path).read_text())

    if conditions is None:
        conditions = DEFAULT_CONDITIONS

    if compromise_fractions is None:
        compromise_fractions = [0.20]

    if redundancy_factors is None:
        redundancy_factors = DEFAULT_REDUNDANCY_FACTORS

    if magnet_strengths is None:
        magnet_strengths = DEFAULT_MAGNET_STRENGTHS

    if wandering_strengths is None:
        wandering_strengths = DEFAULT_WANDERING_STRENGTHS

    rows = []

    for seed in seeds:
        for condition in conditions:
            for fraction in compromise_fractions:
                for redundancy_factor in redundancy_factors:
                    for magnet_strength in magnet_strengths:
                        for wandering_strength in wandering_strengths:
                            row = simulate_redundant_message(
                                config=config,
                                seed=seed,
                                condition=condition,
                                compromise_fraction=fraction,
                                required_fragments=required_fragments,
                                redundancy_factor=redundancy_factor,
                                magnet_strength=magnet_strength,
                                wandering_strength=wandering_strength,
                                hop_budget=hop_budget,
                                custody_rounds=custody_rounds,
                            )
                            rows.append(row)

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
        "schema_version": "1.3.2",
        "experiment": "redundancy-compensated-pressure-routing",
        "results": rows,
    }, indent=2, sort_keys=True))

    print(f"Wrote {csv_out}")
    print(f"Wrote {json_out}")
    print(f"Total rows: {len(rows)}")


if __name__ == "__main__":
    run_redundancy_pressure_suite(
        config_path="experiments/example.json",
        seeds=["run-001", "run-002", "run-003"],
        conditions=DEFAULT_CONDITIONS,
        compromise_fractions=[0.20],
        redundancy_factors=DEFAULT_REDUNDANCY_FACTORS,
        magnet_strengths=[6.0],
        wandering_strengths=[0.5],
        required_fragments=100,
        hop_budget=12,
        custody_rounds=3,
    )
