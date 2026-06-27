# PROVISIONAL_DELTA_V0_2_ANTI_RECURSION_GUARD

**Status:** PROVISIONAL_HELD  
**Authority:** false  
**Claim level:** observation_only  
**Parent receipt:** `cycle_001_receipt.ingested.json`  
**Observed failure mode:** `PACKET_RETRANSMISSION_RECURSION`  
**Delta type:** additive_only  
**Activation posture:** held until Cycle 001 seal verification is complete or missing fields are explicitly marked UNKNOWN in final sealed form.  

## Purpose

Add a deterministic anti-recursion guard before enabling `advantage_window` scoring.

This delta exists because Cycle 001 surfaced `PACKET_RETRANSMISSION_RECURSION`, which is a structural ingestion hazard. Advantage scoring must not activate while retransmission recursion remains unguarded.

## Constraint Lock

1. No strategy mutation.
2. No advantage scoring activation.
3. No recursive packet emission.
4. No silent promotion from ingestion to seal.
5. One delta only: reject duplicate packet retransmission by `packet_id`.

## Guard Rule

```python
if packet_id in retransmission_cache:
    reject(packet)
else:
    retransmission_cache.add(packet_id)
    accept(packet)
```

## Deterministic Interpretation

A packet is eligible for ingestion only if its `packet_id` has not already appeared in the current retransmission cache.

If the `packet_id` is already present, the packet is rejected as duplicate retransmission and must be logged as:

```text
REJECTED_DUPLICATE_PACKET_RETRANSMISSION
```

## Required Fields

```json
{
  "packet_id": "string",
  "packet_hash": "string",
  "first_seen_at": "string",
  "retransmission_cache_status": "MISS | HIT",
  "decision": "ACCEPT | REJECT",
  "reason": "NEW_PACKET | REJECTED_DUPLICATE_PACKET_RETRANSMISSION"
}
```

## Replay Rule

Given the same ordered packet stream, the guard must produce the same sequence of ACCEPT / REJECT decisions.

No timestamps may override cache membership.
No narrative explanation may override packet identity.
No duplicate packet may mutate existing accepted telemetry.

## Failure Mode Coverage

This guard directly addresses:

```text
PACKET_RETRANSMISSION_RECURSION
```

It does not resolve:

```text
SYNCHRONIZATION_DRIFT_THRESHOLD_EXCEEDED
```

Synchronization drift remains a separate observed failure mode and must not be silently folded into this delta.

## Relationship To Advantage Window

The previous provisional v0.2 advantage-window delta remains held.

`advantage_window` scoring may only be reconsidered after:

1. Cycle 001 is sealed or explicitly finalized with UNKNOWN fields.
2. Anti-recursion guard is applied to the ingestion path.
3. Duplicate retransmission behavior is no longer observed.
4. Required scalar advantage inputs become measurable.

## Current Posture

v0.1 active.  
Cycle 001 ingested but not fully sealed.  
v0.2 advantage_window held.  
v0.2 anti-recursion guard provisional.  
No silent promotion.  
No strategy drift.
