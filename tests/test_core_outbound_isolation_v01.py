from core_outbound_isolation_v01 import (
    OUTBOUND_CHAIN,
    BALOutBuffer,
    DaemonOutBuffer,
    MembraneOutBuffer,
    OutboundMaterial,
    OutboundRetentionLedger,
    OutboundTrace,
    TransporteurBuffer,
    attempt_direct_delivery,
    bal_in_participates_in_outbound,
    bal_out_receive_from_membrane,
    bal_out_release_after_transporteur_ack,
    courier_participates_in_outbound,
    daemon_receive_from_transporteur,
    daemon_release_after_network_ack,
    dome_participates_in_outbound,
    guided_link,
    lemonade_participates_in_outbound,
    membrane_export_from_wasm,
    membrane_release_after_bal_out_ack,
    network_emit_from_daemon,
    network_receives_only_daemon_emitted_material,
    organ_failure_must_not_create_outbound_shortcut,
    organ_restart_must_not_change_outbound_path,
    outbound_blindness_summary,
    outbound_path_valid,
    simulate_daemon_failure_before_network_ack,
    simulate_daemon_restart_can_emit_retained_material,
    simulate_full_outbound,
    simulate_transporteur_failure_before_daemon_ack,
    simulate_transporteur_restart_can_resend_to_daemon,
    transporteur_pickup_from_bal_out,
    transporteur_release_after_daemon_ack,
    wasm_touches_network_directly,
)


def _wasm_material(material_id="m1"):
    return OutboundMaterial(
        material_id=material_id,
        state="wasm_output",
        valid=True,
        visible_payload="wasm-payload",
    )


def test_wasm_output_must_pass_full_outbound_chain():
    assert guided_link("wasm_output_must_pass_full_outbound_chain")

    trace, ledger = simulate_full_outbound(_wasm_material())

    assert trace.reached_network is True
    assert trace.path == OUTBOUND_CHAIN
    assert outbound_path_valid(trace) is True
    assert ledger.membrane_retained == set()
    assert ledger.bal_out_retained == set()
    assert ledger.transporteur_retained == set()
    assert ledger.daemon_retained == set()


def test_wasm_cannot_emit_to_network_directly():
    assert guided_link("wasm_cannot_emit_to_network_directly")

    assert attempt_direct_delivery("wasm", "network") is False
    assert wasm_touches_network_directly() is False


def test_network_receives_only_from_daemon():
    assert guided_link("network_receives_only_from_daemon")

    assert attempt_direct_delivery("daemon", "network") is True
    assert attempt_direct_delivery("transporteur", "network") is False
    assert attempt_direct_delivery("bal_out", "network") is False
    assert attempt_direct_delivery("membrane", "network") is False
    assert network_receives_only_daemon_emitted_material() is True


def test_dome_courier_bal_in_and_lemonade_never_participate_in_outbound():
    assert guided_link("dome_courier_bal_in_and_lemonade_never_participate_in_outbound")

    assert dome_participates_in_outbound() is False
    assert courier_participates_in_outbound() is False
    assert bal_in_participates_in_outbound() is False
    assert lemonade_participates_in_outbound() is False


def test_membrane_retains_until_bal_out_ack():
    assert guided_link("membrane_retains_until_bal_out_ack")

    membrane = MembraneOutBuffer()
    ledger = OutboundRetentionLedger()
    trace = OutboundTrace(path=["wasm"], states=["wasm_output"])

    material = membrane_export_from_wasm(_wasm_material(), membrane, ledger, trace)

    assert material.material_id in membrane.retained
    assert material.material_id in ledger.membrane_retained


def test_membrane_does_not_release_on_export_only():
    assert guided_link("membrane_does_not_release_on_export_only")

    membrane = MembraneOutBuffer()
    ledger = OutboundRetentionLedger()
    trace = OutboundTrace(path=["wasm"], states=["wasm_output"])

    material = membrane_export_from_wasm(_wasm_material(), membrane, ledger, trace)

    released = membrane_release_after_bal_out_ack(material.material_id, membrane, ledger)

    assert released is False
    assert material.material_id in membrane.retained


def test_membrane_releases_after_bal_out_ack():
    assert guided_link("membrane_releases_after_bal_out_ack")

    membrane = MembraneOutBuffer()
    bal_out = BALOutBuffer()
    ledger = OutboundRetentionLedger()
    trace = OutboundTrace(path=["wasm"], states=["wasm_output"])

    material = membrane_export_from_wasm(_wasm_material(), membrane, ledger, trace)
    material = bal_out_receive_from_membrane(material, bal_out, ledger, trace)

    released = membrane_release_after_bal_out_ack(material.material_id, membrane, ledger)

    assert released is True
    assert material.material_id not in membrane.retained


def test_bal_out_retains_until_transporteur_ack():
    assert guided_link("bal_out_retains_until_transporteur_ack")

    membrane = MembraneOutBuffer()
    bal_out = BALOutBuffer()
    ledger = OutboundRetentionLedger()
    trace = OutboundTrace(path=["wasm"], states=["wasm_output"])

    material = membrane_export_from_wasm(_wasm_material(), membrane, ledger, trace)
    material = bal_out_receive_from_membrane(material, bal_out, ledger, trace)

    assert material.material_id in bal_out.retained
    assert material.material_id in ledger.bal_out_retained


