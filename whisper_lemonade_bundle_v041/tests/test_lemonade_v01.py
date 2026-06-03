# tests/test_lemonade_v01.py

from lemonade_v01 import Lemonade


def test_detect_overflow():
    lemonade = Lemonade()
    assert lemonade.detect_overflow(10) is False
    assert lemonade.detect_overflow(Lemonade.MAX_QUEUE_DEPTH + 1) is True
    assert lemonade.get_threat_level() >= 2


def test_detect_spam():
    lemonade = Lemonade()
    assert lemonade.detect_spam(100.0) is False
    assert lemonade.detect_spam(Lemonade.MAX_FRAGMENT_RATE + 1) is True
    assert "spam" in lemonade.report().signals


def test_detect_poison():
    lemonade = Lemonade()
    assert lemonade.detect_poison(b"clean") is False
    assert lemonade.detect_poison(b"prefix WHISPER_POISON suffix") is True
    assert "poison" in lemonade.report().signals


def test_detect_oversize():
    lemonade = Lemonade()
    bad = b"x" * (Lemonade.MAX_FRAGMENT_SIZE + 1)
    assert lemonade.detect_oversize(b"ok") is False
    assert lemonade.detect_oversize(bad) is True
    assert "oversize" in lemonade.report().signals


def test_detect_replay():
    lemonade = Lemonade()
    assert lemonade.detect_replay(7) is False
    assert lemonade.detect_replay(7) is True
    assert "replay" in lemonade.report().signals


def test_detect_entropy_drop():
    lemonade = Lemonade()
    assert lemonade.detect_entropy_drop(bytes(range(256))) is False
    assert lemonade.detect_entropy_drop(b"\x00" * 256) is True
    assert "entropy_drop" in lemonade.report().signals


def test_detect_state_anomaly_and_threat_escalation():
    lemonade = Lemonade()
    assert lemonade.detect_state_anomaly({"valid": True, "issues": []}) is False
    assert lemonade.detect_state_anomaly({"valid": False, "issues": ["bad"]}) is True
    assert lemonade.get_threat_level() >= 3
    assert "state_anomaly" in lemonade.report().signals


def test_scan_fragment_report_blocks_when_many_signals():
    lemonade = Lemonade()
    report = lemonade.scan_fragment(
        fragment=b"WHISPER_POISON" + (b"\x00" * 1001),
        fragment_id=1,
        queue_depth=Lemonade.MAX_QUEUE_DEPTH + 1,
        fragment_rate=Lemonade.MAX_FRAGMENT_RATE + 1,
        validation_report={"valid": False, "issues": ["bad"]},
    )
    assert report.threat_level >= Lemonade.BLOCK_THRESHOLD
    assert report.blocked is True
    assert "poison" in report.signals
    assert "overflow" in report.signals
    assert "spam" in report.signals
    assert "state_anomaly" in report.signals


def test_scan_fragment_stateless_does_not_poison_global_threat_level():
    lemonade = Lemonade()

    report = lemonade.scan_fragment_stateless(
        fragment=b"WHISPER_POISON" + (b"\x00" * 1001),
        fragment_id=123,
        queue_depth=Lemonade.MAX_QUEUE_DEPTH + 1,
        fragment_rate=Lemonade.MAX_FRAGMENT_RATE + 1,
        validation_report={"valid": False, "issues": ["bad"]},
    )

    assert report.blocked is True
    assert lemonade.get_threat_level() == 0
    assert lemonade.report().signals == []


def test_scan_fragment_stateless_preserves_replay_memory():
    lemonade = Lemonade()

    first = lemonade.scan_fragment_stateless(
        fragment=b"normal",
        fragment_id=7,
        validation_report={"valid": True, "issues": []},
    )
    second = lemonade.scan_fragment_stateless(
        fragment=b"normal",
        fragment_id=7,
        validation_report={"valid": True, "issues": []},
    )

    assert first.blocked is False
    assert "replay" in second.signals
