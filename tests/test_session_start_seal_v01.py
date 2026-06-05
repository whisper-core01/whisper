from session_hash_v01 import SessionContext, derive_session_hash
from session_start_seal_v01 import (
    SessionStartContext,
    derive_session_start_seal,
    derive_start_step_digest,
    validate_session_start_seal,
)


def _session_context(session_nonce="session-nonce"):
    return SessionContext(
        sol_id="sol",
        epoch="1",
        local_ephemeral_material="local",
        remote_ephemeral_material="remote",
        session_nonce=session_nonce,
        message_commitment="message",
        transfer_profile_commitment="profile",
    )


def _session_hash():
    return derive_session_hash(_session_context())


def _start_context(open_reason="USER_STARTED_SESSION", created_at=1):
    session_ctx = _session_context()
    session_hash = derive_session_hash(session_ctx)

    return SessionStartContext(
        session_hash=session_hash,
        session_nonce=session_ctx.session_nonce,
        start_nonce="start",
        open_reason=open_reason,
        wasm_init_digest=derive_start_step_digest(session_hash, "WASM_INITIALIZED", "wasm"),
        custody_init_digest=derive_start_step_digest(session_hash, "CUSTODY_EMPTY", "custody"),
        volatile_init_digest=derive_start_step_digest(session_hash, "VOLATILE_BUFFERS_EMPTY", "volatile"),
        created_at=created_at,
    )


def test_start_step_digest_is_deterministic():
    session_hash = _session_hash()

    a = derive_start_step_digest(session_hash, "WASM_INITIALIZED", "nonce")
    b = derive_start_step_digest(session_hash, "WASM_INITIALIZED", "nonce")

    assert a == b
    assert len(a) == 64


def test_start_step_digest_changes_with_step():
    session_hash = _session_hash()

    a = derive_start_step_digest(session_hash, "WASM_INITIALIZED", "nonce")
    b = derive_start_step_digest(session_hash, "CUSTODY_EMPTY", "nonce")

    assert a != b


def test_session_start_seal_is_deterministic():
    ctx = _start_context()

    a = derive_session_start_seal(ctx)
    b = derive_session_start_seal(ctx)

    assert a == b
    assert len(a) == 64


def test_session_start_seal_changes_with_reason():
    a = derive_session_start_seal(_start_context(open_reason="USER_STARTED_SESSION"))
    b = derive_session_start_seal(_start_context(open_reason="TRANSFER_REQUESTED"))

    assert a != b


def test_session_start_seal_changes_with_time():
    a = derive_session_start_seal(_start_context(created_at=1))
    b = derive_session_start_seal(_start_context(created_at=2))

    assert a != b


def test_session_start_seal_changes_with_session_nonce():
    session_ctx_a = _session_context(session_nonce="nonce-a")
    session_hash_a = derive_session_hash(session_ctx_a)

    session_ctx_b = _session_context(session_nonce="nonce-b")
    session_hash_b = derive_session_hash(session_ctx_b)

    a = derive_session_start_seal(
        SessionStartContext(
            session_hash=session_hash_a,
            session_nonce=session_ctx_a.session_nonce,
            start_nonce="start",
            open_reason="USER_STARTED_SESSION",
            wasm_init_digest=derive_start_step_digest(session_hash_a, "WASM_INITIALIZED", "wasm"),
            custody_init_digest=derive_start_step_digest(session_hash_a, "CUSTODY_EMPTY", "custody"),
            volatile_init_digest=derive_start_step_digest(session_hash_a, "VOLATILE_BUFFERS_EMPTY", "volatile"),
            created_at=1,
        )
    )

    b = derive_session_start_seal(
        SessionStartContext(
            session_hash=session_hash_b,
            session_nonce=session_ctx_b.session_nonce,
            start_nonce="start",
            open_reason="USER_STARTED_SESSION",
            wasm_init_digest=derive_start_step_digest(session_hash_b, "WASM_INITIALIZED", "wasm"),
            custody_init_digest=derive_start_step_digest(session_hash_b, "CUSTODY_EMPTY", "custody"),
            volatile_init_digest=derive_start_step_digest(session_hash_b, "VOLATILE_BUFFERS_EMPTY", "volatile"),
            created_at=1,
        )
    )

    assert a != b


def test_invalid_open_reason_rejected():
    try:
        derive_session_start_seal(
            _start_context(open_reason="BAD_REASON")  # type: ignore[arg-type]
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for invalid open_reason")


def test_negative_created_at_rejected():
    try:
        derive_session_start_seal(_start_context(created_at=-1))
    except ValueError:
        return

    raise AssertionError("Expected ValueError for negative created_at")


def test_validate_session_start_seal_true_and_false():
    a = derive_session_start_seal(_start_context())
    b = derive_session_start_seal(_start_context(created_at=2))

    assert validate_session_start_seal(a, a) is True
    assert validate_session_start_seal(a, b) is False


def test_invalid_session_hash_rejected():
    try:
        derive_start_step_digest("not-a-valid-hash", "WASM_INITIALIZED", "nonce")
    except ValueError:
        return

    raise AssertionError("Expected ValueError for invalid session_hash")
