from secure_session_shutdown_v01 import (
    block_new_material,
    close_session,
    create_runtime_state,
    destroy_keys,
    freeze_custody,
    generate_rotor_close,
    purge_wasm,
    revoke_closed_session,
    secure_shutdown_session,
    zeroize_volatile,
)
from session_hash_v01 import SessionContext
from session_revocation_v01 import SessionRevocationStore, is_session_revoked


def _ctx():
    return SessionContext(
        sol_id="sol",
        epoch="1",
        local_ephemeral_material="local",
        remote_ephemeral_material="remote",
        session_nonce="nonce",
        message_commitment="message",
        transfer_profile_commitment="profile",
    )


def test_create_runtime_state_active():
    runtime = create_runtime_state(_ctx())

    assert runtime.state == "ACTIVE"
    assert runtime.accepts_new_material is True
    assert len(runtime.session_hash) == 64


def test_secure_shutdown_session_full_sequence():
    runtime = create_runtime_state(_ctx())
    store = SessionRevocationStore()

    result = secure_shutdown_session(
        runtime=runtime,
        store=store,
        close_reason="USER_LEFT_SESSION",
        revocation_reason="USER_LEFT_SESSION",
        shutdown_nonce="shutdown",
        key_epoch="epoch-1",
        destruction_nonce="destroy",
        closed_at=123,
    )

    assert result.final_state == "CLOSED"
    assert result.revoked is True
    assert result.keys_destroyed is True
    assert result.wasm_purged is True
    assert result.volatile_zeroized is True
    assert result.custody_frozen is True
    assert result.accepts_new_material is False
    assert len(result.rotor_close_code) == 64
    assert is_session_revoked(store, result.session_hash, now=123) is True
    assert result.shutdown_steps == [
        "BLOCK_NEW_MATERIAL",
        "FREEZE_CUSTODY",
        "PURGE_WASM",
        "ZEROIZE_VOLATILE",
        "GENERATE_ROTOR_CLOSE",
        "DESTROY_KEYS",
        "REVOKE_SESSION",
        "CLOSE_SESSION",
    ]


def test_cannot_freeze_custody_before_blocking_material():
    runtime = create_runtime_state(_ctx())

    try:
        freeze_custody(runtime, "nonce")
    except ValueError:
        return

    raise AssertionError("Expected ValueError")


def test_cannot_purge_wasm_before_custody_freeze():
    runtime = create_runtime_state(_ctx())
    block_new_material(runtime, "block")

    try:
        purge_wasm(runtime, "wasm")
    except ValueError:
        return

    raise AssertionError("Expected ValueError")


def test_cannot_zeroize_before_wasm_purge():
    runtime = create_runtime_state(_ctx())

    try:
        zeroize_volatile(runtime, "zeroize")
    except ValueError:
        return

    raise AssertionError("Expected ValueError")


def test_cannot_generate_rotor_before_zeroize():
    runtime = create_runtime_state(_ctx())
    block_new_material(runtime, "block")
    freeze_custody(runtime, "custody")
    purge_wasm(runtime, "wasm")

    try:
        generate_rotor_close(
            runtime=runtime,
            shutdown_nonce="shutdown",
            close_reason="USER_LEFT_SESSION",
            key_epoch="epoch-1",
            destruction_nonce="destroy",
            closed_at=123,
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError")


def test_cannot_destroy_keys_before_rotor_close():
    runtime = create_runtime_state(_ctx())
    block_new_material(runtime, "block")
    freeze_custody(runtime, "custody")
    purge_wasm(runtime, "wasm")
    zeroize_volatile(runtime, "zeroize")

    try:
        destroy_keys(runtime, "keys")
    except ValueError:
        return

    raise AssertionError("Expected ValueError")


def test_cannot_revoke_before_key_destruction():
    runtime = create_runtime_state(_ctx())
    store = SessionRevocationStore()

    try:
        revoke_closed_session(
            runtime=runtime,
            store=store,
            reason="USER_LEFT_SESSION",
            created_at=123,
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError")


def test_cannot_close_before_revocation():
    runtime = create_runtime_state(_ctx())

    try:
        close_session(runtime)
    except ValueError:
        return

    raise AssertionError("Expected ValueError")
