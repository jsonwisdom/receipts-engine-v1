# ERC1155 Payment Adapter Execution Checklist V0.1

## Phase 0: Preconditions

- PR #43 is merged.
- `ERC20_PAYMENT_PROFILE_V0_1` is canonical on `main`.
- `tools/alms.py` already supports the unified payment CLI surface.
- Receipt core verification remains unchanged.

## Phase 1: Fixture Creation

Add these fixtures:

```text
fixtures/payments/erc1155_profile.v0_1.json
fixtures/payments/erc1155_payment.valid.json
fixtures/payments/erc1155_payment.invalid_token_id.json
fixtures/payments/erc1155_payment.batch_disallowed.json
fixtures/payments/erc1155_payment.reference_mismatch.json
```

### Required fixture outputs

```text
erc1155_profile.v0_1.json -> PROFILE_VALID
erc1155_payment.valid.json -> VALID_PAYMENT
erc1155_payment.invalid_token_id.json -> INVALID_PAYMENT
erc1155_payment.batch_disallowed.json -> INVALID_PAYMENT
erc1155_payment.reference_mismatch.json -> INVALID_PAYMENT
```

## Phase 2: Dispatch Code

Modify `tools/alms.py` only inside the payment layer.

### Dispatcher rule

```text
profile.asset_standard missing -> ERC20 verifier
profile.asset_standard == "erc20" -> ERC20 verifier
profile.asset_standard == "erc1155" -> ERC1155 verifier
otherwise -> INVALID_PAYMENT
```

### Forbidden changes

```text
receipt verifier mutation: forbidden
signed payload mutation: forbidden
receipt_hash rule mutation: forbidden
signature rule mutation: forbidden
```

## Phase 3: ERC1155 Profile Validation

`payment-refresh` must return `PROFILE_VALID` only when:

1. `payment_profile_version == "ERC1155_PAYMENT_ADAPTER_V0_1"`.
2. `asset_standard == "erc1155"`.
3. `chain_id` is an integer.
4. `token_address` is a non-empty string.
5. `accepted_token_ids` is a non-empty list of strings.
6. `min_units` and `max_units` are integer strings.
7. `payee` is a non-empty string.
8. `batch_allowed` is boolean.

## Phase 4: ERC1155 Payment Verification

`payment-verify` must return `VALID_PAYMENT` only when:

1. Profile validates.
2. Proof `chain_id` matches profile `chain_id`.
3. Proof `token_address` matches profile `token_address` after lowercase normalization.
4. Proof `token_id` is in `accepted_token_ids`.
5. Proof `units` is within `[min_units, max_units]`.
6. Proof `payee` matches profile `payee` after lowercase normalization.
7. `payer`, `tx_hash`, `block_number`, and `receipt_hash` are present.
8. Single transfer event starts with `c3d58168`.
9. Batch transfer event starts with `4a39dc06`.
10. Batch transfer requires `batch_allowed == true` and integer `batch_index`.
11. Single transfer has `batch_index == null` or no `batch_index`.
12. `payment_reference` recomputes exactly.

## Phase 5: Binding Rule

For ERC-1155:

```text
payment_reference = sha256(JCS({
  receipt_hash,
  payment_profile_version,
  asset_standard,
  chain_id,
  token_address,
  token_id,
  payee
}))
```

Normalize `token_address` and `payee` to lowercase before hashing.

## Phase 6: Deterministic Tests

Extend `.github/workflows/deterministic-verify.yml` with:

```bash
python3 tools/alms.py payment-refresh fixtures/payments/erc1155_profile.v0_1.json | tee /tmp/alms_erc1155_refresh.out
test "$(cat /tmp/alms_erc1155_refresh.out)" = "PROFILE_VALID"

python3 tools/alms.py payment-bind fixtures/receipts/valid_signed.json fixtures/payments/erc1155_profile.v0_1.json | tee /tmp/alms_erc1155_bind.out
test "$(cat /tmp/alms_erc1155_bind.out)" = "<computed_reference>"

python3 tools/alms.py payment-verify fixtures/payments/erc1155_profile.v0_1.json fixtures/payments/erc1155_payment.valid.json | tee /tmp/alms_erc1155_valid.out
test "$(cat /tmp/alms_erc1155_valid.out)" = "VALID_PAYMENT"

python3 tools/alms.py payment-verify fixtures/payments/erc1155_profile.v0_1.json fixtures/payments/erc1155_payment.invalid_token_id.json | tee /tmp/alms_erc1155_bad_token.out
test "$(cat /tmp/alms_erc1155_bad_token.out)" = "INVALID_PAYMENT"

python3 tools/alms.py payment-verify fixtures/payments/erc1155_profile.v0_1.json fixtures/payments/erc1155_payment.batch_disallowed.json | tee /tmp/alms_erc1155_batch.out
test "$(cat /tmp/alms_erc1155_batch.out)" = "INVALID_PAYMENT"

python3 tools/alms.py payment-verify fixtures/payments/erc1155_profile.v0_1.json fixtures/payments/erc1155_payment.reference_mismatch.json | tee /tmp/alms_erc1155_ref.out
test "$(cat /tmp/alms_erc1155_ref.out)" = "INVALID_PAYMENT"
```

## Phase 7: Verification Commands

Run locally or in CI:

```bash
python3 tools/alms.py verify fixtures/receipts/valid_signed.json
python3 tools/alms.py payment-refresh fixtures/payments/erc20_profile.v0_1.json
python3 tools/alms.py payment-verify fixtures/payments/erc20_profile.v0_1.json fixtures/payments/erc20_payment.valid.json
python3 tools/alms.py payment-refresh fixtures/payments/erc1155_profile.v0_1.json
python3 tools/alms.py payment-verify fixtures/payments/erc1155_profile.v0_1.json fixtures/payments/erc1155_payment.valid.json
```

Expected canonical stdout:

```text
VALID
PROFILE_VALID
VALID_PAYMENT
PROFILE_VALID
VALID_PAYMENT
```

## Phase 8: Merge Gate

Do not merge ERC-1155 executable adapter code until:

- positive ERC-1155 fixture passes
- all negative ERC-1155 fixtures fail closed
- ERC-20 fixture still passes
- ALMS receipt verifier still emits `VALID`
- release gate passes

## Boundary

```text
authority: false
receipt_core_mutation: forbidden
payment_dispatch_only: true
```
