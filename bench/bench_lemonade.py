# bench/bench_lemonade.py

import argparse
import os
import random
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lemonade_v01 import Lemonade  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fragments", type=int, default=10000)
    parser.add_argument("--payload-size", type=int, default=256)
    parser.add_argument("--bad-rate", type=float, default=0.05)
    args = parser.parse_args()

    rng = random.Random(12345)
    lemonade = Lemonade()
    timings = []
    blocked = 0

    start_total = time.perf_counter()

    for i in range(args.fragments):
        if rng.random() < args.bad_rate:
            fragment = b"WHISPER_POISON" + (b"\x00" * 1001)
            queue_depth = 2048
            fragment_rate = 10000.0
            validation = {"valid": False, "issues": ["bench"]}
        else:
            fragment = os.urandom(args.payload_size)
            queue_depth = 10
            fragment_rate = 100.0
            validation = {"valid": True, "issues": []}

        start = time.perf_counter()
        report = lemonade.scan_fragment_stateless(
            fragment=fragment,
            fragment_id=i,
            queue_depth=queue_depth,
            fragment_rate=fragment_rate,
            validation_report=validation,
        )
        end = time.perf_counter()

        if report.blocked:
            blocked += 1

        timings.append((end - start) * 1000.0)

    elapsed = time.perf_counter() - start_total

    print("Lemonade benchmark")
    print("------------------")
    print(f"fragments:        {args.fragments}")
    print(f"payload size:     {args.payload_size} bytes")
    print(f"bad rate:         {args.bad_rate:.4f}")
    print(f"blocked reports:  {blocked}")
    print(f"global threat:    {lemonade.get_threat_level()}")
    print(f"global signals:   {lemonade.report().signals}")
    print(f"total time:       {elapsed:.3f} s")
    print(f"mean ms/op:       {statistics.mean(timings):.6f}")
    print(f"p95 ms/op:        {statistics.quantiles(timings, n=20)[18]:.6f}")
    print("target:           < 1 ms per stateless scan")


if __name__ == "__main__":
    main()
