from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple


@dataclass(frozen=True)
class TopologyGraph:
    topology_type: str
    nodes: List[str]
    edges: List[Tuple[str, str]]
    adjacency: Dict[str, Set[str]]

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)


def _make_adjacency(nodes: List[str], edges: List[Tuple[str, str]]) -> Dict[str, Set[str]]:
    adjacency = {n: set() for n in nodes}
    for a, b in edges:
        if a == b:
            continue
        adjacency[a].add(b)
        adjacency[b].add(a)
    return adjacency


def _normalize_edges(edges: Set[Tuple[str, str]]) -> List[Tuple[str, str]]:
    return sorted((min(a, b), max(a, b)) for a, b in edges if a != b)


def generate_erdos_renyi(node_count: int, edge_probability: float, seed: str) -> TopologyGraph:
    rng = random.Random(seed)
    nodes = [f"n{i}" for i in range(node_count)]
    edges: Set[Tuple[str, str]] = set()

    for i in range(node_count):
        for j in range(i + 1, node_count):
            if rng.random() < edge_probability:
                edges.add((nodes[i], nodes[j]))

    edge_list = _normalize_edges(edges)
    return TopologyGraph("erdos_renyi", nodes, edge_list, _make_adjacency(nodes, edge_list))


def generate_barabasi_albert(node_count: int, m: int, seed: str) -> TopologyGraph:
    if node_count < 2:
        raise ValueError("node_count must be >= 2")
    if m < 1:
        raise ValueError("m must be >= 1")

    rng = random.Random(seed)
    nodes = [f"n{i}" for i in range(node_count)]
    edges: Set[Tuple[str, str]] = set()

    # Start with a small connected core.
    initial = min(m + 1, node_count)
    for i in range(initial):
        for j in range(i + 1, initial):
            edges.add((nodes[i], nodes[j]))

    degree_pool: List[str] = []
    for a, b in edges:
        degree_pool.extend([a, b])

    for i in range(initial, node_count):
        new_node = nodes[i]
        targets: Set[str] = set()

        while len(targets) < min(m, i):
            if degree_pool:
                targets.add(rng.choice(degree_pool))
            else:
                targets.add(nodes[rng.randrange(i)])

        for target in targets:
            edges.add((new_node, target))
            degree_pool.extend([new_node, target])

    edge_list = _normalize_edges(edges)
    return TopologyGraph("barabasi_albert", nodes, edge_list, _make_adjacency(nodes, edge_list))


def generate_watts_strogatz(node_count: int, k: int, beta: float, seed: str) -> TopologyGraph:
    if node_count < 3:
        raise ValueError("node_count must be >= 3")
    if k < 2 or k >= node_count or k % 2 != 0:
        raise ValueError("k must be even and satisfy 2 <= k < node_count")

    rng = random.Random(seed)
    nodes = [f"n{i}" for i in range(node_count)]
    edges: Set[Tuple[str, str]] = set()

    # Ring lattice.
    half_k = k // 2
    for i in range(node_count):
        for offset in range(1, half_k + 1):
            j = (i + offset) % node_count
            edges.add((nodes[i], nodes[j]))

    # Rewire one endpoint with probability beta.
    rewired: Set[Tuple[str, str]] = set()
    for a, b in list(edges):
        if rng.random() < beta:
            possible = [n for n in nodes if n != a and (min(a, n), max(a, n)) not in edges]
            if possible:
                new_b = rng.choice(possible)
                rewired.add((a, new_b))
            else:
                rewired.add((a, b))
        else:
            rewired.add((a, b))

    edge_list = _normalize_edges(rewired)
    return TopologyGraph("watts_strogatz", nodes, edge_list, _make_adjacency(nodes, edge_list))


def generate_topology(config: dict, seed: str) -> TopologyGraph:
    topology = config.get("topology", {})
    topology_type = topology.get("type", "erdos_renyi")
    node_count = int(topology.get("node_count", 100))

    if topology_type == "erdos_renyi":
        return generate_erdos_renyi(
            node_count=node_count,
            edge_probability=float(topology.get("edge_probability", 0.05)),
            seed=seed,
        )

    if topology_type == "barabasi_albert":
        return generate_barabasi_albert(
            node_count=node_count,
            m=int(topology.get("m", 3)),
            seed=seed,
        )

    if topology_type == "watts_strogatz":
        return generate_watts_strogatz(
            node_count=node_count,
            k=int(topology.get("k", 4)),
            beta=float(topology.get("beta", 0.1)),
            seed=seed,
        )

    raise ValueError(f"Unsupported topology type: {topology_type}")
