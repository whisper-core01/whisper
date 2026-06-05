"""
WHISPER v1.3.1 — Sol-Link Pressure Field Routing.

Builds on v1.3.0 Sol-link magnetic routing.

Adds:
- randomness dissipation
- wandering safety
- routing basin safety
- candidate-count tracking
- transport delivery ratio
- dead-end detection

Still preserves:
- no Reticulum graph enumeration
- no Reticulum identity visible to VoxMesh
- no WHISPER payload visible to Reticulum
- weighted random choice, never argmax
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

from flv_node_score_policy_v01 import node_score_risk
from sol_link_magnetic_policy_v01 import (
    LogicalHopDecision,
    LogicalRelay,
    LogicalRelayId,
    NodeScoreTable,
    OpaqueTransportCapsule,
    admissible_logical_neighbors,
    clamp,
    degradation_safety,
    derive_sol_link_alias,
    deterministic_unit_interval,
    flv_health_safety,
    reticulum_transport_attempt,
    sol_link_affinity,
    stable_hash_hex,
    structural_exposure_safety,
    weighted_random_choice,
)


def randomness_dissipation(
    hop_index: int,
    hop_budget: int,
    min_factor: float = 0.35,
) -> float:
    """
    Reduce random pressure as TTL is consumed.

    Early hops explore.
    Late hops converge.
    """
    if hop_budget <= 0:
        return min_factor

    progress = min(max(hop_index / hop_budget, 0.0), 1.0)
    return clamp(1.0 - (1.0 - min_factor) * progress, min_factor, 1.0)


def wandering_safety(
    affinity: float,
    hop_index: int,
    hop_budget: int,
    wandering_strength: float = 1.0,
) -> float:
    """
    Penalize weak Sol-link affinity more strongly as the fragment consumes TTL.

    This does not ban low-affinity relays.
    It reduces their probability when the fragment is already wandering.
    """
    if wandering_strength < 0.0:
        raise ValueError("wandering_strength must be >= 0.0")

    if hop_budget <= 0:
        return 1.0

    ttl_pressure = min(max(hop_index / hop_budget, 0.0), 1.0)
    weak_affinity = max(0.0, 0.50 - affinity)

    penalty = wandering_strength * ttl_pressure * weak_affinity * 2.0

    return clamp(1.0 - penalty, 0.15, 1.0)


def routing_basin_safety(
    candidate: LogicalRelay,
    known_neighbors: Dict[LogicalRelayId, List[LogicalRelayId]],
) -> float:
    """
    Local logical basin safety.

    A relay with no known logical outlets is a dead-end-like basin edge.
    It is not banned, but heavily discouraged.
    """
    degree = len(set(known_neighbors.get(candidate.relay_alias, [])))

    if degree <= 0:
        return 0.20

    if degree == 1:
        return 0.55

    if degree == 2:
        return 0.75

    return 1.0


def pressure_next_hop_weight(
    current_relay: LogicalRelayId,
    candidate: LogicalRelay,
    sol_link_alias: str,
    node_scores: NodeScoreTable,
    degradation_scores: Dict[Tuple[str, str], float],
    known_neighbors: Dict[LogicalRelayId, List[LogicalRelayId]],
    visited: Set[LogicalRelayId],
    seed: str,
    hop_index: int,
    hop_budget: int,
    magnet_strength: float = 4.0,
    wandering_strength: float = 1.0,
) -> float:
    """
    v1.3.1 pressure field next-hop weight.

    Scores bend probability.
    They never deterministically define the path.
    """
    if magnet_strength < 0.0:
        raise ValueError("magnet_strength must be >= 0.0")

    base_random_pressure = 0.05 + 0.95 * deterministic_unit_interval(
        seed,
        current_relay,
        candidate.relay_alias,
        "pressure-random",
    )

    dissipated_random = base_random_pressure * randomness_dissipation(
        hop_index=hop_index,
        hop_budget=hop_budget,
    )

    affinity = sol_link_affinity(
        current_relay=current_relay,
        candidate_relay=candidate.relay_alias,
        sol_link_alias=sol_link_alias,
        seed=seed,
    )

    magnet = 1.0 + magnet_strength * affinity

    # Existing loop safety is intentionally simple:
    # visited relays are not impossible, but almost never selected.
    loop = 0.01 if candidate.relay_alias in visited else 1.0

    weight = (
        dissipated_random
        * magnet
        * wandering_safety(
            affinity=affinity,
            hop_index=hop_index,
            hop_budget=hop_budget,
            wandering_strength=wandering_strength,
        )
        * routing_basin_safety(candidate, known_neighbors)
        * flv_health_safety(candidate.relay_alias, node_scores)
        * degradation_safety(current_relay, candidate.relay_alias, degradation_scores)
        * structural_exposure_safety(candidate.relay_alias, known_neighbors)
        * loop
    )

    return max(weight, 1e-9)


def select_pressure_next_hop(
    current_relay: LogicalRelayId,
    known_neighbors: Dict[LogicalRelayId, List[LogicalRelayId]],
    relays: Dict[LogicalRelayId, LogicalRelay],
    sol_link_alias: str,
    node_scores: NodeScoreTable,
    degradation_scores: Dict[Tuple[str, str], float],
    visited: Set[LogicalRelayId],
    seed: str,
    hop_index: int,
    hop_budget: int,
    magnet_strength: float = 4.0,
    wandering_strength: float = 1.0,
) -> Optional[LogicalHopDecision]:
    candidates = admissible_logical_neighbors(
        current_relay=current_relay,
        known_neighbors=known_neighbors,
        relays=relays,
    )

    if not candidates:
        return None

    weighted = []
    candidate_weights = {}

    for candidate in candidates:
        weight = pressure_next_hop_weight(
            current_relay=current_relay,
            candidate=candidate,
            sol_link_alias=sol_link_alias,
            node_scores=node_scores,
            degradation_scores=degradation_scores,
            known_neighbors=known_neighbors,
            visited=visited,
            seed=seed,
            hop_index=hop_index,
            hop_budget=hop_budget,
            magnet_strength=magnet_strength,
            wandering_strength=wandering_strength,
        )

        weighted.append((candidate, weight))
        candidate_weights[candidate.relay_alias] = weight

    selected, selected_weight = weighted_random_choice(
        weighted,
        seed=f"{seed}:pressure-choice:{current_relay}:{hop_index}",
    )

    return LogicalHopDecision(
        current_relay=current_relay,
        selected_relay=selected.relay_alias,
        selected_weight=selected_weight,
        candidate_weights=candidate_weights,
    )


def route_sol_link_pressure_hop_by_hop(
    source_relay: LogicalRelayId,
    relays: Dict[LogicalRelayId, LogicalRelay],
    known_neighbors: Dict[LogicalRelayId, List[LogicalRelayId]],
    local_ephemeral_material: str,
    remote_ephemeral_material: str,
    sol_id: str,
    epoch: str,
    session_nonce: str,
    opaque_whisper_capsule: OpaqueTransportCapsule,
    node_scores: NodeScoreTable,
    degradation_scores: Dict[Tuple[str, str], float],
    seed: str,
    hop_budget: int = 12,
    magnet_strength: float = 4.0,
    wandering_strength: float = 1.0,
) -> Dict[str, Any]:
    if hop_budget < 1:
        raise ValueError("hop_budget must be >= 1")

    sol_link_alias = derive_sol_link_alias(
        local_ephemeral_material=local_ephemeral_material,
        remote_ephemeral_material=remote_ephemeral_material,
        sol_id=sol_id,
        epoch=epoch,
        session_nonce=session_nonce,
    )

    current = source_relay
    visited: Set[LogicalRelayId] = {source_relay}
    path: List[LogicalRelayId] = [source_relay]
    decisions: List[LogicalHopDecision] = []
    transport_results: List[Dict[str, Any]] = []
    candidate_counts: List[int] = []
    dead_end = False

    for hop_index in range(hop_budget):
        candidates = admissible_logical_neighbors(
            current_relay=current,
            known_neighbors=known_neighbors,
            relays=relays,
        )
        candidate_counts.append(len(candidates))

        if not candidates:
            dead_end = True
            break

        decision = select_pressure_next_hop(
            current_relay=current,
            known_neighbors=known_neighbors,
            relays=relays,
            sol_link_alias=sol_link_alias,
            node_scores=node_scores,
            degradation_scores=degradation_scores,
            visited=visited,
            seed=f"{seed}:hop:{hop_index}",
            hop_index=hop_index,
            hop_budget=hop_budget,
            magnet_strength=magnet_strength,
            wandering_strength=wandering_strength,
        )

        if decision is None:
            dead_end = True
            break

        selected_relay = relays[decision.selected_relay]

        transport = reticulum_transport_attempt(
            relay=selected_relay,
            opaque_whisper_capsule=opaque_whisper_capsule,
            seed=f"{seed}:transport:{hop_index}",
        )

        decisions.append(decision)
        transport_results.append(transport)

        if not transport["delivered"]:
            break

        current = decision.selected_relay
        path.append(current)
        visited.add(current)

    loop_detected = len(path) != len(set(path))

    attempted = len(transport_results)
    successful = sum(1 for item in transport_results if item["delivered"])

    transport_delivery_ratio = (
        successful / attempted
        if attempted > 0
        else 0.0
    )

    relay_reuse_count = len(path) - len(set(path))

    mean_candidate_count = (
        sum(candidate_counts) / len(candidate_counts)
        if candidate_counts
        else 0.0
    )

    return {
        "policy": "sol_link_pressure_hop_by_hop",
        "source_relay": source_relay,
        "path": path,
        "hop_count": max(0, len(path) - 1),
        "hop_budget": hop_budget,
        "loop_detected": loop_detected,
        "dead_end": dead_end,
        "relay_reuse_count": relay_reuse_count,
        "candidate_counts": candidate_counts,
        "mean_candidate_count": mean_candidate_count,
        "transport_attempts": attempted,
        "successful_transport_attempts": successful,
        "transport_delivery_ratio": transport_delivery_ratio,
        "transport_success": attempted > 0 and successful == attempted,
        "sol_link_alias": sol_link_alias,
        "sol_link_alias_prefix": sol_link_alias[:16],
        "magnet_strength": magnet_strength,
        "wandering_strength": wandering_strength,
        "decisions": [
            {
                "current_relay": d.current_relay,
                "selected_relay": d.selected_relay,
                "selected_weight": d.selected_weight,
                "candidate_weights": d.candidate_weights,
            }
            for d in decisions
        ],
        "transport_results": transport_results,
        "reticulum_graph_visible": False,
        "voxmesh_knows_reticulum_identity": False,
        "reticulum_knows_whisper_payload": False,
    }


if __name__ == "__main__":
    relays = {
        "a": LogicalRelay("a", opaque_transport_capsule="capsule:a"),
        "b": LogicalRelay("b", opaque_transport_capsule="capsule:b"),
        "c": LogicalRelay("c", opaque_transport_capsule="capsule:c"),
        "d": LogicalRelay("d", opaque_transport_capsule="capsule:d"),
    }

    known_neighbors = {
        "a": ["b", "c"],
        "b": ["d"],
        "c": ["d"],
        "d": [],
    }

    result = route_sol_link_pressure_hop_by_hop(
        source_relay="a",
        relays=relays,
        known_neighbors=known_neighbors,
        local_ephemeral_material="local",
        remote_ephemeral_material="remote",
        sol_id="sol-demo",
        epoch="1",
        session_nonce="nonce-demo",
        opaque_whisper_capsule="opaque-whisper-fragment",
        node_scores={},
        degradation_scores={},
        seed="demo",
        hop_budget=4,
        magnet_strength=4.0,
        wandering_strength=1.0,
    )

    print("Policy:", result["policy"])
    print("Path:", result["path"])
    print("Hop count:", result["hop_count"])
    print("Loop detected:", result["loop_detected"])
    print("Dead end:", result["dead_end"])
    print("Delivery ratio:", result["transport_delivery_ratio"])
    print("Mean candidates:", result["mean_candidate_count"])
