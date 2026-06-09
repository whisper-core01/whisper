from verve_wake_seed_rotation_v01 import (
    FROZEN_WINDOW_SECONDS,
    LuksHeaderMock,
    VerveVault,
    clean_shutdown_prepare_verve_wake_path,
    configure_luks_verve_keyslot,
    consume_rotating_code,
    derive_rotating_code,
    freeze_code_on_first_input,
    frozen_code_expired,
    generate_wake_seed,
    guided_link,
    handoff_wake_seed_to_verve,
    human_passphrase_is_fallback,
    pre_luks_stage_contains_core_secrets,
    revoke_verve_keyslot,
    rotating_code_contains_luks_key,
    start_rotating_code_session,
    update_rotating_code_session,
    verve_attempt_luks_unlock,
    verve_contains_vault_or_flv,
    verve_wake_seed_summary,
    wake_seed_is_64_chars,
    wake_seed_is_well_formed,
    zeroize_wake_seed,
)


def test_clean_shutdown_generates_wake_seed():
    assert guided_link("clean_shutdown_generates_wake_seed")

    wake_seed = generate_wake_seed("entropy-1")

    assert wake_seed.state == "GENERATED"
    assert wake_seed_is_64_chars(wake_seed.seed) is True
    assert wake_seed_is_well_formed(wake_seed.seed) is True


def test_wake_seed_configures_verve_luks_keyslot():
    assert guided_link("wake_seed_configures_verve_luks_keyslot")

    luks = LuksHeaderMock()
    wake_seed = generate_wake_seed("entropy-1")

    configure_luks_verve_keyslot(luks, "verve-slot-1", wake_seed)

    assert "verve-slot-1" in luks.verve_keyslots


def test_wake_seed_transmitted_to_verve_before_shutdown():
    assert guided_link("wake_seed_transmitted_to_verve_before_shutdown")

    verve = VerveVault()
    wake_seed = generate_wake_seed("entropy-1")

    handoff_wake_seed_to_verve(wake_seed, verve, "verve-slot-1")

    assert wake_seed.state == "HANDED_TO_VERVE"
    assert verve.wake_seed is not None
    assert verve.keyslot_id == "verve-slot-1"


def test_wake_seed_zeroized_after_handoff():
    assert guided_link("wake_seed_zeroized_after_handoff")

    verve = VerveVault()
    wake_seed = generate_wake_seed("entropy-1")

    handoff_wake_seed_to_verve(wake_seed, verve, "verve-slot-1")
    zeroize_wake_seed(wake_seed)

    assert wake_seed.state == "ZEROIZED"
    assert wake_seed.seed == "\x00" * 64


def test_rotating_code_derived_from_wake_seed():
    assert guided_link("rotating_code_derived_from_wake_seed")

    wake_seed = generate_wake_seed("entropy-1")

    code = derive_rotating_code(wake_seed.seed, 0)

    assert code.state == "ROTATING"
    assert len(code.code) == 16
    assert code.block_index == 0


def test_rotating_code_changes_every_10_seconds():
    assert guided_link("rotating_code_changes_every_10_seconds")

    wake_seed = generate_wake_seed("entropy-1")

    code_0 = derive_rotating_code(wake_seed.seed, 0)
    code_9 = derive_rotating_code(wake_seed.seed, 9)
    code_10 = derive_rotating_code(wake_seed.seed, 10)

    assert code_0.code == code_9.code
    assert code_0.code != code_10.code


def test_rotating_code_freezes_on_first_input():
    assert guided_link("rotating_code_freezes_on_first_input")

    wake_seed = generate_wake_seed("entropy-1")
    session = start_rotating_code_session(wake_seed.seed, 0)

    first_code = session.current_code.code

    freeze_code_on_first_input(session, 5)
    update_rotating_code_session(session, wake_seed.seed, 20)

    assert session.current_code.state == "FROZEN"
    assert session.current_code.code == first_code


