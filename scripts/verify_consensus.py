#!/usr/bin/env python3
"""CASE_STUDY_001 verifier report consensus checker.

This script checks N verifier_report.json files against the fixed CASE_STUDY_001
expected digest and commit SHA. It does not infer truth from majority. Reports must
match the declared target exactly.

Authority: false.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

EXPECTED_COMMIT_SHA = "ea4d77117c5cdcd9acb4ba6d1092298ed84c6c1d"
EXPECTED_DIGEST_SHA256 = "80bea317ecca694ffd1e709ea2f986374eb0753890f8fc33478567ce408e2675"
EXPECTED_AUTHORITY = False


def load_report(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {
            "_path": str(path),
            "_load_error": str(exc),
        }


def check_report(path: Path, report: dict[str, Any]) -> dict[str, Any]:
    observed_digest = report.get("observed_digest_sha256")
    expected_digest = report.get("expected_digest_sha256")
    commit_sha = report.get("commit_sha")
    expected_commit = report.get("expected_commit_sha", EXPECTED_COMMIT_SHA)
    verdict = report.get("verdict")
    authority = report.get("authority")

    errors: list[str] = []

    if report.get("_load_error"):
        errors.append(f"LOAD_ERROR: {report['_load_error']}")
    if expected_digest != EXPECTED_DIGEST_SHA256:
        errors.append("EXPECTED_DIGEST_FIELD_MISMATCH")
    if observed_digest != EXPECTED_DIGEST_SHA256:
        errors.append("OBSERVED_DIGEST_MISMATCH")
    if expected_commit != EXPECTED_COMMIT_SHA:
        errors.append("EXPECTED_COMMIT_FIELD_MISMATCH")
    if commit_sha != EXPECTED_COMMIT_SHA:
        errors.append("COMMIT_SHA_MISMATCH")
    if verdict != "PASS":
        errors.append("VERDICT_NOT_PASS")
    if authority is not EXPECTED_AUTHORITY:
        errors.append("AUTHORITY_NOT_FALSE")

    return {
        "path": str(path),
        "pass": not errors,
        "errors": errors,
        "observed_digest_sha256": observed_digest,
        "commit_sha": commit_sha,
        "verdict": verdict,
        "authority": authority,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check CASE_STUDY_001 verifier report consensus.")
    parser.add_argument("reports", nargs="+", help="Path(s) to verifier_report.json files")
    parser.add_argument("--require", type=int, default=3, help="Required PASS report count")
    args = parser.parse_args()

    results = [check_report(Path(p), load_report(Path(p))) for p in args.reports]
    pass_count = sum(1 for result in results if result["pass"])

    output = {
        "case_study": "CASE_STUDY_001",
        "expected_digest_sha256": EXPECTED_DIGEST_SHA256,
        "expected_commit_sha": EXPECTED_COMMIT_SHA,
        "required_passes": args.require,
        "observed_reports": len(results),
        "pass_count": pass_count,
        "consensus_verdict": "PASS" if pass_count >= args.require else "FAIL",
        "authority": False,
        "results": results,
    }

    print(json.dumps(output, indent=2, sort_keys=True))
    return 0 if pass_count >= args.require else 1


if __name__ == "__main__":
    sys.exit(main())
