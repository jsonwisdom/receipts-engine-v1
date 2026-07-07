# ERC1155 Payment Adapter Implementation Manifest V0.1

## Purpose

Convert `ERC1155_PAYMENT_ADAPTER_V0_1` from sealed specification to executable implementation without mutating ALMS receipt core semantics.

The implementation must preserve the existing unified payment CLI surface:

```text
alms payment-bind <receipt.json> <profile.json>
alms payment-verify <profile.json> <proof.json>
alms payment-refresh <profile.json>
```

## Files To Add

```text
fixtures/payments/erc1155_profile.v0_1.json
fixtures/payments/erc1155_payment.valid.json
fixtures/payments/erc1155_payment.invalid_token_id.json
fixtures/payments/erc1155_payment.batch_disallowed.json
fixtures/payments/erc1155_payment.reference_mismatch.json
```

## Files To Modify

```text
tools/alms.py
.github/workflows/deterministic-verify.yml
```

## Profile Fixture Schema

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

## Valid Proof Fixture Schema

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

## Dispatch Logic

`tools/alms.py` must dispatch only inside the payment layer:

```text
profile.asset_standard missing -> ERC20 verifier
profile.asset_standard == erc20 -> ERC20 verifier
profile.asset_standard == erc1155 -> ERC1155 verifier
otherwise -> INVALID_PAYMENT
```

The signed receipt verifier remains unchanged.

## ERC1155 Reference Binding

For ERC-1155, compute payment reference as:

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

All address fields must be lowercase-normalized before hashing.

## Verification Rules

`payment-refresh` must return `PROFILE_VALID` only when:

1. `asset_standard == "erc1155"`.
2. `payment_profile_version == "ERC1155_PAYMENT_ADAPTER_V0_1"`.
3. `chain_id` is an integer.
4. `token_address` is a non-empty string.
5. `accepted_token_ids` is a non-empty list of strings.
6. `min_units` and `max_units` are integer strings.
7. `payee` is a non-empty string.
8. `batch_allowed` is a boolean.

`payment-verify` must return `VALID_PAYMENT` only when:

1. Profile is valid.
2. Proof `chain_id` matches profile `chain_id`.
3. Proof `token_address` matches profile `token_address` after lowercase normalization.
4. Proof `token_id` is accepted by profile.
5. Proof `units` is within `[min_units, max_units]`.
6. Proof `payee` matches profile `payee` after lowercase normalization.
7. `payer`, `tx_hash`, `block_number`, and `receipt_hash` are present.
8. `transfer_event_hash` starts with `c3d58168` for single transfer.
9. `transfer_event_hash` starts with `4a39dc06` for batch transfer.
10. Batch transfer is accepted only when `batch_allowed == true` and `batch_index` is an integer.
11. Single transfer must have `batch_index == null` or no `batch_index`.
12. `payment_reference` recomputes exactly.

## Negative Fixtures

```text
erc1155_payment.invalid_token_id.json
- token_id not present in accepted_token_ids
- expected: INVALID_PAYMENT

erc1155_payment.batch_disallowed.json
- transfer_event_hash starts with 4a39dc06
- batch_allowed false
- expected: INVALID_PAYMENT

erc1155_payment.reference_mismatch.json
- valid proof except payment_reference changed
- expected: INVALID_PAYMENT
```

## Deterministic Test Vectors

Append to `.github/workflows/deterministic-verify.yml`:

```bash
python3 tools/alms.py payment-refresh fixtures/payments/erc1155_profile.v0_1.json | tee /tmp/alms_erc1155_refresh.out
test "$(cat /tmp/alms_erc1155_refresh.out)" = "PROFILE_VALID"

python3 tools/alms.py payment-bind fixtures/receipts/valid_signed.json fixtures/payments/erc1155_profile.v0_1.json | tee /tmp/alms_erc1155_bind.out
# compare to committed fixture reference once computed

python3 tools/alms.py payment-verify fixtures/payments/erc1155_profile.v0_1.json fixtures/payments/erc1155_payment.valid.json | tee /tmp/alms_erc1155_verify.out
test "$(cat /tmp/alms_erc1155_verify.out)" = "VALID_PAYMENT"

python3 tools/alms.py payment-verify fixtures/payments/erc1155_profile.v0_1.json fixtures/payments/erc1155_payment.invalid_token_id.json | tee /tmp/alms_erc1155_bad_token.out
test "$(cat /tmp/alms_erc1155_bad_token.out)" = "INVALID_PAYMENT"

python3 tools/alms.py payment-verify fixtures/payments/erc1155_profile.v0_1.json fixtures/payments/erc1155_payment.batch_disallowed.json | tee /tmp/alms_erc1155_batch_disallowed.out
test "$(cat /tmp/alms_erc1155_batch_disallowed.out)" = "INVALID_PAYMENT"

python3 tools/alms.py payment-verify fixtures/payments/erc1155_profile.v0_1.json fixtures/payments/erc1155_payment.reference_mismatch.json | tee /tmp/alms_erc1155_ref_mismatch.out
test "$(cat /tmp/alms_erc1155_ref_mismatch.out)" = "INVALID_PAYMENT"
```

## Merge Rule

Do not merge executable adapter code until CI witnesses both positive and negative fixtures.

## Boundary

```text
authority: false
receipt_core_mutation: forbidden
payment_dispatch_only: true
```
