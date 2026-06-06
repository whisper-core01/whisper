from session_lifecycle_flv_v01 import (
    FLVMachineBindingContext,
    build_session_lifecycle_flv_record,
    derive_flv_binding_digest,
    derive_lifecycle_record_digest,
    derive_local_master_binding_hash,
    derive_luks_context_digest,
    derive_machine_context_digest,
    lifecycle_record_to_public_summary,
    stable_hash_hex,
    validate_session_lifecycle_flv_record,
)
from session_hash_v01 import SessionContext, derive_session_hash
from session_start_seal_v01 import (
    SessionStartContext,
    derive_session_start_seal,
    derive_start_step_digest,
)
from secure_session_shutdown_v01 import create_runtime_state, secure_shutdown_session
from session_revocation_v01 import SessionRevocationStore


def _ctx():
    return SessionContext(
        sol_id="sol",
        epoch="1",
        local_ephemeral_material="local",
        remote_ephemeral_material="remote",
        session_nonce="session-nonce",
        message_commitment="message",
        transfer_profile_commitment="profile",
    )


def _session_hash():
    return derive_session_hash(_ctx())


def _start_seal(session_hash):
    ctx = _ctx()

    return derive_session_start_seal(
        SessionStartContext(
            session_hash=session_hash,
            session_nonce=ctx.session_nonce,
            start_nonce="start",
            open_reason="USER_STARTED_SESSION",
            wasm_init_digest=derive_start_step_digest(session_hash, "WASM_INITIALIZED", "wasm"),
            custody_init_digest=derive_start_step_digest(session_hash, "CUSTODY_EMPTY", "custody"),
            volatile_init_digest=derive_start_step_digest(session_hash, "VOLATILE_BUFFERS_EMPTY", "volatile"),
            created_at=1,
        )
    )


def _shutdown():
    runtime = create_runtime_state(_ctx())
    store = SessionRevocationStore()

    return secure_shutdown_session(
        runtime=runtime,
        store=store,
        close_reason="USER_LEFT_SESSION",
        revocation_reason="USER_LEFT_SESSION",
        shutdown_nonce="shutdown",
        key_epoch="epoch-1",
        destruction_nonce="destroy",
        closed_at=123,
    )


def _binding(seed="a"):
    master_hash = stable_hash_hex("local-master", seed)

    return FLVMachineBindingContext(
        local_master_binding_hash=derive_local_master_binding_hash(master_hash, "binding"),
        machine_context_digest=derive_machine_context_digest("machine", "machine-nonce"),
        luks_context_digest=derive_luks_context_digest("luks", "luks-nonce"),
    )


def _record(binding_seed="a"):
    session_hash = _session_hash()
    start_seal = _start_seal(session_hash)
    shutdown = _shutdown()

    return build_session_lifecycle_flv_record(
        session_hash=session_hash,
        session_start_seal=start_seal,
        rotor_close_code=shutdown.rotor_close_code,
        lifecycle_state="DORMANT",
        open_reason="USER_STARTED_SESSION",
        close_reason="USER_LEFT_SESSION",
        receive_mode="BUFFERED",
        created_at=1,
        closed_at=123,
        dormant=True,
        binding=_binding(binding_seed),
    )


def test_local_master_binding_is_deterministic():
    master_hash = stable_hash_hex("local-master")

    a = derive_local_master_binding_hash(master_hash, "nonce")
    b = derive_local_master_binding_hash(master_hash, "nonce")

    assert a == b
    assert len(a) == 64


def test_local_master_binding_changes_with_nonce():
    master_hash = stable_hash_hex("local-master")

    a = derive_local_master_binding_hash(master_hash, "nonce-a")
    b = derive_local_master_binding_hash(master_hash, "nonce-b")

    assert a != b


def test_flv_binding_changes_with_machine_context():
    session_hash = _session_hash()
    start_seal = _start_seal(session_hash)
    close_code = _shutdown().rotor_close_code

    a = derive_flv_binding_digest(
        _binding("a"),
        session_hash,
        start_seal,
        close_code,
    )

    b = derive_flv_binding_digest(
        _binding("b"),
        session_hash,
        start_seal,
        close_code,
    )

    assert a != b


def test_build_lifecycle_flv_record_valid():
    record = _record()

    assert record.lifecycle_state == "DORMANT"
    assert record.dormant is True
    assert len(record.flv_binding_digest) == 64
    assert len(record.record_digest) == 64
    assert validate_session_lifecycle_flv_record(record) is True


