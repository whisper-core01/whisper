"""
WHISPER v1.4.0 — Local Session Revocation.

Local-first session revocation.

This module implements:
- mark_session_revoked()
- is_session_revoked()
- validate_not_revoked()
- expire_revocations()

Core invariant:
A session may die locally without global accusation.

Revocation is local refusal, not proof of compromise.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Literal, Optional

from session_hash_v01 import validate_session_tag


RevocationReason = Literal[
    "USER_LEFT_SESSION",
    "USER_CANCELLED_TRANSFER",
    "LOCAL_SESSION_CLOSED",
    "SESSION_EXPIRED",
    "REPLAY_DETECTED",
    "CUSTODY_EXPIRED",
    "REPAIR_ABUSE",
    "POLICY_VIOLATION",
    "INVALID_MATERIAL",
    "STORAGE_PRESSURE",
]

RevocationScope = Literal[
    "SESSION",
    "EPOCH",
    "SOL_LINK",
    "RELAY_LOCAL",
    "TEMPORARY",
    "PERMANENT_LOCAL",
]


@dataclass(frozen=True)
class RevocationEntry:
    session_hash: str
    reason: RevocationReason
    scope: RevocationScope = "SESSION"
    created_at: int = 0
    expires_at: Optional[int] = None
    evidence_digest: Optional[str] = None


@dataclass
class SessionRevocationStore:
    entries: Dict[str, RevocationEntry] = field(default_factory=dict)


VALID_REASONS = {
    "USER_LEFT_SESSION",
    "USER_CANCELLED_TRANSFER",
    "LOCAL_SESSION_CLOSED",
    "SESSION_EXPIRED",
    "REPLAY_DETECTED",
    "CUSTODY_EXPIRED",
    "REPAIR_ABUSE",
    "POLICY_VIOLATION",
    "INVALID_MATERIAL",
    "STORAGE_PRESSURE",
}

VALID_SCOPES = {
    "SESSION",
    "EPOCH",
    "SOL_LINK",
    "RELAY_LOCAL",
    "TEMPORARY",
    "PERMANENT_LOCAL",
}


def _require_session_hash(session_hash: str) -> None:
    if not isinstance(session_hash, str) or len(session_hash) != 64:
        raise ValueError("session_hash must be a 64-char hex hash")

    try:
        int(session_hash, 16)
    except ValueError as exc:
        raise ValueError("session_hash must be hex") from exc


def _require_reason(reason: str) -> None:
    if reason not in VALID_REASONS:
        raise ValueError(f"unsupported revocation reason: {reason}")


def _require_scope(scope: str) -> None:
    if scope not in VALID_SCOPES:
        raise ValueError(f"unsupported revocation scope: {scope}")


def mark_session_revoked(
    store: SessionRevocationStore,
    session_hash: str,
    reason: RevocationReason,
    scope: RevocationScope = "SESSION",
    created_at: int = 0,
    expires_at: Optional[int] = None,
    evidence_digest: Optional[str] = None,
) -> RevocationEntry:
    """
    Mark a session hash as locally revoked.

    This is not a global accusation.
    It only means this local WHISPER instance refuses future material
    bound to that session hash.
    """
    _require_session_hash(session_hash)
    _require_reason(reason)
    _require_scope(scope)

    if created_at < 0:
        raise ValueError("created_at must be >= 0")

    if expires_at is not None and expires_at <= created_at:
        raise ValueError("expires_at must be greater than created_at")

    entry = RevocationEntry(
        session_hash=session_hash,
        reason=reason,
        scope=scope,
        created_at=created_at,
        expires_at=expires_at,
        evidence_digest=evidence_digest,
    )

    store.entries[session_hash] = entry
    return entry


def is_session_revoked(
    store: SessionRevocationStore,
    session_hash: str,
    now: int = 0,
) -> bool:
    _require_session_hash(session_hash)

    entry = store.entries.get(session_hash)

    if entry is None:
        return False

    if entry.expires_at is not None and now >= entry.expires_at:
        return False

    return True


def get_revocation_entry(
    store: SessionRevocationStore,
    session_hash: str,
    now: int = 0,
) -> Optional[RevocationEntry]:
    _require_session_hash(session_hash)

    entry = store.entries.get(session_hash)

    if entry is None:
        return None

    if entry.expires_at is not None and now >= entry.expires_at:
        return None

    return entry


def validate_not_revoked(
    store: SessionRevocationStore,
    session_hash: str,
    now: int = 0,
) -> bool:
    return not is_session_revoked(store, session_hash, now=now)


def expire_revocations(
    store: SessionRevocationStore,
    now: int,
) -> int:
    """
    Remove expired local revocation entries.

    Returns the number of entries removed.
    """
    if now < 0:
        raise ValueError("now must be >= 0")

    expired = [
        session_hash
        for session_hash, entry in store.entries.items()
        if entry.expires_at is not None and now >= entry.expires_at
    ]

    for session_hash in expired:
        del store.entries[session_hash]

    return len(expired)


def validate_session_tag_not_revoked(
    store: SessionRevocationStore,
    session_hash: str,
    expected_tag: str,
    observed_tag: str,
    now: int = 0,
) -> bool:
    """
    Validate both:
    - session tag matches
    - session hash is not locally revoked
    """
    if is_session_revoked(store, session_hash, now=now):
        return False

    return validate_session_tag(expected_tag, observed_tag)


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

    store = SessionRevocationStore()

    print("Initially revoked:", is_session_revoked(store, session_hash))

    mark_session_revoked(
        store=store,
        session_hash=session_hash,
        reason="USER_LEFT_SESSION",
        scope="SESSION",
        created_at=10,
    )

    print("After revocation:", is_session_revoked(store, session_hash))
    print("Validate not revoked:", validate_not_revoked(store, session_hash))
