# Receipt Backbone Receipt Specification v0.1

> Status: Draft MVP contract

This document defines the minimal receipt format for the Receipt Backbone MVP.

The goal is narrow: produce deterministic, signed records for agent actions so a third party can verify what happened without trusting the original runtime.

## Design Goals

- Drop-in instrumentation for existing GitHub agent workflows
- Deterministic hashing over canonical receipt bytes
- Explicit policy version recorded on every receipt
- Signature verification independent of the runtime
- Replay bundle capable of reproducing the same receipt hash

## Minimal Receipt Shape

```json
{
  "receipt_version": "receipt-backbone/v0.1",
  "receipt_id": "sha256:<hex>",
  "run_id": "gh600-demo-001",
  "sequence": 1,
  "timestamp_utc": "2026-07-02T00:00:00Z",
  "actor": {
    "type": "github-agent",
    "id": "example-agent"
  },
  "action": {
    "type": "tool_call",
    "tool_name": "echo",
    "input_sha256": "sha256:<hex>",
    "output_sha256": "sha256:<hex>"
  },
  "policy": {
    "policy_id": "default-policy",
    "policy_version": "0.1.0",
    "decision": "pass",
    "rule_results": [
      {
        "rule_id": "RB-001",
        "result": "pass"
      }
    ]
  },
  "replay": {
    "bundle_id": "sha256:<hex>",
    "canonicalization": "JCS",
    "hash_algorithm": "SHA-256"
  },
  "signature": {
    "scheme": "ed25519",
    "public_key_id": "example-dev-key",
    "signature": "base64:<signature>"
  }
}
```

## Required Fields

| Field | Purpose |
|---|---|
| `receipt_version` | Declares the receipt schema version. |
| `receipt_id` | SHA-256 hash of canonical receipt core bytes before signature attachment. |
| `run_id` | Groups receipts from a single workflow execution. |
| `sequence` | Orders receipts inside the run. |
| `timestamp_utc` | Records observation time. Not a truth oracle. |
| `actor` | Identifies the agent or workflow component that produced the action. |
| `action` | Records action type, tool name, and input/output hashes. |
| `policy` | Records policy ID, version, decision, and rule results. |
| `replay` | Records deterministic replay metadata. |
| `signature` | Binds receipt bytes to a signing key. |

## Hashing Rule

`receipt_id` is computed over the canonical receipt core:

1. Remove the `signature` field.
2. Set `receipt_id` to `null` or omit it during preimage construction.
3. Serialize using JSON Canonicalization Scheme style deterministic ordering.
4. Compute SHA-256 over UTF-8 bytes.
5. Encode as `sha256:<hex>`.

## Signature Rule

The MVP signature scheme is Ed25519.

The signature signs the canonical receipt core bytes after `receipt_id` is computed and inserted, but before the `signature.signature` value is attached.

## Versioning

Breaking schema changes require a new `receipt_version`.

Policy changes require a new `policy_version`.

Replay logic changes require explicit replay metadata updates.

## Scope of Guarantees

This specification can support evidence that:

- a recorded action occurred within the instrumented workflow,
- specific input and output hashes were attached,
- a named policy version evaluated the receipt,
- canonical bytes have not changed since signing.

This specification does not prove:

- the agent's reasoning was correct,
- the external world was honest,
- the selected policy was morally or legally sufficient,
- the runtime was uncompromised before instrumentation.
