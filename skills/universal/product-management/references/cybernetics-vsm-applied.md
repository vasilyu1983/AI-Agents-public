---
description: Cybernetics and VSM applied to product management — squad autonomy (S1), PM-of-PMs as S3, discovery as S4, product principles as S5, shared roadmap and experiment calendar as S2, SEV escalation as algedonic channels, recursive product orgs, and coverage checks on opportunity solution trees. Adapter over foundations-cybernetics-vsm; theory lives in the foundation.
status: stable
---

# Cybernetics and VSM Applied: Product Management

> **Gate before invoking:** Check [`foundations-cybernetics-vsm` § When to Apply](../../foundations-cybernetics-vsm/SKILL.md#when-to-apply) first. If the skip conditions fire, use the foundation it routes to instead.

This file maps the VSM onto product squads, roadmaps, discovery and escalation. It does not restate the theory:

- System definitions (S1–S5, S3*, recursion): [primitives overview](../../foundations-cybernetics-vsm/references/primitives-overview.md)
- Ashby's Law, attenuators and amplifiers: [02-ashbys-law](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/02-ashbys-law.md) and [response coverage audit](../../foundations-cybernetics-vsm/references/response-coverage-audit.md)
- Algedonic channel design and testing: [11-algedonic-channels](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/11-algedonic-channels.md)
- Generic traps: [foundation anti-patterns](../../foundations-cybernetics-vsm/SKILL.md#anti-patterns) and [patterns, scenarios, traps](../../foundations-cybernetics-vsm/references/patterns-scenarios-traps.md)

## Table of Contents

- [Product Org to VSM Map](#product-org-to-vsm-map)
- [Pattern Catalog](#pattern-catalog)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
- [Recipes](#recipes)
- [Cross-References](#cross-references)
- [Sources](#sources)

---

## Product Org to VSM Map

| VSM function | Product-management mechanism | Healthy signal | Failure signal |
| --- | --- | --- | --- |
| S1 operations | Squads owning a funnel stage, segment or metric | Squad ships and runs experiments without case-by-case approval | Approval queue for copy changes and A/B tests |
| S2 coordination | Experiment calendar, shared roadmap as visibility surface, metric-ownership matrix | Concurrent tests do not share a segment and funnel stage | Uninterpretable results from overlapping experiments |
| S3 control | Head of product / PM-of-PMs: capacity allocation, outcome agreements, policies | Decisions are resource or policy decisions | Leader approves individual tickets and tests |
| S3* audit | Leader reads raw tickets, joins an interview unannounced | Picture of reality differs from status reports and gets reconciled | Only filtered status updates reach S3 |
| S4 intelligence | Continuous discovery, competitive and regulatory scanning, technology horizon | Findings change capacity allocation | Research only validates designed features |
| S5 identity | Product principles that resolve cross-squad conflicts | Past conflicts get a clear answer from the principles | "Whoever argues loudest wins" |
| Algedonic channel | SEV path for customer-breaking defects, trust and safety events | Critical issues reach the accountable PM and eng lead outside the sprint queue | Critical issue sits in the backlog for days |

---

## Pattern Catalog

### P1 — Product Squads as S1: Autonomy Within Policy

A squad is a correct S1 when it has a defined primary activity and environmental boundary (for example, the retention squad owns engagement signals and the activation-to-habit funnel), resources negotiated at the planning cycle rather than item by item, and policy constraints from S3/S5 rather than execution instructions.

**Autonomy scope test.** List the recent decisions that needed approval outside the squad. For each, ask whether the approval enforced a policy or was S3 making an execution choice. Every execution-choice item is a candidate for a written policy that replaces the approval. The fix is rules, not blanket permission.

**Example boundary.** The retention squad picks its next re-engagement experiment alone. It does not unilaterally sunset a feature the monetisation squad depends on; that needs S3 coordination and possibly S5.

### P2 — PM-of-PMs as S3: Internal Control Without Micromanagement

A head of product acting as S3 does four things: allocates capacity across squads at the planning cycle; negotiates outcome agreements ("activation up by an agreed amount this quarter", not "ship the referral programme"); writes policies that let squads act alone (for example, "no two squads run experiments on the same segment and funnel stage without registering in the experiment calendar"); and rebalances capacity mid-cycle when system-level metrics move.

S3 does not write user stories, approve individual tests, or attend sprint reviews as an approver. S3* is sporadic direct contact with ground truth (raw tickets, an unannounced interview, an hour with a squad) used for calibration, not control.

### P3 — Discovery Research as S4

S4 in product maps to continuous discovery not tied to a roadmap item, competitive and market scanning, technology horizon scanning (model capability and inference-cost changes for AI products), and regulatory and trust signals.

**Homeostat test.** A strategy review that produces a deck but does not change the next cycle's capacity allocation has failed the S3/S4 coupling. Every S4 output should carry an S3 implication: which bets to accelerate, pause or kill. Use [quarterly-product-review.md](../assets/strategy/quarterly-product-review.md) as the output format.

**Consumed-by-operations signal.** Discovery capacity repeatedly reassigned to delivery support (usability tests for the current sprint, copy review) means S4 has been absorbed into S1, whatever the job titles say.

### P4 — Product Principles as S5: Identity Over Instruction

S5 resolves the class of conflict, not the instance. "We do not trade activation for short-term monetisation" resolves the upsell-modal-in-onboarding dispute without designing the modal. "We do not use dark patterns regardless of conversion impact" is S5 policy.

**Identity test.** Take recent cross-squad conflicts and ask whether the current principles give a clear answer. If the answer is "it depends on the quarter", S5 is absent or too vague. A squad's charter is its own S5 and is not the company's S5 (recursion).

### P5 — Shared Roadmap and Experiment Calendar as S2

S2 prevents collisions on shared resources (the user population, shared surfaces such as navigation, onboarding and notifications) without deciding what squads build. Mechanisms: an experiment registry with non-overlapping allocations for concurrent tests on the same funnel stage; the roadmap as a place where squads publish intent so others can spot interference; a metric-ownership matrix so cross-squad interventions are judged against the owner's primary metric.

**Cadence test.** If squads ship daily but S2 syncs on a fixed calendar, coordination lags the change rate. Prefer event-driven S2: a squad publishes a change intent and gets an interference check before shipping. If an S2 mechanism blocks a squad pending S3 approval, it has become S3; redesign it.

### P6 — SEV Customer Issues as Algedonic Signals

Candidate product algedonic triggers:

- A defect that breaks a core workflow for a paying customer.
- Any detected data exposure, privacy violation or user-harm event (route to the accountable executive and legal, bypassing intermediate layers).
- A collapse in a primary metric (activation, payment conversion) relative to its own recent baseline.
- Positive signals too: an unexpected organic spike or a strategic customer request that implies a category opportunity, routed to S4/S5 outside the planning cycle.

| Element | Product specification |
| --- | --- |
| Trigger | Unambiguous condition: no judgment call needed to fire |
| Bypass route | Page to on-call PM and engineering lead; not the sprint queue |
| Signal content | Account and revenue at risk, affected surface, last deploy, current error rate |
| Response window | Set from the customer or regulatory consequence deadline, not a house default |
| De-escalation | Resolved and confirmed, or mitigation in place |
| Post-event | Blameless review including why normal channels did not surface it |

Set the metric-drop thresholds and response windows from your own baseline variance and contractual or regulatory deadlines; this file does not supply numbers. Channel hygiene and drill timing follow [11-algedonic-channels](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/11-algedonic-channels.md): re-test after on-call, routing or authority changes and at an interval set by the consequence of a missed signal.

### P7 — Recursive Product Orgs

| Level | S5 | S4 | S3 | S2 | S1 units |
| --- | --- | --- | --- | --- | --- |
| Company product function | CPO + product principles | Market and platform strategy | CPO allocating across groups | Cross-group roadmap coordination | Product groups |
| Product group | Group charter interpreting company principles | Group discovery lead | Head of product for the group | Within-group experiment calendar | Squads |
| Squad | Squad charter, quality bar | Squad PM's continuous discovery | Tech lead: sprint capacity, technical policy | Standup, ticket protocol | Engineers or pairs |

**Collapse diagnosis.** A CPO approving work in squad standups is company-level S3 doing squad-level S1 work. The fix is to give group-level S3 genuine resource authority and outcome agreements so escalations resolve there.

### P8 — Opportunity Solution Trees: Coverage, Not Counts

An OST is a regulator only if each distinguishable opportunity the team has chosen to address has a response path. Do not score variety as "number of segments" versus "number of experiments" and subtract or compare the counts; counts of different things are not varieties of the same disturbance set, and Ashby's bound is a lower bound on outcome variety in log units, not a count gap. Run the [response coverage audit](../../foundations-cybernetics-vsm/references/response-coverage-audit.md) instead:

| Opportunity (disturbance class) | Response available now | Evidence it works | Gap action |
| --- | --- | --- | --- |
| Distinct problem statement from the target segment | Candidate solution(s) at a stated validation stage | Assumption test, prototype or live-experiment result | Add a candidate, attenuate (park the opportunity), or escalate |

- **Attenuate** the problem space by parking opportunities that lack recurring, unsolicited evidence; record a tripwire for re-entry.
- **Amplify** the solution side where one failed experiment would leave an active opportunity with no next option.
- **Transduce** raw interview notes into opportunity statements before they enter the tree.

Add the coverage columns to [opportunity-solution-tree.md](../assets/discovery/opportunity-solution-tree.md) nodes rather than a numeric "variety" score.

### P9 — Closing the Loop on Product Bets

| Loop element | Product translation |
| --- | --- |
| Goal variable | Primary metric the bet should move, with formula and timeframe |
| Sensor | Data source, query, measurement frequency |
| Comparator | Pre-registered kill or pivot rule from [kill-criteria-template.md](../assets/prioritization/kill-criteria-template.md) |
| Effector | Named action: kill, pivot, extend, escalate to S3 |
| Delay | Measurement window long enough to pass novelty effects, short enough to act on |

**Goal erosion.** Lowering the success threshold after a bet underperforms removes the setpoint. Lock the kill criterion at launch; only S3 changes it, with a written rationale. Close each loop with a review against the original bet memo using [a3-debrief.md](../assets/ops/a3-debrief.md); if the loop cannot be closed (no instrumentation, no isolation), that is the finding.

---

## Anti-Pattern Catalog

| ID | Anti-pattern | Product symptom | Fix |
| --- | --- | --- | --- |
| A1 | S3 collapsed into S1 | Head of product approves individual tests and copy; squads shrink experiments to pass approval | Classify recent approvals as policy vs execution; convert execution approvals into written policy or delegation; re-audit |
| A2 | S4 consumed by operations | Research budget and discovery time go to current-sprint support; competitor moves learned from customers | Protect discovery capacity as an explicit planning constraint, like engineering capacity |
| A3 | S5 too vague | "We build for the user" cannot decide privacy vs revenue; similar conflicts decided differently | Test principles against recent real conflicts; rewrite until each gets a clear answer |
| A4 | Algedonic channel silenced | Engineers fix SEVs quietly because post-mortems became blame sessions | Separate escalation from performance management; announce it; drill the channel and check the review is system-focused |
| A5 | OST without attenuators | Many active opportunities, constant context switching, no signal matures | Cap active opportunities and experiments per opportunity to what capacity can see through; park the rest with tripwires |

See the [foundation anti-patterns](../../foundations-cybernetics-vsm/SKILL.md#anti-patterns) for the generic forms.

---

## Recipes

### R1 — VSM Squad Design

1. **Fix the recursion level.** Write level above, system-in-focus, level below. Confirm each level has its own S5.
2. **Map S1 units.** For each squad: primary activity, environmental boundary, shared surfaces. Any shared surface needs an S2 mechanism; fully overlapping domains need redrawn boundaries or explicit primary ownership.
3. **Classify S3 decisions.** Resource allocation and cross-squad policy stay at S3; execution choices inside a squad's domain move to the squad; S3/S4 conflicts go to S5 only if principles cannot resolve them.
4. **Design S2.** Experiment calendar, metric-ownership matrix, and a visibility window for changes to shared surfaces sized to how far ahead affected squads need to know. S2 informs; it does not approve.
5. **Write or test S5.** Use the form: "We [do / do not] [behaviour] because [identity constraint]. This resolves conflicts between [A] and [B] in favour of [A/B]." Test it against recent conflicts.

**Output:** a squad map with recursion levels, S1 boundaries, S2 mechanisms, classified S3 decisions and a tested S5 statement.

### R2 — Discovery-to-Strategy Pipeline

1. **Horizons.** Operational (current product friction), tactical (problem-space change affecting current bets), strategic (market, technology, regulation). Give each explicit capacity; no capacity on the strategic horizon means no long-range S4.
2. **Scanning mechanism per horizon** with an output that lands somewhere: OST nodes, competitor move log, environmental model update.
3. **S3/S4 translation.** Each finding is written as "We observed X. The implication for current allocation is Y. The proposed adaptation is Z." Hold the S3/S4 review at a rhythm matched to how fast the relevant environment moves, plus ad hoc when S4 sees a discontinuity.
4. **S5 escalation.** A finding that would change what the product is goes to S5 before S3 acts.
5. **Close discovery loops** with the P9 loop specification applied to each interview block or assumption test.

### R3 — Algedonic Design for Product Incidents

1. Define trigger categories (customer impact, metric collapse, trust and safety), each unambiguous.
2. Make the bypass route infrastructure: monitoring alerts and ticket classifiers route automatically; do not rely on "escalate if you think it's serious".
3. Set acknowledgement and decision windows from customer, contractual and regulatory deadlines; state when the accountable executive (S5) is pulled in. Trust and safety events always involve S5.
4. After every event, check: was the channel used as soon as the condition was detectable, was the response inside the window, was the review system-focused, and would the team fire it again?
5. Drill the channel with a labelled synthetic trigger per [11-algedonic-channels](../../foundations-cybernetics-vsm/assets/templates/cybernetics-vsm/11-algedonic-channels.md); publish results so teams trust it.

**Output:** a channel specification (triggers, route, windows, S5 criteria, review format) anchored to [a3-debrief.md](../assets/ops/a3-debrief.md).

---

## Cross-References

- [assets/discovery/opportunity-solution-tree.md](../assets/discovery/opportunity-solution-tree.md) — OST template (P8)
- [assets/strategy/quarterly-product-review.md](../assets/strategy/quarterly-product-review.md) — S4 output format
- [assets/prioritization/kill-criteria-template.md](../assets/prioritization/kill-criteria-template.md) — loop comparator
- [assets/ops/a3-debrief.md](../assets/ops/a3-debrief.md) — post-event review
- [causal-inference-applied.md](causal-inference-applied.md), [theory-of-constraints-applied.md](theory-of-constraints-applied.md), [decision-theory-applied.md](decision-theory-applied.md)
- Foundation: [foundations-cybernetics-vsm](../../foundations-cybernetics-vsm/SKILL.md)

## Sources

1. Ashby, W. R. (1956). _An Introduction to Cybernetics_, §11/7 (requisite variety as a lower bound on outcome variety). Chapman & Hall.
2. Beer, S. (1972). _Brain of the Firm_; (1979) _The Heart of Enterprise_; (1985) _Diagnosing the System for Organizations_.
3. Torres, T. (2021). _Continuous Discovery Habits_. Product Talk.
4. Sterman, J. D. (2000). _Business Dynamics_ — delays and goal erosion.

Theory sources and their verification status live in the foundation's [data/sources.json](../../foundations-cybernetics-vsm/data/sources.json).
