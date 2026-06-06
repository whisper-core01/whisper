"""
WHISPER — Nerve Mobile Runtime v0.1

Purpose:
Define the life of the mobile nerve after boot/admission.

The runtime does not think.

It transmits.

It never reopens the Mobile Vault.

It does not perform admission.

It does not hold Whisper secrets.

It only:
- receives user events
- wraps them into JSON-like envelopes
- sends them into the Sol
- receives Core responses
- renders them
- updates a minimal runtime status

Core rule:

The Vault opens for birth.
It closes before life.
The runtime only lets current pass.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal


UserEventType = Literal["text", "audio", "image", "file", "gesture"]
RuntimeStatus = Literal[
    "WHISPER_RESPONDING",
    "WHISPER_SILENT",
    "OFFLINE",
]
TransportResult = Literal["sent", "offline", "error"]


@dataclass(frozen=True)
class UserEvent:
    event_type: UserEventType
    payload: Dict[str, Any]
    event_nonce: str


@dataclass(frozen=True)
class NerveRuntimeEnvelope:
    nerve: str
    kind: str
    input: Dict[str, Any]
    meta: Dict[str, Any]


@dataclass(frozen=True)
class CoreResponse:
    response_type: str
    payload: Dict[str, Any]
    response_nonce: str


@dataclass
class RuntimeState:
    status: RuntimeStatus = "WHISPER_SILENT"
    vault_opened_after_boot: bool = False
    admission_attempted_after_boot: bool = False
    sent_count: int = 0
    received_count: int = 0
    rendered_count: int = 0
    errors: List[str] = field(default_factory=list)


@dataclass
class MockSolChannel:
    online: bool = True
    outbound: List[NerveRuntimeEnvelope] = field(default_factory=list)
    inbound: List[CoreResponse] = field(default_factory=list)

    def send(self, envelope: NerveRuntimeEnvelope) -> TransportResult:
        if not self.online:
            return "offline"

        self.outbound.append(envelope)
        return "sent"

    def receive(self) -> CoreResponse | None:
        if not self.online:
            return None

        if not self.inbound:
            return None

        return self.inbound.pop(0)


def _require_non_empty(name: str, value: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")


def validate_user_event(event: UserEvent) -> None:
    if event.event_type not in {"text", "audio", "image", "file", "gesture"}:
        raise ValueError(f"unsupported event_type: {event.event_type}")

    if not isinstance(event.payload, dict):
        raise ValueError("payload must be a dict")

    _require_non_empty("event_nonce", event.event_nonce)


def make_nerve_envelope(event: UserEvent) -> NerveRuntimeEnvelope:
    """
    Wrap a user event into a Nerve runtime envelope.

    No Vault data.

    No admission data.

    No binding.

    No identity.
    """
    validate_user_event(event)

    return NerveRuntimeEnvelope(
        nerve="mobile",
        kind="runtime_input",
        input={
            "type": event.event_type,
            "payload": dict(event.payload),
        },
        meta={
            "event_nonce": event.event_nonce,
            "runtime": "stateless",
            "vault": "closed",
            "admission": "not_performed",
        },
    )


def send_to_sol(
    channel: MockSolChannel,
    envelope: NerveRuntimeEnvelope,
    state: RuntimeState,
) -> TransportResult:
    result = channel.send(envelope)

    if result == "sent":
        state.sent_count += 1
        return "sent"

    if result == "offline":
        state.status = "OFFLINE"
        state.errors.append("sol_channel_offline")
        return "offline"

    state.status = "WHISPER_SILENT"
    state.errors.append("sol_channel_error")
    return "error"


def read_from_sol(
    channel: MockSolChannel,
    state: RuntimeState,
) -> CoreResponse | None:
    response = channel.receive()

    if response is None:
        if state.status != "OFFLINE":
            state.status = "WHISPER_SILENT"
        return None

    state.received_count += 1
    state.status = "WHISPER_RESPONDING"
    return response


def render_response(
    response: CoreResponse | None,
    state: RuntimeState,
) -> Dict[str, Any] | None:
    """
    Render a Core response into a minimal UI-facing dict.

    Prototype only.
    """
    if response is None:
        return None

    state.rendered_count += 1

    return {
        "type": response.response_type,
        "payload": dict(response.payload),
        "response_nonce": response.response_nonce,
    }


def update_runtime_state(
    response: CoreResponse | None,
    state: RuntimeState,
) -> RuntimeStatus:
    if response is None:
        if state.status != "OFFLINE":
            state.status = "WHISPER_SILENT"
        return state.status

    state.status = "WHISPER_RESPONDING"
    return state.status


def runtime_step(
    event: UserEvent,
    channel: MockSolChannel,
    state: RuntimeState,
) -> Dict[str, Any] | None:
    """
    Execute one runtime I/O step.

    No Vault access.

    No admission.

    No identity logic.
    """
    envelope = make_nerve_envelope(event)
    result = send_to_sol(channel, envelope, state)

    if result != "sent":
        return None

    response = read_from_sol(channel, state)
    rendered = render_response(response, state)
    update_runtime_state(response, state)

    return rendered


def runtime_invariants_ok(state: RuntimeState) -> bool:
    return (
        state.vault_opened_after_boot is False
        and state.admission_attempted_after_boot is False
    )


def runtime_loop(
    events: List[UserEvent],
    channel: MockSolChannel,
) -> RuntimeState:
    """
    Prototype bounded runtime loop.

    It processes a finite event list for tests.
    """
    state = RuntimeState()

    for event in events:
        runtime_step(event, channel, state)

    return state


if __name__ == "__main__":
    channel = MockSolChannel(
        online=True,
        inbound=[
            CoreResponse(
                response_type="text",
                payload={"text": "Whisper répond."},
                response_nonce="response-1",
            )
        ],
    )

    state = RuntimeState()

    rendered = runtime_step(
        UserEvent(
            event_type="text",
            payload={"text": "hello"},
            event_nonce="event-1",
        ),
        channel,
        state,
    )

    print("Rendered:", rendered)
    print("Runtime status:", state.status)
    print("Vault opened after boot:", state.vault_opened_after_boot)
    print("Admission attempted after boot:", state.admission_attempted_after_boot)
    print("Invariants OK:", runtime_invariants_ok(state))
