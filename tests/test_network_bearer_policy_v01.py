from network_bearer_policy_v01 import (
    FULL_PAYLOADS,
    TEXT_ONLY_PAYLOADS,
    BearerBoundaryState,
    BearerProbe,
    OutgoingPayload,
    apply_bearer_decision,
    bearer_changes_core_rails,
    bearer_has_forbidden_privileges,
    bearer_is_viable,
    bearer_participates_in_immunity,
    bearer_policy_summary,
    bearer_reads_payload,
    bearer_touches_internal_organs,
    filter_payloads_for_bearer,
    guided_link,
    ip_bearer_keeps_full_capabilities,
    lora_bearer_is_text_only,
    payload_allowed_by_bearer,
    select_bearer,
)


def test_selects_primary_internet_when_available():
    assert guided_link("selects_primary_internet_when_available")

    decision = select_bearer(
        [
            BearerProbe("PRIMARY_INTERNET", "AVAILABLE", latency_ms=30, packet_loss_percent=0),
            BearerProbe("MOBILE_DATA_4G_5G", "AVAILABLE", latency_ms=70, packet_loss_percent=1),
            BearerProbe("LORA_RNODE", "AVAILABLE", latency_ms=900, packet_loss_percent=5),
        ]
    )

    assert decision.bearer == "PRIMARY_INTERNET"
    assert decision.mode == "CONNECTED"
    assert decision.stack == "RETICULUM_VOXMESH"
    assert decision.allowed_payloads == FULL_PAYLOADS
    assert ip_bearer_keeps_full_capabilities(decision) is True


def test_selects_mobile_data_when_primary_unavailable():
    assert guided_link("selects_mobile_data_when_primary_unavailable")

    decision = select_bearer(
        [
            BearerProbe("PRIMARY_INTERNET", "UNAVAILABLE"),
            BearerProbe("MOBILE_DATA_4G_5G", "AVAILABLE", latency_ms=80, packet_loss_percent=2),
            BearerProbe("LORA_RNODE", "AVAILABLE", latency_ms=900, packet_loss_percent=5),
        ]
    )

    assert decision.bearer == "MOBILE_DATA_4G_5G"
    assert decision.mode == "CONNECTED"
    assert decision.stack == "RETICULUM_VOXMESH"
    assert decision.allowed_payloads == FULL_PAYLOADS
    assert ip_bearer_keeps_full_capabilities(decision) is True


def test_selects_lora_only_when_no_ip_bearer_viable():
    assert guided_link("selects_lora_only_when_no_ip_bearer_viable")

    decision = select_bearer(
        [
            BearerProbe("PRIMARY_INTERNET", "UNAVAILABLE"),
            BearerProbe("MOBILE_DATA_4G_5G", "UNAVAILABLE"),
            BearerProbe("LORA_RNODE", "AVAILABLE", latency_ms=900, packet_loss_percent=5),
        ]
    )

    assert decision.bearer == "LORA_RNODE"
    assert decision.mode == "DEGRADED_SURVIVAL"
    assert decision.stack == "LORA_TEXT"
    assert decision.allowed_payloads == TEXT_ONLY_PAYLOADS
    assert lora_bearer_is_text_only(decision) is True


def test_offline_when_no_bearer_viable():
    assert guided_link("offline_when_no_bearer_viable")

    decision = select_bearer(
        [
            BearerProbe("PRIMARY_INTERNET", "UNAVAILABLE"),
            BearerProbe("MOBILE_DATA_4G_5G", "UNAVAILABLE"),
            BearerProbe("LORA_RNODE", "UNAVAILABLE"),
        ]
    )

    assert decision.bearer is None
    assert decision.mode == "OFFLINE"
    assert decision.stack == "NONE"
    assert decision.allowed_payloads == set()


def test_mobile_data_preserves_full_capabilities():
    assert guided_link("mobile_data_preserves_full_capabilities")

    decision = select_bearer(
        [
            BearerProbe("PRIMARY_INTERNET", "UNAVAILABLE"),
            BearerProbe("MOBILE_DATA_4G_5G", "AVAILABLE", latency_ms=80, packet_loss_percent=2),
        ]
    )

    for kind in ["text", "audio", "image", "video", "file", "event"]:
        assert payload_allowed_by_bearer(
            OutgoingPayload(payload_id=f"p-{kind}", kind=kind, body="ok"),
            decision,
        ) is True


def test_lora_allows_text_only():
    assert guided_link("lora_allows_text_only")

    decision = select_bearer(
        [
            BearerProbe("PRIMARY_INTERNET", "UNAVAILABLE"),
            BearerProbe("MOBILE_DATA_4G_5G", "UNAVAILABLE"),
            BearerProbe("LORA_RNODE", "AVAILABLE", latency_ms=900, packet_loss_percent=5),
        ]
    )

    assert payload_allowed_by_bearer(
        OutgoingPayload(payload_id="p-text", kind="text", body="hello"),
        decision,
    ) is True

    for kind in ["audio", "image", "video", "file", "event"]:
        assert payload_allowed_by_bearer(
            OutgoingPayload(payload_id=f"p-{kind}", kind=kind, body="blocked"),
            decision,
        ) is False


