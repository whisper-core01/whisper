from nerve_mobile_transport_v01 import (
    MockSolTransport,
    SolResponseEnvelope,
    TransportRuntime,
)
from nerve_mobile_ui_v01 import (
    NerveMobileUIState,
    UIInput,
    render_core_response,
    render_human_input,
    ui_has_no_configuration_surface,
    ui_invariants_ok,
    ui_loop,
    ui_status_label,
    ui_submit_input,
)


def test_ui_renders_text_responses():
    response = SolResponseEnvelope(
        type="text",
        payload={"text": "ok"},
        response_nonce="r1",
    )

    rendered = render_core_response(response)

    assert rendered.render_type == "text"
    assert rendered.payload == {"text": "ok"}


def test_ui_renders_image_responses():
    response = SolResponseEnvelope(
        type="image",
        payload={"image_ref": "img-1"},
        response_nonce="r1",
    )

    rendered = render_core_response(response)

    assert rendered.render_type == "image"
    assert rendered.payload["image_ref"] == "img-1"


def test_ui_renders_audio_responses():
    response = SolResponseEnvelope(
        type="audio",
        payload={"audio_ref": "aud-1"},
        response_nonce="r1",
    )

    rendered = render_core_response(response)

    assert rendered.render_type == "audio"
    assert rendered.payload["audio_ref"] == "aud-1"


def test_ui_renders_video_responses():
    response = SolResponseEnvelope(
        type="video",
        payload={"video_ref": "vid-1"},
        response_nonce="r1",
    )

    rendered = render_core_response(response)

    assert rendered.render_type == "video"
    assert rendered.payload["video_ref"] == "vid-1"


def test_ui_renders_human_input_without_metadata():
    item = render_human_input(
        UIInput(
            input_type="text",
            payload={"text": "hello"},
            input_nonce="input-1",
        )
    )

    assert item.render_type == "text"
    assert item.payload == {"text": "hello"}
    assert "input_nonce" not in item.payload
    assert "identity" not in item.payload
    assert "session" not in item.payload


def test_ui_updates_status_correctly_when_whisper_responds():
    transport = MockSolTransport(
        online=True,
        responses=[
            SolResponseEnvelope(
                type="text",
                payload={"text": "Whisper répond."},
                response_nonce="r1",
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

    assert rendered is not None
    assert ui_state.status == "WHISPER_RESPONDING"
    assert ui_status_label(ui_state.status) == "Whisper répond"


def test_ui_updates_status_correctly_when_whisper_silent():
    transport = MockSolTransport(online=True)
    runtime = TransportRuntime()
    ui_state = NerveMobileUIState()

    rendered = ui_submit_input(
        ui_input=UIInput(
            input_type="text",
            payload={"text": "hello"},
            input_nonce="input-1",
        ),
        capabilities=["text"],
        transport=transport,
        runtime=runtime,
        ui_state=ui_state,
    )

    assert rendered is None
    assert ui_state.status == "WHISPER_SILENT"
    assert ui_status_label(ui_state.status) == "Whisper silencieux"


def test_ui_updates_status_correctly_when_offline():
    transport = MockSolTransport(online=False)
    runtime = TransportRuntime()
    ui_state = NerveMobileUIState()

    rendered = ui_submit_input(
        ui_input=UIInput(
            input_type="text",
            payload={"text": "hello"},
            input_nonce="input-1",
        ),
        capabilities=["text"],
        transport=transport,
        runtime=runtime,
        ui_state=ui_state,
    )

    assert rendered is None
    assert ui_state.status == "OFFLINE"
    assert ui_status_label(ui_state.status) == "Hors-ligne"


def test_ui_does_not_access_vault():
    ui_state = NerveMobileUIState()

    assert ui_state.vault_access_attempted is False
    assert ui_invariants_ok(ui_state) is True


def test_ui_does_not_trigger_admission():
    ui_state = NerveMobileUIState()

    assert ui_state.admission_attempted is False
    assert ui_invariants_ok(ui_state) is True


def test_ui_does_not_store_state():
    ui_state = NerveMobileUIState()

    assert ui_state.stored_internal_state == {}
    assert ui_invariants_ok(ui_state) is True


def test_ui_does_not_expose_internal_json():
    ui_state = NerveMobileUIState()

    assert ui_state.internal_json_exposed is False
    assert ui_invariants_ok(ui_state) is True


def test_ui_has_no_configuration_surface():
    assert ui_has_no_configuration_surface() is True


def test_ui_loop_renders_visible_items():
    transport = MockSolTransport(
        online=True,
        responses=[
            SolResponseEnvelope(
                type="text",
                payload={"text": "ok"},
                response_nonce="r1",
            )
        ],
    )

    state = ui_loop(
        inputs=[
            UIInput(
                input_type="text",
                payload={"text": "hello"},
                input_nonce="input-1",
            )
        ],
        capabilities=["text", "audio", "image", "video", "event"],
        transport=transport,
    )

    assert len(state.visible_items) == 2
    assert state.visible_items[0].render_type == "text"
    assert state.visible_items[1].render_type == "text"
    assert ui_invariants_ok(state) is True


def test_invalid_ui_input_rejected():
    try:
        render_human_input(
            UIInput(
                input_type="bad",  # type: ignore[arg-type]
                payload={},
                input_nonce="input-1",
            )
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for invalid input type")
