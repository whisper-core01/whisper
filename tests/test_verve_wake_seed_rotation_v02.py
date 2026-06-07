from verve_wake_seed_rotation_v02 import (
    WAKE_SEED_LABELS,
    LocalShard,
    RotationLog,
    WakeSeedSession,
    create_rotation_model,
    create_wake_seed_root,
    derive_wake_seed_session,
    guided_link,
    human_passphrase_remains_valid_fallback,
    no_network_required_for_any_rotation_step,
    old_session_seed_cannot_unlock_luks_after_rotation,
    verve_luks_keyslot_updates_on_rotation,
    verve_zeroizes_all_seeds_after_unlock,
    wake_seed_root_is_never_exposed,
    wake_seed_rotation_summary,
    wake_seed_session_is_derived_from_root,
)


def test_wake_seed_v02_labels_are_present():
    assert guided_link("wake_seed_v02_labels_are_present")

    assert "wake_seed_root" in WAKE_SEED_LABELS
    assert "wake_seed_session" in WAKE_SEED_LABELS
    assert "wake_seed_rotates_on_clean_shutdown" in WAKE_SEED_LABELS
    assert "wake_seed_not_reused_after_boot" in WAKE_SEED_LABELS
    assert "wake_seed_split_optional" in WAKE_SEED_LABELS
    assert "verve_rotation_log_local_only" in WAKE_SEED_LABELS


def test_wake_seed_root_is_never_exposed():
    assert guided_link("wake_seed_root_is_never_exposed")

    model = create_rotation_model()

    assert wake_seed_root_is_never_exposed(model) is True
    assert model.root.exposed is False


def test_wake_seed_session_is_derived_from_root():
    assert guided_link("wake_seed_session_is_derived_from_root")

    root = create_wake_seed_root(b"root-material")
    session = derive_wake_seed_session(
        root=root,
        boot_counter=1,
        rotation_nonce=b"session-nonce",
    )

    assert (
        wake_seed_session_is_derived_from_root(
            root=root,
            session=session,
            rotation_nonce=b"session-nonce",
        )
        is True
    )


def test_different_session_nonce_derives_different_seed():
    assert guided_link("different_session_nonce_derives_different_seed")

    root = create_wake_seed_root(b"root-material")

    session_a = derive_wake_seed_session(
        root=root,
        boot_counter=1,
        rotation_nonce=b"nonce-a",
    )

    session_b = derive_wake_seed_session(
        root=root,
        boot_counter=1,
        rotation_nonce=b"nonce-b",
    )

    assert session_a.fingerprint != session_b.fingerprint


def test_different_boot_counter_derives_different_seed():
    assert guided_link("different_boot_counter_derives_different_seed")

    root = create_wake_seed_root(b"root-material")

    session_a = derive_wake_seed_session(
        root=root,
        boot_counter=1,
        rotation_nonce=b"same-nonce",
    )

    session_b = derive_wake_seed_session(
        root=root,
        boot_counter=2,
        rotation_nonce=b"same-nonce",
    )

    assert session_a.fingerprint != session_b.fingerprint


def test_clean_shutdown_rotates_session_seed():
    assert guided_link("clean_shutdown_rotates_session_seed")

    model = create_rotation_model()

    old_fingerprint = model.current_session.fingerprint

    status = model.rotate_on_shutdown(
        shutdown_kind="clean_shutdown",
        rotation_nonce=b"next-nonce",
    )

    assert status == "rotation_ok"
    assert model.current_session.fingerprint != old_fingerprint
    assert model.rotation_log.last_rotation_status == "rotation_ok"


def test_dirty_shutdown_does_not_rotate_session_seed():
    assert guided_link("dirty_shutdown_does_not_rotate_session_seed")

    model = create_rotation_model()

    old_fingerprint = model.current_session.fingerprint

    status = model.rotate_on_shutdown(
        shutdown_kind="dirty_shutdown",
        rotation_nonce=b"next-nonce",
    )

    assert status == "rotation_nok"
    assert model.current_session.fingerprint == old_fingerprint
    assert model.rotation_log.last_rotation_status == "rotation_nok"


def test_verve_luks_keyslot_updates_on_rotation():
    assert guided_link("verve_luks_keyslot_updates_on_rotation")

    model = create_rotation_model()

    model.rotate_on_shutdown(
        shutdown_kind="clean_shutdown",
        rotation_nonce=b"next-nonce",
    )

    assert verve_luks_keyslot_updates_on_rotation(model) is True
    assert model.keyslot.accepted_session_fingerprint == model.current_session.fingerprint


