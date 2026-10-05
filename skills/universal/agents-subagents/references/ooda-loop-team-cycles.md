---
description: Observe-Orient-Decide-Act applied to agent-team review cadences and synthesis sensemaking.
last_verified: 2026-09-16
status: stable
---

# OODA Loop for Agent Team Review Cycles

Observe-Orient-Decide-Act applied to agent team review cadences, sensemaking in team synthesis, and decision speed vs. quality tradeoffs. Based on Boyd's OODA theory and 2026 multi-agent orchestration patterns.

## Contents

- [Team Reviews as OODA Cycles](#team-reviews-as-ooda-cycles)
- [Mapping Team Phases to OODA](#mapping-team-phases-to-ooda)
- [Orientation as Sensemaking](#orientation-as-sensemaking)
- [Tempo in Review Cadences](#tempo-in-review-cadences)
- [Speed vs. Quality Tradeoffs](#speed-vs-quality-tradeoffs)
- [Team OODA Anti-Patterns](#team-ooda-anti-patterns)
- [Enhancing Existing Teams with OODA](#enhancing-existing-teams-with-ooda)
- [Decision Checklist](#decision-checklist)

---

## Team Reviews as OODA Cycles

Every agent team review is an OODA cycle. Treating it explicitly as OODA improves both quality and speed.

### The Classical Review (Implicit OODA)

Most review teams follow an implicit OODA loop:

```
Read context → Form opinions → Discuss → Decide → Execute
```

But without explicit structure, each phase is muddled — observation mixes with opinion, orientation is hidden, decisions rely on vibes, and actions often lack clear feedback.

### The Explicit OODA Review

```
Observe (all members read context in parallel)
  ↓
Orient (each member articulates interpretation from their lens)
  ↓
Decide (synthesis owner selects action from alternatives)
  ↓
Act (execute decision)
  ↓
Observe outcomes → loop
```

Making each phase explicit catches errors that implicit cycles miss.

---

## Mapping Team Phases to OODA

### Standard Review Flow with OODA

| OODA Phase | Team Activity | Members |
|-----------|---------------|---------|
| **Observe** | Read context, gather evidence | All members in parallel |
| **Orient** | Each member produces interpretation | All members independently |
| **Decide** | Synthesis owner integrates and chooses | Synthesis owner |
| **Act** | Execute decision | Handoff team or implementer |

### Example: `expert-board` Monetization-mode OODA

```
Observe phase:
  - pricing-advisor reads: current pricing, historical changes
  - marketing-product-analytics reads: conversion data, funnel metrics
  - marketing-strategist reads: positioning, competitive pricing
  - startup-operating-system-reviewer reads: cash flow, revenue projections
  - business-developer reads: customer feedback, deal data

Orient phase:
  - pricing-advisor: "Current pricing under-captures value on annual plans"
  - product-analytics: "Trial-to-paid conversion is acceptable, but expansion is weak"
  - marketing-strategist: "Message doesn't match target segment's WTP"
  - finance-ops: "Revenue stable but concentration risk in top 10 customers"
  - business-developer: "Customers ask for usage-based options"

Decide phase (synthesis owner):
  Given orientations, the decision is: test usage-based tier alongside existing flat tiers.
  Alternatives considered: raise existing prices, add enterprise tier, keep status quo.
  Selected because: usage-based tier captures expansion without raising acquisition friction.
  Confidence: medium — requires validation before full rollout.

Act phase:
  Handoff: Product/engineering team builds usage-based tier
  Experiment: Offer to 10% of new customers in next quarter
  Observation for next cycle: conversion rate, revenue per customer, churn
```

### Why Explicit OODA Improves Team Quality

| Without Explicit OODA | With Explicit OODA |
|----------------------|-------------------|
| Members mix observation with opinion | Observations separated from interpretation |
| Orientation is hidden in reasoning | Interpretation is explicit and comparable |
| Decisions jump from data to action | Alternatives considered explicitly |
| No feedback loop planned | Next cycle's observations defined in advance |

---

## Orientation as Sensemaking

### The Sensemaking Moment

In team reviews, the **orient phase is where the real work happens**. Raw observations become meaning. Different members can observe the same data and produce radically different interpretations.

### Weick's Sensemaking Lens

Organizational theorist Karl Weick described sensemaking as:

1. **Extracting cues** from the environment
2. **Selecting a plausible frame** to interpret them
3. **Updating identity and action** based on the frame

For agent teams, sensemaking = orientation. Each team member is a sensemaker, bringing their domain's frame to the observations.

### Productive Sensemaking in Teams

| Property | How to Foster |
|----------|---------------|
| **Multiple frames considered** | Each member explicitly states their lens |
| **Disconfirmation welcome** | "What would change my interpretation?" |
| **Uncertainty acknowledged** | Confidence levels per interpretation |
| **Frame conflicts surfaced** | Disagreements about meaning, not just facts |
| **Integration over averaging** | Synthesis owner builds coherent view from multiple lenses |

### Anti-Sensemaking Patterns

| Pattern | Problem |
|---------|---------|
| **False consensus** | Members agree to avoid conflict — loses information |
| **Frame hegemony** | One member's frame dominates — loses diversity |
| **Observation only** | Team reports data without interpretation — decision has no basis |
| **Interpretation without data** | Members state opinions without grounding |
| **Circular sensemaking** | Frames never update based on evidence |

---

## Tempo in Review Cadences

### Match Cadence to Decision Speed Requirements

| Decision Type | OODA Cycle Time | Team Pattern |
|--------------|:---------------:|--------------|
| **Incident response** | Minutes | Small team, fast cycles, clear playbook |
| **Tactical decisions** | Hours | Standard review team |
| **Strategic reviews** | Days-weeks | Full review with deep orientation |
| **Quarterly planning** | Weeks | Multiple iterations of OODA |

### Fast Team OODA

For tactical decisions needing fast cycles:

```
Observe (30 min): Each member reads context
Orient (30 min): Each produces 5-point summary of their view
Decide (15 min): Synthesis owner chooses from alternatives
Act: Execute and prepare observations for next cycle
Total cycle: ~90 minutes
```

### Slow Team OODA

For strategic decisions needing depth:

```
Observe (days): Each member does deep research
Orient (days): Members produce full analyses
Decide (session): Team discusses and decides
Act: Rollout plan with milestones
Total cycle: 1-2 weeks
```

### The Cadence Mismatch Problem

Common failure: running strategic-cadence OODA on tactical decisions (too slow), or tactical-cadence OODA on strategic decisions (too shallow).

**Rule**: Match OODA depth to decision reversibility and impact.

---

## Speed vs. Quality Tradeoffs

### The Tempo Advantage (for Teams)

In dynamic situations, a team that cycles OODA faster beats a slower team even if the slower team has better analysis. This is Boyd's core insight applied to reviews:

- Fast review + quick execution + feedback + fast review → adaptive advantage
- Slow review + late execution + delayed feedback → reactive disadvantage

### When Speed Matters

| Situation | Prefer Speed |
|-----------|:-----------:|
| Market moving rapidly | Yes |
| Competitive pressure | Yes |
| Experimentation context | Yes |
| Reversible decisions | Yes |
| Information rapidly changing | Yes |

### When Quality Matters More

| Situation | Prefer Quality |
|-----------|:-------------:|
| Irreversible decisions | Yes |
| High stakes / low trials | Yes |
| Regulatory / compliance | Yes |
| Stable environment | Yes |
| Coordination costs of redo | Yes |

### The Fast-Enough Rule

In most situations, you don't need optimal speed — you need speed that's faster than the environment changes. If the market is evolving monthly, weekly OODA beats monthly OODA. Daily OODA adds no additional value.

---

## Team OODA Anti-Patterns

| Anti-Pattern | OODA Failure | Fix |
|-------------|--------------|-----|
| **Endless observation** | Team gathers data without orienting | Time-box observation phase |
| **Orientation without data** | Opinions without evidence | Require citations per interpretation |
| **Decision by consensus** | Averaging away disagreement | Preserve dissent, synthesis owner decides |
| **Action without feedback** | Execution without measuring | Define success metrics in the decide phase |
| **Zombie cycles** | Same decisions repeatedly | Break the loop with external input or orientation reset |
| **Frame lock-in** | Team stuck in one interpretation | Explicitly consider counter-frames |
| **No memory between cycles** | Each review starts from scratch | Persistent orientation across cycles |
| **Observation by the wrong members** | People gathering data outside their expertise | Assign observation tasks to specialized members |

---

## Enhancing Existing Teams with OODA

### Upgrade Path for Workflow Modes

An `expert-board` mode contract can be enhanced with explicit OODA phases:

```yaml
# Existing fields
workflow: expert-board
board: monetization
panel: [...]
synthesis_owner: pricing-advisor

# OODA enhancement
workflow:
  observe:
    duration: 60min
    parallel: true
    output: evidence summary per member
  orient:
    duration: 60min
    parallel: true
    output: interpretation + confidence + key uncertainty
    require_disconfirmation: true
  decide:
    owner: synthesis_owner
    output: chosen action + alternatives considered + success metrics
  act:
    handoff: defined in team-specific playbook
    feedback_loop: observations for next cycle

cadence:
  type: strategic  # tactical | strategic | incident
  frequency: quarterly
```

### Launch Prompt Enhancement

Add OODA structure to launch prompts:

```
OBSERVE phase (read these sources):
  - pricing-advisor: current pricing, historical changes
  - analytics-lead: funnel data, conversion cohorts
  - ...

ORIENT phase (produce these interpretations):
  Each member outputs:
    - Key finding (1-2 sentences)
    - Evidence cited
    - Confidence level
    - One counter-interpretation that could also fit the data

DECIDE phase:
  Synthesis owner (pricing-advisor) produces:
    - Chosen recommendation
    - Alternatives considered and rejected
    - Success metrics for validation
    - Next cycle trigger (when to review again)

ACT phase:
  Handoff to: [execution team]
  Observation for next cycle: [specific metrics to watch]
```

---

## Decision Checklist

- [ ] Each team review has explicit OODA phases, not implicit
- [ ] Observation phase is parallel — members gather in parallel, not sequentially
- [ ] Orientation phase requires explicit interpretation + confidence + counter-frame
- [ ] Decision phase considers alternatives, not just the first option
- [ ] Action phase defines success metrics for next cycle's observation
- [ ] Cadence matches decision type (tactical fast, strategic slow)
- [ ] Zombie cycles detected and broken (external input, orientation reset)
- [ ] Disconfirmation actively sought in orient phase
- [ ] Memory persists between cycles (orientation builds on history)
- [ ] Speed sufficient for environmental change rate

---

## Sources

- Boyd, J. (1976-1996). OODA loop theory
- Weick, K. (1995). *Sensemaking in Organizations*
- Osinga, F. (2007). *Science, Strategy and War*
- NVIDIA LLo11yPop, Snyk Agentic OODA (2026 production examples)
- Related: `game-theory-agent-teams.md` (belief-driven coordination, Shapley scoring)
- Related: `ooda-loop-agent-architecture.md` in ai-agents (individual agent level)