def test_filter_payloads_for_lora_keeps_only_text():
    assert guided_link("filter_payloads_for_lora_keeps_only_text")

    decision = select_bearer(
        [
            BearerProbe("PRIMARY_INTERNET", "UNAVAILABLE"),
            BearerProbe("MOBILE_DATA_4G_5G", "UNAVAILABLE"),
            BearerProbe("LORA_RNODE", "AVAILABLE", latency_ms=900, packet_loss_percent=5),
        ]
    )

    payloads = [
        OutgoingPayload("p1", "text", "hello"),
        OutgoingPayload("p2", "image", "image"),
        OutgoingPayload("p3", "audio", "audio"),
        OutgoingPayload("p4", "video", "video"),
        OutgoingPayload("p5", "file", "file"),
    ]

    filtered = filter_payloads_for_bearer(payloads, decision)

    assert [payload.payload_id for payload in filtered] == ["p1"]


def test_apply_bearer_decision_updates_boundary_state():
    assert guided_link("apply_bearer_decision_updates_boundary_state")

    boundary = BearerBoundaryState()
    decision = select_bearer(
        [
            BearerProbe("PRIMARY_INTERNET", "UNAVAILABLE"),
            BearerProbe("MOBILE_DATA_4G_5G", "AVAILABLE", latency_ms=80, packet_loss_percent=2),
        ]
    )

    apply_bearer_decision(boundary, decision)

    assert boundary.selected_bearer == "MOBILE_DATA_4G_5G"
    assert boundary.mode == "CONNECTED"
    assert boundary.stack == "RETICULUM_VOXMESH"
    assert boundary.allowed_payloads == FULL_PAYLOADS


def test_bearer_does_not_touch_internal_organs_payload_or_immunity():
    assert guided_link("bearer_does_not_touch_internal_organs_payload_or_immunity")

    boundary = BearerBoundaryState()

    assert bearer_touches_internal_organs(boundary) is False
    assert bearer_reads_payload(boundary) is False
    assert bearer_participates_in_immunity(boundary) is False
    assert bearer_has_forbidden_privileges(boundary) is False


def test_bearer_does_not_change_core_rails():
    assert guided_link("bearer_does_not_change_core_rails")

    boundary = BearerBoundaryState()

    assert bearer_changes_core_rails(boundary) is False


def test_forbidden_state_detects_forbidden_privileges():
    assert guided_link("forbidden_state_detects_forbidden_privileges")

    boundary = BearerBoundaryState(
        touched_wasm=True,
        changed_core_rails=True,
    )

    assert bearer_touches_internal_organs(boundary) is True
    assert bearer_changes_core_rails(boundary) is True
    assert bearer_has_forbidden_privileges(boundary) is True


def test_bearer_viability_rejects_unstable_or_high_loss():
    assert guided_link("bearer_viability_rejects_unstable_or_high_loss")

    assert bearer_is_viable(BearerProbe("PRIMARY_INTERNET", "AVAILABLE", stable=False)) is False
    assert bearer_is_viable(BearerProbe("PRIMARY_INTERNET", "AVAILABLE", packet_loss_percent=80)) is False
    assert bearer_is_viable(BearerProbe("PRIMARY_INTERNET", "AVAILABLE", latency_ms=-1)) is False


def test_bearer_policy_summary_primary_mobile_lora():
    assert guided_link("bearer_policy_summary_primary_mobile_lora")

    primary = bearer_policy_summary(
        [
            BearerProbe("PRIMARY_INTERNET", "AVAILABLE", latency_ms=30, packet_loss_percent=0),
            BearerProbe("MOBILE_DATA_4G_5G", "AVAILABLE", latency_ms=70, packet_loss_percent=1),
            BearerProbe("LORA_RNODE", "AVAILABLE", latency_ms=900, packet_loss_percent=5),
        ]
    )

    mobile = bearer_policy_summary(
        [
            BearerProbe("PRIMARY_INTERNET", "UNAVAILABLE"),
            BearerProbe("MOBILE_DATA_4G_5G", "AVAILABLE", latency_ms=80, packet_loss_percent=2),
            BearerProbe("LORA_RNODE", "AVAILABLE", latency_ms=900, packet_loss_percent=5),
        ]
    )

    lora = bearer_policy_summary(
        [
            BearerProbe("PRIMARY_INTERNET", "UNAVAILABLE"),
            BearerProbe("MOBILE_DATA_4G_5G", "UNAVAILABLE"),
            BearerProbe("LORA_RNODE", "AVAILABLE", latency_ms=900, packet_loss_percent=5),
        ]
    )

    assert primary["bearer"] == "PRIMARY_INTERNET"
    assert primary["stack"] == "RETICULUM_VOXMESH"

    assert mobile["bearer"] == "MOBILE_DATA_4G_5G"
    assert mobile["stack"] == "RETICULUM_VOXMESH"

    assert lora["bearer"] == "LORA_RNODE"
    assert lora["stack"] == "LORA_TEXT"
    assert lora["allowed_payloads"] == ["text"]
    assert lora["touches_internal_organs"] is False
    assert lora["changes_core_rails"] is False
