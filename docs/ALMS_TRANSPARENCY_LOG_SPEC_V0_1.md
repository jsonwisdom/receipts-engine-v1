# ALMS Transparency Log Spec V0.1

## Genesis Entry 0

receipt_hash: `cd6f730c46b5a0255c21d0bce30d8a2bebb1a6fc654b0150de0784ad0c1c2427`

timestamp: `2026-07-07T08:57:37Z`

merge_commit: `a4247024201c456e7b648aabebee76c714fbe36e`

verifier: `ALMS deterministic-verify`

status: `VALID`

---

## Append Rules

- Only CI-gated `VALID` receipts may be appended.
- Append-only JSONL log.
- Merkle tree provides inclusion proofs.
- Public replay nodes SHOULD mirror the log.
- Auditor revocation handled through trust anchors.

---

## CLI

```text
alms log-append <receipt.json>

alms log-verify --hash <receipt_hash> --proof <proof.json>
```

---

## Boundary

```text
authority: false
```
