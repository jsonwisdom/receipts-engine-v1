# Receipt Backbone Replay

> Status: Stub

Replay reproduces the receipt hash from deterministic input material.

For v0.1, replay should:

1. Load the replay bundle.
2. Load the referenced input, output, and policy files.
3. Rebuild canonical receipt core bytes.
4. Recompute SHA-256.
5. Compare against the recorded receipt hash.

Replay proves hash reproducibility, not external truth.
