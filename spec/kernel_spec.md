# Receipts Engine v1 — Kernel Spec

## Purpose
Deterministically evaluate eligibility + proof inputs and return a decision.

## Inputs
- `eligibility_flags`: object
  - `eligible`: boolean
- `attendance_proof`: array of strings
- `prior_state`: string or null

## Rules
1. If `eligible` is false → `DENY`
2. If `eligible` is true and `attendance_proof` is empty → `HOLD`
3. If `eligible` is true and `attendance_proof` has at least 1 item → `APPROVE`

## Determinism Constraints
- No system time
- No randomness
- No network access
- No environment-variable dependence
- Same input must produce same output

## Outputs
- `decision`: `APPROVE` | `DENY` | `HOLD`
- `receipt_hash`: SHA-256 of canonical input + decision
- `new_state_hash`: SHA-256 of prior_state + receipt_hash
