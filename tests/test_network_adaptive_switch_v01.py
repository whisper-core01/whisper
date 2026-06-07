from network_adaptive_switch_v01 import (
    FULL_PAYLOADS,
    TEXT_ONLY_PAYLOADS,
    AdaptiveThresholds,
    BearerHistory,
    BearerSample,
    NetworkSwitchState,
    adaptive_switch_summary,
    apply_switch_decision,
    decide_adaptive_switch,
    guided_link,
    sample_is_good,
    sample_is_viable,
    stable_recovery,
    sustained_bad,
    switch_changes_core_rails,
    switch_exposes_wasm,
    switch_is_user_transparent,
    switch_participates_in_immunity,
    switch_touches_dome,
)


def test_keeps_primary_when_primary_is_good():
    assert guided_link("keeps_primary_when_primary_is_good")

    history = BearerHistory()
    history.add(BearerSample("PRIMARY_INTERNET", True, latency_ms=40, packet_loss_percent=0))

    state = NetworkSwitchState(current_bearer="PRIMARY_INTERNET")

    decision = decide_adaptive_switch(state, history)

    assert decision.bearer == "PRIMARY_INTERNET"
    assert decision.switched is False
    assert decision.allowed_payloads == FULL_PAYLOADS


def test_does_not_switch_on_single_latency_spike():
    assert guided_link("does_not_switch_on_single_latency_spike")

    history = BearerHistory()
    history.add(BearerSample("PRIMARY_INTERNET", True, latency_ms=900, packet_loss_percent=0))
    history.add(BearerSample("MOBILE_DATA_4G_5G", True, latency_ms=80, packet_loss_percent=2))

    state = NetworkSwitchState(current_bearer="PRIMARY_INTERNET")

    decision = decide_adaptive_switch(state, history)

    assert decision.bearer == "PRIMARY_INTERNET"
    assert decision.switched is False
    assert decision.reason == "waiting_for_sustained_degradation"


def test_switches_to_mobile_after_sustained_primary_degradation():
    assert guided_link("switches_to_mobile_after_sustained_primary_degradation")

    history = BearerHistory()

    for _ in range(3):
        history.add(BearerSample("PRIMARY_INTERNET", True, latency_ms=900, packet_loss_percent=30))
        history.add(BearerSample("MOBILE_DATA_4G_5G", True, latency_ms=80, packet_loss_percent=2))

    state = NetworkSwitchState(current_bearer="PRIMARY_INTERNET")

    decision = decide_adaptive_switch(state, history)

    assert decision.bearer == "MOBILE_DATA_4G_5G"
    assert decision.switched is True
    assert decision.mode == "CONNECTED"
    assert decision.stack == "RETICULUM_VOXMESH"
    assert decision.allowed_payloads == FULL_PAYLOADS


def test_mobile_keeps_full_capabilities():
    assert guided_link("mobile_keeps_full_capabilities")

    history = BearerHistory()

    for _ in range(3):
        history.add(BearerSample("PRIMARY_INTERNET", False))
        history.add(BearerSample("MOBILE_DATA_4G_5G", True, latency_ms=90, packet_loss_percent=2))

    state = NetworkSwitchState(current_bearer="PRIMARY_INTERNET")

    decision = decide_adaptive_switch(state, history)

    assert decision.bearer == "MOBILE_DATA_4G_5G"
    assert decision.allowed_payloads == FULL_PAYLOADS
    assert "video" in decision.allowed_payloads


def test_uses_lora_only_when_no_ip_viable():
    assert guided_link("uses_lora_only_when_no_ip_viable")

    history = BearerHistory()

    for _ in range(3):
        history.add(BearerSample("PRIMARY_INTERNET", False))
        history.add(BearerSample("MOBILE_DATA_4G_5G", False))
        history.add(BearerSample("LORA_RNODE", True, latency_ms=900, packet_loss_percent=5))

    state = NetworkSwitchState(current_bearer="PRIMARY_INTERNET")

    decision = decide_adaptive_switch(state, history)

    assert decision.bearer == "LORA_RNODE"
    assert decision.mode == "DEGRADED_SURVIVAL"
    assert decision.stack == "LORA_TEXT"
    assert decision.allowed_payloads == TEXT_ONLY_PAYLOADS


