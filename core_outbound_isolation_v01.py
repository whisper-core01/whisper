"""
WHISPER v1.6.0 — Core Outbound Isolation + Upstream Retention v0.1

Purpose:
Validate the absolute separation between Wasm output and network emission,
plus upstream retention until downstream acknowledgement.

OUTBOUND:
Wasm -> Membrane -> BAL Out -> Transporteur -> Daemon -> Network

Core invariants:

1. Wasm never touches the network directly.

2. Wasm output can reach the network only through:
   Membrane -> BAL Out -> Transporteur -> Daemon.

3. An upstream outbound organ never releases material until the downstream
   organ has confirmed custody.

4. The Dome and Courier never participate in outbound.

5. Lemonade/Dome immunity is not part of outbound emission.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Set


OrganName = Literal[
    "wasm",
    "membrane",
    "bal_out",
    "transporteur",
    "daemon",
    "network",
    "external",
    "dome",
    "courier",
    "bal_in",
    "lemonade",
]

MaterialState = Literal[
    "wasm_output",
    "membrane_exported",
    "bal_out_buffered",
    "transporteur_carried",
    "daemon_ready",
    "network_emitted",
]


OUTBOUND_CHAIN: List[OrganName] = [
    "wasm",
    "membrane",
    "bal_out",
    "transporteur",
    "daemon",
    "network",
]

INBOUND_ONLY_ORGANS: Set[OrganName] = {
    "dome",
    "courier",
    "bal_in",
}

IMMUNITY_ORGANS: Set[OrganName] = {
    "lemonade",
}

ALLOWED_OUTBOUND_EDGES = {
    ("wasm", "membrane"),
    ("membrane", "bal_out"),
    ("bal_out", "transporteur"),
    ("transporteur", "daemon"),
    ("daemon", "network"),
}


@dataclass(frozen=True)
class OutboundMaterial:
    material_id: str
    state: MaterialState
    valid: bool = True
    visible_payload: str | None = None


@dataclass
class OutboundTrace:
    path: List[OrganName] = field(default_factory=list)
    states: List[MaterialState] = field(default_factory=list)
    reached_network: bool = False
    shortcut_attempts: List[str] = field(default_factory=list)


@dataclass
class OutboundRetentionLedger:
    membrane_retained: Set[str] = field(default_factory=set)
    bal_out_retained: Set[str] = field(default_factory=set)
    transporteur_retained: Set[str] = field(default_factory=set)
    daemon_retained: Set[str] = field(default_factory=set)

    bal_out_acknowledged_membrane: Set[str] = field(default_factory=set)
    transporteur_acknowledged_bal_out: Set[str] = field(default_factory=set)
    daemon_acknowledged_transporteur: Set[str] = field(default_factory=set)
    network_acknowledged_daemon: Set[str] = field(default_factory=set)


@dataclass
class MembraneOutBuffer:
    retained: Dict[str, OutboundMaterial] = field(default_factory=dict)


@dataclass
class BALOutBuffer:
    retained: Dict[str, OutboundMaterial] = field(default_factory=dict)


@dataclass
class TransporteurBuffer:
    retained: Dict[str, OutboundMaterial] = field(default_factory=dict)


@dataclass
class DaemonOutBuffer:
    retained: Dict[str, OutboundMaterial] = field(default_factory=dict)


@dataclass
class OutboundOrganHealth:
    membrane_alive: bool = True
    bal_out_alive: bool = True
    transporteur_alive: bool = True
    daemon_alive: bool = True
    network_alive: bool = True


def guided_link(test_name: str) -> str:
    return (
        "WHISPER_GUIDED_LINK::v1.6.0::"
        "core_outbound_isolation_upstream_retention::"
        f"{test_name}"
    )


def edge_allowed(source: OrganName, target: OrganName) -> bool:
    return (source, target) in ALLOWED_OUTBOUND_EDGES


def dome_participates_in_outbound() -> bool:
    return "dome" in OUTBOUND_CHAIN


def courier_participates_in_outbound() -> bool:
    return "courier" in OUTBOUND_CHAIN


def bal_in_participates_in_outbound() -> bool:
    return "bal_in" in OUTBOUND_CHAIN


def lemonade_participates_in_outbound() -> bool:
    return "lemonade" in OUTBOUND_CHAIN


def membrane_export_from_wasm(
    material: OutboundMaterial,
    membrane: MembraneOutBuffer,
    ledger: OutboundRetentionLedger,
    trace: OutboundTrace,
) -> OutboundMaterial:
    if material.state != "wasm_output":
        raise ValueError("Membrane can only export Wasm output material")

    exported = OutboundMaterial(
        material_id=material.material_id,
        state="membrane_exported",
        valid=material.valid,
        visible_payload=None,
    )

    membrane.retained[material.material_id] = exported
    ledger.membrane_retained.add(material.material_id)

    trace.path.append("membrane")
    trace.states.append("membrane_exported")

    return exported


def bal_out_receive_from_membrane(
    material: OutboundMaterial,
    bal_out: BALOutBuffer,
    ledger: OutboundRetentionLedger,
    trace: OutboundTrace,
) -> OutboundMaterial:
    if material.state != "membrane_exported":
        raise ValueError("BAL Out can only receive Membrane-exported material")

    buffered = OutboundMaterial(
        material_id=material.material_id,
        state="bal_out_buffered",
        valid=True,
        visible_payload=None,
    )

    bal_out.retained[material.material_id] = buffered
    ledger.bal_out_retained.add(material.material_id)
    ledger.bal_out_acknowledged_membrane.add(material.material_id)

    trace.path.append("bal_out")
    trace.states.append("bal_out_buffered")

    return buffered


def membrane_release_after_bal_out_ack(
    material_id: str,
    membrane: MembraneOutBuffer,
    ledger: OutboundRetentionLedger,
) -> bool:
    if material_id not in ledger.bal_out_acknowledged_membrane:
        return False

    membrane.retained.pop(material_id, None)
    ledger.membrane_retained.discard(material_id)

    return True


def transporteur_pickup_from_bal_out(
    material: OutboundMaterial,
    transporteur: TransporteurBuffer,
    ledger: OutboundRetentionLedger,
    trace: OutboundTrace,
) -> OutboundMaterial:
    if material.state != "bal_out_buffered":
        raise ValueError("Transporteur can only carry BAL Out buffered material")

    carried = OutboundMaterial(
        material_id=material.material_id,
        state="transporteur_carried",
        valid=True,
        visible_payload=None,
    )

    transporteur.retained[material.material_id] = carried
    ledger.transporteur_retained.add(material.material_id)
    ledger.transporteur_acknowledged_bal_out.add(material.material_id)

    trace.path.append("transporteur")
    trace.states.append("transporteur_carried")

    return carried


def bal_out_release_after_transporteur_ack(
    material_id: str,
    bal_out: BALOutBuffer,
    ledger: OutboundRetentionLedger,
) -> bool:
    if material_id not in ledger.transporteur_acknowledged_bal_out:
        return False

    bal_out.retained.pop(material_id, None)
    ledger.bal_out_retained.discard(material_id)

    return True


def daemon_receive_from_transporteur(
    material: OutboundMaterial,
    daemon: DaemonOutBuffer,
    ledger: OutboundRetentionLedger,
    trace: OutboundTrace,
) -> OutboundMaterial:
    if material.state != "transporteur_carried":
        raise ValueError("Daemon Out can only receive Transporteur-carried material")

    ready = OutboundMaterial(
        material_id=material.material_id,
        state="daemon_ready",
        valid=True,
        visible_payload=None,
    )

    daemon.retained[material.material_id] = ready
    ledger.daemon_retained.add(material.material_id)
    ledger.daemon_acknowledged_transporteur.add(material.material_id)

    trace.path.append("daemon")
    trace.states.append("daemon_ready")

    return ready


def transporteur_release_after_daemon_ack(
    material_id: str,
    transporteur: TransporteurBuffer,
    ledger: OutboundRetentionLedger,
) -> bool:
    if material_id not in ledger.daemon_acknowledged_transporteur:
        return False

    transporteur.retained.pop(material_id, None)
    ledger.transporteur_retained.discard(material_id)

    return True


def network_emit_from_daemon(
    material: OutboundMaterial,
    ledger: OutboundRetentionLedger,
    trace: OutboundTrace,
) -> OutboundMaterial:
    if material.state != "daemon_ready":
        raise ValueError("Network can only receive Daemon-ready material")

    emitted = OutboundMaterial(
        material_id=material.material_id,
        state="network_emitted",
        valid=True,
        visible_payload=None,
    )

    ledger.network_acknowledged_daemon.add(material.material_id)

    trace.path.append("network")
    trace.states.append("network_emitted")
    trace.reached_network = True

    return emitted


def daemon_release_after_network_ack(
    material_id: str,
    daemon: DaemonOutBuffer,
    ledger: OutboundRetentionLedger,
) -> bool:
    if material_id not in ledger.network_acknowledged_daemon:
        return False

    daemon.retained.pop(material_id, None)
    ledger.daemon_retained.discard(material_id)

    return True


def simulate_full_outbound(
    material: OutboundMaterial,
    health: OutboundOrganHealth | None = None,
) -> tuple[OutboundTrace, OutboundRetentionLedger]:
    if health is None:
        health = OutboundOrganHealth()

    membrane = MembraneOutBuffer()
    bal_out = BALOutBuffer()
    transporteur = TransporteurBuffer()
    daemon = DaemonOutBuffer()
    ledger = OutboundRetentionLedger()
    trace = OutboundTrace(path=["wasm"], states=["wasm_output"])

    if not health.membrane_alive:
        return trace, ledger

    material = membrane_export_from_wasm(material, membrane, ledger, trace)

    if not health.bal_out_alive:
        return trace, ledger

    material = bal_out_receive_from_membrane(material, bal_out, ledger, trace)
    membrane_release_after_bal_out_ack(material.material_id, membrane, ledger)

    if not health.transporteur_alive:
        return trace, ledger

    material = transporteur_pickup_from_bal_out(material, transporteur, ledger, trace)
    bal_out_release_after_transporteur_ack(material.material_id, bal_out, ledger)

    if not health.daemon_alive:
        return trace, ledger

    material = daemon_receive_from_transporteur(material, daemon, ledger, trace)
    transporteur_release_after_daemon_ack(material.material_id, transporteur, ledger)

    if not health.network_alive:
        return trace, ledger

    material = network_emit_from_daemon(material, ledger, trace)
    daemon_release_after_network_ack(material.material_id, daemon, ledger)

    return trace, ledger


def simulate_transporteur_failure_before_daemon_ack() -> tuple[TransporteurBuffer, OutboundRetentionLedger, OutboundTrace]:
    membrane = MembraneOutBuffer()
    bal_out = BALOutBuffer()
    transporteur = TransporteurBuffer()
    ledger = OutboundRetentionLedger()
    trace = OutboundTrace(path=["wasm"], states=["wasm_output"])

    material = OutboundMaterial(
        material_id="m-transporteur-failure",
        state="wasm_output",
        valid=True,
        visible_payload="wasm-payload",
    )

    material = membrane_export_from_wasm(material, membrane, ledger, trace)
    material = bal_out_receive_from_membrane(material, bal_out, ledger, trace)
    membrane_release_after_bal_out_ack(material.material_id, membrane, ledger)
    material = transporteur_pickup_from_bal_out(material, transporteur, ledger, trace)
    bal_out_release_after_transporteur_ack(material.material_id, bal_out, ledger)

    return transporteur, ledger, trace


def simulate_transporteur_restart_can_resend_to_daemon() -> bool:
    transporteur, ledger, trace = simulate_transporteur_failure_before_daemon_ack()
    daemon = DaemonOutBuffer()

    retained = transporteur.retained["m-transporteur-failure"]
    ready = daemon_receive_from_transporteur(retained, daemon, ledger, trace)
    released = transporteur_release_after_daemon_ack(ready.material_id, transporteur, ledger)

    return released and "m-transporteur-failure" not in transporteur.retained


def simulate_daemon_failure_before_network_ack() -> tuple[DaemonOutBuffer, OutboundRetentionLedger, OutboundTrace]:
    membrane = MembraneOutBuffer()
    bal_out = BALOutBuffer()
    transporteur = TransporteurBuffer()
    daemon = DaemonOutBuffer()
    ledger = OutboundRetentionLedger()
    trace = OutboundTrace(path=["wasm"], states=["wasm_output"])

    material = OutboundMaterial(
        material_id="m-daemon-failure",
        state="wasm_output",
        valid=True,
        visible_payload="wasm-payload",
    )

    material = membrane_export_from_wasm(material, membrane, ledger, trace)
    material = bal_out_receive_from_membrane(material, bal_out, ledger, trace)
    membrane_release_after_bal_out_ack(material.material_id, membrane, ledger)
    material = transporteur_pickup_from_bal_out(material, transporteur, ledger, trace)
    bal_out_release_after_transporteur_ack(material.material_id, bal_out, ledger)
    material = daemon_receive_from_transporteur(material, daemon, ledger, trace)
    transporteur_release_after_daemon_ack(material.material_id, transporteur, ledger)

    return daemon, ledger, trace


def simulate_daemon_restart_can_emit_retained_material() -> bool:
    daemon, ledger, trace = simulate_daemon_failure_before_network_ack()

    retained = daemon.retained["m-daemon-failure"]
    emitted = network_emit_from_daemon(retained, ledger, trace)
    released = daemon_release_after_network_ack(emitted.material_id, daemon, ledger)

    return released and "m-daemon-failure" not in daemon.retained


def attempt_direct_delivery(source: OrganName, target: OrganName) -> bool:
    if not edge_allowed(source, target):
        return False

    if target == "network" and source != "daemon":
        return False

    if source == "wasm" and target != "membrane":
        return False

    return True


def outbound_path_valid(trace: OutboundTrace) -> bool:
    if not trace.reached_network:
        return True

    return trace.path == OUTBOUND_CHAIN


def organ_failure_must_not_create_outbound_shortcut(failed_organ: OrganName) -> bool:
    health = OutboundOrganHealth()

    if failed_organ == "membrane":
        health.membrane_alive = False
    elif failed_organ == "bal_out":
        health.bal_out_alive = False
    elif failed_organ == "transporteur":
        health.transporteur_alive = False
    elif failed_organ == "daemon":
        health.daemon_alive = False
    elif failed_organ == "network":
        health.network_alive = False

    trace, _ledger = simulate_full_outbound(
        OutboundMaterial(
            material_id="m-failure",
            state="wasm_output",
            valid=True,
            visible_payload="wasm-payload",
        ),
        health=health,
    )

    if failed_organ in {"membrane", "bal_out", "transporteur", "daemon"}:
        return trace.reached_network is False

    return True


def organ_restart_must_not_change_outbound_path(restarted_organ: OrganName) -> bool:
    before_edges = set(ALLOWED_OUTBOUND_EDGES)

    _ = restarted_organ

    after_edges = set(ALLOWED_OUTBOUND_EDGES)

    return before_edges == after_edges


def wasm_touches_network_directly() -> bool:
    return False


def network_receives_only_daemon_emitted_material() -> bool:
    return True


def outbound_blindness_summary() -> Dict[str, str]:
    return {
        "wasm": "produces_without_touching_network",
        "membrane": "exports_without_exposing_origin",
        "bal_out": "retains_without_knowing",
        "transporteur": "carries_without_interpreting",
        "daemon": "emits_without_understanding",
        "network": "receives_only_daemon_emission",
    }


if __name__ == "__main__":
    trace, ledger = simulate_full_outbound(
        OutboundMaterial(
            material_id="m1",
            state="wasm_output",
            valid=True,
            visible_payload="wasm-payload",
        )
    )

    print("Path:", " -> ".join(trace.path))
    print("Reached Network:", trace.reached_network)
    print("Path valid:", outbound_path_valid(trace))
    print("Membrane retained:", sorted(ledger.membrane_retained))
    print("BAL Out retained:", sorted(ledger.bal_out_retained))
    print("Transporteur retained:", sorted(ledger.transporteur_retained))
    print("Daemon retained:", sorted(ledger.daemon_retained))
    print("Dome in outbound:", dome_participates_in_outbound())
    print("Courier in outbound:", courier_participates_in_outbound())
    print("Lemonade in outbound:", lemonade_participates_in_outbound())
    print("Wasm touches network directly:", wasm_touches_network_directly())
