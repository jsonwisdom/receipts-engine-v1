#!/usr/bin/env python3
"""Independent third-party verifier for Store Release Merkle v0.1.

Stdlib only. This script intentionally does not import the production Store Release
builder. It reads the committed source manifest and claims fixture, verifies the
exact Store Git commit and declared Git blob IDs, then independently rebuilds the
Receipt Engine v1 domain-separated Merkle root and Receipt Core hash.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

EXPECTED_ROOT = "10c51683dc14f12128c472ecdda4e6a459ea6f6561ee6ec9f8459732d6e7376a"
EXPECTED_RECEIPT_CORE = "aba9765c769f9e9d3d05dd472dd0a3812d62e38bcab3ea0e5e761b0252a46706"
ALGORITHM = "RECEIPTS_ENGINE_DOMAIN_SEPARATED_SHA256_V1"
POLICY_PATH = "store/money-machine/policy/JAY_ONLY_PROFIT_POLICY_V0_1.json"


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def leaf_hash(content_sha256: str) -> str:
    return sha256_hex(b"\x00" + b"v1" + content_sha256.encode("ascii"))


def parent_hash(left: str, right: str) -> str:
    return sha256_hex(b"\x01" + left.encode("ascii") + right.encode("ascii"))


def build_tree(leaf_hexes: list[str]) -> str:
    if not leaf_hexes:
        raise ValueError("no leaves")
    layer = leaf_hexes[:]
    while len(layer) > 1:
        nxt: list[str] = []
        for i in range(0, len(layer), 2):
            left = layer[i]
            right = layer[i + 1] if i + 1 < len(layer) else left
            nxt.append(parent_hash(left, right))
        layer = nxt
    return layer[0]


def git_head(repo: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def verify(args: argparse.Namespace) -> int:
    manifest_raw = args.manifest.read_bytes()
    manifest = json.loads(manifest_raw)
    claims = json.loads(args.claims.read_text(encoding="utf-8"))
    build_receipt = json.loads(args.build_receipt.read_text(encoding="utf-8"))

    if manifest.get("merkle_algorithm", {}).get("id") != ALGORITHM:
        return fail("algorithm mismatch")
    if manifest.get("leaf_count") != len(manifest.get("leaves", [])):
        return fail("manifest leaf_count mismatch")

    declared_paths = [entry["path"] for entry in manifest["leaves"]]
    if len(declared_paths) != len(set(declared_paths)):
        return fail("duplicate source path")

    observed_head = git_head(args.source_root)
    expected_head = manifest["source_ref"]
    if observed_head != expected_head:
        return fail(f"Store HEAD mismatch: expected {expected_head}, got {observed_head}")

    leaf_records: list[dict[str, str]] = []
    for entry in sorted(manifest["leaves"], key=lambda item: item["path"]):
        rel = entry["path"]
        path = args.source_root / rel
        if not path.is_file():
            return fail(f"missing source leaf: {rel}")
        data = path.read_bytes()
        observed_blob = git_blob_sha1(data)
        if observed_blob != entry["git_blob_sha1"]:
            return fail(
                f"Git blob mismatch for {rel}: expected {entry['git_blob_sha1']}, got {observed_blob}"
            )
        content_sha256 = sha256_hex(data)
        leaf_records.append(
            {
                "path": rel,
                "content_sha256": content_sha256,
                "leaf_hash": leaf_hash(content_sha256),
            }
        )

    root = build_tree([record["leaf_hash"] for record in leaf_records])
    if root != EXPECTED_ROOT:
        return fail(f"Merkle root mismatch: expected {EXPECTED_ROOT}, got {root}")

    source_manifest_sha256 = sha256_hex(manifest_raw)
    claim_graph_sha256 = sha256_hex(canonical_json_bytes(claims))
    claims_count = len(claims.get("claims", []))
    policy_record = next((r for r in leaf_records if r["path"] == POLICY_PATH), None)
    if policy_record is None:
        return fail("profit policy leaf missing")

    receipt_core = {
        "release_id": manifest["release_id"],
        "source_repository": manifest["source_repository"],
        "source_ref": manifest["source_ref"],
        "source_manifest_sha256": source_manifest_sha256,
        "claim_graph_sha256": claim_graph_sha256,
        "claims_count": claims_count,
        "policy_sha256": policy_record["content_sha256"],
        "leaf_count": len(leaf_records),
        "merkle_root": root,
        "algorithm": ALGORITHM,
        "authority_none": True,
        "version": "store-release-v0.1",
    }
    receipt_core_sha256 = sha256_hex(canonical_json_bytes(receipt_core))
    if receipt_core_sha256 != EXPECTED_RECEIPT_CORE:
        return fail(
            f"Receipt Core mismatch: expected {EXPECTED_RECEIPT_CORE}, got {receipt_core_sha256}"
        )

    receipt_checks = {
        "store_release_merkle_root": root,
        "receipt_core_sha256": receipt_core_sha256,
        "source_ref": expected_head,
        "source_leaf_count": len(leaf_records),
        "eas_attestation_broadcast": False,
        "signer_used": False,
        "payment_activated": False,
        "wallet_mutation": False,
        "authority_created": False,
        "merge_authorized": False,
    }
    for key, expected in receipt_checks.items():
        if build_receipt.get(key) != expected:
            return fail(
                f"Build Receipt 0001 mismatch for {key}: expected {expected!r}, got {build_receipt.get(key)!r}"
            )

    print("STORE_RELEASE_THIRD_PARTY_VERIFICATION=PASS")
    print(f"STORE_SOURCE_REF={expected_head}")
    print(f"SOURCE_LEAF_COUNT={len(leaf_records)}")
    print(f"STORE_RELEASE_MERKLE_ROOT={root}")
    print(f"RECEIPT_CORE_SHA256={receipt_core_sha256}")
    print(f"SOURCE_MANIFEST_SHA256={source_manifest_sha256}")
    print(f"CLAIM_GRAPH_SHA256={claim_graph_sha256}")
    print(f"POLICY_SHA256={policy_record['content_sha256']}")
    print("RECORDED_EAS_ATTESTATION_BROADCAST=FALSE")
    print("RECORDED_SIGNER_USED=FALSE")
    print("RECORDED_AUTHORITY_CREATED=FALSE")
    print("MERKLE_INCLUSION_WORLD_TRUE=FALSE")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("store-release/sources/STORE_SOURCE_MANIFEST_V0_1.json"),
    )
    parser.add_argument(
        "--claims",
        type=Path,
        default=Path("store-release/fixtures/STORE_CLAIMS_V0_1.json"),
    )
    parser.add_argument(
        "--build-receipt",
        type=Path,
        default=Path("store-release/receipts/BUILD_RECEIPT_0001.json"),
    )
    return verify(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
