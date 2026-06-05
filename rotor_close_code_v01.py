"""
WHISPER v1.4.0 — Rotor Close Code.

A rotor close code is a local closure seal.

It is generated during secure session shutdown, before session-bound keys are destroyed.

It is not:
- a recovery key
- a session key
- a fragment key
- a repair key
- a Reticulum identity
- a route identity
- a payload commitment

It proves locally that shutdown occurred.

It must not contain, preserve, derive, or restore destroyed keys.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Literal


CloseReason = Literal[
    "USER_LEFT_SESSION",
    "USER_CANCELLED_TRANSFER",
    "LOCAL_SESSION_CLOSED",
    "SESSION_EXPIRED",
    "POLICY_CLOSE",
    "INVALID_MATERIAL",
    "STORAGE_PRESSURE",
]


@dataclass(frozen=True)
class RotorCloseContext:
    session_hash: str
    shutdown_nonce: str
    close_reason: CloseReason
    wasm_purge_digest: str
    volatile_zeroize_digest: str
    custody_freeze_digest: str
    key_destruction_commitment: str
    closed_at: int


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


VALID_CLOSE_REASONS = {
    "USER_LEFT_SESSION",
    "USER_CANCELLED_TRANSFER",
    "LOCAL_SESSION_CLOSED",
    "SESSION_EXPIRED",
    "POLICY_CLOSE",
    "INVALID_MATERIAL",
    "STORAGE_PRESSURE",
}


def derive_shutdown_step_digest(
    session_hash: str,
    step_name: str,
    step_nonce: str,
    step_status: str = "OK",
) -> str:
    """
    Derive a local digest for a shutdown step.

    This is a commitment to the fact that a local step occurred.
    It must not contain memory, keys, payload, fragments, routes, or transport identities.
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
        "WHISPER_SHUTDOWN_STEP_DIGEST_V1",
    )


def derive_key_destruction_commitment(
    session_hash: str,
    key_epoch: str,
    destruction_nonce: str,
) -> str:
    """
    Commit to key destruction without preserving the key.

    This function must never receive the key itself.
    """
    _require_hex_hash("session_hash", session_hash)
    _require_non_empty("key_epoch", key_epoch)
    _require_non_empty("destruction_nonce", destruction_nonce)

    return stable_hash_hex(
        session_hash,
        key_epoch,
        destruction_nonce,
        "KEYS_DESTROYED",
        "WHISPER_KEY_DESTRUCTION_COMMITMENT_V1",
    )


def derive_rotor_close_code(ctx: RotorCloseContext) -> str:
    """
    Derive the local rotor close code.

    The close code is generated before final session key destruction, but it must not
    contain or preserve any key material.
    """
    _require_hex_hash("session_hash", ctx.session_hash)
    _require_non_empty("shutdown_nonce", ctx.shutdown_nonce)

    if ctx.close_reason not in VALID_CLOSE_REASONS:
        raise ValueError(f"unsupported close_reason: {ctx.close_reason}")

    _require_hex_hash("wasm_purge_digest", ctx.wasm_purge_digest)
    _require_hex_hash("volatile_zeroize_digest", ctx.volatile_zeroize_digest)
    _require_hex_hash("custody_freeze_digest", ctx.custody_freeze_digest)
    _require_hex_hash("key_destruction_commitment", ctx.key_destruction_commitment)

    if ctx.closed_at < 0:
        raise ValueError("closed_at must be >= 0")

    return stable_hash_hex(
        ctx.session_hash,
        ctx.shutdown_nonce,
        ctx.close_reason,
        ctx.wasm_purge_digest,
        ctx.volatile_zeroize_digest,
        ctx.custody_freeze_digest,
        ctx.key_destruction_commitment,
        str(ctx.closed_at),
        "WHISPER_ROTOR_CLOSE_CODE_V1",
    )


def validate_rotor_close_code(expected_code: str, observed_code: str) -> bool:
    _require_non_empty("expected_code", expected_code)
    _require_non_empty("observed_code", observed_code)

    return hmac.compare_digest(expected_code, observed_code)


if __name__ == "__main__":
    from session_hash_v01 import SessionContext, derive_session_hash

    session_hash = derive_session_hash(
        SessionContext(
            sol_id="sol-demo",
            epoch="1",
            local_ephemeral_material="local",
            remote_ephemeral_material="remote",
            session_nonce="nonce",
            message_commitment="message",
            transfer_profile_commitment="profile",
        )
    )

    wasm = derive_shutdown_step_digest(session_hash, "WASM_PURGE", "wasm-nonce")
    zeroize = derive_shutdown_step_digest(session_hash, "VOLATILE_ZEROIZE", "zeroize-nonce")
    custody = derive_shutdown_step_digest(session_hash, "CUSTODY_FREEZE", "custody-nonce")
    key_destroy = derive_key_destruction_commitment(session_hash, "epoch-1", "destroy-nonce")

    close_code = derive_rotor_close_code(
        RotorCloseContext(
            session_hash=session_hash,
            shutdown_nonce="shutdown-nonce",
            close_reason="USER_LEFT_SESSION",
            wasm_purge_digest=wasm,
            volatile_zeroize_digest=zeroize,
            custody_freeze_digest=custody,
            key_destruction_commitment=key_destroy,
            closed_at=123,
        )
    )

    print("Rotor close code:", close_code[:16])
    print("Valid close code:", validate_rotor_close_code(close_code, close_code))
