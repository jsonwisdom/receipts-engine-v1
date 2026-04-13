# Release Verification — Tier 2 Locked

## Artifact
receipts_engine_v1.tar.gz

## Checksum (source anchored)
See: receipts_engine_v1.tar.gz.sha256

## Verification Commands

```bash
sha256sum -c receipts_engine_v1.tar.gz.sha256

cosign verify-blob \
  --bundle receipts_engine_v1.tar.gz.sigstore.json \
  --certificate-identity jaywisdom@proton.me \
  --certificate-oidc-issuer https://github.com/login/oauth \
  receipts_engine_v1.tar.gz
```

## Build Provenance

Artifact is rebuilt deterministically using build.sh before signing.

## Status

TIER 2: REBUILD → VERIFY → SIGN

This closes the supply chain loop.
