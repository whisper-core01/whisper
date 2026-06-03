# Changelog

## v0.4.2

Final MVP integration release candidate.

### Added

- `reticulum_bridge_v01.py`
- `full_pipeline_v01.py`
- `tests/test_reticulum_bridge_v01.py`
- `tests/test_full_pipeline_v01.py`
- `bench/bench_full_pipeline.py`
- `RELEASE_NOTES_v0.4.2.md`

### Behavior

Adds simple bridge encapsulation skeleton and full end-to-end MVP integration test harness.

## v0.4.1

Lemonade benchmark semantics fix.

### Added

- `scan_fragment_stateless()` for per-fragment threat reports.
- Tests ensuring stateless scans do not permanently poison global threat state.

### Fixed

- `bench/bench_lemonade.py` now uses stateless scans.
- Blocked report count now reflects per-fragment blocking, not cumulative global saturation.

### Notes

`scan_fragment()` remains cumulative by design.
`scan_fragment_stateless()` is recommended for benchmarks and per-fragment routing/filtering decisions.

## v0.4.0

Added Lemonade immune-system skeleton.

## v0.3.1

Benchmark correction patch.

### Fixed

- `bench/bench_bal.py`
  - Removed misleading comparison against `list(fragments)` no-op.
  - Added indexed direct baseline.
  - Added absolute `ms/fragment` target.

- `bench/bench_dome.py`
  - Removed double acceptance check.
  - Rejection-rate tracking now matches generated rejection ratio more closely.

### Notes

BAL functional tests passed in v0.3.0. This patch corrects benchmark interpretation, not BAL behavior.

## v0.3.0

Week 2 components: BAL, Dome and VoxMesh.

### Added

- `bal_v01.py`
- `dome_v01.py`
- `voxmesh_v01.py`
- `tests/test_bal_v01.py`
- `tests/test_dome_v01.py`
- `tests/test_voxmesh_v01.py`
- `bench/bench_bal.py`
- `bench/bench_dome.py`
- `bench/bench_voxmesh.py`

### Behavior

BAL adds:

- in-memory parallel lanes;
- round-robin fragment distribution;
- reassembly in original order.

Dome adds:

- simple accept/reject filtering;
- minimal reversible envelope;
- rejection-rate tracking.

VoxMesh adds:

- 36 deterministic fractal states;
- mutation cycles;
- divergence score;
- coherence check.

### Targets

- BAL: < 5% overhead vs direct processing.
- Dome: < 1 ms per wrap/unwrap.
- VoxMesh: < 5 ms per full mutation cycle.

## v0.2.0

Week 1 components: MCE hardening and Loader.

### Added

- `mce_hardened_v01.py`
- `loader_v01.py`
- `tests/test_mce_hardened_v01.py`
- `tests/test_loader_v01.py`
- `tests/test_week1_integration.py`
- `bench/bench_mce_hardened.py`
- `bench/bench_loader.py`

### Behavior

MCEHardened adds:

- state validation;
- coherence checks;
- checked digest wrapper.

Loader adds:

- deterministic fragment size decisions;
- deterministic route count decisions;
- deterministic retry policy.

### Targets

- MCEHardened: < 10% overhead vs MCE v0.1.0.
- Loader: < 1 ms per decision.

## v0.1.8

Benchmark import-path fix.

### Fixed

- `bench/bench_vaultdisk.py` now prepends the project root to `sys.path`.
- Allows VaultDisk benchmark to be launched from outside the bundle directory.

### Added

- `tests/test_bench_import_paths.py` smoke test for external benchmark execution.

## v0.1.7

Added VaultDisk v0.1 JSON disk persistence.

### Added

- `vault_disk_v01.py`
- `tests/test_vault_disk_v01.py`
- `bench/bench_vaultdisk.py`
- README VaultDisk usage section.

### Behavior

VaultDisk persists Vault metadata to deterministic JSON and reloads it into a fresh Vault instance.

### Security notes

VaultDisk is not encrypted storage, not tamper-resistant storage, not secure audit logging, and not rollback-protected.

## v0.1.6

Added end-to-end pipeline demo.

### Added

- `pipeline_demo.py`
- `tests/test_pipeline_demo.py`
- `bench/bench_pipeline.py`
- README pipeline demo section.

### Behavior

Pipeline demo shows:

```text
payload -> fragmentation -> MCE/RotorMachine -> Vault -> JSON summary
```

### Security notes

Pipeline demo is integration-only. It is not encryption and not a production Whisper pipeline.

## v0.1.5

Test runner import-path fix.

### Added

- `tests/conftest.py`

### Fixed

- Allows pytest to be run from the `tests/` directory without `ModuleNotFoundError` for project-level modules such as `mce_v01`, `rotor_machine_v01`, and `vault_v01`.

## v0.1.4

Added Vault v0.1 minimal metadata persistence.

### Added

- `vault_v01.py`
- `tests/test_vault_v01.py`
- `bench/bench_vault.py`
- Vault usage section in README.
- Vault non-guarantees section.
- Explicit system split:
  - RotorMachine = transformation;
  - MCE = state evolution;
  - Vault = state persistence.

### Security notes

Vault v0.1 is an in-memory metadata store only. It is not encrypted storage, not tamper-resistant storage, and not a key vault.

## v0.1.3

README and documentation hardening.

### Added

- Explicit statement: `RotorMachine is deterministic per (seed, fragment_id)`.
- Explicit bijection statement for a given `(seed, fragment_id)`.
- Unicode behavior section.
- Byte mode behavior section.
- Non-guarantees section.
- MCE usage section.
- MCE non-guarantees.
- Operational recommendation section.

## v0.1.2

Added MCE integration bundle.

## v0.1.1

RotorMachine MVP hardening.

## v0.1.0

Initial RotorMachine MVP.
