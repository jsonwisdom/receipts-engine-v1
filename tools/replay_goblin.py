#!/usr/bin/env python3
"""GitHub Goblin replay witness.

Authority: false.

This script reads the hello_world fixture, canonicalizes JSON with a minimal
RFC8785-compatible form for ordinary JSON values, computes SHA-256, compares
against expected.json, and writes either a receipt or divergence report.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "hello_world" / "conformance_package.json"
EXPECTED = ROOT / "fixtures" / "hello_world" / "expected.json"
RECEIPTS = ROOT / "receipts"
DIVERGENCE = ROOT / "reports" / "divergence"
LOG = ROOT / "replay-goblin.log"


def canonical_json_bytes(value: Any) -> bytes:
    """Return deterministic UTF-8 JSON bytes.

    This covers the fixture class used here: objects, arrays, strings,
    booleans, null, and integers. It sorts object keys and removes whitespace.
    """
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_prefixed(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    fixture = read_json(FIXTURE)
    expected = read_json(EXPECTED)

    computed_hash = sha256_prefixed(canonical_json_bytes(fixture))
    expected_hash = expected["expected_hash"]
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    if computed_hash == expected_hash:
        receipt = {
            "artifact_hashes": [computed_hash],
            "merkle_roots": [],
            "outputs": [
                {
                    "fixture": "hello_world",
                    "result": "MATCH_CONFIRMED",
                    "computed_hash": computed_hash,
                    "expected_hash": expected_hash,
                }
            ],
            "timestamp": now,
            "version": "RECEIPT_HELLO_WORLD_MATCH_CONFIRMED_V0_1",
        }
        output_path = RECEIPTS / "hello_world_match_confirmed.json"
        write_json(output_path, receipt)
        status = "MATCH_CONFIRMED"
    else:
        report = {
            "divergence": {
                "detected": True,
                "primary_code": "D005_DETERMINISTIC_OUTPUT",
                "secondary_codes": [],
                "description": "Computed fixture hash did not match expected baseline.",
                "fsm_target": "DIVERGENCE_DETECTED",
                "retry_allowed": True,
            },
            "computed_hash": computed_hash,
            "expected_hash": expected_hash,
            "timestamp": now,
            "version": "DIVERGENCE_REPORT_HELLO_WORLD_PLACEHOLDER_HASH_V0_1",
        }
        output_path = DIVERGENCE / "hello_world_divergence_d005.json"
        write_json(output_path, report)
        status = "DIVERGENCE_DETECTED"

    LOG.write_text(
        "\n".join(
            [
                f"status={status}",
                f"fixture={FIXTURE.relative_to(ROOT)}",
                f"expected_hash={expected_hash}",
                f"computed_hash={computed_hash}",
                f"output={output_path.relative_to(ROOT)}",
                "authority=false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(LOG.read_text(encoding="utf-8"))
    return 0 if status == "MATCH_CONFIRMED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
