# tests/test_dome_v01.py

import pytest

from dome_v01 import Dome


def test_accept_valid_fragments():
    dome = Dome()

    assert dome.should_accept(b"hello") is True
    assert dome.should_accept(b"") is True
    assert dome.rejected_count == 0


def test_reject_oversized_fragment():
    dome = Dome()
    oversized = b"x" * (Dome.MAX_FRAGMENT_SIZE + 1)

    assert dome.should_accept(oversized) is False
    assert dome.rejected_count == 1


def test_reject_null_sequence_anomaly():
    dome = Dome()
    bad = b"a" + (b"\x00" * (Dome.MAX_NULL_RUN + 1)) + b"b"

    assert dome.should_accept(bad) is False
    assert dome.rejected_count == 1


def test_wrap_unwrap_roundtrip():
    dome = Dome()
    fragment = b"hello dome"
    metadata = "route=1"

    wrapped = dome.wrap_fragment(fragment, metadata=metadata)
    unwrapped, recovered_metadata = dome.unwrap_fragment(wrapped)

    assert unwrapped == fragment
    assert recovered_metadata == metadata


def test_rejection_rate_tracking():
    dome = Dome()

    dome.should_accept(b"ok")
    dome.should_accept(b"\x00" * (Dome.MAX_NULL_RUN + 1))

    assert dome.rejected_count == 1
    assert dome.total_checked == 2
    assert dome.get_rejection_rate() == 0.5


def test_unwrap_rejects_bad_magic():
    dome = Dome()

    with pytest.raises(ValueError):
        dome.unwrap_fragment(b"BAD!" + b"\x01" + b"\x00" * 8)
