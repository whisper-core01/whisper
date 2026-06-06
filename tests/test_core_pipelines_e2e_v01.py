from core_intake_isolation_v01 import (
    INBOUND_CHAIN,
    IntakeMaterial,
    intake_path_valid,
    organ_failure_must_not_create_shortcut,
    simulate_full_intake,
    transporteur_participates_in_intake,
)
from core_outbound_isolation_v01 import (
    OUTBOUND_CHAIN,
    OutboundMaterial,
    courier_participates_in_outbound,
    dome_participates_in_outbound,
    lemonade_participates_in_outbound,
    outbound_path_valid,
    simulate_full_outbound,
    simulate_transporteur_failure_before_daemon_ack,
    simulate_transporteur_restart_can_resend_to_daemon,
)
from lemonade_dome_immunity_v01 import (
    dome_apply_local_coherence_without_lemonade,
    simulate_lemonade_abnormal_closure,
)
from organ_restart_safety_v01 import (
    BASE_PRIVILEGES,
    RestartRequest,
    create_runtime_record,
    mark_failed,
    organ_restart_changes_rails,
    organ_restart_creates_shortcut,
    reintegrate_restarted_organ,
    request_restart,
    restarted_organ_has_no_forbidden_privileges,
)


def _intake_trace(result):
    # Compatible with current API returning IntakeTrace,
    # and future API returning (IntakeTrace, ledger).
    if isinstance(result, tuple):
        return result[0]
    return result


def _outbound_trace_and_ledger(result):
    # Current outbound API returns (OutboundTrace, ledger).
    if isinstance(result, tuple):
        return result
    return result, None


def test_e2e_valid_external_material_reaches_wasm_then_network():
    intake_trace = _intake_trace(
        simulate_full_intake(
            IntakeMaterial(
                material_id="e2e-1",
                state="external_raw",
                valid=True,
                visible_payload="external-payload",
            )
        )
    )

    assert intake_trace.reached_wasm is True
    assert intake_trace.path == INBOUND_CHAIN
    assert intake_path_valid(intake_trace) is True

    outbound_trace, outbound_ledger = _outbound_trace_and_ledger(
        simulate_full_outbound(
            OutboundMaterial(
                material_id="e2e-1-out",
                state="wasm_output",
                valid=True,
                visible_payload="wasm-payload",
            )
        )
    )

    assert outbound_trace.reached_network is True
    assert outbound_trace.path == OUTBOUND_CHAIN
    assert outbound_path_valid(outbound_trace) is True

    if outbound_ledger is not None:
        assert outbound_ledger.membrane_retained == set()
        assert outbound_ledger.bal_out_retained == set()
        assert outbound_ledger.transporteur_retained == set()
        assert outbound_ledger.daemon_retained == set()


def test_e2e_rejected_inbound_material_never_creates_outbound():
    intake_trace = _intake_trace(
        simulate_full_intake(
            IntakeMaterial(
                material_id="e2e-rejected",
                state="external_raw",
                valid=False,
                visible_payload="bad-external-payload",
            )
        )
    )

    assert intake_trace.rejected is True
    assert intake_trace.reached_wasm is False
    assert "wasm" not in intake_trace.path
    assert "membrane_absorbed" not in intake_trace.states
    assert "wasm_received" not in intake_trace.states


def test_e2e_inbound_organ_failure_never_creates_shortcut():
    for organ in ["daemon", "dome", "courier", "bal_in", "membrane"]:
        assert organ_failure_must_not_create_shortcut(organ) is True


def test_e2e_transporteur_failure_keeps_transporteur_retention_then_restart_resends():
    transporteur, ledger, trace = simulate_transporteur_failure_before_daemon_ack()

    assert "m-transporteur-failure" in transporteur.retained
    assert "m-transporteur-failure" in ledger.transporteur_retained
    assert "daemon" not in trace.path

    assert simulate_transporteur_restart_can_resend_to_daemon() is True


def test_e2e_lemonade_failure_falls_back_but_intake_still_accepts_coherent_material():
    lemonade, dome = simulate_lemonade_abnormal_closure()

    assert lemonade.status == "DOWN"
    assert dome.mode == "FALLBACK_STRICT_LOCAL_COHERENCE"
    assert dome.strict_local_coherence is True
    assert dome.restart_requests == ["lemonade"]

    fallback_action = dome_apply_local_coherence_without_lemonade(
        material_coherent=True,
    )

    assert fallback_action.action == "ACCEPT_MATERIAL"

    intake_trace = _intake_trace(
        simulate_full_intake(
            IntakeMaterial(
                material_id="e2e-fallback",
                state="external_raw",
                valid=True,
                visible_payload="external-payload",
            )
        )
    )

    assert intake_trace.reached_wasm is True
    assert intake_trace.path == INBOUND_CHAIN


def test_e2e_lemonade_failure_fallback_rejects_incoherent_material():
    _lemonade, dome = simulate_lemonade_abnormal_closure()

    assert dome.strict_local_coherence is True

    fallback_action = dome_apply_local_coherence_without_lemonade(
        material_coherent=False,
    )

    assert fallback_action.action == "REJECT_MATERIAL"

    intake_trace = _intake_trace(
        simulate_full_intake(
            IntakeMaterial(
                material_id="e2e-fallback-reject",
                state="external_raw",
                valid=False,
                visible_payload="bad-external-payload",
            )
        )
    )

    assert intake_trace.rejected is True
    assert intake_trace.reached_wasm is False


def test_e2e_restarted_organs_keep_minimal_privileges_and_no_shortcuts():
    for organ in BASE_PRIVILEGES:
        record = create_runtime_record(organ)
        mark_failed(record, "e2e_failure")

        restart = request_restart(
            record,
            RestartRequest(
                organ=organ,
                reason="e2e_failure",
                requested_by="dome",
            ),
        )

        assert restart.decision == "restart_allowed"

        reintegrated = reintegrate_restarted_organ(record)

        assert reintegrated.decision == "reintegrated"
        assert record.privileges == BASE_PRIVILEGES[organ]
        assert restarted_organ_has_no_forbidden_privileges(organ) is True

    assert organ_restart_changes_rails() is False
    assert organ_restart_creates_shortcut() is False


def test_e2e_inbound_and_outbound_roles_never_cross():
    assert transporteur_participates_in_intake() is False

    assert dome_participates_in_outbound() is False
    assert courier_participates_in_outbound() is False
    assert lemonade_participates_in_outbound() is False
