from network_signal_loss_v01 import (
    AdaptivePingPolicy,
    NetworkSample,
    PingEvidence,
    bearer_available,
    compute_next_ping_delay,
    compute_signal_state,
    effective_jitter_ms,
    guided_link,
    has_drastic_signal_drop,
    has_sudden_latency_spike,
    normalized_signal_quality,
    rssi_dbm_to_quality,
    signal_detector_destroys_nothing,
    signal_loss_summary,
)


def test_unknown_when_no_evidence():
    assert guided_link("unknown_when_no_evidence")

    evidence = PingEvidence()

    assert compute_signal_state(evidence, now=0.0) == "UNKNOWN"


def test_in_flight_returns_probing():
    assert guided_link("in_flight_returns_probing")

    evidence = PingEvidence(in_flight=True)

    assert compute_signal_state(evidence, now=0.0) == "SIGNAL_PROBING"


def test_no_bearer_returns_no_bearer():
    assert guided_link("no_bearer_returns_no_bearer")

    evidence = PingEvidence()
    evidence.add_sample(
        NetworkSample(
            timestamp=1.0,
            bearer="NONE",
            link_up=False,
            success=False,
        )
    )

    assert compute_signal_state(evidence, now=1.0) == "NO_BEARER"


def test_offline_bearer_returns_no_bearer():
    assert guided_link("offline_bearer_returns_no_bearer")

    evidence = PingEvidence()
    evidence.add_sample(
        NetworkSample(
            timestamp=1.0,
            bearer="OFFLINE",
            link_up=False,
            success=False,
        )
    )

    assert compute_signal_state(evidence, now=1.0) == "NO_BEARER"


def test_bearer_available_for_active_link():
    assert guided_link("bearer_available_for_active_link")

    sample = NetworkSample(
        timestamp=1.0,
        bearer="PRIMARY_INTERNET",
        link_up=True,
        success=True,
    )

    assert bearer_available(sample) is True


def test_bearer_unavailable_for_none_or_down_link():
    assert guided_link("bearer_unavailable_for_none_or_down_link")

    none_sample = NetworkSample(
        timestamp=1.0,
        bearer="NONE",
        link_up=True,
        success=False,
    )

    down_sample = NetworkSample(
        timestamp=1.0,
        bearer="PRIMARY_INTERNET",
        link_up=False,
        success=False,
    )

    assert bearer_available(none_sample) is False
    assert bearer_available(down_sample) is False


def test_rssi_dbm_to_quality_is_clamped():
    assert guided_link("rssi_dbm_to_quality_is_clamped")

    assert rssi_dbm_to_quality(-120.0) == 0.0
    assert rssi_dbm_to_quality(-30.0) == 1.0
    assert 0.0 < rssi_dbm_to_quality(-60.0) < 1.0


def test_normalized_signal_quality_prefers_explicit_quality():
    assert guided_link("normalized_signal_quality_prefers_explicit_quality")

    sample = NetworkSample(
        timestamp=1.0,
        signal_quality=0.75,
        rssi_dbm=-30.0,
    )

    assert normalized_signal_quality(sample) == 0.75


def test_excellent_signal_returns_excellent_state():
    assert guided_link("excellent_signal_returns_excellent_state")

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

    assert compute_signal_state(evidence, now=1.0) == "SIGNAL_EXCELLENT"


def test_normal_signal_returns_ok_state():
    assert guided_link("normal_signal_returns_ok_state")

    evidence = PingEvidence()
    evidence.add_sample(
        NetworkSample(
            timestamp=1.0,
            bearer="PRIMARY_INTERNET",
            link_up=True,
            success=True,
            latency_ms=80.0,
            jitter_ms=10.0,
            packet_loss=0.0,
            signal_quality=0.80,
        )
    )

    assert compute_signal_state(evidence, now=1.0) == "SIGNAL_OK"


def test_drastic_signal_drop_triggers_suspect_state():
    assert guided_link("drastic_signal_drop_triggers_suspect_state")

    evidence = PingEvidence()
    policy = AdaptivePingPolicy()

    evidence.add_sample(
        NetworkSample(
            timestamp=1.0,
            latency_ms=20.0,
            packet_loss=0.0,
            signal_quality=0.95,
            success=True,
        )
    )

    evidence.add_sample(
        NetworkSample(
            timestamp=2.0,
            latency_ms=25.0,
            packet_loss=0.0,
            signal_quality=0.45,
            success=True,
        )
    )

    assert has_drastic_signal_drop(evidence, policy) is True
    assert compute_signal_state(evidence, now=2.0, policy=policy) == "SIGNAL_SUSPECT"


