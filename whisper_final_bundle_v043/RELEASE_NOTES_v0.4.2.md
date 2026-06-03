# Release Notes — Whisper Remote Nerve MVP v0.4.2

## Status

This is a final MVP integration baseline.

It is not a production security protocol.

## Included components

```text
RotorMachine      deterministic reversible fragment transformation
MCE               state evolution
MCEHardened       state validation and coherence checks
Loader            fragmentation / route / retry decisions
BAL               in-memory parallel lanes
Dome              filtering and envelope
VoxMesh           36-fractal state skeleton
Lemonade          immune-system anomaly skeleton
Vault             in-memory metadata store
VaultDisk         JSON disk persistence
ReticulumBridge   simple bridge encapsulation skeleton
FullPipeline      final end-to-end MVP integration
```

## Full pipeline

```text
payload
  -> Loader
  -> fragment_payload()
  -> Dome wrap/filter
  -> BAL distribute/collect
  -> MCEHardened digest checked
  -> Lemonade stateless scan
  -> ReticulumBridge encapsulation
  -> Vault metadata storage
  -> optional VaultDisk persistence
```

## Non-goals

```text
not encryption
not authenticated transport
not Reticulum integration
not anonymity
not metadata protection
not tamper-resistant persistence
not production-ready
```

## Test command

```bash
pytest -q
```

## Smoke commands

```bash
python3 reticulum_bridge_v01.py
python3 full_pipeline_v01.py
```

## Benchmark command

```bash
python3 bench/bench_full_pipeline.py --payload-size 1048576
```
