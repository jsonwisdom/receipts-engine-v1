#!/usr/bin/env python3
import json
import sys

suite_path = sys.argv[1] if len(sys.argv) > 1 else "specs/trust_membrane_validator_vectors_v1.json"
with open(suite_path, "r", encoding="utf-8") as fh:
    suite = json.load(fh)


def outcome(failed_stage, primary_diagnostic, terminal):
    return {
        "failedStage": failed_stage,
        "primaryDiagnostic": primary_diagnostic,
        "terminal": terminal,
    }


def evaluate(facts):
    f = {
        "structureValid": True,
        "artifactValid": True,
        "cryptoValid": True,
        "bundleSignatureValid": True,
        "bundleSequenceValid": True,
        "housingBundleValid": True,
        "keyResolvable": True,
        "transitionKind": "none",
        "leafSuccessionValid": False,
        "rootSuccessionCryptoValid": True,
        "keyStatus": "active",
        "historicalOrder": "not_applicable",
        "rootWitnessSatisfied": True,
        "localRepinApproved": True,
    }
    f.update(facts or {})

    if not f["structureValid"]:
        return outcome("1_STRUCTURE", "DELTA_STRUCTURAL", "HOLD")
    if not f["artifactValid"]:
        return outcome("2_ARTIFACT", "DELTA_ARTIFACT", "HOLD")
    if not f["cryptoValid"]:
        return outcome("3_CRYPTO", "DELTA_CRYPTO", "HOLD")

    if not f["bundleSignatureValid"]:
        return outcome("4A_BUNDLE_CHAIN_VALIDITY", "DELTA_CHAIN_SIGNATURE", "HOLD")
    if not f["bundleSequenceValid"]:
        return outcome("4A_BUNDLE_CHAIN_VALIDITY", "DELTA_CHAIN_SEQUENCE", "HOLD")
    if not f["housingBundleValid"]:
        return outcome("4A_BUNDLE_CHAIN_VALIDITY", "DELTA_CHAIN_HOUSING", "HOLD")

    if not f["keyResolvable"]:
        return outcome("4B_KEY_RESOLUTION", "DELTA_TRUST", "HOLD")

    if f["transitionKind"] == "root" and not f["rootSuccessionCryptoValid"]:
        return outcome("5_TRANSITION_EVIDENCE", "DELTA_ROOT_CRYPTO", "HOLD")

    if f["keyStatus"] == "revoked":
        if f["historicalOrder"] == "proven_before_affected_window":
            return outcome(None, "DELTA_REVOCATION", "MATCH")
        return outcome("6_HISTORICAL_OR_WITNESS_EVIDENCE", "DELTA_TIME", "HOLD")

    if f["transitionKind"] == "root" and not f["rootWitnessSatisfied"]:
        return outcome(
            "6_HISTORICAL_OR_WITNESS_EVIDENCE",
            "DELTA_ROOT_UNWITNESSED",
            "HOLD_PENDING_LOCAL_TRUST",
        )

    if f["transitionKind"] == "root" and not f["localRepinApproved"]:
        return outcome("7_LOCAL_POLICY", "DELTA_ROOT_UNPINNED", "HOLD_PENDING_LOCAL_TRUST")

    if f["transitionKind"] == "leaf" and f["leafSuccessionValid"]:
        return outcome(None, "DELTA_SUCCESSION", "MATCH")

    return outcome(None, "MATCH", "MATCH")


results = []
failed = False
for vector in suite["vectors"]:
    actual = evaluate(vector.get("facts", {}))
    if actual != vector["expected"]:
        failed = True
        print(
            f"{vector['id']}: expected {json.dumps(vector['expected'], separators=(',', ':'))} "
            f"got {json.dumps(actual, separators=(',', ':'))}",
            file=sys.stderr,
        )
    results.append(actual)

sys.stdout.write(json.dumps(results, separators=(",", ":")) + "\n")
if failed:
    raise SystemExit(1)
