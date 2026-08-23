# TRUST_MEMBRANE_VALIDATOR_CONFORMANCE_V1

Status: implementation candidate  
Authority created: false

## Purpose

Prove that `EVALUATION_MODE = SEQUENTIAL_SHORT_CIRCUIT` is implemented deterministically across independent validators.

This suite does not prove cryptographic primitive correctness. It proves deterministic stage ordering and deterministic normative output once stage facts are supplied.

## Normative stage order

1. `1_STRUCTURE`
2. `2_ARTIFACT`
3. `3_CRYPTO`
4. `4A_BUNDLE_CHAIN_VALIDITY`
5. `4B_KEY_RESOLUTION`
6. `5_TRANSITION_EVIDENCE`
7. `6_HISTORICAL_OR_WITNESS_EVIDENCE`
8. `7_LOCAL_POLICY`

Evaluation is sequential and short-circuiting. The first failing stage determines the normative failure output. Later stages are not evaluated for decision purposes.

`FAILED != NOT_EVALUATED`.

## Normative output

Each vector produces exactly:

```json
{"failedStage":null,"primaryDiagnostic":"MATCH","terminal":"MATCH"}
```

The normative keys are exactly, and in this serialized order:

1. `failedStage`
2. `primaryDiagnostic`
3. `terminal`

`observations[]` is non-normative and is intentionally excluded from this conformance output. No downstream authorization, routing, trust decision, terminal state, or primary diagnostic may depend on `observations[]`.

## Chain ordering

Within trust evaluation:

- bundle/root signature validity precedes sequence/predecessor validity where both are separately exercised by vectors;
- all `4A_BUNDLE_CHAIN_VALIDITY` checks precede `4B_KEY_RESOLUTION`;
- key resolution against an invalid/unvalidated bundle is prohibited;
- child transition evidence cannot repair invalid parent/housing trust.

Diagnostics:

- `DELTA_CHAIN_SIGNATURE` — housing/root bundle signature failure.
- `DELTA_CHAIN_SEQUENCE` — sequence or predecessor failure.
- `DELTA_CHAIN_HOUSING` — required housing bundle is not independently valid.
- `DELTA_TRUST` — key cannot resolve after bundle-chain validity has passed.

## Transition and historical semantics covered

- valid planned leaf succession may emit `DELTA_SUCCESSION` with terminal `MATCH`;
- a revoked key with independently proven signing before the affected window may emit `DELTA_REVOCATION` with terminal `MATCH`;
- unresolved revoked-key chronology emits `DELTA_TIME` / `HOLD`;
- invalid root succession crypto emits `DELTA_ROOT_CRYPTO` / `HOLD`;
- crypto-valid but unwitnessed root succession emits `DELTA_ROOT_UNWITNESSED` / `HOLD_PENDING_LOCAL_TRUST`;
- witness-satisfied but locally unpinned root succession emits `DELTA_ROOT_UNPINNED` / `HOLD_PENDING_LOCAL_TRUST`.

Root-anchor mutation is outside this per-object terminal table. A local pin update is verifier state mutation, not a receipt/object terminal value.

## Required precedence vectors

The suite includes multi-defect vectors proving at least:

- artifact failure precedes crypto failure;
- bundle signature failure precedes key resolution;
- bundle sequence failure precedes key resolution;
- invalid housing precedes succession evidence;
- invalid housing precedes key resolution;
- root witness evaluation precedes local re-pin policy.

## Cross-implementation oracle

Two independent implementations are included:

- `scripts/trust-membrane-validator-node.mjs`
- `scripts/trust_membrane_validator.py`

For the same vector file, PASS requires:

1. each implementation matches every vector's expected triplet;
2. the complete serialized normative outputs are byte-identical;
3. every emitted object contains exactly `failedStage`, `primaryDiagnostic`, and `terminal`.

The GitHub Actions workflow `.github/workflows/trust-membrane-conformance-v1.yml` enforces these requirements.

## Boundary

```text
AUTHORITY_CREATED = FALSE
AUTO_REPIN = PROHIBITED
OBSERVATIONS_NORMATIVE = FALSE
CHILD_CAN_REPAIR_PARENT = FALSE
EVALUATION_MODE = SEQUENTIAL_SHORT_CIRCUIT
```

A green conformance run establishes cross-implementation agreement for these vectors. It does not establish public authority, legal identity, historical truth beyond supplied evidence facts, or correctness of cryptographic libraries not exercised by this suite.
