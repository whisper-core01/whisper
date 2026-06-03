# TODO v0.6.0 — Minimum Viable Simulator

Goal: implement the first deterministic topology simulator that produces a valid simulation_run.json.

## Scope

### topology_v01.py

Required:

- Erdős-Rényi graph
- Barabási-Albert graph
- Watts-Strogatz graph

### path_sampler_v01.py

Required:

- shortest path
- random simple path
- k candidate paths

### metrics_v01.py

Required:

- path_overlap
- unique_path_ratio

### simulation_runner_v01.py

Required:

- load experiments/example.json
- generate topology
- sample paths
- compute metrics
- write outputs/simulation_run.json

### bench/bench_simulator.py

Required:

- mean ms/run
- p95 ms/run
- runs/sec
- warning if mean > 5s/run

## Non-goals

- no adversary model yet
- no state-to-path mapping yet
- no baselines yet
- no NAT model
- no latency model
- no libp2p
- no security claim

## Acceptance criteria

Run:

    python3 simulation_runner_v01.py --config experiments/example.json
    python3 bench/bench_simulator.py --runs 100
    pytest -q tests

Expected artifact:

    outputs/simulation_run.json

## Anti-rabbit-hole rule

If a feature is not required to produce the first simulation_run.json, it goes to v0.6.1+.
