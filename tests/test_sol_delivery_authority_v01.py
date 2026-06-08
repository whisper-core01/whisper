import pytest

from sol_delivery_authority_v01 import (
    DeliveryContext,
    canonical_transport_law,
    delivery_allowed,
    delivery_invariants,
    evaluate_delivery,
    evaluate_delivery_state,
    guided_link,
    zeroize_allowed,
)


def ctx(
    network=True,
    custody=False,
    sol=False,
    compatible=True,
    ack=False,
):
    return DeliveryContext(
        network_available=network,
        custody_available=custody,
        sol_present=sol,
        fragment_compatible=compatible,
        recipient_ack_received=ack,
    )


def test_guided_link_namespace():
    assert guided_link("x") == "WHISPER_GUIDED_LINK::v1.8.0::sol_delivery_authority_v01::x"


def test_no_network_blocks_delivery():
    c = ctx(network=False, custody=False, sol=False, compatible=True, ack=False)
    e = evaluate_delivery(c)

    assert e.state == "NO_NETWORK"
    assert e.decision == "delivery_blocked_no_network"
    assert e.delivery_allowed is False
    assert e.zeroize_allowed is False


def test_network_available_without_sol_is_not_delivery():
    c = ctx(network=True, custody=False, sol=False, compatible=True, ack=False)
    e = evaluate_delivery(c)

    assert e.state == "CARRIED_BY_NETWORK"
    assert e.delivery_allowed is False
    assert e.zeroize_allowed is False


def test_network_and_custody_without_sol_waits_for_sol():
    c = ctx(network=True, custody=True, sol=False, compatible=True, ack=False)
    e = evaluate_delivery(c)

    assert e.state == "WAITING_SOL_PRESENCE"
    assert e.decision == "delivery_blocked_waiting_sol"
    assert e.delivery_allowed is False
    assert e.zeroize_allowed is False


def test_custody_available_is_not_delivery_allowed():
    c = ctx(network=True, custody=True, sol=False, compatible=True, ack=False)

    assert delivery_allowed(c) is False
    assert zeroize_allowed(c) is False


def test_sol_present_with_incompatible_fragment_blocks_delivery():
    c = ctx(network=True, custody=True, sol=True, compatible=False, ack=False)
    e = evaluate_delivery(c)

    assert e.state == "SOL_PRESENT"
    assert e.decision == "delivery_blocked_incompatible_fragment"
    assert e.delivery_allowed is False
    assert e.zeroize_allowed is False


def test_sol_present_and_compatible_allows_delivery_attempt():
    c = ctx(network=True, custody=True, sol=True, compatible=True, ack=False)
    e = evaluate_delivery(c)

    assert e.state == "DELIVERY_ATTEMPT_ALLOWED"
    assert e.decision == "delivery_attempt_allowed"
    assert e.delivery_allowed is True
    assert e.zeroize_allowed is False


def test_delivery_attempt_allowed_is_not_zeroize_allowed():
    c = ctx(network=True, custody=True, sol=True, compatible=True, ack=False)

    assert delivery_allowed(c) is True
    assert zeroize_allowed(c) is False


def test_sol_and_ack_allow_zeroize():
    c = ctx(network=True, custody=True, sol=True, compatible=True, ack=True)
    e = evaluate_delivery(c)

    assert e.state == "ZEROIZE_ALLOWED"
    assert e.decision == "zeroize_allowed"
    assert e.delivery_allowed is True
    assert e.zeroize_allowed is True


def test_ack_without_sol_never_allows_zeroize():
    c = ctx(network=True, custody=True, sol=False, compatible=True, ack=True)
    e = evaluate_delivery(c)

    assert e.state == "WAITING_SOL_PRESENCE"
    assert e.delivery_allowed is False
    assert e.zeroize_allowed is False


def test_ack_without_network_never_allows_zeroize():
    c = ctx(network=False, custody=True, sol=True, compatible=True, ack=True)
    e = evaluate_delivery(c)

    assert e.state == "NO_NETWORK"
    assert e.delivery_allowed is False
    assert e.zeroize_allowed is False


def test_ack_with_incompatible_fragment_never_allows_zeroize():
    c = ctx(network=True, custody=True, sol=True, compatible=False, ack=True)
    e = evaluate_delivery(c)

    assert e.state == "SOL_PRESENT"
    assert e.delivery_allowed is False
    assert e.zeroize_allowed is False


