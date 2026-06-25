#!/usr/bin/env python3
"""
Signal Core Negative Mutation Runner v0.1

Proves the pipeline fails correctly:
- TC-03 authority violation fails before sealing
- TC-07 dependency cycle fails before sealing
- TC-04 claim mutation fails against a sealed base receipt
- TC-04-A artifact bit flip fails against a sealed base receipt

No partial trust. Expected failures are PASS for this runner.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
CANONICALIZER = ROOT / "canonicalizer" / "canonicalize_claim_graph.py"
SEALER = ROOT / "sealer" / "seal_receipt_v0_1.py"
VALIDATOR = ROOT / "validator" / "validator_strict_v0_1.py"
ARTIFACT = REPO / "README.md"
BASE_VECTOR = ROOT / "tests" / "vectors" / "tc-01_commutative_order.json"
AUTHORITY_VECTOR = ROOT / "tests" / "vectors" / "tc-03_authority_violation.json"
CYCLE_VECTOR = ROOT / "tests" / "vectors" / "tc-07_cycle_violation.json"
MUTATION_VECTOR = ROOT / "tests" / "vectors" / "tc-04_claim_mutation.json"


@dataclass(frozen=True)
class NegativeCase:
    case_id: str
    name: str
    expected_code: str
    runner: Callable[[Path], subprocess.CompletedProcess[str]]


def run_command(cmd: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def output_text(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stdout or "") + "\n" + (result.stderr or "")


def seal_base(tmp: Path) -> tuple[Path, Path]:
    canonical = tmp / "canonical_base.json"
    sealed = tmp / "sealed_base.json"

    canonical_result = run_command([sys.executable, str(CANONICALIZER), str(BASE_VECTOR), str(canonical)])
    if canonical_result.returncode != 0:
        raise RuntimeError(output_text(canonical_result))

    seal_result = run_command([sys.executable, str(SEALER), str(ARTIFACT), str(canonical), str(sealed)])
    if seal_result.returncode != 0:
        raise RuntimeError(output_text(seal_result))

    return canonical, sealed


def parse_fail_codes(result: subprocess.CompletedProcess[str]) -> List[str]:
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    return [item.get("component", "") for item in payload.get("fail_reasons", [])]


def run_authority_violation(tmp: Path) -> subprocess.CompletedProcess[str]:
    return run_command([sys.executable, str(CANONICALIZER), str(AUTHORITY_VECTOR), str(tmp / "authority_out.json")])


def run_cycle_violation(tmp: Path) -> subprocess.CompletedProcess[str]:
    gauntlet = ROOT / "tests" / "run_gauntlet.py"
    return run_command([sys.executable, str(gauntlet)])


def run_claim_mutation(tmp: Path) -> subprocess.CompletedProcess[str]:
    base_canonical, sealed = seal_base(tmp)
    mutated_canonical = tmp / "canonical_mutated.json"

    canon_result = run_command([sys.executable, str(CANONICALIZER), str(MUTATION_VECTOR), str(mutated_canonical)])
    if canon_result.returncode != 0:
        raise RuntimeError(output_text(canon_result))

    return run_command([sys.executable, str(VALIDATOR), str(sealed), str(ARTIFACT), str(mutated_canonical)])


def flip_first_byte(src: Path, dst: Path) -> None:
    data = bytearray(src.read_bytes())
    if not data:
        raise ValueError("cannot flip empty artifact")
    data[0] ^= 0x01
    dst.write_bytes(bytes(data))


def run_artifact_bitflip(tmp: Path) -> subprocess.CompletedProcess[str]:
    base_canonical, sealed = seal_base(tmp)
    mutated_artifact = tmp / "artifact_bitflip.bin"
    flip_first_byte(ARTIFACT, mutated_artifact)
    return run_command([sys.executable, str(VALIDATOR), str(sealed), str(mutated_artifact), str(base_canonical)])


def evaluate_case(case: NegativeCase, tmp: Path) -> bool:
    try:
        result = case.runner(tmp)
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"{case.case_id} {case.name}: FAIL runner_exception={exc}")
        return False

    text = output_text(result)
    codes = parse_fail_codes(result)

    if case.expected_code in codes:
        print(f"{case.case_id} {case.name}: PASS expected_code={case.expected_code}")
        return True

    if case.expected_code in text and result.returncode != 0:
        print(f"{case.case_id} {case.name}: PASS expected_text={case.expected_code}")
        return True

    print(f"{case.case_id} {case.name}: FAIL expected={case.expected_code} rc={result.returncode}")
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return False


def main() -> int:
    if not ARTIFACT.exists():
        print(f"FAIL missing artifact fixture: {ARTIFACT}", file=sys.stderr)
        return 1

    cases = [
        NegativeCase("TC-03", "authority violation", "authority must be NONE", run_authority_violation),
        NegativeCase("TC-07", "dependency cycle", "cycle detected", run_cycle_violation),
        NegativeCase("TC-04", "claim mutation", "CLAIM_GRAPH_HASH_MISMATCH", run_claim_mutation),
        NegativeCase("TC-04-A", "artifact bit flip", "ARTIFACT_HASH_MISMATCH", run_artifact_bitflip),
    ]

    with tempfile.TemporaryDirectory(prefix="signal-core-mutations-") as tmpdir:
        tmp = Path(tmpdir)
        results = [evaluate_case(case, tmp) for case in cases]

    passed = sum(1 for value in results if value)
    total = len(results)
    print(f"Mutation Runner: {passed}/{total} expected failures observed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
