# ERC1155 Payment Adapter V0.1

## Purpose

Define an ERC-1155 adapter over the existing ALMS payment profile abstraction.

The adapter does not mutate canonical receipts. It extends payment proof verification with `token_id`, `units`, and batch-aware transfer semantics while preserving the same replay and transparency model.

## Adapter Fields

- payment_profile_version
- asset_standard
- chain_id
- token_address
- accepted_token_ids
- min_units
- max_units
- payee
- batch_allowed

## Proof Fields

- chain_id
- token_address
- token_id
- units
- payer
- payee
- tx_hash
- block_number
- transfer_event_hash
- receipt_hash
- payment_reference
- batch_index

## Invariants

1. `chain_id` matches the configured network.
2. `token_address` matches the ERC-1155 contract.
3. `token_id` is explicitly accepted.
4. `units` are within policy bounds.
5. `payment_reference` binds receipt_hash + profile + token_id + payee.
6. Batch transfers require `batch_allowed: true`.
7. `receipt_hash` and `payment_reference` are immutable.

## CLI

```text
alms payment-bind <receipt.json> <profile.json>
alms payment-verify <profile.json> <proof.json>
alms payment-refresh <profile.json>
