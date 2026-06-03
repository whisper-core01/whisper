# bench/bench_mce_hardened.py

import argparse
import os
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mce_v01 import MCE  # noqa: E402
from mce_hardened_v01 import MCEHardened  # noqa: E402


def run_plain(fragments, seed: bytes):
    mce = MCE(seed)
    timings = []

    start_total = time.perf_counter()

    for fragment in fragments:
        start = time.perf_counter()
        mce.digest_fragment(fragment)
        end = time.perf_counter()
        timings.append((end - start) * 1000.0)

    return time.perf_counter() - start_total, timings


def run_hardened(fragments, seed: bytes):
    mce = MCEHardened(seed)
    timings = []

    start_total = time.perf_counter()

    for fragment in fragments:
        start = time.perf_counter()
        mce.digest_fragment_checked(fragment)
        end = time.perf_counter()
        timings.append((end - start) * 1000.0)

    return time.perf_counter() - start_total, timings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fragments", type=int, default=10000)
    parser.add_argument("--payload-size", type=int, default=256)
    parser.add_argument("--seed", type=str, default="whisper-mce-hardened-seed")
    args = parser.parse_args()

    seed = args.seed.encode("utf-8")
    fragments = [os.urandom(args.payload_size) for _ in range(args.fragments)]

    plain_elapsed, plain_timings = run_plain(fragments, seed)
    hardened_elapsed, hardened_timings = run_hardened(fragments, seed)

    overhead = ((hardened_elapsed / plain_elapsed) - 1.0) * 100.0 if plain_elapsed else 0.0

    print("MCE Hardened benchmark")
    print("----------------------")
    print(f"fragments:             {args.fragments}")
    print(f"payload size:          {args.payload_size} bytes")
    print(f"plain total:           {plain_elapsed:.3f} s")
    print(f"hardened total:        {hardened_elapsed:.3f} s")
    print(f"overhead:              {overhead:.2f}%")
    print(f"plain mean ms/op:      {statistics.mean(plain_timings):.4f}")
    print(f"hardened mean ms/op:   {statistics.mean(hardened_timings):.4f}")
    print(f"hardened p95 ms/op:    {statistics.quantiles(hardened_timings, n=20)[18]:.4f}")
    print("target overhead:       < 10%")


if __name__ == "__main__":
    main()
