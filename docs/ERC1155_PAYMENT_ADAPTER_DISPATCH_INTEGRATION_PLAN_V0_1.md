# ERC1155 Payment Adapter Dispatch Integration Plan V0.1

## Purpose

Define the implementation path for routing `payment-refresh`, `payment-bind`, and `payment-verify` across ERC-20 and ERC-1155 profiles without changing ALMS receipt-core verification.

## Core Principle

The CLI remains unified. Adapter selection happens only after profile loading.

```text
receipt verification: unchanged
payment profile loading: shared
payment adapter dispatch: profile-driven
payment result stdout: canonical
```

## Profile Loading

All payment commands load `profile.json` first.

Required behavior:

1. Read JSON as UTF-8.
2. Fail closed on malformed JSON.
3. Require the loaded value to be an object.
4. Inspect `asset_standard`.
5. Route to adapter-specific validator.

## Dispatch Table

```text
asset_standard missing -> ERC20 verifier
asset_standard == "erc20" -> ERC20 verifier
asset_standard == "erc1155" -> ERC1155 verifier
otherwise -> invalid profile or INVALID_PAYMENT
```

This preserves compatibility with existing ERC20 fixtures where `asset_standard` is not present.

## CLI Routing

### payment-refresh

```text
load profile
select adapter
run adapter profile validator
PROFILE_VALID if true
PROFILE_INVALID if false
```

### payment-bind

```text
load receipt
load profile
require receipt.receipt_hash
select adapter
run adapter profile validator
compute adapter payment_reference
print payment_reference
```

Failure stdout:

```text
INVALID
```

### payment-verify

```text
load profile
load proof
select adapter
run adapter payment verifier
VALID_PAYMENT if true
INVALID_PAYMENT if false
```

## ERC20 Compatibility Rule

Existing ERC20 behavior must remain stable:

```text
payment_profile_version == ERC20_PAYMENT_PROFILE_V0_1
asset_standard missing OR asset_standard == erc20
payment_reference excludes token_id
```

Existing ERC20 fixture must still pass:

```text
fixtures/payments/erc20_profile.v0_1.json
fixtures/payments/erc20_payment.valid.json
```

## ERC1155 Adapter Rule

ERC1155 profile requires:

```text
payment_profile_version == ERC1155_PAYMENT_ADAPTER_V0_1
asset_standard == erc1155
accepted_token_ids: non-empty list[str]
min_units: integer string
max_units: integer string
batch_allowed: bool
```

ERC1155 proof requires:

```text
token_id: str
units: integer string
transfer_event_hash startswith c3d58168 OR 4a39dc06
batch_index rules enforced
payment_reference recomputes exactly
```

## Error Paths

All error paths fail closed.

```text
malformed JSON -> invalid
profile not object -> invalid
unknown asset_standard -> invalid
missing required profile field -> invalid
missing required proof field -> INVALID_PAYMENT
reference mismatch -> INVALID_PAYMENT
unsupported event hash -> INVALID_PAYMENT
batch proof with batch_allowed false -> INVALID_PAYMENT
single proof with non-null batch_index -> INVALID_PAYMENT
```

## Canonical Stdout

```text
verify -> VALID | INVALID
payment-refresh -> PROFILE_VALID | PROFILE_INVALID
payment-bind -> <payment_reference> | INVALID
payment-verify -> VALID_PAYMENT | INVALID_PAYMENT
```

No additional stdout is allowed in deterministic CI steps.

## Test Bindings

### ERC20 regression

```bash
python3 tools/alms.py payment-refresh fixtures/payments/erc20_profile.v0_1.json
python3 tools/alms.py payment-bind fixtures/receipts/valid_signed.json fixtures/payments/erc20_profile.v0_1.json
python3 tools/alms.py payment-verify fixtures/payments/erc20_profile.v0_1.json fixtures/payments/erc20_payment.valid.json
```

Expected:

```text
PROFILE_VALID
3c3be77111337595cf3e2639a7bd79ee33aeb8475b3511ce0cd8e5c03de6fc85
VALID_PAYMENT
```

### ERC1155 positive

```bash
python3 tools/alms.py payment-refresh fixtures/payments/erc1155_profile.v0_1.json
python3 tools/alms.py payment-bind fixtures/receipts/valid_signed.json fixtures/payments/erc1155_profile.v0_1.json
python3 tools/alms.py payment-verify fixtures/payments/erc1155_profile.v0_1.json fixtures/payments/erc1155_payment.valid.json
```

Expected:

```text
PROFILE_VALID
<computed_erc1155_reference>
VALID_PAYMENT
```

### ERC1155 negative

```bash
python3 tools/alms.py payment-verify fixtures/payments/erc1155_profile.v0_1.json fixtures/payments/erc1155_payment.invalid_token_id.json
python3 tools/alms.py payment-verify fixtures/payments/erc1155_profile.v0_1.json fixtures/payments/erc1155_payment.batch_disallowed.json
python3 tools/alms.py payment-verify fixtures/payments/erc1155_profile.v0_1.json fixtures/payments/erc1155_payment.reference_mismatch.json
```

Expected:

```text
INVALID_PAYMENT
INVALID_PAYMENT
INVALID_PAYMENT
```

## Implementation Order

1. Add ERC1155 fixtures.
2. Add adapter profile validators.
3. Add adapter-specific payment reference function.
4. Add dispatch wrapper around existing ERC20 verifier.
5. Add ERC1155 payment verifier.
6. Extend deterministic CI with ERC20 regression and ERC1155 positive/negative tests.
7. Confirm no receipt-core diff beyond payment-layer changes.

## Merge Gate

Adapter code can merge only when:

```text
ALMS receipt verify -> VALID
ERC20 regression -> PASS
ERC1155 positive -> PASS
ERC1155 negatives -> fail closed
release gate -> PASS
```

## Boundary

```text
authority: false
receipt_core_mutation: forbidden
payment_dispatch_only: true
```
