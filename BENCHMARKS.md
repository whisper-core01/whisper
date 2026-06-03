# BENCHMARKS.md — WHISPER Remote Nerve MVP v0.4.3

## Status

These are MVP smoke benchmarks.

They are intended to document functional performance of the current Python prototype.

They are **not security claims**.

They do not prove:

```text
confidentiality
anonymity
metadata protection
traffic-analysis resistance
Sybil resistance
DoS resistance
network-level resilience
```

The current benchmark results only show that the local MVP pipeline executes, remains coherent, and stays within practical prototype-level performance bounds.

---

## Environment

Observed local test environment:

```text
Machine: ASUS Vivobook 16 V3607VU
OS: Linux
Python: 3.14
Execution mode: local Python MVP
Date: 2026-06-03
```

Exact CPU, RAM, kernel, and Python build should be added before external publication if precise reproducibility is required.

---

## Validation summary

Latest validated release:

```text
Version: v0.4.3
Status: final MVP baseline + regression suite
```

Validation commands:

```bash
pytest -q
pytest -q tests/test_regression_v043.py
python3 full_pipeline_v01.py
python3 bench/bench_full_pipeline.py --payload-size 1048576
```

Observed results:

```text
Full test suite:        104 passed in 1.13s
Regression suite:       9 passed in 0.05s
FullPipeline smoke:     OK
FullPipeline benchmark: OK
```

---

## FullPipeline benchmark

Command:

```bash
python3 bench/bench_full_pipeline.py --payload-size 1048576
```

Observed output:

```text
FullPipeline benchmark
----------------------
payload size:       1048576 bytes
fragment size:      1024 bytes
fragment count:     1024
route count:        1
bridge packets:     1024
blocked reports:    0
elapsed:            0.771 s
throughput MB/sec:  1.297
final state:        5308c0f032ff45d4
```

Summary:

| Metric | Result |
|---|---:|
| Payload size | 1,048,576 bytes |
| Fragment size | 1,024 bytes |
| Fragment count | 1,024 |
| Route count | 1 |
| Bridge packets | 1,024 |
| Blocked reports | 0 |
| Elapsed time | 0.771 s |
| Throughput | 1.297 MB/s |

Interpretation:

```text
The full local MVP pipeline can process a 1 MiB payload into 1024 fragments,
produce bridge packets, update MCE state, run Lemonade scans, and store Vault
metadata without functional errors.
```

Non-interpretation:

```text
This does not prove transport security, network resilience, anonymity, or
metadata confidentiality.
```

---

## FullPipeline smoke test

Command:

```bash
python3 full_pipeline_v01.py
```

Observed output:

```text
=== FullPipeline v0.1 Smoke Test ===
pipeline: Loader -> Dome -> BAL -> MCEHardened -> Lemonade -> ReticulumBridge -> Vault
input_size: 5400
fragment_size: 256
fragment_count: 22
route_count: 1
lane_count: 1
lane_loads: [22]
bridge_packets: 22
vault_entries: 22
blocked_reports: 0
max_threat_level: 0
final_mce_counter: 22
final_mce_state_hex: 1c6149d6b43d5ade
dome_rejection_rate: 0.0
persisted: True
elapsed_seconds: 0.012553
```

Coherence checks:

```text
fragment_count == bridge_packets == vault_entries == final_mce_counter
22 == 22 == 22 == 22
```

---

## Regression benchmark

Command:

```bash
pytest -q tests/test_regression_v043.py
```

Observed output:

```text
9 passed in 0.05s
```

Regression suite covers:

```text
RotorMachine deterministic roundtrip
MCEHardened deterministic state sequence
Loader deterministic decisions
Dome envelope roundtrip
Lemonade stateless scan semantics
VoxMesh deterministic mutation
ReticulumBridge packet roundtrip
VaultDisk save/load roundtrip
FullPipeline stable summary shape
```

---

## Component benchmarks

The following values were observed during MVP development on the local machine.

They should be treated as indicative smoke results, not portable performance guarantees.

### MCEHardened

Command:

```bash
python3 bench/bench_mce_hardened.py --fragments 1000
```

Observed output:

```text
fragments:             1000
payload size:          256 bytes
plain total:           0.507 s
hardened total:        0.508 s
overhead:              0.14%
plain mean ms/op:      0.5073
hardened mean ms/op:   0.5080
hardened p95 ms/op:    0.5380
target overhead:       < 10%
```

Result:

```text
PASS
```

Interpretation:

```text
State validation and coherence checking add negligible overhead in this local benchmark.
```

---

### Loader

Command:

```bash
python3 bench/bench_loader.py --payloads 1000
```

Observed output:

```text
payloads:        1000
total time:      0.001325 s
decisions/sec:   754800.72
mean ms/op:      0.001262
median ms/op:    0.001215
p95 ms/op:       0.001312
target:          < 1 ms per decision
```

Result:

```text
PASS
```

Interpretation:

```text
Loader rule-based decisions are effectively negligible compared to the rest of the MVP pipeline.
```

---

### BAL

Command:

```bash
python3 bench/bench_bal.py --fragments 10000 --routes 3
```

