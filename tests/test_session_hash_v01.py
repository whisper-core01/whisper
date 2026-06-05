from session_hash_v01 import (
    CapsuleSessionContext,
    FragmentSessionContext,
    RepairSessionContext,
    SessionContext,
    derive_capsule_session_tag,
    derive_fragment_session_tag,
    derive_repair_hash,
    derive_session_hash,
    validate_session_tag,
)


def _session_context(epoch="1", nonce="nonce"):
    return SessionContext(
        sol_id="sol",
        epoch=epoch,
        local_ephemeral_material="local",
        remote_ephemeral_material="remote",
        session_nonce=nonce,
        message_commitment="message",
        transfer_profile_commitment="profile",
    )


def test_derive_session_hash_is_deterministic():
    a = derive_session_hash(_session_context())
    b = derive_session_hash(_session_context())

    assert a == b
    assert len(a) == 64


def test_derive_session_hash_changes_with_epoch():
    a = derive_session_hash(_session_context(epoch="1"))
    b = derive_session_hash(_session_context(epoch="2"))

    assert a != b


def test_derive_session_hash_changes_with_nonce():
    a = derive_session_hash(_session_context(nonce="nonce-a"))
    b = derive_session_hash(_session_context(nonce="nonce-b"))

    assert a != b


def test_fragment_session_tag_is_deterministic():
    session_hash = derive_session_hash(_session_context())

    ctx = FragmentSessionContext(
        session_hash=session_hash,
        fragment_nonce="fragment-nonce",
        fragment_index_commitment="idx",
        fragment_role="primary",
        capsule_nonce="capsule-nonce",
    )

    a = derive_fragment_session_tag(ctx)
    b = derive_fragment_session_tag(ctx)

    assert a == b
    assert len(a) == 64


def test_fragment_session_tag_changes_with_role():
    session_hash = derive_session_hash(_session_context())

    primary = derive_fragment_session_tag(
        FragmentSessionContext(
            session_hash=session_hash,
            fragment_nonce="fragment-nonce",
            fragment_index_commitment="idx",
            fragment_role="primary",
            capsule_nonce="capsule-nonce",
        )
    )

    repair = derive_fragment_session_tag(
        FragmentSessionContext(
            session_hash=session_hash,
            fragment_nonce="fragment-nonce",
            fragment_index_commitment="idx",
            fragment_role="repair",
            capsule_nonce="capsule-nonce",
        )
    )

    assert primary != repair


def test_fragment_session_tag_rejects_invalid_role():
    session_hash = derive_session_hash(_session_context())

    try:
        derive_fragment_session_tag(
            FragmentSessionContext(
                session_hash=session_hash,
                fragment_nonce="fragment-nonce",
                fragment_index_commitment="idx",
                fragment_role="invalid",  # type: ignore[arg-type]
                capsule_nonce="capsule-nonce",
            )
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for invalid fragment role")


def test_capsule_session_tag_changes_with_epoch():
    session_hash = derive_session_hash(_session_context())

    a = derive_capsule_session_tag(
        CapsuleSessionContext(
            session_hash=session_hash,
            capsule_nonce="capsule",
            capsule_role="data",
            capsule_epoch="1",
        )
    )

    b = derive_capsule_session_tag(
        CapsuleSessionContext(
            session_hash=session_hash,
            capsule_nonce="capsule",
            capsule_role="data",
            capsule_epoch="2",
        )
    )

    assert a != b


def test_repair_hash_changes_with_counter():
    session_hash = derive_session_hash(_session_context())

    a = derive_repair_hash(
        RepairSessionContext(
            session_hash=session_hash,
            repair_epoch="1",
            repair_nonce="repair",
            repair_counter=0,
        )
    )

    b = derive_repair_hash(
        RepairSessionContext(
            session_hash=session_hash,
            repair_epoch="1",
            repair_nonce="repair",
            repair_counter=1,
        )
    )

    assert a != b


def test_repair_hash_rejects_negative_counter():
    session_hash = derive_session_hash(_session_context())

    try:
        derive_repair_hash(
            RepairSessionContext(
                session_hash=session_hash,
                repair_epoch="1",
                repair_nonce="repair",
                repair_counter=-1,
            )
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for negative repair_counter")


def test_validate_session_tag_true_and_false():
    session_hash = derive_session_hash(_session_context())

    tag = derive_fragment_session_tag(
        FragmentSessionContext(
            session_hash=session_hash,
            fragment_nonce="fragment-nonce",
            fragment_index_commitment="idx",
            fragment_role="primary",
            capsule_nonce="capsule-nonce",
        )
    )

    other = derive_fragment_session_tag(
        FragmentSessionContext(
            session_hash=session_hash,
            fragment_nonce="fragment-nonce-2",
            fragment_index_commitment="idx",
            fragment_role="primary",
            capsule_nonce="capsule-nonce",
        )
    )

    assert validate_session_tag(tag, tag) is True
    assert validate_session_tag(tag, other) is False


def test_invalid_session_hash_rejected_for_fragment_tag():
    try:
        derive_fragment_session_tag(
            FragmentSessionContext(
                session_hash="not-a-valid-hash",
                fragment_nonce="fragment-nonce",
                fragment_index_commitment="idx",
                fragment_role="primary",
                capsule_nonce="capsule-nonce",
            )
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for invalid session_hash")
