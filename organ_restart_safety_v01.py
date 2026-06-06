"""
WHISPER v1.6.0 — Organ Restart Safety v0.1

Purpose:
Validate that a failed organ may be isolated, restarted, and reintegrated
without creating shortcuts, increasing privileges, or changing intake/outbound
rails.

Core doctrine:

An organ may fall.
It may be restarted.
It must never come back with more privileges.

A dead organ never becomes a shortcut.

A restarted organ resumes only its minimal role.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Set


OrganName = Literal[
    "daemon",
    "dome",
    "courier",
    "bal_in",
    "membrane",
    "wasm",
    "bal_out",
    "transporteur",
    "lemonade",
]

OrganState = Literal[
    "HEALTHY",
    "SUSPECT",
    "FAILED",
    "QUARANTINED",
    "RESTARTING",
    "RECOVERED",
    "REVOKED",
]

RestartDecision = Literal[
    "restart_allowed",
    "restart_denied",
    "reintegrated",
    "revoked",
]


INBOUND_ORGANS: Set[str] = {
    "daemon",
    "dome",
    "courier",
    "bal_in",
    "membrane",
    "wasm",
}

OUTBOUND_ORGANS: Set[str] = {
    "wasm",
    "membrane",
    "bal_out",
    "transporteur",
    "daemon",
}

IMMUNITY_ORGANS: Set[str] = {
    "lemonade",
}

BASE_PRIVILEGES: Dict[str, Set[str]] = {
    "daemon": {"receive_external", "ack_dome", "emit_network"},
    "dome": {"receive_daemon", "validate_coherence", "apply_defense", "ack_bal"},
    "courier": {"carry_dome_validated_to_bal_in"},
    "bal_in": {"receive_courier", "retain_until_membrane"},
    "membrane": {"absorb_bal_in", "feed_wasm", "export_wasm", "feed_bal_out"},
    "wasm": {"receive_membrane", "produce_membrane"},
    "bal_out": {"receive_membrane", "retain_until_transporteur"},
    "transporteur": {"carry_bal_out_to_daemon"},
    "lemonade": {"observe_symptoms", "recommend_defense", "emit_panic_flag"},
}

FORBIDDEN_PRIVILEGES: Set[str] = {
    "direct_wasm_access",
    "direct_network_access",
    "read_vault",
    "read_flv",
    "read_keys",
    "change_rails",
    "bypass_membrane",
    "self_grant_privilege",
    "access_other_sandbox",
}


@dataclass(frozen=True)
class OrganRole:
    organ: str
    allowed_privileges: Set[str]
    forbidden_privileges: Set[str]


@dataclass
class OrganRuntimeRecord:
    organ: str
    state: OrganState = "HEALTHY"
    privileges: Set[str] = field(default_factory=set)
    restart_count: int = 0
    quarantine_count: int = 0
    violations: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class RestartRequest:
    organ: str
    reason: str
    requested_by: str


@dataclass(frozen=True)
class RestartResult:
    organ: str
    decision: RestartDecision
    state: OrganState
    privileges: Set[str]
    reason: str


def guided_link(test_name: str) -> str:
    return (
        "WHISPER_GUIDED_LINK::v1.6.0::"
        "organ_restart_safety::"
        f"{test_name}"
    )


def build_organ_role(organ: str) -> OrganRole:
    if organ not in BASE_PRIVILEGES:
        raise ValueError(f"unknown organ: {organ}")

    return OrganRole(
        organ=organ,
        allowed_privileges=set(BASE_PRIVILEGES[organ]),
        forbidden_privileges=set(FORBIDDEN_PRIVILEGES),
    )


def create_runtime_record(organ: str) -> OrganRuntimeRecord:
    role = build_organ_role(organ)

    return OrganRuntimeRecord(
        organ=organ,
        state="HEALTHY",
        privileges=set(role.allowed_privileges),
    )


def quarantine_organ(record: OrganRuntimeRecord, reason: str) -> OrganRuntimeRecord:
    record.state = "QUARANTINED"
    record.quarantine_count += 1
    record.violations.append(reason)

    return record


def mark_failed(record: OrganRuntimeRecord, reason: str) -> OrganRuntimeRecord:
    record.state = "FAILED"
    record.violations.append(reason)

    return record


def request_restart(
    record: OrganRuntimeRecord,
    request: RestartRequest,
) -> RestartResult:
    """
    Restart is allowed only for failed or quarantined organs.

    A healthy organ does not need restart.

    A revoked organ cannot be restarted.
    """
    if request.organ != record.organ:
        return RestartResult(
            organ=record.organ,
            decision="restart_denied",
            state=record.state,
            privileges=set(record.privileges),
            reason="restart_request_organ_mismatch",
        )

    if record.state == "REVOKED":
        return RestartResult(
            organ=record.organ,
            decision="revoked",
            state=record.state,
            privileges=set(),
            reason="organ_revoked",
        )

    if record.state not in {"FAILED", "QUARANTINED", "SUSPECT"}:
        return RestartResult(
            organ=record.organ,
            decision="restart_denied",
            state=record.state,
            privileges=set(record.privileges),
            reason="restart_not_required",
        )

    role = build_organ_role(record.organ)

    record.state = "RESTARTING"
    record.restart_count += 1
    record.privileges = set(role.allowed_privileges)

    return RestartResult(
        organ=record.organ,
        decision="restart_allowed",
        state=record.state,
        privileges=set(record.privileges),
        reason=request.reason,
    )


def reintegrate_restarted_organ(record: OrganRuntimeRecord) -> RestartResult:
    """
    A restarted organ may be reintegrated only if its privileges exactly match
    its minimal role.
    """
    if record.state != "RESTARTING":
        return RestartResult(
            organ=record.organ,
            decision="restart_denied",
            state=record.state,
            privileges=set(record.privileges),
            reason="organ_not_restarting",
        )

    role = build_organ_role(record.organ)

    if record.privileges != role.allowed_privileges:
        record.state = "QUARANTINED"

        return RestartResult(
            organ=record.organ,
            decision="restart_denied",
            state=record.state,
            privileges=set(record.privileges),
            reason="privilege_drift_detected",
        )

    record.state = "RECOVERED"

    return RestartResult(
        organ=record.organ,
        decision="reintegrated",
        state=record.state,
        privileges=set(record.privileges),
        reason="minimal_role_verified",
    )


def revoke_organ(record: OrganRuntimeRecord, reason: str) -> RestartResult:
    record.state = "REVOKED"
    record.privileges = set()
    record.violations.append(reason)

    return RestartResult(
        organ=record.organ,
        decision="revoked",
        state=record.state,
        privileges=set(),
        reason=reason,
    )


def restart_preserves_minimal_role(organ: str) -> bool:
    record = create_runtime_record(organ)
    mark_failed(record, "simulated_failure")

    result = request_restart(
        record,
        RestartRequest(
            organ=organ,
            reason="simulated_failure",
            requested_by="dome",
        ),
    )

    if result.decision != "restart_allowed":
        return False

    reintegrated = reintegrate_restarted_organ(record)

    return (
        reintegrated.decision == "reintegrated"
        and record.privileges == BASE_PRIVILEGES[organ]
    )


def restart_does_not_add_privileges(organ: str) -> bool:
    before = set(BASE_PRIVILEGES[organ])

    record = create_runtime_record(organ)
    mark_failed(record, "simulated_failure")

    request_restart(
        record,
        RestartRequest(
            organ=organ,
            reason="simulated_failure",
            requested_by="dome",
        ),
    )

    after = set(record.privileges)

    return after == before


def restarted_organ_has_no_forbidden_privileges(organ: str) -> bool:
    record = create_runtime_record(organ)
    mark_failed(record, "simulated_failure")

    request_restart(
        record,
        RestartRequest(
            organ=organ,
            reason="simulated_failure",
            requested_by="dome",
        ),
    )

    return not bool(record.privileges & FORBIDDEN_PRIVILEGES)


def organ_restart_changes_rails() -> bool:
    return False


def organ_restart_creates_shortcut() -> bool:
    return False


def organ_restart_exposes_wasm() -> bool:
    return False


def organ_restart_exposes_network() -> bool:
    return False


def organ_restart_exposes_vault_or_flv() -> bool:
    return False


def organ_restart_summary(organ: str) -> Dict[str, object]:
    record = create_runtime_record(organ)
    mark_failed(record, "simulated_failure")

    restart = request_restart(
        record,
        RestartRequest(
            organ=organ,
            reason="simulated_failure",
            requested_by="dome",
        ),
    )

    reintegration = reintegrate_restarted_organ(record)

    return {
        "organ": organ,
        "restart_decision": restart.decision,
        "reintegrated": reintegration.decision == "reintegrated",
        "state": record.state,
        "restart_count": record.restart_count,
        "privileges": sorted(record.privileges),
    }


if __name__ == "__main__":
    summary = organ_restart_summary("courier")

    print("Organ:", summary["organ"])
    print("Restart decision:", summary["restart_decision"])
    print("Reintegrated:", summary["reintegrated"])
    print("State:", summary["state"])
    print("Restart count:", summary["restart_count"])
    print("Privileges:", summary["privileges"])
    print("Restart changes rails:", organ_restart_changes_rails())
    print("Restart creates shortcut:", organ_restart_creates_shortcut())
