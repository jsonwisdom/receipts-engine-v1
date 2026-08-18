#!/usr/bin/env python3
"""Build a draft candidate Store Release root from a current Store checkout.

This is deliberately non-promoting. It reuses the v0.1 declared leaf topology but
uses the current raw Store bytes and current Git blob IDs. It never writes to the
Store repository, signs, broadcasts, pays, deploys, or promotes a release.

If a caller supplies a changed-path list and a changed commercial Store path is
outside the v0.1 declared leaf set, the tool reports HOLD_TOPOLOGY_CHANGE rather
than silently pretending the fixed 13-leaf topology still covers the new state.
Store automation code is explicitly outside the commercial-state root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ALGORITHM = "RECEIPTS_ENGINE_DOMAIN_SEPARATED_SHA256_V1"
BASELINE_ROOT = "10c51683dc14f12128c472ecdda4e6a459ea6f6561ee6ec9f8459732d6e7376a"
NON_COMMERCIAL_PREFIXES = ("store/automation/",)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def leaf_hash(content_sha256: str) -> str:
    return sha256_hex(b"\x00" + b"v1" + content_sha256.encode("ascii"))


def parent_hash(left: str, right: str) -> str:
    return sha256_hex(b"\x01" + left.encode("ascii") + right.encode("ascii"))


def build_tree(leaves: list[str]) -> str:
    if not leaves:
        raise ValueError("no leaves")
    layer = leaves[:]
    while len(layer) > 1:
        nxt: list[str] = []
        for i in range(0, len(layer), 2):
            left = layer[i]
            right = layer[i + 1] if i + 1 < len(layer) else left
            nxt.append(parent_hash(left, right))
        layer = nxt
    return layer[0]


def git_head(repo: Path) -> str:
    return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()


def read_changed_paths(path: Path | None) -> list[str]:
    if path is None:
        return []
    return sorted({line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()})


def is_non_commercial(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in NON_COMMERCIAL_PREFIXES)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("store-release/sources/STORE_SOURCE_MANIFEST_V0_1.json"),
    )
    parser.add_argument("--changed-paths-file", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("merkle_algorithm", {}).get("id") != ALGORITHM:
        print("CANDIDATE_ROOT_STATUS=REJECT_ALGORITHM_MISMATCH", file=sys.stderr)
        return 1

    entries = sorted(manifest.get("leaves", []), key=lambda item: item["path"])
    declared_paths = [entry["path"] for entry in entries]
    declared_set = set(declared_paths)
    if len(declared_paths) != len(declared_set):
        print("CANDIDATE_ROOT_STATUS=REJECT_DUPLICATE_SOURCE_PATH", file=sys.stderr)
        return 1

    changed_paths = read_changed_paths(args.changed_paths_file)
    topology_unknown = sorted(
        path for path in changed_paths
        if path.startswith("store/")
        and not is_non_commercial(path)
        and path not in declared_set
    )

    leaf_records: list[dict[str, Any]] = []
    for entry in entries:
        rel = entry["path"]
        path = args.source_root / rel
        if not path.is_file():
            print(f"CANDIDATE_ROOT_STATUS=HOLD_MISSING_DECLARED_LEAF:{rel}", file=sys.stderr)
            return 2
        data = path.read_bytes()
        content_sha256 = sha256_hex(data)
        leaf_records.append(
            {
                "path": rel,
                "role": entry["role"],
                "git_blob_sha1": git_blob_sha1(data),
                "content_sha256": content_sha256,
                "leaf_hash": leaf_hash(content_sha256),
            }
        )

    root = build_tree([record["leaf_hash"] for record in leaf_records])
    head = git_head(args.source_root)
    result = {
        "candidate_type": "STORE_RELEASE_CANDIDATE_ROOT_V0_1",
        "algorithm": ALGORITHM,
        "source_repository": manifest["source_repository"],
        "source_ref": head,
        "declared_leaf_count": len(leaf_records),
        "candidate_merkle_root": root,
        "baseline_merkle_root": BASELINE_ROOT,
        "root_changed": root != BASELINE_ROOT,
        "changed_paths": changed_paths,
        "non_commercial_prefixes": list(NON_COMMERCIAL_PREFIXES),
        "topology_unknown_paths": topology_unknown,
        "promotion_performed": False,
        "merge_performed": False,
        "eas_attestation_broadcast": False,
        "signer_used": False,
        "payment_activated": False,
        "brand_promotion_performed": False,
        "authority_created": False,
        "leaves": leaf_records,
    }

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"STORE_SOURCE_REF={head}")
    print(f"CANDIDATE_STORE_RELEASE_MERKLE_ROOT={root}")
    print(f"BASELINE_STORE_RELEASE_MERKLE_ROOT={BASELINE_ROOT}")
    print(f"ROOT_CHANGED={str(root != BASELINE_ROOT).upper()}")
    print("AUTO_MERGE=FALSE")
    print("AUTO_EAS_BROADCAST=FALSE")
    print("AUTO_SIGN=FALSE")
    print("AUTO_PAYMENT_ACTIVATION=FALSE")
    print("AUTO_BRAND_PROMOTION=FALSE")
    print("AUTHORITY_CREATED=FALSE")

    if topology_unknown:
        print("CANDIDATE_ROOT_STATUS=HOLD_TOPOLOGY_CHANGE")
        for path in topology_unknown:
            print(f"TOPOLOGY_UNKNOWN_PATH={path}")
        return 2

    print("CANDIDATE_ROOT_STATUS=PASS_DRAFT_ONLY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
