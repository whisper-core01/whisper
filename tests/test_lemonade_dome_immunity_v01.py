from lemonade_dome_immunity_v01 import (
    DefenseSignal,
    DomeImmunityState,
    LemonadeState,
    daemon_receives_panic_flag,
    dome_apply_local_coherence_without_lemonade,
    dome_apply_recommendation,
    dome_enter_fallback_mode,
    dome_trigger_lemonade_restart,
    guided_link,
    handle_lemonade_panic_flag,
    lemonade_emit_panic_flag_on_abnormal_close,
    lemonade_failure_exposes_wasm,
    lemonade_failure_opens_shortcut,
    lemonade_never_blocks_material_directly,
    lemonade_never_touches_payload,
    lemonade_observe_signal,
    simulate_lemonade_abnormal_closure,
)


def test_lemonade_recommendation_is_applied_by_dome_when_available():
    assert guided_link("lemonade_recommendation_is_applied_by_dome_when_available")

    dome = DomeImmunityState()
    signal = DefenseSignal(
        source_organ="courier",
        signal_type="role_violation",
        severity=9,
    )

    recommendation = lemonade_observe_signal(signal)
    action = dome_apply_recommendation(dome, recommendation)

    assert recommendation.recommendation == "QUARANTINE_ORGAN"
    assert action.action == "QUARANTINE_ORGAN"
    assert action.target_organ == "courier"


def test_lemonade_emits_panic_flag_on_crash():
    assert guided_link("lemonade_emits_panic_flag_on_crash")

    lemonade = LemonadeState()

    flag = lemonade_emit_panic_flag_on_abnormal_close(
        lemonade=lemonade,
        timestamp="t-1",
        cause="LEMONADE_CRASH",
    )

    assert flag.type == "LEMONADE_FAILURE"
    assert flag.organ_id == "lemonade"
    assert flag.priority == "URGENT"
    assert lemonade.status == "DOWN"
    assert len(lemonade.emitted_panic_flags) == 1


def test_dome_enters_fallback_on_lemonade_failure():
    assert guided_link("dome_enters_fallback_on_lemonade_failure")

    lemonade = LemonadeState()
    dome = DomeImmunityState()

    flag = lemonade_emit_panic_flag_on_abnormal_close(
        lemonade=lemonade,
        timestamp="t-1",
        cause="LEMONADE_ABNORMAL_CLOSE",
    )

    action = dome_enter_fallback_mode(dome, flag)

    assert action.action == "STRICT_LOCAL_COHERENCE"
    assert dome.fallback_active is True
    assert dome.strict_local_coherence is True
    assert dome.adaptive_recommendations_enabled is False


def test_dome_triggers_lemonade_restart():
    assert guided_link("dome_triggers_lemonade_restart")

    lemonade = LemonadeState()
    dome = DomeImmunityState()

    flag = lemonade_emit_panic_flag_on_abnormal_close(
        lemonade=lemonade,
        timestamp="t-1",
        cause="LEMONADE_TIMEOUT",
    )

    action = dome_trigger_lemonade_restart(dome, flag)

    assert action.action == "REQUEST_RESTART"
    assert action.target_organ == "lemonade"
    assert dome.restart_requests == ["lemonade"]


def test_daemon_does_not_receive_panic_flag():
    assert guided_link("daemon_does_not_receive_panic_flag")

    _lemonade, dome = simulate_lemonade_abnormal_closure()

    assert daemon_receives_panic_flag(dome) is False


def test_intake_continues_without_lemonade_with_local_coherence():
    assert guided_link("intake_continues_without_lemonade")

    accepted = dome_apply_local_coherence_without_lemonade(material_coherent=True)
    rejected = dome_apply_local_coherence_without_lemonade(material_coherent=False)

    assert accepted.action == "ACCEPT_MATERIAL"
    assert rejected.action == "REJECT_MATERIAL"


def test_dome_applies_local_coherence_in_fallback():
    assert guided_link("dome_applies_local_coherence_in_fallback")

    _lemonade, dome = simulate_lemonade_abnormal_closure()

    assert dome.mode == "FALLBACK_STRICT_LOCAL_COHERENCE"
    assert dome.strict_local_coherence is True

    action = dome_apply_local_coherence_without_lemonade(material_coherent=False)

    assert action.action == "REJECT_MATERIAL"


def test_panic_flag_is_priority_and_triggers_fallback_then_restart():
    assert guided_link("panic_flag_is_priority_and_triggers_fallback_then_restart")

    lemonade = LemonadeState()
    dome = DomeImmunityState()

    flag = lemonade_emit_panic_flag_on_abnormal_close(
        lemonade=lemonade,
        timestamp="t-1",
        cause="LEMONADE_SELF_CHECK_FAILED",
    )

    actions = handle_lemonade_panic_flag(dome, flag)

    assert actions[0].action == "STRICT_LOCAL_COHERENCE"
    assert actions[1].action == "REQUEST_RESTART"
    assert dome.fallback_active is True
    assert dome.restart_requests == ["lemonade"]


def test_lemonade_never_blocks_material_directly():
    assert guided_link("lemonade_never_blocks_material_directly")

    assert lemonade_never_blocks_material_directly() is True


def test_lemonade_never_touches_payload():
    assert guided_link("lemonade_never_touches_payload")

    lemonade = LemonadeState()

    assert lemonade_never_touches_payload(lemonade) is True


def test_lemonade_failure_does_not_open_shortcut_or_expose_wasm():
    assert guided_link("lemonade_failure_does_not_open_shortcut_or_expose_wasm")

    assert lemonade_failure_opens_shortcut() is False
    assert lemonade_failure_exposes_wasm() is False


def test_recommendation_levels():
    assert guided_link("recommendation_levels")

    assert lemonade_observe_signal(
        DefenseSignal(source_organ="daemon", signal_type="normal", severity=1)
    ).recommendation == "ALLOW"

    assert lemonade_observe_signal(
        DefenseSignal(source_organ="dome", signal_type="bad_fragment", severity=3)
    ).recommendation == "REJECT"

    assert lemonade_observe_signal(
        DefenseSignal(source_organ="bal_in", signal_type="ack_timeout", severity=5)
    ).recommendation == "HOLD"

    assert lemonade_observe_signal(
        DefenseSignal(source_organ="membrane", signal_type="transition_error", severity=7)
    ).recommendation == "RESTART_REQUIRED"

    assert lemonade_observe_signal(
        DefenseSignal(source_organ="courier", signal_type="shortcut_attempt", severity=9)
    ).recommendation == "QUARANTINE_ORGAN"
