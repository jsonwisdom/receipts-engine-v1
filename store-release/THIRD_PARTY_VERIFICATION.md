# Jay's American Storefront — Third-Party Verification Contract v0.1

## Purpose

Allow an independent auditor with Git and Python 3 to reproduce the exact Store Release Merkle root and Receipt Core hash without importing the production Store Release builder.

This contract verifies deterministic repository state. It does not prove product quality, external truth, payment, wallet control, Google endorsement, legal authority, or an on-chain attestation.

## Exact inputs

- Store repository: `jsonwisdom/flywheel-of-wisdom`
- Store source head: `de9e1dde3bda66f697671abf94f932e58a577066`
- Receipt Engine repository: `jsonwisdom/receipts-engine-v1`
- Independent verifier basis head: `58f6ff11514369f5db86aa5f4a2f0b9711eacac9`
- Store source leaves: 13

Expected outputs:

```text
STORE_RELEASE_MERKLE_ROOT=10c51683dc14f12128c472ecdda4e6a459ea6f6561ee6ec9f8459732d6e7376a
RECEIPT_CORE_SHA256=aba9765c769f9e9d3d05dd472dd0a3812d62e38bcab3ea0e5e761b0252a46706
SOURCE_MANIFEST_SHA256=18d79d3c18049f078bb8c1adeff93023124530d5b02bf223e5fb32d5383734f6
CLAIM_GRAPH_SHA256=12ac355e9bec3f98c2aa51152899043023f0b757a73c19a776f70cb4783ba59e
POLICY_SHA256=a76d47db992c665d7f0662d6821fd5c474b6b973291f9450a81eec02658703b9
```

## Clone and pin

```bash
git clone https://github.com/jsonwisdom/receipts-engine-v1.git
git -C receipts-engine-v1 checkout 58f6ff11514369f5db86aa5f4a2f0b9711eacac9

git clone https://github.com/jsonwisdom/flywheel-of-wisdom.git
git -C flywheel-of-wisdom checkout de9e1dde3bda66f697671abf94f932e58a577066
```

The Store SHA above is intentionally the full exact source SHA. Do not substitute similarly prefixed commits.

## Independent replay

From the parent directory containing both repositories:

```bash
python3 receipts-engine-v1/store-release/tools/verify_store_release_independent.py \
  --source-root flywheel-of-wisdom \
  --manifest receipts-engine-v1/store-release/sources/STORE_SOURCE_MANIFEST_V0_1.json \
  --claims receipts-engine-v1/store-release/fixtures/STORE_CLAIMS_V0_1.json \
  --build-receipt receipts-engine-v1/store-release/receipts/BUILD_RECEIPT_0001.json
```

Expected terminal state:

```text
STORE_RELEASE_THIRD_PARTY_VERIFICATION=PASS
STORE_SOURCE_REF=de9e1dde3bda66f697671abf94f932e58a577066
SOURCE_LEAF_COUNT=13
STORE_RELEASE_MERKLE_ROOT=10c51683dc14f12128c472ecdda4e6a459ea6f6561ee6ec9f8459732d6e7376a
RECEIPT_CORE_SHA256=aba9765c769f9e9d3d05dd472dd0a3812d62e38bcab3ea0e5e761b0252a46706
RECORDED_EAS_ATTESTATION_BROADCAST=FALSE
RECORDED_SIGNER_USED=FALSE
RECORDED_AUTHORITY_CREATED=FALSE
MERKLE_INCLUSION_WORLD_TRUE=FALSE
```

## What the verifier independently checks

1. Store `HEAD` equals the exact source SHA declared by the Store source manifest.
2. Every declared source path exists.
3. Every source file reproduces its declared Git blob SHA-1 using Git's `blob <length>\0<bytes>` object encoding.
4. Every source file is SHA-256 hashed as raw bytes.
5. Leaves are ordered by source path lexicographically.
6. Leaf hash is `SHA256(0x00 || "v1" || ASCII(content_sha256_hex))`.
7. Parent hash is `SHA256(0x01 || ASCII(left_hex) || ASCII(right_hex))`.
8. Odd layers duplicate the last node.
9. The exact Store Release Merkle root is reproduced.
10. Source manifest, claims graph, policy, and Receipt Core hashes are independently reconstructed.
11. Build Receipt 0001 records unsigned/non-promoting state.

## Important algorithm correction

Do **not** sort leaf hashes or parent hashes independently. Determinism comes from sorting the declared **source paths once before leaf construction**. Re-sorting hashes at each level produces a different tree topology and is not the Receipt Engine v1 algorithm.

Likewise, plain `SHA256(left_hex + right_hex)` is not sufficient; Receipt Engine v1 uses explicit domain separation for both leaves and parents.

## Boundaries

```text
MERKLE_INCLUSION != WORLD_TRUE
GIT_BLOB_MATCH != SEMANTIC_TRUTH
RECEIPT_CORE_MATCH != PAYMENT
EAS_DRAFT_PAYLOAD != ONCHAIN_ATTESTATION
GOOGLE_LISTING != ENDORSEMENT
CI_SUCCESS != COMMERCIAL_PROMOTION
AUTHORITY_CREATED = FALSE
```
