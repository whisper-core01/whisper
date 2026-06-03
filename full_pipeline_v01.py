# full_pipeline_v01.py
# Requires Python 3.8+

"""
FullPipeline v0.1.0 — Final MVP integration pipeline.

Flow:
    payload
      -> Loader decides fragment size and route count
      -> fragment_payload()
      -> Dome wrap/filter
      -> BAL distribute/collect
      -> MCEHardened digest checked
      -> Lemonade stateless scan
      -> ReticulumBridge encapsulation
      -> Vault metadata storage
      -> optional VaultDisk persistence
      -> summary report

Security warning:
    This is NOT a production Whisper pipeline.
    This is NOT encrypted transport.
    This is a final MVP integration test harness.
"""

from __future__ import annotations

import tempfile
import time
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional

from bal_v01 import BAL
from dome_v01 import Dome
from lemonade_v01 import Lemonade
from loader_v01 import Loader
from mce_hardened_v01 import MCEHardened
from pipeline_demo import fragment_payload
from reticulum_bridge_v01 import ReticulumBridge
from vault_disk_v01 import VaultDisk
from vault_v01 import Vault


__version__ = "0.1.0"
__all__ = ["FullPipeline"]


class FullPipeline:
    """Final MVP end-to-end integration pipeline."""

    def __init__(self, seed: bytes, persist_path: Optional[Path] = None):
        if not isinstance(seed, (bytes, bytearray)):
            raise TypeError("seed must be bytes")

        self.seed = bytes(seed)
        self.mce = MCEHardened(self.seed)
        self.loader = Loader(self.mce)
        self.dome = Dome()
        self.lemonade = Lemonade()
        self.vault = Vault()
        self.bridge = ReticulumBridge()
        self.persist_path = Path(persist_path) if persist_path is not None else None

    def process(self, payload: bytes) -> Dict[str, object]:
        """Process payload through the complete MVP pipeline."""
        if not isinstance(payload, (bytes, bytearray)):
            raise TypeError("payload must be bytes")

        payload = bytes(payload)
        started = time.time()

        decisions = self.loader.decide_all(len(payload))
        fragment_size = int(decisions["fragment_size"])
        route_count = int(decisions["route_count"])

        fragments = fragment_payload(payload, fragment_size)

        bal = BAL(self.loader, route_count=route_count)
        bal.distribute(fragments)
        ordered_fragments = bal.collect_results()

        bridge_packets: List[bytes] = []
        threat_reports: List[Dict[str, object]] = []

        for fragment_id, fragment in enumerate(ordered_fragments):
            wrapped = self.dome.wrap_fragment(fragment, metadata=f"fragment_id={fragment_id}")
            unwrapped, metadata = self.dome.unwrap_fragment(wrapped)

            transformed, snapshot, validation = self.mce.digest_fragment_checked(unwrapped)

            report = self.lemonade.scan_fragment_stateless(
                fragment=transformed,
                fragment_id=fragment_id,
                queue_depth=len(ordered_fragments),
                fragment_rate=float(len(ordered_fragments)),
                validation_report=validation,
            )

            packet = self.bridge.encapsulate(
                payload=transformed,
                lane_id=fragment_id % route_count,
                sequence_id=fragment_id,
                metadata=metadata,
            )

            bridge_packets.append(packet)
            threat_reports.append(asdict(report))

            self.vault.store(
                fragment_id=fragment_id,
                input_size=len(fragment),
                output_size=len(transformed),
                mce_state=self.mce.snapshot(),
                timestamp=time.time(),
            )

        persisted = False
        persisted_path = None

        if self.persist_path is not None:
            disk = VaultDisk(self.persist_path)
            disk.save(self.vault)
            persisted = True
            persisted_path = str(self.persist_path)

        elapsed = time.time() - started

        return {
            "pipeline": "Loader -> Dome -> BAL -> MCEHardened -> Lemonade -> ReticulumBridge -> Vault",
            "input_size": len(payload),
            "fragment_size": fragment_size,
            "fragment_count": len(fragments),
            "route_count": route_count,
            "lane_count": len(bal.lanes),
            "lane_loads": bal.lane_loads(),
            "bridge_packets": len(bridge_packets),
            "vault_entries": len(self.vault.entries),
            "blocked_reports": sum(1 for report in threat_reports if report["blocked"]),
            "max_threat_level": max([report["threat_level"] for report in threat_reports], default=0),
            "final_mce_counter": self.mce.fragment_counter,
            "final_mce_state_hex": self.mce.snapshot().hex(8),
            "dome_rejection_rate": self.dome.get_rejection_rate(),
            "persisted": persisted,
            "persisted_path": persisted_path,
            "elapsed_seconds": round(elapsed, 6),
        }


if __name__ == "__main__":
    print("=== FullPipeline v0.1 Smoke Test ===")

    payload = (b"Whisper final MVP payload. " * 200)

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "vault.json"
        pipeline = FullPipeline(b"whisper-final-pipeline-seed", persist_path=path)
        summary = pipeline.process(payload)

        for key, value in summary.items():
            print(f"{key}: {value}")
