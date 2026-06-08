"""
WHISPER — Flux Dial Widget v0.1

Display-only widget.

WHISPER prepares the complete display frame.
The widget only renders the frame it receives.

No network logic.
No transport logic.
No Sol logic.
No ACK logic.
No retry logic.
No payload policy.
No history.
No side effects.

WHISPER prepares the curve.
The widget draws the curve.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Tuple


RenderMode = Literal[
    "DIAL_WITH_ECG",
    "DIAL_ONLY",
    "ECG_ONLY",
    "COMPACT",
]


@dataclass(frozen=True)
class ECGPoint:
    """
    One precomputed visual point of the ECG-like network trace.

    Coordinates are already prepared by WHISPER.
    The widget must not infer network meaning from them.
    """

    x: float
    y: float


@dataclass(frozen=True)
class FluxDialFrame:
    """
    Fully prepared display frame produced by WHISPER.

    The widget must not derive or reinterpret transport state from this.
    It only renders these fields.
    """

    timestamp_ms: int
    render_mode: RenderMode
    title: str
    active_bearer_label: str
    state_label: str
    needle_angle_deg: float
    latency_label: str
    jitter_label: str
    loss_label: str
    retry_label: str
    throughput_label: str
    fragment_density_label: str
    badges: Tuple[str, ...]
    ecg_trace_points: Tuple[ECGPoint, ...]
    ecg_grid_enabled: bool = True


@dataclass(frozen=True)
class FluxDialRender:
    """
    Passive render object returned to the UI layer.

    It mirrors the prepared frame.
    """

    frame: FluxDialFrame
    display_ready: bool = True


def render_flux_dial(frame: FluxDialFrame) -> FluxDialRender:
    """
    Render a WHISPER-prepared FluxDialFrame.

    No calculation.
    No decision.
    No interpretation.
    """

    return FluxDialRender(frame=frame)


def flux_dial_widget_invariants() -> Dict[str, bool]:
    return {
        "widget_receives_prepared_frame": True,
        "widget_renders_prepared_frame": True,
        "widget_receives_precomputed_ecg_points": True,
        "widget_does_not_compute_ecg_curve": True,
        "widget_contains_no_network_logic": True,
        "widget_contains_no_transport_logic": True,
        "widget_contains_no_sol_logic": True,
        "widget_contains_no_ack_logic": True,
        "widget_contains_no_retry_logic": True,
        "widget_contains_no_payload_policy": True,
        "widget_contains_no_history": True,
        "widget_has_no_side_effects": True,
        "whisper_prepares_display_frame": True,
        "whisper_prepares_ecg_curve": True,
        "widget_does_not_choose_what_to_display": True,
    }


def guided_link(test_name: str) -> str:
    return f"WHISPER_GUIDED_LINK::v1.8.0::ui_flux_dial_widget_v01::{test_name}"


def smoke_demo() -> None:
    print("WHISPER Flux Dial Widget v0.1 — Smoke Test")

    frame = FluxDialFrame(
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
        ecg_trace_points=(
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
        ),
        ecg_grid_enabled=True,
    )

    rendered = render_flux_dial(frame)

    print("Display ready:", rendered.display_ready)
    print("Title:", rendered.frame.title)
    print("Bearer:", rendered.frame.active_bearer_label)
    print("State:", rendered.frame.state_label)
    print("Needle angle:", rendered.frame.needle_angle_deg)
    print("Badges:", ",".join(rendered.frame.badges))
    print("ECG point count:", len(rendered.frame.ecg_trace_points))
    print("ECG grid enabled:", rendered.frame.ecg_grid_enabled)
    print("First ECG point:", rendered.frame.ecg_trace_points[0])
    print("Invariant count:", len(flux_dial_widget_invariants()))


if __name__ == "__main__":
    smoke_demo()
