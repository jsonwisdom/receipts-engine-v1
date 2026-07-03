# LLM Radar Workflow

LLM Radar turns model-market alerts into replayable ReceiptOS evaluation tasks.

## Boundary

Email alerts are signals only. ReceiptOS replay is verification.

## Flow

```text
FreeLLM change detected
  -> email alert
  -> Gmail label: LLM Radar
  -> GitHub issue created from Model Radar Alert template
  -> benchmark and repo-task replay
  -> hash outputs
  -> update models/model_registry.json
  -> append receipts/model_alerts.jsonl
```

## Tracked alert classes

- New free model available
- Model goes offline
- Rate limit changes
- Context window changes
- API endpoint changes
- Provider removes free tier
- New coding-capable model appears

## GitHub issue labels

- model-scout
- freellm
- needs-replay

## Receipt rule

A registry update should not land unless the issue includes replay evidence and a receipt entry with `authority: false`.
