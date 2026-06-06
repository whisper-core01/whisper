"""
WHISPER v1.4.0 — Session Lifecycle FLV Record.

This module binds the full local lifecycle of a WHISPER session into a FLV-style
machine-bound dormant memory record.

Lifecycle structure:
- session_start_seal: local birth proof
- session_hash: validity boundary
- rotor_close_code: local death proof
- FLV binding: local machine/LUKS-bound dormant memory

Core invariants:
- FLV is not portable
- FLV does not store keys
- FLV does not store payload
- FLV does not store Reticulum identity
- FLV does not store routes
- FLV sleeps inside LUKS
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Literal

from rotor_close_code_v01 import CloseReason
from session_start_seal_v01 import OpenReason


LifecycleState = Literal[
    "OPENED",
    "ACTIVE",
    "CLOSING",
    "CLOSED",
    "DORMANT",
]

ReceiveMode = Literal[
    "BUFFERED",
    "STREAMING",
]


@dataclass(frozen=True)
class FLVMachineBindingContext:
    local_master_binding_hash: str
    machine_context_digest: str
    luks_context_digest: str


@dataclass(frozen=True)
class SessionLifecycleFLVRecord:
    session_hash: str
    session_start_seal: str
    rotor_close_code: str
    lifecycle_state: LifecycleState
    open_reason: OpenReason
    close_reason: CloseReason
    receive_mode: ReceiveMode
    created_at: int
    closed_at: int
    dormant: bool
    local_master_binding_hash: str
    machine_context_digest: str
    luks_context_digest: str
    flv_binding_digest: str
    record_digest: str


def stable_hash_hex(*parts: str) -> str:
    return hashlib.sha256("::".join(parts).encode("utf-8")).hexdigest()


def _require_non_empty(name: str, value: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")


def _require_hex_hash(name: str, value: str) -> None:
    _require_non_empty(name, value)

    if len(value) != 64:
        raise ValueError(f"{name} must be a 64-char hex hash")

    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be hex") from exc


def derive_local_master_binding_hash(
    master_key_hash: str,
    binding_nonce: str,
) -> str:
    """
    Derive a local FLV binding hash from master-key-derived material.

    This function must never receive or store the master key itself.
    """
    _require_hex_hash("master_key_hash", master_key_hash)
    _require_non_empty("binding_nonce", binding_nonce)

    return stable_hash_hex(
        master_key_hash,
        binding_nonce,
        "WHISPER_LOCAL_MASTER_FLV_BINDING_V1",
    )


def derive_machine_context_digest(
    machine_id_commitment: str,
    machine_nonce: str,
) -> str:
    """
    Derive a local machine context digest.

    This is not a portable identity.
    """
    _require_non_empty("machine_id_commitment", machine_id_commitment)
    _require_non_empty("machine_nonce", machine_nonce)

    return stable_hash_hex(
        machine_id_commitment,
        machine_nonce,
        "WHISPER_MACHINE_CONTEXT_DIGEST_V1",
    )


def derive_luks_context_digest(
    luks_volume_commitment: str,
    luks_nonce: str,
) -> str:
    """
    Derive a local LUKS context digest.

    This binds FLV validity to the local protected storage environment.
    """
    _require_non_empty("luks_volume_commitment", luks_volume_commitment)
    _require_non_empty("luks_nonce", luks_nonce)

    return stable_hash_hex(
        luks_volume_commitment,
        luks_nonce,
        "WHISPER_LUKS_CONTEXT_DIGEST_V1",
    )


def derive_flv_binding_digest(
    binding: FLVMachineBindingContext,
    session_hash: str,
    session_start_seal: str,
    rotor_close_code: str,
) -> str:
    """
    Bind the FLV lifecycle record to local protected machine context.

    This makes the FLV non-portable.
    """
    _require_hex_hash("local_master_binding_hash", binding.local_master_binding_hash)
    _require_hex_hash("machine_context_digest", binding.machine_context_digest)
    _require_hex_hash("luks_context_digest", binding.luks_context_digest)
    _require_hex_hash("session_hash", session_hash)
    _require_hex_hash("session_start_seal", session_start_seal)
    _require_hex_hash("rotor_close_code", rotor_close_code)

    return stable_hash_hex(
        binding.local_master_binding_hash,
        binding.machine_context_digest,
        binding.luks_context_digest,
        session_hash,
        session_start_seal,
        rotor_close_code,
        "WHISPER_FLV_MACHINE_BINDING_V1",
    )


def derive_lifecycle_record_digest(
    session_hash: str,
    session_start_seal: str,
    rotor_close_code: str,
    lifecycle_state: str,
    open_reason: str,
    close_reason: str,
    receive_mode: str,
    created_at: int,
    closed_at: int,
    dormant: bool,
    flv_binding_digest: str,
) -> str:
    _require_hex_hash("session_hash", session_hash)
    _require_hex_hash("session_start_seal", session_start_seal)
    _require_hex_hash("rotor_close_code", rotor_close_code)
    _require_hex_hash("flv_binding_digest", flv_binding_digest)

    if created_at < 0:
        raise ValueError("created_at must be >= 0")

    if closed_at < created_at:
        raise ValueError("closed_at must be >= created_at")

    return stable_hash_hex(
        session_hash,
        session_start_seal,
        rotor_close_code,
        lifecycle_state,
        open_reason,
        close_reason,
        receive_mode,
        str(created_at),
        str(closed_at),
        str(dormant),
        flv_binding_digest,
        "WHISPER_SESSION_LIFECYCLE_FLV_RECORD_V1",
    )


def build_session_lifecycle_flv_record(
    session_hash: str,
    session_start_seal: str,
    rotor_close_code: str,
    lifecycle_state: LifecycleState,
    open_reason: OpenReason,
    close_reason: CloseReason,
    receive_mode: ReceiveMode,
    created_at: int,
    closed_at: int,
    dormant: bool,
    binding: FLVMachineBindingContext,
) -> SessionLifecycleFLVRecord:
    """
    Build a full lifecycle FLV record.

    A DORMANT record requires:
    - session birth seal
    - session hash
    - rotor close code
    - local machine/LUKS binding
    - dormant=True
    """
    _require_hex_hash("session_hash", session_hash)
    _require_hex_hash("session_start_seal", session_start_seal)
    _require_hex_hash("rotor_close_code", rotor_close_code)

    if lifecycle_state not in {"OPENED", "ACTIVE", "CLOSING", "CLOSED", "DORMANT"}:
        raise ValueError("unsupported lifecycle_state")

    if receive_mode not in {"BUFFERED", "STREAMING"}:
        raise ValueError("unsupported receive_mode")

    if created_at < 0:
        raise ValueError("created_at must be >= 0")

    if closed_at < created_at:
        raise ValueError("closed_at must be >= created_at")

    if lifecycle_state == "DORMANT" and not dormant:
        raise ValueError("DORMANT lifecycle_state requires dormant=True")

    flv_binding_digest = derive_flv_binding_digest(
        binding=binding,
        session_hash=session_hash,
        session_start_seal=session_start_seal,
        rotor_close_code=rotor_close_code,
    )

    record_digest = derive_lifecycle_record_digest(
        session_hash=session_hash,
        session_start_seal=session_start_seal,
        rotor_close_code=rotor_close_code,
        lifecycle_state=lifecycle_state,
        open_reason=open_reason,
        close_reason=close_reason,
        receive_mode=receive_mode,
        created_at=created_at,
        closed_at=closed_at,
        dormant=dormant,
        flv_binding_digest=flv_binding_digest,
    )

    return SessionLifecycleFLVRecord(
        session_hash=session_hash,
        session_start_seal=session_start_seal,
        rotor_close_code=rotor_close_code,
        lifecycle_state=lifecycle_state,
        open_reason=open_reason,
        close_reason=close_reason,
        receive_mode=receive_mode,
        created_at=created_at,
        closed_at=closed_at,
        dormant=dormant,
        local_master_binding_hash=binding.local_master_binding_hash,
        machine_context_digest=binding.machine_context_digest,
        luks_context_digest=binding.luks_context_digest,
        flv_binding_digest=flv_binding_digest,
        record_digest=record_digest,
    )


def validate_session_lifecycle_flv_record(record: SessionLifecycleFLVRecord) -> bool:
    binding = FLVMachineBindingContext(
        local_master_binding_hash=record.local_master_binding_hash,
        machine_context_digest=record.machine_context_digest,
        luks_context_digest=record.luks_context_digest,
    )

    expected_binding = derive_flv_binding_digest(
        binding=binding,
        session_hash=record.session_hash,
        session_start_seal=record.session_start_seal,
        rotor_close_code=record.rotor_close_code,
    )

    if not hmac.compare_digest(expected_binding, record.flv_binding_digest):
        return False

    expected_record = derive_lifecycle_record_digest(
        session_hash=record.session_hash,
        session_start_seal=record.session_start_seal,
        rotor_close_code=record.rotor_close_code,
        lifecycle_state=record.lifecycle_state,
        open_reason=record.open_reason,
        close_reason=record.close_reason,
        receive_mode=record.receive_mode,
        created_at=record.created_at,
        closed_at=record.closed_at,
        dormant=record.dormant,
        flv_binding_digest=record.flv_binding_digest,
    )

    return hmac.compare_digest(expected_record, record.record_digest)


def lifecycle_record_to_public_summary(record: SessionLifecycleFLVRecord) -> dict:
    """
    Export a safe lifecycle summary.

    Does not expose full hashes or binding material.
    """
    return {
        "session_hash_prefix": record.session_hash[:16],
        "session_start_seal_prefix": record.session_start_seal[:16],
        "rotor_close_code_prefix": record.rotor_close_code[:16],
        "lifecycle_state": record.lifecycle_state,
        "open_reason": record.open_reason,
        "close_reason": record.close_reason,
        "receive_mode": record.receive_mode,
        "created_at": record.created_at,
        "closed_at": record.closed_at,
        "dormant": record.dormant,
        "record_digest_prefix": record.record_digest[:16],
    }


if __name__ == "__main__":
    from session_hash_v01 import SessionContext, derive_session_hash
    from session_start_seal_v01 import (
        SessionStartContext,
        derive_session_start_seal,
        derive_start_step_digest,
    )
    from secure_session_shutdown_v01 import create_runtime_state, secure_shutdown_session
    from session_revocation_v01 import SessionRevocationStore

    ctx = SessionContext(
        sol_id="sol-demo",
        epoch="1",
        local_ephemeral_material="local",
        remote_ephemeral_material="remote",
        session_nonce="session-nonce",
        message_commitment="message",
        transfer_profile_commitment="profile",
    )

    session_hash = derive_session_hash(ctx)

    start_seal = derive_session_start_seal(
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

    runtime = create_runtime_state(ctx)
    store = SessionRevocationStore()

    shutdown = secure_shutdown_session(
        runtime=runtime,
        store=store,
        close_reason="USER_LEFT_SESSION",
        revocation_reason="USER_LEFT_SESSION",
        shutdown_nonce="shutdown",
        key_epoch="epoch-1",
        destruction_nonce="destroy",
        closed_at=123,
    )

    master_key_hash = stable_hash_hex("local-master-key-derived-material")
    binding = FLVMachineBindingContext(
        local_master_binding_hash=derive_local_master_binding_hash(master_key_hash, "binding"),
        machine_context_digest=derive_machine_context_digest("machine", "machine-nonce"),
        luks_context_digest=derive_luks_context_digest("luks", "luks-nonce"),
    )

    record = build_session_lifecycle_flv_record(
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
        binding=binding,
    )

    print("Lifecycle FLV valid:", validate_session_lifecycle_flv_record(record))
    print("Lifecycle state:", record.lifecycle_state)
    print("Dormant:", record.dormant)
