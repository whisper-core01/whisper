from network_medium_selection_v03 import (
    BearerHistory,
    BearerSample,
    NetworkSwitchState,
    PRIMARY_INTERNET,
    MOBILE_DATA_4G_5G,
    LORA_RNODE,
    OFFLINE,
    decide_adaptive_switch,
)


def test_returns_to_primary_only_after_stable_recovery_v03():
    history = BearerHistory()

    for _ in range(2):
        history.add(
            BearerSample(
                PRIMARY_INTERNET,
                True,
                latency_ms=40,
                packet_loss_percent=0,
                jitter_ms=5,
            )
        )

    state = NetworkSwitchState(
        current_bearer=MOBILE_DATA_4G_5G,
        recovery_window=3,
    )

    decision = decide_adaptive_switch(state, history)

    assert decision.bearer == MOBILE_DATA_4G_5G
    assert decision.switched is False
    assert decision.reason == "current_bearer_still_usable"

    history.add(
        BearerSample(
            PRIMARY_INTERNET,
            True,
            latency_ms=35,
            packet_loss_percent=0,
            jitter_ms=4,
        )
    )

    decision = decide_adaptive_switch(state, history)

    assert decision.bearer == PRIMARY_INTERNET
    assert decision.switched is True
    assert decision.reason == "primary_stably_recovered"


def test_stays_on_current_bearer_when_still_usable():
    history = BearerHistory()

    history.add(
        BearerSample(
            MOBILE_DATA_4G_5G,
            True,
            latency_ms=90,
            packet_loss_percent=1,
            jitter_ms=20,
        )
    )

    state = NetworkSwitchState(
        current_bearer=MOBILE_DATA_4G_5G,
    )

    decision = decide_adaptive_switch(state, history)

    assert decision.bearer == MOBILE_DATA_4G_5G
    assert decision.switched is False
    assert decision.reason == "current_bearer_still_usable"


def test_bad_jitter_forces_fallback_to_mobile():
    history = BearerHistory()

    history.add(
        BearerSample(
            PRIMARY_INTERNET,
            True,
            latency_ms=40,
            packet_loss_percent=0,
            jitter_ms=120,
        )
    )

    history.add(
        BearerSample(
            MOBILE_DATA_4G_5G,
            True,
            latency_ms=55,
            packet_loss_percent=0,
            jitter_ms=10,
        )
    )

    state = NetworkSwitchState(
        current_bearer=PRIMARY_INTERNET,
    )

    decision = decide_adaptive_switch(state, history)

    assert decision.bearer == MOBILE_DATA_4G_5G
    assert decision.switched is True
    assert decision.reason == "fallback_to_mobile"


def test_packet_loss_forces_fallback_to_mobile():
    history = BearerHistory()

    history.add(
        BearerSample(
            PRIMARY_INTERNET,
            True,
            latency_ms=30,
            packet_loss_percent=15,
            jitter_ms=5,
        )
    )

    history.add(
        BearerSample(
            MOBILE_DATA_4G_5G,
            True,
            latency_ms=70,
            packet_loss_percent=0,
            jitter_ms=10,
        )
    )

    state = NetworkSwitchState(
        current_bearer=PRIMARY_INTERNET,
    )

    decision = decide_adaptive_switch(state, history)

    assert decision.bearer == MOBILE_DATA_4G_5G
    assert decision.switched is True
    assert decision.reason == "fallback_to_mobile"


def test_primary_is_kept_when_quality_is_close():
    history = BearerHistory()

    history.add(
        BearerSample(
            PRIMARY_INTERNET,
            True,
            latency_ms=45,
            packet_loss_percent=0,
            jitter_ms=8,
            energy_cost=1,
        )
    )

    history.add(
        BearerSample(
            MOBILE_DATA_4G_5G,
            True,
            latency_ms=42,
            packet_loss_percent=0,
            jitter_ms=7,
            energy_cost=2,
        )
    )

    state = NetworkSwitchState(
        current_bearer=PRIMARY_INTERNET,
    )

    decision = decide_adaptive_switch(state, history)

    assert decision.bearer == PRIMARY_INTERNET
    assert decision.switched is False
    assert decision.reason == "current_bearer_still_usable"


def test_lora_is_fallback_when_everything_else_is_down():
    history = BearerHistory()

    history.add(
        BearerSample(
            PRIMARY_INTERNET,
            False,
            latency_ms=0,
            packet_loss_percent=100,
            jitter_ms=0,
        )
    )

    history.add(
        BearerSample(
            MOBILE_DATA_4G_5G,
            False,
            latency_ms=0,
            packet_loss_percent=100,
            jitter_ms=0,
        )
    )

    history.add(
        BearerSample(
            LORA_RNODE,
            True,
            latency_ms=650,
            packet_loss_percent=2,
            jitter_ms=80,
        )
    )

    state = NetworkSwitchState(
        current_bearer=PRIMARY_INTERNET,
    )

    decision = decide_adaptive_switch(state, history)

    assert decision.bearer == LORA_RNODE
    assert decision.switched is True
    assert decision.reason == "fallback_to_lora"


def test_offline_when_no_bearer_available():
    history = BearerHistory()

    history.add(
        BearerSample(
            PRIMARY_INTERNET,
            False,
            latency_ms=0,
            packet_loss_percent=100,
            jitter_ms=0,
        )
    )

    history.add(
        BearerSample(
            MOBILE_DATA_4G_5G,
            False,
            latency_ms=0,
            packet_loss_percent=100,
            jitter_ms=0,
        )
    )

    history.add(
        BearerSample(
            LORA_RNODE,
            False,
            latency_ms=0,
            packet_loss_percent=100,
            jitter_ms=0,
        )
    )

    state = NetworkSwitchState(
        current_bearer=PRIMARY_INTERNET,
    )

    decision = decide_adaptive_switch(state, history)

    assert decision.bearer == OFFLINE
    assert decision.switched is True
    assert decision.reason == "no_available_bearer"
    
def test_detects_signal_loss_after_consecutive_down_samples():
    history = BearerHistory()

    for _ in range(3):
        history.add(
            BearerSample(
                PRIMARY_INTERNET,
                False,
                latency_ms=0,
                packet_loss_percent=100,
                jitter_ms=0,
            )
        )

    assert history.has_signal_loss(
        PRIMARY_INTERNET,
        window=3,
    ) is True
    
def test_does_not_detect_signal_loss_too_early():
    history = BearerHistory()

    for _ in range(2):
        history.add(
            BearerSample(
                PRIMARY_INTERNET,
                False,
                latency_ms=0,
                packet_loss_percent=100,
                jitter_ms=0,
            )
        )

    assert history.has_signal_loss(
        PRIMARY_INTERNET,
        window=3,
    ) is False
    
def test_detects_signal_loss_on_extreme_degradation():
    history = BearerHistory()

    for _ in range(3):
        history.add(
            BearerSample(
                PRIMARY_INTERNET,
                True,
                latency_ms=1500,
                packet_loss_percent=40,
                jitter_ms=350,
            )
        )

    assert history.has_signal_loss(
        PRIMARY_INTERNET,
        window=3,
    ) is True
