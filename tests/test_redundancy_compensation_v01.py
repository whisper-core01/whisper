from redundancy_compensation_v01 import (
    build_redundancy_plan,
    can_reconstruct,
    effective_reconstruction_ratio,
    fragment_role,
    reconstruction_margin,
    summarize_fragment_delivery,
)


def test_build_redundancy_plan_default_110_percent():
    plan = build_redundancy_plan(100, 1.10)

    assert plan.required_fragments == 100
    assert plan.emitted_fragments == 111  # ceil(110.00000000000001)
    assert plan.recovery_fragments == 11
    assert plan.reconstruction_threshold == 100


def test_fragment_role_primary_and_recovery():
    plan = build_redundancy_plan(10, 1.20)

    assert fragment_role(0, plan) == "primary"
    assert fragment_role(9, plan) == "primary"
    assert fragment_role(10, plan) == "recovery"


def test_can_reconstruct_threshold():
    plan = build_redundancy_plan(10, 1.20)

    assert can_reconstruct(9, plan) is False
    assert can_reconstruct(10, plan) is True
    assert can_reconstruct(12, plan) is True


def test_reconstruction_margin():
    plan = build_redundancy_plan(10, 1.20)

    assert reconstruction_margin(9, plan) == -1
    assert reconstruction_margin(10, plan) == 0
    assert reconstruction_margin(12, plan) == 2


def test_effective_reconstruction_ratio():
    plan = build_redundancy_plan(10, 1.20)

    assert effective_reconstruction_ratio(5, plan) == 0.5
    assert effective_reconstruction_ratio(10, plan) == 1.0
    assert effective_reconstruction_ratio(12, plan) == 1.0


def test_summarize_fragment_delivery():
    plan = build_redundancy_plan(10, 1.20)

    delivered = {i: i < 10 for i in range(plan.emitted_fragments)}
    summary = summarize_fragment_delivery(delivered, plan)

    assert summary["delivered_total"] == 10
    assert summary["primary_delivered"] == 10
    assert summary["recovery_delivered"] == 0
    assert summary["message_reconstructed"] is True
