# DOGE Procurement Overlay v2.5 — Anchor Registry

## Purpose

The anchor registry is a public integrity checkpoint for replayable procurement audit packages.

```text
Bundle = canonical evidence
Graph = projection
Anchor = timestamped receipt
Replay wins every dispute
```

## Doctrine

An anchor proves that an audit package existed in a declared integrity state at a specific time.

It does **not** prove guilt, intent, fraud, corruption, or criminal conduct.

## Files

- `anchors.jsonl` — append-only anchor records.
- `anchor_manifest.json` — manifest describing allowed states, guardrails, and file hashes.

## Allowed States

- `VERIFIED`
- `INCOMPLETE`
- `INCONSISTENT`
- `REVIEW_REQUIRED`
- `INVALID`

## Canonical Rule

The replay bundle is canonical. Neo4j or other graph exports are projections. If the graph conflicts with the bundle, the bundle controls.

## Local Integrity Check

```bash
sha256sum anchors/anchors.jsonl anchors/anchor_manifest.json
```

Expected current hashes:

```text
865ad382b6acbddbcd93160636a7ce0f70983fd27d6c22664853524217bc3628  anchors/anchors.jsonl
45f6fb0b89f64991d66a5bf3d923e1174c04334228641bed8745b02e62f660ba  anchors/anchor_manifest.json
```

## Authority

`authority=false`

This registry is an evidence integrity layer, not a truth engine.
