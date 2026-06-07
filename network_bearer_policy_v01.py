"""
WHISPER v1.8.0 — Network Bearer Policy v0.1

Purpose:
Select proven external transport bearers without reimplementing them.

WHISPER does not reinvent transport protocols.

It uses proven bearers, places them behind the Daemon boundary, and preserves
Core organ invariants regardless of the selected medium.

Bearer priority:

1. PRIMARY_INTERNET
   - Reticulum + VoxMesh
   - full capabilities

2. MOBILE_DATA_4G_5G
   - Reticulum + VoxMesh
   - full capabilities

3. LORA_RNODE
   - LoRa / RNode
   - text only

Core doctrine:
Protocols carry.
WHISPER protects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Set


BearerName = Literal[
    "PRIMARY_INTERNET",
    "MOBILE_DATA_4G_5G",
    "LORA_RNODE",
]

BearerState = Literal[
    "AVAILABLE",
    "DEGRADED",
    "UNAVAILABLE",
]

BearerClass = Literal[
    "IP",
    "LOW_BANDWIDTH_RADIO",
]

BearerMode = Literal[
    "CONNECTED",
    "DEGRADED_SURVIVAL",
    "OFFLINE",
]

PayloadKind = Literal[
    "text",
    "audio",
    "image",
    "video",
    "file",
    "event",
]

TransportStack = Literal[
    "RETICULUM_VOXMESH",
    "LORA_TEXT",
    "NONE",
]


FULL_PAYLOADS: Set[str] = {
    "text",
    "audio",
    "image",
    "video",
    "file",
    "event",
}

TEXT_ONLY_PAYLOADS: Set[str] = {
    "text",
}

BEARER_PRIORITY: List[BearerName] = [
    "PRIMARY_INTERNET",
    "MOBILE_DATA_4G_5G",
    "LORA_RNODE",
]

BEARER_CLASS: Dict[BearerName, BearerClass] = {
    "PRIMARY_INTERNET": "IP",
    "MOBILE_DATA_4G_5G": "IP",
    "LORA_RNODE": "LOW_BANDWIDTH_RADIO",
}

BEARER_STACK: Dict[BearerName, TransportStack] = {
    "PRIMARY_INTERNET": "RETICULUM_VOXMESH",
    "MOBILE_DATA_4G_5G": "RETICULUM_VOXMESH",
    "LORA_RNODE": "LORA_TEXT",
}

FORBIDDEN_BEARER_PRIVILEGES: Set[str] = {
    "touch_wasm",
    "touch_membrane",
    "touch_dome",
    "touch_courier",
    "touch_bal",
    "validate_material",
    "read_payload",
    "read_core_truth",
    "read_vault",
    "read_flv",
    "change_core_rails",
    "participate_in_immunity",
}


@dataclass(frozen=True)
class BearerProbe:
    bearer: BearerName
    state: BearerState
    latency_ms: int | None = None
    packet_loss_percent: int | None = None
    stable: bool = True


@dataclass(frozen=True)
class BearerDecision:
    bearer: BearerName | None
    mode: BearerMode
    stack: TransportStack
    allowed_payloads: Set[str]
    reason: str


@dataclass(frozen=True)
class OutgoingPayload:
    payload_id: str
    kind: PayloadKind
    body: str


@dataclass
class BearerBoundaryState:
    selected_bearer: BearerName | None = None
    mode: BearerMode = "OFFLINE"
    stack: TransportStack = "NONE"
    allowed_payloads: Set[str] = field(default_factory=set)

    touched_wasm: bool = False
    touched_membrane: bool = False
    touched_dome: bool = False
    touched_courier: bool = False
    touched_bal: bool = False
    read_payload: bool = False
    changed_core_rails: bool = False
    participated_in_immunity: bool = False


def guided_link(test_name: str) -> str:
    return (
        "WHISPER_GUIDED_LINK::v1.8.0::"
        "network_bearer_policy::"
        f"{test_name}"
    )


def bearer_is_viable(probe: BearerProbe) -> bool:
    if probe.state == "UNAVAILABLE":
        return False

    if probe.stable is False:
        return False

    if probe.latency_ms is not None and probe.latency_ms < 0:
        return False

    if probe.packet_loss_percent is not None:
        if probe.packet_loss_percent < 0:
            return False
        if probe.packet_loss_percent > 50:
            return False

    return True


def select_bearer(probes: List[BearerProbe]) -> BearerDecision:
    by_name = {probe.bearer: probe for probe in probes}

    for bearer in BEARER_PRIORITY:
        probe = by_name.get(bearer)

        if probe is None:
            continue

        if not bearer_is_viable(probe):
            continue

        if bearer in {"PRIMARY_INTERNET", "MOBILE_DATA_4G_5G"}:
            return BearerDecision(
                bearer=bearer,
                mode="CONNECTED",
                stack="RETICULUM_VOXMESH",
                allowed_payloads=set(FULL_PAYLOADS),
                reason=f"{bearer.lower()}_viable",
            )

        if bearer == "LORA_RNODE":
            return BearerDecision(
                bearer=bearer,
                mode="DEGRADED_SURVIVAL",
                stack="LORA_TEXT",
                allowed_payloads=set(TEXT_ONLY_PAYLOADS),
                reason="lora_survival_text_only",
            )

    return BearerDecision(
        bearer=None,
        mode="OFFLINE",
        stack="NONE",
        allowed_payloads=set(),
        reason="no_viable_bearer",
    )


def apply_bearer_decision(
    boundary: BearerBoundaryState,
    decision: BearerDecision,
) -> BearerBoundaryState:
    boundary.selected_bearer = decision.bearer
    boundary.mode = decision.mode
    boundary.stack = decision.stack
    boundary.allowed_payloads = set(decision.allowed_payloads)

    return boundary


def payload_allowed_by_bearer(
    payload: OutgoingPayload,
    decision: BearerDecision,
) -> bool:
    return payload.kind in decision.allowed_payloads


def filter_payloads_for_bearer(
    payloads: List[OutgoingPayload],
    decision: BearerDecision,
) -> List[OutgoingPayload]:
    return [
        payload
        for payload in payloads
        if payload_allowed_by_bearer(payload, decision)
    ]


def ip_bearer_keeps_full_capabilities(decision: BearerDecision) -> bool:
    if decision.bearer not in {"PRIMARY_INTERNET", "MOBILE_DATA_4G_5G"}:
        return False

    return (
        decision.mode == "CONNECTED"
        and decision.stack == "RETICULUM_VOXMESH"
        and decision.allowed_payloads == FULL_PAYLOADS
    )


def lora_bearer_is_text_only(decision: BearerDecision) -> bool:
    if decision.bearer != "LORA_RNODE":
        return False

    return (
        decision.mode == "DEGRADED_SURVIVAL"
        and decision.stack == "LORA_TEXT"
        and decision.allowed_payloads == TEXT_ONLY_PAYLOADS
    )


def bearer_touches_internal_organs(boundary: BearerBoundaryState) -> bool:
    return (
        boundary.touched_wasm
        or boundary.touched_membrane
        or boundary.touched_dome
        or boundary.touched_courier
        or boundary.touched_bal
    )


def bearer_reads_payload(boundary: BearerBoundaryState) -> bool:
    return boundary.read_payload


def bearer_changes_core_rails(boundary: BearerBoundaryState) -> bool:
    return boundary.changed_core_rails


def bearer_participates_in_immunity(boundary: BearerBoundaryState) -> bool:
    return boundary.participated_in_immunity


def bearer_has_forbidden_privileges(boundary: BearerBoundaryState) -> bool:
    active = set()

    if boundary.touched_wasm:
        active.add("touch_wasm")
    if boundary.touched_membrane:
        active.add("touch_membrane")
    if boundary.touched_dome:
        active.add("touch_dome")
    if boundary.touched_courier:
        active.add("touch_courier")
    if boundary.touched_bal:
        active.add("touch_bal")
    if boundary.read_payload:
        active.add("read_payload")
    if boundary.changed_core_rails:
        active.add("change_core_rails")
    if boundary.participated_in_immunity:
        active.add("participate_in_immunity")

    return bool(active & FORBIDDEN_BEARER_PRIVILEGES)


def bearer_policy_summary(probes: List[BearerProbe]) -> Dict[str, object]:
    boundary = BearerBoundaryState()
    decision = select_bearer(probes)
    apply_bearer_decision(boundary, decision)

    return {
        "bearer": boundary.selected_bearer,
        "mode": boundary.mode,
        "stack": boundary.stack,
        "allowed_payloads": sorted(boundary.allowed_payloads),
        "touches_internal_organs": bearer_touches_internal_organs(boundary),
        "reads_payload": bearer_reads_payload(boundary),
        "changes_core_rails": bearer_changes_core_rails(boundary),
        "participates_in_immunity": bearer_participates_in_immunity(boundary),
        "has_forbidden_privileges": bearer_has_forbidden_privileges(boundary),
    }


if __name__ == "__main__":
    primary = bearer_policy_summary(
        [
            BearerProbe(
                bearer="PRIMARY_INTERNET",
                state="AVAILABLE",
                latency_ms=30,
                packet_loss_percent=0,
            ),
            BearerProbe(
                bearer="MOBILE_DATA_4G_5G",
                state="AVAILABLE",
                latency_ms=70,
                packet_loss_percent=1,
            ),
            BearerProbe(
                bearer="LORA_RNODE",
                state="AVAILABLE",
                latency_ms=900,
                packet_loss_percent=5,
            ),
        ]
    )

    mobile = bearer_policy_summary(
        [
            BearerProbe(
                bearer="PRIMARY_INTERNET",
                state="UNAVAILABLE",
            ),
            BearerProbe(
                bearer="MOBILE_DATA_4G_5G",
                state="AVAILABLE",
                latency_ms=80,
                packet_loss_percent=2,
            ),
            BearerProbe(
                bearer="LORA_RNODE",
                state="AVAILABLE",
                latency_ms=900,
                packet_loss_percent=5,
            ),
        ]
    )

    lora = bearer_policy_summary(
        [
            BearerProbe(
                bearer="PRIMARY_INTERNET",
                state="UNAVAILABLE",
            ),
            BearerProbe(
                bearer="MOBILE_DATA_4G_5G",
                state="UNAVAILABLE",
            ),
            BearerProbe(
                bearer="LORA_RNODE",
                state="AVAILABLE",
                latency_ms=900,
                packet_loss_percent=5,
            ),
        ]
    )

    print("Primary bearer:", primary["bearer"])
    print("Primary stack:", primary["stack"])
    print("Primary payloads:", primary["allowed_payloads"])

    print("Mobile bearer:", mobile["bearer"])
    print("Mobile stack:", mobile["stack"])
    print("Mobile payloads:", mobile["allowed_payloads"])

    print("LoRa bearer:", lora["bearer"])
    print("LoRa stack:", lora["stack"])
    print("LoRa payloads:", lora["allowed_payloads"])

    print("LoRa touches internal organs:", lora["touches_internal_organs"])
    print("LoRa changes Core rails:", lora["changes_core_rails"])
