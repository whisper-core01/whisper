"""
WHISPER — Sol Delivery Authority v0.1

Doctrine:
- Network can carry.
- Custody can store.
- Sol enables final delivery attempt.
- Recipient ACK proves delivery.
- Origin zeroize is allowed only after Sol delivery ACK.

Core law:
No Sol.
No delivery.
No delivery ACK.
No origin zeroize.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Tuple


DeliveryState = Literal[
    "NO_NETWORK",
    "CARRIED_BY_NETWORK",
    "CUSTODY_ACCEPTED",
    "WAITING_SOL_PRESENCE",
    "SOL_PRESENT",
    "DELIVERY_ATTEMPT_ALLOWED",
    "ACK_PENDING",
    "DELIVERY_ACK_RECEIVED",
    "ZEROIZE_ALLOWED",
]


DeliveryDecision = Literal[
    "delivery_blocked_no_network",
    "delivery_blocked_waiting_sol",
    "delivery_blocked_incompatible_fragment",
    "delivery_attempt_allowed",
    "delivery_ack_received",
    "zeroize_allowed",
]


@dataclass(frozen=True)
class DeliveryContext:
    network_available: bool
    custody_available: bool
    sol_present: bool
    fragment_compatible: bool
    recipient_ack_received: bool


@dataclass(frozen=True)
class DeliveryEvaluation:
    state: DeliveryState
    decision: DeliveryDecision
    delivery_allowed: bool
    zeroize_allowed: bool
    reason: str


def evaluate_delivery_state(ctx: DeliveryContext) -> DeliveryState:
    """
    Return the authoritative delivery state.

    Important:
    recipient_ack_received alone is never enough.
    A valid final delivery ACK requires Sol presence and fragment compatibility.
    """

    if not ctx.network_available:
        return "NO_NETWORK"

    if not ctx.sol_present:
        if ctx.custody_available:
            return "WAITING_SOL_PRESENCE"
        return "CARRIED_BY_NETWORK"

    if ctx.sol_present and not ctx.fragment_compatible:
        return "SOL_PRESENT"

    if ctx.sol_present and ctx.fragment_compatible and not ctx.recipient_ack_received:
        return "DELIVERY_ATTEMPT_ALLOWED"

    if ctx.sol_present and ctx.fragment_compatible and ctx.recipient_ack_received:
        return "ZEROIZE_ALLOWED"

    return "WAITING_SOL_PRESENCE"


def evaluate_delivery(ctx: DeliveryContext) -> DeliveryEvaluation:
    state = evaluate_delivery_state(ctx)

    if state == "NO_NETWORK":
        return DeliveryEvaluation(
            state=state,
            decision="delivery_blocked_no_network",
            delivery_allowed=False,
            zeroize_allowed=False,
            reason="network_available is false; no transport can carry the fragment",
        )

    if state in ("CARRIED_BY_NETWORK", "CUSTODY_ACCEPTED", "WAITING_SOL_PRESENCE"):
        return DeliveryEvaluation(
            state=state,
            decision="delivery_blocked_waiting_sol",
            delivery_allowed=False,
            zeroize_allowed=False,
            reason="network/custody may carry, but Sol presence is required for delivery",
        )

    if state == "SOL_PRESENT":
        return DeliveryEvaluation(
            state=state,
            decision="delivery_blocked_incompatible_fragment",
            delivery_allowed=False,
            zeroize_allowed=False,
            reason="Sol is present, but the fragment is not compatible with the delivery path",
        )

    if state == "DELIVERY_ATTEMPT_ALLOWED":
        return DeliveryEvaluation(
            state=state,
            decision="delivery_attempt_allowed",
            delivery_allowed=True,
            zeroize_allowed=False,
            reason="Sol is present and fragment is compatible; final recipient ACK is still required",
        )

    if state == "DELIVERY_ACK_RECEIVED":
        return DeliveryEvaluation(
            state=state,
            decision="delivery_ack_received",
            delivery_allowed=True,
            zeroize_allowed=False,
            reason="delivery ACK received but zeroize still requires explicit final authority",
        )

    if state == "ZEROIZE_ALLOWED":
        return DeliveryEvaluation(
            state=state,
            decision="zeroize_allowed",
            delivery_allowed=True,
            zeroize_allowed=True,
            reason="Sol delivery ACK received; origin zeroize is authorized",
        )

    return DeliveryEvaluation(
        state="WAITING_SOL_PRESENCE",
        decision="delivery_blocked_waiting_sol",
        delivery_allowed=False,
        zeroize_allowed=False,
        reason="fallback: delivery blocked until Sol presence",
    )


def delivery_allowed(ctx: DeliveryContext) -> bool:
    return evaluate_delivery(ctx).delivery_allowed


def zeroize_allowed(ctx: DeliveryContext) -> bool:
    return evaluate_delivery(ctx).zeroize_allowed


def canonical_transport_law() -> Tuple[str, ...]:
    return (
        "network_carries",
        "custody_stores",
        "sol_connects",
        "recipient_receives",
        "ack_confirms",
        "origin_zeroizes",
    )


def delivery_invariants() -> Dict[str, bool]:
    return {
        "network_can_carry_without_sol": True,
        "network_cannot_deliver_without_sol": True,
        "custody_can_store_without_sol": True,
        "custody_cannot_deliver_without_sol": True,
        "custody_ack_is_not_delivery_ack": True,
        "sol_presence_required_for_delivery": True,
        "recipient_ack_required_for_origin_zeroize": True,
        "origin_zeroize_requires_sol_delivery_ack": True,
        "internet_return_does_not_imply_sol_presence": True,
        "network_available_is_not_delivery_allowed": True,
        "custody_available_is_not_delivery_allowed": True,
        "no_sol_no_delivery": True,
        "no_sol_no_delivery_ack": True,
        "no_sol_no_origin_zeroize": True,
    }


def guided_link(test_name: str) -> str:
    return f"WHISPER_GUIDED_LINK::v1.8.0::sol_delivery_authority_v01::{test_name}"


def smoke_demo() -> None:
    print("WHISPER Sol Delivery Authority v0.1 — Smoke Test")

    no_sol = DeliveryContext(
        network_available=True,
        custody_available=True,
        sol_present=False,
        fragment_compatible=True,
        recipient_ack_received=False,
    )
    print("Network + custody without Sol:", evaluate_delivery(no_sol).state)

    with_sol = DeliveryContext(
        network_available=True,
        custody_available=True,
        sol_present=True,
        fragment_compatible=True,
        recipient_ack_received=False,
    )
    print("Sol present without ACK:", evaluate_delivery(with_sol).state)

    final_ack = DeliveryContext(
        network_available=True,
        custody_available=True,
        sol_present=True,
        fragment_compatible=True,
        recipient_ack_received=True,
    )
    print("Sol + final ACK:", evaluate_delivery(final_ack).state)
    print("Zeroize allowed:", evaluate_delivery(final_ack).zeroize_allowed)

    forged_ack_no_sol = DeliveryContext(
        network_available=True,
        custody_available=True,
        sol_present=False,
        fragment_compatible=True,
        recipient_ack_received=True,
    )
    print("ACK without Sol zeroize allowed:", evaluate_delivery(forged_ack_no_sol).zeroize_allowed)

    print("Invariant count:", len(delivery_invariants()))
    print("Canonical law:", " -> ".join(canonical_transport_law()))


if __name__ == "__main__":
    smoke_demo()
