from __future__ import annotations

import json
import os
import statistics
import time
from pathlib import Path

import pytest

from fragment_ack_lifecycle_v01 import (
    BearerSignalState,
    FragmentAckRecord,
    FragmentAckState,
)


REPORT_DIR = Path("reports")


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


def run_fragment_ack_lifecycle_soak(
    *,
    loops: int,
    test_name: str,
    report_name: str,
) -> dict:
    metrics = {
        "test_name": test_name,
        "loops": loops,
        "created": 0,
        "sent": 0,
        "acked": 0,
        "retry_scheduled": 0,
        "retried": 0,
        "failed": 0,
        "expired": 0,
        "signal_absent_events": 0,
        "signal_lost_events": 0,
        "signal_present_events": 0,
        "no_phone_delivery_allowed": 0,
        "no_phone_delivery_blocked": 0,
        "phone_required_blocked": 0,
        "invalid_ack_accepted": 0,
        "terminal_send_accepted": 0,
        "state_mismatch_errors": 0,
        "history_events_total": 0,
        "max_history_len": 0,
    }

    cycle_ms: list[float] = []
    create_ms: list[float] = []
    send_ms: list[float] = []
    ack_ms: list[float] = []
    tick_ms: list[float] = []
    retry_ms: list[float] = []
    expire_ms: list[float] = []
    phone_block_ms: list[float] = []

    started = time.perf_counter()

    for i in range(loops):
        cycle_started = time.perf_counter()
        fragment_id = f"frag-{i:09d}"
        base_t = i * 10_000

        t0 = time.perf_counter()
        rec = FragmentAckRecord(
            fragment_id=fragment_id,
            created_at_ms=base_t,
            ack_timeout_ms=1_000,
            retry_backoff_ms=100,
            max_attempts=3,
            phone_required=False,
        )
        rec.log(base_t, "created")
        create_ms.append(ms(time.perf_counter() - t0))

        metrics["created"] += 1
        assert rec.state == FragmentAckState.CREATED
        assert rec.delivery_allowed is True

        # No-phone degraded mode: absent signal must not block delivery when phone_required=False.
        if i % 10 == 0:
            rec.mark_signal_absent(base_t + 5)
            metrics["signal_absent_events"] += 1
            if rec.delivery_allowed:
                metrics["no_phone_delivery_allowed"] += 1
            else:
                metrics["no_phone_delivery_blocked"] += 1

        # Signal loss must not fail the fragment by itself.
        if i % 15 == 0:
            rec.mark_signal_lost(base_t + 6)
            metrics["signal_lost_events"] += 1
            assert rec.signal_state == BearerSignalState.LOST
            assert rec.state == FragmentAckState.CREATED

        if i % 21 == 0:
            rec.mark_signal_present(base_t + 7)
            metrics["signal_present_events"] += 1
            assert rec.signal_state == BearerSignalState.PRESENT

        # Separate phone-required check: absence blocks only when explicitly required.
        if i % 100 == 0:
            t0 = time.perf_counter()
            phone_rec = FragmentAckRecord(
                fragment_id=f"phone-required-{i:09d}",
                created_at_ms=base_t,
                ack_timeout_ms=1_000,
                retry_backoff_ms=100,
                max_attempts=3,
                phone_required=True,
            )
            phone_rec.mark_signal_absent(base_t + 8)
            phone_rec.mark_sent(base_t + 9, bearer="phone")
            phone_block_ms.append(ms(time.perf_counter() - t0))

            if phone_rec.state == FragmentAckState.CREATED and phone_rec.attempts == 0:
                metrics["phone_required_blocked"] += 1
            else:
                metrics["state_mismatch_errors"] += 1

        # SEND
        t0 = time.perf_counter()
        rec.mark_sent(base_t + 100, bearer="reticulum")
        send_ms.append(ms(time.perf_counter() - t0))

        assert rec.state == FragmentAckState.ACK_PENDING
        assert rec.attempts == 1
        metrics["sent"] += 1

        # Deterministic paths:
        # 0: ACK normally
        # 1: timeout + retry + ACK
        # 2: timeout until FAILED
        # 3: expire before ACK
        path = i % 4

        if path == 0:
            t0 = time.perf_counter()
            rec.mark_ack(base_t + 200)
            ack_ms.append(ms(time.perf_counter() - t0))

            assert rec.state == FragmentAckState.ACKED
            metrics["acked"] += 1

            before_attempts = rec.attempts
            rec.mark_sent(base_t + 300, bearer="reticulum")
            if rec.attempts != before_attempts:
                metrics["terminal_send_accepted"] += 1

        elif path == 1:
            t0 = time.perf_counter()
            rec.tick(base_t + 1_100)
            tick_ms.append(ms(time.perf_counter() - t0))

            assert rec.state == FragmentAckState.RETRY_SCHEDULED
            metrics["retry_scheduled"] += 1

            t0 = time.perf_counter()
            rec.retry(base_t + 1_200)
            retry_ms.append(ms(time.perf_counter() - t0))

            assert rec.state == FragmentAckState.ACK_PENDING
            assert rec.attempts == 2
            metrics["retried"] += 1

            t0 = time.perf_counter()
            rec.mark_ack(base_t + 1_300)
            ack_ms.append(ms(time.perf_counter() - t0))

            assert rec.state == FragmentAckState.ACKED
            metrics["acked"] += 1

        elif path == 2:
            t0 = time.perf_counter()
            rec.tick(base_t + 1_100)
            tick_ms.append(ms(time.perf_counter() - t0))
            assert rec.state == FragmentAckState.RETRY_SCHEDULED
            metrics["retry_scheduled"] += 1

            t0 = time.perf_counter()
            rec.retry(base_t + 1_200)
            retry_ms.append(ms(time.perf_counter() - t0))
            assert rec.state == FragmentAckState.ACK_PENDING
            metrics["retried"] += 1

            t0 = time.perf_counter()
            rec.tick(base_t + 2_200)
            tick_ms.append(ms(time.perf_counter() - t0))
            assert rec.state == FragmentAckState.RETRY_SCHEDULED
            metrics["retry_scheduled"] += 1

            t0 = time.perf_counter()
            rec.retry(base_t + 2_300)
            retry_ms.append(ms(time.perf_counter() - t0))
            assert rec.state == FragmentAckState.ACK_PENDING
            assert rec.attempts == 3
            metrics["retried"] += 1

            t0 = time.perf_counter()
            rec.tick(base_t + 3_300)
            tick_ms.append(ms(time.perf_counter() - t0))
            assert rec.state == FragmentAckState.FAILED
            metrics["failed"] += 1

            rec.mark_ack(base_t + 3_400)
            if rec.state == FragmentAckState.ACKED:
                metrics["invalid_ack_accepted"] += 1

        else:
            t0 = time.perf_counter()
            rec.expire(base_t + 500)
            expire_ms.append(ms(time.perf_counter() - t0))

            assert rec.state == FragmentAckState.EXPIRED
            metrics["expired"] += 1

            rec.mark_ack(base_t + 600)
            if rec.state == FragmentAckState.ACKED:
                metrics["invalid_ack_accepted"] += 1

        if rec.state not in {
            FragmentAckState.ACKED,
            FragmentAckState.FAILED,
            FragmentAckState.EXPIRED,
        }:
            metrics["state_mismatch_errors"] += 1

        history_len = len(rec.history)
        metrics["history_events_total"] += history_len
        if history_len > metrics["max_history_len"]:
            metrics["max_history_len"] = history_len

        cycle_ms.append(ms(time.perf_counter() - cycle_started))

    total_ms = ms(time.perf_counter() - started)

    metrics["total_ms"] = round(total_ms, 6)
    metrics["throughput_cycles_per_sec"] = round(loops / (total_ms / 1000.0), 6)
    metrics["success_rate_percent"] = round(
        ((loops - metrics["state_mismatch_errors"]) / loops) * 100,
        6,
    )

    summarize_timing(metrics, "cycle_ms", cycle_ms)
    summarize_timing(metrics, "create_ms", create_ms)
    summarize_timing(metrics, "send_ms", send_ms)
    summarize_timing(metrics, "ack_ms", ack_ms)
    summarize_timing(metrics, "tick_ms", tick_ms)
    summarize_timing(metrics, "retry_ms", retry_ms)
    summarize_timing(metrics, "expire_ms", expire_ms)
    summarize_timing(metrics, "phone_block_ms", phone_block_ms)

    REPORT_DIR.mkdir(exist_ok=True)
    report_path = REPORT_DIR / report_name
    report_path.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")

    print(f"\n{test_name}")
    print(json.dumps(metrics, indent=2, sort_keys=True))

    assert metrics["created"] == loops
    assert metrics["sent"] == loops
    assert metrics["acked"] == loops // 2
    assert metrics["failed"] == loops // 4
    assert metrics["expired"] == loops // 4

    assert metrics["invalid_ack_accepted"] == 0
    assert metrics["terminal_send_accepted"] == 0
    assert metrics["state_mismatch_errors"] == 0

    assert metrics["no_phone_delivery_blocked"] == 0
    assert metrics["no_phone_delivery_allowed"] == loops // 10
    assert metrics["phone_required_blocked"] == loops // 100

    return metrics


@pytest.mark.slow
def test_fragment_ack_lifecycle_soak_100k():
    if os.environ.get("WHISPER_RUN_ACK_100K") != "1":
        pytest.skip("Set WHISPER_RUN_ACK_100K=1 to run the 100K ACK lifecycle soak test")

    run_fragment_ack_lifecycle_soak(
        loops=100_000,
        test_name="FRAGMENT_ACK_LIFECYCLE_SOAK_100K_V01",
        report_name="fragment_ack_lifecycle_soak_100k_v01.json",
    )


@pytest.mark.slow
@pytest.mark.soak
def test_fragment_ack_lifecycle_soak_1m():
    if os.environ.get("WHISPER_RUN_ACK_1M") != "1":
        pytest.skip("Set WHISPER_RUN_ACK_1M=1 to run the 1M ACK lifecycle soak test")

    run_fragment_ack_lifecycle_soak(
        loops=1_000_000,
        test_name="FRAGMENT_ACK_LIFECYCLE_SOAK_1M_V01",
        report_name="fragment_ack_lifecycle_soak_1m_v01.json",
    )
