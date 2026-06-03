# voxmesh_v01.py
# Requires Python 3.8+

"""
VoxMesh v0.1.0 — 36 living fractals skeleton.

Purpose:
    Maintain 36 deterministic fractal state machines and measure divergence.

Scope:
    - create 36 fractals;
    - mutate all fractals with entropy;
    - compute state diversity score;
    - coherence check;
    - deterministic per seed.

Security warning:
    VoxMesh is not a randomness beacon, not consensus, and not a cryptographic
    entropy extractor. It is a simplified MVP state-divergence skeleton.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import List


__version__ = "0.1.0"
__all__ = ["Fractal", "VoxMesh"]


def h32(data: bytes) -> bytes:
    """Portable 32-byte hash helper."""
    return hashlib.blake2b(data, digest_size=32).digest()


@dataclass
class Fractal:
    """Single fractal state machine."""

    fractal_id: int
    state: bytes
    steps: int = 0

    def __init__(self, fractal_id: int, seed: bytes):
        if not isinstance(fractal_id, int):
            raise TypeError("fractal_id must be an int")
        if fractal_id < 0:
            raise ValueError("fractal_id must be >= 0")
        if not isinstance(seed, (bytes, bytearray)):
            raise TypeError("seed must be bytes")

        self.fractal_id = fractal_id
        self.state = h32(
            b"voxmesh:fractal:init|"
            + fractal_id.to_bytes(2, "big")
            + b"|"
            + bytes(seed)
        )
        self.steps = 0

    def mutate(self, entropy: bytes) -> None:
        """Evolve state via BLAKE2b(state + entropy + fractal_id + steps)."""
        if not isinstance(entropy, (bytes, bytearray)):
            raise TypeError("entropy must be bytes")

        self.state = h32(
            b"voxmesh:fractal:mutate|"
            + self.fractal_id.to_bytes(2, "big")
            + b"|"
            + self.steps.to_bytes(8, "big")
            + b"|"
            + self.state
            + b"|"
            + bytes(entropy)
        )
        self.steps += 1

    def get_state_hex(self, n: int = 8) -> str:
        """Return first n bytes of state as hex. Defaults to 8 bytes."""
        if not isinstance(n, int):
            raise TypeError("n must be an int")
        if n <= 0:
            raise ValueError("n must be > 0")

        return self.state[:n].hex()


class VoxMesh:
    """36 living fractals."""

    FRACTAL_COUNT = 36

    def __init__(self, seed: bytes):
        if not isinstance(seed, (bytes, bytearray)):
            raise TypeError("seed must be bytes")

        self.seed = bytes(seed)
        self.fractals: List[Fractal] = [
            Fractal(i, self.seed)
            for i in range(self.FRACTAL_COUNT)
        ]

    def mutate_all(self, entropy: bytes) -> None:
        """Evolve all 36 fractals with same entropy."""
        for fractal in self.fractals:
            fractal.mutate(entropy)

    def get_divergence_score(self) -> float:
        """
        Measure state diversity across fractals: 0..1.

        Uses unique state count divided by fractal count.
        0.0 means no fractals or no diversity.
        1.0 means all fractal states are unique.
        """
        if not self.fractals:
            return 0.0

        unique = len({fractal.state for fractal in self.fractals})
        return unique / len(self.fractals)

    def coherence_check(self) -> bool:
        """
        Return True if all fractals are structurally coherent.

        Coherence here means:
            - exactly 36 fractals;
            - IDs are 0..35;
            - all states are 32 bytes;
            - all step counters are equal.
        """
        if len(self.fractals) != self.FRACTAL_COUNT:
            return False

        expected_ids = list(range(self.FRACTAL_COUNT))
        actual_ids = [fractal.fractal_id for fractal in self.fractals]
        if actual_ids != expected_ids:
            return False

        if any(not isinstance(fractal.state, bytes) or len(fractal.state) != 32 for fractal in self.fractals):
            return False

        steps = {fractal.steps for fractal in self.fractals}
        if len(steps) != 1:
            return False

        return True

    def get_states_hex(self, n: int = 8) -> List[str]:
        """Return truncated hex states for all fractals."""
        return [fractal.get_state_hex(n) for fractal in self.fractals]


if __name__ == "__main__":
    mesh = VoxMesh(b"whisper-voxmesh-seed")

    print("=== VoxMesh v0.1 Smoke Test ===")
    print(f"fractals:          {len(mesh.fractals)}")
    print(f"coherent init:     {mesh.coherence_check()}")
    print(f"divergence init:   {mesh.get_divergence_score():.3f}")

    for i in range(5):
        mesh.mutate_all(b"entropy_%d" % i)

    print(f"coherent after:    {mesh.coherence_check()}")
    print(f"divergence after:  {mesh.get_divergence_score():.3f}")
    print(f"first 5 states:    {mesh.get_states_hex()[:5]}")
