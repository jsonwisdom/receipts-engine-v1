# ZT Observer Network – Media Ingestion Verification

## Evidence-Grade Boundary

This directory defines the exact verification procedure that makes the system **credible** and the exact runtime gate that makes it **proven**.

- **Credible**: design + docs + verifier logic complete
- **Proven**: `./jay.sh --golden` exits `0` on pinned Foundry with a real Base transaction

The source of truth for the toolchain is:

- `./.foundry_version`
- `./.anchor_contract`
- `./testdata/golden_receipt.json`
- `./testdata/golden_expected.json`

## Foundry Version

Foundry version: see `.foundry_version`

Golden mode must fail hard on Foundry version mismatch.

## Contract

Anchor contract path:

- `src/Anchor.sol`

Expected event surface:

```solidity
event Anchored(
    bytes32 indexed contentHash,
    string contentCid,
    string receiptCid,
    string sourceUrl,
    string observedAt,
    address indexed observer
);
```

## Golden Fixture

Golden fixture files:

- `testdata/golden_receipt.json`
- `testdata/golden_expected.json`

`golden_receipt.json` is append-only unless you intentionally re-baseline.

`golden_expected.json` is not decoration. It drives hard assertions for:

1. `contract_addr`
2. `tx_hash`
3. `content_hash`
4. `content_cid`
5. `receipt_cid`
6. `source_url`
7. `retrieved_at_utc`
8. `foundry_version` via `.foundry_version`

## What Golden Mode Must Prove

Golden mode is stricter than normal verify.

It must assert all of the following:

- Foundry version exact match
- Contract address exact match
- Tx hash exact match
- Content hash exact match
- Content CID exact match
- Receipt CID exact match
- Source URL exact match
- Retrieved-at UTC exact match
- Exactly one matching log from the anchor contract
- `topics[0]`, `topics[1]`, and `data` all match expected values from `cast abi-encode-event --json`

Any deviation = fail.

No warnings. No partial passes.

## Runtime Verification Surface

Normal verify checks:

- content hash matches canonical text from IPFS
- content CID resolves
- receipt CID resolves and matches receipt object
- transaction receipt exists on Base
- exactly one matching contract log exists
- actual `topics[0]`, `topics[1]`, and `data` match expected JSON from `cast abi-encode-event --json`

Hex comparisons must be normalized to lowercase before comparison.

## Setup

1. Install Foundry
2. Pin Foundry version:
   - `cast --version | head -1 > .foundry_version`
3. Deploy contract:
   - `forge create src/Anchor.sol:Anchor --rpc-url $BASE_RPC --private-key $KEY`
4. Save deployed address:
   - `echo 0x... > .anchor_contract`
5. Create a real anchored receipt
6. Save it to `testdata/golden_receipt.json`
7. Create `testdata/golden_expected.json`
8. Run:
   - `./jay.sh --golden`

## If Golden Fails

1. Check `cast --version`
2. Compare with `.foundry_version`
3. Re-deploy `src/Anchor.sol:Anchor` if contract drifted
4. Re-anchor a fresh real receipt
5. Update the golden fixture only if you are intentionally re-baselining
6. Re-run `./jay.sh --golden`

## Trust Boundary

This system is evidence-grade only for:

- content integrity
- IPFS persistence of referenced objects
- append-only observation receipts
- Base event anchoring
- reproducible runtime verification on pinned Foundry

This system is **not** evidence-grade for:

- publisher authenticity
- global first-seen claims
- decentralized consensus
- multi-observer agreement

## Expected Golden Output

```text
🏆 Running golden self-test with pure event encoding...
📋 Test 1: Golden pass (should succeed)
✅ PASS – verifier accepts known-good fixture
📋 Test 2: Tampered content_hash (should fail)
✅ PASS – verifier rejected tampered content_hash
📋 Test 3: Tampered source_url (should fail)
✅ PASS – verifier rejected tampered source_url
🏆 ALL GOLDEN TESTS PASS
```

## Bottom Line

Blueprint locked.

Proof begins when golden runs.
