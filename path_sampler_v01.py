from __future__ import annotations

import random
from collections import deque
from typing import List, Optional

from topology_v01 import TopologyGraph


Path = List[str]


def shortest_path(graph: TopologyGraph, source: str, target: str) -> Optional[Path]:
    """Return the shortest path between source and target using BFS."""
    if source not in graph.adjacency:
        raise ValueError(f"Unknown source node: {source}")
    if target not in graph.adjacency:
        raise ValueError(f"Unknown target node: {target}")
    if source == target:
        return [source]

    visited = {source}
    queue = deque([[source]])

    while queue:
        path = queue.popleft()
        node = path[-1]

        for neighbor in sorted(graph.adjacency[node]):
            if neighbor in visited:
                continue

            next_path = path + [neighbor]
            if neighbor == target:
                return next_path

            visited.add(neighbor)
            queue.append(next_path)

    return None


def random_simple_path(
    graph: TopologyGraph,
    source: str,
    target: str,
    seed: str,
    max_steps: Optional[int] = None,
) -> Optional[Path]:
    """Return a deterministic random simple path, or None if no path is found."""
    if source not in graph.adjacency:
        raise ValueError(f"Unknown source node: {source}")
    if target not in graph.adjacency:
        raise ValueError(f"Unknown target node: {target}")
    if source == target:
        return [source]

    rng = random.Random(seed)
    max_steps = max_steps or max(4, graph.node_count * 2)

    current = source
    path = [source]
    visited = {source}

    for _ in range(max_steps):
        neighbors = [n for n in graph.adjacency[current] if n not in visited]

        if not neighbors:
            return None

        rng.shuffle(neighbors)

        # Prefer target if directly available after shuffle, to avoid pointless wandering.
        if target in neighbors:
            path.append(target)
            return path

        current = neighbors[0]
        path.append(current)
        visited.add(current)

    return None


def candidate_paths(
    graph: TopologyGraph,
    source: str,
    target: str,
    seed: str,
    k: int = 3,
) -> List[Path]:
    """
    Return up to k deterministic candidate paths.

    The first candidate is shortest_path if available.
    Remaining candidates are deterministic random simple paths.
    Duplicate paths are removed.
    """
    if k < 1:
        raise ValueError("k must be >= 1")

    paths: List[Path] = []

    sp = shortest_path(graph, source, target)
    if sp is not None:
        paths.append(sp)

    attempts = max(k * 5, 10)
    for i in range(attempts):
        if len(paths) >= k:
            break

        rp = random_simple_path(graph, source, target, f"{seed}:random:{i}")
        if rp is None:
            continue
        if rp not in paths:
            paths.append(rp)

    return paths


def select_source_target(graph: TopologyGraph, seed: str) -> tuple[str, str]:
    """Select a deterministic source/target pair."""
    if graph.node_count < 2:
        raise ValueError("graph must contain at least two nodes")

    rng = random.Random(seed)
    source, target = rng.sample(graph.nodes, 2)
    return source, target
