from core_session_revocation_v01 import (
    attempt_session_reactivation,
    build_session_identity,
    close_session,
    create_session_store,
    daemon_resend_restores_session,
    decide_inbound_for_session,
    decide_outbound_for_session,
    is_session_revoked,
    lemonade_fallback_restores_session,
    organ_restart_restores_session,
    register_session,
    revoke_core_session,
    session_revocation_summary,
)


def _store_with_active_session():
    store = create_session_store()

    identity = build_session_identity(
        session_id="session-1",
        session_start_seal="seal-1",
        core_binding_material="core-binding",
    )

    record = register_session(store, identity)

    return store, identity, record


def test_register_session_starts_active():
    store, identity, record = _store_with_active_session()

    assert record.state == "ACTIVE"
    assert record.revocation_flag is False
    assert is_session_revoked(store, identity.session_id) is False


def test_revoke_active_session_sets_core_truth():
    store, identity, _record = _store_with_active_session()

    revoked = revoke_core_session(
        store=store,
        session_id=identity.session_id,
        revocation_epoch="epoch-2",
        reason="USER_REVOKED",
    )

    assert revoked.state == "REVOKED"
    assert revoked.revocation_flag is True
    assert revoked.revocation_epoch == "epoch-2"
    assert revoked.revocation_reason == "USER_REVOKED"
    assert is_session_revoked(store, identity.session_id) is True


def test_revocation_is_idempotent():
    store, identity, _record = _store_with_active_session()

    revoke_core_session(store, identity.session_id, "epoch-2", "USER_REVOKED")
    revoked = revoke_core_session(store, identity.session_id, "epoch-3", "CORE_POLICY")

    assert revoked.state == "REVOKED"
    assert is_session_revoked(store, identity.session_id) is True
    assert identity.session_id in store.revoked_sessions


def test_revoked_session_cannot_reactivate_with_old_seal():
    store, identity, _record = _store_with_active_session()

    revoke_core_session(store, identity.session_id, "epoch-2", "USER_REVOKED")

    decision = attempt_session_reactivation(
        store,
        identity.session_id,
        proposed_start_seal="seal-1",
    )

    assert decision == "reject"


def test_revoked_session_cannot_reactivate_with_new_seal():
    store, identity, _record = _store_with_active_session()

    revoke_core_session(store, identity.session_id, "epoch-2", "USER_REVOKED")

    decision = attempt_session_reactivation(
        store,
        identity.session_id,
        proposed_start_seal="seal-2",
    )

    assert decision == "reject"


def test_closed_session_cannot_reactivate():
    store, identity, _record = _store_with_active_session()

    close_session(store, identity.session_id, close_code="close-1")

    decision = attempt_session_reactivation(
        store,
        identity.session_id,
        proposed_start_seal="seal-1",
    )

    assert decision == "reject"


def test_active_session_with_correct_seal_can_continue_before_revocation():
    store, identity, _record = _store_with_active_session()

    decision = attempt_session_reactivation(
        store,
        identity.session_id,
        proposed_start_seal="seal-1",
    )

    assert decision == "allow"


def test_active_session_with_wrong_seal_is_denied():
    store, identity, _record = _store_with_active_session()

    decision = attempt_session_reactivation(
        store,
        identity.session_id,
        proposed_start_seal="wrong-seal",
    )

    assert decision == "deny"


def test_revoked_session_blocks_inbound_even_if_material_coherent():
    store, identity, _record = _store_with_active_session()

    revoke_core_session(store, identity.session_id, "epoch-2", "USER_REVOKED")

    decision = decide_inbound_for_session(
        store,
        identity.session_id,
        material_coherent=True,
    )

    assert decision == "reject"


def test_non_revoked_inbound_rejects_incoherent_material():
    store, identity, _record = _store_with_active_session()

    decision = decide_inbound_for_session(
        store,
        identity.session_id,
        material_coherent=False,
    )

    assert decision == "reject"


def test_non_revoked_inbound_accepts_coherent_active_material():
    store, identity, _record = _store_with_active_session()

    decision = decide_inbound_for_session(
        store,
        identity.session_id,
        material_coherent=True,
    )

    assert decision == "allow"


def test_revoked_session_blocks_outbound():
    store, identity, _record = _store_with_active_session()

    revoke_core_session(store, identity.session_id, "epoch-2", "USER_REVOKED")

    decision = decide_outbound_for_session(store, identity.session_id)

    assert decision == "reject"


def test_closed_session_blocks_outbound():
    store, identity, _record = _store_with_active_session()

    close_session(store, identity.session_id, close_code="close-1")

    decision = decide_outbound_for_session(store, identity.session_id)

    assert decision == "reject"


def test_unknown_session_denied():
    store = create_session_store()

    assert attempt_session_reactivation(store, "unknown", "seal") == "deny"
    assert decide_inbound_for_session(store, "unknown", True) == "deny"
    assert decide_outbound_for_session(store, "unknown") == "deny"


def test_revoked_unknown_session_creates_revoked_record():
    store = create_session_store()

    record = revoke_core_session(
        store,
        session_id="unknown-session",
        revocation_epoch="epoch-2",
        reason="REPLAY_DETECTED",
    )

    assert record.state == "REVOKED"
    assert is_session_revoked(store, "unknown-session") is True


def test_organ_restart_does_not_restore_revoked_session():
    store, identity, _record = _store_with_active_session()

    revoke_core_session(store, identity.session_id, "epoch-2", "STATE_VIOLATION")

    assert organ_restart_restores_session(store, identity.session_id) is False


def test_lemonade_fallback_does_not_restore_revoked_session():
    store, identity, _record = _store_with_active_session()

    revoke_core_session(store, identity.session_id, "epoch-2", "STATE_VIOLATION")

    assert lemonade_fallback_restores_session(store, identity.session_id) is False


def test_daemon_resend_does_not_restore_revoked_session():
    store, identity, _record = _store_with_active_session()

    revoke_core_session(store, identity.session_id, "epoch-2", "STATE_VIOLATION")

    assert daemon_resend_restores_session(store, identity.session_id) is False


def test_close_ignored_after_revocation():
    store, identity, _record = _store_with_active_session()

    revoke_core_session(store, identity.session_id, "epoch-2", "USER_REVOKED")
    record = close_session(store, identity.session_id, close_code="close-after-revoke")

    assert record.state == "REVOKED"
    assert record.close_code is None
    assert "close_ignored_session_revoked" in record.events


def test_session_revocation_summary():
    store, identity, _record = _store_with_active_session()

    revoke_core_session(store, identity.session_id, "epoch-2", "USER_REVOKED")

    summary = session_revocation_summary(store, identity.session_id)

    assert summary["session_id"] == identity.session_id
    assert summary["known"] is True
    assert summary["state"] == "REVOKED"
    assert summary["revoked"] is True
    assert summary["revocation_epoch"] == "epoch-2"
    assert summary["revocation_reason"] == "USER_REVOKED"
