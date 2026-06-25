#!/usr/bin/env python3
"""
Signal Core Verification Receipt v0.1 validator stub.

Purpose:
- Validate the structural primitive.
- Recompute the receipt_id from canonical components.
- Refuse truth arbitration.

Authority is always NONE.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict


SCHEMA_VERSION = "signal.receipt.v0.1"
AUTHORITY = "NONE"


def canonical_json(value: Any) -> bytes:
    """
    Minimal deterministic JSON fallback.
    TODO: replace with full RFC8785/JCS implementation before production use.
    """
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def expected_receipt_id(receipt: Dict[str, Any]) -> str:
    core = {
        "artifact.hash": receipt["artifact"]["hash"],
        "claim_snapshot.hash": receipt["claim_snapshot"]["hash"],
        "evidence_bundle.hash": receipt["evidence_bundle"]["hash"],
    }
    return sha256_hex(canonical_json(core))


def validate(receipt: Dict[str, Any], strict_id: bool = False) -> None:
    if receipt.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("schema_version mismatch")

    if receipt.get("authority") != AUTHORITY:
        raise ValueError("authority must be NONE")

    if "truth" in canonical_json(receipt).decode("utf-8").lower():
        raise ValueError("truth arbitration language is forbidden in receipt primitive")

    telemetry = receipt.get("telemetry", {})
    required_axes = [
        "provenance",
        "recursion",
        "crypto_integrity",
        "coverage",
        "replay",
        "uncertainty",
    ]
    for axis in required_axes:
        value = telemetry.get(axis)
        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            raise ValueError(f"telemetry.{axis} must be a number from 0 to 1")

    computed = expected_receipt_id(receipt)
    declared = receipt.get("receipt_id")
    if strict_id and declared != computed:
        raise ValueError(f"receipt_id mismatch: declared={declared} computed={computed}")

    print("PASS signal.receipt.v0.1")
    print(f"authority={receipt['authority']}")
    print(f"declared_receipt_id={declared}")
    print(f"computed_receipt_id={computed}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--strict-id", action="store_true", help="fail unless receipt_id matches recomputed core hash")
    args = parser.parse_args()

    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
        validate(receipt, strict_id=args.strict_id)
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
