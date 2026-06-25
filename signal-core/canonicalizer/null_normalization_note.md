# Pending null normalization hardening

The canonicalizer must treat optional `null` and missing optional fields as the same canonical state.

Required behavior:

- drop top-level keys whose value is `null`
- drop claim-level keys whose value is `null`
- drop pointer/provenance keys whose value is `null`
- omit empty provenance blocks after normalization

This note exists because the direct source-code patch was blocked by the GitHub connector safety layer during update. The gauntlet vectors and manifest were updated first; the source patch still needs to be applied before TC-05 can pass.
