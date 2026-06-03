# REGRESSION_TESTS.md

## Purpose

The regression suite locks deterministic MVP behavior across the v0.4.x components.

It does not prove security.

It protects against accidental behavioral drift in:

```text
RotorMachine
MCEHardened
Loader
Dome
Lemonade
VoxMesh
ReticulumBridge
Vault/VaultDisk
FullPipeline
```

## Run

```bash
pytest -q tests/test_regression_v043.py
```

or:

```bash
python bench/bench_regression.py
```

## What is locked

The regression suite checks:

```text
RotorMachine deterministic bijection per (seed, fragment_id)
MCEHardened stable state sequence
Loader stable decisions
Dome envelope roundtrip
Lemonade stateless report semantics
VoxMesh deterministic mutation
ReticulumBridge packet roundtrip
VaultDisk save/load roundtrip
FullPipeline stable summary shape
```

## What is not locked

The suite does not lock wall-clock timing fields.

The suite does not claim:

```text
confidentiality
integrity
authentication
metadata protection
transport security
Reticulum compatibility
production readiness
```

## Policy

Before every release tag:

```bash
pytest -q
pytest -q tests/test_regression_v043.py
python3 full_pipeline_v01.py
python3 bench/bench_full_pipeline.py --payload-size 1048576
```
