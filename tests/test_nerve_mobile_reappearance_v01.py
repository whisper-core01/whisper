from nerve_mobile_reappearance_v01 import (
    attempt_reappearance,
    boot_for_epoch,
    build_continuity_record,
    derive_origin_hint_commitment,
    derive_reappearance_continuity_commitment,
    simulate_initial_admission,
    stable_hash_hex,
    validate_reappearance_scenario,
)


def test_origin_hint_commitment_is_deterministic():
    master = stable_hash_hex("local-master")

    a = derive_origin_hint_commitment("origin", master, "epoch-1")
    b = derive_origin_hint_commitment("origin", master, "epoch-1")

    assert a == b
    assert len(a) == 64


def test_origin_hint_commitment_changes_with_epoch():
    master = stable_hash_hex("local-master")

    a = derive_origin_hint_commitment("origin", master, "epoch-1")
    b = derive_origin_hint_commitment("origin", master, "epoch-2")

    assert a != b


def test_initial_admission_builds_continuity_record():
    master = stable_hash_hex("local-master")

    boot, record = simulate_initial_admission(master)

    assert len(boot.nerve_admission_code) == 64
    assert len(record.nerve_binding_commitment) == 64
    assert len(record.origin_hint_commitment) == 64
    assert record.revocation_state == "active"


def test_boot_code_changes_after_reboot_challenge():
    a = boot_for_epoch("challenge-a", "boot-a", "epoch-1")
    b = boot_for_epoch("challenge-b", "boot-b", "epoch-1")

    assert a.nerve_admission_code != b.nerve_admission_code


def test_boot_code_changes_after_epoch_change():
    a = boot_for_epoch("challenge", "boot", "epoch-1")
    b = boot_for_epoch("challenge", "boot", "epoch-2")

    assert a.nerve_admission_code != b.nerve_admission_code


def test_reappearance_continuity_commitment_is_deterministic():
    master = stable_hash_hex("local-master")
    previous_boot, record = simulate_initial_admission(master)
    current_boot = boot_for_epoch("challenge-2", "boot-2", "epoch-2")

    a = derive_reappearance_continuity_commitment(
        record,
        current_boot.admission_epoch,
        "challenge-2",
        current_boot.nerve_admission_code,
    )

    b = derive_reappearance_continuity_commitment(
        record,
        current_boot.admission_epoch,
        "challenge-2",
        current_boot.nerve_admission_code,
    )

    assert previous_boot.nerve_admission_code != current_boot.nerve_admission_code
    assert a == b
    assert len(a) == 64


def test_fresh_reappearance_is_admitted():
    master = stable_hash_hex("local-master")
    previous_boot, record = simulate_initial_admission(master)

    current_boot = boot_for_epoch("challenge-2", "boot-2", "epoch-2")

    attempt = attempt_reappearance(
        record=record,
        expected_current_code=current_boot.nerve_admission_code,
        current_boot=current_boot,
        current_challenge="challenge-2",
        previous_boot=previous_boot,
        previous_challenge="challenge-1",
    )

    assert attempt.decision == "admit"
    assert attempt.old_code_reused is False
    assert len(attempt.continuity_commitment) == 64


def test_revoked_reappearance_is_rejected():
    master = stable_hash_hex("local-master")
    previous_boot, record = simulate_initial_admission(master)

    revoked = build_continuity_record(
        nerve_binding_commitment=record.nerve_binding_commitment,
        origin_hint_commitment=record.origin_hint_commitment,
        birth_epoch=record.birth_epoch,
        last_seen_epoch=record.last_seen_epoch,
        revoked=True,
    )

    current_boot = boot_for_epoch("challenge-2", "boot-2", "epoch-2")

    attempt = attempt_reappearance(
        record=revoked,
        expected_current_code=current_boot.nerve_admission_code,
        current_boot=current_boot,
        current_challenge="challenge-2",
        previous_boot=previous_boot,
        previous_challenge="challenge-1",
        existing_revoked=True,
    )

    assert attempt.decision == "revoke"


def test_validate_reappearance_scenario_passes():
    result = validate_reappearance_scenario()

    assert result.continuity_preserved is True
    assert result.old_code_rejected is True
    assert result.current_code_accepted is True
    assert result.revoked_rejected is True
    assert result.passed is True
