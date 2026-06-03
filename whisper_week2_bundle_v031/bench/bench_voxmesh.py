# bench/bench_voxmesh.py

import argparse
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from voxmesh_v01 import VoxMesh  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mutations", type=int, default=1000)
    parser.add_argument("--seed", type=str, default="whisper-voxmesh-seed")
    args = parser.parse_args()

    mesh = VoxMesh(args.seed.encode("utf-8"))
    timings = []

    start_total = time.perf_counter()

    for i in range(args.mutations):
        entropy = b"entropy_%d" % i

        start = time.perf_counter()
        mesh.mutate_all(entropy)
        end = time.perf_counter()

        timings.append((end - start) * 1000.0)

    elapsed = time.perf_counter() - start_total

    print("VoxMesh benchmark")
    print("-----------------")
    print(f"mutations:        {args.mutations}")
    print(f"fractals:         {len(mesh.fractals)}")
    print(f"total time:       {elapsed:.3f} s")
    print(f"mean ms/cycle:    {statistics.mean(timings):.6f}")
    print(f"p95 ms/cycle:     {statistics.quantiles(timings, n=20)[18]:.6f}")
    print(f"divergence:       {mesh.get_divergence_score():.3f}")
    print(f"coherent:         {mesh.coherence_check()}")
    print("target:           < 5 ms per full mutation cycle")


if __name__ == "__main__":
    main()