def test_sudden_latency_spike_triggers_suspect_state():
    assert guided_link("sudden_latency_spike_triggers_suspect_state")

    evidence = PingEvidence()
    policy = AdaptivePingPolicy()

    evidence.add_sample(
        NetworkSample(
            timestamp=1.0,
            latency_ms=20.0,
            packet_loss=0.0,
            signal_quality=0.90,
            success=True,
        )
    )

    evidence.add_sample(
        NetworkSample(
            timestamp=2.0,
            latency_ms=650.0,
            packet_loss=0.0,
            signal_quality=0.90,
            success=True,
        )
    )

    assert has_sudden_latency_spike(evidence, policy) is True
    assert compute_signal_state(evidence, now=2.0, policy=policy) == "SIGNAL_SUSPECT"


def test_packet_loss_triggers_degraded_state():
    assert guided_link("packet_loss_triggers_degraded_state")

    evidence = PingEvidence()

    evidence.add_sample(
        NetworkSample(
            timestamp=1.0,
            latency_ms=70.0,
            packet_loss=0.30,
            signal_quality=0.80,
            success=True,
        )
    )

    assert compute_signal_state(evidence, now=1.0) == "SIGNAL_DEGRADED"


def test_repeated_failures_trigger_degraded_then_lost():
    assert guided_link("repeated_failures_trigger_degraded_then_lost")

    policy = AdaptivePingPolicy(
        degraded_failure_threshold=2,
        lost_failure_threshold=4,
    )

    evidence = PingEvidence()

    evidence.add_sample(NetworkSample(timestamp=1.0, success=False))
    assert compute_signal_state(evidence, now=1.0, policy=policy) == "SIGNAL_SUSPECT"

    evidence.add_sample(NetworkSample(timestamp=2.0, success=False))
    assert compute_signal_state(evidence, now=2.0, policy=policy) == "SIGNAL_DEGRADED"

    evidence.add_sample(NetworkSample(timestamp=3.0, success=False))
    assert compute_signal_state(evidence, now=3.0, policy=policy) == "SIGNAL_DEGRADED"

    evidence.add_sample(NetworkSample(timestamp=4.0, success=False))
    assert compute_signal_state(evidence, now=4.0, policy=policy) == "SIGNAL_LOST"


def test_single_missing_ping_does_not_trigger_lost():
    assert guided_link("single_missing_ping_does_not_trigger_lost")

    evidence = PingEvidence(
        last_attempt_at=1.0,
        last_success_at=1.0,
        consecutive_failures=0,
    )

    state = compute_signal_state(evidence, now=200.0)

    assert state == "SIGNAL_SUSPECT"


def test_stale_ping_without_failures_returns_suspect_not_lost():
    assert guided_link("stale_ping_without_failures_returns_suspect_not_lost")

    evidence = PingEvidence()
    evidence.add_sample(
        NetworkSample(
            timestamp=1.0,
            latency_ms=30.0,
            packet_loss=0.0,
            signal_quality=0.90,
            success=True,
        )
    )

    state = compute_signal_state(evidence, now=200.0)

    assert state == "SIGNAL_SUSPECT"
    assert state != "SIGNAL_LOST"


def test_effective_jitter_can_be_computed_from_latency_deltas():
    assert guided_link("effective_jitter_can_be_computed_from_latency_deltas")

    evidence = PingEvidence()
    evidence.add_sample(NetworkSample(timestamp=1.0, latency_ms=10.0))
    evidence.add_sample(NetworkSample(timestamp=2.0, latency_ms=20.0))
    evidence.add_sample(NetworkSample(timestamp=3.0, latency_ms=50.0))

    assert effective_jitter_ms(evidence) == 20.0


def test_excellent_signal_increases_ping_delay():
    assert guided_link("excellent_signal_increases_ping_delay")

    policy = AdaptivePingPolicy(base_interval_seconds=20.0)
    evidence = PingEvidence()
    evidence.add_sample(
        NetworkSample(
            timestamp=1.0,
            latency_ms=10.0,
            jitter_ms=1.0,
            packet_loss=0.0,
            signal_quality=0.99,
            success=True,
        )
    )

    delay = compute_next_ping_delay(
        evidence,
        now=1.0,
        rng_value=0.5,
        policy=policy,
    )

    assert delay > policy.base_interval_seconds


