from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


PRIMARY_INTERNET = "PRIMARY_INTERNET"
MOBILE_DATA_4G_5G = "MOBILE_DATA_4G_5G"
LORA_RNODE = "LORA_RNODE"
OFFLINE = "OFFLINE"


@dataclass(frozen=True)
class BearerSample:
    bearer: str
    is_up: bool
    latency_ms: int = 0
    packet_loss_percent: float = 0.0
    jitter_ms: int = 0
    energy_cost: int = 1


@dataclass
class BearerHistory:
    samples: List[BearerSample] = field(default_factory=list)

    def add(self, sample: BearerSample) -> None:
        self.samples.append(sample)

    def by_bearer(self, bearer: str) -> List[BearerSample]:
        return [
            sample
            for sample in self.samples
            if sample.bearer == bearer
        ]

    def recent_by_bearer(self, bearer: str, window: int) -> List[BearerSample]:
        return self.by_bearer(bearer)[-window:]

    def is_stable(
        self,
        bearer: str,
        min_samples: int = 3,
        max_latency_ms: int = 100,
        max_packet_loss_percent: float = 1.0,
        max_jitter_ms: int = 30,
    ) -> bool:
        recent_samples = self.recent_by_bearer(bearer, min_samples)

        if len(recent_samples) < min_samples:
            return False

        return all(
            sample.is_up
            and sample.latency_ms <= max_latency_ms
            and sample.packet_loss_percent <= max_packet_loss_percent
            and sample.jitter_ms <= max_jitter_ms
            for sample in recent_samples
        )

    def is_usable(
        self,
        bearer: str,
        min_samples: int = 1,
        max_latency_ms: int = 800,
        max_packet_loss_percent: float = 10.0,
        max_jitter_ms: int = 100,
    ) -> bool:
        recent_samples = self.recent_by_bearer(bearer, min_samples)

        if len(recent_samples) < min_samples:
            return False

        return all(
            sample.is_up
            and sample.latency_ms <= max_latency_ms
            and sample.packet_loss_percent <= max_packet_loss_percent
            and sample.jitter_ms <= max_jitter_ms
            for sample in recent_samples
        )

    def has_signal_loss(
        self,
        bearer: str,
        window: int = 3,
        max_latency_ms: int = 1200,
        max_packet_loss_percent: float = 30.0,
        max_jitter_ms: int = 300,
    ) -> bool:
        recent_samples = self.recent_by_bearer(bearer, window)

        if len(recent_samples) < window:
            return False

        hard_down = all(
            not sample.is_up
            for sample in recent_samples
        )

        degraded_signal = all(
            sample.is_up
            and (
                sample.latency_ms >= max_latency_ms
                or sample.packet_loss_percent >= max_packet_loss_percent
                or sample.jitter_ms >= max_jitter_ms
            )
            for sample in recent_samples
        )

        return hard_down or degraded_signal
@dataclass(frozen=True)
class NetworkSwitchState:
    current_bearer: str = PRIMARY_INTERNET
    recovery_window: int = 3


@dataclass(frozen=True)
class NetworkDecision:
    bearer: str
    switched: bool
    reason: str


def decide_adaptive_switch(
    state: NetworkSwitchState,
    history: BearerHistory,
) -> NetworkDecision:
    primary_stably_recovered = history.is_stable(
        bearer=PRIMARY_INTERNET,
        min_samples=state.recovery_window,
        max_latency_ms=100,
        max_packet_loss_percent=1.0,
        max_jitter_ms=30,
    )

    if (
        state.current_bearer != PRIMARY_INTERNET
        and primary_stably_recovered
    ):
        return NetworkDecision(
            bearer=PRIMARY_INTERNET,
            switched=True,
            reason="primary_stably_recovered",
        )

    current_bearer_still_usable = history.is_usable(
        bearer=state.current_bearer,
        max_latency_ms=700,
        max_packet_loss_percent=5.0,
        max_jitter_ms=100,
    )

    if current_bearer_still_usable:
        return NetworkDecision(
            bearer=state.current_bearer,
            switched=False,
            reason="current_bearer_still_usable",
        )

    current_bearer_has_no_sample = (
        state.current_bearer != PRIMARY_INTERNET
        and len(history.by_bearer(state.current_bearer)) == 0
    )

    if current_bearer_has_no_sample:
        return NetworkDecision(
            bearer=state.current_bearer,
            switched=False,
            reason="current_bearer_still_usable",
        )

    mobile_usable = history.is_usable(
        bearer=MOBILE_DATA_4G_5G,
        max_latency_ms=250,
        max_packet_loss_percent=5.0,
        max_jitter_ms=80,
    )

    if mobile_usable:
        return NetworkDecision(
            bearer=MOBILE_DATA_4G_5G,
            switched=state.current_bearer != MOBILE_DATA_4G_5G,
            reason="fallback_to_mobile",
        )

    satellite_usable = history.is_usable(
        bearer=LORA_RNODE,
        max_latency_ms=900,
        max_packet_loss_percent=10.0,
        max_jitter_ms=150,
    )

    if satellite_usable:
        return NetworkDecision(
            bearer=LORA_RNODE,
            switched=state.current_bearer != LORA_RNODE,
            reason="fallback_to_lora",
        )

    return NetworkDecision(
        bearer=OFFLINE,
        switched=state.current_bearer != OFFLINE,
        reason="no_available_bearer",
    )
