# CLASSIFICATION_RECEIPT_HASH_V0_1

Status: HOLD / NON-EXECUTING CONTRACT SURFACE

Repository: `jsonwisdom/receipts-engine-v1`  
Environment: `signal-core`  
Branch: `agent/nine-field-byte-contract-v0-1`  
Authority created: FALSE  
Canon: FALSE  
Execution added: FALSE  
Canonical preimage frozen: FALSE

## Purpose

Define the future byte/hash contract for the separate nine-field classification receipt object without adding a hashing implementation, replay validator, truth arbiter, or authority surface.

This document is intentionally non-executing. It records boundaries and unresolved gates only.

## Placement

- Shape/type constraints: `signal-core/schema/receipt-schema-nine-field-v0.1.schema.json` — FUTURE
- Byte/hash contract: `docs/CLASSIFICATION_RECEIPT_HASH_V0_1.md` — THIS FILE
- Replay implementation: `signal-core/validator/replay_nine_field_hash_v0_1.py` — FUTURE
- Conformance fixtures: FUTURE, after the byte contract is frozen

## Existing Signal Core context

Signal Core already separates schema, deterministic representation, SHA-256, validation/replay, and fixtures.

Its existing verification-receipt schema declares JCS / RFC 8785 for production use.

The existing Python validator currently uses a temporary deterministic JSON fallback:

```python
json.dumps(
    value,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False
).encode("utf-8")
```

That fallback MUST NOT be inherited by the nine-field receipt unless a later explicit decision freezes it as part of this contract.

## Current decision surface

```text
REPOSITORY = receipts-engine-v1
ENVIRONMENT = signal-core
EXECUTION_ADDED = FALSE

unicode_normalization FIELD TYPE = CONTENT
unicode_normalization FIELD AUTHORITY = FALSE

BYTE_LAYER_UNICODE_POLICY = U-1 / NONE
ABSENT_FIELD_POLICY = UNRESOLVED
NULL_POLICY = UNRESOLVED
CANONICAL_PREIMAGE_FROZEN = FALSE
```

The `unicode_normalization` field, when present in the nine-field preimage, is data. It is not a canonicalization directive, encoding selector, or sibling-field modifier.

That field-level typing is separate from the byte-layer policy.

The byte-layer policy is now U-1 / NONE: preserve exact code points and encode them as UTF-8 bytes. Do not apply NFC, NFD, compatibility normalization, case-folding, quote substitution, or semantic rewriting.

## Freeze gates

No implementation, fixture hash, or schema requirement may imply answers to unresolved byte-contract questions.

Before `CANONICAL_PREIMAGE_FROZEN = TRUE`, an explicit later receipt must resolve at least:

1. absent-field behavior;
2. null behavior;
3. exact canonical representation rules needed to reproduce the preimage bytes.

The Unicode byte-layer gate is resolved as U-1 / NONE, but that does not freeze the remaining representation rules.

## Non-authority invariant

A schema-valid or hash-replayable receipt does not establish world truth.

```text
STRUCTURAL_VALIDITY != TRUTH
HASH_MATCH != TRUTH
REPLAY_SUCCESS != AUTHORITY
RECEIPT != ADJUDICATION
```

## Federation rule

`CITIZEN_ROOT` may eventually point to the frozen source artifact and its digest. It should not own or duplicate this protocol artifact.

Until the freeze gates close, downstream pointers must preserve HOLD state.
