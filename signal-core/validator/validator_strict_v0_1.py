#!/usr/bin/env python3
"""
Signal Core Strict Receipt Validator v0.1

Recomputes the full receipt hash chain independently.
Any mismatch returns FAIL with explicit fail_reasons.

Authority must remain NONE.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


AUTHORITY = "NONE"
REQUIRED_TOP_LEVEL = [
    "version",
    "artifact_hash",
    "claim_graph_hash",
    "evidence_bundle_hash",
    "claims_count",
    "analysis",
    "confidence",
    "dimensions",
    "receipt_core_hash",
    "receipt_id",
]


def canonical_json(data: Any) -> bytes:
    return json.dumps(data, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")


def compute_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prefixed_hash(data: bytes) -> str:
    return f"sha256:{compute_hash(data)}"


def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def add_fail(fail_reasons: List[Dict[str, Any]], component: str, **kwargs: Any) -> None:
    failure: Dict[str, Any] = {"component": component}
    failure.update(kwargs)
    fail_reasons.append(failure)


def receipt_core_from_receipt(receipt: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: value
        for key, value in receipt.items()
        if key not in {"receipt_id", "receipt_core_hash"}
    }


def validate_receipt(
    receipt_path: str,
    artifact_path: Optional[str] = None,
    claim_graph_path: Optional[str] = None,
    evidence_path: Optional[str] = None,
) -> Dict[str, Any]:
    receipt = load_json(receipt_path)
    fail_reasons: List[Dict[str, Any]] = []
    receipt_id = receipt.get("receipt_id")

    for field in REQUIRED_TOP_LEVEL:
        if field not in receipt:
            add_fail(fail_reasons, "SCHEMA_FIELD_MISSING", field=field)

    if receipt.get("confidence", {}).get("authority") != AUTHORITY:
        add_fail(fail_reasons, "AUTHORITY_VIOLATION", details="confidence.authority must be NONE")

    if artifact_path:
        actual_artifact_hash = prefixed_hash(Path(artifact_path).read_bytes())
        if actual_artifact_hash != receipt.get("artifact_hash"):
            add_fail(
                fail_reasons,
                "ARTIFACT_HASH_MISMATCH",
                expected=receipt.get("artifact_hash"),
                actual=actual_artifact_hash,
            )

    if claim_graph_path:
        claim_graph = load_json(claim_graph_path)
        if claim_graph.get("authority") != AUTHORITY:
            add_fail(fail_reasons, "CLAIM_GRAPH_AUTHORITY_VIOLATION", details="claim graph authority must be NONE")
        actual_claim_hash = prefixed_hash(canonical_json(claim_graph))
        if actual_claim_hash != receipt.get("claim_graph_hash"):
            add_fail(
                fail_reasons,
                "CLAIM_GRAPH_HASH_MISMATCH",
                expected=receipt.get("claim_graph_hash"),
                actual=actual_claim_hash,
            )
        claims = claim_graph.get("claims")
        if isinstance(claims, list) and len(claims) != receipt.get("claims_count"):
            add_fail(
                fail_reasons,
                "CLAIMS_COUNT_MISMATCH",
                expected=receipt.get("claims_count"),
                actual=len(claims),
            )

    if evidence_path:
        evidence = load_json(evidence_path)
        if not isinstance(evidence, list):
            add_fail(fail_reasons, "EVIDENCE_SCHEMA_VIOLATION", details="evidence bundle must be a list")
        actual_evidence_hash = prefixed_hash(canonical_json(evidence))
        if actual_evidence_hash != receipt.get("evidence_bundle_hash"):
            add_fail(
                fail_reasons,
                "EVIDENCE_BUNDLE_HASH_MISMATCH",
                expected=receipt.get("evidence_bundle_hash"),
                actual=actual_evidence_hash,
            )

    core_fields = receipt_core_from_receipt(receipt)
    computed_core_hash = prefixed_hash(canonical_json(core_fields))
    if computed_core_hash != receipt.get("receipt_core_hash"):
        add_fail(
            fail_reasons,
            "RECEIPT_CORE_HASH_MISMATCH",
            expected=receipt.get("receipt_core_hash"),
            actual=computed_core_hash,
        )

    receipt_for_id = {key: value for key, value in receipt.items() if key != "receipt_id"}
    computed_id = f"vr:sha256:{compute_hash(canonical_json(receipt_for_id))}"
    if computed_id != receipt_id:
        add_fail(
            fail_reasons,
            "RECEIPT_ID_MISMATCH",
            expected=receipt_id,
            actual=computed_id,
        )

    status = "PASS" if not fail_reasons else "FAIL"
    result: Dict[str, Any] = {
        "status": status,
        "receipt_id": receipt_id,
        "fail_reasons": fail_reasons,
    }

    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Strictly validate a Signal Core receipt v0.1.")
    parser.add_argument("receipt", help="Receipt JSON to validate")
    parser.add_argument("artifact", nargs="?", help="Optional artifact path")
    parser.add_argument("canonical_claims", nargs="?", help="Optional canonical claim graph JSON")
    parser.add_argument("evidence", nargs="?", help="Optional evidence bundle JSON")
    args = parser.parse_args()

    try:
        result = validate_receipt(args.receipt, args.artifact, args.canonical_claims, args.evidence)
        return 0 if result["status"] == "PASS" else 1
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(json.dumps({"status": "FAIL", "fail_reasons": [{"component": "VALIDATOR_EXCEPTION", "details": str(exc)}]}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
