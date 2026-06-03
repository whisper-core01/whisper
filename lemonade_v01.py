# lemonade_v01.py
# Requires Python 3.8+

"""
Lemonade v0.1.1 — Immune system skeleton for Whisper MVP.

Security warning:
    Not an IDS, not an antivirus, not a SIEM, not a formal detector.
    Minimal deterministic anomaly detector skeleton only.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Set


__version__ = "0.1.1"
__all__ = ["Lemonade", "ThreatReport"]


@dataclass(frozen=True)
class ThreatReport:
    threat_level: int
    signals: List[str]
    blocked: bool


class Lemonade:
    """Immune system: detect 7 simple attack/anomaly types."""

    MAX_QUEUE_DEPTH = 1024
    MAX_FRAGMENT_RATE = 5000.0
    MAX_FRAGMENT_SIZE = 10 * 1024 * 1024
    MIN_ENTROPY_BITS_PER_BYTE = 1.5
    BLOCK_THRESHOLD = 7

    BAD_PATTERNS = [
        b"DROP TABLE",
        b"<script",
        b"../",
        b"\x00" * 1001,
        b"WHISPER_POISON",
    ]

    def __init__(self):
        self.threat_level = 0
        self.signals: List[str] = []
        self.seen_fragment_ids: Set[int] = set()
        self.scan_count = 0

    def reset(self) -> None:
        self.threat_level = 0
        self.signals.clear()
        self.seen_fragment_ids.clear()
        self.scan_count = 0

    def detect_overflow(self, queue_depth: int) -> bool:
        if not isinstance(queue_depth, int):
            raise TypeError("queue_depth must be an int")
        if queue_depth < 0:
            raise ValueError("queue_depth must be >= 0")
        detected = queue_depth > self.MAX_QUEUE_DEPTH
        if detected:
            self._raise("overflow", 2)
        return detected

    def detect_spam(self, fragment_rate: float) -> bool:
        if not isinstance(fragment_rate, (int, float)):
            raise TypeError("fragment_rate must be numeric")
        if fragment_rate < 0:
            raise ValueError("fragment_rate must be >= 0")
        detected = float(fragment_rate) > self.MAX_FRAGMENT_RATE
        if detected:
            self._raise("spam", 2)
        return detected

    def detect_poison(self, fragment: bytes) -> bool:
        fragment = self._ensure_bytes(fragment)
        detected = any(pattern in fragment for pattern in self.BAD_PATTERNS)
        if detected:
            self._raise("poison", 3)
        return detected

    def detect_oversize(self, fragment: bytes) -> bool:
        fragment = self._ensure_bytes(fragment)
        detected = len(fragment) > self.MAX_FRAGMENT_SIZE
        if detected:
            self._raise("oversize", 2)
        return detected

    def detect_replay(self, fragment_id: int) -> bool:
        if not isinstance(fragment_id, int):
            raise TypeError("fragment_id must be an int")
        if fragment_id < 0:
            raise ValueError("fragment_id must be >= 0")
        detected = fragment_id in self.seen_fragment_ids
        self.seen_fragment_ids.add(fragment_id)
        if detected:
            self._raise("replay", 2)
        return detected

    def detect_entropy_drop(self, fragment: bytes) -> bool:
        fragment = self._ensure_bytes(fragment)
        if not fragment:
            return False
        entropy = self._shannon_entropy_bits_per_byte(fragment)
        detected = entropy < self.MIN_ENTROPY_BITS_PER_BYTE
        if detected:
            self._raise("entropy_drop", 1)
        return detected

    def detect_state_anomaly(self, validation_report: Dict[str, object]) -> bool:
        if not isinstance(validation_report, dict):
            raise TypeError("validation_report must be a dict")
        detected = validation_report.get("valid") is not True
        if detected:
            self._raise("state_anomaly", 3)
        return detected

    def scan_fragment(
        self,
        fragment: bytes,
        fragment_id: int,
        queue_depth: int = 0,
        fragment_rate: float = 0.0,
        validation_report: Optional[Dict[str, object]] = None,
    ) -> ThreatReport:
        self.scan_count += 1
        self.detect_overflow(queue_depth)
        self.detect_spam(fragment_rate)
        self.detect_oversize(fragment)
        self.detect_poison(fragment)
        self.detect_entropy_drop(fragment)
        self.detect_replay(fragment_id)
        if validation_report is not None:
            self.detect_state_anomaly(validation_report)
        return self.report()

    def scan_fragment_stateless(
        self,
        fragment: bytes,
        fragment_id: int,
        queue_depth: int = 0,
        fragment_rate: float = 0.0,
        validation_report: Optional[Dict[str, object]] = None,
    ) -> ThreatReport:
        """
        Run detectors for a single fragment without permanently accumulating
        threat level/signals.

        Replay memory is still preserved, because replay detection is inherently
        stateful. Threat score and signals are restored after the scan.
        """
        previous_level = self.threat_level
        previous_signals = list(self.signals)

        self.threat_level = 0
        self.signals = []

        report = self.scan_fragment(
            fragment=fragment,
            fragment_id=fragment_id,
            queue_depth=queue_depth,
            fragment_rate=fragment_rate,
            validation_report=validation_report,
        )

        self.threat_level = previous_level
        self.signals = previous_signals

        return report

    def get_threat_level(self) -> int:
        return self.threat_level

    def report(self) -> ThreatReport:
        return ThreatReport(
            threat_level=self.threat_level,
            signals=list(self.signals),
            blocked=self.threat_level >= self.BLOCK_THRESHOLD,
        )

    def _raise(self, signal: str, amount: int) -> None:
        if signal not in self.signals:
            self.signals.append(signal)
        self.threat_level = min(10, self.threat_level + amount)

    @staticmethod
    def _ensure_bytes(fragment: bytes) -> bytes:
        if not isinstance(fragment, (bytes, bytearray)):
            raise TypeError("fragment must be bytes")
        return bytes(fragment)

    @staticmethod
    def _shannon_entropy_bits_per_byte(data: bytes) -> float:
        counts = {}
        for byte in data:
            counts[byte] = counts.get(byte, 0) + 1
        total = len(data)
        entropy = 0.0
        for count in counts.values():
            p = count / total
            entropy -= p * math.log2(p)
        return entropy


if __name__ == "__main__":
    lemonade = Lemonade()
    print("=== Lemonade v0.1 Smoke Test ===")
    clean = lemonade.scan_fragment(
        fragment=b"normal fragment payload",
        fragment_id=0,
        queue_depth=10,
        fragment_rate=100.0,
        validation_report={"valid": True, "issues": []},
    )
    print(f"clean report:   {clean}")
    bad = lemonade.scan_fragment(
        fragment=b"WHISPER_POISON" + (b"\x00" * 1001),
        fragment_id=0,
        queue_depth=2048,
        fragment_rate=10000.0,
        validation_report={"valid": False, "issues": ["demo"]},
    )
    print(f"bad report:     {bad}")
