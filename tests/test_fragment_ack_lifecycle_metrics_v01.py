from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

from fragment_ack_lifecycle_v01 import (
    BearerSignalState,
    FragmentAckLifecycle,
    FragmentAckState,
)


REPORT_DIR = Path("reports")
REPORT_PATH = REPORT_DIR / "fragment_ack_lifecycle_metrics_v01.json"

LOOPS = 10_000


def ms(seconds: float) -> float:
    return seconds * 1000.0


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    k = int(round((len(ordered) - 1) * p))
    return ordered[k]


def summarize_timing(metrics: dict, name: str, values: list[float]) -> None:
    metrics[f"{name}_mean"] = round(statistics.mean(values), 6)
    metrics[f"{name}_median"] = round(statistics.median(values), 6)
    metrics[f"{name}_p95"] = round(percentile(values, 0.95), 6)
    metrics[f"{name}_p99"] = round(percentile(values, 0.99), 6)
    metrics[f"{name}_max"] = round(max(values), 6)


def test_fragment_ack_lifecycle_metrics_v01():
    lifecycle = FragmentAckLifecycle(
        ack_timeout_ms=1_000,
        retry_backoff_ms=100,
        max_attempts=3,
        phone_required=False,
    )

    metrics = {
        "test_name": "FRAGMENT_ACK_LIFECYCLE_METRICS_V01",
        "loops": LOOPS,
        "created": 0,
        "sent": 0,
        "acked": 0,
        "retry_scheduled": 0,
        "retried": 0,
        "failed": 0,
        "expired": 0,
        "signal_lost_events": 0,
        "signal_absent_events": 0,
        "signal_present_events": 0,
        "no_phone_delivery_blocked": 0,
        "no_phone_delivery_allowed": 0,
        "invalid_ack_accepted": 0,
        "duplicate_fragment_errors": 0,
        "unknown_fragment_errors": 0,
        "terminal_send_accepted": 0,
        "state_mismatch_errors": 0,
        "history_events_total": 0,
    }

    cycle_ms: list[float] = []
    create_ms: list[float] = []
    send_ms: list[float] = []
    ack_ms: list[float] = []
    tick_ms: list[float] = []
    retry_ms: list[float] = []

    started = time.perf_counter()

    for i in range(LOOPS):
        cycle_started = time.perf_counter()
        fragment_id = f"frag-{i:05d}"
        base_t = i * 10_000

        # CREATE
        t0 = time.perf_counter()
        rec = lifecycle.create(fragment_id, base_t)
        create_ms.append(ms(time.perf_counter() - t0))
        metrics["created"] += 1

        assert rec.state == FragmentAckState.CREATED

        # Duplicate create must fail.
        try:
            lifecycle.create(fragment_id, base_t + 1)
        except ValueError:
            metrics["duplicate_fragment_errors"] += 1
        else:
            metrics["state_mismatch_errors"] += 1

        # Unknown fragment must fail.
        try:
            lifecycle.send(f"missing-{i}", base_t + 2)
        except KeyError:
            metrics["unknown_fragment_errors"] += 1
        else:
            metrics["state_mismatch_errors"] += 1

        # No-phone degraded mode: absent signal must not block when phone_required=False.
        if i % 10 == 0:
            lifecycle.mark_signal_absent(fragment_id, base_t + 5)
            metrics["signal_absent_events"] += 1
            if lifecycle.get(fragment_id).delivery_allowed:
                metrics["no_phone_delivery_allowed"] += 1
            else:
                metrics["no_phone_delivery_blocked"] += 1

        # Signal loss is not failure by itself.
        if i % 15 == 0:
            lifecycle.mark_signal_lost(fragment_id, base_t + 6)
            metrics["signal_lost_events"] += 1
            assert lifecycle.get(fragment_id).state == FragmentAckState.CREATED

        if i % 21 == 0:
            lifecycle.mark_signal_present(fragment_id, base_t + 7)
            metrics["signal_present_events"] += 1
            assert lifecycle.get(fragment_id).signal_state == BearerSignalState.PRESENT

        # SEND
        t0 = time.perf_counter()
        rec = lifecycle.send(fragment_id, base_t + 100, bearer="reticulum")
        send_ms.append(ms(time.perf_counter() - t0))

        assert rec.state == FragmentAckState.ACK_PENDING
        assert rec.attempts == 1
        metrics["sent"] += 1

        # Four deterministic paths:
        # 0: ACK normally
        # 1: timeout + retry + ACK
        # 2: timeout until FAILED
        # 3: expire before ACK
        path = i % 4

        if path == 0:
            t0 = time.perf_counter()
            rec = lifecycle.ack(fragment_id, base_t + 200)
            ack_ms.append(ms(time.perf_counter() - t0))

            assert rec.state == FragmentAckState.ACKED
            metrics["acked"] += 1

            # Sending after terminal ACK must not be accepted.
            before_attempts = rec.attempts
            lifecycle.send(fragment_id, base_t + 300, bearer="reticulum")
            if rec.attempts != before_attempts:
                metrics["terminal_send_accepted"] += 1

        elif path == 1:
            # Timeout schedules retry.
            t0 = time.perf_counter()
            lifecycle.tick(base_t + 1_100)
            tick_ms.append(ms(time.perf_counter() - t0))

            rec = lifecycle.get(fragment_id)
            assert rec.state == FragmentAckState.RETRY_SCHEDULED
            metrics["retry_scheduled"] += 1

            due = lifecycle.retry_due(base_t + 1_200)
            assert any(r.fragment_id == fragment_id for r in due)

            t0 = time.perf_counter()
            rec = lifecycle.retry(fragment_id, base_t + 1_200)
            retry_ms.append(ms(time.perf_counter() - t0))

            assert rec.state == FragmentAckState.ACK_PENDING
            assert rec.attempts == 2
            metrics["retried"] += 1

            t0 = time.perf_counter()
            rec = lifecycle.ack(fragment_id, base_t + 1_300)
            ack_ms.append(ms(time.perf_counter() - t0))

            assert rec.state == FragmentAckState.ACKED
            metrics["acked"] += 1

        elif path == 2:
            # Exhaust max attempts.
            lifecycle.tick(base_t + 1_100)
            assert lifecycle.get(fragment_id).state == FragmentAckState.RETRY_SCHEDULED
            metrics["retry_scheduled"] += 1

            lifecycle.retry(fragment_id, base_t + 1_200)
            metrics["retried"] += 1

            lifecycle.tick(base_t + 2_200)
            assert lifecycle.get(fragment_id).state == FragmentAckState.RETRY_SCHEDULED
            metrics["retry_scheduled"] += 1

            lifecycle.retry(fragment_id, base_t + 2_300)
            metrics["retried"] += 1

            lifecycle.tick(base_t + 3_300)
            rec = lifecycle.get(fragment_id)

            assert rec.state == FragmentAckState.FAILED
            metrics["failed"] += 1

            # ACK after failure must be ignored.
            lifecycle.ack(fragment_id, base_t + 3_400)
            if lifecycle.get(fragment_id).state == FragmentAckState.ACKED:
                metrics["invalid_ack_accepted"] += 1

        else:
            rec = lifecycle.expire(fragment_id, base_t + 500)
            assert rec.state == FragmentAckState.EXPIRED
            metrics["expired"] += 1

            # ACK after expiry must be ignored.
            lifecycle.ack(fragment_id, base_t + 600)
            if lifecycle.get(fragment_id).state == FragmentAckState.ACKED:
                metrics["invalid_ack_accepted"] += 1

        final_rec = lifecycle.get(fragment_id)
        metrics["history_events_total"] += len(final_rec.history)

        # State must be terminal at the end of each path.
        if final_rec.state not in {
            FragmentAckState.ACKED,
            FragmentAckState.FAILED,
            FragmentAckState.EXPIRED,
        }:
            metrics["state_mismatch_errors"] += 1

        cycle_ms.append(ms(time.perf_counter() - cycle_started))

    total_ms = ms(time.perf_counter() - started)

    metrics["total_ms"] = round(total_ms, 6)
    metrics["throughput_cycles_per_sec"] = round(LOOPS / (total_ms / 1000.0), 6)
    metrics["success_rate_percent"] = round(
        ((LOOPS - metrics["state_mismatch_errors"]) / LOOPS) * 100,
        6,
    )
    metrics["final_summary"] = lifecycle.summary()

    summarize_timing(metrics, "cycle_ms", cycle_ms)
    summarize_timing(metrics, "create_ms", create_ms)
    summarize_timing(metrics, "send_ms", send_ms, )
    summarize_timing(metrics, "ack_ms", ack_ms)
    summarize_timing(metrics, "tick_ms", tick_ms)
    summarize_timing(metrics, "retry_ms", retry_ms)

    REPORT_DIR.mkdir(exist_ok=True)
    REPORT_PATH.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")

    print("\nFRAGMENT_ACK_LIFECYCLE_METRICS_V01")
    print(json.dumps(metrics, indent=2, sort_keys=True))

    assert metrics["created"] == LOOPS
    assert metrics["sent"] == LOOPS
    assert metrics["acked"] == LOOPS // 2
    assert metrics["failed"] == LOOPS // 4
    assert metrics["expired"] == LOOPS // 4

    assert metrics["invalid_ack_accepted"] == 0
    assert metrics["terminal_send_accepted"] == 0
    assert metrics["state_mismatch_errors"] == 0

    assert metrics["duplicate_fragment_errors"] == LOOPS
    assert metrics["unknown_fragment_errors"] == LOOPS

    assert metrics["no_phone_delivery_blocked"] == 0
    assert metrics["no_phone_delivery_allowed"] == LOOPS // 10

    assert metrics["final_summary"]["acked"] == LOOPS // 2
    assert metrics["final_summary"]["failed"] == LOOPS // 4
    assert metrics["final_summary"]["expired"] == LOOPS // 4
