"""
WHISPER — Nerve Mobile Capabilities v0.1

Purpose:
Define what a Nerve Mobile can declare as sensory capabilities, and what it
must never claim.

Capabilities are not identity.

Capabilities are not rights.

Capabilities are not admission.

Capabilities are only a sensory declaration.

The Core remains sovereign.
The Nerve declares.
The Core decides.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Set


Capability = Literal[
    "text",
    "audio",
    "image",
    "video",
    "event",
    "location_hint",
    "file",
]

CoreCapabilityDecision = Literal["accepted", "ignored", "revoked"]


BASE_CAPABILITIES: Set[str] = {
    "text",
    "audio",
    "image",
    "video",
    "event",
}

OPTIONAL_CAPABILITIES: Set[str] = {
    "location_hint",
    "file",
}

FORBIDDEN_CAPABILITIES: Set[str] = {
    "crypto",
    "identity",
    "session",
}

SUPPORTED_CAPABILITIES: Set[str] = BASE_CAPABILITIES | OPTIONAL_CAPABILITIES


@dataclass(frozen=True)
class CapabilityDeclaration:
    nerve: str
    kind: str
    capabilities: List[str]
    admission_epoch: str


@dataclass(frozen=True)
class CoreCapabilityPolicy:
    accepted_capabilities: List[str]
    ignored_capabilities: List[str]
    revoked_capabilities: List[str]


@dataclass(frozen=True)
class CapabilityDecisionReport:
    accepted: List[str]
    ignored: List[str]
    revoked: List[str]
    rejected_forbidden: List[str]


@dataclass(frozen=True)
class MobileVaultCapabilityProfile:
    capability_profile: List[str]
    ux_only: bool = True
    sovereign: bool = False


def _require_non_empty(name: str, value: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")


def normalize_capabilities(capabilities: List[str]) -> List[str]:
    if not capabilities:
        raise ValueError("capabilities must not be empty")

    normalized = []

    for capability in capabilities:
        _require_non_empty("capability", capability)
        if capability not in normalized:
            normalized.append(capability)

    return normalized


def validate_declared_capabilities(capabilities: List[str]) -> None:
    normalized = normalize_capabilities(capabilities)

    forbidden = [cap for cap in normalized if cap in FORBIDDEN_CAPABILITIES]

    if forbidden:
        raise ValueError(f"forbidden capabilities declared: {forbidden}")


def build_capability_declaration(
    capabilities: List[str],
    admission_epoch: str,
) -> CapabilityDeclaration:
    """
    Build the Nerve Mobile capability declaration.

    This declaration is sensory only.

    It must not contain:
    - crypto
    - identity
    - session
    - Vault
    - binding
    - secret
    """
    _require_non_empty("admission_epoch", admission_epoch)

    normalized = normalize_capabilities(capabilities)
    validate_declared_capabilities(normalized)

    return CapabilityDeclaration(
        nerve="mobile",
        kind="capability_declaration",
        capabilities=normalized,
        admission_epoch=admission_epoch,
    )


def evaluate_capabilities_for_core(
    declaration: CapabilityDeclaration,
    revoked_capabilities: List[str] | None = None,
) -> CapabilityDecisionReport:
    """
    Core-side capability evaluation.

    Capabilities do not grant rights.

    Unsupported capabilities are ignored.

    Revoked capabilities remain revoked.

    Forbidden capabilities are rejected if they appear.
    """
    if declaration.nerve != "mobile":
        raise ValueError("unsupported nerve kind")

    if declaration.kind != "capability_declaration":
        raise ValueError("unsupported declaration kind")

    revoked_set = set(revoked_capabilities or [])
    accepted = []
    ignored = []
    revoked = []
    rejected_forbidden = []

    for capability in declaration.capabilities:
        if capability in FORBIDDEN_CAPABILITIES:
            rejected_forbidden.append(capability)
            continue

        if capability in revoked_set:
            revoked.append(capability)
            continue

        if capability in SUPPORTED_CAPABILITIES:
            accepted.append(capability)
            continue

        ignored.append(capability)

    return CapabilityDecisionReport(
        accepted=accepted,
        ignored=ignored,
        revoked=revoked,
        rejected_forbidden=rejected_forbidden,
    )


def build_core_capability_policy(
    report: CapabilityDecisionReport,
) -> CoreCapabilityPolicy:
    """
    Convert a capability decision report into a Core-side policy.

    The Core may accept, ignore, or revoke capabilities.

    The Nerve does not negotiate.
    """
    return CoreCapabilityPolicy(
        accepted_capabilities=list(report.accepted),
        ignored_capabilities=list(report.ignored),
        revoked_capabilities=list(report.revoked),
    )


def build_mobile_vault_capability_profile(
    capabilities: List[str],
) -> MobileVaultCapabilityProfile:
    """
    Optional UX-only capability profile.

    This profile may exist in the Mobile Vault only as local UX memory.

    It is never sovereign.

    It must never be used for admission.
    """
    normalized = normalize_capabilities(capabilities)
    validate_declared_capabilities(normalized)

    return MobileVaultCapabilityProfile(
        capability_profile=normalized,
        ux_only=True,
        sovereign=False,
    )


def capabilities_affect_admission() -> bool:
    """
    Capabilities must not affect admission.

    Admission depends on Sol challenge, admission code, Core binding, and
    revocation state.

    Not on sensory capabilities.
    """
    return False


def capabilities_affect_reappearance() -> bool:
    """
    Capabilities must not affect reappearance.

    Reappearance depends on fresh Sol challenge continuity and Core-side
    binding state.

    Not on sensory capabilities.
    """
    return False


def capability_report_to_safe_summary(
    report: CapabilityDecisionReport,
) -> Dict[str, List[str]]:
    return {
        "accepted": list(report.accepted),
        "ignored": list(report.ignored),
        "revoked": list(report.revoked),
        "rejected_forbidden": list(report.rejected_forbidden),
    }


if __name__ == "__main__":
    declaration = build_capability_declaration(
        capabilities=["text", "audio", "image", "video", "event"],
        admission_epoch="epoch-1",
    )

    report = evaluate_capabilities_for_core(declaration)

    print("Declared capabilities:", declaration.capabilities)
    print("Accepted capabilities:", report.accepted)
    print("Ignored capabilities:", report.ignored)
    print("Revoked capabilities:", report.revoked)
    print("Capabilities affect admission:", capabilities_affect_admission())
