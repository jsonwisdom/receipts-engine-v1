# Workflow Classification Matrix V0.1

Status: documentation-only
Runtime changes: none
Workflows inspected: 17 of 17 listed in `WORKFLOW_AUTHORITY_SEMANTICS_AUDIT_V0_1.md`

## Classification rules

- `pass meaning` records only what the executed checks establish.
- `mutation` means the workflow can alter repository, issue, ENS, IPFS, or other external state.
- `authority semantics` records whether success could be confused with decision-making authority.
- `kernel gate` is true only when the workflow directly runs the sealed kernel verifier and independently verifies the sealed archive.

## Complete matrix

| Workflow | Scope and commands | Inputs / fixtures | Output or pass meaning | Mutation / secrets / network | Authority semantics | Kernel gate |
|---|---|---|---|---|---|---|
| `audit-gate.yml` | Runs `analysis/rank_report.py`, compares baseline and head audit sets, creates GitHub checks | analysis audit JSON | PASS means no new P0/P1 audit artifacts relative to baseline | Writes PR comments/checks; may commit and push baseline; `contents:write`, `pull-requests:write`, `checks:write` | Check success must not imply global validity or authority | No |
| `deterministic-verify.yml` | Installs `cryptography`, `blake3`; exercises ALMS receipt, payment-adapter, transparency-log, and render commands | signed receipt, ERC20/ERC1155 payment, render fixtures | PASS means listed ALMS fixture assertions matched | Network used for dependency install; no observed repository mutation | Ambiguous: asserts `authority:true` and `authority.valid:true` while narrative says authority false | No |
| `witness-replay.yml` | Builds `replay/Dockerfile`; runs frozen replay container | anchors, checkpoint, replay tree | PASS means container build and replay process exited successfully | Docker build/run; read-only repository checkout | Replay success is not authority and does not independently establish sealed-kernel validity | No |
| `replay-goblin.yml` | Runs `python tools/replay_goblin.py`; uploads log | schemas, fixtures, receipts, reports, seals | PASS means replay-goblin process exited successfully; artifact is `replay-goblin.log` | `issues:write`; artifact upload; no code push observed | Tool contains authority surfaces; log success must not imply governance authority | No |
| `ens-update.yml` | Installs `viem`; runs `scripts/update-ens-records.mjs` | secret RPC, private key, resolver, CID, batch, Merkle root, receipt hash | Success means mutation script exited successfully | External chain mutation; uses `PRIVATE_KEY` and multiple secrets | Authority-bearing operational capability; must be isolated from verification-validity semantics | No |
| `signal-core.yml` | Installs pytest; runs `signal-core/tests/test_receipt_pipeline.py` | Signal Core test code and fixtures | PASS means selected pytest suite passed | Dependency network access; no external mutation observed | Signal Core code contains authority fields; test success does not resolve their meaning | No |
| `case-study-001-independent-verify.yml` | Checks out pinned commit; computes `git archive` SHA-256; emits JSON report | commit `ea4d...`, expected digest | PASS means observed commit and archive digest match pinned values; uploads verifier report | Read-only; artifact upload | Explicit `authority:false`; validity scoped to pinned source-tree digest | No |
| `autonomous-verification.yml` | Installs ethers; reads ENS resolver text record and compares it with local SHA file | `jaywisdom.eth`, ENS key, local `.sha256` file | PASS means ENS text value equals local expected hash | Public Ethereum RPC read | Proves record/hash equality only; not ownership, kernel execution, or authority | No |
| `apple-observer.yml` | Scheduled watcher, diff, receipt build, local verification, Pinata pin, index update, git commit/push | Apple watcher outputs and receipt | PASS means all observer, verifier, pin, and commit commands exited successfully | Uses `PINATA_JWT`; mutates IPFS pin state and repository main branch | Observer output and publication must not be promoted to authoritative truth | No |
| `case-study-001-tally-verifiers.yml` | Requires manual `yes`; counts three reports; runs `verify_consensus.py`; uploads result | three verifier JSON reports | PASS means operator asserted independence, exactly three files existed, and consensus script completed | Read-only repo; artifact upload | Manual assertion of independence is not independently proven; consensus validity is not authority | No |
| `verify-pin.yml` | Installs `eth-hash`; verifies one receipt; pins it to Pinata | `golden-v1-final/receipt.json` | PASS means local receipt verifier and pin command exited successfully | Uses `PINATA_JWT`; external IPFS mutation | Verification and publication are combined; neither grants governance authority | No |
| `autonomous-verification-final.yml` | Duplicate-style ENS read and hash comparison using ethers | same ENS name/key and SHA file | PASS means ENS record equals local SHA | Public Ethereum RPC read | Same narrow equality semantics as autonomous verification; name “Final” must not imply final authority | No |
| `phase3-continuity-replay.yml` | Recomputes archive SHA, checks release attestation and SHA file, verifies ENS text record, emits report | phase-3 attestation, archive, SHA file, ENS record | PASS means four explicit equality checks succeeded; uploads continuity report | Public RPC read; artifact upload | Explicit `authority:false`; strongest artifact continuity check observed, but does not run `impl/verify.py` | No |
| `autonomous-verification-fixed.yml` | Another ENS read and local SHA comparison | same ENS inputs and SHA file | PASS means ENS record equals local SHA | Public Ethereum RPC read | “Fixed” names implementation version, not authority or broader correctness | No |
| `genesis.yml` | Runs analysis ingest and query; uploads generated state | analysis example input | PASS means ingest/query exited successfully and outputs were uploaded | Artifact upload; no repository push observed | Generated analysis and attestations are outputs, not authoritative conclusions | No |
| `case-study-001-digest.yml` | Checks out pinned commit; emits source-tree digest text artifact | commit `ea4d...` | PASS means commands completed; artifact records digest but does not compare to a separate expected digest | Read-only; artifact upload | Explicit `authority=false`; digest generation is observation, not independent verification by itself | No |
| `release-gate.yml` | Installs `cryptography`; verifies one signed ALMS receipt fixture | `fixtures/receipts/valid_signed.json` | PASS means one fixture returned literal `VALID` | Dependency network access; no artifact upload | Release-gate name overstates scope; cryptographic fixture validity is not release authority | No |

