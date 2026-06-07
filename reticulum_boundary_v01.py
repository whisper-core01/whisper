"""
WHISPER v1.8.0 — Reticulum Boundary v0.1

Purpose:
Define Reticulum as an external network layer, never as an internal WHISPER
organ.

Reticulum is outside.

The Daemon is the boundary.

The Dome handles validity and defense.

The Courier only delivers what the Dome hands off.

The Wasm never sees the network.

Core doctrine:
Reticulum carries outside.
Daemon receives/emits at the boundary.
Dome validates.
Courier delivers.
BAL retains.
Membrane passes.
Wasm transforms.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Set


BoundaryActor = Literal[
    "reticulum",
    "daemon",
    "dome",
    "courier",
    "bal_in",
    "membrane",
    "wasm",
    "bal_out",
    "transporteur",
    "network",
]

ReticulumDirection = Literal[
    "INBOUND",
    "OUTBOUND",
]

ReticulumPacketState = Literal[
    "reticulum_raw",
    "daemon_received",
    "dome_handoff_ready",
    "daemon_outbound_ready",
    "reticulum_emitted",
]

BoundaryDecision = Literal[
    "allow",
    "deny",
    "reject",
]


RETICULUM_BOUNDARY_EDGES = {
    ("reticulum", "daemon"),
    ("daemon", "reticulum"),
}

FORBIDDEN_RETICULUM_EDGES = {
    ("reticulum", "dome"),
    ("reticulum", "courier"),
    ("reticulum", "bal_in"),
    ("reticulum", "membrane"),
    ("reticulum", "wasm"),
    ("dome", "reticulum"),
    ("courier", "reticulum"),
    ("bal_in", "reticulum"),
    ("membrane", "reticulum"),
    ("wasm", "reticulum"),
}

INTERNAL_ORGANS: Set[str] = {
    "dome",
    "courier",
    "bal_in",
    "membrane",
    "wasm",
    "bal_out",
    "transporteur",
}


@dataclass(frozen=True)
class ReticulumPacket:
    packet_id: str
    direction: ReticulumDirection
    state: ReticulumPacketState
    visible_payload: str | None = None


@dataclass(frozen=True)
class DaemonInboundEnvelope:
    packet_id: str
    source: str
    state: str = "daemon_received"
    visible_payload: str | None = None


@dataclass(frozen=True)
class DaemonOutboundEnvelope:
    packet_id: str
    target: str
    state: str = "daemon_outbound_ready"
    visible_payload: str | None = None


@dataclass
class ReticulumBoundaryLedger:
    daemon_inbound_retained: Set[str] = field(default_factory=set)
    daemon_outbound_retained: Set[str] = field(default_factory=set)

    dome_acknowledged_daemon: Set[str] = field(default_factory=set)
    reticulum_acknowledged_daemon: Set[str] = field(default_factory=set)

    forbidden_attempts: List[str] = field(default_factory=list)


@dataclass
class DaemonReticulumBoundary:
    inbound_retained: Dict[str, DaemonInboundEnvelope] = field(default_factory=dict)
    outbound_retained: Dict[str, DaemonOutboundEnvelope] = field(default_factory=dict)
    touched_payload: bool = False
    decided_validity: bool = False
    participated_in_immunity: bool = False


@dataclass
class ReticulumAdapter:
    stored_core_truth: Dict[str, str] = field(default_factory=dict)
    touched_payload: bool = False
    touched_wasm: bool = False
    touched_dome: bool = False
    touched_membrane: bool = False


def guided_link(test_name: str) -> str:
    return (
        "WHISPER_GUIDED_LINK::v1.8.0::"
        "reticulum_boundary::"
        f"{test_name}"
    )


def reticulum_edge_allowed(source: BoundaryActor, target: BoundaryActor) -> bool:
    return (source, target) in RETICULUM_BOUNDARY_EDGES


def reticulum_can_reach_internal_organ(target: BoundaryActor) -> bool:
    return reticulum_edge_allowed("reticulum", target)


def wasm_can_reach_reticulum_directly() -> bool:
    return reticulum_edge_allowed("wasm", "reticulum")


def reticulum_is_internal_organ() -> bool:
    return False


def daemon_is_reticulum_interface() -> bool:
    return True


def daemon_receive_from_reticulum(
    packet: ReticulumPacket,
    daemon: DaemonReticulumBoundary,
    ledger: ReticulumBoundaryLedger,
) -> DaemonInboundEnvelope:
    if packet.direction != "INBOUND":
        raise ValueError("Daemon can only receive inbound Reticulum packets")

    if packet.state != "reticulum_raw":
        raise ValueError("Daemon can only receive raw Reticulum material")

    envelope = DaemonInboundEnvelope(
        packet_id=packet.packet_id,
        source="reticulum",
        state="daemon_received",
        visible_payload=None,
    )

    daemon.inbound_retained[packet.packet_id] = envelope
    ledger.daemon_inbound_retained.add(packet.packet_id)

    return envelope


def dome_acknowledge_daemon_inbound(
    envelope: DaemonInboundEnvelope,
    ledger: ReticulumBoundaryLedger,
) -> None:
    if envelope.state != "daemon_received":
        raise ValueError("Dome can only ACK Daemon-received material")

    ledger.dome_acknowledged_daemon.add(envelope.packet_id)


def daemon_release_after_dome_ack(
    packet_id: str,
    daemon: DaemonReticulumBoundary,
    ledger: ReticulumBoundaryLedger,
) -> bool:
    if packet_id not in ledger.dome_acknowledged_daemon:
        return False

    daemon.inbound_retained.pop(packet_id, None)
    ledger.daemon_inbound_retained.discard(packet_id)

    return True


def dome_create_handoff_for_courier(
    envelope: DaemonInboundEnvelope,
) -> ReticulumPacket:
    """
    The Dome handles validity and creates a handoff.

    The Courier does not touch validity.

    The Courier only receives the handoff.
    """
    if envelope.state != "daemon_received":
        raise ValueError("Dome can only hand off Daemon-received material")

    return ReticulumPacket(
        packet_id=envelope.packet_id,
        direction="INBOUND",
        state="dome_handoff_ready",
        visible_payload=None,
    )


def courier_accepts_only_dome_handoff(packet: ReticulumPacket) -> bool:
    return packet.state == "dome_handoff_ready"


def daemon_prepare_outbound_for_reticulum(
    envelope: DaemonOutboundEnvelope,
    daemon: DaemonReticulumBoundary,
    ledger: ReticulumBoundaryLedger,
) -> DaemonOutboundEnvelope:
    if envelope.state != "daemon_outbound_ready":
        raise ValueError("Daemon can only emit outbound-ready material")

    retained = DaemonOutboundEnvelope(
        packet_id=envelope.packet_id,
        target="reticulum",
        state="daemon_outbound_ready",
        visible_payload=None,
    )

    daemon.outbound_retained[envelope.packet_id] = retained
    ledger.daemon_outbound_retained.add(envelope.packet_id)

    return retained


def reticulum_acknowledge_daemon_outbound(
    envelope: DaemonOutboundEnvelope,
    ledger: ReticulumBoundaryLedger,
) -> None:
    if envelope.target != "reticulum":
        raise ValueError("Reticulum can only ACK its own outbound target")

    ledger.reticulum_acknowledged_daemon.add(envelope.packet_id)


def daemon_release_after_reticulum_ack(
    packet_id: str,
    daemon: DaemonReticulumBoundary,
    ledger: ReticulumBoundaryLedger,
) -> bool:
    if packet_id not in ledger.reticulum_acknowledged_daemon:
        return False

    daemon.outbound_retained.pop(packet_id, None)
    ledger.daemon_outbound_retained.discard(packet_id)

    return True


def reticulum_emit_from_daemon(
    envelope: DaemonOutboundEnvelope,
    ledger: ReticulumBoundaryLedger,
) -> ReticulumPacket:
    if envelope.target != "reticulum":
        raise ValueError("Reticulum emission requires Daemon outbound target")

    reticulum_acknowledge_daemon_outbound(envelope, ledger)

    return ReticulumPacket(
        packet_id=envelope.packet_id,
        direction="OUTBOUND",
        state="reticulum_emitted",
        visible_payload=None,
    )


def attempt_reticulum_direct_delivery(
    source: BoundaryActor,
    target: BoundaryActor,
    ledger: ReticulumBoundaryLedger | None = None,
) -> BoundaryDecision:
    if reticulum_edge_allowed(source, target):
        return "allow"

    if (source, target) in FORBIDDEN_RETICULUM_EDGES:
        if ledger is not None:
            ledger.forbidden_attempts.append(f"{source}->{target}")
        return "reject"

    return "deny"


def reticulum_failure_creates_core_shortcut() -> bool:
    return False


def reticulum_restart_changes_core_rails() -> bool:
    return False


def reticulum_adapter_stores_core_truth(adapter: ReticulumAdapter) -> bool:
    return bool(adapter.stored_core_truth)


def reticulum_adapter_touches_payload(adapter: ReticulumAdapter) -> bool:
    return adapter.touched_payload


def reticulum_adapter_touches_internal_organs(adapter: ReticulumAdapter) -> bool:
    return (
        adapter.touched_wasm
        or adapter.touched_dome
        or adapter.touched_membrane
    )


def daemon_touches_validity(daemon: DaemonReticulumBoundary) -> bool:
    return daemon.decided_validity


def daemon_participates_in_immunity(daemon: DaemonReticulumBoundary) -> bool:
    return daemon.participated_in_immunity


def daemon_touches_payload(daemon: DaemonReticulumBoundary) -> bool:
    return daemon.touched_payload


def boundary_summary() -> Dict[str, str]:
    return {
        "reticulum": "external_network_layer",
        "daemon": "network_boundary_interface",
        "dome": "validity_and_defense",
        "courier": "internal_delivery_of_dome_handoff",
        "bal": "retention",
        "membrane": "passage",
        "wasm": "isolated_transformation",
    }


if __name__ == "__main__":
    daemon = DaemonReticulumBoundary()
    ledger = ReticulumBoundaryLedger()

    packet = ReticulumPacket(
        packet_id="r-1",
        direction="INBOUND",
        state="reticulum_raw",
        visible_payload="network-payload",
    )

    inbound = daemon_receive_from_reticulum(packet, daemon, ledger)
    dome_acknowledge_daemon_inbound(inbound, ledger)
    daemon_release_after_dome_ack(inbound.packet_id, daemon, ledger)

    outbound = daemon_prepare_outbound_for_reticulum(
        DaemonOutboundEnvelope(packet_id="r-2", target="reticulum"),
        daemon,
        ledger,
    )
    emitted = reticulum_emit_from_daemon(outbound, ledger)
    daemon_release_after_reticulum_ack(emitted.packet_id, daemon, ledger)

    print("Reticulum is internal organ:", reticulum_is_internal_organ())
    print("Daemon is Reticulum interface:", daemon_is_reticulum_interface())
    print("Inbound retained:", sorted(ledger.daemon_inbound_retained))
    print("Outbound retained:", sorted(ledger.daemon_outbound_retained))
    print("Reticulum can reach Wasm:", reticulum_can_reach_internal_organ("wasm"))
    print("Wasm can reach Reticulum:", wasm_can_reach_reticulum_directly())
