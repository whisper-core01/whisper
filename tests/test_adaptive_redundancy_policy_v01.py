from adaptive_redundancy_policy_v01 import (
    NetworkSymptoms,
    adaptive_custody_rounds,
    adaptive_receive_mode,
    adaptive_redundancy_factor,
    build_adaptive_redundancy_profile,
    compute_network_risk,
)


def test_compute_network_risk_bounds():
    symptoms = NetworkSymptoms(
        latency_risk=2.0,
        jitter_risk=-1.0,
        timeout_risk=0.5,
        signal_loss_risk=0.5,
        receiver_capacity_risk=0.0,
    )

    risk = compute_network_risk(symptoms)

    assert 0.0 <= risk <= 1.0


def test_adaptive_redundancy_factor_increases_with_risk():
    low = adaptive_redundancy_factor(0.0)
    high = adaptive_redundancy_factor(1.0)

    assert low == 1.25
    assert high == 1.40
    assert high > low


def test_adaptive_custody_rounds_increases_with_risk():
    low = adaptive_custody_rounds(0.0)
    high = adaptive_custody_rounds(1.0)

    assert low == 5
    assert high == 7
    assert high > low


def test_receive_mode_streaming_when_capacity_constrained():
    symptoms = NetworkSymptoms(
        latency_risk=0.1,
        jitter_risk=0.1,
        timeout_risk=0.1,
        signal_loss_risk=0.1,
        receiver_capacity_risk=0.9,
    )

    assert adaptive_receive_mode(symptoms) == "STREAMING"


def test_build_profile_good_network():
    profile = build_adaptive_redundancy_profile(
        NetworkSymptoms(
            latency_risk=0.0,
            jitter_risk=0.0,
            timeout_risk=0.0,
            signal_loss_risk=0.0,
            receiver_capacity_risk=0.0,
        )
    )

    assert profile.network_risk == 0.0
    assert profile.redundancy_factor == 1.25
    assert profile.custody_rounds == 5
    assert profile.receive_mode == "BUFFERED"


def test_build_profile_bad_network():
    profile = build_adaptive_redundancy_profile(
        NetworkSymptoms(
            latency_risk=1.0,
            jitter_risk=1.0,
            timeout_risk=1.0,
            signal_loss_risk=1.0,
            receiver_capacity_risk=1.0,
        )
    )

    assert profile.network_risk == 1.0
    assert profile.redundancy_factor == 1.40
    assert profile.custody_rounds == 7
    assert profile.receive_mode == "STREAMING"
