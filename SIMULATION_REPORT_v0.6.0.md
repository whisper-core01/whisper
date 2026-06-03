# WHISPER Remote Nerve — Simulation Report v0.6.0

## Status

Preliminary minimum viable simulator report.

This report documents the first reproducible WHISPER Phase 2 simulation artifacts.

These results are preliminary and do not support security, anonymity, metadata-protection, or resilience claims yet.

## Scope

v0.6.0 implements a minimum viable simulator with:

- Erdős-Rényi topology generation
- Barabási-Albert topology generation
- Watts-Strogatz topology generation
- deterministic source/target selection
- shortest path sampling
- deterministic random simple path sampling
- candidate path generation
- path_overlap metric
- unique_path_ratio metric
- JSON simulation output
- CSV summary output
- simulator benchmark

## Non-goals

v0.6.0 does not include:

- adversary model
- state-to-path mapping
- lane collapse metrics
- baseline comparison
- NAT model
- latency model
- packet loss model
- libp2p PoC
- security claim

## Reproduction

Run:

    python3 simulation_runner_v01.py --config experiments/example.json --seed run-001 --output outputs/run_001.json
    python3 simulation_runner_v01.py --config experiments/example.json --seed run-002 --output outputs/run_002.json
    python3 simulation_runner_v01.py --config experiments/example.json --seed run-003 --output outputs/run_003.json

Then generate summary:

    cat outputs/summary.csv

Run simulator benchmark:

    python3 bench/bench_simulator.py --runs 100

Run tests:

    pytest -q tests

## Test results

Current test status:

    110 passed

Simulator-specific tests:

    6 passed

## Simulator benchmark

Observed benchmark:

| Metric | Value |
|---|---:|
| Runs | 100 |
| Total seconds | 0.031755 |
| Mean ms/run | 0.316955 |
| Median ms/run | 0.296489 |
| P95 ms/run | 0.418983 |
| Runs/sec | 3149.06 |
| Status | fast enough for n=30 pilot |

## Reproducible runs

| Run | Seed | Topology | Nodes | Edges | Path count | Unique path ratio | Path overlap |
|---|---|---|---:|---:|---:|---:|---:|
| run_001 | run-001 | erdos_renyi | 100 | 265 | 3 | 1.000 | 0.2738 |
| run_002 | run-002 | erdos_renyi | 100 | 250 | 3 | 1.000 | 0.1333 |
| run_003 | run-003 | erdos_renyi | 100 | 251 | 3 | 1.000 | 0.1111 |

## Preliminary interpretation

All three runs produced three unique candidate paths.

The observed path_overlap values are low to moderate in these initial Erdős-Rényi runs.

However, these results are not yet sufficient to support claims about WHISPER resilience.

The current simulator does not yet model:

- adversarial compromise
- state-to-path mapping
- lane collapse
- baseline comparison
- realistic decentralized network constraints

Therefore, v0.6.0 should be interpreted only as evidence that the simulator can produce deterministic, machine-readable, reproducible path-diversity metrics.

## Limitations

The current results are limited because:

- only one topology family was used in the three published runs
- no adversary was modeled
- no baseline was compared
- no statistical significance is claimed
- no latency or bandwidth overhead is modeled
- no real network behavior is modeled

## Next step: v0.6.1

v0.6.1 should add:

- adversary_v01.py
- random node compromise
- targeted high-degree compromise
- state_material
- state_distance
- path_distance
- state_to_path_correlation
- lane_collapse_rate
- metrics_report.json

## Conclusion

v0.6.0 successfully creates the first reproducible WHISPER Phase 2 simulation artifacts.

It does not prove WHISPER resilience.

It establishes the minimum empirical foundation required for the next validation stage.
