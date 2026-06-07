from network_medium_selection_v03 import (
    PRIMARY_INTERNET,
    MOBILE_DATA_4G_5G,
    LORA_RNODE,
    OFFLINE,
    BearerHistory,
    BearerSample,
    NetworkSwitchState,
    decide_adaptive_switch,
)


def add_samples(history, bearer, is_up, latency, loss, jitter, count=1):
    for _ in range(count):
        history.add(
            BearerSample(
                bearer,
                is_up,
                latency_ms=latency,
                packet_loss_percent=loss,
                jitter_ms=jitter,
            )
        )


def run_case(name, current_bearer, samples):
    history = BearerHistory()

    for sample in samples:
        add_samples(
            history,
            sample["bearer"],
            sample["is_up"],
            sample["latency"],
            sample["loss"],
            sample["jitter"],
            sample.get("count", 1),
        )

    state = NetworkSwitchState(current_bearer=current_bearer)
    decision = decide_adaptive_switch(state, history)

    print(f"\n=== {name} ===")
    print("Current bearer:", current_bearer)
    print("Decision bearer:", decision.bearer)
    print("Switched:", decision.switched)
    print("Reason:", decision.reason)

    for bearer in [PRIMARY_INTERNET, MOBILE_DATA_4G_5G, LORA_RNODE]:
        recent = history.by_bearer(bearer)
        if not recent:
            continue

        last = recent[-1]
        print(
            f"{bearer}: "
            f"up={last.is_up}, "
            f"latency={last.latency_ms}ms, "
            f"loss={last.packet_loss_percent}%, "
            f"jitter={last.jitter_ms}ms, "
            f"samples={len(recent)}, "
            f"stable={history.is_stable(bearer)}, "
            f"usable={history.is_usable(bearer)}, "
            f"signal_loss={history.has_signal_loss(bearer)}"
        )


def main():
    run_case(
        "PRIMARY STABLE",
        PRIMARY_INTERNET,
        [
            {
                "bearer": PRIMARY_INTERNET,
                "is_up": True,
                "latency": 40,
                "loss": 0,
                "jitter": 5,
                "count": 3,
            },
            {
                "bearer": MOBILE_DATA_4G_5G,
                "is_up": True,
                "latency": 70,
                "loss": 1,
                "jitter": 20,
                "count": 3,
            },
        ],
    )

    run_case(
        "PRIMARY BAD JITTER -> MOBILE",
        PRIMARY_INTERNET,
        [
            {
                "bearer": PRIMARY_INTERNET,
                "is_up": True,
                "latency": 40,
                "loss": 0,
                "jitter": 400,
                "count": 3,
            },
            {
                "bearer": MOBILE_DATA_4G_5G,
                "is_up": True,
                "latency": 55,
                "loss": 0,
                "jitter": 10,
                "count": 3,
            },
        ],
    )

    run_case(
        "PRIMARY DOWN -> MOBILE",
        PRIMARY_INTERNET,
        [
            {
                "bearer": PRIMARY_INTERNET,
                "is_up": False,
                "latency": 0,
                "loss": 100,
                "jitter": 0,
                "count": 3,
            },
            {
                "bearer": MOBILE_DATA_4G_5G,
                "is_up": True,
                "latency": 80,
                "loss": 2,
                "jitter": 15,
                "count": 3,
            },
        ],
    )

    run_case(
        "PRIMARY + MOBILE DOWN -> LoRa",
        PRIMARY_INTERNET,
        [
            {
                "bearer": PRIMARY_INTERNET,
                "is_up": False,
                "latency": 0,
                "loss": 100,
                "jitter": 0,
                "count": 3,
            },
            {
                "bearer": MOBILE_DATA_4G_5G,
                "is_up": False,
                "latency": 0,
                "loss": 100,
                "jitter": 0,
                "count": 3,
            },
            {
                "bearer": LORA_RNODE,
                "is_up": True,
                "latency": 650,
                "loss": 2,
                "jitter": 80,
                "count": 3,
            },
        ],
    )

    run_case(
        "ALL DOWN -> OFFLINE",
        PRIMARY_INTERNET,
        [
            {
                "bearer": PRIMARY_INTERNET,
                "is_up": False,
                "latency": 0,
                "loss": 100,
                "jitter": 0,
                "count": 3,
            },
            {
                "bearer": MOBILE_DATA_4G_5G,
                "is_up": False,
                "latency": 0,
                "loss": 100,
                "jitter": 0,
                "count": 3,
            },
            {
                "bearer": LORA_RNODE,
                "is_up": False,
                "latency": 0,
                "loss": 100,
                "jitter": 0,
                "count": 3,
            },
        ],
    )

    run_case(
        "MOBILE ACTIVE -> PRIMARY RECOVERED",
        MOBILE_DATA_4G_5G,
        [
            {
                "bearer": PRIMARY_INTERNET,
                "is_up": True,
                "latency": 40,
                "loss": 0,
                "jitter": 5,
                "count": 3,
            },
            {
                "bearer": MOBILE_DATA_4G_5G,
                "is_up": True,
                "latency": 90,
                "loss": 1,
                "jitter": 20,
                "count": 3,
            },
        ],
    )


if __name__ == "__main__":
    main()
