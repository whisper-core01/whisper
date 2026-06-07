"""
WHISPER v1.8.0 — Network Medium Selection v0.2

Correct hierarchy:

1. INTERNET_PRIMARY
   - Reticulum + VoxMesh
   - full capabilities

2. MOBILE_DATA_4G_5G
   - Reticulum + VoxMesh
   - full capabilities

3. LORA_FALLBACK
   - degraded survival mode
   - text only

Core doctrine:
Internet first.
4G/5G next.
LoRa last resort.

As long as an IP path exists, WHISPER stays complete.
When IP disappears, WHISPER reduces its voice to text.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Set


MediumState = Literal["AVAILABLE", "UNAVAILABLE"]
NetworkMode = Literal["CONNECTED", "DEGRADED_SURVIVAL", "OFFLINE"]
NetworkMedium = Literal["INTERNET_PRIMARY", "MOBILE_DATA_4G_5G", "LORA_FALLBACK", "NONE"]
TransportStack = Literal["RETICULUM_VOXMESH", "LORA_TEXT", "NONE"]

FULL_PAYLOADS: Set[str] = {"text", "audio", "image", "video", "file", "event"}
TEXT_ONLY_PAYLOADS: Set[str] = {"text"}


@dataclass(frozen=True)
class NetworkAvailability:
    internet_primary: MediumState
    mobile_data_4g_5g: MediumState
    lora: MediumState


@dataclass(frozen=True)
class NetworkMediumDecision:
    mode: NetworkMode
    medium: NetworkMedium
    stack: TransportStack
    allowed_payloads: Set[str]
    reason: str


@dataclass
class DaemonNetworkBoundaryState:
    mode: NetworkMode = "OFFLINE"
    medium: NetworkMedium = "NONE"
    stack: TransportStack = "NONE"
    allowed_payloads: Set[str] = field(default_factory=set)
    changed_core_rails: bool = False
    exposed_wasm: bool = False
    touched_dome: bool = False
    participated_in_immunity: bool = False


def guided_link(test_name: str) -> str:
    return f"WHISPER_GUIDED_LINK::v1.8.0::network_medium_selection_v02::{test_name}"


def decide_network_medium(availability: NetworkAvailability) -> NetworkMediumDecision:
    if availability.internet_primary == "AVAILABLE":
        return NetworkMediumDecision(
            mode="CONNECTED",
            medium="INTERNET_PRIMARY",
            stack="RETICULUM_VOXMESH",
            allowed_payloads=set(FULL_PAYLOADS),
            reason="internet_primary_available",
        )

    if availability.mobile_data_4g_5g == "AVAILABLE":
        return NetworkMediumDecision(
            mode="CONNECTED",
            medium="MOBILE_DATA_4G_5G",
            stack="RETICULUM_VOXMESH",
            allowed_payloads=set(FULL_PAYLOADS),
            reason="mobile_data_4g_5g_available",
        )

    if availability.lora == "AVAILABLE":
        return NetworkMediumDecision(
            mode="DEGRADED_SURVIVAL",
            medium="LORA_FALLBACK",
            stack="LORA_TEXT",
            allowed_payloads=set(TEXT_ONLY_PAYLOADS),
            reason="lora_fallback_available",
        )

    return NetworkMediumDecision(
        mode="OFFLINE",
        medium="NONE",
        stack="NONE",
        allowed_payloads=set(),
        reason="no_network_medium_available",
    )


def apply_network_medium_decision(
    daemon: DaemonNetworkBoundaryState,
    decision: NetworkMediumDecision,
) -> DaemonNetworkBoundaryState:
    daemon.mode = decision.mode
    daemon.medium = decision.medium
    daemon.stack = decision.stack
    daemon.allowed_payloads = set(decision.allowed_payloads)
    return daemon


def is_full_capability_mode(decision: NetworkMediumDecision) -> bool:
    return (
        decision.mode == "CONNECTED"
        and decision.stack == "RETICULUM_VOXMESH"
        and decision.allowed_payloads == FULL_PAYLOADS
    )


def is_text_only_mode(decision: NetworkMediumDecision) -> bool:
    return (
        decision.mode == "DEGRADED_SURVIVAL"
        and decision.stack == "LORA_TEXT"
        and decision.allowed_payloads == TEXT_ONLY_PAYLOADS
    )


def network_switch_changes_core_rails(daemon: DaemonNetworkBoundaryState) -> bool:
    return daemon.changed_core_rails


def network_switch_exposes_wasm(daemon: DaemonNetworkBoundaryState) -> bool:
    return daemon.exposed_wasm


def network_switch_touches_dome(daemon: DaemonNetworkBoundaryState) -> bool:
    return daemon.touched_dome


def network_switch_participates_in_immunity(daemon: DaemonNetworkBoundaryState) -> bool:
    return daemon.participated_in_immunity


if __name__ == "__main__":
    primary = decide_network_medium(NetworkAvailability("AVAILABLE", "AVAILABLE", "AVAILABLE"))
    mobile = decide_network_medium(NetworkAvailability("UNAVAILABLE", "AVAILABLE", "AVAILABLE"))
    lora = decide_network_medium(NetworkAvailability("UNAVAILABLE", "UNAVAILABLE", "AVAILABLE"))
    offline = decide_network_medium(NetworkAvailability("UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE"))

    print("Primary medium:", primary.medium)
    print("Primary stack:", primary.stack)
    print("Primary payloads:", sorted(primary.allowed_payloads))

    print("Mobile medium:", mobile.medium)
    print("Mobile stack:", mobile.stack)
    print("Mobile payloads:", sorted(mobile.allowed_payloads))

    print("LoRa medium:", lora.medium)
    print("LoRa stack:", lora.stack)
    print("LoRa payloads:", sorted(lora.allowed_payloads))

    print("Offline medium:", offline.medium)
    print("Offline mode:", offline.mode)
