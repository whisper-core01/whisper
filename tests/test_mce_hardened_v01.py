# tests/test_mce_hardened_v01.py

import pytest

from mce_hardened_v01 import MCEHardened


SEED = b"whisper-mce-hardened-seed"


def test_state_validation_passes_on_init():
    mce = MCEHardened(SEED)

    assert mce.validate_state() is True
    assert mce.coherence_check()["valid"] is True


def test_state_validation_fails_on_corrupted_state():
    mce = MCEHardened(SEED)
    mce.state = b"bad"  # deliberate corruption

    assert mce.validate_state() is False

    report = mce.coherence_check()
    assert report["valid"] is False
    assert "state hash length is not 32 bytes" in report["issues"]


def test_coherence_check_detects_counter_inconsistency():
    mce = MCEHardened(SEED)
    mce.fragment_counter = -1  # deliberate corruption

    report = mce.coherence_check()

    assert report["valid"] is False
    assert "fragment_counter is negative" in report["issues"]


def test_digest_fragment_checked_returns_all_three_values():
    mce = MCEHardened(SEED)

    transformed, snapshot, validation = mce.digest_fragment_checked(b"fragment")

    assert isinstance(transformed, bytes)
    assert snapshot.fragment_counter == 1
    assert isinstance(validation, dict)
    assert validation["valid"] is True


def test_digest_fragment_checked_refuses_corrupted_pre_state():
    mce = MCEHardened(SEED)
    mce.state = b"bad"

    with pytest.raises(RuntimeError):
        mce.digest_fragment_checked(b"fragment")


def test_stress_1000_fragments_coherence_remains_valid():
    mce = MCEHardened(SEED)

    for i in range(1000):
        fragment = b"fragment_%d" % i
        transformed, snapshot, validation = mce.digest_fragment_checked(fragment)

        assert isinstance(transformed, bytes)
        assert snapshot.fragment_counter == i + 1
        assert validation["valid"] is True

    assert mce.fragment_counter == 1000
    assert mce.validate_state() is True
