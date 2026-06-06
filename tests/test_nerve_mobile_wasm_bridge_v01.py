from nerve_mobile_wasm_bridge_v01 import (
    FORBIDDEN_HOST_CALLS,
    HostCallRequest,
    WasmBridgeState,
    authorize_host_call,
    bridge_affects_admission,
    bridge_affects_identity,
    bridge_exposes_core_secrets,
    close_bridge,
    execute_host_call,
    transition_to_runtime,
    wasm_bridge_invariants_ok,
)


def test_load_vault_allowed_only_during_boot():
    state = WasmBridgeState()

    request = HostCallRequest(
        name="load_mobile_vault_boot",
        payload={},
    )

    assert authorize_host_call(state, request) is True

    execute_host_call(state, request)
    assert state.vault_open is True

    assert authorize_host_call(state, request) is False


def test_close_vault_allowed_when_open():
    state = WasmBridgeState()

    execute_host_call(
        state,
        HostCallRequest(name="load_mobile_vault_boot", payload={}),
    )

    result = execute_host_call(
        state,
        HostCallRequest(name="close_mobile_vault", payload={}),
    )

    assert result.status == "allowed"
    assert result.payload["vault_closed"] is True
    assert state.vault_open is False


def test_transition_to_runtime_requires_closed_vault():
    state = WasmBridgeState()

    execute_host_call(
        state,
        HostCallRequest(name="load_mobile_vault_boot", payload={}),
    )

    try:
        transition_to_runtime(state)
    except ValueError:
        return

    raise AssertionError("Expected ValueError when Vault is open")


def test_transition_to_runtime_after_close():
    state = WasmBridgeState()

    execute_host_call(state, HostCallRequest(name="load_mobile_vault_boot", payload={}))
    execute_host_call(state, HostCallRequest(name="close_mobile_vault", payload={}))

    transition_to_runtime(state)

    assert state.phase == "RUNTIME"
    assert state.vault_open is False


def test_runtime_can_emit_sol_impulse():
    state = WasmBridgeState()

    execute_host_call(state, HostCallRequest(name="load_mobile_vault_boot", payload={}))
    execute_host_call(state, HostCallRequest(name="close_mobile_vault", payload={}))
    transition_to_runtime(state)

    result = execute_host_call(
        state,
        HostCallRequest(name="emit_sol_impulse", payload={"kind": "input"}),
    )

    assert result.status == "allowed"
    assert state.sol_emit_count == 1


def test_runtime_can_poll_sol_response():
    state = WasmBridgeState()

    execute_host_call(state, HostCallRequest(name="load_mobile_vault_boot", payload={}))
    execute_host_call(state, HostCallRequest(name="close_mobile_vault", payload={}))
    transition_to_runtime(state)

    result = execute_host_call(
        state,
        HostCallRequest(name="poll_sol_response", payload={}),
    )

    assert result.status == "allowed"
    assert state.sol_poll_count == 1


def test_runtime_cannot_open_vault():
    state = WasmBridgeState()

    transition_to_runtime(state)

    result = execute_host_call(
        state,
        HostCallRequest(name="open_vault_runtime", payload={}),
    )

    assert result.status == "denied"
    assert result.error == "forbidden_host_call"
    assert "open_vault_runtime" in state.denied_calls


def test_forbidden_calls_are_denied():
    state = WasmBridgeState()

    for call in sorted(FORBIDDEN_HOST_CALLS):
        result = execute_host_call(
            state,
            HostCallRequest(name=call, payload={}),  # type: ignore[arg-type]
        )

        assert result.status == "denied"
        assert result.error == "forbidden_host_call"


def test_sensor_permission_request_allowed_without_vault_open():
    state = WasmBridgeState()

    result = execute_host_call(
        state,
        HostCallRequest(
            name="request_sensor_permission",
            payload={"permission": "audio_capture"},
        ),
    )

    assert result.status == "allowed"
    assert state.permission_request_count == 1


def test_sensor_permission_request_denied_while_vault_open():
    state = WasmBridgeState()

    execute_host_call(state, HostCallRequest(name="load_mobile_vault_boot", payload={}))

    result = execute_host_call(
        state,
        HostCallRequest(
            name="request_sensor_permission",
            payload={"permission": "audio_capture"},
        ),
    )

    assert result.status == "denied"


def test_zeroize_allowed_during_boot():
    state = WasmBridgeState()

    result = execute_host_call(
        state,
        HostCallRequest(name="zeroize_admission_buffers", payload={}),
    )

    assert result.status == "allowed"
    assert state.zeroize_count == 1


def test_bridge_invariants_ok_after_normal_sequence():
    state = WasmBridgeState()

    execute_host_call(state, HostCallRequest(name="load_mobile_vault_boot", payload={}))
    execute_host_call(state, HostCallRequest(name="close_mobile_vault", payload={}))
    execute_host_call(state, HostCallRequest(name="zeroize_admission_buffers", payload={}))
    transition_to_runtime(state)
    execute_host_call(state, HostCallRequest(name="emit_sol_impulse", payload={}))

    assert wasm_bridge_invariants_ok(state) is True


def test_close_bridge_requires_closed_vault():
    state = WasmBridgeState()

    execute_host_call(state, HostCallRequest(name="load_mobile_vault_boot", payload={}))

    try:
        close_bridge(state)
    except ValueError:
        return

    raise AssertionError("Expected ValueError when Vault is open")


def test_close_bridge_sets_closed_phase():
    state = WasmBridgeState()

    close_bridge(state)

    assert state.phase == "CLOSED"


def test_bridge_does_not_affect_admission_identity_or_core_secrets():
    assert bridge_affects_admission() is False
    assert bridge_affects_identity() is False
    assert bridge_exposes_core_secrets() is False
