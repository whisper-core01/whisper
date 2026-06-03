# bal_v01.py
# Requires Python 3.8+

"""
BAL v0.1.0 — Biological Adaptive Lanes.

Purpose:
    Minimal adaptive transport skeleton using parallel in-memory lanes.

Scope:
    - create N lanes;
    - round-robin distribute fragments;
    - collect fragments back in original order;
    - no network I/O;
    - no Reticulum integration yet.

Security warning:
    BAL is not an anonymity layer, not a congestion-control protocol, and not
    secure routing. It is an MVP transport skeleton only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from loader_v01 import Loader


__version__ = "0.1.0"
__all__ = ["Lane", "BAL"]


@dataclass(frozen=True)
class LaneFragment:
    """Fragment stored with its original global order."""

    index: int
    data: bytes


class Lane:
    """Single transport lane."""

    def __init__(self, lane_id: int):
        if not isinstance(lane_id, int):
            raise TypeError("lane_id must be an int")
        if lane_id < 0:
            raise ValueError("lane_id must be >= 0")

        self.lane_id = lane_id
        self.fragments: List[LaneFragment] = []

    def add_fragment(self, fragment: bytes, index: int) -> None:
        """Add a fragment to this lane with original order index."""
        if not isinstance(fragment, (bytes, bytearray)):
            raise TypeError("fragment must be bytes")
        if not isinstance(index, int):
            raise TypeError("index must be an int")
        if index < 0:
            raise ValueError("index must be >= 0")

        self.fragments.append(LaneFragment(index=index, data=bytes(fragment)))

    def clear(self) -> None:
        """Remove all fragments from this lane."""
        self.fragments.clear()


class BAL:
    """Biological Adaptive Lanes — parallel transport skeleton."""

    def __init__(self, loader: Loader, route_count: int = 3):
        if not isinstance(loader, Loader):
            raise TypeError("loader must be a Loader instance")
        if not isinstance(route_count, int):
            raise TypeError("route_count must be an int")
        if route_count <= 0:
            raise ValueError("route_count must be > 0")

        self.loader = loader
        self.route_count = route_count
        self.lanes = [Lane(i) for i in range(route_count)]

    def distribute(self, fragments: List[bytes]) -> None:
        """Round-robin distribute fragments to lanes."""
        if not isinstance(fragments, list):
            raise TypeError("fragments must be a list")

        self.clear()

        for index, fragment in enumerate(fragments):
            lane = self.lanes[index % self.route_count]
            lane.add_fragment(fragment, index)

    def collect_results(self) -> List[bytes]:
        """Reassemble fragments from all lanes in original order."""
        collected: List[LaneFragment] = []

        for lane in self.lanes:
            collected.extend(lane.fragments)

        collected.sort(key=lambda item: item.index)
        return [item.data for item in collected]

    def lane_loads(self) -> List[int]:
        """Return number of fragments per lane."""
        return [len(lane.fragments) for lane in self.lanes]

    def clear(self) -> None:
        """Clear all lanes."""
        for lane in self.lanes:
            lane.clear()


if __name__ == "__main__":
    from mce_v01 import MCE
    from loader_v01 import Loader

    fragments = [b"fragment_%d" % i for i in range(10)]
    bal = BAL(Loader(MCE(b"whisper-bal-seed")), route_count=3)

    bal.distribute(fragments)
    recovered = bal.collect_results()

    print("=== BAL v0.1 Smoke Test ===")
    print(f"lanes:       {len(bal.lanes)}")
    print(f"lane loads:  {bal.lane_loads()}")
    print(f"roundtrip:   {recovered == fragments}")
