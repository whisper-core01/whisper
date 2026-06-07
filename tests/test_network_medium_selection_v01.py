from network_medium_selection_v01 import (
    CONNECTED_PAYLOADS,
    DEGRADED_PAYLOADS,
    DaemonNetworkBoundaryState,
    NetworkProbeResult,
    OutgoingPayload,
    apply_network_medium_decision,
    connected_mode_allows_full_payloads,
    daemon_reads_payload,
    decide_network_medium,
    degraded_mode_allows_only_text,
    filter_payloads_for_medium,
    guided_link,
    lora_is_internal_organ,
    network_mode_changes_core_rails,
    network_mode_changes_dome_validity,
    network_mode_exposes_wasm,
    network_mode_participates_in_immunity,
    network_mode_summary,
    payload_allowed_in_mode,
    reticulum_is_internal_organ,
)


def test_internet_available_selects_reticulum_connected_mode():
    assert guided_link("internet_available_selects_reticulum_connected_mode")

    decision = decide_network_medium(
        NetworkProbeResult(
            internet_state="INTERNET_AVAILABLE",
            responding_probe_count=5,
            sampled_probe_count=5,
        )
    )

    assert decision.mode == "CONNECTED"
    assert decision.medium == "RETICULUM_INTERNET"
    assert decision.allowed_payloads == CONNECTED_PAYLOADS
    assert connected_mode_allows_full_payloads(decision) is True


def test_internet_degraded_still_uses_reticulum_connected_mode():
    assert guided_link("internet_degraded_still_uses_reticulum_connected_mode")

    decision = decide_network_medium(
        NetworkProbeResult(
            internet_state="INTERNET_DEGRADED",
            responding_probe_count=2,
            sampled_probe_count=5,
        )
    )

    assert decision.mode == "CONNECTED"
    assert decision.medium == "RETICULUM_INTERNET"
    assert decision.allowed_payloads == CONNECTED_PAYLOADS


def test_internet_unavailable_selects_lora_degraded_text_only():
    assert guided_link("internet_unavailable_selects_lora_degraded_text_only")

    decision = decide_network_medium(
        NetworkProbeResult(
            internet_state="INTERNET_UNAVAILABLE",
            responding_probe_count=0,
            sampled_probe_count=5,
        )
    )

    assert decision.mode == "DEGRADED"
    assert decision.medium == "LORA_FALLBACK"
    assert decision.allowed_payloads == DEGRADED_PAYLOADS
    assert degraded_mode_allows_only_text(decision) is True


def test_degraded_mode_rejects_audio_image_video_file_event():
    assert guided_link("degraded_mode_rejects_audio_image_video_file_event")

    decision = decide_network_medium(
        NetworkProbeResult(
            internet_state="INTERNET_UNAVAILABLE",
            responding_probe_count=0,
            sampled_probe_count=5,
        )
    )

    assert payload_allowed_in_mode(
        OutgoingPayload(payload_id="p-text", kind="text", body="hello"),
        decision,
    ) is True

    for kind in ["audio", "image", "video", "file", "event"]:
        assert payload_allowed_in_mode(
            OutgoingPayload(payload_id=f"p-{kind}", kind=kind, body="blocked"),
            decision,
        ) is False


def test_connected_mode_allows_all_payloads():
    assert guided_link("connected_mode_allows_all_payloads")

    decision = decide_network_medium(
        NetworkProbeResult(
            internet_state="INTERNET_AVAILABLE",
            responding_probe_count=5,
            sampled_probe_count=5,
        )
    )

    for kind in ["text", "audio", "image", "video", "file", "event"]:
        assert payload_allowed_in_mode(
            OutgoingPayload(payload_id=f"p-{kind}", kind=kind, body="ok"),
            decision,
        ) is True


def test_filter_payloads_for_lora_degraded_keeps_only_text():
    assert guided_link("filter_payloads_for_lora_degraded_keeps_only_text")

    decision = decide_network_medium(
        NetworkProbeResult(
            internet_state="INTERNET_UNAVAILABLE",
            responding_probe_count=0,
            sampled_probe_count=5,
        )
    )

    payloads = [
        OutgoingPayload(payload_id="p1", kind="text", body="hello"),
        OutgoingPayload(payload_id="p2", kind="image", body="image"),
        OutgoingPayload(payload_id="p3", kind="audio", body="audio"),
        OutgoingPayload(payload_id="p4", kind="video", body="video"),
    ]

    filtered = filter_payloads_for_medium(payloads, decision)

    assert [p.payload_id for p in filtered] == ["p1"]


def test_apply_network_decision_to_daemon_boundary_state():
    assert guided_link("apply_network_decision_to_daemon_boundary_state")

    daemon = DaemonNetworkBoundaryState()
    decision = decide_network_medium(
        NetworkProbeResult(
            internet_state="INTERNET_UNAVAILABLE",
            responding_probe_count=0,
            sampled_probe_count=5,
        )
    )

    apply_network_medium_decision(daemon, decision)

    assert daemon.mode == "DEGRADED"
    assert daemon.selected_medium == "LORA_FALLBACK"
    assert daemon.allowed_payloads == {"text"}


def test_lora_and_reticulum_are_not_internal_organs():
    assert guided_link("lora_and_reticulum_are_not_internal_organs")

    assert lora_is_internal_organ() is False
    assert reticulum_is_internal_organ() is False


def test_network_mode_does_not_change_core_rails_or_expose_wasm():
    assert guided_link("network_mode_does_not_change_core_rails_or_expose_wasm")

    daemon = DaemonNetworkBoundaryState()

    assert network_mode_changes_core_rails(daemon) is False
    assert network_mode_exposes_wasm(daemon) is False


def test_network_mode_does_not_touch_dome_immunity_or_payload():
    assert guided_link("network_mode_does_not_touch_dome_immunity_or_payload")

    daemon = DaemonNetworkBoundaryState()

    assert network_mode_changes_dome_validity(daemon) is False
    assert network_mode_participates_in_immunity(daemon) is False
    assert daemon_reads_payload(daemon) is False


def test_probe_validation_rejects_invalid_counts():
    assert guided_link("probe_validation_rejects_invalid_counts")

    try:
        decide_network_medium(
            NetworkProbeResult(
                internet_state="INTERNET_AVAILABLE",
                responding_probe_count=1,
                sampled_probe_count=0,
            )
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected sampled count validation error")

    try:
        decide_network_medium(
            NetworkProbeResult(
                internet_state="INTERNET_AVAILABLE",
                responding_probe_count=6,
                sampled_probe_count=5,
            )
        )
    except ValueError:
        return

    raise AssertionError("Expected responding count validation error")


def test_network_mode_summary_connected_and_degraded():
    assert guided_link("network_mode_summary_connected_and_degraded")

    connected = network_mode_summary(
        NetworkProbeResult(
            internet_state="INTERNET_AVAILABLE",
            responding_probe_count=5,
            sampled_probe_count=5,
        )
    )

    degraded = network_mode_summary(
        NetworkProbeResult(
            internet_state="INTERNET_UNAVAILABLE",
            responding_probe_count=0,
            sampled_probe_count=5,
        )
    )

    assert connected["mode"] == "CONNECTED"
    assert connected["medium"] == "RETICULUM_INTERNET"
    assert "video" in connected["allowed_payloads"]

    assert degraded["mode"] == "DEGRADED"
    assert degraded["medium"] == "LORA_FALLBACK"
    assert degraded["allowed_payloads"] == ["text"]
    assert degraded["core_rails_changed"] is False
    assert degraded["wasm_exposed"] is False
