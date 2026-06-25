# Signal Core: Verification Receipt v0.1

## Purpose

A receipt is the atomic, replayable unit for epistemic transport.

It records construction history, evidence pointers, replay steps, cryptographic hashes, gaps, circularity, and measurable telemetry.

It does **not** decide truth.

## Core invariant

```text
Authority: NONE
```

No single integrity score. No oracle capture. No reputation baked into the primitive.

Reputation, scoring, trust graphs, dashboards, APIs, and market overlays are separate composable layers.

## Receipt layers

1. **Artifact** — immutable hash anchor for content and metadata.
2. **Claim Snapshot** — directed claims and dependencies.
3. **Evidence Bundle** — source pointers with fetch methods and expected hashes.
4. **Replay Log** — timestamped verification steps and outcomes.
5. **Telemetry** — multi-axis measurable properties.
6. **Extensions** — optional claim-specific verifiers, zk stubs, future proof modules.

## Canonical rule

Production receipts should use JCS / RFC8785 canonical JSON before hashing.

Current validator stub uses deterministic sorted JSON as a temporary local fallback. Replace before production sealing.

## Receipt ID rule

```text
receipt_id = sha256(JCS({
  artifact.hash,
  claim_snapshot.hash,
  evidence_bundle.hash
}))
```

## Forbidden behavior

The primitive must not output:

- true / false claim verdicts
- guilt / innocence labels
- official authority claims
- single final integrity scores
- reputation conclusions

Allowed output is structural telemetry only.

## Files

- `schema/verification-receipt-v0.1.schema.json`
- `examples/verification-receipt-v0.1.example.json`
- `validator/validate_receipt_v0_1.py`

## Local validation

```bash
python3 signal-core/validator/validate_receipt_v0_1.py \
  signal-core/examples/verification-receipt-v0.1.example.json
```

Strict receipt-id recomputation:

```bash
python3 signal-core/validator/validate_receipt_v0_1.py \
  signal-core/examples/verification-receipt-v0.1.example.json \
  --strict-id
```

The example intentionally uses placeholder hashes, so strict mode should fail until the sample is sealed with recomputed hashes.

## Jay Wisdom lock

Build. Seal. Verify. Repeat.

Receipts over narrative.

# CI trigger
