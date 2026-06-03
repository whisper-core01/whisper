# tests/test_bench_import_paths.py

import subprocess
import sys
from pathlib import Path


def test_bench_vaultdisk_runs_from_project_parent():
    project_root = Path(__file__).resolve().parents[1]
    parent = project_root.parent
    script = project_root / "bench" / "bench_vaultdisk.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--entries",
            "10",
        ],
        cwd=str(parent),
        capture_output=True,
        text=True,
        check=True,
    )

    assert "VaultDisk benchmark" in result.stdout
    assert "roundtrip:     True" in result.stdout
