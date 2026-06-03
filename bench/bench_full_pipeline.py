# bench/bench_full_pipeline.py

import argparse
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from full_pipeline_v01 import FullPipeline  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload-size", type=int, default=1024 * 1024)
    parser.add_argument("--seed", type=str, default="whisper-final-pipeline-seed")
    args = parser.parse_args()

    payload = os.urandom(args.payload_size)

    pipeline = FullPipeline(args.seed.encode("utf-8"))

    start = time.perf_counter()
    summary = pipeline.process(payload)
    elapsed = time.perf_counter() - start

    print("FullPipeline benchmark")
    print("----------------------")
    print(f"payload size:       {args.payload_size} bytes")
    print(f"fragment size:      {summary['fragment_size']} bytes")
    print(f"fragment count:     {summary['fragment_count']}")
    print(f"route count:        {summary['route_count']}")
    print(f"bridge packets:     {summary['bridge_packets']}")
    print(f"blocked reports:    {summary['blocked_reports']}")
    print(f"elapsed:            {elapsed:.3f} s")
    print(f"throughput MB/sec:  {(args.payload_size / (1024 * 1024)) / elapsed:.3f}")
    print(f"final state:        {summary['final_mce_state_hex']}")


if __name__ == "__main__":
    main()
