# GH-600 Mapping: Receipt Backbone

> Status: Draft mapping for adoption-first MVP

Receipt Backbone is positioned as a drop-in verifiable governance layer for GitHub agent workflows.

It does not replace a GitHub agent runtime. It instruments the runtime and emits independently verifiable artifacts.

## Mapping Table

| GH-600 Domain | Receipt Backbone Extension | Concrete Artifact |
|---|---|---|
| Agent architecture | Receipt instrumentation | `receipt_hook()` around agent actions |
| Tool use | Tool receipts | `action.type = tool_call` with input/output hashes |
| Memory/state | State transition receipts | `action.type = state_transition` |
| Evaluation | Replay verification | `replay.bundle_id` and receipt hash reproduction |
| Multi-agent | Cross-agent provenance | `actor.id`, `run_id`, and sequence ordering |
| Guardrails | Versioned constitutional policies | `policy.policy_id`, `policy_version`, `decision` |

## Example: Agent Architecture

```ts
const result = await receiptHook({
  actor: "example-agent",
  action: "tool_call",
  toolName: "echo",
  input: { message: "hello receipt backbone" }
});
```

## Example: Tool Use

```json
{
  "action": {
    "type": "tool_call",
    "tool_name": "echo",
    "input_sha256": "sha256:<hex>",
    "output_sha256": "sha256:<hex>"
  }
}
```

## Example: Memory / State

```json
{
  "action": {
    "type": "state_transition",
    "from_sha256": "sha256:<previous-state>",
    "to_sha256": "sha256:<next-state>"
  }
}
```

## Example: Evaluation

```bash
node verifier/verify-receipt.js receipts/gh600-demo.receipt.json
node replay/replay-bundle.js examples/gh600-demo/replay-bundle.json
```

Expected result:

```text
signature: pass
policy: pass
replay_hash_match: pass
```

## Example: Multi-Agent Provenance

```json
{
  "run_id": "gh600-demo-001",
  "sequence": 2,
  "actor": {
    "type": "github-agent",
    "id": "review-agent"
  }
}
```

## Example: Guardrails

```json
{
  "policy": {
    "policy_id": "default-policy",
    "policy_version": "0.1.0",
    "decision": "pass"
  }
}
```

## Adoption Boundary

GH-600 teams should be able to adopt Receipt Backbone without changing their runtime architecture.

The MVP integration requirement is one hook:

```text
agent action -> receipt hook -> policy check -> signed receipt -> replay bundle
```

That is the adoption wedge.
