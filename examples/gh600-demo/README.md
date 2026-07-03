# GH-600 Demo: Receipt Backbone Vertical Slice

> Status: MVP stub

This example demonstrates one complete vertical slice:

```text
one tool call -> receipt hook -> policy evaluation -> signed receipt -> replay bundle
```

## Demo Goal

Prove the four Receipt Backbone properties in the smallest possible workflow:

| Property | Demo Check |
|---|---|
| Receipt generation | `receipts/gh600-demo.receipt.json` exists. |
| Policy evaluation | Receipt includes policy decision and version. |
| Replay | Replay bundle reproduces receipt hash. |
| Independent verification | Verifier can validate without access to runtime. |

## Minimal Tool Call

The first tool is intentionally simple:

```text
echo("hello receipt backbone") -> "hello receipt backbone"
```

The point is not tool complexity. The point is end-to-end verifiability.

## Expected Files

```text
examples/gh600-demo/
├── README.md
├── tool-call.input.json
├── tool-call.output.json
└── replay-bundle.json
```

## Intended Command Shape

```bash
node examples/gh600-demo/run-demo.js
node verifier/verify-receipt.js receipts/gh600-demo.receipt.json
node replay/replay-bundle.js examples/gh600-demo/replay-bundle.json
```

## Expected Result

```text
receipt_generated: pass
policy_evaluated: pass
signature_verified: pass
replay_hash_match: pass
```

## Boundary

This demo proves a recorded execution trace stayed stable under verification.

It does not prove the agent was correct or that external dependencies were honest.
