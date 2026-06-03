# bench/bench_loader.py

import argparse
import random
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from loader_v01 import Loader  # noqa: E402
from mce_v01 import MCE  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--payloads", type=int, default=10000)
    parser.add_argument("--seed", type=str, default="whisper-loader-seed")
    args = parser.parse_args()

    rng = random.Random(12345)
    payload_sizes = [rng.randint(0, 2 * 1024 * 1024) for _ in range(args.payloads)]

    mce = MCE(args.seed.encode("utf-8"))
    loader = Loader(mce)

    timings = []
    start_total = time.perf_counter()

    for payload_size in payload_sizes:
        start = time.perf_counter()
        loader.decide_all(payload_size)
        end = time.perf_counter()
        timings.append((end - start) * 1000.0)

    elapsed = time.perf_counter() - start_total

    print("Loader benchmark")
    print("----------------")
    print(f"payloads:        {args.payloads}")
    print(f"total time:      {elapsed:.6f} s")
    print(f"decisions/sec:   {args.payloads / elapsed:.2f}")
    print(f"mean ms/op:      {statistics.mean(timings):.6f}")
    print(f"median ms/op:    {statistics.median(timings):.6f}")
    print(f"p95 ms/op:       {statistics.quantiles(timings, n=20)[18]:.6f}")
    print("target:          < 1 ms per decision")


if __name__ == "__main__":
    main()
