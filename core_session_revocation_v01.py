"""
WHISPER v1.6.x — Core Session Revocation v0.1

Purpose:
Validate Core-side session revocation.

A revoked session cannot become active again.

Revocation is Core-side truth.

It is not undone by:
- old session seal replay
- new activation attempt
- organ restart
- Lemonade fallback
- Daemon resend
- intake retry
- outbound retry

Core rule:
A session may die.
It must not resurrect.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Dict, List, Literal, Set


SessionState = Literal[
    "ACTIVE",
    "CLOSING",
    "CLOSED",
    "REVOKED",
]

SessionDecision = Literal[
    "allow",
    "deny",
    "reject",
]

RevocationReason = Literal[
    "USER_REVOKED",
    "CORE_POLICY",
    "REPLAY_DETECTED",
    "STATE_VIOLATION",
    "ORGAN_COMPROMISED",
]


@dataclass(frozen=True)
class CoreSessionIdentity:
    session_id: str
    session_start_seal: str
    core_binding_commitment: str


@dataclass
class CoreSessionRecord:
    identity: CoreSessionIdentity
    state: SessionState = "ACTIVE"
    revocation_flag: bool = False
    revocation_epoch: str | None = None
    revocation_reason: RevocationReason | None = None
    close_code: str | None = None
    events: List[str] = field(default_factory=list)


@dataclass
class CoreSessionStore:
    sessions: Dict[str, CoreSessionRecord] = field(default_factory=dict)
    revoked_sessions: Set[str] = field(default_factory=set)


def stable_hash_hex(*parts: str) -> str:
    h = sha256()

    for part in parts:
        h.update(part.encode("utf-8"))
        h.update(b"\x00")

    return h.hexdigest()


def build_session_identity(
    session_id: str,
    session_start_seal: str,
    core_binding_material: str,
) -> CoreSessionIdentity:
    if not session_id:
        raise ValueError("session_id must be non-empty")
    if not session_start_seal:
        raise ValueError("session_start_seal must be non-empty")
    if not core_binding_material:
        raise ValueError("core_binding_material must be non-empty")

    return CoreSessionIdentity(
        session_id=session_id,
        session_start_seal=session_start_seal,
        core_binding_commitment=stable_hash_hex(
            session_id,
            session_start_seal,
            core_binding_material,
            "WHISPER_CORE_SESSION_BINDING_V1",
        ),
    )


def create_session_store() -> CoreSessionStore:
    return CoreSessionStore()


def register_session(
    store: CoreSessionStore,
    identity: CoreSessionIdentity,
) -> CoreSessionRecord:
    if identity.session_id in store.revoked_sessions:
        raise ValueError("cannot register revoked session")

    record = CoreSessionRecord(
        identity=identity,
        state="ACTIVE",
        revocation_flag=False,
        events=["session_registered"],
    )

    store.sessions[identity.session_id] = record

    return record


def revoke_core_session(
    store: CoreSessionStore,
    session_id: str,
    revocation_epoch: str,
    reason: RevocationReason,
) -> CoreSessionRecord:
    if not session_id:
        raise ValueError("session_id must be non-empty")
    if not revocation_epoch:
        raise ValueError("revocation_epoch must be non-empty")

    record = store.sessions.get(session_id)

    if record is None:
        identity = CoreSessionIdentity(
            session_id=session_id,
            session_start_seal="unknown",
            core_binding_commitment=stable_hash_hex(
                session_id,
                "revoked_unknown_session",
            ),
        )

        record = CoreSessionRecord(
            identity=identity,
            state="REVOKED",
            revocation_flag=True,
            revocation_epoch=revocation_epoch,
            revocation_reason=reason,
            events=["unknown_session_revoked"],
        )

        store.sessions[session_id] = record
    else:
        record.state = "REVOKED"
        record.revocation_flag = True
        record.revocation_epoch = revocation_epoch
        record.revocation_reason = reason
        record.events.append("session_revoked")

    store.revoked_sessions.add(session_id)

    return record


def is_session_revoked(store: CoreSessionStore, session_id: str) -> bool:
    record = store.sessions.get(session_id)

    if session_id in store.revoked_sessions:
        return True

    if record is None:
        return False

    return record.revocation_flag is True or record.state == "REVOKED"


def close_session(
    store: CoreSessionStore,
    session_id: str,
    close_code: str,
) -> CoreSessionRecord:
    record = store.sessions[session_id]

    if record.state == "REVOKED":
        record.events.append("close_ignored_session_revoked")
        return record

    record.state = "CLOSED"
    record.close_code = close_code
    record.events.append("session_closed")

    return record


def attempt_session_reactivation(
    store: CoreSessionStore,
    session_id: str,
    proposed_start_seal: str,
) -> SessionDecision:
    """
    A revoked session cannot reactivate.

    A closed session cannot reactivate.

    v01 rule:
    sessions are not resurrectable.
    """
    record = store.sessions.get(session_id)

    if is_session_revoked(store, session_id):
        return "reject"

    if record is None:
        return "deny"

    if record.state in {"CLOSED", "CLOSING"}:
        return "reject"

    if record.identity.session_start_seal != proposed_start_seal:
        return "deny"

    return "allow"


def decide_inbound_for_session(
    store: CoreSessionStore,
    session_id: str,
    material_coherent: bool,
) -> SessionDecision:
    """
    Dôme-side decision for session-bound inbound material.
    """
    if is_session_revoked(store, session_id):
        return "reject"

    if not material_coherent:
        return "reject"

    record = store.sessions.get(session_id)

    if record is None:
        return "deny"

    if record.state != "ACTIVE":
        return "reject"

    return "allow"


def decide_outbound_for_session(
    store: CoreSessionStore,
    session_id: str,
) -> SessionDecision:
    """
    Outbound emission must not proceed for revoked or closed sessions.
    """
    if is_session_revoked(store, session_id):
        return "reject"

    record = store.sessions.get(session_id)

    if record is None:
        return "deny"

    if record.state != "ACTIVE":
        return "reject"

    return "allow"


def organ_restart_restores_session(
    store: CoreSessionStore,
    session_id: str,
) -> bool:
    """
    Organ restart must not restore a revoked session.
    """
    _ = "organ_restart"

    return not is_session_revoked(store, session_id)


def lemonade_fallback_restores_session(
    store: CoreSessionStore,
    session_id: str,
) -> bool:
    """
    Lemonade fallback must not restore a revoked session.
    """
    _ = "lemonade_fallback"

    return not is_session_revoked(store, session_id)


def daemon_resend_restores_session(
    store: CoreSessionStore,
    session_id: str,
) -> bool:
    """
    Daemon resend must not restore a revoked session.
    """
    _ = "daemon_resend"

    return not is_session_revoked(store, session_id)


def session_revocation_summary(
    store: CoreSessionStore,
    session_id: str,
) -> Dict[str, object]:
    record = store.sessions.get(session_id)

    if record is None:
        return {
            "session_id": session_id,
            "known": False,
            "revoked": False,
        }

    return {
        "session_id": session_id,
        "known": True,
        "state": record.state,
        "revoked": is_session_revoked(store, session_id),
        "revocation_epoch": record.revocation_epoch,
        "revocation_reason": record.revocation_reason,
        "events": list(record.events),
    }


if __name__ == "__main__":
    store = create_session_store()

    identity = build_session_identity(
        session_id="session-1",
        session_start_seal="seal-1",
        core_binding_material="core-binding",
    )

    register_session(store, identity)

    revoke_core_session(
        store=store,
        session_id="session-1",
        revocation_epoch="epoch-2",
        reason="USER_REVOKED",
    )

    print("Session revoked:", is_session_revoked(store, "session-1"))
    print(
        "Reactivation decision:",
        attempt_session_reactivation(store, "session-1", "seal-1"),
    )
    print(
        "Inbound decision:",
        decide_inbound_for_session(store, "session-1", material_coherent=True),
    )
    print(
        "Outbound decision:",
        decide_outbound_for_session(store, "session-1"),
    )
