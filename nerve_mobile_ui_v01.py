"""
WHISPER — Nerve Mobile UI v0.1

Purpose:
Define the minimal human-facing membrane of Nerve Mobile.

The UI is not an app shell.

It is not a client.

It is not a configuration surface.

It is a sensory membrane.

It shows:
- what the human sends
- what WHISPER returns
- one of three statuses

It must not show:
- internal JSON
- Sol challenges
- admission codes
- binding prefixes
- revocation state
- Vault state
- identities
- sessions
- network configuration
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal

from nerve_mobile_transport_v01 import (
    MockSolTransport,
    SolResponseEnvelope,
    TransportRuntime,
    TransportStatus,
    make_transport_envelope,
    receive_from_sol,
    send_to_sol,
    transport_status,
)


UIInputType = Literal["text", "audio", "image", "video", "event"]
UIRenderType = Literal["text", "audio", "image", "video", "event", "empty"]


@dataclass(frozen=True)
class UIInput:
    input_type: UIInputType
    payload: Dict[str, Any]
    input_nonce: str


@dataclass(frozen=True)
class UIRenderedItem:
    render_type: UIRenderType
    payload: Dict[str, Any]


@dataclass
class NerveMobileUIState:
    visible_items: List[UIRenderedItem] = field(default_factory=list)
    status: TransportStatus = "WHISPER_SILENT"
    vault_access_attempted: bool = False
    admission_attempted: bool = False
    internal_json_exposed: bool = False
    stored_internal_state: Dict[str, Any] = field(default_factory=dict)


def _require_non_empty(name: str, value: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")


def validate_ui_input(ui_input: UIInput) -> None:
    if ui_input.input_type not in {"text", "audio", "image", "video", "event"}:
        raise ValueError(f"unsupported input_type: {ui_input.input_type}")

    if not isinstance(ui_input.payload, dict):
        raise ValueError("payload must be a dict")

    _require_non_empty("input_nonce", ui_input.input_nonce)


def render_human_input(ui_input: UIInput) -> UIRenderedItem:
    """
    Render what the human sends.

    No metadata.

    No timestamp.

    No identity.
    """
    validate_ui_input(ui_input)

    return UIRenderedItem(
        render_type=ui_input.input_type,
        payload=dict(ui_input.payload),
    )


def render_core_response(response: SolResponseEnvelope | None) -> UIRenderedItem:
    """
    Render what WHISPER returns.

    The UI does not expose transport internals.
    """
    if response is None:
        return UIRenderedItem(
            render_type="empty",
            payload={},
        )

    return UIRenderedItem(
        render_type=response.type,
        payload=dict(response.payload),
    )


def update_ui_status(
    ui_state: NerveMobileUIState,
    runtime: TransportRuntime,
) -> TransportStatus:
    ui_state.status = transport_status(runtime)
    return ui_state.status


def ui_submit_input(
    ui_input: UIInput,
    capabilities: List[str],
    transport: MockSolTransport,
    runtime: TransportRuntime,
    ui_state: NerveMobileUIState,
) -> UIRenderedItem | None:
    """
    Submit one human input through the Nerve membrane.

    The UI:
    - renders the human input
    - wraps it into a transport envelope
    - emits it into the Sol
    - renders an optional WHISPER response
    - updates status

    The UI does not:
    - access Vault
    - trigger admission
    - expose JSON
    - store internal state
    """
    validate_ui_input(ui_input)

    human_item = render_human_input(ui_input)
    ui_state.visible_items.append(human_item)

    envelope = make_transport_envelope(
        capabilities=capabilities,
        payload={
            "type": ui_input.input_type,
            "payload": dict(ui_input.payload),
        },
        input_nonce=ui_input.input_nonce,
    )

    result = send_to_sol(
        transport=transport,
        runtime=runtime,
        envelope=envelope,
    )

    if result != "emitted":
        update_ui_status(ui_state, runtime)
        return None

    response = receive_from_sol(transport, runtime)
    rendered = render_core_response(response)

    if rendered.render_type != "empty":
        ui_state.visible_items.append(rendered)

    update_ui_status(ui_state, runtime)

    return rendered if rendered.render_type != "empty" else None


def ui_loop(
    inputs: List[UIInput],
    capabilities: List[str],
    transport: MockSolTransport,
) -> NerveMobileUIState:
    """
    Bounded UI loop for tests.

    No configuration.

    No connection screen.

    No debug panel.
    """
    runtime = TransportRuntime()
    ui_state = NerveMobileUIState()

    for ui_input in inputs:
        ui_submit_input(
            ui_input=ui_input,
            capabilities=capabilities,
            transport=transport,
            runtime=runtime,
            ui_state=ui_state,
        )

    return ui_state


def ui_invariants_ok(ui_state: NerveMobileUIState) -> bool:
    return (
        ui_state.vault_access_attempted is False
        and ui_state.admission_attempted is False
        and ui_state.internal_json_exposed is False
        and ui_state.stored_internal_state == {}
    )


def ui_has_no_configuration_surface() -> bool:
    """
    v01 has no network configuration, account screen, QR flow, or server picker.
    """
    return True


def ui_status_label(status: TransportStatus) -> str:
    if status == "WHISPER_RESPONDING":
        return "Whisper répond"

    if status == "WHISPER_SILENT":
        return "Whisper silencieux"

    if status == "OFFLINE":
        return "Hors-ligne"

    raise ValueError(f"unsupported status: {status}")


if __name__ == "__main__":
    transport = MockSolTransport(
        online=True,
        responses=[
            SolResponseEnvelope(
                type="text",
                payload={"text": "Whisper répond."},
                response_nonce="response-1",
            )
        ],
    )

    runtime = TransportRuntime()
    ui_state = NerveMobileUIState()

    rendered = ui_submit_input(
        ui_input=UIInput(
            input_type="text",
            payload={"text": "hello"},
            input_nonce="input-1",
        ),
        capabilities=["text", "audio", "image", "video", "event"],
        transport=transport,
        runtime=runtime,
        ui_state=ui_state,
    )

    print("Rendered:", rendered)
    print("UI status:", ui_state.status)
    print("UI label:", ui_status_label(ui_state.status))
    print("Visible items:", len(ui_state.visible_items))
    print("UI invariants OK:", ui_invariants_ok(ui_state))
