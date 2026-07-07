#!/usr/bin/env python3
"""ALMS Receipt CLI - V0.1

Canonical verifier contract:
  python tools/alms.py verify fixtures/receipts/valid_signed.json
  VALID

The verifier checks a real Ed25519 signature over canonical JSON bytes.
It fails closed on malformed JSON, missing fields, bad hex, hash mismatch,
or invalid signature.
"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric import ed25519

SIGNATURE_FIELDS = {"signature", "public_key", "receipt_hash"}


def canonical_json_bytes(value: Any) -> bytes:
    """JCS-style canonical JSON for this fixture surface: sorted keys, compact UTF-8."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def signed_payload(receipt: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in receipt.items() if key not in SIGNATURE_FIELDS}


def verify(path: str) -> bool:
    receipt = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(receipt, dict):
        return False

    signature_hex = receipt.get("signature")
    public_key_hex = receipt.get("public_key")
    receipt_hash = receipt.get("receipt_hash")
    if not all(isinstance(v, str) and v for v in (signature_hex, public_key_hex, receipt_hash)):
        return False

    payload = signed_payload(receipt)
    canonical = canonical_json_bytes(payload)
    computed_hash = hashlib.sha256(canonical).hexdigest()
    if receipt_hash != computed_hash:
        return False

    try:
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
        signature = bytes.fromhex(signature_hex)
        public_key.verify(signature, canonical)
        return True
    except Exception:
        return False


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] != "verify":
        print("usage: tools/alms.py verify <receipt.json>", file=sys.stderr)
        return 2

    ok = verify(sys.argv[2])
    print("VALID" if ok else "INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
