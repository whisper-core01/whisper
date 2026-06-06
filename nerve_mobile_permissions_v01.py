"""
WHISPER — Nerve Mobile Permissions v0.1

Purpose:
Define the mobile sensor permissions required by Nerve Mobile capabilities.

Permissions open senses.

They do not grant identity.

They do not grant admission.

They do not grant Core trust.

They do not open the Vault.

They do not create a session.

Core rule:
The Nerve may ask the OS for senses.
The Core decides what it wants to hear.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal


PermissionName = Literal[
    "text_input",
    "audio_capture",
    "image_capture",
    "image_gallery",
    "video_capture",
    "ui_event",
    "file_picker",
    "location_hint",
]

PermissionState = Literal[
    "granted",
    "denied",
    "not_requested",
    "revoked",
]

CapabilityName = Literal[
    "text",
    "audio",
    "image",
    "video",
    "event",
    "file",
    "location_hint",
]


CAPABILITY_PERMISSIONS: Dict[str, List[str]] = {
    "text": ["text_input"],
    "audio": ["audio_capture"],
    "image": ["image_capture", "image_gallery"],
    "video": ["video_capture"],
    "event": ["ui_event"],
    "file": ["file_picker"],
    "location_hint": ["location_hint"],
}


ALWAYS_AVAILABLE_PERMISSIONS = {
    "text_input",
    "ui_event",
}


@dataclass(frozen=True)
class PermissionRequest:
    capability: str
    required_permissions: List[str]


@dataclass
class PermissionStore:
    states: Dict[str, PermissionState] = field(default_factory=dict)


@dataclass(frozen=True)
class PermissionDecision:
    capability: str
    allowed: bool
    missing_permissions: List[str]
    denied_permissions: List[str]
    revoked_permissions: List[str]


def create_permission_store() -> PermissionStore:
    store = PermissionStore()

    for permission in ALWAYS_AVAILABLE_PERMISSIONS:
        store.states[permission] = "granted"

    return store


def required_permissions_for_capability(capability: str) -> List[str]:
    if capability not in CAPABILITY_PERMISSIONS:
        raise ValueError(f"unsupported capability: {capability}")

    return list(CAPABILITY_PERMISSIONS[capability])


def build_permission_request(capability: str) -> PermissionRequest:
    return PermissionRequest(
        capability=capability,
        required_permissions=required_permissions_for_capability(capability),
    )


def set_permission_state(
    store: PermissionStore,
    permission: str,
    state: PermissionState,
) -> None:
    if state not in {"granted", "denied", "not_requested", "revoked"}:
        raise ValueError(f"unsupported permission state: {state}")

    store.states[permission] = state


def grant_permission(store: PermissionStore, permission: str) -> None:
    set_permission_state(store, permission, "granted")


def deny_permission(store: PermissionStore, permission: str) -> None:
    set_permission_state(store, permission, "denied")


def revoke_permission(store: PermissionStore, permission: str) -> None:
    set_permission_state(store, permission, "revoked")


def permission_state(
    store: PermissionStore,
    permission: str,
) -> PermissionState:
    return store.states.get(permission, "not_requested")


def evaluate_capability_permission(
    store: PermissionStore,
    capability: str,
) -> PermissionDecision:
    required = required_permissions_for_capability(capability)

    missing = []
    denied = []
    revoked = []

    for permission in required:
        state = permission_state(store, permission)

        if state == "not_requested":
            missing.append(permission)
        elif state == "denied":
            denied.append(permission)
        elif state == "revoked":
            revoked.append(permission)

    allowed = not missing and not denied and not revoked

    return PermissionDecision(
        capability=capability,
        allowed=allowed,
        missing_permissions=missing,
        denied_permissions=denied,
        revoked_permissions=revoked,
    )


def filter_capabilities_by_permissions(
    store: PermissionStore,
    capabilities: List[str],
) -> List[str]:
    allowed = []

    for capability in capabilities:
        decision = evaluate_capability_permission(store, capability)

        if decision.allowed:
            allowed.append(capability)

    return allowed


def permissions_affect_admission() -> bool:
    return False


def permissions_affect_identity() -> bool:
    return False


def permissions_open_vault() -> bool:
    return False


def permissions_create_session() -> bool:
    return False


def permission_summary(store: PermissionStore) -> Dict[str, str]:
    return dict(store.states)


if __name__ == "__main__":
    store = create_permission_store()

    grant_permission(store, "audio_capture")
    grant_permission(store, "image_capture")
    grant_permission(store, "image_gallery")
    grant_permission(store, "video_capture")

    capabilities = ["text", "audio", "image", "video", "event", "location_hint"]

    allowed = filter_capabilities_by_permissions(store, capabilities)

    print("Allowed capabilities:", allowed)
    print("Permissions affect admission:", permissions_affect_admission())
    print("Permissions open Vault:", permissions_open_vault())
