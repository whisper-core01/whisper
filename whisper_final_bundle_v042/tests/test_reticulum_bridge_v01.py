# tests/test_reticulum_bridge_v01.py

import pytest

from reticulum_bridge_v01 import ReticulumBridge


def test_bridge_roundtrip():
    bridge = ReticulumBridge()
    packet = bridge.encapsulate(b"payload", lane_id=1, sequence_id=42, metadata="demo")
    decoded = bridge.decapsulate(packet)

    assert decoded.payload == b"payload"
    assert decoded.lane_id == 1
    assert decoded.sequence_id == 42
    assert decoded.metadata == "demo"


def test_bridge_batch_encapsulate():
    bridge = ReticulumBridge()
    packets = bridge.batch_encapsulate([b"a", b"b", b"c"], lane_id=2, metadata="batch")

    decoded = [bridge.decapsulate(packet) for packet in packets]

    assert [item.sequence_id for item in decoded] == [0, 1, 2]
    assert [item.payload for item in decoded] == [b"a", b"b", b"c"]


def test_bridge_rejects_bad_magic():
    bridge = ReticulumBridge()

    packet = bridge.encapsulate(b"payload", lane_id=1, sequence_id=1)
    bad = b"BAD!" + packet[4:]

    with pytest.raises(ValueError):
        bridge.decapsulate(bad)


def test_bridge_rejects_invalid_lane_id():
    bridge = ReticulumBridge()

    with pytest.raises(ValueError):
        bridge.encapsulate(b"payload", lane_id=70000, sequence_id=1)
