#!/usr/bin/env python3
"""
Signal Core Receipt Sealer v0.1

Transforms an artifact, canonical claim graph, and evidence bundle into a
receipt envelope with deterministic hashes.

This sealer does not assert truth and does not assign authority.
Authority remains NONE.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


VERSION = "v0.1"
AUTHORITY = "NONE"


def canonical_json(data: Any) -> bytes:
    return json.dumps(data, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")


def compute_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prefixed_hash(data: bytes) -> str:
    return f"sha256:{compute_hash(data)}"


def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def assert_canonical_claim_graph(claim_graph: Dict[str, Any]) -> None:
    if claim_graph.get("authority") != AUTHORITY:
        raise ValueError("canonical claim graph authority must be NONE")
    if "claims" not in claim_graph or not isinstance(claim_graph["claims"], list):
        raise ValueError("canonical claim graph must include claims list")


def seal_receipt(
    artifact_path: str,
    canonical_claims_path: str,
    evidence_bundle: Optional[List[Any]] = None,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    artifact = Path(artifact_path).read_bytes()
    claim_graph = load_json(canonical_claims_path)
    assert_canonical_claim_graph(claim_graph)

    evidence_bundle = evidence_bundle or []
    if not isinstance(evidence_bundle, list):
        raise ValueError("evidence bundle must be a list")

    artifact_hash = prefixed_hash(artifact)
    claim_hash = prefixed_hash(canonical_json(claim_graph))
    evidence_hash = prefixed_hash(canonical_json(evidence_bundle))

    receipt_core: Dict[str, Any] = {
        "version": VERSION,
        "artifact_hash": artifact_hash,
        "claim_graph_hash": claim_hash,
        "evidence_bundle_hash": evidence_hash,
        "claims_count": len(claim_graph.get("claims", [])),
        "analysis": {
            "primary_evidence": 0,
            "secondary_evidence": 0,
            "ai_references": 0,
            "missing_provenance": 0,
            "recursion_depth": 0,
            "circular_references": False,
        },
        "confidence": {
            "structural_integrity": 0,
            "evidence_coverage": 0,
            "reproducibility": 0,
            "authority": AUTHORITY,
        },
        "dimensions": {
            "provenance": "unscored",
            "recursion": "unscored",
            "crypto_integrity": "valid",
            "evidence_coverage": 0,
            "replay_success": True,
            "uncertainty": "unscored",
        },
    }

    receipt_core_hash = prefixed_hash(canonical_json(receipt_core))

    receipt: Dict[str, Any] = {
        **receipt_core,
        "receipt_core_hash": receipt_core_hash,
        "receipt_id": "",
    }

    receipt_for_id = {key: value for key, value in receipt.items() if key != "receipt_id"}
    receipt["receipt_id"] = f"vr:sha256:{compute_hash(canonical_json(receipt_for_id))}"

    if output_path:
        Path(output_path).write_text(json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Sealed -> {output_path}")
        print(f"Receipt ID: {receipt['receipt_id']}")
    else:
        print(json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False))

    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Seal a Signal Core verification receipt v0.1.")
    parser.add_argument("artifact", help="Artifact file to hash")
    parser.add_argument("canonical_claims", help="Canonical claim graph JSON")
    parser.add_argument("evidence", nargs="?", help="Optional evidence bundle JSON list")
    parser.add_argument("output", nargs="?", help="Optional output receipt JSON")
    args = parser.parse_args()

    try:
        evidence = load_json(args.evidence) if args.evidence else []
        seal_receipt(args.artifact, args.canonical_claims, evidence, args.output)
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
