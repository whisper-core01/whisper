from __future__ import annotations

import hashlib
import json
import os
import socket
import statistics
import time
from pathlib import Path

import pytest

from mce_hardened_v01 import MCEHardened
from pipeline_demo import fragment_payload


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


def fp(value: bytes) -> bytes:
    return hashlib.blake2s(value, digest_size=16, person=b"FRAGMCE").digest()


def make_payload(i: int) -> bytes:
    """
    Deterministic payload generator.

    Sizes vary to force different fragmentation patterns while keeping
    the 1M soak test realistic.
    """
    size = [1, 2, 3, 7, 16, 31, 32, 63, 64, 65, 96, 127, 128, 129, 191, 255, 256][i % 17]
    seed = b"WHISPER_FRAGMENTATION_PAYLOAD_V01|" + i.to_bytes(8, "big")
    return hashlib.shake_256(seed).digest(size)


def choose_fragment_size(i: int) -> int:
    return [32, 64, 128, 256][i % 4]


def run_fragmentation_mce_metrics(
    *,
    loops: int,
    test_name: str,
    report_name: str,
    monkeypatch=None,
) -> dict:
    external_dependency_calls = 0

    if monkeypatch is not None:

        def blocked_network(*args, **kwargs):
            nonlocal external_dependency_calls
            external_dependency_calls += 1
            raise AssertionError("External dependency forbidden: network access attempted")

        monkeypatch.setattr(socket, "socket", blocked_network)
        monkeypatch.setattr(socket, "create_connection", blocked_network)

    metrics = {
        "test_name": test_name,
        "loops": loops,
        "payloads_processed": 0,
        "payload_bytes_total": 0,
        "fragments_total": 0,
        "min_fragments_per_payload": None,
        "max_fragments_per_payload": 0,
        "fragment_count_mismatch": 0,
        "empty_fragment_unexpected": 0,
        "fragment_roundtrip_failures": 0,
        "fragment_size_violations": 0,
        "mce_counter_mismatch": 0,
        "mce_validation_failures": 0,
        "mce_state_invalid_after_cycle": 0,
        "mce_output_length_mismatch": 0,
        "same_cycle_output_collisions": 0,
        "final_state_collisions": 0,
        "determinism_checks": 0,
        "determinism_failures": 0,
        "order_sensitivity_checks": 0,
        "order_sensitivity_failures": 0,
        "invalid_fragment_size_rejected": 0,
        "invalid_payload_type_rejected": 0,
        "external_dependency_calls": 0,
        "state_mismatch_errors": 0,
    }

    seen_final_states: set[bytes] = set()

    cycle_ms: list[float] = []
    split_ms: list[float] = []
    recompose_ms: list[float] = []
    mce_ms: list[float] = []
    determinism_ms: list[float] = []
    order_ms: list[float] = []

    started = time.perf_counter()

    # API rejection checks once per campaign.
    try:
        fragment_payload(b"abc", 0)
    except ValueError:
        metrics["invalid_fragment_size_rejected"] += 1

    try:
        fragment_payload("not-bytes", 4)  # type: ignore[arg-type]
    except TypeError:
        metrics["invalid_payload_type_rejected"] += 1

    for i in range(loops):
        cycle_started = time.perf_counter()

        payload = make_payload(i)
        fragment_size = choose_fragment_size(i)
        seed = hashlib.blake2b(
            b"WHISPER_FRAGMENTATION_MCE_SEED_V01|" + i.to_bytes(8, "big"),
            digest_size=32,
        ).digest()

        expected_count = (len(payload) + fragment_size - 1) // fragment_size

        # Fragmentation.
        t0 = time.perf_counter()
        fragments = fragment_payload(payload, fragment_size)
        split_ms.append(ms(time.perf_counter() - t0))

        metrics["payloads_processed"] += 1
        metrics["payload_bytes_total"] += len(payload)
        metrics["fragments_total"] += len(fragments)

        if metrics["min_fragments_per_payload"] is None:
            metrics["min_fragments_per_payload"] = len(fragments)
        else:
            metrics["min_fragments_per_payload"] = min(
                metrics["min_fragments_per_payload"],
                len(fragments),
            )

        metrics["max_fragments_per_payload"] = max(
            metrics["max_fragments_per_payload"],
            len(fragments),
        )

        if len(fragments) != expected_count:
            metrics["fragment_count_mismatch"] += 1

        for index, fragment in enumerate(fragments):
            if len(fragment) == 0:
                metrics["empty_fragment_unexpected"] += 1
            if len(fragment) > fragment_size:
                metrics["fragment_size_violations"] += 1
            if index < len(fragments) - 1 and len(fragment) != fragment_size:
                metrics["fragment_size_violations"] += 1

        # Recomposition.
        t0 = time.perf_counter()
        recomposed = b"".join(fragments)
        recompose_ms.append(ms(time.perf_counter() - t0))

        if recomposed != payload:
            metrics["fragment_roundtrip_failures"] += 1

        # MCE Hardened processing.
        mce = MCEHardened(seed)
        outputs: list[bytes] = []
        output_fps: set[bytes] = set()

        t0 = time.perf_counter()

        for j, fragment in enumerate(fragments):
            transformed, snapshot, validation = mce.digest_fragment_checked(fragment)

            if not validation["valid"]:
                metrics["mce_validation_failures"] += 1

            if snapshot.fragment_counter != j + 1:
                metrics["mce_counter_mismatch"] += 1

            if len(transformed) != len(fragment):
                metrics["mce_output_length_mismatch"] += 1

            transformed_fp = fp(transformed)
            if transformed_fp in output_fps:
                metrics["same_cycle_output_collisions"] += 1
            output_fps.add(transformed_fp)
            outputs.append(transformed)

        mce_ms.append(ms(time.perf_counter() - t0))

        if mce.fragment_counter != len(fragments):
            metrics["mce_counter_mismatch"] += 1

        if not mce.validate_state():
            metrics["mce_state_invalid_after_cycle"] += 1

        final_state_fp = fp(mce.snapshot().state_digest)
        if final_state_fp in seen_final_states:
            metrics["final_state_collisions"] += 1
        seen_final_states.add(final_state_fp)

        # Determinism sample.
        # Same payload + same seed + same fragment_size must produce same outputs/state.
        if i % 100 == 0:
            t0 = time.perf_counter()

            fragments_b = fragment_payload(payload, fragment_size)
            mce_b = MCEHardened(seed)
            outputs_b = [mce_b.digest_fragment_checked(fragment)[0] for fragment in fragments_b]

            metrics["determinism_checks"] += 1

            if fragments_b != fragments or outputs_b != outputs or mce_b.snapshot() != mce.snapshot():
                metrics["determinism_failures"] += 1

            determinism_ms.append(ms(time.perf_counter() - t0))

        # Order sensitivity sample.
        # If more than one fragment exists, reversing order should change MCE output/state.
        if i % 250 == 0 and len(fragments) > 1:
            t0 = time.perf_counter()

            mce_order = MCEHardened(seed)
            reversed_fragments = list(reversed(fragments))
            reversed_outputs = [
                mce_order.digest_fragment_checked(fragment)[0]
                for fragment in reversed_fragments
            ]

            metrics["order_sensitivity_checks"] += 1

            if reversed_outputs == outputs and mce_order.snapshot() == mce.snapshot():
                metrics["order_sensitivity_failures"] += 1

            order_ms.append(ms(time.perf_counter() - t0))

        if (
            metrics["fragment_count_mismatch"]
            or metrics["empty_fragment_unexpected"]
            or metrics["fragment_roundtrip_failures"]
            or metrics["fragment_size_violations"]
            or metrics["mce_counter_mismatch"]
            or metrics["mce_validation_failures"]
            or metrics["mce_state_invalid_after_cycle"]
            or metrics["mce_output_length_mismatch"]
            or metrics["determinism_failures"]
            or metrics["order_sensitivity_failures"]
        ):
            metrics["state_mismatch_errors"] += 1

        cycle_ms.append(ms(time.perf_counter() - cycle_started))

    total_ms = ms(time.perf_counter() - started)

    metrics["external_dependency_calls"] = external_dependency_calls
    metrics["total_ms"] = round(total_ms, 6)
    metrics["throughput_cycles_per_sec"] = round(loops / (total_ms / 1000.0), 6)
    metrics["throughput_fragments_per_sec"] = round(
        metrics["fragments_total"] / (total_ms / 1000.0),
        6,
    )
    metrics["mean_fragments_per_payload"] = round(metrics["fragments_total"] / loops, 6)
    metrics["mean_payload_bytes"] = round(metrics["payload_bytes_total"] / loops, 6)
    metrics["success_rate_percent"] = round(
        ((loops - metrics["state_mismatch_errors"]) / loops) * 100,
        6,
    )

    summarize_timing(metrics, "cycle_ms", cycle_ms)
    summarize_timing(metrics, "split_ms", split_ms)
    summarize_timing(metrics, "recompose_ms", recompose_ms)
    summarize_timing(metrics, "mce_ms", mce_ms)

    if determinism_ms:
        summarize_timing(metrics, "determinism_ms", determinism_ms)

    if order_ms:
        summarize_timing(metrics, "order_ms", order_ms)

    REPORT_DIR.mkdir(exist_ok=True)
    report_path = REPORT_DIR / report_name
    report_path.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")

    print(f"\n{test_name}")
    print(json.dumps(metrics, indent=2, sort_keys=True))

    assert metrics["payloads_processed"] == loops
    assert metrics["fragment_count_mismatch"] == 0
    assert metrics["empty_fragment_unexpected"] == 0
    assert metrics["fragment_roundtrip_failures"] == 0
    assert metrics["fragment_size_violations"] == 0
    assert metrics["mce_counter_mismatch"] == 0
    assert metrics["mce_validation_failures"] == 0
    assert metrics["mce_state_invalid_after_cycle"] == 0
    assert metrics["mce_output_length_mismatch"] == 0
    assert metrics["determinism_failures"] == 0
    assert metrics["order_sensitivity_failures"] == 0
    assert metrics["invalid_fragment_size_rejected"] == 1
    assert metrics["invalid_payload_type_rejected"] == 1
    assert metrics["external_dependency_calls"] == 0
    assert metrics["state_mismatch_errors"] == 0

    # With the deterministic test corpus, final MCE state collisions should not occur.
    assert metrics["final_state_collisions"] == 0

    return metrics


