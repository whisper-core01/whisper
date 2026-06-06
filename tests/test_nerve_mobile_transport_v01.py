from nerve_mobile_transport_v01 import (
    MockSolTransport,
    NerveTransportEnvelope,
    SolResponseEnvelope,
    TransportRuntime,
    envelope_has_no_identity_or_secret,
    make_transport_envelope,
    receive_from_sol,
    retry_backoff_hint,
    send_to_sol,
    transport_affects_admission,
    transport_affects_continuity,
    transport_invariants_ok,
    transport_loop,
    transport_status,
    transport_step,
)


def _envelope():
    return make_transport_envelope(
        capabilities=["text", "audio", "image", "video", "event"],
        payload={"type": "text", "text": "hello"},
        input_nonce="input-1",
    )


def test_transport_sends_envelopes_correctly():
    transport = MockSolTransport(online=True)
    runtime = TransportRuntime()
    envelope = _envelope()

    result = send_to_sol(transport, runtime, envelope)

    assert result == "emitted"
    assert runtime.emitted_count == 1
    assert len(transport.emitted) == 1
    assert transport.emitted[0] == envelope


def test_transport_receives_responses_correctly():
    transport = MockSolTransport(
        online=True,
        responses=[
            SolResponseEnvelope(
                type="text",
                payload={"text": "ok"},
                response_nonce="response-1",
            )
        ],
    )
    runtime = TransportRuntime()

    response = receive_from_sol(transport, runtime)

    assert response is not None
    assert response.type == "text"
    assert runtime.received_count == 1
    assert runtime.status == "WHISPER_RESPONDING"


def test_transport_handles_silence():
    transport = MockSolTransport(online=True)
    runtime = TransportRuntime()

    response = receive_from_sol(transport, runtime)

    assert response is None
    assert runtime.silence_count == 1
    assert runtime.status == "WHISPER_SILENT"


def test_transport_handles_offline():
    transport = MockSolTransport(online=False)
    runtime = TransportRuntime()

    result = send_to_sol(transport, runtime, _envelope())

    assert result == "offline"
    assert runtime.offline_count == 1
    assert runtime.status == "OFFLINE"


def test_transport_handles_send_error():
    transport = MockSolTransport(online=True, fail_next_send=True)
    runtime = TransportRuntime()

    result = send_to_sol(transport, runtime, _envelope())

    assert result == "error"
    assert runtime.error_count == 1
    assert runtime.status == "WHISPER_SILENT"


def test_transport_step_sends_and_receives():
    transport = MockSolTransport(
        online=True,
        responses=[
            SolResponseEnvelope(
                type="text",
                payload={"text": "ok"},
                response_nonce="response-1",
            )
        ],
    )
    runtime = TransportRuntime()

    response = transport_step(transport, runtime, _envelope())

    assert response is not None
    assert response.payload["text"] == "ok"
    assert runtime.emitted_count == 1
    assert runtime.received_count == 1
    assert runtime.status == "WHISPER_RESPONDING"


def test_transport_step_handles_no_response():
    transport = MockSolTransport(online=True)
    runtime = TransportRuntime()

    response = transport_step(transport, runtime, _envelope())

    assert response is None
    assert runtime.emitted_count == 1
    assert runtime.silence_count == 1
    assert runtime.status == "WHISPER_SILENT"


def test_transport_does_not_attempt_connection():
    transport = MockSolTransport(online=True)
    runtime = transport_loop(transport, [_envelope(), _envelope()])

    assert runtime.attempted_connections == 0
    assert transport_invariants_ok(runtime) is True


def test_transport_does_not_store_state():
    runtime = TransportRuntime()

    assert runtime.stored_state == {}
    assert transport_invariants_ok(runtime) is True


def test_transport_does_not_affect_admission():
    assert transport_affects_admission() is False


def test_transport_does_not_affect_continuity():
    assert transport_affects_continuity() is False


def test_envelope_has_no_identity_or_secret():
    envelope = _envelope()

    assert envelope_has_no_identity_or_secret(envelope) is True


def test_envelope_with_forbidden_payload_key_rejected_by_invariant():
    envelope = NerveTransportEnvelope(
        nerve="mobile",
        kind="input",
        capabilities=["text"],
        payload={"identity": "bad"},
        input_nonce="input-1",
    )

    assert envelope_has_no_identity_or_secret(envelope) is False


def test_retry_backoff_hint_increases_with_failures():
    runtime = TransportRuntime()

    assert retry_backoff_hint(runtime) == 0

    runtime.offline_count = 2
    runtime.error_count = 2

    assert retry_backoff_hint(runtime) == 4

    runtime.offline_count = 10
    runtime.error_count = 10

    assert retry_backoff_hint(runtime) == 5


def test_transport_status_returns_status():
    runtime = TransportRuntime(status="WHISPER_SILENT")

    assert transport_status(runtime) == "WHISPER_SILENT"
