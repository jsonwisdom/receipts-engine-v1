# Checkpoint Layer v2.6

This directory documents the next public checkpoint layer for the receipt engine.

```text
GitHub merge commit
-> manifest hash
-> content-addressed storage pointer
-> public attestation pointer
-> receipt pointer
```

## Status

Current values are placeholders until a real storage pin and public attestation transaction are submitted.

## Rule

The public checkpoint proves the record existed. Replay proves what the record means.

## Authority

`authority=false`

This layer records integrity metadata. It is not a final finding.
