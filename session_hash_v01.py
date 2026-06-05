"""
WHISPER v1.4.0 — Session Hash.

Minimal session-scoped validity boundary.

This module implements:
- derive_session_hash()
- derive_fragment_session_tag()
- derive_capsule_session_tag()
- derive_repair_hash()
- validate_session_tag()

Core invariant:
No valid session hash.
No valid fragment.
No valid capsule.
No valid repair.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Literal


FragmentRole = Literal["primary", "recovery", "repair", "decoy"]


@dataclass(frozen=True)
class SessionContext:
    sol_id: str
    epoch: str
    local_ephemeral_material: str
    remote_ephemeral_material: str
    session_nonce: str
    message_commitment: str
    transfer_profile_commitment: str


@dataclass(frozen=True)
class FragmentSessionContext:
    session_hash: str
    fragment_nonce: str
    fragment_index_commitment: str
    fragment_role: FragmentRole
    capsule_nonce: str


@dataclass(frozen=True)
class CapsuleSessionContext:
    session_hash: str
    capsule_nonce: str
    capsule_role: str
    capsule_epoch: str


@dataclass(frozen=True)
class RepairSessionContext:
    session_hash: str
    repair_epoch: str
    repair_nonce: str
    repair_counter: int


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


def derive_session_hash(ctx: SessionContext) -> str:
    """
    Derive an epoch-scoped session validity boundary.

    This is not:
    - a node identity
    - a route identity
    - a Reticulum address
    - a stable user identifier
    """
    for name, value in [
        ("sol_id", ctx.sol_id),
        ("epoch", ctx.epoch),
        ("local_ephemeral_material", ctx.local_ephemeral_material),
        ("remote_ephemeral_material", ctx.remote_ephemeral_material),
        ("session_nonce", ctx.session_nonce),
        ("message_commitment", ctx.message_commitment),
        ("transfer_profile_commitment", ctx.transfer_profile_commitment),
    ]:
        _require_non_empty(name, value)

    return stable_hash_hex(
        ctx.sol_id,
        ctx.epoch,
        ctx.local_ephemeral_material,
        ctx.remote_ephemeral_material,
        ctx.session_nonce,
        ctx.message_commitment,
        ctx.transfer_profile_commitment,
        "WHISPER_SESSION_HASH_V1",
    )


def derive_fragment_session_tag(ctx: FragmentSessionContext) -> str:
    """
    Bind a fragment to a session.

    A tag mismatch means the fragment is invalid for that session.
    """
    _require_hex_hash("session_hash", ctx.session_hash)

    for name, value in [
        ("fragment_nonce", ctx.fragment_nonce),
        ("fragment_index_commitment", ctx.fragment_index_commitment),
        ("fragment_role", ctx.fragment_role),
        ("capsule_nonce", ctx.capsule_nonce),
    ]:
        _require_non_empty(name, value)

    if ctx.fragment_role not in {"primary", "recovery", "repair", "decoy"}:
        raise ValueError("fragment_role must be primary, recovery, repair, or decoy")

    return stable_hash_hex(
        ctx.session_hash,
        ctx.fragment_nonce,
        ctx.fragment_index_commitment,
        ctx.fragment_role,
        ctx.capsule_nonce,
        "WHISPER_FRAGMENT_SESSION_TAG_V1",
    )


def derive_capsule_session_tag(ctx: CapsuleSessionContext) -> str:
    """
    Bind a capsule to a session and epoch.
    """
    _require_hex_hash("session_hash", ctx.session_hash)

    for name, value in [
        ("capsule_nonce", ctx.capsule_nonce),
        ("capsule_role", ctx.capsule_role),
        ("capsule_epoch", ctx.capsule_epoch),
    ]:
        _require_non_empty(name, value)

    return stable_hash_hex(
        ctx.session_hash,
        ctx.capsule_nonce,
        ctx.capsule_role,
        ctx.capsule_epoch,
        "WHISPER_CAPSULE_SESSION_TAG_V1",
    )


def derive_repair_hash(ctx: RepairSessionContext) -> str:
    """
    Derive a session-authorized repair hash.

    Repair material is valid only under the session and repair round.
    """
    _require_hex_hash("session_hash", ctx.session_hash)
    _require_non_empty("repair_epoch", ctx.repair_epoch)
    _require_non_empty("repair_nonce", ctx.repair_nonce)

    if ctx.repair_counter < 0:
        raise ValueError("repair_counter must be >= 0")

    return stable_hash_hex(
        ctx.session_hash,
        ctx.repair_epoch,
        ctx.repair_nonce,
        str(ctx.repair_counter),
        "WHISPER_REPAIR_HASH_V1",
    )


def validate_session_tag(expected_tag: str, observed_tag: str) -> bool:
    """
    Constant-time equality check for session-bound tags.
    """
    _require_non_empty("expected_tag", expected_tag)
    _require_non_empty("observed_tag", observed_tag)

    return hmac.compare_digest(expected_tag, observed_tag)


if __name__ == "__main__":
    session = derive_session_hash(
        SessionContext(
            sol_id="sol-demo",
            epoch="1",
            local_ephemeral_material="local",
            remote_ephemeral_material="remote",
            session_nonce="nonce-demo",
            message_commitment="message-commitment",
            transfer_profile_commitment="profile-commitment",
        )
    )

    fragment_tag = derive_fragment_session_tag(
        FragmentSessionContext(
            session_hash=session,
            fragment_nonce="fragment-nonce",
            fragment_index_commitment="fragment-index-commitment",
            fragment_role="primary",
            capsule_nonce="capsule-nonce",
        )
    )

    capsule_tag = derive_capsule_session_tag(
        CapsuleSessionContext(
            session_hash=session,
            capsule_nonce="capsule-nonce",
            capsule_role="data",
            capsule_epoch="1",
        )
    )

    repair_hash = derive_repair_hash(
        RepairSessionContext(
            session_hash=session,
            repair_epoch="1",
            repair_nonce="repair-nonce",
            repair_counter=0,
        )
    )

    print("Session hash:", session[:16])
    print("Fragment tag:", fragment_tag[:16])
    print("Capsule tag:", capsule_tag[:16])
    print("Repair hash:", repair_hash[:16])
    print("Valid fragment tag:", validate_session_tag(fragment_tag, fragment_tag))
