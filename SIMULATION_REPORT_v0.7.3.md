# WHISPER Remote Nerve — Simulation Report v0.7.3

## Status

Preliminary adversarial exposure report.

This report extends v0.7.2 by adding a minimal random node compromise model.

These results are preliminary and do not support security, anonymity, metadata-protection, or resilience claims yet.

## Objective

v0.7.3 answers one narrow question:

Does observed path diversity remain meaningful under random node compromise?

## Scope

v0.7.3 includes:

- random node compromise
- WHISPER candidate-path policy
- single-path baseline
- naive random multipath baseline
- adversarial exposure metrics
- three reproducible seeds
- adversary_comparison.csv
- adversary_comparison.json

## Non-goals

v0.7.3 does not include:

- targeted adversary
- active adversary behavior
- state-to-path mapping
- lane collapse metrics
- latency model
- packet loss model
- libp2p PoC
- security claim

## Adversary model

The adversary compromises a deterministic random subset of nodes.

For the published v0.7.3 runs:

- compromise fraction: 20%
- compromise type: random node compromise
- active behavior: none
- collusion: not modeled
- packet dropping: not modeled
- path manipulation: not modeled

## Metrics

v0.7.3 reports:

- path_compromise_rate
- clean_path_ratio
- fully_compromised_path_rate
- mean_compromised_nodes_per_path

Definitions:

- path_compromise_rate: fraction of paths touching at least one compromised node.
- clean_path_ratio: fraction of paths touching no compromised node.
- fully_compromised_path_rate: fraction of paths where all nodes are compromised.
- mean_compromised_nodes_per_path: average number of compromised nodes per path.

## Results

Detailed results in:

- `outputs/adversary_comparison.csv` — CSV summary table
- `outputs/adversary_comparison.json` — full JSON results with compromised node lists

Summary table below.

## Summary table

| Seed | Policy | Path Count | Clean Path Ratio | Mean Compromised Nodes/Path |
|---|---|---:|---:|---:|
| run-001 | WHISPER | 3 | 0.00 | 3.67 |
| run-001 | single-path | 3 | 0.00 | 1.00 |
| run-001 | random-multipath | 3 | 0.00 | 4.33 |
| run-002 | WHISPER | 3 | 0.33 | 3.00 |
| run-002 | single-path | 3 | 1.00 | 0.00 |
| run-002 | random-multipath | 3 | 1.00 | 0.00 |
| run-003 | WHISPER | 3 | 0.00 | 1.00 |
| run-003 | single-path | 3 | 0.00 | 1.00 |
| run-003 | random-multipath | 3 | 0.00 | 2.00 |

## Observed results

The first random-compromise experiment produced mixed results.

In run-001:

- all policies had clean_path_ratio = 0.0
- WHISPER touched fewer compromised nodes per path than random_multipath
- single_path touched fewer compromised nodes per path than both

In run-002:

- WHISPER clean_path_ratio = 0.3333
- single_path clean_path_ratio = 1.0
- random_multipath clean_path_ratio = 1.0
- WHISPER performed worse than both baselines under this compromise sample

In run-003:

- all policies had clean_path_ratio = 0.0
- WHISPER matched single_path on mean compromised nodes per path
- WHISPER performed better than random_multipath on mean compromised nodes per path

## Preliminary interpretation

v0.7.3 does not show that WHISPER is more robust than the baselines under random node compromise.

The result is mixed.

This is an important finding.

It shows that path diversity alone is not sufficient to claim adversarial robustness.

It also shows that lower path overlap does not necessarily imply lower adversarial exposure.

The next required step is to introduce state-to-path mapping and lane-collapse metrics.

## Limitations

The current comparison is limited because:

- only random compromise is modeled
- only three seeds are reported
- no targeted compromise is modeled
- no active adversary behavior is modeled
- no state-to-path mapping is implemented
- no lane collapse metric is implemented
- no statistical significance is claimed
- no real network behavior is modeled

## Next step

v0.8.0 should add:

- state_material
- state_distance
- path_distance
- state_to_path_correlation
- lane_collapse_rate
- targeted high-degree compromise

## Conclusion

v0.7.3 adds the first adversarial exposure metric.

The result is mixed and does not demonstrate WHISPER superiority.

It establishes that the simulator can now falsify weak claims and identify the next missing mechanism: state-aware routing and lane-collapse analysis.
