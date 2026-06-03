#!/usr/bin/env bash
set -euo pipefail

echo "== WHISPER FullPipeline benchmark =="
python3 bench/bench_full_pipeline.py --payload-size 1048576
