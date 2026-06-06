from nerve_mobile_runtime_v01 import (
    CoreResponse,
    MockSolChannel,
    RuntimeState,
    UserEvent,
    make_nerve_envelope,
    read_from_sol,
    render_response,
    runtime_invariants_ok,
    runtime_loop,
    runtime_step,
    send_to_sol,
)


def test_make_nerve_envelope_has_no_vault_or_admission():
    event = UserEvent(
        event_type="text",
        payload={"text": "hello"},
        event_nonce="event-1",
    )

    envelope = make_nerve_envelope(event)

    assert envelope.nerve == "mobile"
    assert envelope.kind == "runtime_input"
    assert envelope.input["type"] == "text"
    assert envelope.meta["vault"] == "closed"
    assert envelope.meta["admission"] == "not_performed"
    assert "binding" not in envelope.meta
    assert "identity" not in envelope.meta


def test_send_to_sol_online_sends_envelope():
    channel = MockSolChannel(online=True)
    state = RuntimeState()

    envelope = make_nerve_envelope(
        UserEvent(
            event_type="text",
            payload={"text": "hello"},
            event_nonce="event-1",
        )
    )

    result = send_to_sol(channel, envelope, state)

    assert result == "sent"
    assert state.sent_count == 1
    assert len(channel.outbound) == 1


def test_send_to_sol_offline_sets_offline_status():
    channel = MockSolChannel(online=False)
    state = RuntimeState()

    envelope = make_nerve_envelope(
        UserEvent(
            event_type="text",
            payload={"text": "hello"},
            event_nonce="event-1",
        )
    )

    result = send_to_sol(channel, envelope, state)

    assert result == "offline"
    assert state.status == "OFFLINE"
    assert "sol_channel_offline" in state.errors


def test_read_from_sol_none_sets_silent():
    channel = MockSolChannel(online=True)
    state = RuntimeState()

    response = read_from_sol(channel, state)

    assert response is None
    assert state.status == "WHISPER_SILENT"


def test_read_from_sol_response_sets_responding():
    channel = MockSolChannel(
        online=True,
        inbound=[
            CoreResponse(
                response_type="text",
                payload={"text": "ok"},
                response_nonce="r1",
            )
        ],
    )
    state = RuntimeState()

    response = read_from_sol(channel, state)

    assert response is not None
    assert state.status == "WHISPER_RESPONDING"
    assert state.received_count == 1


def test_render_response_returns_ui_payload():
    state = RuntimeState()

    rendered = render_response(
        CoreResponse(
            response_type="text",
            payload={"text": "ok"},
            response_nonce="r1",
        ),
        state,
    )

    assert rendered == {
        "type": "text",
        "payload": {"text": "ok"},
        "response_nonce": "r1",
    }
    assert state.rendered_count == 1


def test_runtime_step_sends_and_renders_response():
    channel = MockSolChannel(
        online=True,
        inbound=[
            CoreResponse(
                response_type="text",
                payload={"text": "Whisper répond."},
                response_nonce="r1",
            )
        ],
    )
    state = RuntimeState()

    rendered = runtime_step(
        UserEvent(
            event_type="text",
            payload={"text": "hello"},
            event_nonce="e1",
        ),
        channel,
        state,
    )

    assert rendered is not None
    assert rendered["payload"]["text"] == "Whisper répond."
    assert state.sent_count == 1
    assert state.received_count == 1
    assert state.rendered_count == 1
    assert state.status == "WHISPER_RESPONDING"


def test_runtime_step_no_response_sets_silent():
    channel = MockSolChannel(online=True)
    state = RuntimeState()

    rendered = runtime_step(
        UserEvent(
            event_type="text",
            payload={"text": "hello"},
            event_nonce="e1",
        ),
        channel,
        state,
    )

    assert rendered is None
    assert state.sent_count == 1
    assert state.status == "WHISPER_SILENT"


def test_runtime_loop_preserves_no_vault_no_admission_invariants():
    channel = MockSolChannel(online=True)
    events = [
        UserEvent(
            event_type="text",
            payload={"text": "a"},
            event_nonce="e1",
        ),
        UserEvent(
            event_type="gesture",
            payload={"name": "tap"},
            event_nonce="e2",
        ),
    ]

    state = runtime_loop(events, channel)

    assert state.sent_count == 2
    assert runtime_invariants_ok(state) is True


def test_invalid_event_type_rejected():
    try:
        make_nerve_envelope(
            UserEvent(
                event_type="bad",  # type: ignore[arg-type]
                payload={},
                event_nonce="e1",
            )
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for invalid event_type")
