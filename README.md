# Receipts Engine v1

Deterministic, reproducible, and cryptographically verifiable release.

## Status

TIER 3: REBUILD → VERIFY → SIGN → DOCUMENTED

Independent verification requires only this repository, the release assets, and cosign. No trust in the author is required.

---

## Artifact

receipts_engine_v1.tar.gz

---

## Checksum (source-anchored)

See:

receipts_engine_v1.tar.gz.sha256

Expected:

9f73ce11d4bc0f9870ee1a9e46d45c9526632b8defd14a7f378f50d0497d3942  receipts_engine_v1.tar.gz

---

## Verification

```bash
sha256sum -c receipts_engine_v1.tar.gz.sha256

cosign verify-blob \
  --bundle receipts_engine_v1.tar.gz.sigstore.json \
  --certificate-identity jaywisdom@proton.me \
  --certificate-oidc-issuer https://github.com/login/oauth \
  receipts_engine_v1.tar.gz
```

Expected result:

Verified OK

---

## Build Provenance

The artifact is deterministically rebuilt from source using:

```bash
./build.sh
```

The rebuild must produce a byte-identical tarball matching the published checksum before signing.

---

## Correction Notice

The original published hash was not reproducible from the source tree. This release replaces it with a deterministic rebuild.

---

## Summary

This repository provides a full zero-trust verification chain:

source → deterministic build → checksum → signature → transparency → independent verification

