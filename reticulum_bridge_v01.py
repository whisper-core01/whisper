# reticulum_bridge_v01.py
# Requires Python 3.8+

"""
ReticulumBridge v0.1.0 — Simple encapsulation skeleton.

Purpose:
    Provide a minimal transport envelope shaped like a future Reticulum bridge.

Scope:
    - no real Reticulum dependency;
    - no network I/O;
    - deterministic envelope format;
    - encode/decode bridge packets;
    - metadata preserved as UTF-8 string.

Security warning:
    This is NOT Reticulum integration.
    This is NOT encrypted transport.
    This is NOT authenticated transport.
    This is a bridge skeleton only.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import List


__version__ = "0.1.0"
__all__ = ["BridgePacket", "ReticulumBridge"]


@dataclass(frozen=True)
class BridgePacket:
    """Decoded bridge packet."""

    lane_id: int
    sequence_id: int
    metadata: str
    payload: bytes


class ReticulumBridge:
    """
    Minimal encapsulation bridge.

    Format:
        MAGIC[4] VERSION[1] lane_id[2] sequence_id[8]
        metadata_len[4] payload_len[4] metadata payload
    """

    MAGIC = b"RBRG"
    VERSION = 1
    HEADER_SIZE = 4 + 1 + 2 + 8 + 4 + 4
    MAX_METADATA_SIZE = 4096
    MAX_PAYLOAD_SIZE = 10 * 1024 * 1024

    def encapsulate(
        self,
        payload: bytes,
        lane_id: int,
        sequence_id: int,
        metadata: str = "",
    ) -> bytes:
        """Wrap payload into a bridge packet."""
        if not isinstance(payload, (bytes, bytearray)):
            raise TypeError("payload must be bytes")
        if not isinstance(lane_id, int):
            raise TypeError("lane_id must be an int")
        if not isinstance(sequence_id, int):
            raise TypeError("sequence_id must be an int")
        if not isinstance(metadata, str):
            raise TypeError("metadata must be a str")

        payload = bytes(payload)
        metadata_bytes = metadata.encode("utf-8")

        if lane_id < 0 or lane_id > 0xFFFF:
            raise ValueError("lane_id must fit in uint16")
        if sequence_id < 0 or sequence_id >= 2**64:
            raise ValueError("sequence_id must fit in uint64")
        if len(metadata_bytes) > self.MAX_METADATA_SIZE:
            raise ValueError("metadata too large")
        if len(payload) > self.MAX_PAYLOAD_SIZE:
            raise ValueError("payload too large")

        header = (
            self.MAGIC
            + bytes([self.VERSION])
            + struct.pack(">H", lane_id)
            + struct.pack(">Q", sequence_id)
            + struct.pack(">I", len(metadata_bytes))
            + struct.pack(">I", len(payload))
        )

        return header + metadata_bytes + payload

    def decapsulate(self, packet: bytes) -> BridgePacket:
        """Decode a bridge packet."""
        if not isinstance(packet, (bytes, bytearray)):
            raise TypeError("packet must be bytes")

        packet = bytes(packet)

        if len(packet) < self.HEADER_SIZE:
            raise ValueError("packet too short")

        magic = packet[:4]
        version = packet[4]

        if magic != self.MAGIC:
            raise ValueError("invalid bridge magic")
        if version != self.VERSION:
            raise ValueError("unsupported bridge version")

        lane_id = struct.unpack(">H", packet[5:7])[0]
        sequence_id = struct.unpack(">Q", packet[7:15])[0]
        metadata_len = struct.unpack(">I", packet[15:19])[0]
        payload_len = struct.unpack(">I", packet[19:23])[0]

        if metadata_len > self.MAX_METADATA_SIZE:
            raise ValueError("metadata too large")
        if payload_len > self.MAX_PAYLOAD_SIZE:
            raise ValueError("payload too large")

        expected_len = self.HEADER_SIZE + metadata_len + payload_len
        if len(packet) != expected_len:
            raise ValueError("packet length mismatch")

        metadata_start = self.HEADER_SIZE
        metadata_end = metadata_start + metadata_len
        payload_start = metadata_end

        metadata = packet[metadata_start:metadata_end].decode("utf-8")
        payload = packet[payload_start:]

        return BridgePacket(
            lane_id=lane_id,
            sequence_id=sequence_id,
            metadata=metadata,
            payload=payload,
        )

    def batch_encapsulate(self, payloads: List[bytes], lane_id: int, metadata: str = "") -> List[bytes]:
        """Encapsulate a list of payloads with increasing sequence IDs."""
        if not isinstance(payloads, list):
            raise TypeError("payloads must be a list")

        return [
            self.encapsulate(
                payload=payload,
                lane_id=lane_id,
                sequence_id=i,
                metadata=metadata,
            )
            for i, payload in enumerate(payloads)
        ]


if __name__ == "__main__":
    bridge = ReticulumBridge()
    packet = bridge.encapsulate(b"hello bridge", lane_id=2, sequence_id=7, metadata="demo")
    decoded = bridge.decapsulate(packet)

    print("=== ReticulumBridge v0.1 Smoke Test ===")
    print(f"packet size:  {len(packet)}")
    print(f"lane_id:      {decoded.lane_id}")
    print(f"sequence_id:  {decoded.sequence_id}")
    print(f"metadata:     {decoded.metadata}")
    print(f"roundtrip:    {decoded.payload == b'hello bridge'}")
