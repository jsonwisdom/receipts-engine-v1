# Anchor 001 Compatibility

## Status

This verifier, `receipts-engine-v1`, supports the **Looking Glass** ENS-based anchor model.

Anchor 001 uses a different model: GitHub commit plus EAS on-chain attestation.

This file prevents drift between the older ENS-first verifier surface and the current canonical Anchor 001 trust path.

## Anchor 001 — Canonical State

| Field | Value |
|---|---|
| Source Repo | `jsonwisdom/Welcome-to-JSONWISDOM` |
| Git Commit | `13004719dd0c34f765ca95dfe8566b6feb2bf6cf` |
| Merkle Root (SHA-256) | `ff55160908ff41d23f7af0df8873ef7a0dcf8163d1a308f58941e87b5a95bad9` |
| Leaf Keccak-256 | `0xb7e55f9e1f4f27cd96f38d74e6510e184a14772ef3f9f628d5acc68531dd185d` |
| EAS Schema UID | `0x3bab210b4da3faff084e146075caf9168efb5c9c87f18509bca2c07d7f2e49c` |
| EAS Attestation UID | `0x18b5b00c62c648df2ccf4a746645493fa2a0b0dcda6697052d8c3a3d1586c142` |
| Chain | Base |
| ENS | `DEFERRED` |

## Verification Path

1. Clone `jsonwisdom/Welcome-to-JSONWISDOM`.
2. Check out commit `13004719dd0c34f765ca95dfe8566b6feb2bf6cf`.
3. Run `./scripts/merkle-build.sh` and confirm Merkle root `ff55160908ff41d23f7af0df8873ef7a0dcf8163d1a308f58941e87b5a95bad9`.
4. Run `./scripts/keccak-leaf.sh examples/sample-record.json` and confirm leaf Keccak `0xb7e55f9e1f4f27cd96f38d74e6510e184a14772ef3f9f628d5acc68531dd185d`.
5. Verify EAS attestation UID `0x18b5b00c62c648df2ccf4a746645493fa2a0b0dcda6697052d8c3a3d1586c142` on Base.

## ENS Model — Legacy Looking Glass

The ENS-first verifier in this repo remains available for Looking Glass artifacts that use text records on `jaywisdom.base.eth`.

Expected Looking Glass text keys:

```text
lookingglass.brief.sha256
lookingglass.brief.cid
lookingglass.brief.tx
```

Those keys are not required for Anchor 001.

## Boundary

ENS is optional discovery for Anchor 001, not a required trust layer.

The canonical trust path is:

```text
GitHub commit → JCS canonical bytes → SHA-256 → Keccak-256 → EAS attestation on Base
```

Rule: no ghost anchor.
