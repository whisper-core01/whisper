#!/usr/bin/env bash
set -euo pipefail

echo "== WHISPER artifact validation =="

REQUIRED_FILES=(
  "experiments/example.json"
  "schemas/simulation_run.schema.json"
  "schemas/metrics_report.schema.json"
  "schemas/topology_graph.schema.json"
  "schemas/baseline_comparison.schema.json"
  "outputs/run_001.json"
  "outputs/run_002.json"
  "outputs/run_003.json"
  "outputs/summary.csv"
  "SIMULATION_REPORT_v0.6.0.md"
)

for f in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$f" ]; then
    echo "missing: $f"
    exit 1
  fi
  echo "ok: $f"
done

python3 - <<'PY'
import csv
import json
from pathlib import Path

required_run_fields = [
    "schema_version",
    "metadata",
    "topology",
    "policy",
    "paths",
    "results",
]

required_metadata_fields = [
    "experiment_id",
    "seed",
    "whisper_version",
]

required_result_fields = [
    "path_count",
    "unique_path_ratio",
    "path_overlap",
]

for path in sorted(Path("outputs").glob("run_*.json")):
    data = json.loads(path.read_text())

    for field in required_run_fields:
        assert field in data, f"{path}: missing {field}"

    for field in required_metadata_fields:
        assert field in data["metadata"], f"{path}: missing metadata.{field}"

    for field in required_result_fields:
        assert field in data["results"], f"{path}: missing results.{field}"

    assert isinstance(data["paths"], list), f"{path}: paths must be a list"
    assert 0.0 <= data["results"]["unique_path_ratio"] <= 1.0
    assert 0.0 <= data["results"]["path_overlap"] <= 1.0

summary = Path("outputs/summary.csv")
rows = list(csv.DictReader(summary.open()))

assert len(rows) >= 3, "summary.csv must contain at least 3 rows"

for row in rows:
    for field in [
        "run_file",
        "seed",
        "topology",
        "node_count",
        "edge_count",
        "path_count",
        "unique_path_ratio",
        "path_overlap",
    ]:
        assert field in row, f"summary.csv missing {field}"

print("json/csv validation: OK")
PY

echo "artifact validation: OK"
