# bench/bench_dome.py

import argparse
import os
import random
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dome_v01 import Dome  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fragments", type=int, default=10000)
    parser.add_argument("--payload-size", type=int, default=256)
    parser.add_argument("--rejection-rate", type=float, default=0.05)
    args = parser.parse_args()

    rng = random.Random(12345)
    dome = Dome()
    timings = []
    accepted = 0
    rejected = 0

    start_total = time.perf_counter()

    for i in range(args.fragments):
        if rng.random() < args.rejection_rate:
            fragment = b"\x00" * (Dome.MAX_NULL_RUN + 1)
        else:
            fragment = os.urandom(args.payload_size)

        start = time.perf_counter()

        try:
            # Do not call should_accept() before wrap_fragment().
            # wrap_fragment() already performs exactly one tracked acceptance check.
            wrapped = dome.wrap_fragment(fragment, metadata=f"id={i}")
            unwrapped, _metadata = dome.unwrap_fragment(wrapped)
            assert unwrapped == fragment
            accepted += 1
        except ValueError:
            rejected += 1

        end = time.perf_counter()
        timings.append((end - start) * 1000.0)

    elapsed = time.perf_counter() - start_total

    print("Dome benchmark")
    print("--------------")
    print(f"fragments:        {args.fragments}")
    print(f"payload size:     {args.payload_size} bytes")
    print(f"accepted:         {accepted}")
    print(f"rejected:         {rejected}")
    print(f"requested reject: {args.rejection_rate:.4f}")
    print(f"tracked reject:   {dome.get_rejection_rate():.4f}")
    print(f"total time:       {elapsed:.3f} s")
    print(f"mean ms/op:       {statistics.mean(timings):.6f}")
    print(f"p95 ms/op:        {statistics.quantiles(timings, n=20)[18]:.6f}")
    print("target:           < 1 ms per wrap/unwrap")


if __name__ == "__main__":
    main()
