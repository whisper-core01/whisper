"""
WHISPER v1.3.0 — Compare Sol-link magnetic logical routing.

This comparator evaluates the v1.3.0 logical-relay model:

- VoxMesh qualifies logical relays.
- WHISPER selects by weighted random choice.
- Reticulum transports opaque capsules.
- No Reticulum graph is enumerated.
- VoxMesh does not know Reticulum transport identity.
- Reticulum does not know WHISPER payload.

This is a logical routing comparator, not a Reticulum transport graph comparator.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from sol_anchored_hop_policy_v01 import graph_neighbors
from sol_link_magnetic_policy_v01 import (
    LogicalRelay,
    route_sol_link_magnetic_hop_by_hop,
    deterministic_unit_interval,
)
from topology_v01 import generate_topology


LogicalRelayId = str
NodePath = List[str]

DEFAULT_MAGNET_STRENGTHS = [0.0, 1.0, 2.0, 4.0, 8.0]
DEFAULT_CONDITIONS = ["random", "targeted", "behavioral"]


def graph_nodes(graph: Any) -> List[str]:
    if hasattr(graph, "nodes"):
        nodes = graph.nodes
        if callable(nodes):
            nodes = nodes()
        return list(nodes)

    if hasattr(graph, "node_count"):
        return [f"n{i}" for i in range(graph.node_count)]

    raise TypeError("graph must expose nodes or node_count")


def build_known_neighbors(graph: Any) -> Dict[LogicalRelayId, List[LogicalRelayId]]:
    """
    Build VoxMesh-known logical adjacency from the simulation graph.

    In this comparator, the topology graph represents the known logical VoxMesh
    tissue, not the Reticulum transport graph.
    """
    known: Dict[str, List[str]] = {}

    for node in graph_nodes(graph):
        known[node] = list(graph_neighbors(graph, node))

    return known


def build_logical_relays(nodes: List[str], condition: str, seed: str) -> Dict[str, LogicalRelay]:
    """
    Build logical WHISPER relays.

    The opaque_transport_capsule is intentionally opaque. It is not a Reticulum
    address and is not inspected by VoxMesh routing logic.
    """
    relays = {}

    for node in nodes:
        observable = True
        admissible = True
        revoked = False
        unfit = False
        sol_compatible = True

        if condition == "behavioral":
            # Deterministic local degradation-like condition:
            # a small fraction of logical relays become unfit/less usable.
            r = deterministic_unit_interval(seed, node, "behavioral-unfit")
            if r < 0.05:
                unfit = True
            elif r < 0.10:
                observable = False

        relays[node] = LogicalRelay(
            relay_alias=node,
            sol_compatible=sol_compatible,
            observable=observable,
            admissible=admissible,
            revoked=revoked,
            unfit=unfit,
            opaque_transport_capsule=f"opaque-transport-capsule:{seed}:{node}",
        )

    return relays


def deterministic_compromise(
    nodes: List[str],
    fraction: float,
    seed: str,
) -> Set[str]:
    count = max(0, int(round(len(nodes) * fraction)))
    ranked = sorted(
        nodes,
        key=lambda n: deterministic_unit_interval(seed, n, "compromise-rank"),
    )
    return set(ranked[:count])


def targeted_high_degree_compromise(
    known_neighbors: Dict[str, List[str]],
    fraction: float,
) -> Set[str]:
    nodes = list(known_neighbors)
    count = max(0, int(round(len(nodes) * fraction)))

    ranked = sorted(
        nodes,
        key=lambda n: len(set(known_neighbors.get(n, []))),
        reverse=True,
    )

    return set(ranked[:count])


def compromised_nodes_for_condition(
    nodes: List[str],
    known_neighbors: Dict[str, List[str]],
    condition: str,
    fraction: float,
    seed: str,
) -> Set[str]:
    if condition == "random":
        return deterministic_compromise(nodes, fraction, seed)

    if condition == "targeted":
        return targeted_high_degree_compromise(known_neighbors, fraction)

    if condition == "behavioral":
        return set()

    raise ValueError(f"unsupported condition: {condition}")


def build_degradation_scores(
    known_neighbors: Dict[str, List[str]],
    condition: str,
    seed: str,
) -> Dict[Tuple[str, str], float]:
    """
    Relationship-scoped logical degradation.

    Non-oracle: independent from compromise labels.
    """
    scores: Dict[Tuple[str, str], float] = {}

    for current, neighbors in known_neighbors.items():
        for nxt in neighbors:
            base = deterministic_unit_interval(seed, current, nxt, "logical-degradation")
            if condition == "behavioral":
                scores[(current, nxt)] = min(1.0, 0.50 + 0.50 * base)
            else:
                scores[(current, nxt)] = 0.30 * base

    return scores


def build_node_scores(nodes: List[str], seed: str) -> Dict[str, float]:
    """
    Deterministic synthetic FLV-like logical node scores.

    Range approximately [-0.5, 2.5].
    """
    scores = {}

    for node in nodes:
        x = deterministic_unit_interval(seed, node, "node-score")
        scores[node] = -0.5 + 3.0 * x

    return scores


def evaluate_path_exposure(path: NodePath, compromised: Set[str]) -> Dict[str, Any]:
    if not path:
        return {
            "compromised_relays": 0,
            "clean_path": True,
            "compromise_rate": 0.0,
        }

    count = sum(1 for node in path if node in compromised)

    return {
        "compromised_relays": count,
        "clean_path": count == 0,
        "compromise_rate": count / len(path),
    }


def compare_sol_link_magnetic(
    config: Dict[str, Any],
    seed: str,
    condition: str = "random",
    compromise_fraction: float = 0.20,
    magnet_strengths: List[float] | None = None,
    hop_budget: int = 12,
) -> Dict[str, Any]:
    if magnet_strengths is None:
        magnet_strengths = DEFAULT_MAGNET_STRENGTHS

    graph = generate_topology(config, seed)
    nodes = graph_nodes(graph)
    known_neighbors = build_known_neighbors(graph)
    relays = build_logical_relays(nodes, condition, seed)

    source = nodes[int(deterministic_unit_interval(seed, "source") * len(nodes)) % len(nodes)]

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

    for strength in magnet_strengths:
        result = route_sol_link_magnetic_hop_by_hop(
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
            seed=f"{seed}:magnet:{strength}",
            hop_budget=hop_budget,
            magnet_strength=strength,
        )

        transport_results = result["transport_results"]
        attempted = len(transport_results)
        failures = sum(1 for r in transport_results if not r["delivered"])
        transport_success = attempted > 0 and failures == 0

        exposure = evaluate_path_exposure(result["path"], compromised)

        rows.append({
            "policy": "sol_link_magnetic_hop_by_hop",
            "magnet_strength": strength,
            "source_relay": source,
            "hop_count": result["hop_count"],
            "hop_budget": hop_budget,
            "path_len": len(result["path"]),
            "transport_attempts": attempted,
            "transport_failures": failures,
            "transport_success": transport_success,
            "loop_detected": result["loop_detected"],
            "compromised_relays": exposure["compromised_relays"],
            "clean_path": exposure["clean_path"],
            "path_compromise_rate": exposure["compromise_rate"],
            "voxmesh_knows_reticulum_identity": result["voxmesh_knows_reticulum_identity"],
            "reticulum_knows_whisper_payload": result["reticulum_knows_whisper_payload"],
            "reticulum_graph_visible": result["reticulum_graph_visible"],
        })

    return {
        "schema_version": "1.3.0",
        "experiment": "sol-link-magnetic-logical-routing",
        "seed": seed,
        "condition": condition,
        "compromise_fraction": compromise_fraction,
        "node_count": len(nodes),
        "known_logical_edge_count": sum(len(v) for v in known_neighbors.values()),
        "compromised_node_count": len(compromised),
        "hop_budget": hop_budget,
        "magnet_strengths": magnet_strengths,
        "results": rows,
        "invariants": {
            "reticulum_graph_visible": False,
            "voxmesh_knows_reticulum_identity": False,
            "reticulum_knows_whisper_payload": False,
        },
    }


def flatten_result(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []

    base = {
        "schema_version": result["schema_version"],
        "experiment": result["experiment"],
        "seed": result["seed"],
        "condition": result["condition"],
        "compromise_fraction": result["compromise_fraction"],
        "node_count": result["node_count"],
        "known_logical_edge_count": result["known_logical_edge_count"],
        "compromised_node_count": result["compromised_node_count"],
        "hop_budget": result["hop_budget"],
    }

    for row in result["results"]:
        item = dict(base)
        item.update(row)
        out.append(item)

    return out


def run_sol_link_magnetic_suite(
    config_path: str,
    seeds: List[str],
    conditions: List[str] | None = None,
    compromise_fractions: List[float] | None = None,
    magnet_strengths: List[float] | None = None,
    hop_budget: int = 12,
    csv_path: str = "outputs/compare_sol_link_magnetic_v01.csv",
    json_path: str = "outputs/compare_sol_link_magnetic_v01.json",
) -> None:
    config = json.loads(Path(config_path).read_text())

    if conditions is None:
        conditions = DEFAULT_CONDITIONS

    if compromise_fractions is None:
        compromise_fractions = [0.20]

    if magnet_strengths is None:
        magnet_strengths = DEFAULT_MAGNET_STRENGTHS

    results = []
    rows = []

    for seed in seeds:
        for condition in conditions:
            for fraction in compromise_fractions:
                result = compare_sol_link_magnetic(
                    config=config,
                    seed=seed,
                    condition=condition,
                    compromise_fraction=fraction,
                    magnet_strengths=magnet_strengths,
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
        "schema_version": "1.3.0",
        "experiment": "sol-link-magnetic-logical-routing",
        "results": results,
    }, indent=2, sort_keys=True))

    print(f"Wrote {csv_out}")
    print(f"Wrote {json_out}")
    print(f"Total experiment conditions: {len(results)}")
    print(f"Total CSV rows: {len(rows)}")


if __name__ == "__main__":
    run_sol_link_magnetic_suite(
        config_path="experiments/example.json",
        seeds=["run-001", "run-002", "run-003"],
        conditions=DEFAULT_CONDITIONS,
        compromise_fractions=[0.20],
        magnet_strengths=DEFAULT_MAGNET_STRENGTHS,
        hop_budget=12,
    )
