# bench/bench_regression.py

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    test_file = ROOT / "tests" / "test_regression_v043.py"

    start = time.perf_counter()

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", str(test_file)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )

    elapsed = time.perf_counter() - start

    print("Regression benchmark")
    print("--------------------")
    print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())
    print(f"elapsed: {elapsed:.3f} s")

    if result.returncode != 0:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
