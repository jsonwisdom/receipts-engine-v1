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
- The latest inspected main commit was `95469e5c01bb021afab811063c044c0290c5eb84`.
- No kernel-specific artifact gate was observed that runs both:
  - `python3 impl/verify.py --test vectors/test_vectors.json`
  - `sha256sum receipts_engine_v1.tar.gz`
- Public verification of the sealed kernel artifact remains pending until a run and artifact are independently inspected.

## Workflow inventory

The following root-level workflows were observed through repository search:

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

Each workflow must be classified in a later audit pass as one of:

- kernel verification
- receipt verification
- payment adapter verification
- replay/witness verification
- publication or release
- observer/monitoring
- governance/audit automation
- chain or ENS mutation

## Detailed observed findings

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

Audit classification:

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

Audit classification:

```text
SCOPE = GOVERNANCE_AUDIT_AUTOMATION
KERNEL_GATE = FALSE
PASS_MEANING = NO_NEW_HIGH_PRIORITY_DELTA
MUTATION_CAPABILITY = TRUE
AUTHORITY_SEMANTICS = MUST_NOT_BE_INFERRED_FROM_CHECK_SUCCESS
```

## Repository-wide authority surface

Repository search found `authority: true` references in workflows, tools, Signal Core code, documentation, and adapter materials, including:

- `.github/workflows/deterministic-verify.yml`
- `.github/workflows/case-study-001-independent-verify.yml`
- `.github/workflows/case-study-001-tally-verifiers.yml`
- `tools/alms.py`
- `tools/replay_goblin.py`
- `scripts/verify_consensus.py`
- `signal-core/` validators, canonicalizers, sealers, tests, and documentation
- receipt-render and ERC-1155 adapter documentation

This confirms that the ambiguity is repository-wide and must not be repaired through blind boolean replacement.

## Open semantic questions

For every occurrence of `authority`, `authority.valid`, `valid`, `verified`, `confirmed`, `pass`, or `success`, the repair PR must answer:

1. Does the field describe evidence validity, workflow completion, permission, governance power, or publication state?
2. Is the value derived from execution or copied from fixture data?
3. Can downstream code interpret the value as decision-making authority?
4. Is the field part of a stable serialized interface?
5. Would renaming it break fixtures, hashes, signatures, or compatibility?
6. Should it become `verification.valid`, remain a domain-specific capability field, or be isolated in a separate subsystem?

## Required next audit pass

Inspect every root-level workflow and record:

- triggers
- permissions
- commands
- network access
- secrets
- inputs and fixtures
- outputs and uploaded artifacts
- mutation capability
- pass/fail meaning
- `authority` and `valid` fields
- whether the workflow touches the sealed kernel

No runtime repair is authorized by this document.

## Current admissible state

```text
ROOT_LEVEL_WORKFLOWS_PRESENT = TRUE
SEALED_ARTIFACT_PRESENT = TRUE
AUTHORITY_SEMANTICS = AMBIGUOUS
GLOBAL_AUTHORITY_FALSE_PRESERVATION = UNCONFIRMED
KERNEL_ARTIFACT_GATE = NOT_OBSERVED
PUBLIC_VERIFICATION_STATUS = PENDING
B20_REQUIRED = FALSE
```

## Promotion boundary

This audit does not promote repository state.

```text
DOCUMENTED != REPAIRED
WORKFLOW_SUCCESS != KERNEL_VERIFICATION
VERIFICATION_VALIDITY != GOVERNANCE_AUTHORITY
```

The next governed change must be based on completed workflow-by-workflow evidence and must either rename, isolate, or explicitly define ambiguous fields without erasing their provenance.