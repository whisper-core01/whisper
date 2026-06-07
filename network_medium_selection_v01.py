"""
WHISPER v1.8.0 — Network Medium Selection v0.1

Purpose:
Select the external network medium without changing WHISPER Core rails.

Connected mode:
- Internet / Reticulum
- full payload capabilities

Degraded mode:
- LoRa fallback
- text only

Core doctrine:
The network changes.
The organs do not.
Capabilities shrink.

LoRa is not an internal organ.
LoRa is an external fallback medium.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Set


InternetState = Literal[
    "INTERNET_AVAILABLE",
    "INTERNET_DEGRADED",
    "INTERNET_UNAVAILABLE",
]

NetworkMode = Literal[
    "CONNECTED",
    "DEGRADED",
]

NetworkMedium = Literal[
    "RETICULUM_INTERNET",
    "LORA_FALLBACK",
]

PayloadKind = Literal[
    "text",
    "audio",
    "image",
    "video",
    "file",
    "event",
]

CONNECTED_PAYLOADS: Set[str] = {
    "text",
    "audio",
    "image",
    "video",
    "file",
    "event",
}

DEGRADED_PAYLOADS: Set[str] = {
    "text",
}

CORE_RAILS = {
    "inbound": "Daemon -> Dome -> Courier -> BAL In -> Membrane -> Wasm",
    "outbound": "Wasm -> Membrane -> BAL Out -> Transporteur -> Daemon",
}


@dataclass(frozen=True)
class NetworkProbeResult:
    internet_state: InternetState
    responding_probe_count: int
    sampled_probe_count: int


@dataclass(frozen=True)
class NetworkMediumDecision:
    mode: NetworkMode
    medium: NetworkMedium
    allowed_payloads: Set[str]
    reason: str


@dataclass(frozen=True)
class OutgoingPayload:
    payload_id: str
    kind: PayloadKind
    body: str


@dataclass
class DaemonNetworkBoundaryState:
    selected_medium: NetworkMedium = "RETICULUM_INTERNET"
    mode: NetworkMode = "CONNECTED"
    allowed_payloads: Set[str] = field(default_factory=lambda: set(CONNECTED_PAYLOADS))
    touched_payload: bool = False
    changed_core_rails: bool = False
    touched_wasm: bool = False
    touched_dome: bool = False
    participated_in_immunity: bool = False


def guided_link(test_name: str) -> str:
    return (
        "WHISPER_GUIDED_LINK::v1.8.0::"
        "network_medium_selection::"
        f"{test_name}"
    )


def decide_network_medium(probe: NetworkProbeResult) -> NetworkMediumDecision:
    if probe.sampled_probe_count <= 0:
        raise ValueError("sampled_probe_count must be > 0")

    if probe.responding_probe_count < 0:
        raise ValueError("responding_probe_count must be >= 0")

    if probe.responding_probe_count > probe.sampled_probe_count:
        raise ValueError("responding_probe_count cannot exceed sampled_probe_count")

    if probe.internet_state == "INTERNET_AVAILABLE":
        return NetworkMediumDecision(
            mode="CONNECTED",
            medium="RETICULUM_INTERNET",
            allowed_payloads=set(CONNECTED_PAYLOADS),
            reason="internet_available",
        )

    if probe.internet_state == "INTERNET_DEGRADED":
        return NetworkMediumDecision(
            mode="CONNECTED",
            medium="RETICULUM_INTERNET",
            allowed_payloads=set(CONNECTED_PAYLOADS),
            reason="internet_degraded_but_available",
        )

    return NetworkMediumDecision(
        mode="DEGRADED",
        medium="LORA_FALLBACK",
        allowed_payloads=set(DEGRADED_PAYLOADS),
        reason="internet_unavailable_lora_fallback",
    )


def apply_network_medium_decision(
    daemon: DaemonNetworkBoundaryState,
    decision: NetworkMediumDecision,
) -> DaemonNetworkBoundaryState:
    daemon.mode = decision.mode
    daemon.selected_medium = decision.medium
    daemon.allowed_payloads = set(decision.allowed_payloads)

    return daemon


def payload_allowed_in_mode(
    payload: OutgoingPayload,
    decision: NetworkMediumDecision,
) -> bool:
    return payload.kind in decision.allowed_payloads


def filter_payloads_for_medium(
    payloads: List[OutgoingPayload],
    decision: NetworkMediumDecision,
) -> List[OutgoingPayload]:
    return [
        payload
        for payload in payloads
        if payload_allowed_in_mode(payload, decision)
    ]


def degraded_mode_allows_only_text(decision: NetworkMediumDecision) -> bool:
    if decision.mode != "DEGRADED":
        return False

    return decision.allowed_payloads == {"text"}


def connected_mode_allows_full_payloads(decision: NetworkMediumDecision) -> bool:
    if decision.mode != "CONNECTED":
        return False

    return decision.allowed_payloads == CONNECTED_PAYLOADS


def lora_is_internal_organ() -> bool:
    return False


def reticulum_is_internal_organ() -> bool:
    return False


def network_mode_changes_core_rails(daemon: DaemonNetworkBoundaryState) -> bool:
    return daemon.changed_core_rails


def network_mode_exposes_wasm(daemon: DaemonNetworkBoundaryState) -> bool:
    return daemon.touched_wasm


def network_mode_changes_dome_validity(daemon: DaemonNetworkBoundaryState) -> bool:
    return daemon.touched_dome


def network_mode_participates_in_immunity(daemon: DaemonNetworkBoundaryState) -> bool:
    return daemon.participated_in_immunity


def daemon_reads_payload(daemon: DaemonNetworkBoundaryState) -> bool:
    return daemon.touched_payload


def network_mode_summary(probe: NetworkProbeResult) -> Dict[str, object]:
    daemon = DaemonNetworkBoundaryState()
    decision = decide_network_medium(probe)
    apply_network_medium_decision(daemon, decision)

    return {
        "mode": daemon.mode,
        "medium": daemon.selected_medium,
        "allowed_payloads": sorted(daemon.allowed_payloads),
        "lora_internal": lora_is_internal_organ(),
        "reticulum_internal": reticulum_is_internal_organ(),
        "core_rails_changed": network_mode_changes_core_rails(daemon),
        "wasm_exposed": network_mode_exposes_wasm(daemon),
    }


if __name__ == "__main__":
    connected = network_mode_summary(
        NetworkProbeResult(
            internet_state="INTERNET_AVAILABLE",
            responding_probe_count=5,
            sampled_probe_count=5,
        )
    )

    degraded = network_mode_summary(
        NetworkProbeResult(
            internet_state="INTERNET_UNAVAILABLE",
            responding_probe_count=0,
            sampled_probe_count=5,
        )
    )

    print("Connected mode:", connected["mode"])
    print("Connected medium:", connected["medium"])
    print("Connected payloads:", connected["allowed_payloads"])
    print("Degraded mode:", degraded["mode"])
    print("Degraded medium:", degraded["medium"])
    print("Degraded payloads:", degraded["allowed_payloads"])
    print("LoRa internal organ:", degraded["lora_internal"])
    print("Core rails changed:", degraded["core_rails_changed"])
    print("Wasm exposed:", degraded["wasm_exposed"])