## Cross-workflow findings

### 1. No narrow sealed-kernel gate

None of the 17 workflows performs the required pair:

```text
python3 impl/verify.py --test vectors/test_vectors.json
sha256sum receipts_engine_v1.tar.gz
```

`phase3-continuity-replay.yml` independently hashes the archive and checks ENS continuity, but it does not execute the kernel verifier.

### 2. Mutation-capable surfaces

At least three workflows can mutate external or repository state:

- `audit-gate.yml`: GitHub comments, checks, and baseline push
- `ens-update.yml`: ENS record mutation using a private key
- `apple-observer.yml`: Pinata publication and repository push

`replay-goblin.yml` also has `issues:write`, even though the visible workflow only uploads a log.

### 3. Duplicate ENS verification surfaces

The following workflows implement substantially the same read-only ENS/local-hash comparison:

- `autonomous-verification.yml`
- `autonomous-verification-final.yml`
- `autonomous-verification-fixed.yml`

Their names suggest progression, but their pass meaning remains narrowly scoped to record equality.

### 4. Ambiguous or overstated PASS surfaces

- `release-gate.yml` validates one signed fixture, not an entire release.
- `deterministic-verify.yml` validates a selected ALMS fixture suite, not the sealed Python kernel.
- `case-study-001-tally-verifiers.yml` depends on a manual statement that reports are independent.
- `case-study-001-digest.yml` generates a digest but does not independently compare it with a separately sourced expected value.
- ENS verification workflows prove equality between two values, not wallet control, source truth, or authority.

### 5. Authority semantic split

Observed workflows support the following target distinction:

```json
{
  "verification": {
    "valid": true,
    "scope": "explicit-check-name",
    "status": "confirmed"
  },
  "authority": false
}
```

This remains a proposed semantic model, not an adopted runtime schema.

## Step 1B disposition

```text
WORKFLOW_INVENTORY = 17
WORKFLOWS_CLASSIFIED = 17
STEP_1B_AUDIT_EVIDENCE = COMPLETE_FOR_LISTED_WORKFLOWS
RUNTIME_REPAIR = NOT_AUTHORIZED
AUTHORITY_SEMANTICS = AMBIGUOUS
PUBLIC_VERIFICATION_STATUS = PENDING
B20_REQUIRED = FALSE
```

Completion here means each listed workflow has been classified from its YAML. It does not mean workflow runs, artifacts, scripts, or external effects have been independently executed or inspected.

## Remaining Step 1C review questions

Before merge, reviewers should verify:

1. The 17-file inventory is complete for the audited commit.
2. Each scope and PASS statement matches the corresponding YAML.
3. Mutation capabilities and secret use are accurately recorded.
4. No classification promotes workflow success into authority.
5. The audit remains documentation-only.

```text
INVENTORIED = TRUE
CLASSIFIED = TRUE
RUN_EVIDENCE_INSPECTED = FALSE
DOCUMENTED != REPAIRED
```