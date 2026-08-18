#!/usr/bin/env python3
"""Fail-closed verification for Store Release Merkle v0.1."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD_PATH = HERE / "build_store_release_root.py"
SPEC = importlib.util.spec_from_file_location("store_release_builder", BUILD_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load builder")
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)

EXPECTED_SOURCE_REF = "de9e1dde3bda66f697671abf94f932e58a577066"
EXPECTED_MERCHANT_ID = "5624520187"
EXPECTED_LEAF_COUNT = 13
EXPECTED_POLICY_PATH = "store/money-machine/policy/JAY_ONLY_PROFIT_POLICY_V0_1.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify_source_semantics(source_root: Path, manifest: dict, claims: dict) -> None:
    require(manifest["source_ref"] == EXPECTED_SOURCE_REF, "unexpected source ref")
    require(manifest["merchant_center_id"] == EXPECTED_MERCHANT_ID, "merchant id mismatch")
    require(manifest["leaf_count"] == EXPECTED_LEAF_COUNT, "leaf count mismatch")
    require(manifest["authority_created"] is False, "manifest authority drift")
    require(manifest["brand_promotion_performed"] is False, "brand candidate silently promoted")

    paths = [entry["path"] for entry in manifest["leaves"]]
    require(len(paths) == len(set(paths)), "duplicate path in source manifest")
    require(EXPECTED_POLICY_PATH in paths, "profit policy is not committed by the root")

    catalog = read_json(source_root / "store/catalog/catalog.json")
    require(catalog["merchant_center_id"] == EXPECTED_MERCHANT_ID, "catalog merchant id mismatch")
    require(catalog["production"]["checkout_live"] is False, "checkout silently live")
    require(catalog["production"]["payment_processor_live"] is False, "processor silently live")
    require(catalog["production"]["deployment_verified"] is False, "deployment silently verified")
    require(catalog["customer_reviews"]["google_generated_store_rating_verified"] is False, "rating silently verified")

    public_catalog = read_json(source_root / "store/public/catalog.json")
    require(public_catalog["production_deployment"] is False, "public catalog deployment drift")
    require(public_catalog["rating_verified"] is False, "public catalog rating drift")

    for rel in (
        "store/products/flywheel-of-wisdom/manifest.json",
        "store/products/receiptos-replay-proof-report/manifest.json",
    ):
        product = read_json(source_root / rel)
        require(product.get("payment_processor_live") is False, f"{rel}: processor drift")
        require(product.get("production_deployment") is False, f"{rel}: deployment drift")
        require(product.get("authority_created") is False, f"{rel}: authority drift")

    operator = read_json(source_root / "store/identity/jaywisdom.eth/operator.json")
    require(operator["wallet_control_verified_in_this_build"] is False, "wallet control silently promoted")
    require(operator["payment_authority"] is False, "payment authority silently promoted")
    require(operator["deployment_authority"] is False, "deployment authority silently promoted")
    require(operator["authority_created"] is False, "operator authority drift")

    release = read_json(source_root / "store/releases/store-v0.1-directory-first/release.json")
    require(release["payment_processor_live"] is False, "release processor drift")
    require(release["production_deployment"] is False, "release deployment drift")
    require(release["authority_created"] is False, "release authority drift")

    policy = read_json(source_root / EXPECTED_POLICY_PATH)
    require(policy["automatic_accounting"] is True, "automatic accounting missing")
    require(policy["automatic_payout"] is False, "automatic payout silently enabled")
    require(policy["other_profit_share_bps"] == 0, "non-Jay project profit share present")
    require(len(policy["beneficiaries"]) == 1, "beneficiary count drift")
    beneficiary = policy["beneficiaries"][0]
    require(beneficiary["id"] == "JAY", "Jay beneficiary missing")
    require(beneficiary["profit_share_bps"] == 10000, "Jay project profit share drift")
    require(beneficiary["payout_address_control_verified"] is False, "wallet control silently verified")
    require(policy["authority_created"] is False, "profit policy authority drift")

    require(claims["source_ref"] == EXPECTED_SOURCE_REF, "claims source mismatch")
    require(claims["authority_created"] is False, "claims authority drift")
    claim_map = {claim["id"]: claim["value"] for claim in claims["claims"]}
    require(claim_map["checkout-live"] is False, "claims checkout drift")
    require(claim_map["automatic-profit-accounting"] is True, "claims accounting drift")
    require(claim_map["automatic-payout"] is False, "claims payout drift")
    require(claim_map["jay-profit-share-bps"] == 10000, "claims Jay share drift")
    require(claim_map["authority-created"] is False, "claims authority drift")


def verify_generated(generated_dir: Path, expected_root: str) -> None:
    tree = read_json(generated_dir / "tree.json")
    receipt = read_json(generated_dir / "store-release-receipt.json")
    eas = read_json(generated_dir / "eas-payload.json")

    require(tree["merkle_root"] == expected_root, "generated tree root mismatch")
    require(tree["leaf_count"] == EXPECTED_LEAF_COUNT, "generated leaf count mismatch")
    require(tree["authority_created"] is False, "tree authority drift")

    require(receipt["merkle_root"] == expected_root, "receipt root mismatch")
    require(receipt["eas_attestation_broadcast"] is False, "receipt claims EAS broadcast")
    require(receipt["signer_used"] is False, "receipt claims signer use")
    require(receipt["authority_none"] is True, "authorityNone drift")
    require(receipt["authority_created"] is False, "receipt authority drift")

    require(eas["broadcast"] is False, "EAS payload broadcast drift")
    require(eas["signer_used"] is False, "EAS signer drift")
    require(eas["data"]["authorityNone"] is True, "EAS authorityNone drift")
    require(eas["data"]["bundleRoot"] == f"sha256:{expected_root}", "EAS bundleRoot mismatch")
    require(eas["schema_number"] == 1618, "EAS schema number mismatch")
    require(eas["schema_uid"] == builder.EAS_SCHEMA_UID, "EAS schema UID mismatch")
    require(eas["schema_creator_rail"] == builder.EAS_SCHEMA_CREATOR_RAIL, "EAS creator rail mismatch")


def copy_declared_sources(source_root: Path, manifest: dict, dst: Path) -> None:
    for entry in manifest["leaves"]:
        src = source_root / entry["path"]
        out = dst / entry["path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, out)


def verify_fail_closed_vectors(source_root: Path, manifest_path: Path, claims_path: Path, baseline_root: str) -> None:
    manifest = read_json(manifest_path)

    # Vector 1: source-list order is presentation only; path sorting keeps the same root.
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        reversed_manifest = dict(manifest)
        reversed_manifest["leaves"] = list(reversed(manifest["leaves"]))
        reversed_path = td_path / "manifest.json"
        reversed_path.write_text(json.dumps(reversed_manifest, indent=2) + "\n", encoding="utf-8")
        out = td_path / "out"
        result = builder.build(source_root, reversed_path, claims_path, out)
        require(result["tree"]["merkle_root"] == baseline_root, "path-order invariance failed")

    # Vector 2: one-byte source mutation must fail the Git blob gate before root promotion.
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        copy_declared_sources(source_root, manifest, td_path / "source")
        target = td_path / "source/store/public/catalog.json"
        target.write_bytes(target.read_bytes() + b" ")
        try:
            builder.build(td_path / "source", manifest_path, claims_path, td_path / "out")
        except ValueError as exc:
            require("git blob mismatch" in str(exc), "mutation failed for wrong reason")
        else:
            raise AssertionError("mutated source was accepted")

    # Vector 3: duplicate source path must fail closed.
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        bad = dict(manifest)
        bad["leaves"] = manifest["leaves"] + [manifest["leaves"][0]]
        bad["leaf_count"] = len(bad["leaves"])
        bad_path = td_path / "bad.json"
        bad_path.write_text(json.dumps(bad, indent=2) + "\n", encoding="utf-8")
        try:
            builder.build(source_root, bad_path, claims_path, td_path / "out")
        except ValueError as exc:
            require("duplicate source path" in str(exc), "duplicate failed for wrong reason")
        else:
            raise AssertionError("duplicate source path was accepted")


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
    parser.add_argument("--generated-dir", type=Path, default=Path("store-release/_generated"))
    args = parser.parse_args()

    manifest = read_json(args.manifest)
    claims = read_json(args.claims)
    verify_source_semantics(args.source_root, manifest, claims)

    with tempfile.TemporaryDirectory() as td:
        replay_dir = Path(td) / "replay"
        replay = builder.build(args.source_root, args.manifest, args.claims, replay_dir)
        root = replay["tree"]["merkle_root"]
        verify_generated(replay_dir, root)
        if args.generated_dir.exists():
            verify_generated(args.generated_dir, root)
        verify_fail_closed_vectors(args.source_root, args.manifest, args.claims, root)

    print("STORE_RELEASE_REPLAY=PASS")
    print("MERKLE_INCLUSION_WORLD_TRUE=FALSE")
    print("EAS_ATTESTATION_BROADCAST=FALSE")
    print("SIGNER_USED=FALSE")
    print("PAYMENT_ACTIVATED=FALSE")
    print("AUTHORITY_CREATED=FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
