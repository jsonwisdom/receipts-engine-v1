# AGENTIC_TOURNAMENT_RECEIPT_V0_1

**Status:** CANONICAL_DRAFT  
**Authority:** false  
**Claim level:** observation_only  
**Operator:** Jay Wisdom / jaywisdom.eth  
**Purpose:** Turn each Agentic Tournament cycle into a replayable receipt with bounded claims, explicit triggers, telemetry, failure modes, and one controlled delta per redeploy.

## Invariants

1. No truth claim beyond observed telemetry.
2. No causal claim without replay evidence.
3. One delta per redeploy cycle.
4. Agent behavior must map to declared triggers.
5. Failed triggers are preserved, not rewritten.
6. Identity anchor records attribution only; it does not prove performance.

## v0.1 Squad Vector

- **Squad Version:** v0.1
- **Primary Objective:** qualify through durable resource accumulation while avoiding negative-value fights.
- **Secondary Objective:** capture opportunistic objectives only when local advantage is present.
- **Risk Budget:** preserve squad survivability over short-term combat upside.
- **Operating Posture:** survive first, farm second, fight only with advantage.

## Explicit Triggers

### T1 — Survival Priority

**Condition:**
- Agent survivability drops below safe threshold.
- Squad is outnumbered locally.
- Fight becomes a negative resource trade.

**Action:**
- Disengage.
- Regroup.
- Preserve agent.
- Resume safer route.

### T2 — Resource Differential Fallback

**Condition:**
- Enemy resource lead exceeds threshold.
- Squad loses repeated engagements in same zone.
- Objective cost exceeds expected reward.

**Action:**
- Abandon contested zone.
- Farm safer route.
- Delay combat.
- Re-enter only after resource parity improves.

### T3 — Advantage Engagement

**Condition:**
- Local advantage is detected.
- Enemy is isolated or weakened.
- Objective reward exceeds survival risk.

**Action:**
- Focus fire.
- Secure objective.
- Exit before counter-collapse.

## Telemetry Fields

- timestamp_start
- timestamp_end
- qualifier_window
- map_or_mode
- wins
- losses
- resources_gained
- deaths
- objectives_captured
- retreats_triggered
- failed_triggers
- unexpected_behavior

## First Failure Modes To Extract

1. **Overfight Loop:** agents continue fighting after advantage disappears.
2. **Late Retreat:** survival trigger fires after fatal damage window.
3. **Farm Paralysis:** squad avoids fights but fails to convert resources into rank.

## Delta Rule

Each redeploy may change exactly one of:

- threshold
- route priority
- engagement rule
- fallback rule
- squad composition

No multi-variable mutation unless cycle is marked INVALID_FOR_COMPARISON.

## Anchor Targets

- IPFS metadata packet
- EAS attestation on Base
- ENS / jaywisdom.eth reference
- Witness / ALMS replay packet