def test_offline_when_no_bearer_available():
    assert guided_link("offline_when_no_bearer_available")

    history = BearerHistory()

    for _ in range(3):
        history.add(BearerSample("PRIMARY_INTERNET", False))
        history.add(BearerSample("MOBILE_DATA_4G_5G", False))
        history.add(BearerSample("LORA_RNODE", False))

    state = NetworkSwitchState(current_bearer="PRIMARY_INTERNET")

    decision = decide_adaptive_switch(state, history)

    assert decision.bearer == "NONE"
    assert decision.mode == "OFFLINE"
    assert decision.stack == "NONE"
    assert decision.allowed_payloads == set()


def test_returns_to_primary_only_after_stable_recovery():
    assert guided_link("returns_to_primary_only_after_stable_recovery")

    history = BearerHistory()

    for _ in range(2):
        history.add(BearerSample("PRIMARY_INTERNET", True, latency_ms=40, packet_loss_percent=0))

    state = NetworkSwitchState(current_bearer="MOBILE_DATA_4G_5G")

    decision = decide_adaptive_switch(state, history)

    assert decision.bearer == "MOBILE_DATA_4G_5G"
    assert decision.switched is False

    history.add(BearerSample("PRIMARY_INTERNET", True, latency_ms=35, packet_loss_percent=0))

    decision = decide_adaptive_switch(state, history)

    assert decision.bearer == "PRIMARY_INTERNET"
    assert decision.switched is True
    assert decision.reason == "primary_internet_stably_recovered"


def test_sample_viability_and_goodness():
    assert guided_link("sample_viability_and_goodness")

    thresholds = AdaptiveThresholds()

    assert sample_is_viable(BearerSample("PRIMARY_INTERNET", True, latency_ms=50, packet_loss_percent=0), thresholds) is True
    assert sample_is_good(BearerSample("PRIMARY_INTERNET", True, latency_ms=50, packet_loss_percent=0), thresholds) is True

    assert sample_is_viable(BearerSample("PRIMARY_INTERNET", False), thresholds) is False
    assert sample_is_good(BearerSample("PRIMARY_INTERNET", True, latency_ms=900, packet_loss_percent=0), thresholds) is False
    assert sample_is_viable(BearerSample("PRIMARY_INTERNET", True, latency_ms=50, packet_loss_percent=80), thresholds) is False


def test_sustained_bad_and_stable_recovery():
    assert guided_link("sustained_bad_and_stable_recovery")

    thresholds = AdaptiveThresholds()
    history = BearerHistory()

    for _ in range(3):
        history.add(BearerSample("PRIMARY_INTERNET", True, latency_ms=900, packet_loss_percent=30))

    assert sustained_bad(history, "PRIMARY_INTERNET", thresholds) is True

    recovery = BearerHistory()
    for _ in range(3):
        recovery.add(BearerSample("PRIMARY_INTERNET", True, latency_ms=40, packet_loss_percent=0))

    assert stable_recovery(recovery, "PRIMARY_INTERNET", thresholds) is True


def test_apply_switch_decision_updates_state():
    assert guided_link("apply_switch_decision_updates_state")

    history = BearerHistory()

    for _ in range(3):
        history.add(BearerSample("PRIMARY_INTERNET", False))
        history.add(BearerSample("MOBILE_DATA_4G_5G", True, latency_ms=90, packet_loss_percent=2))

    state = NetworkSwitchState(current_bearer="PRIMARY_INTERNET")
    decision = decide_adaptive_switch(state, history)

    apply_switch_decision(state, decision)

    assert state.current_bearer == "MOBILE_DATA_4G_5G"
    assert state.mode == "CONNECTED"
    assert state.stack == "RETICULUM_VOXMESH"


def test_switch_is_transparent_and_does_not_touch_core():
    assert guided_link("switch_is_transparent_and_does_not_touch_core")

    state = NetworkSwitchState()

    assert switch_is_user_transparent(state) is True
    assert switch_changes_core_rails(state) is False
    assert switch_exposes_wasm(state) is False
    assert switch_touches_dome(state) is False
    assert switch_participates_in_immunity(state) is False


def test_adaptive_switch_summary():
    assert guided_link("adaptive_switch_summary")

    summary = adaptive_switch_summary()

    assert summary["bearer"] == "MOBILE_DATA_4G_5G"
    assert summary["mode"] == "CONNECTED"
    assert summary["stack"] == "RETICULUM_VOXMESH"
    assert "video" in summary["allowed_payloads"]
    assert summary["switched"] is True
    assert summary["user_transparent"] is True
    assert summary["core_rails_changed"] is False
    assert summary["wasm_exposed"] is False
