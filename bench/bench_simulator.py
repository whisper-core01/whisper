from __future__ import annotations

import argparse
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulation_runner_v01 import run_simulation


DEFAULT_CONFIG = {
    "experiment_id": "bench-v060",
    "whisper_version": "v0.6.0",
    "topology": {
        "type": "erdos_renyi",
        "node_count": 100,
        "edge_probability": 0.05
    },
    "policy": {
        "type": "whisper_structural_divergence",
        "route_count": 3,
        "fractal_count": 36
    },
    "payload": {
        "size_bytes": 1048576,
        "fragment_size": 1024
    }
}


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0

    ordered = sorted(values)
    index = int(round((len(ordered) - 1) * p))
    return ordered[index]


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark WHISPER v0.6.0 simulator")
    parser.add_argument("--runs", type=int, default=100)
    args = parser.parse_args()

    if args.runs < 1:
        raise ValueError("--runs must be >= 1")

    durations = []

    start_total = time.perf_counter()

    for i in range(args.runs):
        seed = f"bench-run-{i:04d}"
        start = time.perf_counter()
        run_simulation(DEFAULT_CONFIG, seed)
        durations.append(time.perf_counter() - start)

    total = time.perf_counter() - start_total
    mean = statistics.mean(durations)
    median = statistics.median(durations)
    p95 = percentile(durations, 0.95)
    runs_per_second = args.runs / total if total else 0.0

    print("Simulator benchmark")
    print("-------------------")
    print(f"runs:              {args.runs}")
    print(f"total seconds:     {total:.6f}")
    print(f"mean ms/run:       {mean * 1000:.6f}")
    print(f"median ms/run:     {median * 1000:.6f}")
    print(f"p95 ms/run:        {p95 * 1000:.6f}")
    print(f"runs/sec:          {runs_per_second:.2f}")

    if mean > 5.0:
        print("warning: mean runtime > 5s/run; reduce conditions or optimize simulator")
    elif mean > 2.0:
        print("warning: mean runtime > 2s/run; prefer n=10 or n=20 pilot")
    elif mean > 0.5:
        print("warning: mean runtime > 0.5s/run; n=30 only on priority conditions")
    else:
        print("status:            fast enough for n=30 pilot")


if __name__ == "__main__":
    main()
