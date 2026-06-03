#!/usr/bin/env python3
"""
CASE_STUDY_001 Consensus Verifier

Deterministic, no-network, no-deps validation that N independent
verifiers all report the expected commit SHA and content digest.

authority: false
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXPECTED_COMMIT_SHA = "ea4d77117c5cdcd9acb4ba6d1092298ed84c6c1d"
EXPECTED_DIGEST = "80bea317ecca694ffd1e709ea2f986374eb0753890f8fc33478567ce408e2675"
EXPECTED_AUTHORITY = False


def first_present(report: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in report:
            return report[key]
    return None


def load_report(filepath: str) -> dict[str, Any]:
    path = Path(filepath)
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{filepath}: invalid JSON: {exc}") from exc
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"{filepath}: failed to load report: {exc}") from exc

    verifier = first_present(report, ["verifier", "github_actor", "run_url"])
    commit_sha = first_present(report, ["commit_sha", "resolved_commit_sha"])
    digest = first_present(report, ["observed_digest_sha256", "content_hash"])

    missing = []
    if verifier is None:
        missing.append("verifier")
    if commit_sha is None:
        missing.append("commit_sha or resolved_commit_sha")
    if digest is None:
        missing.append("observed_digest_sha256 or content_hash")
    if "authority" not in report:
        missing.append("authority")
    if missing:
        raise ValueError(f"{filepath}: missing required field(s): {', '.join(missing)}")

    return report


def verify_consensus(reports: dict[str, dict[str, Any]], require: int = 3) -> dict[str, Any]:
    errors: list[str] = []
    passing_verifiers: list[str] = []
    seen_verifier_paths: dict[str, str] = {}

    if len(reports) != require:
        errors.append(f"Expected exactly {require} reports, found {len(reports)}")

    for report_path, report_data in reports.items():
        verifier = str(first_present(report_data, ["verifier", "github_actor", "run_url"]))
        commit_sha = first_present(report_data, ["commit_sha", "resolved_commit_sha"])
        digest = first_present(report_data, ["observed_digest_sha256", "content_hash"])
        authority = report_data.get("authority")
        verdict = report_data.get("verdict")

        if verifier in seen_verifier_paths:
            errors.append(
                f"Duplicate report from verifier: {verifier} "
                f"({seen_verifier_paths[verifier]} and {report_path})"
            )
            continue
        seen_verifier_paths[verifier] = report_path

        if commit_sha != EXPECTED_COMMIT_SHA:
            errors.append(f"{verifier}: wrong commit SHA: got {commit_sha}, expected {EXPECTED_COMMIT_SHA}")
            continue
        if digest != EXPECTED_DIGEST:
            errors.append(f"{verifier}: wrong digest: got {digest}, expected {EXPECTED_DIGEST}")
            continue
        if authority != EXPECTED_AUTHORITY:
            errors.append(f"{verifier}: authority must be false, got {authority}")
            continue
        if verdict not in (None, "PASS"):
            errors.append(f"{verifier}: verdict must be PASS when present, got {verdict}")
            continue

        passing_verifiers.append(verifier)

    duplicates = [verifier for verifier, count in Counter(passing_verifiers).items() if count > 1]
    if duplicates:
        errors.append(f"Duplicate PASS in same report set: {duplicates}")

    unique_passing_verifiers = sorted(set(passing_verifiers))
    verdict = "PASS" if len(unique_passing_verifiers) >= require and not errors else "FAIL"

    return {
        "case_study": "CASE_STUDY_001",
        "verdict": verdict,
        "unique_passing_verifiers": len(unique_passing_verifiers),
        "passing_verifiers": unique_passing_verifiers,
        "errors": errors,
        "authority": False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "expected_commit_sha": EXPECTED_COMMIT_SHA,
        "expected_digest": EXPECTED_DIGEST,
        "require": require,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify consensus across independent CASE_STUDY_001 reports")
    parser.add_argument("reports", nargs="+", help="Paths to verifier_report.json files")
    parser.add_argument("--require", type=int, default=3, help="Number of unique PASS reports required")
    parser.add_argument("--output", help="Output file for consensus_result.json")
    args = parser.parse_args()

    reports_dict: dict[str, dict[str, Any]] = {}
    load_errors: list[str] = []
    for report_path in args.reports:
        try:
            reports_dict[report_path] = load_report(report_path)
        except ValueError as exc:
            load_errors.append(str(exc))

    if load_errors:
        result = {
            "case_study": "CASE_STUDY_001",
            "verdict": "FAIL",
            "unique_passing_verifiers": 0,
            "passing_verifiers": [],
            "errors": load_errors,
            "authority": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "expected_commit_sha": EXPECTED_COMMIT_SHA,
            "expected_digest": EXPECTED_DIGEST,
            "require": args.require,
        }
    else:
        result = verify_consensus(reports_dict, require=args.require)

    output_json = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(output_json + "\n", encoding="utf-8")
    else:
        print(output_json)

    print("\n" + "=" * 50, file=sys.stderr)
    print(f"VERDICT: {result['verdict']}", file=sys.stderr)
    print(f"Unique passing verifiers: {result['unique_passing_verifiers']}/{args.require}", file=sys.stderr)
    if result["errors"]:
        print("\nErrors:", file=sys.stderr)
        for error in result["errors"]:
            print(f"  - {error}", file=sys.stderr)
    if result["passing_verifiers"]:
        print("\nPassing verifiers:", file=sys.stderr)
        for verifier in result["passing_verifiers"]:
            print(f"  - {verifier}", file=sys.stderr)
    print("=" * 50 + "\n", file=sys.stderr)

    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
