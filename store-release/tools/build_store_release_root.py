#!/usr/bin/env python3
"""Build Jay's American Storefront release Merkle root deterministically.

Stdlib only. This tool reads an exact checked-out storefront snapshot, verifies
its declared Git blob IDs, computes Receipt Engine v1 domain-separated leaves,
and emits a release receipt plus an unsigned EAS payload. It never signs or
broadcasts a transaction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ALGORITHM = "RECEIPTS_ENGINE_DOMAIN_SEPARATED_SHA256_V1"
POLICY_PATH = "store/money-machine/policy/JAY_ONLY_PROFIT_POLICY_V0_1.json"
EAS_SCHEMA_STRING = (
    "string receiptId,string artifactHash,string claimGraphHash,uint256 claimsCount,"
    "string receiptCoreHash,bool authorityNone,string policyHash,string bundleRoot,string version"
)
EAS_SCHEMA_UID = "0xa5b0d2dd5470542a119d50eba19898f50e1f77591f01d4fec4c6f3075054aa11"
EAS_SCHEMA_CREATOR_RAIL = "0xC345B26094c63C69222Ee775189a3d3eaead5a84"


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()  # Git object identity, not a security claim.


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def leaf_hash(content_sha256: str) -> str:
    return sha256_hex(b"\x00" + b"v1" + content_sha256.encode("ascii"))


def parent_hash(left: str, right: str) -> str:
    return sha256_hex(b"\x01" + left.encode("ascii") + right.encode("ascii"))


def build_tree(leaf_hexes: list[str]) -> tuple[str, list[list[str]]]:
    if not leaf_hexes:
        raise ValueError("no leaves")
    levels = [leaf_hexes[:]]
    layer = leaf_hexes[:]
    while len(layer) > 1:
        nxt: list[str] = []
        for i in range(0, len(layer), 2):
            left = layer[i]
            right = layer[i + 1] if i + 1 < len(layer) else left
            nxt.append(parent_hash(left, right))
        layer = nxt
        levels.append(layer[:])
    return layer[0], levels


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def build(source_root: Path, manifest_path: Path, claims_path: Path, out_dir: Path) -> dict[str, Any]:
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    claims = json.loads(claims_path.read_text(encoding="utf-8"))

    if manifest.get("merkle_algorithm", {}).get("id") != ALGORITHM:
        raise ValueError("algorithm mismatch")
    if manifest.get("leaf_count") != len(manifest.get("leaves", [])):
        raise ValueError("manifest leaf_count mismatch")

    declared_paths = [entry["path"] for entry in manifest["leaves"]]
    if len(declared_paths) != len(set(declared_paths)):
        raise ValueError("duplicate source path")

    leaf_records: list[dict[str, Any]] = []
    for entry in sorted(manifest["leaves"], key=lambda x: x["path"]):
        rel = entry["path"]
        path = source_root / rel
        if not path.is_file():
            raise FileNotFoundError(f"missing source leaf: {rel}")
        data = path.read_bytes()
        observed_blob = git_blob_sha1(data)
        expected_blob = entry["git_blob_sha1"]
        if observed_blob != expected_blob:
            raise ValueError(f"git blob mismatch for {rel}: expected {expected_blob}, got {observed_blob}")
        content_hash = sha256_hex(data)
        leaf_records.append(
            {
                "path": rel,
                "role": entry["role"],
                "git_blob_sha1": observed_blob,
                "content_sha256": content_hash,
                "leaf_hash": leaf_hash(content_hash),
            }
        )

    root, levels = build_tree([record["leaf_hash"] for record in leaf_records])
    source_manifest_sha256 = sha256_hex(manifest_raw)
    claim_graph_sha256 = sha256_hex(canonical_json_bytes(claims))
    claims_count = len(claims.get("claims", []))

    policy_record = next((r for r in leaf_records if r["path"] == POLICY_PATH), None)
    if policy_record is None:
        raise ValueError("profit policy leaf missing")
    policy_sha256 = policy_record["content_sha256"]

    receipt_core = {
        "release_id": manifest["release_id"],
        "source_repository": manifest["source_repository"],
        "source_ref": manifest["source_ref"],
        "source_manifest_sha256": source_manifest_sha256,
        "claim_graph_sha256": claim_graph_sha256,
        "claims_count": claims_count,
        "policy_sha256": policy_sha256,
        "leaf_count": len(leaf_records),
        "merkle_root": root,
        "algorithm": ALGORITHM,
        "authority_none": True,
        "version": "store-release-v0.1",
    }
    receipt_core_sha256 = sha256_hex(canonical_json_bytes(receipt_core))

    receipt = {
        "receipt_type": "STORE_RELEASE_MERKLE_RECEIPT_V0_1",
        "release_id": manifest["release_id"],
        "source_repository": manifest["source_repository"],
        "source_ref": manifest["source_ref"],
        "source_manifest_sha256": source_manifest_sha256,
        "claim_graph_sha256": claim_graph_sha256,
        "claims_count": claims_count,
        "policy_sha256": policy_sha256,
        "leaf_count": len(leaf_records),
        "merkle_root": root,
        "algorithm": ALGORITHM,
        "receipt_core_sha256": receipt_core_sha256,
        "authority_none": True,
        "eas_attestation_broadcast": False,
        "signer_used": False,
        "authority_created": False,
    }

    eas_payload = {
        "network": "base",
        "schema_number": 1618,
        "schema_uid": EAS_SCHEMA_UID,
        "schema_creator_rail": EAS_SCHEMA_CREATOR_RAIL,
        "schema_string": EAS_SCHEMA_STRING,
        "broadcast": False,
        "signer_used": False,
        "data": {
            "receiptId": f"store-release:sha256:{receipt_core_sha256}",
            "artifactHash": f"sha256:{source_manifest_sha256}",
            "claimGraphHash": f"sha256:{claim_graph_sha256}",
            "claimsCount": claims_count,
            "receiptCoreHash": f"sha256:{receipt_core_sha256}",
            "authorityNone": True,
            "policyHash": f"sha256:{policy_sha256}",
            "bundleRoot": f"sha256:{root}",
            "version": "store-release-v0.1",
        },
    }

    tree = {
        "algorithm": ALGORITHM,
        "source_repository": manifest["source_repository"],
        "source_ref": manifest["source_ref"],
        "leaf_count": len(leaf_records),
        "merkle_root": root,
        "leaves": leaf_records,
        "levels": levels,
        "authority_created": False,
    }

    write_json(out_dir / "leaves.json", leaf_records)
    write_json(out_dir / "tree.json", tree)
    write_json(out_dir / "store-release-receipt.json", receipt)
    write_json(out_dir / "eas-payload.json", eas_payload)

    print(f"STORE_RELEASE_MERKLE_ROOT={root}")
    print(f"RECEIPT_CORE_SHA256={receipt_core_sha256}")
    print(f"EAS_ATTESTATION_BROADCAST={str(eas_payload['broadcast']).upper()}")
    print("AUTHORITY_CREATED=FALSE")
    return {"tree": tree, "receipt": receipt, "eas_payload": eas_payload}


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
    parser.add_argument("--out-dir", type=Path, default=Path("store-release/_generated"))
    args = parser.parse_args()
    build(args.source_root, args.manifest, args.claims, args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
