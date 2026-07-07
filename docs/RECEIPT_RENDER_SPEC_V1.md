# Receipt Render Spec V1

## Purpose

`alms receipt-render` provides a deterministic ReceiptOS rendering surface for human triage, markdown publication, and JSONL machine ingestion.

Renderer output is not authority. It is user-facing provenance over existing receipt and witness data.

```text
authority:false
render != witness
render_hash = user-saw provenance
```

## CLI

```text
alms receipt-render <witness.json> [--format=term|jsonl|md] [--verbose] [--trace] [--with-render-hash] [--verify <hash>]
```

## Authority Footer Canon

Human render modes, including terminal and markdown, must use a pipe-delimited footer:

```text
authority: false | status: confirmed | ts: 1741449600 | collapsed: true
```

Delimiters are canonical:

```text
pipe | separates fields
colon : separates key and value
all fields are required
boolean values are lowercase
status is pending | confirmed | failed
ts is UNIX epoch integer
```

JSONL mode must emit a structured object:

```json
{"authority":{"valid":false,"status":"confirmed","timestamp":1741449600,"collapsed":true}}
```

## Render Modes

### term

Default mode. Emits a compact triage header, adapter block, witness footer, and authority footer.

### jsonl

One JSON object per line. Keys must be deterministic and sorted by the emitter.

Required top-level fields:

```text
adapter
authority
payment_adapter_block
proof_summary
receipt_core
witness
```

### md

GitHub-flavored markdown tables. The authority row must preserve the same semantics as terminal and JSONL output.

## ANSI Policy

Only the following ANSI codes are allowed:

```text
bold:    \033[1m
dim:     \033[2m
reverse: \033[7m
```

Forbidden:

```text
italic
underline
color codes of any kind
```

The aesthetic layer must never depend on color semantics.

## Render Hash

`--with-render-hash` emits a BLAKE3 digest over the final rendered bytes. For terminal output, ANSI is stripped before hashing. Runtime hash emission is optional.

If BLAKE3 is unavailable, implementations may fail closed or use a clearly internal fallback only for local test surfaces. Canonical production emission is BLAKE3.

## Exit Codes

```text
0 success
1 render-hash mismatch
2 malformed witness
3 unsupported adapter
4 I/O or path error
5 internal render failure
```

## Golden Fixtures

Required fixture classes:

```text
erc20_basic.witness.json
erc1155_batch.witness.json
discriminated_union.witness.json
token_id_collapse.witness.json
zero_amount.witness.json
corrupt_proof.witness.json
```

## Boundary

```text
authority:false preserved
receipt core mutation forbidden
renderer is presentation only
```