def test_near_zero_latency_increases_ping_delay():
    assert guided_link("near_zero_latency_increases_ping_delay")

    policy = AdaptivePingPolicy(base_interval_seconds=20.0)
    evidence = PingEvidence()
    evidence.add_sample(
        NetworkSample(
            timestamp=1.0,
            latency_ms=1.0,
            jitter_ms=0.0,
            packet_loss=0.0,
            signal_quality=0.95,
            success=True,
        )
    )

    delay = compute_next_ping_delay(
        evidence,
        now=1.0,
        rng_value=0.5,
        policy=policy,
    )

    assert delay > policy.base_interval_seconds


def test_high_latency_decreases_ping_delay():
    assert guided_link("high_latency_decreases_ping_delay")

    policy = AdaptivePingPolicy(base_interval_seconds=20.0)
    evidence = PingEvidence()
    evidence.add_sample(
        NetworkSample(
            timestamp=1.0,
            latency_ms=950.0,
            jitter_ms=80.0,
            packet_loss=0.0,
            signal_quality=0.70,
            success=True,
        )
    )

    delay = compute_next_ping_delay(
        evidence,
        now=1.0,
        rng_value=0.5,
        policy=policy,
    )

    assert delay < policy.base_interval_seconds


def test_jitter_decreases_ping_delay():
    assert guided_link("jitter_decreases_ping_delay")

    policy = AdaptivePingPolicy(base_interval_seconds=20.0)
    evidence = PingEvidence()
    evidence.add_sample(
        NetworkSample(
            timestamp=1.0,
            latency_ms=80.0,
            jitter_ms=200.0,
            packet_loss=0.0,
            signal_quality=0.80,
            success=True,
        )
    )

    delay = compute_next_ping_delay(
        evidence,
        now=1.0,
        rng_value=0.5,
        policy=policy,
    )

    assert delay < policy.base_interval_seconds


def test_failures_decrease_ping_delay_without_spam():
    assert guided_link("failures_decrease_ping_delay_without_spam")

    policy = AdaptivePingPolicy(
        min_interval_seconds=5.0,
        base_interval_seconds=20.0,
    )

    evidence = PingEvidence()
    evidence.add_sample(NetworkSample(timestamp=1.0, success=False))
    evidence.add_sample(NetworkSample(timestamp=2.0, success=False))

    delay = compute_next_ping_delay(
        evidence,
        now=2.0,
        rng_value=0.5,
        policy=policy,
    )

    assert delay < policy.base_interval_seconds
    assert delay >= policy.min_interval_seconds


def test_next_ping_delay_is_clamped_between_min_and_max():
    assert guided_link("next_ping_delay_is_clamped_between_min_and_max")

    policy = AdaptivePingPolicy(
        min_interval_seconds=5.0,
        base_interval_seconds=100.0,
        max_interval_seconds=90.0,
    )

    evidence = PingEvidence()
    evidence.add_sample(
        NetworkSample(
            timestamp=1.0,
            latency_ms=1.0,
            jitter_ms=0.0,
            packet_loss=0.0,
            signal_quality=1.0,
            success=True,
        )
    )

    delay = compute_next_ping_delay(
        evidence,
        now=1.0,
        rng_value=1.0,
        policy=policy,
    )

    assert delay == policy.max_interval_seconds


def test_scheduler_keeps_random_jitter_with_injected_rng():
    assert guided_link("scheduler_keeps_random_jitter_with_injected_rng")

    policy = AdaptivePingPolicy(base_interval_seconds=20.0, jitter_ratio=0.25)

    evidence = PingEvidence()
    evidence.add_sample(
        NetworkSample(
            timestamp=1.0,
            latency_ms=80.0,
            jitter_ms=10.0,
            packet_loss=0.0,
            signal_quality=0.80,
            success=True,
        )
    )

    low_rng_delay = compute_next_ping_delay(
        evidence,
        now=1.0,
        rng_value=0.0,
        policy=policy,
    )

    high_rng_delay = compute_next_ping_delay(
        evidence,
        now=1.0,
        rng_value=1.0,
        policy=policy,
    )

    assert low_rng_delay < high_rng_delay


def test_signal_detector_destroys_nothing():
    assert guided_link("signal_detector_destroys_nothing")

    assert signal_detector_destroys_nothing() is True


def test_signal_loss_summary():
    assert guided_link("signal_loss_summary")

    summary = signal_loss_summary()

    assert summary["excellent_state"] == "SIGNAL_EXCELLENT"
    assert summary["excellent_delay_seconds"] > 20.0
    assert summary["suspect_state_after_rupture"] == "SIGNAL_SUSPECT"
    assert summary["suspect_delay_seconds"] < summary["excellent_delay_seconds"]
    assert summary["missing_ping_does_not_imply_lost"] is True
    assert summary["signal_detector_destroys_nothing"] is True
    assert summary["scheduler_uses_injected_rng"] is True
