from reticulum_boundary_v01 import (
    DaemonOutboundEnvelope,
    DaemonReticulumBoundary,
    ReticulumAdapter,
    ReticulumBoundaryLedger,
    ReticulumPacket,
    attempt_reticulum_direct_delivery,
    boundary_summary,
    courier_accepts_only_dome_handoff,
    daemon_is_reticulum_interface,
    daemon_participates_in_immunity,
    daemon_prepare_outbound_for_reticulum,
    daemon_receive_from_reticulum,
    daemon_release_after_dome_ack,
    daemon_release_after_reticulum_ack,
    daemon_touches_payload,
    daemon_touches_validity,
    dome_acknowledge_daemon_inbound,
    dome_create_handoff_for_courier,
    guided_link,
    reticulum_adapter_stores_core_truth,
    reticulum_adapter_touches_internal_organs,
    reticulum_adapter_touches_payload,
    reticulum_can_reach_internal_organ,
    reticulum_edge_allowed,
    reticulum_emit_from_daemon,
    reticulum_failure_creates_core_shortcut,
    reticulum_is_internal_organ,
    reticulum_restart_changes_core_rails,
    wasm_can_reach_reticulum_directly,
)


def _inbound_packet(packet_id="r-in"):
    return ReticulumPacket(
        packet_id=packet_id,
        direction="INBOUND",
        state="reticulum_raw",
        visible_payload="network-payload",
    )


def test_reticulum_is_external_not_internal_organ():
    assert guided_link("reticulum_is_external_not_internal_organ")

    assert reticulum_is_internal_organ() is False
    assert daemon_is_reticulum_interface() is True


def test_reticulum_inbound_enters_only_through_daemon():
    assert guided_link("reticulum_inbound_enters_only_through_daemon")

    assert reticulum_edge_allowed("reticulum", "daemon") is True
    assert attempt_reticulum_direct_delivery("reticulum", "daemon") == "allow"

    for target in ["dome", "courier", "bal_in", "membrane", "wasm"]:
        assert reticulum_can_reach_internal_organ(target) is False
        assert attempt_reticulum_direct_delivery("reticulum", target) == "reject"


def test_reticulum_cannot_reach_wasm_directly():
    assert guided_link("reticulum_cannot_reach_wasm_directly")

    assert reticulum_can_reach_internal_organ("wasm") is False
    assert attempt_reticulum_direct_delivery("reticulum", "wasm") == "reject"


def test_reticulum_cannot_reach_dome_directly():
    assert guided_link("reticulum_cannot_reach_dome_directly")

    assert reticulum_can_reach_internal_organ("dome") is False
    assert attempt_reticulum_direct_delivery("reticulum", "dome") == "reject"


def test_wasm_cannot_emit_to_reticulum_directly():
    assert guided_link("wasm_cannot_emit_to_reticulum_directly")

    assert wasm_can_reach_reticulum_directly() is False
    assert attempt_reticulum_direct_delivery("wasm", "reticulum") == "reject"


def test_daemon_receives_reticulum_packet_and_retains_until_dome_ack():
    assert guided_link("daemon_receives_reticulum_packet_and_retains_until_dome_ack")

    daemon = DaemonReticulumBoundary()
    ledger = ReticulumBoundaryLedger()

    envelope = daemon_receive_from_reticulum(_inbound_packet(), daemon, ledger)

    assert envelope.packet_id in daemon.inbound_retained
    assert envelope.packet_id in ledger.daemon_inbound_retained

    released = daemon_release_after_dome_ack(envelope.packet_id, daemon, ledger)

    assert released is False
    assert envelope.packet_id in daemon.inbound_retained


def test_daemon_releases_reticulum_inbound_after_dome_ack():
    assert guided_link("daemon_releases_reticulum_inbound_after_dome_ack")

    daemon = DaemonReticulumBoundary()
    ledger = ReticulumBoundaryLedger()

    envelope = daemon_receive_from_reticulum(_inbound_packet(), daemon, ledger)

    dome_acknowledge_daemon_inbound(envelope, ledger)
    released = daemon_release_after_dome_ack(envelope.packet_id, daemon, ledger)

    assert released is True
    assert envelope.packet_id not in daemon.inbound_retained
    assert envelope.packet_id not in ledger.daemon_inbound_retained


