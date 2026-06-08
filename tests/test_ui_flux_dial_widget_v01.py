from dataclasses import FrozenInstanceError

import pytest

from ui_flux_dial_widget_v01 import (
    ECGPoint,
    FluxDialFrame,
    FluxDialRender,
    flux_dial_widget_invariants,
    guided_link,
    render_flux_dial,
)


def sample_ecg_points():
    return (
        ECGPoint(0.00, 0.52),
        ECGPoint(0.08, 0.52),
        ECGPoint(0.14, 0.50),
        ECGPoint(0.19, 0.38),
        ECGPoint(0.24, 0.52),
        ECGPoint(0.31, 0.54),
        ECGPoint(0.37, 0.56),
        ECGPoint(0.43, 0.18),
        ECGPoint(0.47, 0.86),
        ECGPoint(0.51, 0.52),
        ECGPoint(0.60, 0.52),
        ECGPoint(0.68, 0.50),
        ECGPoint(0.76, 0.40),
        ECGPoint(0.84, 0.51),
        ECGPoint(0.92, 0.54),
        ECGPoint(1.00, 0.52),
    )


def sample_frame(**overrides):
    base = dict(
        timestamp_ms=123456789,
        render_mode="DIAL_WITH_ECG",
        title="WHISPER Flux",
        active_bearer_label="Reticulum",
        state_label="Sol present — delivery attempt allowed",
        needle_angle_deg=132.5,
        latency_label="42 ms",
        jitter_label="7 ms",
        loss_label="0.0%",
        retry_label="0 retries",
        throughput_label="1.25 Mbps",
        fragment_density_label="32%",
        badges=("SOL", "ACK_PENDING", "RETICULUM"),
        ecg_trace_points=sample_ecg_points(),
        ecg_grid_enabled=True,
    )
    base.update(overrides)
    return FluxDialFrame(**base)


def test_guided_link_namespace():
    assert guided_link("x") == "WHISPER_GUIDED_LINK::v1.8.0::ui_flux_dial_widget_v01::x"


def test_render_returns_flux_dial_render():
    frame = sample_frame()
    rendered = render_flux_dial(frame)

    assert isinstance(rendered, FluxDialRender)


def test_render_marks_display_ready():
    frame = sample_frame()
    rendered = render_flux_dial(frame)

    assert rendered.display_ready is True


def test_render_preserves_exact_frame_object():
    frame = sample_frame()
    rendered = render_flux_dial(frame)

    assert rendered.frame is frame


def test_render_preserves_timestamp():
    frame = sample_frame(timestamp_ms=999)
    rendered = render_flux_dial(frame)

    assert rendered.frame.timestamp_ms == 999


def test_render_preserves_render_mode():
    frame = sample_frame(render_mode="COMPACT")
    rendered = render_flux_dial(frame)

    assert rendered.frame.render_mode == "COMPACT"


def test_render_preserves_title():
    frame = sample_frame(title="Custom Dial")
    rendered = render_flux_dial(frame)

    assert rendered.frame.title == "Custom Dial"


def test_render_preserves_active_bearer_label():
    frame = sample_frame(active_bearer_label="LoRa")
    rendered = render_flux_dial(frame)

    assert rendered.frame.active_bearer_label == "LoRa"


def test_render_preserves_state_label():
    frame = sample_frame(state_label="Waiting Sol presence")
    rendered = render_flux_dial(frame)

    assert rendered.frame.state_label == "Waiting Sol presence"


def test_render_preserves_needle_angle_without_clamping():
    frame = sample_frame(needle_angle_deg=999.0)
    rendered = render_flux_dial(frame)

    assert rendered.frame.needle_angle_deg == 999.0


def test_render_preserves_latency_label():
    frame = sample_frame(latency_label="999 ms")
    rendered = render_flux_dial(frame)

    assert rendered.frame.latency_label == "999 ms"


def test_render_preserves_jitter_label():
    frame = sample_frame(jitter_label="77 ms")
    rendered = render_flux_dial(frame)

    assert rendered.frame.jitter_label == "77 ms"


def test_render_preserves_loss_label():
    frame = sample_frame(loss_label="12.5%")
    rendered = render_flux_dial(frame)

    assert rendered.frame.loss_label == "12.5%"


def test_render_preserves_retry_label():
    frame = sample_frame(retry_label="3 retries")
    rendered = render_flux_dial(frame)

    assert rendered.frame.retry_label == "3 retries"


def test_render_preserves_throughput_label():
    frame = sample_frame(throughput_label="900 bps")
    rendered = render_flux_dial(frame)

    assert rendered.frame.throughput_label == "900 bps"


def test_render_preserves_fragment_density_label():
    frame = sample_frame(fragment_density_label="71%")
    rendered = render_flux_dial(frame)

    assert rendered.frame.fragment_density_label == "71%"


def test_render_preserves_badges():
    frame = sample_frame(badges=("LORA", "TEXT_ONLY"))
    rendered = render_flux_dial(frame)

    assert rendered.frame.badges == ("LORA", "TEXT_ONLY")


def test_render_preserves_ecg_trace_points():
    points = (ECGPoint(0.1, 0.2), ECGPoint(0.3, 0.4))
    frame = sample_frame(ecg_trace_points=points)
    rendered = render_flux_dial(frame)

    assert rendered.frame.ecg_trace_points == points


