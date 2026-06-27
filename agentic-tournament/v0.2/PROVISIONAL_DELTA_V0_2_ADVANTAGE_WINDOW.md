# PROVISIONAL_DELTA_V0_2_ADVANTAGE_WINDOW

**Status:** PROVISIONAL_HELD  
**Authority:** false  
**Claim level:** observation_only  
**Parent receipt:** agentic_tournament_v0.1  
**Activation condition:** Cycle 001 receipt must be completed and sealed with concrete telemetry.  
**Delta type:** additive_only  
**Tri-rule posture:** survival -> accumulate -> advantage-only  

## Purpose

Formalize `advantage_window` as a measurable engagement state for v0.2 without changing the v0.1 survival-first equilibrium.

This delta is held until Cycle 001 produces evidence. It does not activate automatically.

## Constraint Lock

1. No v0.2 activation before Cycle 001 telemetry exists.
2. No modification to survival priority.
3. No recursion or autonomous strategy mutation.
4. One delta only: define and log `advantage_window`.
5. If telemetry is incomplete, mark v0.2 as `HELD_NO_ACTIVATION`.

## Proposed Field

```json
{
  "advantage_window": {
    "state": "open | closed | unknown",
    "score": 0,
    "inputs": {
      "local_resources": 0,
      "objective_value": 0,
      "risk": 0,
      "survival_factor": 1
    },
    "decision": "engage | hold | retreat",
    "evidence_refs": []
  }
}
```

## Proposed Scoring Heuristic

```text
advantage_score = (local_resources + objective_value - risk) * survival_factor
```

## Initial Interpretation

- `advantage_score > 0` may support engagement only if survival priority is not violated.
- `advantage_score <= 0` supports hold or retreat.
- `survival_factor = 0` forces retreat regardless of apparent opportunity.

## Failure Discriminator

`advantage_window` helps distinguish:

1. **overfight_loop** — engagement continues after advantage window closes.
2. **late_retreat** — survival factor collapses before disengagement.
3. **legitimate_engagement** — advantage window opens, action occurs, exit happens before counter-collapse.

## Activation Procedure

After Cycle 001:

1. Complete `cycle_001_receipt.template.json` with real telemetry.
2. Seal Cycle 001 receipt.
3. Compute observed advantage windows from evidence.
4. If evidence supports the field, activate as `agentic_tournament_v0.2`.
5. If evidence does not support it, keep this file as `PROVISIONAL_HELD`.

## Anchor Targets On Activation

- IPFS packet
- EAS attestation on Base
- ENS / jaywisdom.eth reference
- Witness / ALMS replay packet

## Current Position

Position held: survival -> accumulate -> advantage-only.

Envelope pristine. Awaiting first qualifier surface.
