# Receipt Backbone Verifier

> Status: Stub

The verifier is the trust root for the Receipt Backbone MVP.

It should validate:

1. Receipt schema version
2. Canonical receipt hash
3. Signature
4. Policy metadata
5. Replay hash match

The verifier must not need access to the original agent runtime.
