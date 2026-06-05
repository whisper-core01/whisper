from rotor_close_code_v01 import (
    RotorCloseContext,
    derive_key_destruction_commitment,
    derive_rotor_close_code,
    derive_shutdown_step_digest,
    validate_rotor_close_code,
)
from session_hash_v01 import SessionContext, derive_session_hash


def _session_hash():
    return derive_session_hash(
        SessionContext(
            sol_id="sol",
            epoch="1",
            local_ephemeral_material="local",
            remote_ephemeral_material="remote",
            session_nonce="nonce",
            message_commitment="message",
            transfer_profile_commitment="profile",
        )
    )


def _close_context(close_reason="USER_LEFT_SESSION", closed_at=10):
    session_hash = _session_hash()

    return RotorCloseContext(
        session_hash=session_hash,
        shutdown_nonce="shutdown",
        close_reason=close_reason,
        wasm_purge_digest=derive_shutdown_step_digest(session_hash, "WASM_PURGE", "wasm"),
        volatile_zeroize_digest=derive_shutdown_step_digest(session_hash, "VOLATILE_ZEROIZE", "zeroize"),
        custody_freeze_digest=derive_shutdown_step_digest(session_hash, "CUSTODY_FREEZE", "custody"),
        key_destruction_commitment=derive_key_destruction_commitment(session_hash, "epoch-1", "destroy"),
        closed_at=closed_at,
    )


def test_shutdown_step_digest_is_deterministic():
    session_hash = _session_hash()

    a = derive_shutdown_step_digest(session_hash, "WASM_PURGE", "nonce")
    b = derive_shutdown_step_digest(session_hash, "WASM_PURGE", "nonce")

    assert a == b
    assert len(a) == 64


def test_shutdown_step_digest_changes_with_step():
    session_hash = _session_hash()

    a = derive_shutdown_step_digest(session_hash, "WASM_PURGE", "nonce")
    b = derive_shutdown_step_digest(session_hash, "VOLATILE_ZEROIZE", "nonce")

    assert a != b


def test_key_destruction_commitment_is_deterministic():
    session_hash = _session_hash()

    a = derive_key_destruction_commitment(session_hash, "epoch-1", "nonce")
    b = derive_key_destruction_commitment(session_hash, "epoch-1", "nonce")

    assert a == b
    assert len(a) == 64


def test_key_destruction_commitment_changes_with_nonce():
    session_hash = _session_hash()

    a = derive_key_destruction_commitment(session_hash, "epoch-1", "nonce-a")
    b = derive_key_destruction_commitment(session_hash, "epoch-1", "nonce-b")

    assert a != b


def test_rotor_close_code_is_deterministic():
    ctx = _close_context()

    a = derive_rotor_close_code(ctx)
    b = derive_rotor_close_code(ctx)

    assert a == b
    assert len(a) == 64


def test_rotor_close_code_changes_with_reason():
    a = derive_rotor_close_code(_close_context(close_reason="USER_LEFT_SESSION"))
    b = derive_rotor_close_code(_close_context(close_reason="USER_CANCELLED_TRANSFER"))

    assert a != b


def test_rotor_close_code_changes_with_time():
    a = derive_rotor_close_code(_close_context(closed_at=10))
    b = derive_rotor_close_code(_close_context(closed_at=11))

    assert a != b


def test_invalid_close_reason_rejected():
    try:
        derive_rotor_close_code(
            _close_context(close_reason="BAD_REASON")  # type: ignore[arg-type]
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for invalid close_reason")


def test_negative_closed_at_rejected():
    try:
        derive_rotor_close_code(_close_context(closed_at=-1))
    except ValueError:
        return

    raise AssertionError("Expected ValueError for negative closed_at")


def test_validate_rotor_close_code_true_and_false():
    a = derive_rotor_close_code(_close_context())
    b = derive_rotor_close_code(_close_context(closed_at=11))

    assert validate_rotor_close_code(a, a) is True
    assert validate_rotor_close_code(a, b) is False
