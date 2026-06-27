# V0_2_REFINEMENT_REVIEW_ADVANTAGE_WINDOW

**Status:** PROVISIONAL_REFINEMENT_ACCEPTED_HELD  
**Authority:** false  
**Claim level:** review_only  
**Parent sealed receipt:** `agentic-tournament/cycle-001/CYCLE_001_SEALED_RECEIPT.json`  
**Active contract:** v0.1  
**Next state:** Cycle 002 telemetry intake

## Refinement Under Review

```json
{
  "delta_id": "v0.2",
  "field": "advantage_window",
  "definition": "Contiguous period where local_state.advantage_score > threshold AND survival_status == alive",
  "entry_condition": "advantage_score = (local_resources + objective_value - risk) * survival_factor",
  "scoring_function": "deterministic_cycle_002_evidence_derived",
  "boundary": "survival_weighted_non_recursive"
}
```

## Review Notes

### Definition

Accepted as provisional. The field only applies while survival status remains alive.

### Entry Condition

Accepted as provisional.

```text
advantage_score = (local_resources + objective_value - risk) * survival_factor
```

All operands must come from Cycle 002 telemetry.

### Scoring Function

Accepted as provisional but inactive. Scoring begins only after Cycle 002 evidence provides the required scalar inputs.

### Boundary

Accepted as provisional. The refinement is survival-weighted and non-recursive. It does not replace the anti-recursion guard or synchronization-drift guard.

## Verdict

```text
DRAFT_ACCEPTED_PROVISIONAL_HELD
```

## Preserved Boundaries

- No policy expansion.
- No mutation of the v0.1 receipt structure.
- No activation of v0.2.
- No scoring before Cycle 002 evidence.
- No recursion.
- No silent promotion.

## Current Posture

```text
v0.1: ACTIVE
Cycle_001: SEALED
v0.2_advantage_window: PROVISIONAL_HELD
v0.2_anti_recursion_guard: PROVISIONAL_HELD
v0.2_synchronization_drift_guard: PROVISIONAL_HELD
Cycle_002: AWAITING_FIRST_PACKET
```

## Next Input

Cycle 002 packet telemetry.
