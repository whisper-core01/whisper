"""
WHISPER v1.3.0 — Sol-Link Magnetic Hop-by-Hop Routing.

This module implements the architecture frozen in V1_3_ARCHITECTURE_INVARIANTS.md.

Core invariants:
- VoxMesh qualifies logical WHISPER relays.
- WHISPER selects among admissible logical relays.
- Reticulum transports opaque capsules.
- VoxMesh does not know Reticulum nodes, addresses, or routes.
- Reticulum does not know WHISPER payload.
- No layer knows everything.
- Scores bend probability; they never deterministically define the path.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from flv_node_score_policy_v01 import node_score_risk


LogicalRelayId = str
OpaqueTransportCapsule = str
NodeScoreTable = Dict[str, float]


@dataclass(frozen=True)
class LogicalRelay:
    """
    VoxMesh-visible logical relay.

    This object intentionally does not expose:
    - Reticulum address
    - Reticulum node identity
    - transport route
    - physical location
    - IP-level data
    """

    relay_alias: LogicalRelayId
    sol_compatible: bool = True
    observable: bool = True
    admissible: bool = True
    revoked: bool = False
    unfit: bool = False
    opaque_transport_capsule: Optional[OpaqueTransportCapsule] = None


@dataclass(frozen=True)
class LogicalHopDecision:
    current_relay: LogicalRelayId
    selected_relay: LogicalRelayId
    selected_weight: float
    candidate_weights: Dict[LogicalRelayId, float]


def stable_hash_hex(*parts: str) -> str:
    return hashlib.sha256("::".join(parts).encode("utf-8")).hexdigest()


def deterministic_unit_interval(*parts: str) -> float:
    digest = stable_hash_hex(*parts)
    return int(digest[:8], 16) / 0xFFFFFFFF


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def derive_sol_link_alias(
    local_ephemeral_material: str,
    remote_ephemeral_material: str,
    sol_id: str,
    epoch: str,
    session_nonce: str,
) -> str:
    """
    Derive the epoch-scoped Sol-link magnet.

    This is not a stable node identity.
    This is not a Reticulum address.
    This is not a route.
    """
    return stable_hash_hex(
        local_ephemeral_material,
        remote_ephemeral_material,
        sol_id,
        epoch,
        session_nonce,
        "WHISPER_SOL_LINK_V1",
    )


def sol_link_affinity(
    current_relay: LogicalRelayId,
    candidate_relay: LogicalRelayId,
    sol_link_alias: str,
    seed: str,
) -> float:
    """
    Local magnetic affinity to the Sol-link attractor.

    This is intentionally probabilistic and context-scoped.
    """
    return 0.05 + 0.95 * deterministic_unit_interval(
        seed,
        current_relay,
        candidate_relay,
        sol_link_alias,
        "sol-link-affinity",
    )


def flv_health_safety(relay_alias: LogicalRelayId, node_scores: NodeScoreTable) -> float:
    return 1.0 - node_score_risk(node_scores.get(relay_alias, 0.0))


def degradation_safety(
    current_relay: LogicalRelayId,
    candidate_relay: LogicalRelayId,
    degradation_scores: Dict[Tuple[str, str], float],
) -> float:
    risk = degradation_scores.get((current_relay, candidate_relay), 0.0)
    return 1.0 - clamp(risk)


def structural_exposure_safety(
    candidate_relay: LogicalRelayId,
    known_neighbors: Dict[LogicalRelayId, List[LogicalRelayId]],
) -> float:
    """
    Local-only structural exposure proxy.

    More local alternatives means less brittle local flow.
    """
    degree = len(set(known_neighbors.get(candidate_relay, [])))
    diversity = min(degree / 8.0, 1.0)
    return clamp(0.20 + 0.80 * diversity)


def loop_safety(candidate_relay: LogicalRelayId, visited: Set[LogicalRelayId]) -> float:
    if candidate_relay in visited:
        return 0.01
    return 1.0


def admissible_logical_neighbors(
    current_relay: LogicalRelayId,
    known_neighbors: Dict[LogicalRelayId, List[LogicalRelayId]],
    relays: Dict[LogicalRelayId, LogicalRelay],
) -> List[LogicalRelay]:
    """
    VoxMesh qualification step.

    Returns only logical WHISPER relays.
    Never enumerates Reticulum.
    Never exposes Reticulum addresses.
    """
    out: List[LogicalRelay] = []

    for alias in known_neighbors.get(current_relay, []):
        relay = relays.get(alias)
        if relay is None:
            continue

        if not relay.admissible:
            continue
        if not relay.sol_compatible:
            continue
        if not relay.observable:
            continue
        if relay.revoked:
            continue
        if relay.unfit:
            continue
        if relay.opaque_transport_capsule is None:
            continue

        out.append(relay)

    return out


def logical_next_hop_weight(
    current_relay: LogicalRelayId,
    candidate: LogicalRelay,
    sol_link_alias: str,
    node_scores: NodeScoreTable,
    degradation_scores: Dict[Tuple[str, str], float],
    known_neighbors: Dict[LogicalRelayId, List[LogicalRelayId]],
    visited: Set[LogicalRelayId],
    seed: str,
    magnet_strength: float = 1.0,
) -> float:
    """
    Sol-link magnetic next-hop weight.

    Scores bend probability.
    They do not deterministically define the path.
    """
    if magnet_strength < 0.0:
        raise ValueError("magnet_strength must be >= 0.0")

    base_random_pressure = 0.05 + 0.95 * deterministic_unit_interval(
        seed,
        current_relay,
        candidate.relay_alias,
        "base-random-pressure",
    )

    magnet = 1.0 + magnet_strength * sol_link_affinity(
        current_relay=current_relay,
        candidate_relay=candidate.relay_alias,
        sol_link_alias=sol_link_alias,
        seed=seed,
    )

    weight = (
        base_random_pressure
        * magnet
        * flv_health_safety(candidate.relay_alias, node_scores)
        * degradation_safety(current_relay, candidate.relay_alias, degradation_scores)
        * structural_exposure_safety(candidate.relay_alias, known_neighbors)
        * loop_safety(candidate.relay_alias, visited)
    )

    return max(weight, 1e-9)


def weighted_random_choice(
    weighted_items: List[Tuple[LogicalRelay, float]],
    seed: str,
) -> Tuple[LogicalRelay, float]:
    """
    Deterministic weighted random choice.

    Same seed + same candidates + same weights => same result.
    This is still probabilistic selection, not argmax.
    """
    if not weighted_items:
        raise ValueError("weighted_items must not be empty")

    total = sum(weight for _, weight in weighted_items)

    if total <= 0.0:
        return weighted_items[0]

    rng = random.Random(seed)
    threshold = rng.random() * total

    cumulative = 0.0
    for item, weight in weighted_items:
        cumulative += weight
        if cumulative >= threshold:
            return item, weight

    return weighted_items[-1]


def select_logical_next_hop(
    current_relay: LogicalRelayId,
    known_neighbors: Dict[LogicalRelayId, List[LogicalRelayId]],
    relays: Dict[LogicalRelayId, LogicalRelay],
    sol_link_alias: str,
    node_scores: NodeScoreTable,
    degradation_scores: Dict[Tuple[str, str], float],
    visited: Set[LogicalRelayId],
    seed: str,
    magnet_strength: float = 1.0,
) -> Optional[LogicalHopDecision]:
    candidates = admissible_logical_neighbors(
        current_relay=current_relay,
        known_neighbors=known_neighbors,
        relays=relays,
    )

    if not candidates:
        return None

    weighted: List[Tuple[LogicalRelay, float]] = []
    candidate_weights: Dict[LogicalRelayId, float] = {}

    for candidate in candidates:
        weight = logical_next_hop_weight(
            current_relay=current_relay,
            candidate=candidate,
            sol_link_alias=sol_link_alias,
            node_scores=node_scores,
            degradation_scores=degradation_scores,
            known_neighbors=known_neighbors,
            visited=visited,
            seed=seed,
            magnet_strength=magnet_strength,
        )
        weighted.append((candidate, weight))
        candidate_weights[candidate.relay_alias] = weight

    selected, selected_weight = weighted_random_choice(
        weighted,
        seed=f"{seed}:weighted-choice:{current_relay}",
    )

    return LogicalHopDecision(
        current_relay=current_relay,
        selected_relay=selected.relay_alias,
        selected_weight=selected_weight,
        candidate_weights=candidate_weights,
    )


def reticulum_transport_attempt(
    relay: LogicalRelay,
    opaque_whisper_capsule: str,
    seed: str,
) -> Dict[str, Any]:
    """
    Simulated Reticulum adapter boundary.

    Reticulum may decode the opaque transport capsule in real time.
    VoxMesh never learns the Reticulum node, address, or route.

    The WHISPER payload remains opaque to Reticulum.
    """
    if relay.opaque_transport_capsule is None:
        return {
            "attempted": False,
            "delivered": False,
            "failure": "missing_transport_capsule",
        }

    success_score = deterministic_unit_interval(
        seed,
        relay.relay_alias,
        relay.opaque_transport_capsule,
        "reticulum-transport-attempt",
    )

    delivered = success_score >= 0.15

    return {
        "attempted": True,
        "delivered": delivered,
        "failure": None if delivered else "transport_timeout",
        "reticulum_identity_exposed_to_voxmesh": False,
        "whisper_payload_visible_to_reticulum": False,
        "opaque_whisper_capsule_len": len(opaque_whisper_capsule),
    }


def route_sol_link_magnetic_hop_by_hop(
    source_relay: LogicalRelayId,
    relays: Dict[LogicalRelayId, LogicalRelay],
    known_neighbors: Dict[LogicalRelayId, List[LogicalRelayId]],
    local_ephemeral_material: str,
    remote_ephemeral_material: str,
    sol_id: str,
    epoch: str,
    session_nonce: str,
    opaque_whisper_capsule: str,
    node_scores: NodeScoreTable,
    degradation_scores: Dict[Tuple[str, str], float],
    seed: str,
    hop_budget: int = 12,
    magnet_strength: float = 1.0,
) -> Dict[str, Any]:
    """
    Logical hop-by-hop routing through VoxMesh-known relays.

    There is no full route precomputation.
    There is no Reticulum graph enumeration.
    There is no plaintext transport identity in VoxMesh.
    """
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

    for hop_index in range(hop_budget):
        decision = select_logical_next_hop(
            current_relay=current,
            known_neighbors=known_neighbors,
            relays=relays,
            sol_link_alias=sol_link_alias,
            node_scores=node_scores,
            degradation_scores=degradation_scores,
            visited=visited,
            seed=f"{seed}:hop:{hop_index}",
            magnet_strength=magnet_strength,
        )

        if decision is None:
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

    return {
        "policy": "sol_link_magnetic_hop_by_hop",
        "source_relay": source_relay,
        "path": path,
        "hop_count": max(0, len(path) - 1),
        "hop_budget": hop_budget,
        "loop_detected": loop_detected,
        "sol_link_alias": sol_link_alias,
        "sol_link_alias_prefix": sol_link_alias[:16],
        "magnet_strength": magnet_strength,
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

    result = route_sol_link_magnetic_hop_by_hop(
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
        magnet_strength=2.0,
    )

    print("Policy:", result["policy"])
    print("Path:", result["path"])
    print("Hop count:", result["hop_count"])
    print("Loop detected:", result["loop_detected"])
    print("Sol-link alias prefix:", result["sol_link_alias_prefix"])
    print("VoxMesh knows Reticulum identity:", result["voxmesh_knows_reticulum_identity"])
    print("Reticulum knows WHISPER payload:", result["reticulum_knows_whisper_payload"])
