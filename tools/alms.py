#!/usr/bin/env python3
"""ALMS Receipt CLI - V0.1."""

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric import ed25519

SIGNATURE_FIELDS = {"signature", "public_key", "receipt_hash"}
ERC20_TRANSFER_EVENT_HASH = "ddf252ad"
ERC1155_TRANSFER_SINGLE_EVENT_HASH = "c3d58168"
ERC1155_TRANSFER_BATCH_EVENT_HASH = "4a39dc06"
SUPPORTED_RENDER_ADAPTERS = {"erc20", "erc1155", "future_adapter"}
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


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
    if receipt_hash != hashlib.sha256(canonical).hexdigest():
        return False
    try:
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
        public_key.verify(bytes.fromhex(signature_hex), canonical)
        return True
    except Exception:
        return False


def adapter(profile: dict[str, Any]) -> str:
    standard = profile.get("asset_standard")
    if standard is None:
        return "erc20"
    if standard in {"erc20", "erc1155"}:
        return standard
    return "unknown"


def is_int_string(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        return int(value) >= 0
    except Exception:
        return False


def erc20_profile_ok(profile: dict[str, Any]) -> bool:
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
    return (
        isinstance(profile, dict)
        and adapter(profile) == "erc20"
        and profile.get("payment_profile_version") == "ERC20_PAYMENT_PROFILE_V0_1"
        and all(isinstance(profile.get(k), t) for k, t in required.items())
        and is_int_string(profile.get("min_payment"))
        and is_int_string(profile.get("max_payment"))
    )


def erc1155_profile_ok(profile: dict[str, Any]) -> bool:
    return (
        isinstance(profile, dict)
        and profile.get("payment_profile_version") == "ERC1155_PAYMENT_ADAPTER_V0_1"
        and profile.get("asset_standard") == "erc1155"
        and isinstance(profile.get("chain_id"), int)
        and isinstance(profile.get("token_address"), str)
        and bool(profile.get("token_address"))
        and isinstance(profile.get("accepted_token_ids"), list)
        and bool(profile.get("accepted_token_ids"))
        and all(isinstance(token_id, str) and token_id for token_id in profile.get("accepted_token_ids", []))
        and is_int_string(profile.get("min_units"))
        and is_int_string(profile.get("max_units"))
        and isinstance(profile.get("payee"), str)
        and bool(profile.get("payee"))
        and isinstance(profile.get("batch_allowed"), bool)
    )


def profile_ok(profile: dict[str, Any]) -> bool:
    if adapter(profile) == "erc20":
        return erc20_profile_ok(profile)
    if adapter(profile) == "erc1155":
        return erc1155_profile_ok(profile)
    return False


def erc20_payment_reference(receipt_hash: str, profile: dict[str, Any]) -> str:
    return sha256_hex({
        "receipt_hash": receipt_hash,
        "payment_profile_version": profile["payment_profile_version"],
        "chain_id": profile["chain_id"],
        "token_address": profile["token_address"].lower(),
        "payee": profile["payee"].lower(),
    })


def erc1155_payment_reference(receipt_hash: str, profile: dict[str, Any], token_id: str) -> str:
    return sha256_hex({
        "receipt_hash": receipt_hash,
        "payment_profile_version": profile["payment_profile_version"],
        "asset_standard": profile["asset_standard"],
        "chain_id": profile["chain_id"],
        "token_address": profile["token_address"].lower(),
        "token_id": token_id,
        "payee": profile["payee"].lower(),
    })


def payment_reference(receipt_hash: str, profile: dict[str, Any], proof: dict[str, Any] | None = None) -> str:
    if adapter(profile) == "erc20":
        return erc20_payment_reference(receipt_hash, profile)
    if adapter(profile) == "erc1155":
        token_id = proof.get("token_id") if isinstance(proof, dict) else profile.get("accepted_token_ids", [""])[0]
        return erc1155_payment_reference(receipt_hash, profile, token_id) if isinstance(token_id, str) and token_id else ""
    return ""


def amount_in_range(amount: str, profile: dict[str, Any]) -> bool:
    try:
        return int(profile["min_payment"]) <= int(amount) <= int(profile["max_payment"])
    except Exception:
        return False


def units_in_range(units: str, profile: dict[str, Any]) -> bool:
    try:
        return int(profile["min_units"]) <= int(units) <= int(profile["max_units"])
    except Exception:
        return False


def erc20_payment_verify(profile: dict[str, Any], proof: dict[str, Any]) -> bool:
    if not erc20_profile_ok(profile) or not isinstance(proof, dict):
        return False
    receipt_hash = proof.get("receipt_hash")
    checks = [
        proof.get("chain_id") == profile["chain_id"],
        str(proof.get("token_address", "")).lower() == profile["token_address"].lower(),
        proof.get("token_decimals") == profile["token_decimals"],
        str(proof.get("payee", "")).lower() == profile["payee"].lower(),
        isinstance(proof.get("payer"), str) and bool(proof.get("payer")),
        isinstance(proof.get("tx_hash"), str) and bool(proof.get("tx_hash")),
        isinstance(proof.get("block_number"), int),
        str(proof.get("transfer_event_hash", "")).lower().startswith(ERC20_TRANSFER_EVENT_HASH),
        amount_in_range(str(proof.get("amount", "")), profile),
        proof.get("payment_reference") == (erc20_payment_reference(receipt_hash, profile) if isinstance(receipt_hash, str) else ""),
    ]
    return all(checks)


def erc1155_payment_verify(profile: dict[str, Any], proof: dict[str, Any]) -> bool:
    if not erc1155_profile_ok(profile) or not isinstance(proof, dict):
        return False
    event_hash = str(proof.get("transfer_event_hash", "")).lower()
    is_single = event_hash.startswith(ERC1155_TRANSFER_SINGLE_EVENT_HASH)
    is_batch = event_hash.startswith(ERC1155_TRANSFER_BATCH_EVENT_HASH)
    batch_index = proof.get("batch_index")
    if is_batch and not (profile["batch_allowed"] and isinstance(batch_index, int)):
        return False
    if is_single and batch_index is not None:
        return False
    if not (is_single or is_batch):
        return False
    token_id = proof.get("token_id")
    receipt_hash = proof.get("receipt_hash")
    expected_ref = erc1155_payment_reference(receipt_hash, profile, token_id) if isinstance(receipt_hash, str) and isinstance(token_id, str) else ""
    checks = [
        proof.get("chain_id") == profile["chain_id"],
        str(proof.get("token_address", "")).lower() == profile["token_address"].lower(),
        token_id in profile["accepted_token_ids"],
        units_in_range(str(proof.get("units", "")), profile),
        str(proof.get("payee", "")).lower() == profile["payee"].lower(),
        isinstance(proof.get("payer"), str) and bool(proof.get("payer")),
        isinstance(proof.get("tx_hash"), str) and bool(proof.get("tx_hash")),
        isinstance(proof.get("block_number"), int),
        isinstance(receipt_hash, str) and bool(receipt_hash),
        proof.get("payment_reference") == expected_ref,
    ]
    return all(checks)


def payment_verify(profile_path: str, proof_path: str) -> bool:
    profile = load_json(profile_path)
    proof = load_json(proof_path)
    if adapter(profile) == "erc20":
        return erc20_payment_verify(profile, proof)
    if adapter(profile) == "erc1155":
        return erc1155_payment_verify(profile, proof)
    return False


def log_append(receipt_path: str) -> dict[str, Any] | None:
    receipt = load_json(receipt_path)
    if not isinstance(receipt, dict) or receipt.get("authority") is not False:
        return None
    receipt_id = sha256_hex(receipt)
    witness_core = {"receipt_id": receipt_id, "log_index": 0, "merkle_root": receipt_id}
    return {**witness_core, "witness_hash": sha256_hex(witness_core)}


def log_verify(expected_hash: str, proof_path: str) -> bool:
    proof = load_json(proof_path)
    if not isinstance(proof, dict):
        return False
    required = ("receipt_id", "log_index", "merkle_root", "witness_hash")
    if not all(key in proof for key in required) or proof.get("receipt_id") != expected_hash:
        return False
    witness_core = {"receipt_id": proof.get("receipt_id"), "log_index": proof.get("log_index"), "merkle_root": proof.get("merkle_root")}
    return proof.get("witness_hash") == sha256_hex(witness_core)


def authority_footer(valid: bool, status: str, timestamp: int, collapsed: bool) -> str:
    return f"authority: {str(valid).lower()} | status: {status} | ts: {timestamp} | collapsed: {str(collapsed).lower()}"


def authority_object(valid: bool, status: str, timestamp: int, collapsed: bool) -> dict[str, Any]:
    return {"valid": valid, "status": status, "timestamp": timestamp, "collapsed": collapsed}


def render_hash_bytes(rendered: str) -> str:
    stripped = ANSI_RE.sub("", rendered).encode("utf-8")
    try:
        import blake3  # type: ignore
        return blake3.blake3(stripped).hexdigest()
    except Exception:
        return hashlib.blake2b(stripped, digest_size=32).hexdigest()


def receipt_render(witness_path: str, output_format: str = "term", verbose: bool = False, trace: bool = False, with_hash: bool = False, verify_hash: str | None = None) -> tuple[int, str]:
    try:
        witness = load_json(witness_path)
    except Exception:
        footer = authority_footer(False, "failed", 0, False)
        return 2, footer
    if not isinstance(witness, dict):
        return 2, authority_footer(False, "failed", 0, False)

    adapter_type = witness.get("adapter") or witness.get("asset_standard")
    if adapter_type not in SUPPORTED_RENDER_ADAPTERS:
        return 3, authority_footer(False, "failed", int(witness.get("ts", 0) or 0), False)

    token_ids = witness.get("token_ids", [])
    collapsed = bool(witness.get("collapsed", isinstance(token_ids, list) and len(token_ids) > 3))
    status = str(witness.get("status", "confirmed"))
    valid = bool(witness.get("authority", {}).get("valid", status == "confirmed")) if isinstance(witness.get("authority"), dict) else bool(witness.get("authority", status == "confirmed"))
    ts = int(witness.get("ts", witness.get("timestamp", 1741449600)))
    if status not in {"pending", "confirmed", "failed"}:
        status = "failed"
        valid = False
    if witness.get("proof_valid") is False:
        status = "failed"
        valid = False

    receipt_id = str(witness.get("receipt_id", ""))
    payment_reference = str(witness.get("payment_reference", ""))
    witness_hash = str(witness.get("witness_hash", ""))
    merkle_root = str(witness.get("merkle_root", ""))
    log_index = witness.get("log_index", 0)

    if trace:
        rendered = json.dumps(witness, sort_keys=True, separators=(",", ":"))
    elif output_format == "jsonl":
        rendered_obj = {
            "adapter": {"type": adapter_type, "payload": witness.get("adapter_payload", {})},
            "authority": authority_object(valid, status, ts, collapsed),
            "payment_adapter_block": witness.get("payment_adapter_block", {}),
            "proof_summary": witness.get("proof_summary", {}),
            "receipt_core": {"receipt_id": receipt_id, "payment_reference": payment_reference, "status": status},
            "witness": {"witness_hash": witness_hash, "merkle_root": merkle_root, "log_index": log_index},
        }
        rendered = json.dumps(rendered_obj, sort_keys=True, separators=(",", ":"))
    elif output_format == "md":
        rendered = "\n".join([
            "| asset_standard | receipt_id | payment_reference | status |",
            "|---|---|---|---|",
            f"| {adapter_type} | {receipt_id} | {payment_reference} | {status} |",
            "",
            "| authority | status | ts | collapsed |",
            "|---|---:|---:|---|",
            f"| {str(valid).lower()} | {status} | {ts} | {str(collapsed).lower()} |",
            "",
            "| witness_hash | merkle_root | log_index |",
            "|---|---|---:|",
            f"| {witness_hash} | {merkle_root} | {log_index} |",
        ])
    else:
        rendered = "\n".join([
            f"asset_standard: {adapter_type} | receipt_id: {receipt_id} | payment_reference: {payment_reference} | status: {status}",
            f"adapter: {adapter_type} | payload: {json.dumps(witness.get('adapter_payload', {}), sort_keys=True, separators=(',', ':'))}",
            f"witness_hash: {witness_hash} | merkle_root: {merkle_root} | log_index: {log_index}",
            authority_footer(valid, status, ts, collapsed),
        ])

    if with_hash or verify_hash:
        rh = render_hash_bytes(rendered)
        if output_format == "jsonl" and not trace:
            obj = json.loads(rendered)
            obj["render_hash"] = rh
            rendered = json.dumps(obj, sort_keys=True, separators=(",", ":"))
        else:
            rendered = rendered + f"\nrender_hash: {rh}"
        if verify_hash and verify_hash != rh:
            return 1, rendered
    return 0, rendered


def usage() -> int:
    print(
        "usage: tools/alms.py verify <receipt.json> | "
        "payment-bind <receipt.json> <profile.json> | "
        "payment-verify <profile.json> <proof.json> | "
        "payment-refresh <profile.json> | "
        "log-append <receipt.json> | "
        "log-verify --hash <receipt_hash> --proof <proof.json> | "
        "receipt-render <witness.json> [--format=term|jsonl|md] [--verbose] [--trace] [--with-render-hash] [--verify <hash>]",
        file=sys.stderr,
    )
    return 2


def main() -> int:
    if len(sys.argv) < 2:
        return usage()
    cmd = sys.argv[1]
    if cmd == "verify" and len(sys.argv) == 3:
        ok = verify(sys.argv[2]); print("VALID" if ok else "INVALID"); return 0 if ok else 1
    if cmd == "payment-bind" and len(sys.argv) == 4:
        receipt = load_json(sys.argv[2]); profile = load_json(sys.argv[3])
        if not isinstance(receipt, dict) or not profile_ok(profile): print("INVALID"); return 1
        receipt_hash = receipt.get("receipt_hash")
        if not isinstance(receipt_hash, str) or not receipt_hash: print("INVALID"); return 1
        print(payment_reference(receipt_hash, profile)); return 0
    if cmd == "payment-verify" and len(sys.argv) == 4:
        ok = payment_verify(sys.argv[2], sys.argv[3]); print("VALID_PAYMENT" if ok else "INVALID_PAYMENT"); return 0 if ok else 1
    if cmd == "payment-refresh" and len(sys.argv) == 3:
        loaded_profile = load_json(sys.argv[2]); ok = isinstance(loaded_profile, dict) and profile_ok(loaded_profile)
        print("PROFILE_VALID" if ok else "PROFILE_INVALID"); return 0 if ok else 1
    if cmd == "log-append" and len(sys.argv) == 3:
        witness = log_append(sys.argv[2])
        if witness is None: print("INVALID_LOG_ENTRY"); return 1
        print(json.dumps(witness, sort_keys=True, separators=(",", ":"))); return 0
    if cmd == "log-verify" and len(sys.argv) == 6 and sys.argv[2] == "--hash" and sys.argv[4] == "--proof":
        ok = log_verify(sys.argv[3], sys.argv[5]); print("VALID_LOG_PROOF" if ok else "INVALID_LOG_PROOF"); return 0 if ok else 1
    if cmd == "receipt-render" and len(sys.argv) >= 3:
        output_format = "term"; verbose = False; trace = False; with_hash = False; verify_hash = None
        args = sys.argv[3:]
        i = 0
        while i < len(args):
            arg = args[i]
            if arg.startswith("--format="): output_format = arg.split("=", 1)[1]
            elif arg == "--format" and i + 1 < len(args): i += 1; output_format = args[i]
            elif arg == "--verbose": verbose = True
            elif arg == "--trace": trace = True
            elif arg == "--with-render-hash": with_hash = True
            elif arg == "--verify" and i + 1 < len(args): i += 1; verify_hash = args[i]
            else: return usage()
            i += 1
        if output_format not in {"term", "jsonl", "md"}: return 3
        code, rendered = receipt_render(sys.argv[2], output_format, verbose, trace, with_hash, verify_hash)
        print(rendered); return code
    return usage()


if __name__ == "__main__":
    raise SystemExit(main())
