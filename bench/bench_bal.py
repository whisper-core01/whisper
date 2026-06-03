# bench/bench_bal.py

import argparse
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bal_v01 import BAL  # noqa: E402
from loader_v01 import Loader  # noqa: E402
from mce_v01 import MCE  # noqa: E402


def direct_indexed_roundtrip(fragments):
    """
    Minimal meaningful baseline:
        - attach an index;
        - recover data in indexed order.

    This is still much simpler than BAL but avoids comparing BAL against a
    meaningless list(fragments) no-op.
    """
    indexed = [(i, fragment) for i, fragment in enumerate(fragments)]
    return [fragment for _i, fragment in indexed]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fragments", type=int, default=10000)
    parser.add_argument("--routes", type=int, default=3)
    args = parser.parse_args()

    fragments = [b"fragment_%d" % i for i in range(args.fragments)]

    direct_timings = []
    bal_timings = []

    # Multiple rounds reduce noise for very fast operations.
    rounds = 10

    for _ in range(rounds):
        direct_start = time.perf_counter()
        direct = direct_indexed_roundtrip(fragments)
        direct_end = time.perf_counter()
        direct_timings.append(direct_end - direct_start)

        bal = BAL(Loader(MCE(b"whisper-bal-seed")), route_count=args.routes)

        bal_start = time.perf_counter()
        bal.distribute(fragments)
        recovered = bal.collect_results()
        bal_end = time.perf_counter()
        bal_timings.append(bal_end - bal_start)

        if recovered != fragments or direct != fragments:
            raise RuntimeError("roundtrip failed")

    direct_elapsed = statistics.median(direct_timings)
    bal_elapsed = statistics.median(bal_timings)
    overhead = ((bal_elapsed / direct_elapsed) - 1.0) * 100.0 if direct_elapsed else 0.0
    ms_per_fragment = (bal_elapsed * 1000.0) / args.fragments if args.fragments else 0.0

    final_bal = BAL(Loader(MCE(b"whisper-bal-seed")), route_count=args.routes)
    final_bal.distribute(fragments)

    print("BAL benchmark")
    print("-------------")
    print(f"fragments:              {args.fragments}")
    print(f"routes:                 {args.routes}")
    print(f"rounds:                 {rounds}")
    print(f"direct indexed median:  {direct_elapsed:.6f} s")
    print(f"BAL median:             {bal_elapsed:.6f} s")
    print(f"overhead vs indexed:    {overhead:.2f}%")
    print(f"BAL ms/fragment:        {ms_per_fragment:.6f}")
    print(f"lane loads:             {final_bal.lane_loads()}")
    print("target:                 report overhead; absolute target < 0.01 ms/fragment")
    print(f"absolute pass:          {ms_per_fragment < 0.01}")


if __name__ == "__main__":
    main()
