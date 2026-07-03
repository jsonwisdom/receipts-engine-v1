---
name: Model Radar Alert
about: Evaluate a FreeLLM or provider-change alert before registry update
title: "Evaluate model alert: <provider/model/change>"
labels: model-scout, freellm, needs-replay
assignees: ''
---

## Signal

- Alert source: FreeLLM email alert
- Gmail label: LLM Radar
- Alert type:
  - [ ] New free model available
  - [ ] Model offline
  - [ ] Rate limit change
  - [ ] Context window change
  - [ ] API endpoint change
  - [ ] Free tier removed
  - [ ] New coding-capable model appears

## Claim Boundary

Email alert is a signal only. ReceiptOS replay is verification.

## Evaluation Checklist

- [ ] Capture alert text or source reference
- [ ] Run benchmark
- [ ] Run repo task
- [ ] Hash output
- [ ] Compare cost and latency
- [ ] Update `model_registry.json`
- [ ] Emit receipt into `receipts/model_alerts.jsonl`

## Receipt Fields

- receipt_id:
- prev_hash:
- event_hash:
- model:
- provider:
- change_type:
- observed_at:
- verifier:
- authority: false

## Notes

Add raw observations here. Do not promote the alert to a verified claim until replay evidence is attached.