def test_old_session_seed_cannot_unlock_luks_after_rotation():
    assert guided_link("old_session_seed_cannot_unlock_luks_after_rotation")

    model = create_rotation_model()
    old_session = model.current_session

    model.rotate_on_shutdown(
        shutdown_kind="clean_shutdown",
        rotation_nonce=b"next-nonce",
    )

    assert old_session_seed_cannot_unlock_luks_after_rotation(
        model,
        old_session,
    ) is True

    assert model.keyslot.accepts_session(old_session) is False
    assert old_session.state == "invalidated"


def test_current_session_can_unlock_before_zeroization():
    assert guided_link("current_session_can_unlock_before_zeroization")

    model = create_rotation_model()

    decision = model.unlock_with_session(model.current_session)

    assert decision == "unlock_allowed"
    assert model.current_session.used_for_unlock is True
    assert model.current_session.state == "zeroized"


def test_wrong_old_or_foreign_session_is_rejected_and_zeroized():
    assert guided_link("wrong_old_or_foreign_session_is_rejected_and_zeroized")

    model = create_rotation_model()

    foreign_session = WakeSeedSession(
        material=b"foreign-session-material",
        boot_counter=999,
        root_generation=999,
    )

    decision = model.unlock_with_session(foreign_session)

    assert decision == "unlock_rejected"
    assert foreign_session.state == "zeroized"


def test_verve_zeroizes_all_seeds_after_unlock():
    assert guided_link("verve_zeroizes_all_seeds_after_unlock")

    model = create_rotation_model()

    assert verve_zeroizes_all_seeds_after_unlock(model) is True
    assert model.root.zeroized is True
    assert model.current_session.state == "zeroized"


def test_human_passphrase_remains_valid_fallback():
    assert guided_link("human_passphrase_remains_valid_fallback")

    model = create_rotation_model(human_passphrase="valid-human-passphrase")

    assert human_passphrase_remains_valid_fallback(
        model,
        "valid-human-passphrase",
    ) is True

    assert model.unlock_with_human_passphrase("wrong-passphrase") == "unlock_rejected"


def test_no_network_required_for_any_rotation_step():
    assert guided_link("no_network_required_for_any_rotation_step")

    model = create_rotation_model()

    assert no_network_required_for_any_rotation_step(model) is True

    model.network_required = True

    assert no_network_required_for_any_rotation_step(model) is False


def test_optional_local_shard_can_be_used_without_network():
    assert guided_link("optional_local_shard_can_be_used_without_network")

    shard = LocalShard(
        enabled=True,
        encrypted_local_file_present=True,
        human_passphrase_required=False,
        network_required=False,
    )

    model = create_rotation_model(shard=shard)

    assert model.shard.is_available() is True
    assert model.no_network_required() is True

    status = model.rotate_on_shutdown(
        shutdown_kind="clean_shutdown",
        rotation_nonce=b"local-shard-rotation",
    )

    assert status == "rotation_ok"


def test_optional_shard_rejects_network_dependency():
    assert guided_link("optional_shard_rejects_network_dependency")

    shard = LocalShard(
        enabled=True,
        encrypted_local_file_present=True,
        human_passphrase_required=False,
        network_required=True,
    )

    model = create_rotation_model(shard=shard)

    assert model.shard.is_local_only() is False
    assert model.no_network_required() is False

    status = model.rotate_on_shutdown(
        shutdown_kind="clean_shutdown",
        rotation_nonce=b"network-shard-rotation",
    )

    assert status == "rotation_nok"


def test_rotation_log_is_local_only_and_minimal():
    assert guided_link("rotation_log_is_local_only_and_minimal")

    log = RotationLog()

    assert log.is_sovereign_local_only() is True

    log.telemetry_enabled = True

    assert log.is_sovereign_local_only() is False


def test_root_rotation_changes_future_session_derivation():
    assert guided_link("root_rotation_changes_future_session_derivation")

    root = create_wake_seed_root(b"root-material-v1")

    session_a = derive_wake_seed_session(
        root=root,
        boot_counter=1,
        rotation_nonce=b"same-nonce",
    )

    root.rotate_root(b"root-material-v2")

    session_b = derive_wake_seed_session(
        root=root,
        boot_counter=1,
        rotation_nonce=b"same-nonce",
    )

    assert root.generation == 2
    assert session_a.fingerprint != session_b.fingerprint


def test_wake_seed_rotation_summary():
    assert guided_link("wake_seed_rotation_summary")

    summary = wake_seed_rotation_summary()

    assert summary["wake_seed_root_is_never_exposed"] is True
    assert summary["rotation_status"] == "rotation_ok"
    assert summary["session_seed_changed"] is True
    assert summary["verve_luks_keyslot_updates_on_rotation"] is True
    assert summary["old_session_seed_can_unlock_after_rotation"] is False
    assert summary["human_passphrase_fallback"] == "unlock_allowed"
    assert summary["rotation_log_local_only"] is True
    assert summary["no_network_required"] is True
    assert summary["root_zeroized_after_unlock"] is True
    assert summary["session_zeroized_after_unlock"] is True