def test_bal_out_releases_after_transporteur_ack():
    assert guided_link("bal_out_releases_after_transporteur_ack")

    membrane = MembraneOutBuffer()
    bal_out = BALOutBuffer()
    transporteur = TransporteurBuffer()
    ledger = OutboundRetentionLedger()
    trace = OutboundTrace(path=["wasm"], states=["wasm_output"])

    material = membrane_export_from_wasm(_wasm_material(), membrane, ledger, trace)
    material = bal_out_receive_from_membrane(material, bal_out, ledger, trace)
    material = transporteur_pickup_from_bal_out(material, transporteur, ledger, trace)

    released = bal_out_release_after_transporteur_ack(material.material_id, bal_out, ledger)

    assert released is True
    assert material.material_id not in bal_out.retained


def test_transporteur_retains_until_daemon_ack():
    assert guided_link("transporteur_retains_until_daemon_ack")

    transporteur, ledger, trace = simulate_transporteur_failure_before_daemon_ack()

    assert "m-transporteur-failure" in transporteur.retained
    assert "m-transporteur-failure" in ledger.transporteur_retained
    assert "daemon" not in trace.path


def test_transporteur_does_not_release_on_pickup_only():
    assert guided_link("transporteur_does_not_release_on_pickup_only")

    transporteur, ledger, _trace = simulate_transporteur_failure_before_daemon_ack()

    released = transporteur_release_after_daemon_ack(
        "m-transporteur-failure",
        transporteur,
        ledger,
    )

    assert released is False
    assert "m-transporteur-failure" in transporteur.retained


def test_transporteur_restart_can_resend_to_daemon():
    assert guided_link("transporteur_restart_can_resend_to_daemon")

    assert simulate_transporteur_restart_can_resend_to_daemon() is True


def test_daemon_retains_until_network_ack():
    assert guided_link("daemon_retains_until_network_ack")

    daemon, ledger, trace = simulate_daemon_failure_before_network_ack()

    assert "m-daemon-failure" in daemon.retained
    assert "m-daemon-failure" in ledger.daemon_retained
    assert "network" not in trace.path


def test_daemon_releases_after_network_ack():
    assert guided_link("daemon_releases_after_network_ack")

    membrane = MembraneOutBuffer()
    bal_out = BALOutBuffer()
    transporteur = TransporteurBuffer()
    daemon = DaemonOutBuffer()
    ledger = OutboundRetentionLedger()
    trace = OutboundTrace(path=["wasm"], states=["wasm_output"])

    material = membrane_export_from_wasm(_wasm_material(), membrane, ledger, trace)
    material = bal_out_receive_from_membrane(material, bal_out, ledger, trace)
    material = transporteur_pickup_from_bal_out(material, transporteur, ledger, trace)
    material = daemon_receive_from_transporteur(material, daemon, ledger, trace)
    material = network_emit_from_daemon(material, ledger, trace)

    released = daemon_release_after_network_ack(material.material_id, daemon, ledger)

    assert released is True
    assert material.material_id not in daemon.retained


def test_daemon_restart_can_emit_retained_material():
    assert guided_link("daemon_restart_can_emit_retained_material")

    assert simulate_daemon_restart_can_emit_retained_material() is True


def test_invalid_direct_steps_are_rejected():
    assert guided_link("invalid_direct_steps_are_rejected")

    try:
        bal_out_receive_from_membrane(
            _wasm_material(),
            BALOutBuffer(),
            OutboundRetentionLedger(),
            OutboundTrace(),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected BAL Out direct Wasm material rejection")

    try:
        transporteur_pickup_from_bal_out(
            _wasm_material(),
            TransporteurBuffer(),
            OutboundRetentionLedger(),
            OutboundTrace(),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected Transporteur direct Wasm material rejection")

    try:
        daemon_receive_from_transporteur(
            _wasm_material(),
            DaemonOutBuffer(),
            OutboundRetentionLedger(),
            OutboundTrace(),
        )
    except ValueError:
        return

    raise AssertionError("Expected Daemon direct Wasm material rejection")


def test_outbound_organ_failure_must_not_create_shortcut():
    assert guided_link("outbound_organ_failure_must_not_create_shortcut")

    for organ in ["membrane", "bal_out", "transporteur", "daemon"]:
        assert organ_failure_must_not_create_outbound_shortcut(organ) is True


def test_outbound_organ_restart_must_not_change_path():
    assert guided_link("outbound_organ_restart_must_not_change_path")

    for organ in ["membrane", "bal_out", "transporteur", "daemon"]:
        assert organ_restart_must_not_change_outbound_path(organ) is True


def test_outbound_blindness_summary():
    assert guided_link("outbound_blindness_summary")

    summary = outbound_blindness_summary()

    assert summary["wasm"] == "produces_without_touching_network"
    assert summary["membrane"] == "exports_without_exposing_origin"
    assert summary["bal_out"] == "retains_without_knowing"
    assert summary["transporteur"] == "carries_without_interpreting"
    assert summary["daemon"] == "emits_without_understanding"
    assert summary["network"] == "receives_only_daemon_emission"
