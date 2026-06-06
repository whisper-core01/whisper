from nerve_mobile_capabilities_v01 import (
    BASE_CAPABILITIES,
    FORBIDDEN_CAPABILITIES,
    OPTIONAL_CAPABILITIES,
    SUPPORTED_CAPABILITIES,
    build_capability_declaration,
    build_core_capability_policy,
    build_mobile_vault_capability_profile,
    capabilities_affect_admission,
    capabilities_affect_reappearance,
    capability_report_to_safe_summary,
    evaluate_capabilities_for_core,
    normalize_capabilities,
)


def test_capabilities_declared_correctly():
    declaration = build_capability_declaration(
        capabilities=["text", "audio", "image", "video"],
        admission_epoch="epoch-1",
    )

    assert declaration.nerve == "mobile"
    assert declaration.kind == "capability_declaration"
    assert declaration.capabilities == ["text", "audio", "image", "video"]
    assert declaration.admission_epoch == "epoch-1"


def test_normalize_capabilities_removes_duplicates_preserves_order():
    normalized = normalize_capabilities(["text", "audio", "text", "image"])

    assert normalized == ["text", "audio", "image"]


def test_base_capabilities_are_supported():
    assert BASE_CAPABILITIES.issubset(SUPPORTED_CAPABILITIES)


def test_optional_capabilities_are_supported():
    assert OPTIONAL_CAPABILITIES.issubset(SUPPORTED_CAPABILITIES)


def test_forbidden_capabilities_rejected_at_declaration():
    for capability in FORBIDDEN_CAPABILITIES:
        try:
            build_capability_declaration(
                capabilities=["text", capability],
                admission_epoch="epoch-1",
            )
        except ValueError:
            continue

        raise AssertionError(f"Expected ValueError for {capability}")


def test_core_accepts_supported_capabilities():
    declaration = build_capability_declaration(
        capabilities=["text", "audio", "image", "video", "event", "file", "location_hint"],
        admission_epoch="epoch-1",
    )

    report = evaluate_capabilities_for_core(declaration)

    assert report.accepted == ["text", "audio", "image", "video", "event", "file", "location_hint"]
    assert report.ignored == []
    assert report.revoked == []
    assert report.rejected_forbidden == []


def test_core_ignores_unsupported_capabilities():
    declaration = build_capability_declaration(
        capabilities=["text", "unknown_sensor"],
        admission_epoch="epoch-1",
    )

    report = evaluate_capabilities_for_core(declaration)

    assert report.accepted == ["text"]
    assert report.ignored == ["unknown_sensor"]


def test_revoked_capabilities_not_restored():
    declaration = build_capability_declaration(
        capabilities=["text", "audio", "image"],
        admission_epoch="epoch-1",
    )

    report = evaluate_capabilities_for_core(
        declaration,
        revoked_capabilities=["audio"],
    )

    assert report.accepted == ["text", "image"]
    assert report.revoked == ["audio"]


def test_core_capability_policy_derived_from_report():
    declaration = build_capability_declaration(
        capabilities=["text", "audio", "unknown_sensor"],
        admission_epoch="epoch-1",
    )

    report = evaluate_capabilities_for_core(
        declaration,
        revoked_capabilities=["audio"],
    )

    policy = build_core_capability_policy(report)

    assert policy.accepted_capabilities == ["text"]
    assert policy.ignored_capabilities == ["unknown_sensor"]
    assert policy.revoked_capabilities == ["audio"]


def test_capabilities_not_in_vault_as_sovereign_state():
    profile = build_mobile_vault_capability_profile(["text", "audio"])

    assert profile.capability_profile == ["text", "audio"]
    assert profile.ux_only is True
    assert profile.sovereign is False


def test_capabilities_do_not_affect_admission():
    assert capabilities_affect_admission() is False


def test_capabilities_do_not_affect_reappearance():
    assert capabilities_affect_reappearance() is False


def test_capability_report_safe_summary():
    declaration = build_capability_declaration(
        capabilities=["text", "audio", "unknown_sensor"],
        admission_epoch="epoch-1",
    )

    report = evaluate_capabilities_for_core(
        declaration,
        revoked_capabilities=["audio"],
    )

    summary = capability_report_to_safe_summary(report)

    assert summary == {
        "accepted": ["text"],
        "ignored": ["unknown_sensor"],
        "revoked": ["audio"],
        "rejected_forbidden": [],
    }


def test_empty_capabilities_rejected():
    try:
        build_capability_declaration(
            capabilities=[],
            admission_epoch="epoch-1",
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError for empty capabilities")
