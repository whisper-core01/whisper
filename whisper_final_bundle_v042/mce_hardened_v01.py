# mce_hardened_v01.py
# Requires Python 3.8+

"""
MCEHardened v0.1.1 — State validation and coherence checks for MCE.

Purpose:
    Add lightweight validation around MCE state evolution.

Scope:
    - validate state shape;
    - detect obvious counter/state inconsistencies;
    - provide checked digest wrapper;
    - keep overhead low.

Security warning:
    This is NOT a formal verification layer.
    This is NOT cryptographic state compromise recovery.
    This is NOT tamper-proof runtime protection.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from mce_v01 import MCE, MCEState


__version__ = "0.1.1"
__all__ = ["MCEHardened"]


class MCEHardened(MCE):
    """MCE with state validation and coherence checks."""

    def validate_state(self) -> bool:
        """
        Validate current MCE runtime state.

        Checks:
            - state is bytes;
            - state hash is 32 bytes;
            - fragment_counter is int;
            - fragment_counter >= 0.
        """
        if not isinstance(getattr(self, "state", None), bytes):
            return False

        if len(self.state) != 32:
            return False

        if not isinstance(getattr(self, "fragment_counter", None), int):
            return False

        if self.fragment_counter < 0:
            return False

        return True

    def coherence_check(self) -> Dict[str, object]:
        """
        Return a structured coherence report.

        Returns:
            {
                "valid": bool,
                "issues": [str]
            }
        """
        issues: List[str] = []

        state = getattr(self, "state", None)
        fragment_counter = getattr(self, "fragment_counter", None)
        initial_seed = getattr(self, "initial_seed", None)
        rotors = getattr(self, "rotors", None)

        if not isinstance(state, bytes):
            issues.append("state is not bytes")
        elif len(state) != 32:
            issues.append("state hash length is not 32 bytes")

        if not isinstance(fragment_counter, int):
            issues.append("fragment_counter is not int")
        elif fragment_counter < 0:
            issues.append("fragment_counter is negative")

        if not isinstance(initial_seed, bytes):
            issues.append("initial_seed is not bytes")

        if not isinstance(rotors, int):
            issues.append("rotors is not int")
        elif rotors <= 0:
            issues.append("rotors must be positive")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }

    def digest_fragment_checked(self, fragment: bytes) -> Tuple[bytes, MCEState, Dict[str, object]]:
        """
        Transform one fragment with post-digest validation.

        Returns:
            (transformed, state_snapshot, validation_result)

        Raises:
            RuntimeError:
                If pre-digest state is invalid.
            TypeError:
                If fragment is not bytes.
        """
        before = self.coherence_check()
        if not before["valid"]:
            raise RuntimeError(f"MCE state invalid before digest: {before['issues']}")

        transformed = self.digest_fragment(fragment)
        snapshot = self.snapshot()
        after = self.coherence_check()

        return transformed, snapshot, after