Observed output:

```text
fragments:              10000
routes:                 3
rounds:                 10
direct indexed median:  0.000348 s
BAL median:             0.003575 s
overhead vs indexed:    927.72%
BAL ms/fragment:        0.000357
lane loads:             [3334, 3333, 3333]
target:                 report overhead; absolute target < 0.01 ms/fragment
absolute pass:          True
```

Result:

```text
PASS on absolute target
```

Interpretation:

```text
The relative overhead is high because the indexed direct baseline is extremely small.
The meaningful MVP metric is absolute cost per fragment: 0.000357 ms/fragment.
```

---

### Dome

Command:

```bash
python3 bench/bench_dome.py --fragments 10000 --rejection-rate 0.05
```

Observed output:

```text
fragments:        10000
payload size:     256 bytes
accepted:         9472
rejected:         528
requested reject: 0.0500
tracked reject:   0.0528
total time:       0.017 s
mean ms/op:       0.001261
p95 ms/op:        0.001384
target:           < 1 ms per wrap/unwrap
```

Result:

```text
PASS
```

Interpretation:

```text
Dome wrapping, unwrapping, and simple filtering are below 1 ms/op by a wide margin.
```

---

### VoxMesh

Command:

```bash
python3 bench/bench_voxmesh.py --mutations 1000
```

Observed output:

```text
mutations:        1000
fractals:         36
total time:       0.024 s
mean ms/cycle:    0.023414
p95 ms/cycle:     0.024683
divergence:       1.000
coherent:         True
target:           < 5 ms per full mutation cycle
```

Result:

```text
PASS
```

Important limitation:

```text
The current VoxMesh divergence score is maximal from initialization because each
fractal is initialized with its fractal_id. This measures state uniqueness, not
adversarial topology resilience.
```

---

### Lemonade

Command:

```bash
python3 bench/bench_lemonade.py --fragments 10000 --bad-rate 0.05
```

Observed output:

```text
fragments:        10000
payload size:     256 bytes
bad rate:         0.0500
blocked reports:  528
global threat:    0
global signals:   []
total time:       0.189 s
mean ms/op:       0.018292
p95 ms/op:        0.031410
target:           < 1 ms per stateless scan
```

Result:

```text
PASS
```

Interpretation:

```text
Stateless Lemonade scanning correctly blocks approximately the generated bad-rate
and does not poison global threat state during benchmark runs.
```

---

## Summary table

| Component | Metric | Result | Target | Status |
|---|---:|---:|---:|---|
| MCEHardened | overhead | 0.14% | < 10% | PASS |
| Loader | mean decision time | 0.001262 ms/op | < 1 ms/op | PASS |
| BAL | absolute lane cost | 0.000357 ms/fragment | < 0.01 ms/fragment | PASS |
| Dome | mean wrap/unwrap | 0.001261 ms/op | < 1 ms/op | PASS |
| VoxMesh | mean mutation cycle | 0.023414 ms/cycle | < 5 ms/cycle | PASS |
| Lemonade | mean stateless scan | 0.018292 ms/op | < 1 ms/op | PASS |
| FullPipeline | throughput | 1.297 MB/s | smoke benchmark | PASS |
| Regression | deterministic suite | 9 passed | all pass | PASS |
| Full tests | full suite | 104 passed | all pass | PASS |

---

## Known benchmark limitations

These benchmarks are limited because:

```text
execution is local only
no real network is involved
ReticulumBridge is an encapsulation skeleton only
BAL lanes are in-memory, not independent network paths
VaultDisk writes JSON metadata, not encrypted storage
Lemonade detectors are simple deterministic rules
VoxMesh divergence currently measures state uniqueness
no adversarial topology is simulated
no baseline comparison is implemented yet
```

Therefore, benchmark results should be used only to assess MVP execution cost and integration stability.

They should not be used to claim security, anonymity, or resilience.

---

## Required next benchmarks

Phase 2 should add benchmarks for:

```text
topology simulator runtime
path diversity under graph models
fragment reconstruction probability
route overlap under compromise
latency under degradation
bandwidth overhead
Sybil-style pseudo-diversity collapse
baseline comparisons
```

Required baseline comparisons:

```text
direct single-path transport
basic multipath routing
Tor-style circuit abstraction
I2P-style tunnel abstraction
mixnet-style batching/delay abstraction
classic OT segmentation
```

---

## Reproducibility notes

Before public review, the repository should include:

```text
requirements.txt
flake.nix or devshell.nix
Python version notes
OS/kernel notes
benchmark command script
machine metadata capture
```

Recommended release validation command:

```bash
pytest -q
pytest -q tests/test_regression_v043.py
python3 full_pipeline_v01.py
python3 bench/bench_full_pipeline.py --payload-size 1048576
```

---

## Correct interpretation

Correct:

```text
WHISPER Remote Nerve v0.4.3 is a tested Python MVP framework with documented
functional benchmarks and regression coverage.
```

Incorrect:

```text
WHISPER Remote Nerve v0.4.3 is a secure, anonymous, or metadata-protecting
communication protocol.
```
