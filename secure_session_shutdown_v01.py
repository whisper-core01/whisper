"""
WHISPER v1.4.0 — Secure Session Shutdown.

This module orchestrates the secure local death of a WHISPER session.

It combines:
- shutdown step digests
- rotor close code
- key destruction commitment
- local session revocation

Core invariant:
A session cannot close before active state is purged, keys are destroyed,
and the session hash is locally revoked.

No persistent keys.
No session resurrection.
No replay after close.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal

from rotor_close_code_v01 import (
    CloseReason,
    RotorCloseContext,
    derive_key_destruction_commitment,
    derive_rotor_close_code,
    derive_shutdown_step_digest,
)
from session_hash_v01 import SessionContext, derive_session_hash
from session_revocation_v01 import (
    RevocationReason,
    SessionRevocationStore,
    is_session_revoked,
    mark_session_revoked,
)


SessionState = Literal[
    "ACTIVE",
    "CLOSING",
    "WASM_PURGED",
    "ZEROIZED",
    "ROTOR_CLOSED",
    "KEYS_DESTROYED",
    "REVOKED",
    "CLOSED",
]

ShutdownStep = Literal[
    "BLOCK_NEW_MATERIAL",
    "FREEZE_CUSTODY",
    "PURGE_WASM",
    "ZEROIZE_VOLATILE",
    "GENERATE_ROTOR_CLOSE",
    "DESTROY_KEYS",
    "REVOKE_SESSION",
    "CLOSE_SESSION",
]


@dataclass
class SessionRuntimeState:
    session_hash: str
    state: SessionState = "ACTIVE"
    accepts_new_material: bool = True
    custody_frozen: bool = False
    wasm_purged: bool = False
    volatile_zeroized: bool = False
    keys_destroyed: bool = False
    rotor_close_code: str | None = None
    shutdown_steps: List[ShutdownStep] = field(default_factory=list)
    shutdown_digests: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ShutdownResult:
    session_hash: str
    final_state: SessionState
    rotor_close_code: str
    revoked: bool
    keys_destroyed: bool
    wasm_purged: bool
    volatile_zeroized: bool
    custody_frozen: bool
    accepts_new_material: bool
    shutdown_steps: List[ShutdownStep]


def _require_session_hash(session_hash: str) -> None:
    if not isinstance(session_hash, str) or len(session_hash) != 64:
        raise ValueError("session_hash must be a 64-char hex hash")

    try:
        int(session_hash, 16)
    except ValueError as exc:
        raise ValueError("session_hash must be hex") from exc


def create_runtime_state(session_ctx: SessionContext) -> SessionRuntimeState:
    return SessionRuntimeState(
        session_hash=derive_session_hash(session_ctx),
    )


def _record_step(
    runtime: SessionRuntimeState,
    step: ShutdownStep,
    step_nonce: str,
    step_status: str = "OK",
) -> str:
    digest = derive_shutdown_step_digest(
        session_hash=runtime.session_hash,
        step_name=step,
        step_nonce=step_nonce,
        step_status=step_status,
    )
    runtime.shutdown_steps.append(step)
    runtime.shutdown_digests[step] = digest
    return digest


def block_new_material(runtime: SessionRuntimeState, step_nonce: str) -> None:
    _require_session_hash(runtime.session_hash)

    if runtime.state != "ACTIVE":
        raise ValueError("session must be ACTIVE to block new material")

    runtime.accepts_new_material = False
    runtime.state = "CLOSING"
    _record_step(runtime, "BLOCK_NEW_MATERIAL", step_nonce)


def freeze_custody(runtime: SessionRuntimeState, step_nonce: str) -> None:
    if runtime.state != "CLOSING":
        raise ValueError("session must be CLOSING to freeze custody")

    runtime.custody_frozen = True
    _record_step(runtime, "FREEZE_CUSTODY", step_nonce)


def purge_wasm(runtime: SessionRuntimeState, step_nonce: str) -> None:
    if runtime.state != "CLOSING":
        raise ValueError("session must be CLOSING to purge Wasm")

    if not runtime.custody_frozen:
        raise ValueError("custody must be frozen before Wasm purge")

    runtime.wasm_purged = True
    runtime.state = "WASM_PURGED"
    _record_step(runtime, "PURGE_WASM", step_nonce)


def zeroize_volatile(runtime: SessionRuntimeState, step_nonce: str) -> None:
    if runtime.state != "WASM_PURGED":
        raise ValueError("Wasm must be purged before volatile zeroization")

    runtime.volatile_zeroized = True
    runtime.state = "ZEROIZED"
    _record_step(runtime, "ZEROIZE_VOLATILE", step_nonce)


def generate_rotor_close(
    runtime: SessionRuntimeState,
    shutdown_nonce: str,
    close_reason: CloseReason,
    key_epoch: str,
    destruction_nonce: str,
    closed_at: int,
) -> str:
    if runtime.state != "ZEROIZED":
        raise ValueError("volatile state must be zeroized before rotor close code")

    wasm_digest = runtime.shutdown_digests.get("PURGE_WASM")
    zeroize_digest = runtime.shutdown_digests.get("ZEROIZE_VOLATILE")
    custody_digest = runtime.shutdown_digests.get("FREEZE_CUSTODY")

    if wasm_digest is None or zeroize_digest is None or custody_digest is None:
        raise ValueError("missing shutdown step digests")

    key_commitment = derive_key_destruction_commitment(
        session_hash=runtime.session_hash,
        key_epoch=key_epoch,
        destruction_nonce=destruction_nonce,
    )

    close_code = derive_rotor_close_code(
        RotorCloseContext(
            session_hash=runtime.session_hash,
            shutdown_nonce=shutdown_nonce,
            close_reason=close_reason,
            wasm_purge_digest=wasm_digest,
            volatile_zeroize_digest=zeroize_digest,
            custody_freeze_digest=custody_digest,
            key_destruction_commitment=key_commitment,
            closed_at=closed_at,
        )
    )

    runtime.rotor_close_code = close_code
    runtime.state = "ROTOR_CLOSED"
    runtime.shutdown_steps.append("GENERATE_ROTOR_CLOSE")
    runtime.shutdown_digests["GENERATE_ROTOR_CLOSE"] = close_code

    return close_code


def destroy_keys(runtime: SessionRuntimeState, step_nonce: str) -> None:
    if runtime.state != "ROTOR_CLOSED":
        raise ValueError("rotor close code must be generated before key destruction")

    runtime.keys_destroyed = True
    runtime.state = "KEYS_DESTROYED"
    _record_step(runtime, "DESTROY_KEYS", step_nonce)


def revoke_closed_session(
    runtime: SessionRuntimeState,
    store: SessionRevocationStore,
    reason: RevocationReason,
    created_at: int,
) -> None:
    if runtime.state != "KEYS_DESTROYED":
        raise ValueError("keys must be destroyed before revocation")

    mark_session_revoked(
        store=store,
        session_hash=runtime.session_hash,
        reason=reason,
        scope="SESSION",
        created_at=created_at,
    )

    runtime.state = "REVOKED"
    runtime.shutdown_steps.append("REVOKE_SESSION")


def close_session(runtime: SessionRuntimeState) -> None:
    if runtime.state != "REVOKED":
        raise ValueError("session must be revoked before close")

    if not runtime.keys_destroyed:
        raise ValueError("keys must be destroyed before close")

    if runtime.rotor_close_code is None:
        raise ValueError("rotor close code must exist before close")

    runtime.state = "CLOSED"
    runtime.shutdown_steps.append("CLOSE_SESSION")


def secure_shutdown_session(
    runtime: SessionRuntimeState,
    store: SessionRevocationStore,
    close_reason: CloseReason,
    revocation_reason: RevocationReason,
    shutdown_nonce: str,
    key_epoch: str,
    destruction_nonce: str,
    closed_at: int,
) -> ShutdownResult:
    """
    Execute the complete local shutdown sequence.
    """
    block_new_material(runtime, f"{shutdown_nonce}:block")
    freeze_custody(runtime, f"{shutdown_nonce}:custody")
    purge_wasm(runtime, f"{shutdown_nonce}:wasm")
    zeroize_volatile(runtime, f"{shutdown_nonce}:zeroize")

    close_code = generate_rotor_close(
        runtime=runtime,
        shutdown_nonce=shutdown_nonce,
        close_reason=close_reason,
        key_epoch=key_epoch,
        destruction_nonce=destruction_nonce,
        closed_at=closed_at,
    )

    destroy_keys(runtime, f"{shutdown_nonce}:keys")

    revoke_closed_session(
        runtime=runtime,
        store=store,
        reason=revocation_reason,
        created_at=closed_at,
    )

    close_session(runtime)

    return ShutdownResult(
        session_hash=runtime.session_hash,
        final_state=runtime.state,
        rotor_close_code=close_code,
        revoked=is_session_revoked(store, runtime.session_hash, now=closed_at),
        keys_destroyed=runtime.keys_destroyed,
        wasm_purged=runtime.wasm_purged,
        volatile_zeroized=runtime.volatile_zeroized,
        custody_frozen=runtime.custody_frozen,
        accepts_new_material=runtime.accepts_new_material,
        shutdown_steps=list(runtime.shutdown_steps),
    )


if __name__ == "__main__":
    ctx = SessionContext(
        sol_id="sol-demo",
        epoch="1",
        local_ephemeral_material="local",
        remote_ephemeral_material="remote",
        session_nonce="nonce",
        message_commitment="message",
        transfer_profile_commitment="profile",
    )

    runtime = create_runtime_state(ctx)
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

    print("Final state:", result.final_state)
    print("Revoked:", result.revoked)
    print("Keys destroyed:", result.keys_destroyed)
    print("Rotor close:", result.rotor_close_code[:16])
