# Store Release EAS Output

The build tool writes `eas-payload.json` into the generated artifact directory.

This directory does **not** contain a private key, signer, transaction sender, RPC credential, or broadcast routine.

Receipt Core v0.4 anchor used by the payload:

```text
network = Base
schema_number = 1618
schema_uid = 0xa5b0d2dd5470542a119d50eba19898f50e1f77591f01d4fec4c6f3075054aa11
schema_creator_rail = 0xC345B26094c63C69222Ee775189a3d3eaead5a84
```

```text
PAYLOAD_GENERATED != ATTESTATION_BROADCAST
SCHEMA_CREATOR_RAIL != CURRENT_SIGNER
EAS_ATTESTATION != WALLET_CONTROL
BUNDLE_ROOT != WORLD_TRUE
AUTHORITY_CREATED = FALSE
```
