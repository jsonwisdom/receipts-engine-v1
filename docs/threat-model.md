# Receipt Backbone Threat Model v0.1

> Status: Narrow MVP threat model

This threat model intentionally covers only the first vertical slice.

Receipt Backbone v0.1 aims to prove what happened inside an instrumented workflow. It does not prove that the agent was correct, that the external world was honest, or that the runtime was uncompromised before instrumentation.

## Assets

| Asset | Why It Matters |
|---|---|
| Receipt core bytes | Primary evidence packet for agent action. |
| Receipt hash | Stable identity for the receipt. |
| Signing key | Binds receipt bytes to a producer identity. |
| Policy version | Prevents silent policy drift. |
| Replay bundle | Allows independent reproduction of receipt hash. |

## Threats and Mitigations

| Threat | Description | MVP Mitigation |
|---|---|---|
| Receipt modification | A receipt is edited after generation. | Digital signatures over canonical receipt bytes. |
| Receipt deletion | A receipt is removed from the local log. | Hash chaining or append-only log in later versions; v0 records deletion risk explicitly. |
| Policy drift | A policy changes without being visible in the receipt. | Every receipt includes `policy_id` and `policy_version`. |
| Replay mismatch | Replay produces a different hash from the original run. | Deterministic serialization and replay metadata. |
| Runtime compromise | The agent runtime lies before receipt creation. | Out of scope for v0; must be stated clearly. |
| External dependency dishonesty | A tool or API returns false information. | Out of scope for v0 unless the dependency output is independently verified. |
| Clock manipulation | Timestamp does not reflect real-world time. | Timestamp is treated as metadata, not proof of truth. |
| Key compromise | Signing key is stolen or misused. | Key rotation and revocation are future work; v0 identifies public key ID. |

## Security Claims Allowed in v0

Receipt Backbone v0.1 may claim:

- The receipt bytes match the recorded receipt hash.
- The receipt signature verifies against the declared public key.
- The receipt records a specific action, input hash, output hash, policy version, and policy decision.
- Replay can reproduce the same receipt hash when inputs and replay bundle are unchanged.

## Security Claims Not Allowed in v0

Receipt Backbone v0.1 must not claim:

- The agent made the correct decision.
- The policy was the correct policy.
- The runtime was fully trustworthy.
- External dependencies behaved honestly.
- The receipt proves legal or factual truth beyond the recorded execution.

## MVP Boundary

The first demo should stay inside this flow:

```text
one tool call -> one policy evaluation -> one signed receipt -> one replay verification
```

Anything beyond that belongs in v0.2 or later.
