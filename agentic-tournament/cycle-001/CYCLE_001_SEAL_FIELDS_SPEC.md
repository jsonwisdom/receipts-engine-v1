# CYCLE_001_SEAL_FIELDS_SPEC

**Status:** FIELD_SPEC_LOCKED  
**Authority:** false  
**Claim level:** validation_rules_only  
**Target receipt:** `cycle_001_receipt.ingested.json`  
**Purpose:** Define the exact missing telemetry fields required before Cycle 001 can become sealable.

## Sealability Gate

Cycle 001 is sealable only if all required fields are populated with concrete values or explicitly finalized as `UNKNOWN_FINAL`.

If any required field remains plain `UNKNOWN`, seal status must remain:

```text
INGESTION_COMPLETE_AWAITING_SEAL
```

## Required Missing Fields

### 1. termination_timestamp

**Type:** string  
**Format:** ISO-8601 UTC preferred  
**Example:** `2026-06-27T19:45:00Z`

**Validation:**

- Must be greater than or equal to `timestamp_start` if start is known.
- Must not be inferred from narrative.
- If unavailable, use `UNKNOWN_FINAL` only at finalization.

### 2. final_packet_count

**Type:** integer  
**Minimum:** 0

**Validation:**

- Must equal the number of packets included in the final telemetry set.
- Must not count rejected duplicate retransmissions as accepted packets.
- Quarantined packets may be counted separately if a quarantine log exists.

### 3. drift_measurement_log

**Type:** array

Each entry must include:

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

**Validation:**

- No timestamp may be invented.
- Observed drift must be reproducible from expected and observed timestamps when both are known.
- Any packet exceeding threshold must be quarantined.
- Quarantined packets must not activate downstream scoring.

### 4. integrity_checksum

**Type:** string  
**Recommended:** SHA-256 hex digest

**Validation:**

- Must hash the complete canonical telemetry set.
- Canonicalization rule must be declared.
- Recommended canonicalization: JSON Canonicalization Scheme style sorted keys, no whitespace significance.
- If checksum is unavailable, Cycle 001 is not hash-sealable.

## Additional Seal Inputs Still Required From v0.1

The original v0.1 telemetry fields also remain required or must be finalized as `UNKNOWN_FINAL`:

```text
wins
losses
resources_gained
deaths
objectives_captured
retreats_triggered
timestamp_start
timestamp_end
qualifier_window
map_or_mode
```

## Deterministic Seal Decision

```python
if any_required_field == "UNKNOWN":
    seal_status = "INGESTION_COMPLETE_AWAITING_SEAL"
elif integrity_checksum in ["", "UNKNOWN", "UNKNOWN_FINAL"]:
    seal_status = "FINALIZED_NOT_HASH_SEALABLE"
else:
    seal_status = "SEALABLE"
```

## v0.2 Activation Boundary

Even if Cycle 001 becomes `SEALABLE`, v0.2 advantage scoring remains held unless the telemetry also includes measurable:

```text
local_resources
objective_value
risk
survival_factor
```

If those are absent, the lawful v0.2 status remains:

```text
HELD_NO_ACTIVATION
```

## Current Instruction

Populate the missing fields from observed telemetry only. Do not infer. Do not backfill from memory. Do not promote v0.2 inside Cycle 001.
