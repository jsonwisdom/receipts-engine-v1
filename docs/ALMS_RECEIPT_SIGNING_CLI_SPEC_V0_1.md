# ALMS Receipt Signing CLI Spec V0.1

## Commands

`alms sign --input <unsigned.json> --key <auditor_key.pem> --output <signed.json>`

`alms verify --input <signed.json>`

## Requirements
- ed25519 signatures
- JCS canonicalization for determinism
- Exit 0 on VALID

## Fixtures
fixtures/receipts/valid_*