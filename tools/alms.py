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
TRANSFER_EVENT_HASH = "ddf252ad"


def canonical_json_bytes(value: Any) -> bytes:
    """JCS-style canonical JSON for this fixture surface: sorted keys, compact UTF-8."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_hex(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def signed_payload(receipt: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in receipt.items() if key not in SIGNATURE_FIELDS}


def verify(path: str) -> bool:
    receipt = load_json(path)
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


def profile_ok(profile: dict[str, Any]) -> bool:
    required = {
        "payment_profile_version": str,
        "chain_id": int,
        "token_address": str,
        "token_symbol": str,
        "token_decimals": int,
        "min_payment": str,
        "max_payment": str,
        "payee": str,
    }
    return isinstance(profile, dict) and all(isinstance(profile.get(k), t) for k, t in required.items())


def payment_reference(receipt_hash: str, profile: dict[str, Any]) -> str:
    core = {
        "receipt_hash": receipt_hash,
        "payment_profile_version": profile["payment_profile_version"],
        "chain_id": profile["chain_id"],
        "token_address": profile["token_address"].lower(),
        "payee": profile["payee"].lower(),
    }
    return sha256_hex(core)


def amount_in_range(amount: str, profile: dict[str, Any]) -> bool:
    try:
        value = int(amount)
        return int(profile["min_payment"]) <= value <= int(profile["max_payment"])
    except Exception:
        return False


def payment_verify(profile_path: str, proof_path: str) -> bool:
    profile = load_json(profile_path)
    proof = load_json(proof_path)
    if not profile_ok(profile) or not isinstance(proof, dict):
        return False

    checks = [
        proof.get("chain_id") == profile["chain_id"],
        str(proof.get("token_address", "")).lower() == profile["token_address"].lower(),
        proof.get("token_decimals") == profile["token_decimals"],
        str(proof.get("payee", "")).lower() == profile["payee"].lower(),
        isinstance(proof.get("payer"), str) and bool(proof.get("payer")),
        isinstance(proof.get("tx_hash"), str) and bool(proof.get("tx_hash")),
        isinstance(proof.get("block_number"), int),
        str(proof.get("transfer_event_hash", "")).lower().startswith(TRANSFER_EVENT_HASH),
        amount_in_range(str(proof.get("amount", "")), profile),
    ]
    receipt_hash = proof.get("receipt_hash")
    expected_ref = payment_reference(receipt_hash, profile) if isinstance(receipt_hash, str) else ""
    checks.append(proof.get("payment_reference") == expected_ref)
    return all(checks)


def usage() -> int:
    print(
        "usage: tools/alms.py verify <receipt.json> | "
        "payment-bind <receipt.json> <profile.json> | "
        "payment-verify <profile.json> <proof.json> | "
        "payment-refresh <profile.json>",
        file=sys.stderr,
    )
    return 2


def main() -> int:
    if len(sys.argv) < 2:
        return usage()

    cmd = sys.argv[1]
    if cmd == "verify" and len(sys.argv) == 3:
        ok = verify(sys.argv[2])
        print("VALID" if ok else "INVALID")
        return 0 if ok else 1

    if cmd == "payment-bind" and len(sys.argv) == 4:
        receipt = load_json(sys.argv[2])
        profile = load_json(sys.argv[3])
        if not isinstance(receipt, dict) or not profile_ok(profile):
            print("INVALID")
            return 1
        receipt_hash = receipt.get("receipt_hash")
        if not isinstance(receipt_hash, str) or not receipt_hash:
            print("INVALID")
            return 1
        print(payment_reference(receipt_hash, profile))
        return 0

    if cmd == "payment-verify" and len(sys.argv) == 4:
        ok = payment_verify(sys.argv[2], sys.argv[3])
        print("VALID_PAYMENT" if ok else "INVALID_PAYMENT")
        return 0 if ok else 1

    if cmd == "payment-refresh" and len(sys.argv) == 3:
        ok = profile_ok(load_json(sys.argv[2]))
        print("PROFILE_VALID" if ok else "PROFILE_INVALID")
        return 0 if ok else 1

    return usage()


if __name__ == "__main__":
    raise SystemExit(main())
