from __future__ import annotations

from typing import Iterable, List, Tuple


Path = List[str]
Edge = Tuple[str, str]


def path_edges(path: Path) -> set[Edge]:
    """Return normalized undirected edges for a path."""
    edges: set[Edge] = set()

    for a, b in zip(path, path[1:]):
        edges.add((min(a, b), max(a, b)))

    return edges


def path_overlap(path_a: Path, path_b: Path) -> float:
    """
    Return edge-overlap ratio between two paths.

    0.0 means no shared edges.
    1.0 means complete overlap relative to the smaller path.
    """
    edges_a = path_edges(path_a)
    edges_b = path_edges(path_b)

    if not edges_a and not edges_b:
        return 1.0

    if not edges_a or not edges_b:
        return 0.0

    shared = len(edges_a & edges_b)
    denom = min(len(edges_a), len(edges_b))

    if denom == 0:
        return 0.0

    return shared / denom


def mean_path_overlap(paths: Iterable[Path]) -> float:
    """Return mean pairwise path overlap."""
    path_list = list(paths)

    if len(path_list) < 2:
        return 0.0

    overlaps: list[float] = []

    for i in range(len(path_list)):
        for j in range(i + 1, len(path_list)):
            overlaps.append(path_overlap(path_list[i], path_list[j]))

    return sum(overlaps) / len(overlaps) if overlaps else 0.0


def unique_path_ratio(paths: Iterable[Path]) -> float:
    """Return unique paths / total paths."""
    path_list = list(paths)

    if not path_list:
        return 0.0

    unique = {tuple(p) for p in path_list}
    return len(unique) / len(path_list)


def summarize_paths(paths: Iterable[Path]) -> dict:
    """Return minimal v0.6.0 path metrics."""
    path_list = list(paths)

    return {
        "path_count": len(path_list),
        "unique_path_ratio": unique_path_ratio(path_list),
        "path_overlap": mean_path_overlap(path_list),
    }
