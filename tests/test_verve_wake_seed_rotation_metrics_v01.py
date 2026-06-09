from __future__ import annotations

import json
import os
import statistics
import time
from pathlib import Path

import pytest

from verve_wake_seed_rotation_v01 import (
    FROZEN_WINDOW_SECONDS,
    LuksHeaderMock,
    VerveVault,
    configure_luks_verve_keyslot,
    consume_rotating_code,
    derive_rotating_code,
    freeze_code_on_first_input,
    frozen_code_expired,
    generate_wake_seed,
    handoff_wake_seed_to_verve,
    revoke_verve_keyslot,
    start_rotating_code_session,
    update_rotating_code_session,
    verve_attempt_luks_unlock,
    wake_seed_is_well_formed,
    zeroize_wake_seed,
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


def run_verve_wake_seed_rotation_metrics(
    *,
    loops: int,
    test_name: str,
    report_name: str,
) -> dict:
    metrics = {
        "test_name": test_name,
        "loops": loops,
        "generated": 0,
        "well_formed": 0,
        "seed_reuse": 0,
        "keyslot_configured": 0,
        "keyslot_binding_collisions": 0,
        "handoff_to_verve": 0,
        "whisper_copy_zeroized": 0,
        "zeroize_failures": 0,
        "unlock_allowed": 0,
        "unlock_rejected": 0,
        "wrong_seed_unlock_accepted": 0,
        "revoked_keyslot_unlock_accepted": 0,
        "verve_zeroized_after_unlock": 0,
        "old_verve_seed_accepted_after_unlock": 0,
        "rotating_code_generated": 0,
        "rotating_code_stability_same_window": 0,
        "rotating_code_changes_next_window": 0,
        "rotating_code_failures": 0,
        "frozen_code_preserved": 0,
        "frozen_code_mutation": 0,
        "frozen_code_expiry_ok": 0,
        "consumed_code_reuse_accepted": 0,
        "state_mismatch_errors": 0,
    }

    seen_seeds: set[str] = set()
    seen_keyslot_bindings: set[str] = set()

    cycle_ms: list[float] = []
    generate_ms: list[float] = []
    keyslot_ms: list[float] = []
    handoff_ms: list[float] = []
    zeroize_ms: list[float] = []
    unlock_ms: list[float] = []
    wrong_unlock_ms: list[float] = []
    revoke_unlock_ms: list[float] = []
    code_ms: list[float] = []
    freeze_ms: list[float] = []
    consume_ms: list[float] = []

    started = time.perf_counter()

    for i in range(loops):
        cycle_started = time.perf_counter()

        local_material = f"local-wake-material-{i:09d}"
        keyslot_id = f"verve-slot-{i:09d}"

        luks = LuksHeaderMock()
        verve = VerveVault()

        # Generate wake seed from local deterministic material.
        t0 = time.perf_counter()
        wake_seed = generate_wake_seed(local_material)
        generate_ms.append(ms(time.perf_counter() - t0))

        metrics["generated"] += 1

        if wake_seed_is_well_formed(wake_seed.seed):
            metrics["well_formed"] += 1
        else:
            metrics["state_mismatch_errors"] += 1

        if wake_seed.seed in seen_seeds:
            metrics["seed_reuse"] += 1
        seen_seeds.add(wake_seed.seed)

        # Configure LUKS Verve keyslot.
        t0 = time.perf_counter()
        configure_luks_verve_keyslot(luks, keyslot_id, wake_seed)
        keyslot_ms.append(ms(time.perf_counter() - t0))

        assert keyslot_id in luks.verve_keyslots
        binding = luks.verve_keyslots[keyslot_id]
        metrics["keyslot_configured"] += 1

        if binding in seen_keyslot_bindings:
            metrics["keyslot_binding_collisions"] += 1
        seen_keyslot_bindings.add(binding)

        # Handoff seed to Verve.
        seed_before_zeroize = wake_seed.seed

        t0 = time.perf_counter()
        handoff_wake_seed_to_verve(wake_seed, verve, keyslot_id)
        handoff_ms.append(ms(time.perf_counter() - t0))

        assert verve.wake_seed == seed_before_zeroize
        assert verve.keyslot_id == keyslot_id
        metrics["handoff_to_verve"] += 1

        # Zeroize WHISPER copy.
        t0 = time.perf_counter()
        zeroize_wake_seed(wake_seed)
        zeroize_ms.append(ms(time.perf_counter() - t0))

        if wake_seed.seed == "\x00" * 64 and wake_seed.state == "ZEROIZED":
            metrics["whisper_copy_zeroized"] += 1
        else:
            metrics["zeroize_failures"] += 1

        # Rotating code properties.
        t0 = time.perf_counter()
        code_0 = derive_rotating_code(seed_before_zeroize, 0)
        code_9 = derive_rotating_code(seed_before_zeroize, 9)
        code_10 = derive_rotating_code(seed_before_zeroize, 10)
        code_ms.append(ms(time.perf_counter() - t0))

        if len(code_0.code) == 16:
            metrics["rotating_code_generated"] += 1
        else:
            metrics["rotating_code_failures"] += 1

        if code_0.code == code_9.code:
            metrics["rotating_code_stability_same_window"] += 1
        else:
            metrics["rotating_code_failures"] += 1

        if code_0.code != code_10.code:
            metrics["rotating_code_changes_next_window"] += 1
        else:
            metrics["rotating_code_failures"] += 1

        # Frozen code must not mutate after first input.
        t0 = time.perf_counter()
        session = start_rotating_code_session(seed_before_zeroize, 0)
        first_code = session.current_code.code
        freeze_code_on_first_input(session, 5)
        update_rotating_code_session(session, seed_before_zeroize, 20)
        freeze_ms.append(ms(time.perf_counter() - t0))

        if session.current_code.code == first_code and session.current_code.state == "FROZEN":
            metrics["frozen_code_preserved"] += 1
        else:
            metrics["frozen_code_mutation"] += 1

        if (
            frozen_code_expired(session, 5 + FROZEN_WINDOW_SECONDS) is False
            and frozen_code_expired(session, 5 + FROZEN_WINDOW_SECONDS + 1) is True
        ):
            metrics["frozen_code_expiry_ok"] += 1
        else:
            metrics["state_mismatch_errors"] += 1

        # Consumed code must remain consumed.
        t0 = time.perf_counter()
        consume_rotating_code(session)
        update_rotating_code_session(session, seed_before_zeroize, 30)
        consume_ms.append(ms(time.perf_counter() - t0))

        if session.current_code.state != "CONSUMED":
            metrics["consumed_code_reuse_accepted"] += 1

        # Correct Verve unlock.
        t0 = time.perf_counter()
        decision, attempt = verve_attempt_luks_unlock(luks, verve)
        unlock_ms.append(ms(time.perf_counter() - t0))

        if decision == "unlock_allowed" and attempt is not None and attempt.zeroized_after_attempt:
            metrics["unlock_allowed"] += 1
        else:
            metrics["state_mismatch_errors"] += 1

        if verve.wake_seed is None and verve.zeroized_after_unlock:
            metrics["verve_zeroized_after_unlock"] += 1
        else:
            metrics["state_mismatch_errors"] += 1

        # Old Verve seed must not unlock again after unlock zeroization.
        decision_again, attempt_again = verve_attempt_luks_unlock(luks, verve)
        if decision_again == "unlock_allowed":
            metrics["old_verve_seed_accepted_after_unlock"] += 1

        # Wrong seed rejection.
        wrong_luks = LuksHeaderMock()
        wrong_verve = VerveVault()
        correct_seed = generate_wake_seed(f"wrong-path-correct-{i:09d}")
        configure_luks_verve_keyslot(wrong_luks, keyslot_id, correct_seed)
        handoff_wake_seed_to_verve(correct_seed, wrong_verve, keyslot_id)

        wrong_verve.wake_seed = generate_wake_seed(f"wrong-path-bad-{i:09d}").seed

        t0 = time.perf_counter()
        wrong_decision, wrong_attempt = verve_attempt_luks_unlock(wrong_luks, wrong_verve)
        wrong_unlock_ms.append(ms(time.perf_counter() - t0))

        if wrong_decision == "unlock_rejected":
            metrics["unlock_rejected"] += 1
        else:
            metrics["wrong_seed_unlock_accepted"] += 1

        assert wrong_attempt is not None
        assert wrong_attempt.zeroized_after_attempt is True

        # Revoked keyslot rejection.
        revoked_luks = LuksHeaderMock()
        revoked_verve = VerveVault()
        revoked_seed = generate_wake_seed(f"revoked-path-{i:09d}")

        configure_luks_verve_keyslot(revoked_luks, keyslot_id, revoked_seed)
        handoff_wake_seed_to_verve(revoked_seed, revoked_verve, keyslot_id)
        revoke_verve_keyslot(revoked_luks, revoked_verve, keyslot_id)

        t0 = time.perf_counter()
        revoked_decision, revoked_attempt = verve_attempt_luks_unlock(
            revoked_luks,
            revoked_verve,
        )
        revoke_unlock_ms.append(ms(time.perf_counter() - t0))

        if revoked_decision == "unlock_rejected" and revoked_attempt is None:
            metrics["unlock_rejected"] += 1
        else:
            metrics["revoked_keyslot_unlock_accepted"] += 1

        cycle_ms.append(ms(time.perf_counter() - cycle_started))

    total_ms = ms(time.perf_counter() - started)

    metrics["total_ms"] = round(total_ms, 6)
    metrics["throughput_cycles_per_sec"] = round(loops / (total_ms / 1000.0), 6)
    metrics["success_rate_percent"] = round(
        ((loops - metrics["state_mismatch_errors"]) / loops) * 100,
        6,
    )

    summarize_timing(metrics, "cycle_ms", cycle_ms)
    summarize_timing(metrics, "generate_ms", generate_ms)
    summarize_timing(metrics, "keyslot_ms", keyslot_ms)
    summarize_timing(metrics, "handoff_ms", handoff_ms)
    summarize_timing(metrics, "zeroize_ms", zeroize_ms)
    summarize_timing(metrics, "unlock_ms", unlock_ms)
    summarize_timing(metrics, "wrong_unlock_ms", wrong_unlock_ms)
    summarize_timing(metrics, "revoke_unlock_ms", revoke_unlock_ms)
    summarize_timing(metrics, "code_ms", code_ms)
    summarize_timing(metrics, "freeze_ms", freeze_ms)
    summarize_timing(metrics, "consume_ms", consume_ms)

    REPORT_DIR.mkdir(exist_ok=True)
    report_path = REPORT_DIR / report_name
    report_path.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")

    print(f"\n{test_name}")
    print(json.dumps(metrics, indent=2, sort_keys=True))

    assert metrics["generated"] == loops
    assert metrics["well_formed"] == loops
    assert metrics["seed_reuse"] == 0
    assert metrics["keyslot_configured"] == loops
    assert metrics["keyslot_binding_collisions"] == 0
    assert metrics["handoff_to_verve"] == loops
    assert metrics["whisper_copy_zeroized"] == loops
    assert metrics["zeroize_failures"] == 0

    assert metrics["unlock_allowed"] == loops
    assert metrics["unlock_rejected"] == loops * 2
    assert metrics["wrong_seed_unlock_accepted"] == 0
    assert metrics["revoked_keyslot_unlock_accepted"] == 0
    assert metrics["verve_zeroized_after_unlock"] == loops
    assert metrics["old_verve_seed_accepted_after_unlock"] == 0

    assert metrics["rotating_code_generated"] == loops
    assert metrics["rotating_code_stability_same_window"] == loops
    assert metrics["rotating_code_changes_next_window"] == loops
    assert metrics["rotating_code_failures"] == 0
    assert metrics["frozen_code_preserved"] == loops
    assert metrics["frozen_code_mutation"] == 0
    assert metrics["frozen_code_expiry_ok"] == loops
    assert metrics["consumed_code_reuse_accepted"] == 0

    assert metrics["state_mismatch_errors"] == 0

    return metrics


def test_verve_wake_seed_rotation_metrics_10k():
    run_verve_wake_seed_rotation_metrics(
        loops=10_000,
        test_name="VERVE_WAKE_SEED_ROTATION_METRICS_10K_V01",
        report_name="verve_wake_seed_rotation_metrics_10k_v01.json",
    )


@pytest.mark.slow
def test_verve_wake_seed_rotation_soak_100k():
    if os.environ.get("WHISPER_RUN_VERVE_100K") != "1":
        pytest.skip("Set WHISPER_RUN_VERVE_100K=1 to run the 100K Verve soak test")

    run_verve_wake_seed_rotation_metrics(
        loops=100_000,
        test_name="VERVE_WAKE_SEED_ROTATION_SOAK_100K_V01",
        report_name="verve_wake_seed_rotation_soak_100k_v01.json",
    )


@pytest.mark.slow
@pytest.mark.soak
def test_verve_wake_seed_rotation_soak_1m():
    if os.environ.get("WHISPER_RUN_VERVE_1M") != "1":
        pytest.skip("Set WHISPER_RUN_VERVE_1M=1 to run the 1M Verve soak test")

    run_verve_wake_seed_rotation_metrics(
        loops=1_000_000,
        test_name="VERVE_WAKE_SEED_ROTATION_SOAK_1M_V01",
        report_name="verve_wake_seed_rotation_soak_1m_v01.json",
    )
