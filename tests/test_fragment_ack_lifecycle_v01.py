from __future__ import annotations

import pytest

from fragment_ack_lifecycle_v01 import (
    BearerSignalState,
    FragmentAckLifecycle,
    FragmentAckState,
)


def test_create_fragment_ack_record():
    lifecycle = FragmentAckLifecycle()
    rec = lifecycle.create("frag-001", 1_000)

    assert rec.fragment_id == "frag-001"
    assert rec.state == FragmentAckState.CREATED
    assert rec.attempts == 0
    assert rec.delivery_allowed is True
    assert rec.ack_pending is False
    assert rec.history[-1].event == "created"


def test_send_sets_ack_pending():
    lifecycle = FragmentAckLifecycle()
    lifecycle.create("frag-001", 1_000)

    rec = lifecycle.send("frag-001", 1_100, bearer="reticulum")

    assert rec.state == FragmentAckState.ACK_PENDING
    assert rec.ack_pending is True
    assert rec.sent_at_ms == 1_100
    assert rec.last_attempt_at_ms == 1_100
    assert rec.attempts == 1
    assert rec.bearer == "reticulum"


def test_ack_confirms_fragment():
    lifecycle = FragmentAckLifecycle()
    lifecycle.create("frag-001", 1_000)
    lifecycle.send("frag-001", 1_100, bearer="reticulum")

    rec = lifecycle.ack("frag-001", 1_500)

    assert rec.state == FragmentAckState.ACKED
    assert rec.acked_at_ms == 1_500
    assert rec.is_terminal is True
    assert rec.delivery_allowed is False
    assert rec.history[-1].event == "acked"


def test_timeout_schedules_retry():
    lifecycle = FragmentAckLifecycle(ack_timeout_ms=1_000, retry_backoff_ms=200, max_attempts=3)
    lifecycle.create("frag-001", 0)
    lifecycle.send("frag-001", 100, bearer="reticulum")

    lifecycle.tick(1_099)
    assert lifecycle.get("frag-001").state == FragmentAckState.ACK_PENDING

    lifecycle.tick(1_100)
    assert lifecycle.get("frag-001").state == FragmentAckState.RETRY_SCHEDULED


def test_retry_due_and_retry_resends():
    lifecycle = FragmentAckLifecycle(ack_timeout_ms=1_000, retry_backoff_ms=200, max_attempts=3)
    lifecycle.create("frag-001", 0)
    lifecycle.send("frag-001", 100, bearer="reticulum")

    assert lifecycle.retry_due(1_100) == []

    due = lifecycle.retry_due(1_300)
    assert len(due) == 1
    assert due[0].fragment_id == "frag-001"

    rec = lifecycle.retry("frag-001", 1_300, bearer="reticulum")
    assert rec.state == FragmentAckState.ACK_PENDING
    assert rec.attempts == 2
    assert rec.last_attempt_at_ms == 1_300


def test_failed_after_max_attempts_exhausted():
    lifecycle = FragmentAckLifecycle(ack_timeout_ms=1_000, retry_backoff_ms=0, max_attempts=2)
    lifecycle.create("frag-001", 0)

    lifecycle.send("frag-001", 100, bearer="reticulum")
    lifecycle.tick(1_100)
    lifecycle.retry("frag-001", 1_100)

    assert lifecycle.get("frag-001").attempts == 2
    assert lifecycle.get("frag-001").state == FragmentAckState.ACK_PENDING

    lifecycle.tick(2_100)
    rec = lifecycle.get("frag-001")

    assert rec.state == FragmentAckState.FAILED
    assert rec.is_terminal is True
    assert rec.history[-1].event == "failed"


def test_no_phone_absence_does_not_block_delivery_by_default():
    lifecycle = FragmentAckLifecycle(phone_required=False)
    lifecycle.create("frag-001", 0)

    rec = lifecycle.mark_signal_absent("frag-001", 10)
    assert rec.signal_state == BearerSignalState.ABSENT
    assert rec.delivery_allowed is True

    rec = lifecycle.send("frag-001", 20, bearer="local")
    assert rec.state == FragmentAckState.ACK_PENDING
    assert rec.attempts == 1


def test_phone_required_blocks_delivery_when_absent():
    lifecycle = FragmentAckLifecycle(phone_required=True)
    lifecycle.create("frag-001", 0)

    lifecycle.mark_signal_absent("frag-001", 10)
    rec = lifecycle.send("frag-001", 20, bearer="phone")

    assert rec.state == FragmentAckState.CREATED
    assert rec.attempts == 0
    assert rec.delivery_allowed is False
    assert rec.history[-1].event == "send_blocked"


def test_signal_loss_does_not_ack_or_fail_by_itself():
    lifecycle = FragmentAckLifecycle(ack_timeout_ms=1_000)
    lifecycle.create("frag-001", 0)
    lifecycle.send("frag-001", 100, bearer="reticulum")

    rec = lifecycle.mark_signal_lost("frag-001", 200)

    assert rec.signal_state == BearerSignalState.LOST
    assert rec.state == FragmentAckState.ACK_PENDING
    assert rec.is_terminal is False


def test_expire_unacked_fragment():
    lifecycle = FragmentAckLifecycle()
    lifecycle.create("frag-001", 0)
    lifecycle.send("frag-001", 100, bearer="reticulum")

    rec = lifecycle.expire("frag-001", 500)

    assert rec.state == FragmentAckState.EXPIRED
    assert rec.is_terminal is True
    assert rec.history[-1].event == "expired"


def test_expire_acked_fragment_is_ignored():
    lifecycle = FragmentAckLifecycle()
    lifecycle.create("frag-001", 0)
    lifecycle.send("frag-001", 100, bearer="reticulum")
    lifecycle.ack("frag-001", 200)

    rec = lifecycle.expire("frag-001", 300)

    assert rec.state == FragmentAckState.ACKED
    assert rec.history[-1].event == "expire_ignored"


def test_duplicate_fragment_rejected():
    lifecycle = FragmentAckLifecycle()
    lifecycle.create("frag-001", 0)

    with pytest.raises(ValueError):
        lifecycle.create("frag-001", 1)


def test_unknown_fragment_rejected():
    lifecycle = FragmentAckLifecycle()

    with pytest.raises(KeyError):
        lifecycle.send("missing", 0)


def test_summary_counts_states():
    lifecycle = FragmentAckLifecycle(ack_timeout_ms=1_000, max_attempts=1)

    lifecycle.create("frag-001", 0)
    lifecycle.create("frag-002", 0)
    lifecycle.create("frag-003", 0)

    lifecycle.send("frag-001", 100)
    lifecycle.ack("frag-001", 200)

    lifecycle.send("frag-002", 100)
    lifecycle.tick(1_100)

    summary = lifecycle.summary()

    assert summary["acked"] == 1
    assert summary["failed"] == 1
    assert summary["created"] == 1


def test_ack_ignored_when_fragment_not_sent():
    lifecycle = FragmentAckLifecycle()
    lifecycle.create("frag-001", 0)

    rec = lifecycle.ack("frag-001", 100)

    assert rec.state == FragmentAckState.CREATED
    assert rec.history[-1].event == "ack_ignored"
