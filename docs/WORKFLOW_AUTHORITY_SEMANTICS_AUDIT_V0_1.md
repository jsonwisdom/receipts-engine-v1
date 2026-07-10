# Workflow Authority Semantics Audit V0.1

Status: documentation-only audit
Runtime changes: none
Authority changes: none

## Purpose

Map the repository's executable workflow surface and identify places where evidence validity, workflow success, governance authority, and permission may be conflated.

This document does not repair fields or change runtime behavior. It records observed semantics and open questions for a later governed patch.

## Required semantic distinction

```json
{
  "verification": {
    "valid": true,
    "status": "confirmed"
  },
  "authority": false
}
```

Definitions:

- `verification.valid`: evidence passed the stated verification procedure.
- `verification.status`: lifecycle state of that verification result.
- `authority`: whether the receipt, workflow, agent, or system may make a binding decision or claim.

A valid receipt does not automatically possess authority.

## Observed repository state

- Root-level GitHub Actions workflows exist and are executable.
- The audited main commit was `95469e5c01bb021afab811063c044c0290c5eb84`.
- Seventeen root-level workflows were inventoried and classified from their YAML.
- The complete workflow-by-workflow matrix is recorded in [`WORKFLOW_CLASSIFICATION_MATRIX_V0_1.md`](./WORKFLOW_CLASSIFICATION_MATRIX_V0_1.md).
- No kernel-specific artifact gate was observed that runs both:
  - `python3 impl/verify.py --test vectors/test_vectors.json`
  - `sha256sum receipts_engine_v1.tar.gz`
- Public verification of the sealed kernel artifact remains pending until a run and artifact are independently inspected.

## Workflow inventory

- `audit-gate.yml`
- `witness-replay.yml`
- `replay-goblin.yml`
- `ens-update.yml`
- `signal-core.yml`
- `case-study-001-independent-verify.yml`
- `autonomous-verification.yml`
- `apple-observer.yml`
- `case-study-001-tally-verifiers.yml`
- `verify-pin.yml`
- `autonomous-verification-final.yml`
- `phase3-continuity-replay.yml`
- `autonomous-verification-fixed.yml`
- `genesis.yml`
- `case-study-001-digest.yml`
- `release-gate.yml`
- `deterministic-verify.yml`

## Detailed anchor findings

### `.github/workflows/deterministic-verify.yml`

Observed commands and dependencies:

- installs `cryptography` and `blake3`
- runs `tools/alms.py verify`
- exercises ERC-20 and ERC-1155 payment adapter commands
- creates and verifies a transparency-log witness
- renders receipt fixtures and checks authority footer output

Kernel relationship:

- Does not run `impl/verify.py --test vectors/test_vectors.json`.
- Does not hash `receipts_engine_v1.tar.gz`.
- Therefore it is not the narrow sealed-kernel verification gate.

Semantic ambiguity:

- Human render checks expect `authority: true` for confirmed fixtures.
- JSON output asserts an object shaped like `authority.valid == true`.
- The same repository and PR narrative state that `authority:false` is preserved.

```text
SCOPE = BROADER_ALMS_VERIFICATION
KERNEL_GATE = FALSE
AUTHORITY_SEMANTICS = AMBIGUOUS
RUNTIME_CHANGE_REQUIRED = UNDECIDED
```

### `.github/workflows/audit-gate.yml`

Observed commands and behavior:

- runs `analysis/rank_report.py`
- creates baseline and head audit files
- blocks newly introduced high-priority audit artifacts
- creates explicit passing or failing GitHub checks
- may update and push the baseline file on `main`

Authority and success semantics:

- A passing check means no new P0/P1 artifacts were detected relative to the stored baseline.
- It does not prove global correctness, kernel validity, or public verification.
- The workflow has `contents: write`, `pull-requests: write`, and `checks: write` permissions.

```text
SCOPE = GOVERNANCE_AUDIT_AUTOMATION
KERNEL_GATE = FALSE
PASS_MEANING = NO_NEW_HIGH_PRIORITY_DELTA
MUTATION_CAPABILITY = TRUE
AUTHORITY_SEMANTICS = MUST_NOT_BE_INFERRED_FROM_CHECK_SUCCESS
```

## Cross-workflow findings

The complete evidence table is maintained in `WORKFLOW_CLASSIFICATION_MATRIX_V0_1.md`. Material findings include:

- No workflow combines sealed-kernel execution with independent sealed-archive verification.
- `ens-update.yml`, `apple-observer.yml`, `verify-pin.yml`, and `audit-gate.yml` possess or exercise mutation capability.
- `replay-goblin.yml` has `issues:write` permission.
- Three workflows duplicate substantially the same ENS/local-hash read check.
- Several workflow names overstate the narrow meaning of their PASS result.
- `authority: true` appears across workflows, tools, Signal Core code, and documentation.

This confirms that the ambiguity is repository-wide and must not be repaired through blind boolean replacement.

## Open semantic questions

For every occurrence of `authority`, `authority.valid`, `valid`, `verified`, `confirmed`, `pass`, or `success`, the repair PR must answer:

1. Does the field describe evidence validity, workflow completion, permission, governance power, or publication state?
2. Is the value derived from execution or copied from fixture data?
3. Can downstream code interpret the value as decision-making authority?
4. Is the field part of a stable serialized interface?
5. Would renaming it break fixtures, hashes, signatures, or compatibility?
6. Should it become `verification.valid`, remain a domain-specific capability field, or be isolated in a separate subsystem?

## Audit completion boundary

```text
STEP_1A_WORKFLOW_INVENTORY = COMPLETE
STEP_1B_YAML_CLASSIFICATION = COMPLETE
STEP_1C_REVIEW_AND_MERGE = PENDING
WORKFLOW_RUNS_INSPECTED = FALSE
RUNTIME_REPAIR_AUTHORIZED = FALSE
```

Step 1B completion means all 17 listed YAML workflows were classified. It does not mean their scripts, runs, uploaded artifacts, or external mutations were independently executed and inspected.

## Current admissible state

```text
ROOT_LEVEL_WORKFLOWS_PRESENT = TRUE
SEALED_ARTIFACT_PRESENT = TRUE
AUTHORITY_SEMANTICS = AMBIGUOUS
GLOBAL_AUTHORITY_FALSE_PRESERVATION = UNCONFIRMED
KERNEL_ARTIFACT_GATE = NOT_OBSERVED
PUBLIC_VERIFICATION_STATUS = PENDING
B20_REQUIRED = FALSE
PR_51_STATUS = OPEN
```

## Promotion boundary

This audit does not promote repository state.

```text
DOCUMENTED != REPAIRED
WORKFLOW_SUCCESS != KERNEL_VERIFICATION
VERIFICATION_VALIDITY != GOVERNANCE_AUTHORITY
CLASSIFIED != EXECUTED
```

The next governed action is Step 1C: review the two documentation files, verify the classifications against the audited YAML, and decide whether PR #51 is merge-admissible. Runtime repair remains blocked.