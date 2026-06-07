from network_medium_selection_v02 import (
    FULL_PAYLOADS,
    TEXT_ONLY_PAYLOADS,
    DaemonNetworkBoundaryState,
    NetworkAvailability,
    apply_network_medium_decision,
    decide_network_medium,
    guided_link,
    is_full_capability_mode,
    is_text_only_mode,
    network_switch_changes_core_rails,
    network_switch_exposes_wasm,
    network_switch_participates_in_immunity,
    network_switch_touches_dome,
)


def test_primary_internet_has_priority_over_4g_5g_and_lora():
    assert guided_link("primary_internet_has_priority_over_4g_5g_and_lora")

    decision = decide_network_medium(NetworkAvailability("AVAILABLE", "AVAILABLE", "AVAILABLE"))

    assert decision.medium == "INTERNET_PRIMARY"
    assert decision.mode == "CONNECTED"
    assert decision.stack == "RETICULUM_VOXMESH"
    assert decision.allowed_payloads == FULL_PAYLOADS
    assert is_full_capability_mode(decision) is True


def test_4g_5g_used_when_primary_internet_unavailable():
    assert guided_link("4g_5g_used_when_primary_internet_unavailable")

    decision = decide_network_medium(NetworkAvailability("UNAVAILABLE", "AVAILABLE", "AVAILABLE"))

    assert decision.medium == "MOBILE_DATA_4G_5G"
    assert decision.mode == "CONNECTED"
    assert decision.stack == "RETICULUM_VOXMESH"
    assert decision.allowed_payloads == FULL_PAYLOADS
    assert is_full_capability_mode(decision) is True


def test_lora_used_only_when_primary_and_mobile_unavailable():
    assert guided_link("lora_used_only_when_primary_and_mobile_unavailable")

    decision = decide_network_medium(NetworkAvailability("UNAVAILABLE", "UNAVAILABLE", "AVAILABLE"))

    assert decision.medium == "LORA_FALLBACK"
    assert decision.mode == "DEGRADED_SURVIVAL"
    assert decision.stack == "LORA_TEXT"
    assert decision.allowed_payloads == TEXT_ONLY_PAYLOADS
    assert is_text_only_mode(decision) is True


def test_offline_when_no_medium_available():
    assert guided_link("offline_when_no_medium_available")

    decision = decide_network_medium(NetworkAvailability("UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE"))

    assert decision.medium == "NONE"
    assert decision.mode == "OFFLINE"
    assert decision.stack == "NONE"
    assert decision.allowed_payloads == set()


def test_4g_5g_is_not_degraded_mode():
    assert guided_link("4g_5g_is_not_degraded_mode")

    decision = decide_network_medium(NetworkAvailability("UNAVAILABLE", "AVAILABLE", "UNAVAILABLE"))

    assert decision.medium == "MOBILE_DATA_4G_5G"
    assert decision.mode == "CONNECTED"
    assert decision.allowed_payloads == FULL_PAYLOADS
    assert "video" in decision.allowed_payloads
    assert "audio" in decision.allowed_payloads


def test_lora_is_text_only():
    assert guided_link("lora_is_text_only")

    decision = decide_network_medium(NetworkAvailability("UNAVAILABLE", "UNAVAILABLE", "AVAILABLE"))

    assert decision.allowed_payloads == {"text"}
    assert "audio" not in decision.allowed_payloads
    assert "image" not in decision.allowed_payloads
    assert "video" not in decision.allowed_payloads
    assert "file" not in decision.allowed_payloads


def test_apply_decision_to_daemon_boundary():
    assert guided_link("apply_decision_to_daemon_boundary")

    daemon = DaemonNetworkBoundaryState()
    decision = decide_network_medium(NetworkAvailability("UNAVAILABLE", "AVAILABLE", "AVAILABLE"))

    apply_network_medium_decision(daemon, decision)

    assert daemon.medium == "MOBILE_DATA_4G_5G"
    assert daemon.mode == "CONNECTED"
    assert daemon.stack == "RETICULUM_VOXMESH"
    assert daemon.allowed_payloads == FULL_PAYLOADS


def test_network_switch_does_not_touch_core_organs():
    assert guided_link("network_switch_does_not_touch_core_organs")

    daemon = DaemonNetworkBoundaryState()

    assert network_switch_changes_core_rails(daemon) is False
    assert network_switch_exposes_wasm(daemon) is False
    assert network_switch_touches_dome(daemon) is False
    assert network_switch_participates_in_immunity(daemon) is False
