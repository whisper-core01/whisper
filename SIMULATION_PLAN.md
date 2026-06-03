# SIMULATION_PLAN.md

## WHISPER Remote Nerve — Topology Simulation Plan

**Target release:** v0.6.x  
**Purpose:** evaluate whether local structural divergence maps to network-level resilience  

---

## 1. Goal

The current MVP validates a local pipeline.

The simulation phase must answer a harder question:

```text
Does WHISPER-style structural divergence produce measurable resilience
under adversarial network topologies?
```

This requires a simulator that can model:

```text
topologies
paths
fragments
lanes
adversaries
compromise
latency
reconstruction
metadata exposure
```

---

## 2. Core simulator modules

Proposed files:

```text
topology_v01.py
adversary_v01.py
simulation_runner_v01.py
metrics_v01.py
baseline_models_v01.py
```

Proposed classes:

```text
TopologyGraph
Node
Edge
Path
PathSampler
AdversaryModel
CompromiseScenario
SimulationRun
MetricsReport
BaselineModel
```

---

## 3. Topology families

Minimum required topologies:

```text
Erdős–Rényi random graph
Barabási–Albert scale-free graph
Watts–Strogatz small-world graph
hub-and-spoke industrial graph
hierarchical OT-style graph
hybrid cloud-edge graph
```

Optional later topologies:

```text
peer-to-peer churn graph
mobile edge graph
partitioned regional graph
small relay network
large relay network
```

---

## 4. Adversary scenarios

Minimum adversary models:

```text
A1 random node compromise
A2 targeted high-degree node compromise
A3 bridge-node compromise
A4 colluding relay group
A5 Sybil-style pseudo-diversity
A6 passive traffic observer
A7 partial network partition
A8 high-churn adversary
```

Each scenario should define:

```text
compromised node count
compromise strategy
observation capability
active capability
collusion capability
duration
```

---

## 5. Metrics

Minimum metrics:

```text
reachability
path overlap
route diversity
fragment reconstruction probability
metadata exposure estimate
latency estimate
bandwidth overhead
degradation frequency
false-positive rate
blocked fragment rate
```

Derived metrics:

```text
mean path overlap
max compromised path share
fragment exposure ratio
route entropy
lane utilization variance
reconstruction threshold
```

---

## 6. Structural divergence mapping

The simulator must explicitly map local MVP concepts to simulated network concepts.

| MVP concept | Simulation concept |
|---|---|
| Loader route_count | number of active candidate paths |
| BAL lane_id | lane-to-path assignment |
| MCE state | path perturbation seed |
| VoxMesh fractal | diversity source / lane policy input |
| Dome rejection | pre-transport filter event |
| Lemonade threat report | degradation signal |
| ReticulumBridge packet | simulated transport packet |
| Vault metadata | experiment trace |

Key question:

```text
Do different local states actually produce different network paths?
```

If not, structural divergence remains local and does not provide network resilience.

---

## 7. Baselines

Minimum baselines:

```text
direct single-path transport
basic random multipath
Tor-style fixed circuit abstraction
I2P-style tunnel abstraction
mixnet-style batching/delay abstraction
classic OT segmentation
```

The baseline models can be simplified. They should be honest abstractions, not full reimplementations.

---

## 8. Experiment format

Each experiment should be reproducible from:

```text
seed
topology type
node count
edge parameters
adversary model
payload size
fragment size
route policy
simulation duration
```

Recommended JSON schema:

```json
{
  "experiment_id": "string",
  "seed": "hex-or-string",
  "topology": {
    "type": "barabasi_albert",
    "nodes": 1000,
    "parameters": {}
  },
  "adversary": {
    "type": "targeted_hub_compromise",
    "compromised_fraction": 0.05
  },
  "payload": {
    "size_bytes": 1048576,
    "fragment_count": 1024
  },
  "metrics": {
    "reachability": 0.0,
    "path_overlap": 0.0,
    "reconstruction_probability": 0.0
  }
}
```

---

## 9. Output artifacts

Required outputs:

```text
simulation_run.json
metrics_report.json
topology_summary.json
baseline_comparison.csv
README for each experiment batch
```

Optional outputs:

```text
plots/*.png
graphs/*.json
ipld/*.json
```

---

## 10. Success criteria

Phase 2 success does not mean proving WHISPER is secure.

Phase 2 success means producing credible evidence.

Success criteria:

```text
simulator runs deterministically from seed
at least 3 topology families implemented
at least 3 adversary models implemented
at least 3 baselines implemented
metrics reports generated as JSON
results documented without overclaiming
```

Strong positive outcome:

```text
WHISPER-style divergence reduces reconstruction probability or path overlap
under specific topologies and adversaries.
```

Strong negative outcome:

```text
WHISPER-style divergence collapses under realistic topology constraints.
```

Both outcomes are useful research results.

---

## 11. Failure criteria

The simulation phase fails if:

```text
local divergence cannot be mapped to topology-level diversity
metrics are not reproducible
baselines are not implemented
results depend on hidden assumptions
Sybil-style pseudo-diversity trivially collapses the model
single-node compromise predicts future routing
```

---

## 12. Timeline

Estimated v0.6.x work:

```text
Week 1: topology graph models
Week 2: path sampler and adversary models
Week 3: metrics and JSON reports
Week 4: baseline models
Week 5: experiment runner and reproducibility checks
Week 6: documentation and first simulation report
```

---

## 13. Relation to grant review

For NLnet:

```text
simulation demonstrates responsible validation before security claims
```

For Protocol Labs:

```text
simulation creates reusable decentralized network research artifacts
```

The same simulator can serve both audiences.
