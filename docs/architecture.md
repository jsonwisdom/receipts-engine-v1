# Receipt Backbone Architecture v0.1

> Verifiable governance for GitHub agent workflows

Receipt Backbone is an adoption-first layer. It instruments existing agent workflows instead of replacing them.

## MVP Flow

```text
GitHub Agent
    ↓
Receipt Hook
    ↓
Policy Check
    ↓
Signed Receipt
    ↓
Replay Bundle
    ↓
Independent Verifier
```

## Components

| Component | Responsibility |
|---|---|
| GitHub Agent | Performs the original workflow action. |
| Receipt Hook | Captures action metadata, input hash, and output hash. |
| Policy Check | Applies a versioned rule set and records pass/fail. |
| Signed Receipt | Produces tamper-evident evidence of the action. |
| Replay Bundle | Stores the deterministic material needed to reproduce the receipt hash. |
| Independent Verifier | Validates hash, signature, policy metadata, and replay result. |

## Four Verifiable Properties

| Property | Success Criterion |
|---|---|
| Receipt generation | Every agent action emits a signed record. |
| Policy evaluation | Every receipt records pass/fail with rule version. |
| Replay | Same inputs reproduce the same receipt hash. |
| Independent verification | Third party validates without trusting the runtime. |

## Design Boundary

Receipt Backbone v0.1 is not a full governance runtime.

It is the smallest useful evidence layer for agent workflows:

```text
record -> hash -> policy -> sign -> replay -> verify
```

The verifier is the trust root. The runtime is only a receipt producer.

## Integration Pattern

The integration point should remain one hook:

```ts
const receipt = await receiptHook({
  actor,
  action,
  input,
  output,
  policy
});
```

A team should be able to adopt the hook without redesigning its agent architecture.
