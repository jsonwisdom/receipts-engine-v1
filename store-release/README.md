# Jay's American Storefront — Store Release Merkle v0.1

**Classification:** deterministic commercial-state integrity verifier  
**Canonical commercial source:** `jsonwisdom/flywheel-of-wisdom` at an exact commit  
**Verifier surface:** `jsonwisdom/receipts-engine-v1`  
**Authority created:** `FALSE`

## Purpose

Compile a deterministic `STORE_RELEASE_MERKLE_ROOT` from a declared, exact GitHub storefront snapshot and emit an **unsigned** EAS Receipt Core v0.4-compatible payload.

The root proves which declared bytes were included. It does not prove product quality, legal truth, payment, wallet ownership, Google endorsement, ratings, deployment, or external authority.

```text
STORE_SOURCE_BYTES
  -> GIT_BLOB_CHECK
  -> CONTENT_SHA256
  -> DOMAIN_SEPARATED_LEAF
  -> MERKLE_TREE
  -> STORE_RELEASE_MERKLE_ROOT
  -> UNSIGNED_EAS_PAYLOAD
```

## Role separation

```text
flywheel-of-wisdom/store = COMMERCIAL_SOURCE
receipts-engine-v1       = VERIFIER / PROOF DISPLAY
STORE_RELEASE_ROOT       = COMMERCIAL_STATE_FINGERPRINT
EAS                      = OPTIONAL PUBLIC WITNESS
Google Merchant Center   = DISTRIBUTION / REVIEW SURFACE
jaywisdom.base.eth       = BENEFICIARY IDENTITY LABEL
0xA380...002E8           = CLAIMED PAYOUT ADDRESS
0xC345...5a84            = RECEIPT/EAS SCHEMA CREATOR RAIL
```

These roles are not interchangeable.

## Source snapshot

v0.1 binds Store / Money Machine PR #2 exact source head:

`de9e1dde3bda66f697671abf94f932e58a577066`

The source currently calls itself `JSONWisdom Store`. `Jay's American Storefront` is a presentation/brand candidate in this verifier package; this package does not rename or promote the source store.

## Merkle algorithm

This package intentionally reuses the repository's existing receipt-engine convention:

- content hash: SHA-256 of raw file bytes;
- leaf: `SHA256(0x00 || "v1" || lowercase_hex(content_sha256))`;
- order: source paths sorted lexicographically;
- parent: `SHA256(0x01 || lowercase_hex(left) || lowercase_hex(right))`;
- odd layer: duplicate the final node.

The hex digests are encoded as ASCII when constructing the leaf/parent preimages, matching the existing watcher implementation.

## EAS boundary

Receipt Core v0.4 schema anchor:

- network: Base
- schema number: `1618`
- schema UID: `0xa5b0d2dd5470542a119d50eba19898f50e1f77591f01d4fec4c6f3075054aa11`
- schema creator rail: `0xC345B26094c63C69222Ee775189a3d3eaead5a84`

The generator emits payload JSON only.

```text
EAS_PAYLOAD_GENERATED = TRUE
EAS_ATTESTATION_BROADCAST = FALSE
SIGNER_USED = FALSE
WALLET_MUTATION = FALSE
AUTHORITY_CREATED = FALSE
```

## Core membranes

```text
MERKLE_INCLUSION != WORLD_TRUE
MERKLE_ROOT != PAYMENT
MERKLE_ROOT != PRODUCT_QUALITY
EAS_ATTESTATION != WALLET_CONTROL
GOOGLE_LISTING != ENDORSEMENT
STORE_RATING_NOT_ESTABLISHED != STORE_FAILURE
IDENTITY_LABEL != KEY_CONTROL
REVENUE != PROFIT
ALLOCATION != TRANSFER
REPLAY_SUCCESS != LEGAL_FINDING
```

## Files

- `sources/STORE_SOURCE_MANIFEST_V0_1.json` — exact source commit and declared leaves.
- `fixtures/STORE_CLAIMS_V0_1.json` — bounded claims carried by the release receipt.
- `schemas/` — receipt and EAS payload schemas.
- `tools/build_store_release_root.py` — deterministic compiler.
- `tools/verify_store_release_v0_1.py` — fail-closed verifier.
- `eas/` — generated unsigned payload output surface.
- `receipts/` — replay/build receipts.
- `openai/agent_contract.json` — deterministic-core boundary.

No OpenAI model or API key is required to build or verify the root.
