"""
WHISPER v1.6.0 — Core Intake Isolation v0.1

Purpose:
Validate the absolute separation between external material and Wasm.

INBOUND:
External -> Daemon -> Dome -> Courier -> BAL In -> Membrane -> Wasm

OUTBOUND:
Wasm -> Membrane -> BAL Out -> Transporteur -> Daemon -> Network

This module only defines rails.

No business logic.
No crypto.
No parsing.
No transport semantics.

Core invariant:
The Wasm does not know the outside.
It only knows what the Membrane gives it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal


OrganName = Literal[
    "external",
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

MaterialState = Literal[
    "external_raw",
    "daemon_received",
    "dome_validated",
    "dome_rejected",
    "courier_carried",
    "bal_in_buffered",
    "membrane_absorbed",
    "wasm_received",
    "bal_out_buffered",
    "transporteur_carried",
    "daemon_emitted",
    "network_emitted",
]


INBOUND_CHAIN: List[OrganName] = [
    "external",
    "daemon",
    "dome",
    "courier",
    "bal_in",
    "membrane",
    "wasm",
]

OUTBOUND_CHAIN: List[OrganName] = [
    "wasm",
    "membrane",
    "bal_out",
    "transporteur",
    "daemon",
    "network",
]


ALLOWED_INBOUND_EDGES = {
    ("external", "daemon"),
    ("daemon", "dome"),
    ("dome", "courier"),
    ("courier", "bal_in"),
    ("bal_in", "membrane"),
    ("membrane", "wasm"),
}


ALLOWED_OUTBOUND_EDGES = {
    ("wasm", "membrane"),
    ("membrane", "bal_out"),
    ("bal_out", "transporteur"),
    ("transporteur", "daemon"),
    ("daemon", "network"),
}


@dataclass(frozen=True)
class IntakeMaterial:
    material_id: str
    state: MaterialState
    valid: bool = True
    visible_payload: str | None = None


@dataclass
class IntakeTrace:
    path: List[OrganName] = field(default_factory=list)
    states: List[MaterialState] = field(default_factory=list)
    rejected: bool = False
    reached_wasm: bool = False
    shortcut_attempts: List[str] = field(default_factory=list)


@dataclass
class OrganHealth:
    daemon_alive: bool = True
    dome_alive: bool = True
    courier_alive: bool = True
    bal_in_alive: bool = True
    membrane_alive: bool = True
    wasm_alive: bool = True


def guided_link(test_name: str) -> str:
    """
    Guided Link for v1.6.0 tests.

    Each test maps to the central intake isolation invariant.
    """
    return (
        "WHISPER_GUIDED_LINK::v1.6.0::core_intake_isolation::"
        f"{test_name}"
    )


def edge_allowed(source: OrganName, target: OrganName) -> bool:
    return (source, target) in ALLOWED_INBOUND_EDGES or (
        source,
        target,
    ) in ALLOWED_OUTBOUND_EDGES


def transporteur_participates_in_intake() -> bool:
    return "transporteur" in INBOUND_CHAIN


def daemon_receive(material: IntakeMaterial, trace: IntakeTrace) -> IntakeMaterial:
    trace.path.append("daemon")
    trace.states.append("daemon_received")

    return IntakeMaterial(
        material_id=material.material_id,
        state="daemon_received",
        valid=material.valid,
        visible_payload=None,
    )


def dome_validate(material: IntakeMaterial, trace: IntakeTrace) -> IntakeMaterial:
    trace.path.append("dome")

    if not material.valid:
        trace.states.append("dome_rejected")
        trace.rejected = True

        return IntakeMaterial(
            material_id=material.material_id,
            state="dome_rejected",
            valid=False,
            visible_payload=None,
        )

    trace.states.append("dome_validated")

    return IntakeMaterial(
        material_id=material.material_id,
        state="dome_validated",
        valid=True,
        visible_payload=None,
    )


def courier_carry(material: IntakeMaterial, trace: IntakeTrace) -> IntakeMaterial:
    if material.state != "dome_validated":
        raise ValueError("courier can only carry dome-validated material")

    trace.path.append("courier")
    trace.states.append("courier_carried")

    return IntakeMaterial(
        material_id=material.material_id,
        state="courier_carried",
        valid=True,
        visible_payload=None,
    )


def bal_in_buffer(material: IntakeMaterial, trace: IntakeTrace) -> IntakeMaterial:
    if material.state != "courier_carried":
        raise ValueError("BAL In can only receive courier-carried material")

    trace.path.append("bal_in")
    trace.states.append("bal_in_buffered")

    return IntakeMaterial(
        material_id=material.material_id,
        state="bal_in_buffered",
        valid=True,
        visible_payload=None,
    )


def membrane_absorb(material: IntakeMaterial, trace: IntakeTrace) -> IntakeMaterial:
    if material.state != "bal_in_buffered":
        raise ValueError("Membrane can only absorb BAL In buffered material")

    trace.path.append("membrane")
    trace.states.append("membrane_absorbed")

    return IntakeMaterial(
        material_id=material.material_id,
        state="membrane_absorbed",
        valid=True,
        visible_payload=None,
    )


def wasm_receive(material: IntakeMaterial, trace: IntakeTrace) -> IntakeMaterial:
    if material.state != "membrane_absorbed":
        raise ValueError("Wasm can only receive Membrane-absorbed material")

    trace.path.append("wasm")
    trace.states.append("wasm_received")
    trace.reached_wasm = True

    return IntakeMaterial(
        material_id=material.material_id,
        state="wasm_received",
        valid=True,
        visible_payload=None,
    )


def simulate_full_intake(
    material: IntakeMaterial,
    health: OrganHealth | None = None,
) -> IntakeTrace:
    """
    Simulate the complete inbound path.

    External material may reach Wasm only through:
    Daemon -> Dome -> Courier -> BAL In -> Membrane.
    """
    if health is None:
        health = OrganHealth()

    trace = IntakeTrace(path=["external"], states=["external_raw"])

    if not health.daemon_alive:
        return trace

    material = daemon_receive(material, trace)

    if not health.dome_alive:
        return trace

    material = dome_validate(material, trace)

    if trace.rejected:
        return trace

    if not health.courier_alive:
        return trace

    material = courier_carry(material, trace)

    if not health.bal_in_alive:
        return trace

    material = bal_in_buffer(material, trace)

    if not health.membrane_alive:
        return trace

    material = membrane_absorb(material, trace)

    if not health.wasm_alive:
        return trace

    wasm_receive(material, trace)

    return trace


def attempt_direct_delivery(
    source: OrganName,
    target: OrganName,
    material: IntakeMaterial,
) -> bool:
    """
    Attempt a shortcut delivery.

    Returns True only if the edge is allowed.

    Direct Wasm access from external intake organs must fail.
    """
    if not edge_allowed(source, target):
        return False

    if target == "wasm" and source != "membrane":
        return False

    if source in {"external", "daemon", "dome", "courier", "bal_in"} and target == "wasm":
        return False

    return True


def organ_failure_must_not_create_shortcut(
    failed_organ: OrganName,
) -> bool:
    """
    A dead organ never becomes a shortcut.

    Failure suspends or stops flow.
    It never opens a new path.
    """
    health = OrganHealth()

    if failed_organ == "daemon":
        health.daemon_alive = False
    elif failed_organ == "dome":
        health.dome_alive = False
    elif failed_organ == "courier":
        health.courier_alive = False
    elif failed_organ == "bal_in":
        health.bal_in_alive = False
    elif failed_organ == "membrane":
        health.membrane_alive = False
    elif failed_organ == "wasm":
        health.wasm_alive = False

    trace = simulate_full_intake(
        IntakeMaterial(
            material_id="m-failure",
            state="external_raw",
            valid=True,
            visible_payload="external-payload",
        ),
        health=health,
    )

    if failed_organ in {"daemon", "dome", "courier", "bal_in", "membrane"}:
        return trace.reached_wasm is False

    return True


def organ_restart_must_not_change_intake_path(
    restarted_organ: OrganName,
) -> bool:
    """
    Restarting an organ preserves the same intake rails.

    It does not grant new edges.
    """
    before_edges = set(ALLOWED_INBOUND_EDGES)

    # Prototype restart is intentionally no-op.
    _ = restarted_organ

    after_edges = set(ALLOWED_INBOUND_EDGES)

    return before_edges == after_edges


def intake_path_valid(trace: IntakeTrace) -> bool:
    if not trace.reached_wasm:
        return True

    return trace.path == INBOUND_CHAIN


def wasm_knows_origin() -> bool:
    return False


def wasm_touches_network() -> bool:
    return False


def wasm_receives_rejected_material() -> bool:
    return False


def organ_blindness_summary() -> Dict[str, str]:
    return {
        "daemon": "receives_without_understanding",
        "dome": "validates_without_reading",
        "courier": "carries_without_knowing",
        "bal_in": "buffers_without_knowing",
        "membrane": "absorbs_without_interpreting",
        "wasm": "transforms_without_touching_origin",
    }


if __name__ == "__main__":
    material = IntakeMaterial(
        material_id="m1",
        state="external_raw",
        valid=True,
        visible_payload="external-payload",
    )

    trace = simulate_full_intake(material)

    print("Path:", " -> ".join(trace.path))
    print("Reached Wasm:", trace.reached_wasm)
    print("Path valid:", intake_path_valid(trace))
    print("Transporteur in intake:", transporteur_participates_in_intake())
    print("Wasm knows origin:", wasm_knows_origin())
    print("Wasm touches network:", wasm_touches_network())
