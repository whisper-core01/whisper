# WHISPER Remote Nerve — Simulation Report v0.7.0

## Status

Preliminary baseline comparison report.

This report extends v0.6.0 by adding a minimal single-path baseline.

These results are preliminary and do not support security, anonymity, metadata-protection, or resilience claims yet.

## Objective

v0.7.0 answers one narrow question:

Does WHISPER candidate-path sampling produce more path diversity than a minimal single-path baseline in the current simulator?

## Scope

v0.7.0 includes:

- WHISPER candidate-path policy
- single-path baseline
- three reproducible seeds
- baseline_comparison.csv
- baseline_comparison.json

## Non-goals

v0.7.0 does not include:

- adversary model
- state-to-path mapping
- lane collapse metrics
- random multipath baseline
- fixed-circuit baseline
- NAT model
- latency model
- packet loss model
- libp2p PoC
- security claim

## Baseline definition

The single-path baseline reuses the same shortest path for all routes.

It is intentionally minimal.

It is not Tor, not I2P, not a mixnet, and not libp2p.

Its purpose is to avoid comparing WHISPER to nothing.

## Reproduction

Run:

    python3 baseline_v01.py

Outputs:

    outputs/baseline_comparison.csv
    outputs/baseline_comparison.json

Run tests:

    pytest -q tests/test_baseline_v01.py
    pytest -q tests

## Results

| Seed | Policy | Path count | Unique path ratio | Path overlap |
|---|---|---:|---:|---:|
| run-001 | whisper_candidate_paths | 3 | 1.0000 | 0.1984 |
| run-001 | single_path | 3 | 0.3333 | 1.0000 |
| run-002 | whisper_candidate_paths | 3 | 1.0000 | 0.2000 |
| run-002 | single_path | 3 | 0.3333 | 1.0000 |
| run-003 | whisper_candidate_paths | 3 | 1.0000 | 0.1414 |
| run-003 | single_path | 3 | 0.3333 | 1.0000 |

## Preliminary interpretation

In these three preliminary runs, WHISPER candidate-path sampling produced three unique candidate paths for each seed.

The single-path baseline reused the same path three times.

As expected, the single-path baseline produced:

- lower unique_path_ratio
- maximal path_overlap

WHISPER candidate-path sampling produced:

- unique_path_ratio = 1.0
- lower path_overlap than the single-path baseline

This is a useful preliminary sanity check.

It does not prove network resilience.

## Limitations

The current comparison is limited because:

- only one baseline is implemented
- only three seeds are reported
- no adversary is modeled
- no state-to-path mapping is modeled
- no lane collapse is measured
- no latency or bandwidth overhead is measured
- no statistical significance is claimed
- the single-path baseline is intentionally simple

## Next steps

v0.7.1 should add:

- random multipath baseline
- repeated pilot runs
- baseline summary statistics
- optional schema validation for baseline_comparison.json

v0.8.x should add:

- state-to-path mapping
- adversary models
- lane collapse metrics
- richer simulation report

## Conclusion

v0.7.0 provides the first baseline comparison.

It shows that WHISPER candidate-path sampling produces more path diversity than a minimal single-path baseline in the current simulator.

It does not support security or resilience claims yet.
