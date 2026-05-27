#!/usr/bin/env python3
"""
sign_lineage.py

Hash-only mission lineage receipt emitter for receipts-engine-v1.

Boundary:
- Reads REPLAY_RESULT.json.
- Reads AL acceptance reference JSON.
- Verifies replay + AL acceptance equivalence.
- Emits only to local outbox/.
- Does not read raw missions.
- Does not interpret mission semantics.
- Does not write into AL.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

RECEIPT_TYPE = "ORG_MISSION_LINEAGE_RECEIPT_V1"
CONTRACT_ID = "receipts-engine-signing-contract-v1"
SIGNATURE_MODE = "HASH_ONLY_V0"
AUTHORITY_BOUNDARY = "RECEIPT_IS_PROOF_OF_ACCEPTED_LINEAGE_NOT_MISSION_MEANING"


def read_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {path}: {exc}")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def get_required(obj: Dict[str, Any], key: str, label: str) -> Any:
    if key not in obj:
        raise SystemExit(f"{label} missing required field: {key}")
    return obj[key]


def build_receipt(replay_result: Dict[str, Any], al_acceptance: Dict[str, Any], al_reference: str) -> Dict[str, Any]:
    replay_verdict = get_required(replay_result, "verdict", "REPLAY_RESULT")
    if replay_verdict != "REPLAY_MATCH":
        raise SystemExit(f"replay verdict rejected: {replay_verdict}")

    al_verdict = get_required(al_acceptance, "verdict", "AL acceptance")
    if al_verdict != "ACCEPTED":
        raise SystemExit(f"AL acceptance rejected: {al_verdict}")

    replay_final = get_required(replay_result, "final_sha256", "REPLAY_RESULT")
    al_final = get_required(al_acceptance, "final_sha256", "AL acceptance")
    if replay_final != al_final:
        raise SystemExit(f"final_sha256 mismatch: replay={replay_final} al={al_final}")

    return {
        "receipt_type": RECEIPT_TYPE,
        "contract_id": CONTRACT_ID,
        "signed_final_sha256": replay_final,
        "replay_result_sha256": sha256_json(replay_result),
        "al_acceptance_sha256": sha256_json(al_acceptance),
        "al_acceptance_reference": al_reference,
        "signed_at": utc_now_iso(),
        "signature_mode": SIGNATURE_MODE,
        "authority_boundary": AUTHORITY_BOUNDARY,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit a hash-only mission lineage receipt into local outbox.")
    parser.add_argument("--replay-result", required=True, help="Path to REPLAY_RESULT.json")
    parser.add_argument("--al-acceptance", required=True, help="Path to AL acceptance reference JSON")
    parser.add_argument("--outbox", default="outbox", help="Local outbox directory")
    parser.add_argument("--output-name", default="ORG_MISSION_LINEAGE_RECEIPT_V1.json", help="Receipt filename")
    args = parser.parse_args()

    replay_path = Path(args.replay_result)
    al_path = Path(args.al_acceptance)
    outbox = Path(args.outbox)

    replay_result = read_json(replay_path)
    al_acceptance = read_json(al_path)

    receipt = build_receipt(replay_result, al_acceptance, str(al_path))

    outbox.mkdir(parents=True, exist_ok=True)
    output_path = outbox / args.output_name
    output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "EMITTED",
        "output": str(output_path),
        "receipt_sha256": sha256_json(receipt),
        "authority_boundary": AUTHORITY_BOUNDARY,
    }, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    sys.exit(main())
