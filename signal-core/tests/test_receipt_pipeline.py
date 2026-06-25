#!/usr/bin/env python3
"""
Signal Core pytest suite v0.1

CI-native wrapper for:
- positive end-to-end pipeline replay
- negative mutation runner
- direct authority violation boundary
- direct cycle detection boundary
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
CLI = ROOT / "cli" / "receipts.py"
CANONICALIZER = ROOT / "canonicalizer" / "canonicalize_claim_graph.py"
GAUNTLET = ROOT / "tests" / "run_gauntlet.py"
MUTATION_RUNNER = ROOT / "tests" / "mutation_runner.py"
ARTIFACT = REPO / "README.md"
BASE_CLAIMS = ROOT / "tests" / "vectors" / "tc-01_commutative_order.json"
AUTHORITY_VECTOR = ROOT / "tests" / "vectors" / "tc-03_authority_violation.json"


def run_cli(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def test_full_pipeline(tmp_path: Path) -> None:
    result = run_cli([
        sys.executable,
        str(CLI),
        str(ARTIFACT),
        str(BASE_CLAIMS),
        "--out",
        str(tmp_path),
    ])
    assert result.returncode == 0, result.stdout + result.stderr

    sealed_path = tmp_path / "sealed_receipt.json"
    canonical_path = tmp_path / "canonical_claims.json"
    assert sealed_path.exists()
    assert canonical_path.exists()

    sealed = json.loads(sealed_path.read_text(encoding="utf-8"))
    assert sealed["confidence"]["authority"] == "NONE"
    assert sealed["receipt_id"].startswith("vr:sha256:")


def test_replay_gauntlet() -> None:
    result = run_cli([sys.executable, str(GAUNTLET)])
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Replay Gauntlet:" in result.stdout


def test_mutation_cases() -> None:
    result = run_cli([sys.executable, str(MUTATION_RUNNER)])
    assert result.returncode == 0, result.stdout + result.stderr
    assert "4/4 expected failures observed" in result.stdout


def test_authority_violation_direct() -> None:
    result = run_cli([
        sys.executable,
        str(CANONICALIZER),
        str(AUTHORITY_VECTOR),
    ])
    assert result.returncode != 0
    assert "authority must be NONE" in (result.stdout + result.stderr)
