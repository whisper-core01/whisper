#!/usr/bin/env bash
set -euo pipefail

echo "== WHISPER simulation stub =="
echo "Simulation runner will be implemented in v0.6.0."
echo "Example config: experiments/example.json"

if [ -f experiments/example.json ]; then
  cat experiments/example.json
else
  echo "Missing experiments/example.json"
  exit 1
fi
