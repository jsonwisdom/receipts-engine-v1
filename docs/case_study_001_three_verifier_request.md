# CASE_STUDY_001 — Three-Verifier Request

Status: `READY_FOR_THREE_VERIFIERS`  
Authority: `false`

This request is replay-only. No production readiness claim is made. No universal correctness claim is made. The only claim being tested is whether independent verifiers can reproduce the same source tree digest for the same canonical commit.

## Important boundary

`v1.1` is currently a **branch ref**, not a Git tag.

A branch ref may move over time. All replay verification must anchor to the commit SHA only:

```text
ea4d77117c5cdcd9acb4ba6d1092298ed84c6c1d
```

Human label: `v1.1`  
Proof anchor: `ea4d77117c5cdcd9acb4ba6d1092298ed84c6c1d`

## Expected values

```json
{
  "case_study": "CASE_STUDY_001",
  "ref_type": "branch",
  "ref_name": "v1.1",
  "canonical_anchor_sha": "ea4d77117c5cdcd9acb4ba6d1092298ed84c6c1d",
  "expected_digest_sha256": "80bea317ecca694ffd1e709ea2f986374eb0753890f8fc33478567ce408e2675",
  "replay_method": "git-archive-tree-sha256",
  "authority": false
}
```

## Canonical commands

Run exactly:

```bash
git clone https://github.com/jsonwisdom/receipts-engine-v1.git
cd receipts-engine-v1
git fetch origin
git checkout ea4d77117c5cdcd9acb4ba6d1092298ed84c6c1d
git archive --format=tar ea4d77117c5cdcd9acb4ba6d1092298ed84c6c1d | sha256sum
git log -1 --format=%H
```

## Required verifier report

Each verifier should report:

```json
{
  "verifier": "<name_or_handle>",
  "os": "<os_and_version>",
  "git_version": "<git_version>",
  "full_sha256sum_output": "<64_hex_digest>  -",
  "commit_sha": "<git_log_output>",
  "checked_out_commit_sha": "ea4d77117c5cdcd9acb4ba6d1092298ed84c6c1d",
  "expected_digest_sha256": "80bea317ecca694ffd1e709ea2f986374eb0753890f8fc33478567ce408e2675",
  "verdict": "PASS | FAIL",
  "authority": false
}
```

## PASS condition

A verifier returns `PASS` only if:

- Their full sha256sum output begins with `80bea317ecca694ffd1e709ea2f986374eb0753890f8fc33478567ce408e2675`
- Their commit SHA equals `ea4d77117c5cdcd9acb4ba6d1092298ed84c6c1d`
- They followed the canonical commands without substituting the branch name for the commit SHA

## CASE_STUDY_001 close condition

CASE_STUDY_001 closes only after three independent verifiers report:

- same digest
- same commit SHA
- PASS verdict

No authority. No interpretation. Only reproducibility.
