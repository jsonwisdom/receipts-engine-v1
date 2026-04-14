# Jason's Wisdom Audit — Git Connect (v1.1)

## Failure Class
Unverified mutation of trust root followed by continued execution.

## Mandatory Model
Any mutation => HALT => full state map before any action.

## State Map (required)
- GitHub: branch, latest SHA, file sizes
- ENS: anchors_json_sha256, receipts_engine_v1_sha256
- Verifier: paths + hashes checked
- Local: file sizes + status
- Auth: method + validity

## Rules
- No incremental fixes
- No terminal delegation
- No trust-root edits without migration

## Phase-3 Separation
- Trust root: attestations/anchors.json (zero-byte)
- Release ledger: attestations/phase3-release.json
- Manifest: attestations/phase3-manifest.json

## Verifier
Use verify-phase3.sh only.

## Verdict
All mutations must be followed by full reconciliation or system is invalid.