def test_network_return_does_not_imply_sol_presence():
    c = ctx(network=True, custody=False, sol=False, compatible=True, ack=False)

    assert evaluate_delivery_state(c) == "CARRIED_BY_NETWORK"
    assert delivery_allowed(c) is False


def test_internet_return_with_custody_does_not_imply_delivery():
    c = ctx(network=True, custody=True, sol=False, compatible=True, ack=False)

    assert evaluate_delivery_state(c) == "WAITING_SOL_PRESENCE"
    assert delivery_allowed(c) is False


def test_no_sol_no_delivery_no_zeroize_even_with_custody_and_ack_flag():
    c = ctx(network=True, custody=True, sol=False, compatible=True, ack=True)

    assert delivery_allowed(c) is False
    assert zeroize_allowed(c) is False


def test_sol_presence_required_for_delivery():
    without_sol = ctx(network=True, custody=True, sol=False, compatible=True, ack=False)
    with_sol = ctx(network=True, custody=True, sol=True, compatible=True, ack=False)

    assert delivery_allowed(without_sol) is False
    assert delivery_allowed(with_sol) is True


def test_recipient_ack_required_for_origin_zeroize():
    no_ack = ctx(network=True, custody=True, sol=True, compatible=True, ack=False)
    with_ack = ctx(network=True, custody=True, sol=True, compatible=True, ack=True)

    assert zeroize_allowed(no_ack) is False
    assert zeroize_allowed(with_ack) is True


def test_origin_zeroize_requires_sol_delivery_ack():
    no_sol_with_ack = ctx(network=True, custody=True, sol=False, compatible=True, ack=True)
    sol_with_ack = ctx(network=True, custody=True, sol=True, compatible=True, ack=True)

    assert zeroize_allowed(no_sol_with_ack) is False
    assert zeroize_allowed(sol_with_ack) is True


def test_network_can_carry_without_sol_invariant():
    inv = delivery_invariants()

    assert inv["network_can_carry_without_sol"] is True
    assert inv["network_cannot_deliver_without_sol"] is True


def test_custody_can_store_without_sol_but_cannot_deliver():
    inv = delivery_invariants()

    assert inv["custody_can_store_without_sol"] is True
    assert inv["custody_cannot_deliver_without_sol"] is True


def test_custody_ack_is_not_delivery_ack_invariant():
    inv = delivery_invariants()

    assert inv["custody_ack_is_not_delivery_ack"] is True


def test_no_sol_laws_are_present():
    inv = delivery_invariants()

    assert inv["no_sol_no_delivery"] is True
    assert inv["no_sol_no_delivery_ack"] is True
    assert inv["no_sol_no_origin_zeroize"] is True


def test_network_available_is_not_delivery_allowed_invariant():
    inv = delivery_invariants()

    assert inv["network_available_is_not_delivery_allowed"] is True


def test_custody_available_is_not_delivery_allowed_invariant():
    inv = delivery_invariants()

    assert inv["custody_available_is_not_delivery_allowed"] is True


def test_canonical_transport_law_order():
    assert canonical_transport_law() == (
        "network_carries",
        "custody_stores",
        "sol_connects",
        "recipient_receives",
        "ack_confirms",
        "origin_zeroizes",
    )


@pytest.mark.parametrize(
    "network,custody,sol,compatible,ack,expected_state,expected_zeroize",
    [
        (False, False, False, True, False, "NO_NETWORK", False),
        (True, False, False, True, False, "CARRIED_BY_NETWORK", False),
        (True, True, False, True, False, "WAITING_SOL_PRESENCE", False),
        (True, True, True, False, False, "SOL_PRESENT", False),
        (True, True, True, True, False, "DELIVERY_ATTEMPT_ALLOWED", False),
        (True, True, True, True, True, "ZEROIZE_ALLOWED", True),
        (True, True, False, True, True, "WAITING_SOL_PRESENCE", False),
        (True, True, True, False, True, "SOL_PRESENT", False),
    ],
)
def test_delivery_state_matrix(
    network,
    custody,
    sol,
    compatible,
    ack,
    expected_state,
    expected_zeroize,
):
    c = ctx(
        network=network,
        custody=custody,
        sol=sol,
        compatible=compatible,
        ack=ack,
    )

    assert evaluate_delivery_state(c) == expected_state
    assert zeroize_allowed(c) is expected_zeroize


def test_invariant_count_is_stable():
    assert len(delivery_invariants()) == 14
