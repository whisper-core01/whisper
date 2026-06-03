# Changelog

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
