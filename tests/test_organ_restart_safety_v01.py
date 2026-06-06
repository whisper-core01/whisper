from organ_restart_safety_v01 import (
    BASE_PRIVILEGES,
    FORBIDDEN_PRIVILEGES,
    RestartRequest,
    build_organ_role,
    create_runtime_record,
    guided_link,
    mark_failed,
    organ_restart_changes_rails,
    organ_restart_creates_shortcut,
    organ_restart_exposes_network,
    organ_restart_exposes_vault_or_flv,
    organ_restart_exposes_wasm,
    organ_restart_summary,
    quarantine_organ,
    reintegrate_restarted_organ,
    request_restart,
    restart_does_not_add_privileges,
    restart_preserves_minimal_role,
    restarted_organ_has_no_forbidden_privileges,
    revoke_organ,
)


def test_build_organ_role_contains_minimal_privileges():
    assert guided_link("build_organ_role_contains_minimal_privileges")

    role = build_organ_role("courier")

    assert role.organ == "courier"
    assert role.allowed_privileges == {"carry_dome_validated_to_bal_in"}
    assert "direct_wasm_access" in role.forbidden_privileges


def test_create_runtime_record_starts_healthy_with_base_privileges():
    assert guided_link("create_runtime_record_starts_healthy_with_base_privileges")

    record = create_runtime_record("dome")

    assert record.state == "HEALTHY"
    assert record.privileges == BASE_PRIVILEGES["dome"]


def test_failed_organ_can_request_restart():
    assert guided_link("failed_organ_can_request_restart")

    record = create_runtime_record("courier")
    mark_failed(record, "ack_timeout")

    result = request_restart(
        record,
        RestartRequest(
            organ="courier",
            reason="ack_timeout",
            requested_by="dome",
        ),
    )

    assert result.decision == "restart_allowed"
    assert result.state == "RESTARTING"
    assert record.restart_count == 1


def test_quarantined_organ_can_request_restart():
    assert guided_link("quarantined_organ_can_request_restart")

    record = create_runtime_record("bal_in")
    quarantine_organ(record, "role_violation")

    result = request_restart(
        record,
        RestartRequest(
            organ="bal_in",
            reason="role_violation",
            requested_by="dome",
        ),
    )

    assert result.decision == "restart_allowed"
    assert result.state == "RESTARTING"


def test_healthy_organ_restart_denied():
    assert guided_link("healthy_organ_restart_denied")

    record = create_runtime_record("membrane")

    result = request_restart(
        record,
        RestartRequest(
            organ="membrane",
            reason="no_failure",
            requested_by="dome",
        ),
    )

    assert result.decision == "restart_denied"
    assert result.reason == "restart_not_required"


def test_revoked_organ_cannot_restart():
    assert guided_link("revoked_organ_cannot_restart")

    record = create_runtime_record("transporteur")
    revoke_organ(record, "repeated_role_violation")

    result = request_restart(
        record,
        RestartRequest(
            organ="transporteur",
            reason="repeated_role_violation",
            requested_by="dome",
        ),
    )

    assert result.decision == "revoked"
    assert result.privileges == set()


def test_restart_mismatch_denied():
    assert guided_link("restart_mismatch_denied")

    record = create_runtime_record("courier")
    mark_failed(record, "failure")

    result = request_restart(
        record,
        RestartRequest(
            organ="dome",
            reason="failure",
            requested_by="dome",
        ),
    )

    assert result.decision == "restart_denied"
    assert result.reason == "restart_request_organ_mismatch"


def test_reintegrate_restarted_organ_after_minimal_role_check():
    assert guided_link("reintegrate_restarted_organ_after_minimal_role_check")

    record = create_runtime_record("courier")
    mark_failed(record, "ack_timeout")

    request_restart(
        record,
        RestartRequest(
            organ="courier",
            reason="ack_timeout",
            requested_by="dome",
        ),
    )

    result = reintegrate_restarted_organ(record)

    assert result.decision == "reintegrated"
    assert result.state == "RECOVERED"
    assert record.privileges == BASE_PRIVILEGES["courier"]


def test_privilege_drift_blocks_reintegration():
    assert guided_link("privilege_drift_blocks_reintegration")

    record = create_runtime_record("courier")
    mark_failed(record, "ack_timeout")

    request_restart(
        record,
        RestartRequest(
            organ="courier",
            reason="ack_timeout",
            requested_by="dome",
        ),
    )

    record.privileges.add("direct_wasm_access")

    result = reintegrate_restarted_organ(record)

    assert result.decision == "restart_denied"
    assert result.reason == "privilege_drift_detected"
    assert record.state == "QUARANTINED"


def test_restart_preserves_minimal_role_for_all_organs():
    assert guided_link("restart_preserves_minimal_role_for_all_organs")

    for organ in BASE_PRIVILEGES:
        assert restart_preserves_minimal_role(organ) is True


def test_restart_does_not_add_privileges_for_all_organs():
    assert guided_link("restart_does_not_add_privileges_for_all_organs")

    for organ in BASE_PRIVILEGES:
        assert restart_does_not_add_privileges(organ) is True


def test_restarted_organ_has_no_forbidden_privileges():
    assert guided_link("restarted_organ_has_no_forbidden_privileges")

    for organ in BASE_PRIVILEGES:
        assert restarted_organ_has_no_forbidden_privileges(organ) is True


def test_restart_does_not_change_rails_or_create_shortcut():
    assert guided_link("restart_does_not_change_rails_or_create_shortcut")

    assert organ_restart_changes_rails() is False
    assert organ_restart_creates_shortcut() is False


def test_restart_does_not_expose_wasm_network_vault_or_flv():
    assert guided_link("restart_does_not_expose_wasm_network_vault_or_flv")

    assert organ_restart_exposes_wasm() is False
    assert organ_restart_exposes_network() is False
    assert organ_restart_exposes_vault_or_flv() is False


def test_forbidden_privileges_are_not_base_privileges():
    assert guided_link("forbidden_privileges_are_not_base_privileges")

    for organ, privileges in BASE_PRIVILEGES.items():
        assert not bool(privileges & FORBIDDEN_PRIVILEGES), organ


def test_organ_restart_summary():
    assert guided_link("organ_restart_summary")

    summary = organ_restart_summary("courier")

    assert summary["organ"] == "courier"
    assert summary["restart_decision"] == "restart_allowed"
    assert summary["reintegrated"] is True
    assert summary["state"] == "RECOVERED"
    assert summary["restart_count"] == 1
    assert summary["privileges"] == ["carry_dome_validated_to_bal_in"]