def test_dome_creates_handoff_and_courier_only_accepts_handoff():
    assert guided_link("dome_creates_handoff_and_courier_only_accepts_handoff")

    daemon = DaemonReticulumBoundary()
    ledger = ReticulumBoundaryLedger()

    envelope = daemon_receive_from_reticulum(_inbound_packet(), daemon, ledger)
    handoff = dome_create_handoff_for_courier(envelope)

    assert handoff.state == "dome_handoff_ready"
    assert courier_accepts_only_dome_handoff(handoff) is True
    assert courier_accepts_only_dome_handoff(_inbound_packet()) is False


def test_courier_does_not_touch_validity_only_handoff():
    assert guided_link("courier_does_not_touch_validity_only_handoff")

    daemon = DaemonReticulumBoundary()
    ledger = ReticulumBoundaryLedger()

    envelope = daemon_receive_from_reticulum(_inbound_packet(), daemon, ledger)
    handoff = dome_create_handoff_for_courier(envelope)

    assert courier_accepts_only_dome_handoff(handoff) is True
    assert handoff.visible_payload is None


def test_outbound_reticulum_receives_only_daemon_emission():
    assert guided_link("outbound_reticulum_receives_only_daemon_emission")

    assert reticulum_edge_allowed("daemon", "reticulum") is True

    for source in ["wasm", "membrane", "bal_out", "transporteur", "dome", "courier"]:
        assert attempt_reticulum_direct_delivery(source, "reticulum") in {"reject", "deny"}


def test_daemon_retains_outbound_until_reticulum_ack():
    assert guided_link("daemon_retains_outbound_until_reticulum_ack")

    daemon = DaemonReticulumBoundary()
    ledger = ReticulumBoundaryLedger()

    outbound = daemon_prepare_outbound_for_reticulum(
        DaemonOutboundEnvelope(packet_id="r-out", target="reticulum"),
        daemon,
        ledger,
    )

    assert outbound.packet_id in daemon.outbound_retained
    assert outbound.packet_id in ledger.daemon_outbound_retained

    released = daemon_release_after_reticulum_ack(outbound.packet_id, daemon, ledger)

    assert released is False
    assert outbound.packet_id in daemon.outbound_retained


def test_daemon_releases_outbound_after_reticulum_ack():
    assert guided_link("daemon_releases_outbound_after_reticulum_ack")

    daemon = DaemonReticulumBoundary()
    ledger = ReticulumBoundaryLedger()

    outbound = daemon_prepare_outbound_for_reticulum(
        DaemonOutboundEnvelope(packet_id="r-out", target="reticulum"),
        daemon,
        ledger,
    )

    emitted = reticulum_emit_from_daemon(outbound, ledger)
    released = daemon_release_after_reticulum_ack(emitted.packet_id, daemon, ledger)

    assert emitted.state == "reticulum_emitted"
    assert released is True
    assert emitted.packet_id not in daemon.outbound_retained


def test_reticulum_adapter_does_not_store_core_truth_or_touch_payload():
    assert guided_link("reticulum_adapter_does_not_store_core_truth_or_touch_payload")

    adapter = ReticulumAdapter()

    assert reticulum_adapter_stores_core_truth(adapter) is False
    assert reticulum_adapter_touches_payload(adapter) is False
    assert reticulum_adapter_touches_internal_organs(adapter) is False


def test_daemon_does_not_read_decide_or_join_immunity():
    assert guided_link("daemon_does_not_read_decide_or_join_immunity")

    daemon = DaemonReticulumBoundary()

    assert daemon_touches_payload(daemon) is False
    assert daemon_touches_validity(daemon) is False
    assert daemon_participates_in_immunity(daemon) is False


def test_reticulum_failure_does_not_create_shortcut():
    assert guided_link("reticulum_failure_does_not_create_shortcut")

    assert reticulum_failure_creates_core_shortcut() is False


def test_reticulum_restart_does_not_change_core_rails():
    assert guided_link("reticulum_restart_does_not_change_core_rails")

    assert reticulum_restart_changes_core_rails() is False


def test_forbidden_attempts_are_logged_without_opening_path():
    assert guided_link("forbidden_attempts_are_logged_without_opening_path")

    ledger = ReticulumBoundaryLedger()

    decision = attempt_reticulum_direct_delivery("reticulum", "wasm", ledger)

    assert decision == "reject"
    assert ledger.forbidden_attempts == ["reticulum->wasm"]


def test_boundary_summary():
    assert guided_link("boundary_summary")

    summary = boundary_summary()

    assert summary["reticulum"] == "external_network_layer"
    assert summary["daemon"] == "network_boundary_interface"
    assert summary["dome"] == "validity_and_defense"
    assert summary["courier"] == "internal_delivery_of_dome_handoff"
    assert summary["wasm"] == "isolated_transformation"
