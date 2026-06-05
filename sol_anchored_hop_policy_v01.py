"""
WHISPER v1.3.0 — Sol-Anchored Hop-by-Hop Reselection.

This module prototypes pressure-weighted hop-by-hop routing.

Core idea:
- WHISPER does not precompute a full path.
- It derives an epoch/session scoped Sol anchor alias.
- Each hop selects the next hop locally using weighted randomness.
- Scores modulate probability; they do not deterministically choose the path.

Scope:
- local simulation only
- no stable node identity routing
- no global reputation
- no compromise oracle
- no harassment / revocation
"""

from __future__ import annotations

import hashlib
import random
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from flv_node_score_policy_v01 import node_score_risk
from next_hop_degradation_policy_v01 import effective_degradation


NodePath = List[str]


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def stable_hash_hex(*parts: str) -> str:
    return hashlib.sha256("::".join(parts).encode("utf-8")).hexdigest()


def deterministic_unit_interval(*parts: str) -> float:
    digest = stable_hash_hex(*parts)
    return int(digest[:8], 16) / 0xFFFFFFFF


def derive_sol_anchor_alias(
    receiver_ephemeral_id: str,
    sol_id: str,
    epoch: str,
    session_nonce: str,
) -> str:
    """
    Derive an epoch/session/Sol scoped routing attractor.

    This is not a stable node identity.
    """
    return stable_hash_hex(
        receiver_ephemeral_id,
        sol_id,
        epoch,
        session_nonce,
        "WHISPER_SOL_ANCHOR_V1",
    )


def anchor_affinity(
    current: str,
    candidate_next_hop: str,
    sol_anchor_alias: str,
    seed: str,
) -> float:
    """
    Deterministic pseudo-affinity between a candidate next-hop and the Sol anchor.

    This is a simulation proxy for pressure toward an anchor basin.
    It does not reveal a stable identity or a full path.
    """
    return 0.05 + 0.95 * deterministic_unit_interval(
        seed,
        current,
        candidate_next_hop,
        sol_anchor_alias,
        "anchor-affinity",
    )


def flv_health_safety(node: str, node_scores: Dict[str, float]) -> float:
    """
    Convert v1.1.0 node-score risk into safety.
    """
    return 1.0 - node_score_risk(node_scores.get(node, 0.0))


def degradation_safety(
    current: str,
    candidate_next_hop: str,
    node_scores: Dict[str, float],
    seed: str,
) -> float:
    """
    Convert v1.2.0 relationship degradation into safety.
    """
    risk = effective_degradation(
        observer=current,
        next_hop=candidate_next_hop,
        node_scores=node_scores,
        seed=seed,
    )
    return 1.0 - risk


def structural_exposure_safety(
    candidate_next_hop: str,
    candidate_neighbors: Iterable[str],
) -> float:
    """
    Minimal local structural exposure proxy.

    In v1.3.0 prototype, a node with many local alternatives is safer
    because the pressure has more possible outlets.

    This is intentionally local and weak.
    """
    neighbors = list(candidate_neighbors)
    if not neighbors:
        return 0.0

    # A tiny proxy: avoid total certainty by bounding safety.
    diversity = min(len(set(neighbors)) / 8.0, 1.0)
    return clamp(0.20 + 0.80 * diversity)


def loop_safety(candidate_next_hop: str, visited: Set[str]) -> float:
    """
    Simple simulation anti-loop rule.

    Future protocol can replace visited_set with a digest.
    """
    if candidate_next_hop in visited:
        return 0.01
    return 1.0


def next_hop_weight(
    current: str,
    candidate_next_hop: str,
    neighbors_of_candidate: Iterable[str],
    sol_anchor_alias: str,
    node_scores: Dict[str, float],
    seed: str,
    visited: Set[str],
) -> float:
    """
    Pressure-weighted local next-hop weight.

    Scores modulate probability. They do not deterministically choose.
    """
    base_random_pressure = 0.05 + 0.95 * deterministic_unit_interval(
        seed,
        current,
        candidate_next_hop,
        "base-pressure",
    )

    weight = (
        base_random_pressure
        * anchor_affinity(current, candidate_next_hop, sol_anchor_alias, seed)
        * flv_health_safety(candidate_next_hop, node_scores)
        * degradation_safety(current, candidate_next_hop, node_scores, seed)
        * structural_exposure_safety(candidate_next_hop, neighbors_of_candidate)
        * loop_safety(candidate_next_hop, visited)
    )

    return max(weight, 1e-9)


def weighted_random_choice(
    weighted_items: List[Tuple[str, float]],
    seed: str,
) -> str:
    """
    Deterministic weighted random choice.

    Same seed + same weights => same choice.
    """
    if not weighted_items:
        raise ValueError("weighted_items must not be empty")

    total = sum(weight for _, weight in weighted_items)
    if total <= 0.0:
        return weighted_items[0][0]

    rng = random.Random(seed)
    threshold = rng.random() * total

    cumulative = 0.0
    for item, weight in weighted_items:
        cumulative += weight
        if cumulative >= threshold:
            return item

    return weighted_items[-1][0]


