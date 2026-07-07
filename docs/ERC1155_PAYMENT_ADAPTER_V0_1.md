# ERC1155 Payment Adapter V0.1

## Purpose

Define an ERC-1155 adapter over the existing ALMS payment profile abstraction.

The adapter does not mutate canonical receipts. It extends payment proof verification with `token_id`, `units`, and batch-aware transfer semantics while preserving the same replay and transparency model.

The replay function remains pure:

```text
verify_payment(profile, proof, receipt_hash) -> VALID_PAYMENT | INVALID_PAYMENT
```

## Profile Schema

```json
{
  "payment_profile_version": "ERC1155_PAYMENT_ADAPTER_V0_1",
  "asset_standard": "erc1155",
  "chain_id": 8453,
  "token_address": "0x...",
  "accepted_token_ids": ["1", "2"],
  "min_units": "1",
  "max_units": "1000",
  "payee": "0x...",
  "batch_allowed": false
}
```

## Proof Schema

```json
{
  "chain_id": 8453,
  "token_address": "0x...",
  "token_id": "1",
  "units": "1",
  "payer": "0x...",
  "payee": "0x...",
  "tx_hash": "0x...",
  "block_number": 1,
  "transfer_event_hash": "c3d58168...",
  "receipt_hash": "sha256...",
  "payment_reference": "sha256...",
  "batch_index": null
}
```

## Canonical Invariants

1. `asset_standard` must equal `erc1155`.
2. `payment_profile_version` must equal `ERC1155_PAYMENT_ADAPTER_V0_1`.
3. `chain_id` must match the configured network.
4. `token_address` must match the configured ERC-1155 contract after lowercase normalization.
5. `token_id` must be explicitly listed in `accepted_token_ids`.
6. `units` must be an integer string within `[min_units, max_units]`.
7. `payer`, `payee`, `tx_hash`, `block_number`, and `receipt_hash` must be present.
8. `payee` must match the profile payee after lowercase normalization.
9. `transfer_event_hash` must match ERC-1155 transfer semantics:
   - `c3d58168` for `TransferSingle`
   - `4a39dc06` for `TransferBatch`
10. Batch transfer proofs are valid only when `batch_allowed` is `true`.
11. Batch transfer proofs must include integer `batch_index`.
12. Single transfer proofs must use `batch_index: null` or omit `batch_index`.
13. `payment_reference` must recompute exactly.
14. `receipt_hash` and `payment_reference` are immutable after issuance.
15. Receipts remain canonical; adapter state must not be written into signed receipt payloads.

## Payment Reference Rule

For ERC-1155, `payment_reference` is:

```text
sha256(JCS({
  receipt_hash,
  payment_profile_version,
  asset_standard,
  chain_id,
  token_address,
  token_id,
  payee
}))
```

This differs from ERC-20 only by including `asset_standard` and `token_id`.

## Dispatcher Rules

The unified CLI dispatches by `asset_standard`:

```text
if profile.asset_standard is missing:
  use ERC20_PAYMENT_PROFILE_V0_1 verifier

if profile.asset_standard == "erc20":
  use ERC20 verifier

if profile.asset_standard == "erc1155":
  use ERC1155 verifier

otherwise:
  INVALID_PAYMENT
```

No receipt-core logic changes are allowed. Dispatch occurs only inside the payment verification layer.

## CLI

```text
alms payment-bind <receipt.json> <profile.json>
alms payment-verify <profile.json> <proof.json>
alms payment-refresh <profile.json>
```

## Fixture Outlines

### `fixtures/payments/erc1155_profile.v0_1.json`

```json
{
  "payment_profile_version": "ERC1155_PAYMENT_ADAPTER_V0_1",
  "asset_standard": "erc1155",
  "chain_id": 8453,
  "token_address": "0x0000000000000000000000000000000000000015",
  "accepted_token_ids": ["1"],
  "min_units": "1",
  "max_units": "10",
  "payee": "0x0000000000000000000000000000000000000002",
  "batch_allowed": false
}
```

### `fixtures/payments/erc1155_payment.valid.json`

```json
{
  "chain_id": 8453,
  "token_address": "0x0000000000000000000000000000000000000015",
  "token_id": "1",
  "units": "1",
  "payer": "0x0000000000000000000000000000000000000003",
  "payee": "0x0000000000000000000000000000000000000002",
  "tx_hash": "0x0000000000000000000000000000000000000000000000000000000000000016",
  "block_number": 1,
  "transfer_event_hash": "c3d5816800000000000000000000000000000000000000000000000000000000",
  "receipt_hash": "cd6f730c46b5a0255c21d0bce30d8a2bebb1a6fc654b0150de0784ad0c1c2427",
  "payment_reference": "<computed>",
  "batch_index": null
}
```

### Negative fixtures

```text
erc1155_payment.invalid_token_id.json -> INVALID_PAYMENT
erc1155_payment.batch_disallowed.json -> INVALID_PAYMENT
erc1155_payment.reference_mismatch.json -> INVALID_PAYMENT
```

## Test Vectors

```text
payment-refresh erc1155_profile.v0_1.json -> PROFILE_VALID
payment-bind valid_signed.json erc1155_profile.v0_1.json -> <computed payment_reference>
payment-verify erc1155_profile.v0_1.json erc1155_payment.valid.json -> VALID_PAYMENT
payment-verify erc1155_profile.v0_1.json erc1155_payment.invalid_token_id.json -> INVALID_PAYMENT
payment-verify erc1155_profile.v0_1.json erc1155_payment.batch_disallowed.json -> INVALID_PAYMENT
```

## Boundary

```text
authority: false
```
