#!/usr/bin/env node
import fs from "node:fs";

const suitePath = process.argv[2] ?? "specs/trust_membrane_validator_vectors_v1.json";
const suite = JSON.parse(fs.readFileSync(suitePath, "utf8"));

function outcome(failedStage, primaryDiagnostic, terminal) {
  return { failedStage, primaryDiagnostic, terminal };
}

function evaluate(facts) {
  const f = {
    structureValid: true,
    artifactValid: true,
    cryptoValid: true,
    bundleSignatureValid: true,
    bundleSequenceValid: true,
    housingBundleValid: true,
    keyResolvable: true,
    transitionKind: "none",
    leafSuccessionValid: false,
    rootSuccessionCryptoValid: true,
    keyStatus: "active",
    historicalOrder: "not_applicable",
    rootWitnessSatisfied: true,
    localRepinApproved: true,
    ...facts,
  };

  if (!f.structureValid) return outcome("1_STRUCTURE", "DELTA_STRUCTURAL", "HOLD");
  if (!f.artifactValid) return outcome("2_ARTIFACT", "DELTA_ARTIFACT", "HOLD");
  if (!f.cryptoValid) return outcome("3_CRYPTO", "DELTA_CRYPTO", "HOLD");

  if (!f.bundleSignatureValid) return outcome("4A_BUNDLE_CHAIN_VALIDITY", "DELTA_CHAIN_SIGNATURE", "HOLD");
  if (!f.bundleSequenceValid) return outcome("4A_BUNDLE_CHAIN_VALIDITY", "DELTA_CHAIN_SEQUENCE", "HOLD");
  if (!f.housingBundleValid) return outcome("4A_BUNDLE_CHAIN_VALIDITY", "DELTA_CHAIN_HOUSING", "HOLD");

  if (!f.keyResolvable) return outcome("4B_KEY_RESOLUTION", "DELTA_TRUST", "HOLD");

  if (f.transitionKind === "root" && !f.rootSuccessionCryptoValid) {
    return outcome("5_TRANSITION_EVIDENCE", "DELTA_ROOT_CRYPTO", "HOLD");
  }

  if (f.keyStatus === "revoked") {
    if (f.historicalOrder === "proven_before_affected_window") {
      return outcome(null, "DELTA_REVOCATION", "MATCH");
    }
    return outcome("6_HISTORICAL_OR_WITNESS_EVIDENCE", "DELTA_TIME", "HOLD");
  }

  if (f.transitionKind === "root" && !f.rootWitnessSatisfied) {
    return outcome("6_HISTORICAL_OR_WITNESS_EVIDENCE", "DELTA_ROOT_UNWITNESSED", "HOLD_PENDING_LOCAL_TRUST");
  }

  if (f.transitionKind === "root" && !f.localRepinApproved) {
    return outcome("7_LOCAL_POLICY", "DELTA_ROOT_UNPINNED", "HOLD_PENDING_LOCAL_TRUST");
  }

  if (f.transitionKind === "leaf" && f.leafSuccessionValid) {
    return outcome(null, "DELTA_SUCCESSION", "MATCH");
  }

  return outcome(null, "MATCH", "MATCH");
}

const results = [];
let failed = false;
for (const vector of suite.vectors) {
  const actual = evaluate(vector.facts ?? {});
  if (JSON.stringify(actual) !== JSON.stringify(vector.expected)) {
    failed = true;
    console.error(`${vector.id}: expected ${JSON.stringify(vector.expected)} got ${JSON.stringify(actual)}`);
  }
  results.push(actual);
}

process.stdout.write(JSON.stringify(results) + "\n");
if (failed) process.exitCode = 1;
