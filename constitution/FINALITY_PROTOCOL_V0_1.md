# FINALITY_PROTOCOL_V0_1

## Status

Draft constitutional protocol.

## Signal Core

The schema defines the shape of evidence.

The protocol defines the validity of evidence.

No `SLAM_DUNK_RECEIPT` is valid unless it is governed by a finality protocol that existed before or at the same commit boundary as the receipt instance.

Protocol before instance.

Law before case law.

## Constitutional Position

A receipt without a governing protocol is an orphan record.

A receipt governed by `FINALITY_PROTOCOL_V0_1` is admissible, verifiable, contestable, and replayable under known rules.

## Scope

This protocol governs finality events inside the JAYCONSTITUTION replay-native architecture, including but not limited to:

- `SLAM_DUNK_RECEIPT` events,
- public replay anchors,
- receipt-sealed state transitions,
- fork-state conflict records,
- lineage-preserving constitutional artifacts.

## Core Rule

A finality event is valid only when the system can say:

> This happened. Anyone may replay it. No one may rewrite it.

## Definitions

### Event

A bounded occurrence submitted for replay verification.

An Event may be a commit, transaction, attestation, receipt, document hash, calldata anchor, signature packet, or other replayable artifact.

### Witness

A person, key, contract, system, repository, chain, or verifier that observes or signs an Event.

A Witness does not create truth. A Witness creates evidence.

### Finality

The state in which an Event has satisfied the admissibility, witness, replay, lineage, and conflict-resolution requirements of this protocol.

Finality does not equal sovereignty.

### SLAM_DUNK

A receipt-sealed finality event that survives replay and cannot be rewritten without visible fork or contradiction.

### Replay Defense

The process by which any participant may challenge a finality event by replaying the Event path, recomputing references, and surfacing mismatch, fork, taint, or contradiction.

## Admissibility Requirements

An Event is admissible only if it contains or points to:

1. `event_id`
2. `event_type`
3. `artifact_path` or external artifact reference
4. `content_hash` or equivalent deterministic digest
5. `timestamp`
6. `lineage_pointer`
7. `replay_steps`
8. `authority=false` unless separately promoted by a constitutional process
9. `protocol_version="FINALITY_PROTOCOL_V0_1"`

Narrative-only claims are inadmissible.

Market activity is inadmissible as proof of constitutional legitimacy.

Attention, volume, holder count, price, or virality may be recorded as observations only.

## Witness Requirements

A valid finality event requires at least one admissible Witness.

A Witness must provide at least one of:

- cryptographic signature,
- repository commit reference,
- chain transaction reference,
- verifiable attestation,
- deterministic system log,
- content-addressed artifact reference.

Witnesses are evidence surfaces, not authorities.

No witness may silently promote an observation into truth.

## Replay Requirements

A finality event must include replay steps sufficient for an independent observer to recompute or inspect the Event path.

Replay steps must include:

1. source artifact location,
2. hash or digest method,
3. expected output,
4. verification command or procedure where available,
5. known limitations,
6. conflict path if mismatch is found.

If replay fails, the Event is not final. It enters `CONTESTED` or `TAINTED` state.

## Finality Thresholds

An Event reaches `SLAM_DUNK` finality only when all of the following are true:

1. The Event is admissible.
2. At least one valid Witness exists.
3. Replay steps are present.
4. Lineage pointer is present.
5. No unresolved conflict record exists.
6. Authority remains explicitly bounded.
7. The Event can be independently replayed without relying on narrative trust.

Optional chain-based thresholds may be added by receipt type, including block depth or confirmation count.

Optional repository thresholds may be added by receipt type, including signed commits or protected branch merges.

## Conflict Resolution

If two or more receipts claim finality over overlapping Events, the system must not choose a winner by narrative preference.

Conflict handling order:

1. Recompute hashes.
2. Inspect lineage pointers.
3. Compare protocol versions.
4. Check witness validity.
5. Check timestamps and commit boundaries.
6. Surface fork state.
7. Mark unresolved conflicts as `CONTESTED`.

Forks are lawful if lineage is preserved.

Lineage erasure is inadmissible.

## States

A finality event may hold one of the following states:

- `DRAFT`
- `ADMISSIBLE`
- `WITNESSED`
- `REPLAYABLE`
- `SLAM_DUNK`
- `CONTESTED`
- `TAINTED`
- `FORKED`
- `REJECTED`

Only `SLAM_DUNK` represents receipt-sealed finality.

No state represents absolute truth.

## Refusal Rules

The system must reject:

- narrative-only proof,
- market-price proof,
- hype-based legitimacy,
- unsigned authority claims,
- lineage-free forks,
- retroactive protocol assignment,
- receipts with missing replay paths,
- witnesses treated as authorities.

## Authority Boundary

`authority=false` is the default and required state.

Promotion requires a separate constitutional process and cannot be inferred from finality.

`CONSTITUTIONALLY_SEALED` does not equal `SOVEREIGN`.

Standing emerges only through replay.

## Canonical Finality Phrase

> This happened. Anyone may replay it. No one may rewrite it.

## Implementation Order

1. Commit `FINALITY_PROTOCOL_V0_1`.
2. Define `SLAM_DUNK_RECEIPT_SCHEMA_V0_1` against this protocol.
3. Generate first receipt instance only after the protocol exists.
4. Attach receipt to commit, transaction, or content-addressed artifact.
5. Record conflicts as observations, not truth claims.

## Non-Goals

This protocol does not create a token launch.

This protocol does not create market legitimacy.

This protocol does not declare sovereignty.

This protocol defines the rules under which a finality event may be admitted, replayed, contested, and sealed.

## Closing Rule

No finality without protocol.

No receipt without replay.

No replay without lineage.

Jaywisdom.eth ⚙️⚖️🏀