def test_render_preserves_ecg_grid_enabled_true():
    frame = sample_frame(ecg_grid_enabled=True)
    rendered = render_flux_dial(frame)

    assert rendered.frame.ecg_grid_enabled is True


def test_render_preserves_ecg_grid_enabled_false():
    frame = sample_frame(ecg_grid_enabled=False)
    rendered = render_flux_dial(frame)

    assert rendered.frame.ecg_grid_enabled is False


def test_widget_accepts_empty_badges():
    frame = sample_frame(badges=())
    rendered = render_flux_dial(frame)

    assert rendered.frame.badges == ()


def test_widget_accepts_empty_ecg_points():
    frame = sample_frame(ecg_trace_points=())
    rendered = render_flux_dial(frame)

    assert rendered.frame.ecg_trace_points == ()


def test_widget_does_not_recalculate_state_from_labels():
    frame = sample_frame(
        active_bearer_label="Offline",
        state_label="SIGNAL_EXCELLENT",
        needle_angle_deg=180.0,
    )
    rendered = render_flux_dial(frame)

    assert rendered.frame.active_bearer_label == "Offline"
    assert rendered.frame.state_label == "SIGNAL_EXCELLENT"
    assert rendered.frame.needle_angle_deg == 180.0


def test_widget_does_not_reinterpret_lora_payload():
    frame = sample_frame(
        active_bearer_label="LoRa",
        state_label="FILE PAYLOAD DISPLAYED BY WHISPER",
        badges=("FILE_ARTIFACT",),
    )
    rendered = render_flux_dial(frame)

    assert rendered.frame.state_label == "FILE PAYLOAD DISPLAYED BY WHISPER"
    assert rendered.frame.badges == ("FILE_ARTIFACT",)


def test_widget_does_not_compute_or_mutate_ecg_curve():
    points = (ECGPoint(9.0, 9.0), ECGPoint(-1.0, -1.0))
    frame = sample_frame(ecg_trace_points=points)
    rendered = render_flux_dial(frame)

    assert rendered.frame.ecg_trace_points is points
    assert rendered.frame.ecg_trace_points == points


def test_widget_does_not_have_history():
    frame_a = sample_frame(timestamp_ms=1, ecg_trace_points=(ECGPoint(0.1, 0.1),))
    frame_b = sample_frame(timestamp_ms=2, ecg_trace_points=(ECGPoint(0.9, 0.9),))
    rendered_a = render_flux_dial(frame_a)
    rendered_b = render_flux_dial(frame_b)

    assert rendered_a.frame.ecg_trace_points == (ECGPoint(0.1, 0.1),)
    assert rendered_b.frame.ecg_trace_points == (ECGPoint(0.9, 0.9),)
    assert rendered_a.frame is frame_a
    assert rendered_b.frame is frame_b


def test_ecg_point_is_frozen():
    point = ECGPoint(0.1, 0.2)

    with pytest.raises(FrozenInstanceError):
        point.x = 9.0


def test_frame_is_frozen():
    frame = sample_frame()

    with pytest.raises(FrozenInstanceError):
        frame.title = "mutated"


def test_render_is_frozen():
    rendered = render_flux_dial(sample_frame())

    with pytest.raises(FrozenInstanceError):
        rendered.display_ready = False


def test_invariants_are_declared():
    inv = flux_dial_widget_invariants()

    assert inv["widget_receives_prepared_frame"] is True
    assert inv["widget_renders_prepared_frame"] is True
    assert inv["whisper_prepares_display_frame"] is True


def test_widget_receives_precomputed_ecg_points_invariant():
    inv = flux_dial_widget_invariants()

    assert inv["widget_receives_precomputed_ecg_points"] is True
    assert inv["whisper_prepares_ecg_curve"] is True


def test_widget_does_not_compute_ecg_curve_invariant():
    inv = flux_dial_widget_invariants()

    assert inv["widget_does_not_compute_ecg_curve"] is True


def test_widget_contains_no_network_logic_invariant():
    inv = flux_dial_widget_invariants()

    assert inv["widget_contains_no_network_logic"] is True


def test_widget_contains_no_transport_logic_invariant():
    inv = flux_dial_widget_invariants()

    assert inv["widget_contains_no_transport_logic"] is True


def test_widget_contains_no_sol_logic_invariant():
    inv = flux_dial_widget_invariants()

    assert inv["widget_contains_no_sol_logic"] is True


def test_widget_contains_no_ack_logic_invariant():
    inv = flux_dial_widget_invariants()

    assert inv["widget_contains_no_ack_logic"] is True


def test_widget_contains_no_retry_logic_invariant():
    inv = flux_dial_widget_invariants()

    assert inv["widget_contains_no_retry_logic"] is True


def test_widget_contains_no_payload_policy_invariant():
    inv = flux_dial_widget_invariants()

    assert inv["widget_contains_no_payload_policy"] is True


def test_widget_contains_no_history_invariant():
    inv = flux_dial_widget_invariants()

    assert inv["widget_contains_no_history"] is True


def test_widget_has_no_side_effects_invariant():
    inv = flux_dial_widget_invariants()

    assert inv["widget_has_no_side_effects"] is True


def test_widget_does_not_choose_what_to_display_invariant():
    inv = flux_dial_widget_invariants()

    assert inv["widget_does_not_choose_what_to_display"] is True


def test_invariant_count_is_stable():
    assert len(flux_dial_widget_invariants()) == 15
