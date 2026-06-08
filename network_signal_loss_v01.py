"""
WHISPER v1.8.0 — Network Signal Loss v0.1

Purpose:
Model network signal loss detection with an adaptive ping scheduler.

This module does not:
- destroy fragments
- retry fragments
- switch bearer
- zeroize anything
- decide UI state

It only produces:
- a safe signal state
- an adaptive next ping delay

Doctrine:
The ping does not command truth.
It provides evidence.

Latency modulates probe cadence.
Randomness protects the rhythm.

A drastic rupture triggers suspicion.
Loss requires confirmation.

A missing ping does not imply signal loss.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional


SignalState = Literal[
    "SIGNAL_EXCELLENT",
    "SIGNAL_OK",
    "SIGNAL_PROBING",
    "SIGNAL_SUSPECT",
    "SIGNAL_DEGRADED",
    "SIGNAL_LOST",
    "NO_BEARER",
    "UNKNOWN",
]

BearerKind = Literal[
    "PRIMARY_INTERNET",
    "MOBILE_DATA_4G_5G",
    "RETICULUM",
    "LORA_RNODE",
    "OFFLINE",
    "NONE",
]

NetworkSampleKind = Literal[
    "PING",
    "LINK",
    "PASSIVE_TRAFFIC",
]


@dataclass(frozen=True)
class NetworkSample:
    timestamp: float
    bearer: BearerKind = "PRIMARY_INTERNET"
    kind: NetworkSampleKind = "PING"

    link_up: bool = True
    success: bool = True

    latency_ms: Optional[float] = None
    jitter_ms: Optional[float] = None
    packet_loss: float = 0.0

    signal_quality: Optional[float] = None
    rssi_dbm: Optional[float] = None

    rx_errors: int = 0
    tx_errors: int = 0
    rx_drops: int = 0
    tx_drops: int = 0
    throughput_bps: float = 0.0


@dataclass
class PingEvidence:
    samples: List[NetworkSample] = field(default_factory=list)

    last_success_at: Optional[float] = None
    last_attempt_at: Optional[float] = None

    consecutive_failures: int = 0
    in_flight: bool = False

    alternative_activity_seen_at: Optional[float] = None

    def add_sample(self, sample: NetworkSample) -> None:
        self.samples.append(sample)
        self.last_attempt_at = sample.timestamp

        if sample.success:
            self.last_success_at = sample.timestamp
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1


@dataclass(frozen=True)
class AdaptivePingPolicy:
    min_interval_seconds: float = 5.0
    base_interval_seconds: float = 20.0
    max_interval_seconds: float = 90.0

    jitter_ratio: float = 0.25

    excellent_latency_ms: float = 30.0
    ok_latency_ms: float = 150.0
    high_latency_ms: float = 800.0

    excellent_signal_quality: float = 0.90
    ok_signal_quality: float = 0.65
    low_signal_quality: float = 0.40

    low_packet_loss: float = 0.02
    high_packet_loss: float = 0.20

    unstable_jitter_ms: float = 120.0

    drastic_latency_spike_ms: float = 300.0
    drastic_signal_drop: float = 0.35

    degraded_failure_threshold: int = 2
    lost_failure_threshold: int = 4

    stale_success_suspect_seconds: float = 120.0


def guided_link(test_name: str) -> str:
    return (
        "WHISPER_GUIDED_LINK::v1.8.0::"
        "network_signal_loss_v01::"
        f"{test_name}"
    )


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def rssi_dbm_to_quality(rssi_dbm: float) -> float:
    """
    Convert Wi-Fi-like RSSI into a normalized quality.

    -90 dBm and below -> 0.0
    -30 dBm and above -> 1.0
    """

    return clamp((rssi_dbm + 90.0) / 60.0, 0.0, 1.0)


def normalized_signal_quality(sample: NetworkSample) -> Optional[float]:
    if sample.signal_quality is not None:
        return clamp(sample.signal_quality, 0.0, 1.0)

    if sample.rssi_dbm is not None:
        return rssi_dbm_to_quality(sample.rssi_dbm)

    return None


def latest_sample(evidence: PingEvidence) -> Optional[NetworkSample]:
    if not evidence.samples:
        return None

    return evidence.samples[-1]


def previous_sample(evidence: PingEvidence) -> Optional[NetworkSample]:
    if len(evidence.samples) < 2:
        return None

    return evidence.samples[-2]


def bearer_available(sample: NetworkSample) -> bool:
    return sample.link_up and sample.bearer not in {"OFFLINE", "NONE"}


def effective_jitter_ms(evidence: PingEvidence) -> float:
    sample = latest_sample(evidence)

    if sample is not None and sample.jitter_ms is not None:
        return sample.jitter_ms

    latencies = [
        item.latency_ms
        for item in evidence.samples[-5:]
        if item.latency_ms is not None and item.success
    ]

    if len(latencies) < 2:
        return 0.0

    deltas = [
        abs(latencies[index] - latencies[index - 1])
        for index in range(1, len(latencies))
    ]

    if not deltas:
        return 0.0

    return statistics.mean(deltas)


def has_drastic_signal_drop(
    evidence: PingEvidence,
    policy: AdaptivePingPolicy,
) -> bool:
    current = latest_sample(evidence)
    previous = previous_sample(evidence)

    if current is None or previous is None:
        return False

    current_quality = normalized_signal_quality(current)
    previous_quality = normalized_signal_quality(previous)

    if current_quality is None or previous_quality is None:
        return False

    return previous_quality - current_quality >= policy.drastic_signal_drop


def has_sudden_latency_spike(
    evidence: PingEvidence,
    policy: AdaptivePingPolicy,
) -> bool:
    current = latest_sample(evidence)
    previous = previous_sample(evidence)

    if current is None or previous is None:
        return False

    if current.latency_ms is None or previous.latency_ms is None:
        return False

    return current.latency_ms - previous.latency_ms >= policy.drastic_latency_spike_ms


def is_stale_without_confirmed_failure(
    evidence: PingEvidence,
    now: float,
    policy: AdaptivePingPolicy,
) -> bool:
    if evidence.consecutive_failures > 0:
        return False

    if evidence.last_success_at is None:
        return False

    return now - evidence.last_success_at >= policy.stale_success_suspect_seconds


def compute_signal_state(
    evidence: PingEvidence,
    now: float,
    policy: AdaptivePingPolicy = AdaptivePingPolicy(),
) -> SignalState:
    sample = latest_sample(evidence)

    if sample is None:
        if evidence.in_flight:
            return "SIGNAL_PROBING"

        if evidence.last_attempt_at is None:
            return "UNKNOWN"

        return "SIGNAL_SUSPECT"

    if not bearer_available(sample):
        return "NO_BEARER"

    if evidence.consecutive_failures >= policy.lost_failure_threshold:
        return "SIGNAL_LOST"

    if evidence.consecutive_failures >= policy.degraded_failure_threshold:
        return "SIGNAL_DEGRADED"

    if evidence.in_flight:
        return "SIGNAL_PROBING"

    if not sample.success:
        return "SIGNAL_SUSPECT"

    if has_drastic_signal_drop(evidence, policy):
        return "SIGNAL_SUSPECT"

    if has_sudden_latency_spike(evidence, policy):
        return "SIGNAL_SUSPECT"

    if is_stale_without_confirmed_failure(evidence, now, policy):
        return "SIGNAL_SUSPECT"

    quality = normalized_signal_quality(sample)
    latency = sample.latency_ms
    jitter = effective_jitter_ms(evidence)

    if sample.packet_loss >= policy.high_packet_loss:
        return "SIGNAL_DEGRADED"

    if sample.packet_loss > policy.low_packet_loss:
        return "SIGNAL_SUSPECT"

    if jitter >= policy.unstable_jitter_ms:
        return "SIGNAL_SUSPECT"

    quality_excellent = (
        quality is None or quality >= policy.excellent_signal_quality
    )
    quality_ok = quality is None or quality >= policy.ok_signal_quality

    latency_excellent = (
        latency is None or latency <= policy.excellent_latency_ms
    )
    latency_ok = latency is None or latency <= policy.ok_latency_ms

    if quality_excellent and latency_excellent and sample.packet_loss == 0.0:
        return "SIGNAL_EXCELLENT"

    if quality_ok and latency_ok and sample.packet_loss <= policy.low_packet_loss:
        return "SIGNAL_OK"

    return "SIGNAL_SUSPECT"


def compute_next_ping_delay(
    evidence: PingEvidence,
    now: float,
    rng_value: float,
    policy: AdaptivePingPolicy = AdaptivePingPolicy(),
) -> float:
    """
    Compute adaptive next ping delay.

    rng_value is injected for deterministic tests.
    In production, pass random.random().
    """

    rng_value = clamp(rng_value, 0.0, 1.0)

    state = compute_signal_state(evidence, now, policy)
    sample = latest_sample(evidence)

    delay = policy.base_interval_seconds

    if state == "SIGNAL_EXCELLENT":
        delay *= 2.5
    elif state == "SIGNAL_OK":
        delay *= 1.25
    elif state == "SIGNAL_PROBING":
        delay *= 0.75
    elif state == "SIGNAL_SUSPECT":
        delay *= 0.65
    elif state == "SIGNAL_DEGRADED":
        delay *= 0.40
    elif state == "SIGNAL_LOST":
        delay *= 0.50
    elif state == "NO_BEARER":
        delay *= 1.50
    else:
        delay *= 1.00

    if sample is not None:
        quality = normalized_signal_quality(sample)

        if sample.latency_ms is not None:
            if sample.latency_ms <= policy.excellent_latency_ms:
                delay *= 1.20
            elif sample.latency_ms >= policy.high_latency_ms:
                delay *= 0.50

        if quality is not None:
            if quality >= policy.excellent_signal_quality:
                delay *= 1.15
            elif quality <= policy.low_signal_quality:
                delay *= 0.60

        if sample.packet_loss > policy.low_packet_loss:
            delay *= 0.65

        if effective_jitter_ms(evidence) >= policy.unstable_jitter_ms:
            delay *= 0.70

    if evidence.consecutive_failures > 0:
        delay *= max(0.35, 1.0 - (0.20 * evidence.consecutive_failures))

    jitter_offset = (rng_value * 2.0) - 1.0
    jitter_multiplier = 1.0 + (jitter_offset * policy.jitter_ratio)

    delay *= jitter_multiplier

    return clamp(
        delay,
        policy.min_interval_seconds,
        policy.max_interval_seconds,
    )


def signal_detector_destroys_nothing() -> bool:
    """
    Explicit invariant marker.

    This module has no fragment mutation API.
    """

    return True


def signal_loss_summary() -> Dict[str, object]:
    policy = AdaptivePingPolicy()

    evidence = PingEvidence()
    evidence.add_sample(
        NetworkSample(
            timestamp=1.0,
            bearer="PRIMARY_INTERNET",
            link_up=True,
            success=True,
            latency_ms=12.0,
            jitter_ms=2.0,
            packet_loss=0.0,
            signal_quality=0.98,
        )
    )

    excellent_state = compute_signal_state(evidence, now=1.0, policy=policy)
    excellent_delay = compute_next_ping_delay(
        evidence,
        now=1.0,
        rng_value=0.5,
        policy=policy,
    )

    evidence.add_sample(
        NetworkSample(
            timestamp=2.0,
            bearer="PRIMARY_INTERNET",
            link_up=True,
            success=True,
            latency_ms=760.0,
            jitter_ms=180.0,
            packet_loss=0.05,
            signal_quality=0.45,
        )
    )

    suspect_state = compute_signal_state(evidence, now=2.0, policy=policy)
    suspect_delay = compute_next_ping_delay(
        evidence,
        now=2.0,
        rng_value=0.5,
        policy=policy,
    )

    return {
        "excellent_state": excellent_state,
        "excellent_delay_seconds": round(excellent_delay, 3),
        "suspect_state_after_rupture": suspect_state,
        "suspect_delay_seconds": round(suspect_delay, 3),
        "missing_ping_does_not_imply_lost": True,
        "signal_detector_destroys_nothing": signal_detector_destroys_nothing(),
        "scheduler_uses_injected_rng": True,
    }


if __name__ == "__main__":
    summary = signal_loss_summary()

    print("Excellent state:", summary["excellent_state"])
    print("Excellent next ping delay:", summary["excellent_delay_seconds"])
    print("State after rupture:", summary["suspect_state_after_rupture"])
    print("Next ping delay after rupture:", summary["suspect_delay_seconds"])
    print(
        "Missing ping does not imply lost:",
        summary["missing_ping_does_not_imply_lost"],
    )
    print(
        "Signal detector destroys nothing:",
        summary["signal_detector_destroys_nothing"],
    )
    print("Scheduler uses injected RNG:", summary["scheduler_uses_injected_rng"])
