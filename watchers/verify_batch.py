#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path
from eth_hash.auto import keccak

def fail(code: int, msg: str) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)

def hex32_to_bytes(x: str) -> bytes:
    x = x.lower()
    if not x.startswith("0x") or len(x) != 66:
        fail(15, f"invalid bytes32: {x}")
    return bytes.fromhex(x[2:])

def node(a: str, b: str) -> str:
    a = a.lower()
    b = b.lower()
    left, right = sorted([hex32_to_bytes(a), hex32_to_bytes(b)])
    return "0x" + keccak(b"\x01" + left + right).hex()

def merkle_root(leaves: list[str]) -> str:
    if not leaves:
        fail(15, "no leaves")
    level = sorted([x.lower() for x in leaves])
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        level = [node(level[i], level[i + 1]) for i in range(0, len(level), 2)]
    return level[0]

def derive_batch_id(leaves: list[str], root: str) -> str:
    normalized = sorted([x.lower() for x in leaves])
    preimage = (
        b"".join(hex32_to_bytes(x) for x in normalized)
        + hex32_to_bytes(root)
        + len(normalized).to_bytes(32, "big")
    )
    return "0x" + keccak(preimage).hex()

def receipt_hash(receipt: dict) -> str:
    pre = dict(receipt)
    pre["receipt_hash"] = None
    canon = json.dumps(pre, sort_keys=True, separators=(",", ":")).encode()
    return "0x" + keccak(canon).hex()

def main() -> None:
    if len(sys.argv) != 2:
        fail(2, "usage: verify_batch.py receipt.json")
    receipt = json.loads(Path(sys.argv[1]).read_text())
    required = ["version", "batch_id", "merkle_root", "receipt_hash", "leaf_count", "leaves", "provenance"]
    missing = [k for k in required if k not in receipt]
    if missing:
        fail(15, f"missing required fields: {','.join(missing)}")
    leaves = receipt["leaves"]
    if not isinstance(leaves, list) or len(leaves) == 0:
        fail(15, "invalid leaves")
    if receipt["leaf_count"] != len(leaves):
        fail(15, "leaf_count mismatch")
    root = merkle_root(leaves)
    if root.lower() != receipt["merkle_root"].lower():
        fail(13, "MERKLE_ROOT_MISMATCH")
    batch_id = derive_batch_id(leaves, root)
    if batch_id.lower() != receipt["batch_id"].lower():
        fail(14, "BATCH_ID_MISMATCH")
    rh = receipt_hash(receipt)
    if rh.lower() != str(receipt["receipt_hash"]).lower():
        fail(12, "RECEIPT_HASH_MISMATCH")
    print(json.dumps({
        "status": "pass",
        "merkle_root": root,
        "batch_id": batch_id,
        "receipt_hash": rh
    }, indent=2))

if __name__ == "__main__":
    main()
