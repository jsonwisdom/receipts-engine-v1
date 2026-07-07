# ERC20 Payment Profile V0.1

## Purpose

Define a parameter layer for replayable ERC-20 payment verification without mutating canonical ALMS receipts.

The receipt remains canonical. The payment profile is loaded beside the receipt and verified against chain-derived payment proof data.

## Profile Fields

- payment_profile_version
- chain_id
- token_address
- token_symbol
- token_decimals
- min_payment
- max_payment
- payee

## Proof Fields

- chain_id
- token_address
- token_decimals
- amount
- payer
- payee
- tx_hash
- block_number
- transfer_event_hash
- receipt_hash
- payment_reference

## Invariants

1. chain_id must match the configured network.
2. token_address must match the expected asset.
3. token_decimals must match the token metadata.
4. transferred amount must be within policy bounds.
5. payment_reference must bind the transfer to exactly one receipt_hash and payment profile.
6. the payment proof must expose an ERC-20 Transfer event hash prefix.
7. receipt_hash and payment_reference must remain immutable after issuance.

## CLI

```text
alms payment-bind <receipt.json> <profile.json>
alms payment-verify <profile.json> <proof.json>
alms payment-refresh <profile.json>
```

## Boundary

authority: false
