# loader_v01.py
# Requires Python 3.8+

"""
Loader v0.1.0 — Deterministic decision layer for Whisper MVP.

Purpose:
    Decide fragmentation size, route count, and retry policy.

Scope:
    - deterministic rules;
    - no AI;
    - no Reticulum integration;
    - no network I/O.

Security warning:
    Loader decisions are operational hints, not security guarantees.
"""

from __future__ import annotations

from typing import Dict

from mce_v01 import MCE


__version__ = "0.1.0"
__all__ = ["Loader"]


class Loader:
    """Decision layer: fragmentation + routing strategy."""

    def __init__(self, mce: MCE):
        if not isinstance(mce, MCE):
            raise TypeError("mce must be an MCE instance")
        self.mce = mce

    def decide_fragment_size(self, payload_size: int) -> int:
        """
        Return fragment size in bytes: 64, 256, 512 or 1024.

        Rules:
            <= 1 KiB   -> 64
            <= 8 KiB   -> 256
            <= 64 KiB  -> 512
            > 64 KiB   -> 1024
        """
        if not isinstance(payload_size, int):
            raise TypeError("payload_size must be an int")
        if payload_size < 0:
            raise ValueError("payload_size must be >= 0")

        if payload_size <= 1024:
            return 64
        if payload_size <= 8192:
            return 256
        if payload_size <= 65536:
            return 512
        return 1024

    def decide_route_count(self, mce_state_hex: str) -> int:
        """
        Return 1-3 parallel routes based on MCE state hex.

        This is deterministic and intentionally simple.
        It is not Reticulum routing.
        """
        if not isinstance(mce_state_hex, str):
            raise TypeError("mce_state_hex must be a str")
        if not mce_state_hex:
            raise ValueError("mce_state_hex must not be empty")

        try:
            value = int(mce_state_hex[:8], 16)
        except ValueError as exc:
            raise ValueError("mce_state_hex must start with hex characters") from exc

        return (value % 3) + 1

    def decide_retry_policy(self) -> Dict[str, float]:
        """
        Return deterministic retry policy based on current MCE state.

        Returns:
            {
                "max_retries": int,
                "backoff": float
            }
        """
        state_hex = self.mce.snapshot().hex(8)
        value = int(state_hex[:8], 16)

        max_retries = 2 + (value % 3)  # 2..4
        backoff = 0.05 * (1 + ((value >> 4) % 5))  # 0.05..0.25

        return {
            "max_retries": int(max_retries),
            "backoff": round(float(backoff), 3),
        }

    def decide_all(self, payload_size: int) -> Dict[str, object]:
        """Return all loader decisions in one deterministic dict."""
        state_hex = self.mce.snapshot().hex(8)

        return {
            "fragment_size": self.decide_fragment_size(payload_size),
            "route_count": self.decide_route_count(state_hex),
            "retry_policy": self.decide_retry_policy(),
            "mce_state_hex": state_hex,
        }


if __name__ == "__main__":
    mce = MCE(b"whisper-loader-seed")
    loader = Loader(mce)

    for size in [12, 1024, 4096, 16384, 1000000]:
        print(f"payload_size={size} -> {loader.decide_all(size)}")