def test_frozen_code_expires_after_max_window():
    assert guided_link("frozen_code_expires_after_max_window")

    wake_seed = generate_wake_seed("entropy-1")
    session = start_rotating_code_session(wake_seed.seed, 0)

    freeze_code_on_first_input(session, 5)

    assert frozen_code_expired(session, 5 + FROZEN_WINDOW_SECONDS) is False
    assert frozen_code_expired(session, 5 + FROZEN_WINDOW_SECONDS + 1) is True


def test_rotating_code_is_one_shot_after_consumption():
    assert guided_link("rotating_code_is_one_shot_after_consumption")

    wake_seed = generate_wake_seed("entropy-1")
    session = start_rotating_code_session(wake_seed.seed, 0)

    consume_rotating_code(session)

    assert session.consumed is True
    assert session.current_code.state == "CONSUMED"


def test_verve_unlocks_luks_with_wake_seed():
    assert guided_link("verve_unlocks_luks_with_wake_seed")

    luks, verve, _wake_seed = clean_shutdown_prepare_verve_wake_path(
        entropy="entropy-1",
    )

    decision, attempt = verve_attempt_luks_unlock(luks, verve)

    assert decision == "unlock_allowed"
    assert attempt is not None
    assert attempt.zeroized_after_attempt is True


def test_verve_zeroizes_after_unlock():
    assert guided_link("verve_zeroizes_after_unlock")

    luks, verve, _wake_seed = clean_shutdown_prepare_verve_wake_path(
        entropy="entropy-1",
    )

    verve_attempt_luks_unlock(luks, verve)

    assert verve.wake_seed is None
    assert verve.zeroized_after_unlock is True


def test_wrong_wake_seed_does_not_unlock_luks():
    assert guided_link("wrong_wake_seed_does_not_unlock_luks")

    luks, verve, _wake_seed = clean_shutdown_prepare_verve_wake_path(
        entropy="entropy-1",
    )

    verve.wake_seed = generate_wake_seed("wrong-entropy").seed

    decision, attempt = verve_attempt_luks_unlock(luks, verve)

    assert decision == "unlock_rejected"
    assert attempt is not None
    assert attempt.zeroized_after_attempt is True
    assert verve.wake_seed is None


def test_revoked_verve_keyslot_rejected():
    assert guided_link("revoked_verve_keyslot_rejected")

    luks, verve, _wake_seed = clean_shutdown_prepare_verve_wake_path(
        entropy="entropy-1",
    )

    revoke_verve_keyslot(luks, verve, "verve-slot-1")

    decision, attempt = verve_attempt_luks_unlock(luks, verve)

    assert decision == "unlock_rejected"
    assert attempt is None


def test_human_passphrase_remains_fallback():
    assert guided_link("human_passphrase_remains_fallback")

    luks = LuksHeaderMock()

    assert human_passphrase_is_fallback(luks) is True


def test_pre_luks_stage_does_not_contain_core_secrets():
    assert guided_link("pre_luks_stage_does_not_contain_core_secrets")

    assert pre_luks_stage_contains_core_secrets() is False
    assert verve_contains_vault_or_flv() is False
    assert rotating_code_contains_luks_key() is False


def test_clean_shutdown_prepares_verve_path_and_zeroizes_whisper_copy():
    assert guided_link("clean_shutdown_prepares_verve_path_and_zeroizes_whisper_copy")

    luks, verve, wake_seed = clean_shutdown_prepare_verve_wake_path(
        entropy="entropy-1",
    )

    assert "verve-slot-1" in luks.verve_keyslots
    assert verve.wake_seed is not None
    assert wake_seed.state == "ZEROIZED"
    assert wake_seed.seed == "\x00" * 64


def test_verve_wake_seed_summary():
    assert guided_link("verve_wake_seed_summary")

    summary = verve_wake_seed_summary()

    assert summary["wake_seed_zeroized_in_whisper"] is True
    assert summary["wake_seed_length"] == 64
    assert summary["code_rotates"] is True
    assert summary["unlock_decision"] == "unlock_allowed"
    assert summary["verve_zeroized_after_unlock"] is True
    assert summary["human_fallback"] is True
    assert summary["pre_luks_contains_core_secrets"] is False