def test_dormant_state_requires_dormant_true():
    session_hash = _session_hash()
    start_seal = _start_seal(session_hash)
    shutdown = _shutdown()

    try:
        build_session_lifecycle_flv_record(
            session_hash=session_hash,
            session_start_seal=start_seal,
            rotor_close_code=shutdown.rotor_close_code,
            lifecycle_state="DORMANT",
            open_reason="USER_STARTED_SESSION",
            close_reason="USER_LEFT_SESSION",
            receive_mode="BUFFERED",
            created_at=1,
            closed_at=123,
            dormant=False,
            binding=_binding(),
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for DORMANT with dormant=False")


def test_invalid_receive_mode_rejected():
    session_hash = _session_hash()
    start_seal = _start_seal(session_hash)
    shutdown = _shutdown()

    try:
        build_session_lifecycle_flv_record(
            session_hash=session_hash,
            session_start_seal=start_seal,
            rotor_close_code=shutdown.rotor_close_code,
            lifecycle_state="DORMANT",
            open_reason="USER_STARTED_SESSION",
            close_reason="USER_LEFT_SESSION",
            receive_mode="BAD_MODE",  # type: ignore[arg-type]
            created_at=1,
            closed_at=123,
            dormant=True,
            binding=_binding(),
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for invalid receive_mode")


def test_closed_at_before_created_at_rejected():
    session_hash = _session_hash()
    start_seal = _start_seal(session_hash)
    shutdown = _shutdown()

    try:
        build_session_lifecycle_flv_record(
            session_hash=session_hash,
            session_start_seal=start_seal,
            rotor_close_code=shutdown.rotor_close_code,
            lifecycle_state="DORMANT",
            open_reason="USER_STARTED_SESSION",
            close_reason="USER_LEFT_SESSION",
            receive_mode="BUFFERED",
            created_at=10,
            closed_at=1,
            dormant=True,
            binding=_binding(),
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for closed_at < created_at")


def test_validate_lifecycle_flv_detects_tamper():
    record = _record()

    tampered = type(record)(
        session_hash=record.session_hash,
        session_start_seal=record.session_start_seal,
        rotor_close_code=record.rotor_close_code,
        lifecycle_state=record.lifecycle_state,
        open_reason=record.open_reason,
        close_reason=record.close_reason,
        receive_mode=record.receive_mode,
        created_at=record.created_at,
        closed_at=record.closed_at + 1,
        dormant=record.dormant,
        local_master_binding_hash=record.local_master_binding_hash,
        machine_context_digest=record.machine_context_digest,
        luks_context_digest=record.luks_context_digest,
        flv_binding_digest=record.flv_binding_digest,
        record_digest=record.record_digest,
    )

    assert validate_session_lifecycle_flv_record(tampered) is False


def test_public_summary_does_not_expose_full_binding_hashes():
    record = _record()
    summary = lifecycle_record_to_public_summary(record)

    assert summary["lifecycle_state"] == "DORMANT"
    assert summary["dormant"] is True
    assert len(summary["session_hash_prefix"]) == 16
    assert len(summary["session_start_seal_prefix"]) == 16
    assert len(summary["rotor_close_code_prefix"]) == 16
    assert "local_master_binding_hash" not in summary
    assert "machine_context_digest" not in summary
    assert "luks_context_digest" not in summary
    assert "flv_binding_digest" not in summary


def test_record_digest_changes_with_dormancy():
    record = _record()

    digest_a = derive_lifecycle_record_digest(
        session_hash=record.session_hash,
        session_start_seal=record.session_start_seal,
        rotor_close_code=record.rotor_close_code,
        lifecycle_state=record.lifecycle_state,
        open_reason=record.open_reason,
        close_reason=record.close_reason,
        receive_mode=record.receive_mode,
        created_at=record.created_at,
        closed_at=record.closed_at,
        dormant=True,
        flv_binding_digest=record.flv_binding_digest,
    )

    digest_b = derive_lifecycle_record_digest(
        session_hash=record.session_hash,
        session_start_seal=record.session_start_seal,
        rotor_close_code=record.rotor_close_code,
        lifecycle_state=record.lifecycle_state,
        open_reason=record.open_reason,
        close_reason=record.close_reason,
        receive_mode=record.receive_mode,
        created_at=record.created_at,
        closed_at=record.closed_at,
        dormant=False,
        flv_binding_digest=record.flv_binding_digest,
    )

    assert digest_a != digest_b
