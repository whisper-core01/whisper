from reticulum_e2e_v01 import (
    reticulum_e2e_summary,
    run_reticulum_e2e,
)


def test_reticulum_e2e_inbound_reaches_wasm_only_through_valid_path():
    result = run_reticulum_e2e()

    assert result.inbound_reached_wasm is True
    assert result.inbound_path_valid is True


def test_reticulum_e2e_outbound_reaches_network_only_through_valid_path():
    result = run_reticulum_e2e()

    assert result.outbound_reached_network is True
    assert result.outbound_path_valid is True


def test_reticulum_e2e_emits_only_after_daemon_boundary():
    result = run_reticulum_e2e()

    assert result.reticulum_emitted is True


def test_reticulum_e2e_wasm_never_reaches_reticulum_directly():
    result = run_reticulum_e2e()

    assert result.wasm_can_reach_reticulum is False


def test_reticulum_e2e_retention_released_after_ack():
    result = run_reticulum_e2e()

    assert result.daemon_inbound_retained is False
    assert result.daemon_outbound_retained is False


def test_reticulum_e2e_summary():
    summary = reticulum_e2e_summary()

    assert summary["inbound_reached_wasm"] is True
    assert summary["inbound_path_valid"] is True
    assert summary["outbound_reached_network"] is True
    assert summary["outbound_path_valid"] is True
    assert summary["reticulum_emitted"] is True
    assert summary["wasm_can_reach_reticulum"] is False
    assert summary["daemon_inbound_retained"] is False
    assert summary["daemon_outbound_retained"] is False
