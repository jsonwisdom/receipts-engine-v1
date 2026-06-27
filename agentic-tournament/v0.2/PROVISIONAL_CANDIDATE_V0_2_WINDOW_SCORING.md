# PROVISIONAL_CANDIDATE_V0_2_WINDOW_SCORING

**Status:** PROVISIONAL_CANDIDATE_HELD  
**Authority:** false  
**Claim level:** candidate_only  
**Active contract:** v0.1  
**Activation dependency:** Cycle 002 packet evidence  

## Purpose

Prepare a deterministic scoring candidate for `advantage_window` without activating it.

This candidate remains inactive until Cycle 002 produces measurable scalar inputs and observed window boundaries.

## Candidate Definition

```text
advantage_window = contiguous period where advantage_score > threshold AND survival_status == alive
```

## Candidate Formula

```text
advantage_score = (local_resources + objective_value - risk) * survival_factor
```

## Required Inputs

```text
local_resources
objective_value
risk
survival_factor
survival_status
advantage_window_entry
advantage_window_exit
```

## Threshold Rule

The threshold must be explicitly declared before scoring.

If no threshold is declared, scoring state remains:

```text
SCORING_HELD_NO_THRESHOLD
```

## Window States

```text
WINDOW_OPEN
WINDOW_CLOSED
WINDOW_UNKNOWN
SCORING_HELD_NO_THRESHOLD
SCORING_HELD_MISSING_INPUTS
```

## Valid Transition

```text
WINDOW_UNKNOWN -> WINDOW_OPEN -> WINDOW_CLOSED
```

## Invalid Transitions

```text
WINDOW_CLOSED -> WINDOW_OPEN without new packet evidence
WINDOW_UNKNOWN -> WINDOW_CLOSED without observed entry
WINDOW_OPEN -> WINDOW_OPEN by duplicate packet retransmission
```

## Deterministic Scoring Rule

```python
if missing_required_inputs:
    state = "SCORING_HELD_MISSING_INPUTS"
elif threshold is None:
    state = "SCORING_HELD_NO_THRESHOLD"
elif survival_status != "alive":
    state = "WINDOW_CLOSED"
elif advantage_score > threshold:
    state = "WINDOW_OPEN"
else:
    state = "WINDOW_CLOSED"
```

## Guard Dependencies

This candidate depends on the prior provisional guards:

1. Anti-recursion guard must reject duplicate retransmission.
2. Synchronization-drift guard must quarantine timing divergence.
3. No quarantined packet may open or close an advantage window.

## Activation Boundary

This candidate is not active.

It may move from `PROVISIONAL_CANDIDATE_HELD` to `CANDIDATE_EVIDENCE_READY` only after Cycle 002 provides measurable inputs and observed window boundaries.

## Current Posture

```text
v0.1 active
Cycle 001 sealed
Cycle 002 awaiting first packet
v0.2 candidate held
advantage scoring inactive
```
