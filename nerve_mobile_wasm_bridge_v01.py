"""
WHISPER — Nerve Mobile Wasm Bridge v0.1

Purpose:
Define the host/Wasm boundary for Nerve Mobile.

The Wasm may request.

The host filters.

The nerve must never escape its role.

Allowed host calls:
- load Mobile Vault during boot only
- close Mobile Vault
- zeroize admission buffers
- emit Sol impulse
- poll Sol response
- request sensor permission

Forbidden host calls:
- open Vault during runtime
- read Core Vault
- read FLV
- read identity
- read session
- read keys
- configure network
- derive WHISPER crypto

Core rule:
The bridge is not a privilege escalation layer.

It is a membrane.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal


BridgePhase = Literal["BOOT", "RUNTIME", "CLOSED"]

HostCallName = Literal[
    "load_mobile_vault_boot",
    "close_mobile_vault",
    "zeroize_admission_buffers",
    "emit_sol_impulse",
    "poll_sol_response",
    "request_sensor_permission",
    "open_vault_runtime",
    "read_core_vault",
    "read_flv",
    "read_identity",
    "read_session",
    "read_keys",
    "configure_network",
    "derive_whisper_crypto",
]

HostCallStatus = Literal["allowed", "denied"]


ALLOWED_HOST_CALLS = {
    "load_mobile_vault_boot",
    "close_mobile_vault",
    "zeroize_admission_buffers",
    "emit_sol_impulse",
    "poll_sol_response",
    "request_sensor_permission",
}

FORBIDDEN_HOST_CALLS = {
    "open_vault_runtime",
    "read_core_vault",
    "read_flv",
    "read_identity",
    "read_session",
    "read_keys",
    "configure_network",
    "derive_whisper_crypto",
}


@dataclass(frozen=True)
class HostCallRequest:
    name: HostCallName
    payload: Dict[str, Any]


@dataclass(frozen=True)
class HostCallResult:
    status: HostCallStatus
    name: str
    payload: Dict[str, Any]
    error: str | None = None


@dataclass
class WasmBridgeState:
    phase: BridgePhase = "BOOT"
    vault_open: bool = False
    vault_open_count: int = 0
    vault_close_count: int = 0
    zeroize_count: int = 0
    sol_emit_count: int = 0
    sol_poll_count: int = 0
    permission_request_count: int = 0
    denied_calls: List[str] = field(default_factory=list)
    successful_forbidden_calls: List[str] = field(default_factory=list)
    stored_state: Dict[str, Any] = field(default_factory=dict)


def authorize_host_call(
    state: WasmBridgeState,
    request: HostCallRequest,
) -> bool:
    """
    Authorize a Wasm host call.

    Authorization is phase-bound.

    Vault loading is boot-only.

    Runtime Vault opening is always forbidden.
    """
    if request.name in FORBIDDEN_HOST_CALLS:
        return False

    if request.name not in ALLOWED_HOST_CALLS:
        return False

    if request.name == "load_mobile_vault_boot":
        return state.phase == "BOOT" and state.vault_open is False

    if request.name == "close_mobile_vault":
        return state.phase == "BOOT" and state.vault_open is True

    if request.name == "zeroize_admission_buffers":
        return state.phase == "BOOT"

    if request.name in {"emit_sol_impulse", "poll_sol_response"}:
        return state.phase == "RUNTIME" and state.vault_open is False

    if request.name == "request_sensor_permission":
        return state.vault_open is False

    return False


def execute_host_call(
    state: WasmBridgeState,
    request: HostCallRequest,
) -> HostCallResult:
    """
    Execute an authorized host call.

    Prototype only.

    This models the Wasm/host boundary and its invariants.
    """
    allowed = authorize_host_call(state, request)

    if not allowed:
        state.denied_calls.append(request.name)

        if request.name in FORBIDDEN_HOST_CALLS:
            return HostCallResult(
                status="denied",
                name=request.name,
                payload={},
                error="forbidden_host_call",
            )

        return HostCallResult(
            status="denied",
            name=request.name,
            payload={},
            error="host_call_not_allowed_in_phase",
        )

    if request.name == "load_mobile_vault_boot":
        state.vault_open = True
        state.vault_open_count += 1

        return HostCallResult(
            status="allowed",
            name=request.name,
            payload={
                "origin_hint": "loaded",
                "nerve_local_material": "loaded",
                "birth_epoch": "loaded",
                "last_seen_epoch": "loaded",
            },
        )

    if request.name == "close_mobile_vault":
        state.vault_open = False
        state.vault_close_count += 1

        return HostCallResult(
            status="allowed",
            name=request.name,
            payload={"vault_closed": True},
        )

    if request.name == "zeroize_admission_buffers":
        state.zeroize_count += 1

        return HostCallResult(
            status="allowed",
            name=request.name,
            payload={"buffers_zeroized": True},
        )

    if request.name == "emit_sol_impulse":
        state.sol_emit_count += 1

        return HostCallResult(
            status="allowed",
            name=request.name,
            payload={"emitted": True},
        )

    if request.name == "poll_sol_response":
        state.sol_poll_count += 1

        return HostCallResult(
            status="allowed",
            name=request.name,
            payload={"response": None},
        )

    if request.name == "request_sensor_permission":
        state.permission_request_count += 1

        return HostCallResult(
            status="allowed",
            name=request.name,
            payload={"permission_requested": request.payload.get("permission")},
        )

    return HostCallResult(
        status="denied",
        name=request.name,
        payload={},
        error="unhandled_host_call",
    )


def transition_to_runtime(state: WasmBridgeState) -> None:
    """
    Move from BOOT to RUNTIME.

    The Vault must be closed first.
    """
    if state.phase != "BOOT":
        raise ValueError("bridge must be in BOOT phase")

    if state.vault_open:
        raise ValueError("cannot enter RUNTIME with Mobile Vault open")

    state.phase = "RUNTIME"


def close_bridge(state: WasmBridgeState) -> None:
    if state.vault_open:
        raise ValueError("cannot close bridge with Mobile Vault open")

    state.phase = "CLOSED"


def wasm_bridge_invariants_ok(state: WasmBridgeState) -> bool:
    """
    Verify bridge invariants.

    Runtime must not have an open Vault.

    Forbidden calls must never succeed.

    The bridge must not store sovereign state.
    """
    if state.phase == "RUNTIME" and state.vault_open:
        return False

    if state.successful_forbidden_calls:
        return False

    if state.stored_state:
        return False

    return True


def bridge_affects_admission() -> bool:
    return False


def bridge_affects_identity() -> bool:
    return False


def bridge_exposes_core_secrets() -> bool:
    return False


if __name__ == "__main__":
    state = WasmBridgeState()

    load = execute_host_call(
        state,
        HostCallRequest(
            name="load_mobile_vault_boot",
            payload={},
        ),
    )

    close = execute_host_call(
        state,
        HostCallRequest(
            name="close_mobile_vault",
            payload={},
        ),
    )

    zeroize = execute_host_call(
        state,
        HostCallRequest(
            name="zeroize_admission_buffers",
            payload={},
        ),
    )

    transition_to_runtime(state)

    emit = execute_host_call(
        state,
        HostCallRequest(
            name="emit_sol_impulse",
            payload={"kind": "input"},
        ),
    )

    forbidden = execute_host_call(
        state,
        HostCallRequest(
            name="read_core_vault",
            payload={},
        ),
    )

    print("Load Vault:", load.status)
    print("Close Vault:", close.payload)
    print("Zeroize:", zeroize.payload)
    print("Runtime emit:", emit.status)
    print("Forbidden read Core Vault:", forbidden.status)
    print("Bridge phase:", state.phase)
    print("Vault open:", state.vault_open)
    print("Invariants OK:", wasm_bridge_invariants_ok(state))
