from session_hash_v01 import (
    FragmentSessionContext,
    SessionContext,
    derive_fragment_session_tag,
    derive_session_hash,
)
from session_revocation_v01 import (
    SessionRevocationStore,
    expire_revocations,
    get_revocation_entry,
    is_session_revoked,
    mark_session_revoked,
    validate_not_revoked,
    validate_session_tag_not_revoked,
)


def _session_hash(nonce="nonce"):
    return derive_session_hash(
        SessionContext(
            sol_id="sol",
            epoch="1",
            local_ephemeral_material="local",
            remote_ephemeral_material="remote",
            session_nonce=nonce,
            message_commitment="message",
            transfer_profile_commitment="profile",
        )
    )


def test_session_is_not_revoked_by_default():
    store = SessionRevocationStore()
    session_hash = _session_hash()

    assert is_session_revoked(store, session_hash) is False
    assert validate_not_revoked(store, session_hash) is True


def test_mark_session_revoked():
    store = SessionRevocationStore()
    session_hash = _session_hash()

    entry = mark_session_revoked(
        store=store,
        session_hash=session_hash,
        reason="USER_LEFT_SESSION",
        scope="SESSION",
        created_at=10,
    )

    assert entry.session_hash == session_hash
    assert entry.reason == "USER_LEFT_SESSION"
    assert is_session_revoked(store, session_hash, now=10) is True
    assert validate_not_revoked(store, session_hash, now=10) is False


def test_temporary_revocation_expires():
    store = SessionRevocationStore()
    session_hash = _session_hash()

    mark_session_revoked(
        store=store,
        session_hash=session_hash,
        reason="SESSION_EXPIRED",
        scope="TEMPORARY",
        created_at=10,
        expires_at=20,
    )

    assert is_session_revoked(store, session_hash, now=19) is True
    assert is_session_revoked(store, session_hash, now=20) is False


def test_expire_revocations_removes_expired_entries():
    store = SessionRevocationStore()
    session_hash_a = _session_hash("a")
    session_hash_b = _session_hash("b")

    mark_session_revoked(
        store=store,
        session_hash=session_hash_a,
        reason="SESSION_EXPIRED",
        scope="TEMPORARY",
        created_at=10,
        expires_at=20,
    )

    mark_session_revoked(
        store=store,
        session_hash=session_hash_b,
        reason="USER_CANCELLED_TRANSFER",
        scope="SESSION",
        created_at=10,
    )

    removed = expire_revocations(store, now=20)

    assert removed == 1
    assert get_revocation_entry(store, session_hash_a, now=20) is None
    assert get_revocation_entry(store, session_hash_b, now=20) is not None


def test_validate_session_tag_not_revoked_accepts_valid_active_session():
    store = SessionRevocationStore()
    session_hash = _session_hash()

    tag = derive_fragment_session_tag(
        FragmentSessionContext(
            session_hash=session_hash,
            fragment_nonce="fragment",
            fragment_index_commitment="idx",
            fragment_role="primary",
            capsule_nonce="capsule",
        )
    )

    assert validate_session_tag_not_revoked(
        store=store,
        session_hash=session_hash,
        expected_tag=tag,
        observed_tag=tag,
    ) is True


def test_validate_session_tag_not_revoked_rejects_revoked_session():
    store = SessionRevocationStore()
    session_hash = _session_hash()

    tag = derive_fragment_session_tag(
        FragmentSessionContext(
            session_hash=session_hash,
            fragment_nonce="fragment",
            fragment_index_commitment="idx",
            fragment_role="primary",
            capsule_nonce="capsule",
        )
    )

    mark_session_revoked(
        store=store,
        session_hash=session_hash,
        reason="USER_LEFT_SESSION",
        scope="SESSION",
        created_at=10,
    )

    assert validate_session_tag_not_revoked(
        store=store,
        session_hash=session_hash,
        expected_tag=tag,
        observed_tag=tag,
        now=10,
    ) is False


def test_validate_session_tag_not_revoked_rejects_bad_tag():
    store = SessionRevocationStore()
    session_hash = _session_hash()

    tag_a = derive_fragment_session_tag(
        FragmentSessionContext(
            session_hash=session_hash,
            fragment_nonce="fragment-a",
            fragment_index_commitment="idx",
            fragment_role="primary",
            capsule_nonce="capsule",
        )
    )

    tag_b = derive_fragment_session_tag(
        FragmentSessionContext(
            session_hash=session_hash,
            fragment_nonce="fragment-b",
            fragment_index_commitment="idx",
            fragment_role="primary",
            capsule_nonce="capsule",
        )
    )

    assert validate_session_tag_not_revoked(
        store=store,
        session_hash=session_hash,
        expected_tag=tag_a,
        observed_tag=tag_b,
    ) is False


def test_invalid_reason_rejected():
    store = SessionRevocationStore()
    session_hash = _session_hash()

    try:
        mark_session_revoked(
            store=store,
            session_hash=session_hash,
            reason="BAD_REASON",  # type: ignore[arg-type]
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for invalid reason")


def test_invalid_scope_rejected():
    store = SessionRevocationStore()
    session_hash = _session_hash()

    try:
        mark_session_revoked(
            store=store,
            session_hash=session_hash,
            reason="USER_LEFT_SESSION",
            scope="BAD_SCOPE",  # type: ignore[arg-type]
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for invalid scope")
