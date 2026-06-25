#!/usr/bin/env python3
"""
Signal Core Receipt Pipeline CLI v0.1

One-command replay:
canonicalize -> seal -> validate

Authority remains NONE throughout the receipt pipeline.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


ROOT = Path(__file__).resolve().parents[1]
CANONICALIZER = ROOT / "canonicalizer" / "canonicalize_claim_graph.py"
SEALER = ROOT / "sealer" / "seal_receipt_v0_1.py"
VALIDATOR = ROOT / "validator" / "validator_strict_v0_1.py"


def run_command(cmd: List[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if result.returncode != 0:
        raise RuntimeError(f"command failed with exit code {result.returncode}: {' '.join(cmd)}")
    return result


def pipeline_replay(
    artifact: str,
    raw_claims: str,
    evidence: Optional[str] = None,
    output_dir: str = ".",
) -> Path:
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    canonical_path = output_root / "canonical_claims.json"
    sealed_path = output_root / "sealed_receipt.json"

    print("=== RECEIPT PIPELINE REPLAY ===")

    run_command([sys.executable, str(CANONICALIZER), raw_claims, str(canonical_path)])

    seal_cmd = [sys.executable, str(SEALER), artifact, str(canonical_path)]
    if evidence:
        seal_cmd.append(evidence)
    seal_cmd.append(str(sealed_path))
    run_command(seal_cmd)

    validate_cmd = [sys.executable, str(VALIDATOR), str(sealed_path), artifact, str(canonical_path)]
    if evidence:
        validate_cmd.append(evidence)
    run_command(validate_cmd)

    print("=== PIPELINE COMPLETE ===")
    print(f"Sealed receipt: {sealed_path}")
    return sealed_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Signal Core canonicalize -> seal -> validate.")
    parser.add_argument("artifact", help="Artifact file")
    parser.add_argument("raw_claims", help="Raw claim graph JSON")
    parser.add_argument("evidence", nargs="?", help="Optional evidence bundle JSON list")
    parser.add_argument("--out", default=".", help="Output directory for canonical_claims.json and sealed_receipt.json")
    args = parser.parse_args()

    try:
        pipeline_replay(args.artifact, args.raw_claims, args.evidence, args.out)
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
