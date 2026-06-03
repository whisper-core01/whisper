#!/usr/bin/env bash
set -euo pipefail

echo "== WHISPER test suite =="
pytest -q tests

echo "== WHISPER regression suite =="
pytest -q tests/test_regression_v043.py
