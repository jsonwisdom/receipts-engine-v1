# PROVISIONAL_DELTA_V0_2_SYNCHRONIZATION_DRIFT_GUARD

**Status:** PROVISIONAL_HELD  
**Authority:** false  
**Claim level:** observation_only  
**Parent receipt:** `cycle_001_receipt.ingested.json`  
**Observed failure mode:** `SYNCHRONIZATION_DRIFT_THRESHOLD_EXCEEDED`  
**Delta type:** additive_only  
**Activation posture:** held until Cycle 001 seal verification is complete or missing fields are explicitly marked UNKNOWN in final sealed form.  

## Purpose

Add a deterministic synchronization-drift guard before enabling `advantage_window` scoring.

Cycle 001 surfaced `SYNCHRONIZATION_DRIFT_THRESHOLD_EXCEEDED`, which indicates ordering, pacing, or timestamp divergence in the telemetry stream. This must remain separate from packet retransmission recursion.

## Constraint Lock

1. No strategy mutation.
2. No advantage scoring activation.
3. No timestamp inference from narrative.
4. No silent correction of event order.
5. One delta only: reject or quarantine packets whose observed timing exceeds drift tolerance.

## Guard Rule

```python
observed_drift = abs(observed_timestamp - expected_timestamp)

if observed_drift > drift_threshold:
    quarantine(packet)
else:
    accept(packet)
```

## Deterministic Rejection State

```text
QUARANTINED_SYNCHRONIZATION_DRIFT_THRESHOLD_EXCEEDED
```

## Required Fields

```json
{
  "packet_id": "string",
  "expected_timestamp": "string",
  "observed_timestamp": "string",
  "drift_threshold_ms": 0,
  "observed_drift_ms": 0,
  "decision": "ACCEPT | QUARANTINE",
  "reason": "WITHIN_DRIFT_THRESHOLD | QUARANTINED_SYNCHRONIZATION_DRIFT_THRESHOLD_EXCEEDED"
}
```

## Replay Rule

Given the same ordered packet stream, expected timestamps, observed timestamps, and drift threshold, the guard must produce the same ACCEPT / QUARANTINE decisions.

No packet may be reordered silently.
No missing timestamp may be invented.
No narrative explanation may override observed drift.
No quarantined packet may activate downstream scoring.

## Failure Mode Coverage

This guard directly addresses:

```text
SYNCHRONIZATION_DRIFT_THRESHOLD_EXCEEDED
```

It does not resolve:

```text
PACKET_RETRANSMISSION_RECURSION
```

Packet retransmission recursion remains covered only by:

```text
PROVISIONAL_DELTA_V0_2_ANTI_RECURSION_GUARD
```

## Relationship To Advantage Window

The provisional v0.2 `advantage_window` delta remains held.

`advantage_window` scoring may only be reconsidered after:

1. Cycle 001 is sealed or explicitly finalized with UNKNOWN fields.
2. Anti-recursion guard is applied to the ingestion path.
3. Synchronization-drift guard is applied to the timing path.
4. Required scalar advantage inputs become measurable.

## Current Posture

v0.1 active.  
Cycle 001 ingested but not fully sealed.  
v0.2 advantage_window held.  
v0.2 anti-recursion guard provisional.  
v0.2 synchronization-drift guard provisional.  
No silent promotion.  
No strategy drift.
