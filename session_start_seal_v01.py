"""
WHISPER v1.4.0 — Session Start Seal.

A session start seal is a local opening seal.

It proves locally that a session was opened cleanly.

It is not:
- a session key
- a fragment key
- a repair key
- a Reticulum identity
- a route identity
- a payload commitment
- a stable identifier

It must not derive, preserve, expose, or recover any key.

Logical structure:
- session_start_seal: act of birth
- session_hash: validity boundary
- rotor_close_code: act of death
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Literal


OpenReason = Literal[
    "USER_STARTED_SESSION",
    "TRANSFER_REQUESTED",
    "RECEIVE_REQUEST_ACCEPTED",
    "STREAMING_SESSION_STARTED",
    "BUFFERED_SESSION_STARTED",
    "LOCAL_POLICY_START",
]


@dataclass(frozen=True)
class SessionStartContext:
    session_hash: str
    session_nonce: str
    start_nonce: str
    open_reason: OpenReason
    wasm_init_digest: str
    custody_init_digest: str
    volatile_init_digest: str
    created_at: int


VALID_OPEN_REASONS = {
    "USER_STARTED_SESSION",
    "TRANSFER_REQUESTED",
    "RECEIVE_REQUEST_ACCEPTED",
    "STREAMING_SESSION_STARTED",
    "BUFFERED_SESSION_STARTED",
    "LOCAL_POLICY_START",
}


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


def derive_start_step_digest(
    session_hash: str,
    step_name: str,
    step_nonce: str,
    step_status: str = "OK",
) -> str:
    """
    Commit to a local session initialization step.

    This digest must not contain keys, payload, route, Reticulum identity,
    or fragment material.
    """
    _require_hex_hash("session_hash", session_hash)
    _require_non_empty("step_name", step_name)
    _require_non_empty("step_nonce", step_nonce)
    _require_non_empty("step_status", step_status)

    return stable_hash_hex(
        session_hash,
        step_name,
        step_nonce,
        step_status,
        "WHISPER_SESSION_START_STEP_DIGEST_V1",
    )


def derive_session_start_seal(ctx: SessionStartContext) -> str:
    """
    Derive the local session start seal.

    The start seal proves that the session opened cleanly under a local context.

    It is not a key and cannot be used to derive any key.
    """
    _require_hex_hash("session_hash", ctx.session_hash)
    _require_non_empty("session_nonce", ctx.session_nonce)
    _require_non_empty("start_nonce", ctx.start_nonce)

    if ctx.open_reason not in VALID_OPEN_REASONS:
        raise ValueError(f"unsupported open_reason: {ctx.open_reason}")

    _require_hex_hash("wasm_init_digest", ctx.wasm_init_digest)
    _require_hex_hash("custody_init_digest", ctx.custody_init_digest)
    _require_hex_hash("volatile_init_digest", ctx.volatile_init_digest)

    if ctx.created_at < 0:
        raise ValueError("created_at must be >= 0")

    return stable_hash_hex(
        ctx.session_hash,
        ctx.session_nonce,
        ctx.start_nonce,
        ctx.open_reason,
        ctx.wasm_init_digest,
        ctx.custody_init_digest,
        ctx.volatile_init_digest,
        str(ctx.created_at),
        "WHISPER_SESSION_START_SEAL_V1",
    )


def validate_session_start_seal(expected_seal: str, observed_seal: str) -> bool:
    """
    Constant-time validation for a start seal.
    """
    _require_non_empty("expected_seal", expected_seal)
    _require_non_empty("observed_seal", observed_seal)

    return hmac.compare_digest(expected_seal, observed_seal)


if __name__ == "__main__":
    from session_hash_v01 import SessionContext, derive_session_hash

    session_ctx = SessionContext(
        sol_id="sol-demo",
        epoch="1",
        local_ephemeral_material="local",
        remote_ephemeral_material="remote",
        session_nonce="session-nonce",
        message_commitment="message",
        transfer_profile_commitment="profile",
    )

    session_hash = derive_session_hash(session_ctx)

    wasm = derive_start_step_digest(session_hash, "WASM_INITIALIZED", "wasm-nonce")
    custody = derive_start_step_digest(session_hash, "CUSTODY_EMPTY", "custody-nonce")
    volatile = derive_start_step_digest(session_hash, "VOLATILE_BUFFERS_EMPTY", "volatile-nonce")

    start_seal = derive_session_start_seal(
        SessionStartContext(
            session_hash=session_hash,
            session_nonce=session_ctx.session_nonce,
            start_nonce="start-nonce",
            open_reason="USER_STARTED_SESSION",
            wasm_init_digest=wasm,
            custody_init_digest=custody,
            volatile_init_digest=volatile,
            created_at=1,
        )
    )

    print("Session start seal:", start_seal[:16])
    print("Valid start seal:", validate_session_start_seal(start_seal, start_seal))
