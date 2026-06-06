"""
WHISPER — Nerve Mobile Transport v0.1

Purpose:
Define how Nerve Mobile emits impulses into the Sol.

The Nerve does not connect.

It emits.

The Sol responds, or stays silent.

Transport v0.1 must not introduce:
- connection semantics
- sessions
- identity
- handshake
- token
- secret
- persistent state

It is JSON in/out, weakly reliable, stateless, and non-sovereign.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal


TransportStatus = Literal[
    "WHISPER_RESPONDING",
    "WHISPER_SILENT",
    "OFFLINE",
]

TransportSendResult = Literal[
    "emitted",
    "offline",
    "error",
]

TransportEnvelopeKind = Literal[
    "input",
]

ResponseType = Literal[
    "text",
    "audio",
    "image",
    "video",
    "event",
]


@dataclass(frozen=True)
class NerveTransportEnvelope:
    nerve: str
    kind: TransportEnvelopeKind
    capabilities: List[str]
    payload: Dict[str, Any]
    input_nonce: str


@dataclass(frozen=True)
class SolResponseEnvelope:
    type: ResponseType
    payload: Dict[str, Any]
    response_nonce: str


@dataclass
class TransportRuntime:
    status: TransportStatus = "WHISPER_SILENT"
    emitted_count: int = 0
    received_count: int = 0
    silence_count: int = 0
    offline_count: int = 0
    error_count: int = 0
    attempted_connections: int = 0
    stored_state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MockSolTransport:
    online: bool = True
    fail_next_send: bool = False
    emitted: List[NerveTransportEnvelope] = field(default_factory=list)
    responses: List[SolResponseEnvelope] = field(default_factory=list)

    def emit(self, envelope: NerveTransportEnvelope) -> TransportSendResult:
        if self.fail_next_send:
            self.fail_next_send = False
            return "error"

        if not self.online:
            return "offline"

        self.emitted.append(envelope)
        return "emitted"

    def poll(self) -> SolResponseEnvelope | None:
        if not self.online:
            return None

        if not self.responses:
            return None

        return self.responses.pop(0)


SUPPORTED_RUNTIME_CAPABILITIES = {
    "text",
    "audio",
    "image",
    "video",
    "event",
    "location_hint",
    "file",
}


def _require_non_empty(name: str, value: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")


def _require_capabilities(capabilities: List[str]) -> None:
    if not capabilities:
        raise ValueError("capabilities must not be empty")

    for capability in capabilities:
        _require_non_empty("capability", capability)


def make_transport_envelope(
    capabilities: List[str],
    payload: Dict[str, Any],
    input_nonce: str,
) -> NerveTransportEnvelope:
    """
    Build an impulse envelope from Nerve Mobile into the Sol.

    This envelope must not contain:
    - identity
    - session
    - token
    - key
    - Vault material
    - admission material
    - binding
    """
    _require_capabilities(capabilities)
    _require_non_empty("input_nonce", input_nonce)

    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    return NerveTransportEnvelope(
        nerve="mobile",
        kind="input",
        capabilities=list(capabilities),
        payload=dict(payload),
        input_nonce=input_nonce,
    )


def send_to_sol(
    transport: MockSolTransport,
    runtime: TransportRuntime,
    envelope: NerveTransportEnvelope,
) -> TransportSendResult:
    """
    Emit an envelope into the Sol.

    This is not a connection.

    It is an impulse emission.
    """
    result = transport.emit(envelope)

    if result == "emitted":
        runtime.emitted_count += 1
        return result

    if result == "offline":
        runtime.offline_count += 1
        runtime.status = "OFFLINE"
        return result

    runtime.error_count += 1
    runtime.status = "WHISPER_SILENT"
    return "error"


def receive_from_sol(
    transport: MockSolTransport,
    runtime: TransportRuntime,
) -> SolResponseEnvelope | None:
    """
    Poll for a Sol response.

    The Sol may respond.

    The Sol may stay silent.
    """
    response = transport.poll()

    if response is None:
        if runtime.status != "OFFLINE":
            runtime.status = "WHISPER_SILENT"
        runtime.silence_count += 1
        return None

    runtime.received_count += 1
    runtime.status = "WHISPER_RESPONDING"
    return response


def transport_status(runtime: TransportRuntime) -> TransportStatus:
    return runtime.status


def retry_backoff_hint(runtime: TransportRuntime) -> int:
    """
    Return a minimal retry/backoff hint.

    The Nerve does not reconnect.

    It keeps emitting with a small delay hint when transport is unhealthy.
    """
    failures = runtime.offline_count + runtime.error_count
    return min(5, failures)


def transport_step(
    transport: MockSolTransport,
    runtime: TransportRuntime,
    envelope: NerveTransportEnvelope,
) -> SolResponseEnvelope | None:
    """
    Execute one transport impulse step.
    """
    result = send_to_sol(transport, runtime, envelope)

    if result != "emitted":
        return None

    return receive_from_sol(transport, runtime)


def transport_loop(
    transport: MockSolTransport,
    envelopes: List[NerveTransportEnvelope],
) -> TransportRuntime:
    """
    Bounded transport loop for tests.

    No connection.

    No session.

    No identity.
    """
    runtime = TransportRuntime()

    for envelope in envelopes:
        transport_step(transport, runtime, envelope)

    return runtime


def transport_invariants_ok(runtime: TransportRuntime) -> bool:
    """
    Verify that transport did not become a client/session/identity layer.
    """
    return (
        runtime.attempted_connections == 0
        and runtime.stored_state == {}
    )


def transport_affects_admission() -> bool:
    return False


def transport_affects_continuity() -> bool:
    return False


def envelope_has_no_identity_or_secret(envelope: NerveTransportEnvelope) -> bool:
    forbidden_keys = {
        "identity",
        "session",
        "token",
        "secret",
        "key",
        "vault",
        "binding",
        "admission",
    }

    payload_keys = set(envelope.payload.keys())

    return not bool(payload_keys & forbidden_keys)


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

    envelope = make_transport_envelope(
        capabilities=["text", "audio", "image", "video", "event"],
        payload={"type": "text", "text": "hello"},
        input_nonce="input-1",
    )

    response = transport_step(
        transport=transport,
        runtime=runtime,
        envelope=envelope,
    )

    print("Transport response:", response)
    print("Transport status:", transport_status(runtime))
    print("Attempted connections:", runtime.attempted_connections)
    print("Stored state:", runtime.stored_state)
    print("Invariants OK:", transport_invariants_ok(runtime))