def test_fragmentation_mce_metrics_10k(monkeypatch):
    run_fragmentation_mce_metrics(
        loops=10_000,
        test_name="FRAGMENTATION_MCE_METRICS_10K_V01",
        report_name="fragmentation_mce_metrics_10k_v01.json",
        monkeypatch=monkeypatch,
    )


@pytest.mark.slow
def test_fragmentation_mce_soak_100k(monkeypatch):
    if os.environ.get("WHISPER_RUN_FRAGMENTATION_100K") != "1":
        pytest.skip("Set WHISPER_RUN_FRAGMENTATION_100K=1 to run the 100K fragmentation soak test")

    run_fragmentation_mce_metrics(
        loops=100_000,
        test_name="FRAGMENTATION_MCE_SOAK_100K_V01",
        report_name="fragmentation_mce_soak_100k_v01.json",
        monkeypatch=monkeypatch,
    )


@pytest.mark.slow
@pytest.mark.soak
def test_fragmentation_mce_soak_1m(monkeypatch):
    if os.environ.get("WHISPER_RUN_FRAGMENTATION_1M") != "1":
        pytest.skip("Set WHISPER_RUN_FRAGMENTATION_1M=1 to run the 1M fragmentation soak test")

    run_fragmentation_mce_metrics(
        loops=1_000_000,
        test_name="FRAGMENTATION_MCE_SOAK_1M_V01",
        report_name="fragmentation_mce_soak_1m_v01.json",
        monkeypatch=monkeypatch,
    )
