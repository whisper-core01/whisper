# dome_v01.py
# Requires Python 3.8+

"""
Dome v0.1.0 — Filtering layer + minimal envelope.

Purpose:
    Add simple fragment accept/reject rules and a minimal reversible envelope.

Scope:
    - reject oversized fragments > 10 MiB;
    - reject long null byte sequences > 1000 bytes;
    - wrap/unwrap fragments with length + metadata;
    - track rejection rate.

Security warning:
    Dome is not a WAF, not a malware scanner, and not authenticated envelope
    encryption. It is a minimal MVP filtering/envelope skeleton only.
"""

from __future__ import annotations

import struct
from typing import Tuple


__version__ = "0.1.0"
__all__ = ["Dome"]


class Dome:
    """Filtering layer + envelope."""

    MAGIC = b"DOME"
    VERSION = 1
    MAX_FRAGMENT_SIZE = 10 * 1024 * 1024
    MAX_NULL_RUN = 1000

    def __init__(self):
        self.rejected_count = 0
        self.total_checked = 0

    def should_accept(self, fragment: bytes) -> bool:
        """
        Return True when fragment passes MVP filters.

        Rules:
            - type must be bytes/bytearray;
            - size must be 0..10 MiB;
            - no null byte sequence longer than 1000 bytes.
        """
        self.total_checked += 1

        if not isinstance(fragment, (bytes, bytearray)):
            self.rejected_count += 1
            return False

        fragment = bytes(fragment)

        if len(fragment) > self.MAX_FRAGMENT_SIZE:
            self.rejected_count += 1
            return False

        if b"\x00" * (self.MAX_NULL_RUN + 1) in fragment:
            self.rejected_count += 1
            return False

        return True

    def wrap_fragment(self, fragment: bytes, metadata: str = "") -> bytes:
        """
        Add minimal envelope.

        Format:
            MAGIC[4] VERSION[1] metadata_len[4] fragment_len[4] metadata fragment
        """
        if not self.should_accept(fragment):
            raise ValueError("fragment rejected by Dome filters")

        if not isinstance(metadata, str):
            raise TypeError("metadata must be a str")

        metadata_bytes = metadata.encode("utf-8")
        fragment = bytes(fragment)

        header = (
            self.MAGIC
            + bytes([self.VERSION])
            + struct.pack(">I", len(metadata_bytes))
            + struct.pack(">I", len(fragment))
        )

        return header + metadata_bytes + fragment

    def unwrap_fragment(self, wrapped: bytes) -> Tuple[bytes, str]:
        """Remove minimal envelope and return (fragment, metadata)."""
        if not isinstance(wrapped, (bytes, bytearray)):
            raise TypeError("wrapped must be bytes")

        wrapped = bytes(wrapped)
        min_size = 4 + 1 + 4 + 4

        if len(wrapped) < min_size:
            raise ValueError("wrapped fragment too short")

        magic = wrapped[:4]
        version = wrapped[4]

        if magic != self.MAGIC:
            raise ValueError("invalid Dome magic")
        if version != self.VERSION:
            raise ValueError("unsupported Dome version")

        metadata_len = struct.unpack(">I", wrapped[5:9])[0]
        fragment_len = struct.unpack(">I", wrapped[9:13])[0]

        expected_len = min_size + metadata_len + fragment_len
        if len(wrapped) != expected_len:
            raise ValueError("wrapped length mismatch")

        metadata_start = min_size
        metadata_end = metadata_start + metadata_len
        fragment_start = metadata_end

        metadata = wrapped[metadata_start:metadata_end].decode("utf-8")
        fragment = wrapped[fragment_start:]

        return fragment, metadata

    def get_rejection_rate(self) -> float:
        """Return rejected / total."""
        if self.total_checked == 0:
            return 0.0

        return self.rejected_count / self.total_checked


if __name__ == "__main__":
    dome = Dome()
    fragment = b"hello dome"

    wrapped = dome.wrap_fragment(fragment, metadata="demo")
    unwrapped, metadata = dome.unwrap_fragment(wrapped)

    print("=== Dome v0.1 Smoke Test ===")
    print(f"wrapped size:     {len(wrapped)}")
    print(f"metadata:         {metadata}")
    print(f"roundtrip:        {unwrapped == fragment}")
    print(f"rejection rate:   {dome.get_rejection_rate():.3f}")
