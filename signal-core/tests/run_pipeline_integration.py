#!/usr/bin/env python3
"""
Signal Core Pipeline Integration Runner v0.1

Runs canonicalizer -> sealer -> validator through the CLI wrapper.
This validates the component wiring, not just individual hash functions.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
CLI = ROOT / "cli" / "receipts.py"
ARTIFACT = REPO / "README.md"
RAW_CLAIMS = ROOT / "tests" / "vectors" / "tc-01_commutative_order.json"


def run_command(cmd: List[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    return result


def main() -> int:
    if not ARTIFACT.exists():
        print(f"FAIL missing artifact fixture: {ARTIFACT}", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="signal-core-integration-") as tmp:
        cmd = [
            sys.executable,
            str(CLI),
            str(ARTIFACT),
            str(RAW_CLAIMS),
            "--out",
            tmp,
        ]
        result = run_command(cmd)
        if result.returncode != 0:
            print("Pipeline Integration: FAIL", file=sys.stderr)
            return result.returncode

        sealed = Path(tmp) / "sealed_receipt.json"
        canonical = Path(tmp) / "canonical_claims.json"
        if not sealed.exists() or not canonical.exists():
            print("Pipeline Integration: FAIL missing output files", file=sys.stderr)
            return 1

    print("Pipeline Integration: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
