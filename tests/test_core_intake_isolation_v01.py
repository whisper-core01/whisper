from core_intake_isolation_v01 import (
    INBOUND_CHAIN,
    IntakeMaterial,
    OrganHealth,
    attempt_direct_delivery,
    bal_in_buffer,
    courier_carry,
    dome_validate,
    guided_link,
    intake_path_valid,
    membrane_absorb,
    organ_blindness_summary,
    organ_failure_must_not_create_shortcut,
    organ_restart_must_not_change_intake_path,
    simulate_full_intake,
    transporteur_participates_in_intake,
    wasm_knows_origin,
    wasm_receive,
    wasm_receives_rejected_material,
    wasm_touches_network,
)


def _external_material(valid=True):
    return IntakeMaterial(
        material_id="m1",
        state="external_raw",
        valid=valid,
        visible_payload="external-payload",
    )


def test_external_material_must_pass_full_intake_chain():
    assert guided_link("external_material_must_pass_full_intake_chain")

    trace = simulate_full_intake(_external_material(valid=True))

    assert trace.reached_wasm is True
    assert trace.path == INBOUND_CHAIN
    assert intake_path_valid(trace) is True


def test_wasm_cannot_receive_from_daemon_directly():
    assert guided_link("wasm_cannot_receive_from_daemon_directly")

    assert attempt_direct_delivery("daemon", "wasm", _external_material()) is False


def test_wasm_cannot_receive_from_dome_directly():
    assert guided_link("wasm_cannot_receive_from_dome_directly")

    assert attempt_direct_delivery("dome", "wasm", _external_material()) is False


def test_wasm_cannot_receive_from_courier_directly():
    assert guided_link("wasm_cannot_receive_from_courier_directly")

    assert attempt_direct_delivery("courier", "wasm", _external_material()) is False


def test_wasm_cannot_read_bal_in_directly():
    assert guided_link("wasm_cannot_read_bal_in_directly")

    assert attempt_direct_delivery("bal_in", "wasm", _external_material()) is False


def test_wasm_receives_only_membrane_absorbed_material():
    assert guided_link("wasm_receives_only_membrane_absorbed_material")

    trace = simulate_full_intake(_external_material(valid=True))

    assert trace.states[-2] == "membrane_absorbed"
    assert trace.states[-1] == "wasm_received"


def test_dome_rejected_material_never_reaches_courier():
    assert guided_link("dome_rejected_material_never_reaches_courier")

    trace = simulate_full_intake(_external_material(valid=False))

    assert trace.rejected is True
    assert trace.reached_wasm is False
    assert "courier" not in trace.path


def test_courier_cannot_carry_unvalidated_material():
    assert guided_link("courier_cannot_carry_unvalidated_material")

    trace = type("T", (), {"path": [], "states": []})()

    try:
        courier_carry(_external_material(valid=True), trace)
    except ValueError:
        return

    raise AssertionError("Expected ValueError for unvalidated material")


def test_bal_in_cannot_receive_external_material_directly():
    assert guided_link("bal_in_cannot_receive_external_material_directly")

    try:
        bal_in_buffer(_external_material(valid=True), type("T", (), {"path": [], "states": []})())
    except ValueError:
        return

    raise AssertionError("Expected ValueError for direct BAL In external material")


def test_membrane_cannot_absorb_external_material_directly():
    assert guided_link("membrane_cannot_absorb_external_material_directly")

    try:
        membrane_absorb(_external_material(valid=True), type("T", (), {"path": [], "states": []})())
    except ValueError:
        return

    raise AssertionError("Expected ValueError for direct Membrane external material")


def test_transporteur_never_participates_in_intake():
    assert guided_link("transporteur_never_participates_in_intake")

    assert transporteur_participates_in_intake() is False


def test_organ_failure_must_not_create_shortcut():
    assert guided_link("organ_failure_must_not_create_shortcut")

    for organ in ["daemon", "dome", "courier", "bal_in", "membrane"]:
        assert organ_failure_must_not_create_shortcut(organ) is True


def test_organ_restart_must_not_change_intake_path():
    assert guided_link("organ_restart_must_not_change_intake_path")

    for organ in ["daemon", "dome", "courier", "bal_in", "membrane"]:
        assert organ_restart_must_not_change_intake_path(organ) is True


def test_wasm_does_not_know_origin_or_network():
    assert guided_link("wasm_does_not_know_origin_or_network")

    assert wasm_knows_origin() is False
    assert wasm_touches_network() is False
    assert wasm_receives_rejected_material() is False


def test_organ_blindness_summary():
    summary = organ_blindness_summary()

    assert summary["daemon"] == "receives_without_understanding"
    assert summary["dome"] == "validates_without_reading"
    assert summary["courier"] == "carries_without_knowing"
    assert summary["bal_in"] == "buffers_without_knowing"
    assert summary["membrane"] == "absorbs_without_interpreting"
    assert summary["wasm"] == "transforms_without_touching_origin"


def test_membrane_is_only_valid_direct_source_to_wasm():
    assert attempt_direct_delivery("membrane", "wasm", _external_material()) is True
    assert attempt_direct_delivery("external", "wasm", _external_material()) is False
    assert attempt_direct_delivery("daemon", "wasm", _external_material()) is False
    assert attempt_direct_delivery("dome", "wasm", _external_material()) is False
    assert attempt_direct_delivery("courier", "wasm", _external_material()) is False
    assert attempt_direct_delivery("bal_in", "wasm", _external_material()) is False


def test_dead_membrane_blocks_wasm():
    health = OrganHealth(membrane_alive=False)

    trace = simulate_full_intake(_external_material(valid=True), health=health)

    assert trace.reached_wasm is False
    assert "wasm" not in trace.path
