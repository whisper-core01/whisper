# WHISPER Remote Nerve — Funding Readiness Overview

## Status

WHISPER Remote Nerve is now a reproducible research artifact suitable for Phase 2 funding review.

It is not a production protocol.
It is not a secure communication system.
It does not claim anonymity, metadata protection, or resilience.

Current status:

- Phase 1 MVP: complete
- Reproducibility pack: complete
- Minimum simulator: complete
- Baseline comparison: complete
- Random compromise exposure metrics: complete
- State-to-path diagnostics: complete
- Security/resilience claims: not supported

## Why WHISPER is Funding-Ready

WHISPER has moved from a documented MVP to a measurable, falsifiable research artifact.

The repository now includes:

- tested local MVP pipeline
- reproducibility scripts
- machine-readable schemas
- reproducible simulation outputs
- baseline comparisons
- adversarial exposure metrics
- state-to-path diagnostics
- explicit limitations
- no unsupported security claims

WHISPER is not asking funders to accept a finished protocol.
It is asking funders to support a falsifiable research program.

## Release Ladder

| Version | Meaning |
|---|---|
| v0.4.4 | Reviewer-ready MVP |
| v0.5.0 | Reproducibility pack |
| v0.6.0 | Minimum viable simulator |
| v0.6.1 | Initial simulation report |
| v0.6.2 | Reproducible artifact bundle with hashes |
| v0.7.0 | Single-path baseline comparison |
| v0.7.1 | Baseline report |
| v0.7.2 | Naive random multipath baseline |
| v0.7.3 | Random node compromise exposure metrics |
| v0.7.4 | Test/report cleanup |
| v0.8.0 | State-to-path and lane-collapse diagnostics |

## Test Status

Current test suite:

```text
125 passed

Coverage includes:

core MVP pipeline
regression suite
simulator topology generation
path sampling
baseline comparison
adversarial exposure metrics
state-to-path diagnostics
Reproducibility Status

The repository provides:

scripts/run_all_tests.sh
scripts/run_all_benchmarks.sh
scripts/run_simulation.sh
scripts/validate_artifacts.sh

And includes:

schemas/
experiments/example.json
outputs/*.json
outputs/*.csv
artifact_bundle/v0.6.2/
SHA256SUMS.txt

Reviewers can fully reproduce the current simulation artifacts.

Protocol Labs Relevance

WHISPER is relevant to Protocol Labs as a decentralized-network research artifact.

PL-relevant outputs include:

machine-readable simulation outputs
JSON schemas
baseline comparison outputs
reproducible artifact bundle
random compromise exposure metrics
state-to-path diagnostic metrics
explicit acknowledgment of negative/mixed results

Current research question:

Can structural-divergence policies improve path diversity and adversarial exposure outcomes in decentralized-network simulations?

Current answer:

Not proven yet. Results are mixed and diagnostic.

This is exactly why the project is fundable as research.

NLnet Relevance

WHISPER is relevant to NLnet as an open, reproducible, public-interest security research project.

NLnet-relevant outputs include:

explicit threat model
security boundaries
reproducible tests
open research artifacts
no overclaiming
documented limitations
negative and mixed results preserved
clear next validation steps

WHISPER is suitable for funding as a Phase 2 validation and simulation project.

Current Empirical Findings
v0.6.x — Minimum Simulator
reproducible path-diversity metrics
deterministic JSON outputs
no resilience claims
v0.7.x — Baselines & Random Compromise

Compared against:

single-path baseline
naive random multipath baseline

Findings:

random multipath sometimes matches or outperforms WHISPER
under random 20% compromise, results are mixed
path diversity alone does not imply adversarial robustness
v0.8.0 — State-to-Path Diagnostics

Added:

state_material
state_distance
path_distance
state_to_path_correlation
lane_collapse_rate

Route count doubled from 3 to 6 for diagnostics.

Results:

Seed	Correlation	Collapse
run-001	0.3198	0.00
run-002	0.0270	0.00
run-003	-0.1400	0.00

Interpretation:

correlation unstable
state does not influence path selection yet
no lane collapse under current threshold
What WHISPER Does Not Claim

WHISPER does not claim:

security
anonymity
metadata protection
resistance to global passive adversaries
resistance to targeted compromise
superiority over Tor/I2P/mixnets/libp2p
production readiness
cryptographic safety
real network scalability
Why Mixed Results Are Valuable

WHISPER has already produced negative and mixed findings, which is scientifically useful:

WHISPER does not consistently outperform naive random multipath
WHISPER can perform worse under some compromise samples
state-to-path correlation is unstable

This shows the simulator can falsify weak claims, which strengthens the research posture.

Remaining Gaps

The next mechanisms needed:

state-aware path selection
targeted high-degree compromise
lane-collapse analysis across more topologies
repeated runs with confidence intervals
random multipath comparison under adversarial conditions
topology diversity beyond ER
churn, NAT, latency, packet loss models
optional libp2p/IPFS/IPLD integration
Next Funded Milestone: v0.8.1 / v0.9.0

Minimum scope:

make state_material influence path selection
compare against random_multipath under same compromise model
measure lane_collapse_rate across multiple route counts
add targeted high-degree compromise
run n=30 pilot runs per condition
publish JSON/CSV outputs
report all negative results
Funding Justification

Funding is justified because WHISPER now has:

working code
reproducible outputs
machine-readable artifacts
tests
baselines
adversarial metrics
state diagnostics
explicit non-claims
clear next experiments

Funding is not for inventing the project.
Funding is for running the next falsifiable experiments.

Reviewer Summary

WHISPER is funding-ready because it has crossed the minimum empirical threshold:

MVP + reproducibility + simulator + baselines + adversarial metrics + state diagnostics

The results are mixed and inconclusive — and that is acceptable.

The project is now strong enough to be:

reviewed
challenged
reproduced
funded

for deeper validation.