def graph_neighbors(graph: Any, node: str) -> List[str]:
    """
    Compatibility helper for WHISPER topology wrappers and networkx-like graphs.
    """
    if hasattr(graph, "neighbors"):
        return list(graph.neighbors(node))

    if hasattr(graph, "adj"):
        return list(graph.adj.get(node, []))

    if hasattr(graph, "edges"):
        edges = graph.edges
        if callable(edges):
            edges = edges()

        neighbors = []
        for edge in edges:
            if len(edge) < 2:
                continue

            a, b = edge[0], edge[1]

            if a == node:
                neighbors.append(b)
            elif b == node:
                neighbors.append(a)

        return neighbors

    if hasattr(graph, "edge_list"):
        neighbors = []
        for a, b in graph.edge_list:
            if a == node:
                neighbors.append(b)
            elif b == node:
                neighbors.append(a)
        return neighbors

    raise TypeError("graph must expose neighbors(node), adj, edges, or edge_list")


def route_sol_anchored_hop_by_hop(
    graph: Any,
    source: str,
    target: str,
    receiver_ephemeral_id: str,
    sol_id: str,
    epoch: str,
    session_nonce: str,
    node_scores: Dict[str, float],
    seed: str,
    hop_budget: int = 12,
) -> Dict[str, Any]:
    """
    Route from source using Sol-anchored pressure-weighted hop-by-hop selection.

    The target is used only as simulation delivery condition.
    Routing pressure is based on sol_anchor_alias, not a stable target identity.
    """
    if hop_budget < 1:
        raise ValueError("hop_budget must be >= 1")

    sol_anchor_alias = derive_sol_anchor_alias(
        receiver_ephemeral_id=receiver_ephemeral_id,
        sol_id=sol_id,
        epoch=epoch,
        session_nonce=session_nonce,
    )

    current = source
    path: NodePath = [source]
    visited: Set[str] = {source}
    hop_weights: List[Dict[str, float]] = []

    for hop_index in range(hop_budget):
        if current == target:
            break

        neighbors = graph_neighbors(graph, current)
        if not neighbors:
            break

        weighted: List[Tuple[str, float]] = []

        for candidate in neighbors:
            candidate_neighbors = graph_neighbors(graph, candidate)
            weight = next_hop_weight(
                current=current,
                candidate_next_hop=candidate,
                neighbors_of_candidate=candidate_neighbors,
                sol_anchor_alias=sol_anchor_alias,
                node_scores=node_scores,
                seed=f"{seed}:hop:{hop_index}",
                visited=visited,
            )
            weighted.append((candidate, weight))

        chosen = weighted_random_choice(
            weighted,
            seed=f"{seed}:choice:{hop_index}:{current}",
        )

        hop_weights.append({node: weight for node, weight in weighted})

        path.append(chosen)
        visited.add(chosen)
        current = chosen

    delivered = current == target
    loop_detected = len(path) != len(set(path))

    return {
        "policy": "sol_anchored_hop_by_hop",
        "source": source,
        "target": target,
        "sol_anchor_alias": sol_anchor_alias,
        "path": path,
        "delivered": delivered,
        "hop_count": max(0, len(path) - 1),
        "hop_budget": hop_budget,
        "loop_detected": loop_detected,
        "hop_weights": hop_weights,
    }


def path_overlap_ratio(path_a: NodePath, path_b: NodePath) -> float:
    if not path_a or not path_b:
        return 0.0

    a = set(path_a)
    b = set(path_b)
    return len(a & b) / len(a | b)


if __name__ == "__main__":
    import json
    from pathlib import Path

    from compare_node_score_reset_v01 import build_pre_reset_flv_scores
    from path_sampler_v01 import select_source_target
    from topology_v01 import generate_topology

    config = json.loads(Path("experiments/example.json").read_text())
    graph = generate_topology(config, "sol-hop-demo")
    source, target = select_source_target(graph, "sol-hop-demo:pair")

    policy_cfg = config.get("policy", {})
    route_count = int(policy_cfg.get("route_count", 3))
    fractal_id = int(policy_cfg.get("fractal_count", 36))

    flv = build_pre_reset_flv_scores(
        graph=graph,
        source=source,
        target=target,
        route_count=route_count,
        fractal_id=fractal_id,
        seed="sol-hop-demo",
        pre_reset_epochs=5,
    )

    result = route_sol_anchored_hop_by_hop(
        graph=graph,
        source=source,
        target=target,
        receiver_ephemeral_id="receiver-demo-ephemeral",
        sol_id="sol-demo",
        epoch="1",
        session_nonce="nonce-demo",
        node_scores=flv["node_scores"],
        seed="sol-hop-demo",
        hop_budget=12,
    )

    print("Policy:", result["policy"])
    print("Source:", result["source"])
    print("Target:", result["target"])
    print("Path:", result["path"])
    print("Delivered:", result["delivered"])
    print("Hop count:", result["hop_count"])
    print("Loop detected:", result["loop_detected"])
    print("Anchor alias prefix:", result["sol_anchor_alias"][:16])
