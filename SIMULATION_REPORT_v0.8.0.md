# WHISPER Remote Nerve — Simulation Report v0.8.0

## Status

Preliminary state-to-path diagnostic report.

This report extends v0.7.4 by adding diagnostic state-to-path correlation and lane-collapse metrics.

These results are preliminary and do not support security, anonymity, metadata-protection, or resilience claims yet.

## Objective

v0.8.0 answers one narrow question:

Does simulated WHISPER state material correlate with observed path diversity in the current simulator?

## Scope

v0.8.0 includes:

- deterministic state_material generation
- normalized state distance
- edge-based path distance
- state_to_path_correlation
- lane_collapse_rate
- doubled route_count for diagnostics
- state_mapping_report.csv
- state_mapping_report.json

## Non-goals

v0.8.0 does not include:

- state-driven path selection
- MCE/VoxMesh-driven routing
- targeted adversary
- active adversary behavior
- latency model
- packet loss model
- libp2p PoC
- security claim

## Diagnostic method

The experiment default route_count is 3.

For the v0.8.0 state-mapping diagnostic, route_count is doubled to 6.

This increases pairwise comparisons from:

    3 paths -> 3 pairwise comparisons

to:

    6 paths -> 15 pairwise comparisons

This reduces, but does not eliminate, instability in correlation estimates.

## Metrics

v0.8.0 reports:

- state_to_path_correlation
- lane_collapse_rate
- pairwise state_distance
- pairwise path_distance

Definitions:

- state_distance: normalized Hamming distance between deterministic state hex strings.
- path_distance: edge-based path distance between two paths.
- state_to_path_correlation: Pearson correlation between pairwise state distances and pairwise path distances.
- lane_collapse_rate: fraction of path pairs whose path_distance is below the collapse threshold.

## Results

Detailed results in:

- outputs/state_mapping_report.csv
- outputs/state_mapping_report.json

## Summary table

| Seed | Original Route Count | Analysis Route Count | Path Count | Pairwise Count | State-to-Path Correlation | Lane Collapse Rate |
|---|---:|---:|---:|---:|---:|---:|
| run-001 | 3 | 6 | 6 | 15 | 0.3198 | 0.00 |
| run-002 | 3 | 6 | 6 | 15 | 0.0270 | 0.00 |
| run-003 | 3 | 6 | 6 | 15 | -0.1400 | 0.00 |

## Observed results

The first state-to-path diagnostic produced unstable correlation results.

In run-001:

- state_to_path_correlation = 0.3198
- lane_collapse_rate = 0.0
- interpretation: weak-to-moderate positive diagnostic signal

In run-002:

- state_to_path_correlation = 0.0270
- lane_collapse_rate = 0.0
- interpretation: near-zero diagnostic signal

In run-003:

- state_to_path_correlation = -0.1400
- lane_collapse_rate = 0.0
- interpretation: weak negative diagnostic signal

## Preliminary interpretation

v0.8.0 does not show stable state-to-path correlation.

This is expected because state_material does not yet influence path selection.

The current result should be interpreted as diagnostic only.

It shows that the simulator can now measure whether state diversity maps to path diversity, but the current WHISPER policy does not yet implement state-aware path selection.

Lane collapse was not observed under the current edge-distance threshold in these three runs.

This does not prove resilience.

It only indicates that, under the current threshold and seeds, the sampled paths were not near-identical.

## Key finding

The key v0.8.0 finding is:

    State material exists, and state/path correlation can now be measured,
    but current path selection is not state-driven.

Therefore, WHISPER still needs a state-aware path selection mechanism before any claim about state-driven structural divergence can be evaluated.

## Limitations

The current comparison is limited because:

- only three seeds are reported
- only one topology configuration is reported
- route_count is doubled only for diagnostics
- state_material does not influence path selection
- no targeted compromise is modeled
- no active adversary behavior is modeled
- no statistical significance is claimed
- no real network behavior is modeled

## Next step

v0.8.1 or v0.9.0 should add:

- state-aware path scoring
- state_material-influenced path selection
- comparison against random_multipath under the same adversary model
- lane-collapse behavior under multiple route counts
- targeted high-degree compromise

## Conclusion

v0.8.0 adds the first state-to-path and lane-collapse diagnostics.

The result is inconclusive and does not demonstrate WHISPER superiority.

It establishes the next required mechanism: state-aware path selection.
