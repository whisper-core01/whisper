# SECURITY.md

## Security policy

WHISPER Remote Nerve is currently an experimental MVP framework.

It is not a secure communication protocol.

The current implementation must not be used to protect real sensitive communications.

---

## Supported versions

| Version | Status |
|---|---|
| v0.4.3 | Current MVP baseline |
| < v0.4.3 | Historical / unsupported |

---

## Current security status

The project currently provides:

```text
functional tests
integration tests
regression tests
basic input validation
simple anomaly detection
metadata persistence tests
explicit threat model
```

The project does not currently provide:

```text
confidentiality
integrity
authentication
anonymous routing
metadata protection
traffic analysis resistance
secure transport
secure storage
tamper resistance
forward secrecy
secure deletion
production hardening
```

---

## Vulnerability reporting

Until a dedicated security contact exists, report issues through the public issue tracker using the prefix:

```text
[security]
```

Example:

```text
[security] VaultDisk accepts malformed metadata under condition X
```

Do not include real secrets, private keys, production credentials, or sensitive operational data in public reports.

If private reporting is needed, add contact information here before public release:

```text
Security contact: TODO
PGP key: TODO
```

---

## Scope for reports

Useful reports include:

```text
crashes on malformed input
unexpected state corruption
regression test failures
incorrect deterministic behavior
VaultDisk malformed file handling
ReticulumBridge malformed packet handling
Dome envelope parsing issues
Lemonade detector bypasses
FullPipeline count/coherence mismatches
```

Out of scope for the current MVP:

```text
lack of encryption
lack of anonymity
lack of secure transport
lack of Reticulum integration
lack of formal verification
lack of host compromise resistance
lack of secure deletion
```

These are known non-goals of the current MVP and are documented in `THREAT_MODEL.md`.

---

## Security expectations

Do not deploy this project as:

```text
secure messaging
anonymous transport
production OT security layer
encrypted tunnel
intrusion detection system
key vault
```

Acceptable use:

```text
local testing
research prototype
architecture review
simulation foundation
grant review artifact
```

---

## Required validation before release

Before tagging a release, run:

```bash
pytest -q
pytest -q tests/test_regression_v043.py
python3 full_pipeline_v01.py
python3 bench/bench_full_pipeline.py --payload-size 1048576
```

A release should not be published if:

```text
tests fail
regression tests fail
FullPipeline smoke fails
FullPipeline count coherence breaks
VaultDisk roundtrip fails
ReticulumBridge roundtrip fails
```

---

## Dependency policy

Current MVP aims to minimize dependencies.

Before adding a dependency, document:

```text
why it is needed
whether it is optional
license compatibility
security impact
reproducibility impact
```

---

## Secret handling

The current Python MVP does not provide secure memory handling.

Do not store or process real secrets in the current implementation.

Known limitations:

```text
Python memory is not securely zeroized
seeds may remain in memory
VaultDisk is cleartext JSON
logs may expose metadata
benchmark outputs may expose metadata
```

Future work may evaluate Rust/WASM/native components for memory hardening.

---

## Disclosure posture

This project uses explicit security boundaries.

Known limitations should be documented rather than hidden.

The correct security posture is:

```text
tested MVP framework, not secure protocol
```

The incorrect posture is:

```text
production-ready secure communication system
```
