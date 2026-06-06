from nerve_mobile_permissions_v01 import (
    build_permission_request,
    create_permission_store,
    deny_permission,
    evaluate_capability_permission,
    filter_capabilities_by_permissions,
    grant_permission,
    permission_state,
    permissions_affect_admission,
    permissions_affect_identity,
    permissions_create_session,
    permissions_open_vault,
    revoke_permission,
)


def test_text_and_event_are_granted_by_default():
    store = create_permission_store()

    assert permission_state(store, "text_input") == "granted"
    assert permission_state(store, "ui_event") == "granted"


def test_build_audio_permission_request():
    request = build_permission_request("audio")

    assert request.capability == "audio"
    assert request.required_permissions == ["audio_capture"]


def test_audio_denied_without_permission():
    store = create_permission_store()

    decision = evaluate_capability_permission(store, "audio")

    assert decision.allowed is False
    assert decision.missing_permissions == ["audio_capture"]


def test_audio_allowed_when_granted():
    store = create_permission_store()
    grant_permission(store, "audio_capture")

    decision = evaluate_capability_permission(store, "audio")

    assert decision.allowed is True


def test_image_requires_capture_and_gallery():
    store = create_permission_store()
    grant_permission(store, "image_capture")

    decision = evaluate_capability_permission(store, "image")

    assert decision.allowed is False
    assert decision.missing_permissions == ["image_gallery"]

    grant_permission(store, "image_gallery")
    decision = evaluate_capability_permission(store, "image")

    assert decision.allowed is True


def test_video_requires_video_capture():
    store = create_permission_store()
    grant_permission(store, "video_capture")

    decision = evaluate_capability_permission(store, "video")

    assert decision.allowed is True


def test_denied_permission_blocks_capability():
    store = create_permission_store()
    deny_permission(store, "audio_capture")

    decision = evaluate_capability_permission(store, "audio")

    assert decision.allowed is False
    assert decision.denied_permissions == ["audio_capture"]


def test_revoked_permission_blocks_capability():
    store = create_permission_store()
    grant_permission(store, "audio_capture")
    revoke_permission(store, "audio_capture")

    decision = evaluate_capability_permission(store, "audio")

    assert decision.allowed is False
    assert decision.revoked_permissions == ["audio_capture"]


def test_filter_capabilities_by_permissions():
    store = create_permission_store()
    grant_permission(store, "audio_capture")

    allowed = filter_capabilities_by_permissions(
        store,
        ["text", "audio", "video", "event"],
    )

    assert allowed == ["text", "audio", "event"]


def test_permissions_do_not_affect_admission_identity_vault_or_session():
    assert permissions_affect_admission() is False
    assert permissions_affect_identity() is False
    assert permissions_open_vault() is False
    assert permissions_create_session() is False
