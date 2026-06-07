"""
WHISPER v1.8.0 — Reticulum E2E v0.1

Purpose:
Validate Reticulum as an external network layer integrated only through the
Daemon boundary.

Reticulum is outside.
Daemon is the boundary.
Dome handles validity.
Courier delivers Dome handoff.
Wasm never sees the network.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from core_intake_isolation_v01 import (
    INBOUND_CHAIN,
    IntakeMaterial,
    intake_path_valid,
    simulate_full_intake,
)
from core_outbound_isolation_v01 import (
    OUTBOUND_CHAIN,
    OutboundMaterial,
    outbound_path_valid,
    simulate_full_outbound,
)
from reticulum_boundary_v01 import (
    DaemonOutboundEnvelope,
    DaemonReticulumBoundary,
    ReticulumBoundaryLedger,
    ReticulumPacket,
    daemon_receive_from_reticulum,
    daemon_release_after_dome_ack,
    daemon_release_after_reticulum_ack,
    dome_acknowledge_daemon_inbound,
    dome_create_handoff_for_courier,
    reticulum_emit_from_daemon,
    wasm_can_reach_reticulum_directly,
)


@dataclass(frozen=True)
class ReticulumE2EResult:
    inbound_reached_wasm: bool
    inbound_path_valid: bool
    outbound_reached_network: bool
    outbound_path_valid: bool
    reticulum_emitted: bool
    wasm_can_reach_reticulum: bool
    daemon_inbound_retained: bool
    daemon_outbound_retained: bool


def _trace(result):
    if isinstance(result, tuple):
        return result[0]
    return result


def run_reticulum_e2e() -> ReticulumE2EResult:
    daemon = DaemonReticulumBoundary()
    boundary_ledger = ReticulumBoundaryLedger()

    packet = ReticulumPacket(
        packet_id="ret-e2e-in",
        direction="INBOUND",
        state="reticulum_raw",
        visible_payload="reticulum-network-payload",
    )

    inbound = daemon_receive_from_reticulum(packet, daemon, boundary_ledger)
    dome_acknowledge_daemon_inbound(inbound, boundary_ledger)
    daemon_release_after_dome_ack(inbound.packet_id, daemon, boundary_ledger)

    handoff = dome_create_handoff_for_courier(inbound)

    intake_trace = _trace(
        simulate_full_intake(
            IntakeMaterial(
                material_id=handoff.packet_id,
                state="external_raw",
                valid=True,
                visible_payload="external-payload",
            )
        )
    )

    outbound_trace, outbound_ledger = simulate_full_outbound(
        OutboundMaterial(
            material_id="ret-e2e-out",
            state="wasm_output",
            valid=True,
            visible_payload="wasm-payload",
        )
    )

    outbound_envelope = DaemonOutboundEnvelope(
        packet_id="ret-e2e-out",
        target="reticulum",
    )

    emitted = reticulum_emit_from_daemon(outbound_envelope, boundary_ledger)
    daemon_release_after_reticulum_ack(emitted.packet_id, daemon, boundary_ledger)

    return ReticulumE2EResult(
        inbound_reached_wasm=intake_trace.reached_wasm,
        inbound_path_valid=intake_trace.path == INBOUND_CHAIN and intake_path_valid(intake_trace),
        outbound_reached_network=outbound_trace.reached_network,
        outbound_path_valid=outbound_trace.path == OUTBOUND_CHAIN and outbound_path_valid(outbound_trace),
        reticulum_emitted=emitted.state == "reticulum_emitted",
        wasm_can_reach_reticulum=wasm_can_reach_reticulum_directly(),
        daemon_inbound_retained=bool(boundary_ledger.daemon_inbound_retained),
        daemon_outbound_retained=bool(boundary_ledger.daemon_outbound_retained),
    )


def reticulum_e2e_summary() -> Dict[str, bool]:
    result = run_reticulum_e2e()

    return {
        "inbound_reached_wasm": result.inbound_reached_wasm,
        "inbound_path_valid": result.inbound_path_valid,
        "outbound_reached_network": result.outbound_reached_network,
        "outbound_path_valid": result.outbound_path_valid,
        "reticulum_emitted": result.reticulum_emitted,
        "wasm_can_reach_reticulum": result.wasm_can_reach_reticulum,
        "daemon_inbound_retained": result.daemon_inbound_retained,
        "daemon_outbound_retained": result.daemon_outbound_retained,
    }


if __name__ == "__main__":
    summary = reticulum_e2e_summary()

    print("Reticulum inbound reached Wasm:", summary["inbound_reached_wasm"])
    print("Inbound path valid:", summary["inbound_path_valid"])
    print("Outbound reached network:", summary["outbound_reached_network"])
    print("Outbound path valid:", summary["outbound_path_valid"])
    print("Reticulum emitted:", summary["reticulum_emitted"])
    print("Wasm can reach Reticulum:", summary["wasm_can_reach_reticulum"])
    print("Daemon inbound retained:", summary["daemon_inbound_retained"])
    print("Daemon outbound retained:", summary["daemon_outbound_retained"])
