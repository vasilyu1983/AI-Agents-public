---
name: foundations-cybernetics-vsm
description: Applies Beer's VSM and Ashby's Law to diagnose org or agent-system viability. Use when a team or agent hierarchy has coordination, escalation, or requisite-variety problems.
compatibility: Portable core only.
version: "1.1"
last_validated: 2026-07-11
---

# Cybernetics and Viable System Model Foundations


## When to Apply

**Apply cybernetics-VSM when:**
- Org or agent-system steering question — viability, requisite variety, escalation paths
- "Why does this team/system keep failing despite individual competence?" — likely missing S2/S3*/S4
- Recursion across levels — same control pattern at squad / department / company
- Algedonic channel design — when does a critical signal bypass hierarchy and reach S5 directly?
- Variety-engineering — orchestrator levers vs environment variety (Ashby's Law)

**Skip and use simpler alternatives when:**
- Single team, no recursion, no orchestration question — VSM is overkill
- Org-design question is purely about reporting lines — use a simple RACI, not VSM
- Throughput/bottleneck question — use foundations-theory-of-constraints
- Strategic-interaction question between agents — use foundations-game-theory
- Feedback-loop tuning on a measurable variable — use foundations-control-theory
- The framing imports VSM jargon (S1-S5) without an actual variety/viability problem — risk of decoration; demand the failure signal first

---

11 canonical cybernetics and VSM primitives for designing viable organizations, control hierarchies, and adaptive systems. Each primitive solves a specific failure mode in how complexity is absorbed, coordinated, and governed. Primitives are domain-agnostic: the same variety-engineering pattern that prevents management overload in an enterprise also prevents orchestrator bottlenecks in an agent swarm; the same algedonic channel that surfaces crises to a board surfaces production incidents to an on-call team.

## Contents

- [Quick Reference](#quick-reference)
- [Primitive Index](#primitive-index)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Misuse Boundaries](#misuse-boundaries)
- [Anti-Patterns](#anti-patterns)
- [Decision Checklist](#decision-checklist)
- [Composition Recipes](#composition-recipes)
- [Workflow](#workflow)
- [ASCII Flow](#ascii-flow)
- [Navigation](#navigation)
- [Fact-Checking](#fact-checking)

---

## Quick Reference

| # | Primitive | Core Function | When to Reach For It |
|---|-----------|---------------|----------------------|
| 1 | [Feedback Loops](assets/templates/cybernetics-vsm/01-feedback-loops.md) | Regulate behavior via negative (balancing) or amplify via positive (reinforcing) loops | Any adaptive control mechanism; stability vs. growth dynamics |
| 2 | [Ashby's Law of Requisite Variety](assets/templates/cybernetics-vsm/02-ashbys-law.md) | Controller must match the variety of the system it governs | Diagnosing under-instrumented control; scaling management layers |
| 3 | [VSM System 1 — Operations](assets/templates/cybernetics-vsm/03-vsm-system-1.md) | Autonomous operational units that do the actual work | Defining work units, microservices, squads, agent executors |
| 4 | [VSM System 2 — Coordination](assets/templates/cybernetics-vsm/04-vsm-system-2.md) | Anti-oscillation coordination layer between S1 units | Preventing interference and thrashing between operational units |
| 5 | [VSM System 3 — Internal Control](assets/templates/cybernetics-vsm/05-vsm-system-3.md) | Here-and-now optimization of the operational environment | Performance management, resource allocation, policy enforcement |
| 6 | [VSM System 3* — Audit Channel](assets/templates/cybernetics-vsm/06-vsm-system-3-star.md) | Sporadic direct channel from S3 to S1 bypassing S2 | Spot-checks, audits, compliance sampling; detecting S2 distortion |
| 7 | [VSM System 4 — Intelligence](assets/templates/cybernetics-vsm/07-vsm-system-4.md) | Outside-and-future scanning; adaptation intelligence | Strategy, environmental scanning, roadmaps, horizon sensing |
| 8 | [VSM System 5 — Identity/Policy](assets/templates/cybernetics-vsm/08-vsm-system-5.md) | Ultimate authority; closure and identity of the whole | Mission, values, constitutional rules, governance closure |
| 9 | [Recursion Levels](assets/templates/cybernetics-vsm/09-recursion-levels.md) | Every viable system contains and is contained in viable systems | Multi-level organizational design; nesting teams, divisions, products |
| 10 | [Variety Engineering](assets/templates/cybernetics-vsm/10-variety-engineering.md) | Amplifiers, attenuators, and transducers to balance variety across channels | Reducing information overload; designing dashboards, APIs, interfaces |
| 11 | [Algedonic Channels](assets/templates/cybernetics-vsm/11-algedonic-channels.md) | High-priority pain/pleasure signals that bypass normal hierarchy levels | Incident escalation, crisis bypass routes, critical alerts |

---

## Primitive Index

Each primitive has a full playbook (definition, when to use, inputs, outputs, failure modes, worked example, sources).

| # | Primitive | Failure Mode It Addresses |
|---|-----------|--------------------------|
| 1 | [Feedback Loops](assets/templates/cybernetics-vsm/01-feedback-loops.md) | Runaway growth or oscillation from unchecked reinforcing dynamics |
| 2 | [Ashby's Law — Requisite Variety](assets/templates/cybernetics-vsm/02-ashbys-law.md) | Control collapse when environmental variety exceeds controller capacity |
| 3 | [VSM S1 — Operations](assets/templates/cybernetics-vsm/03-vsm-system-1.md) | Centralised execution bottleneck; no operational autonomy |
| 4 | [VSM S2 — Coordination](assets/templates/cybernetics-vsm/04-vsm-system-2.md) | Thrashing and interference between operational units |
| 5 | [VSM S3 — Internal Control](assets/templates/cybernetics-vsm/05-vsm-system-3.md) | Local optima divergence; S1 units optimise against each other |
| 6 | [VSM S3* — Audit Channel](assets/templates/cybernetics-vsm/06-vsm-system-3-star.md) | S2/S3 filters distort ground truth before it reaches management |
| 7 | [VSM S4 — Intelligence](assets/templates/cybernetics-vsm/07-vsm-system-4.md) | Strategy-execution gap; S3 unaware of environment shifts |
| 8 | [VSM S5 — Identity/Policy](assets/templates/cybernetics-vsm/08-vsm-system-5.md) | Identity crisis or policy vacuum; S3/S4 conflict never resolved |
| 9 | [Recursion Levels](assets/templates/cybernetics-vsm/09-recursion-levels.md) | Applying VSM at wrong scale; mismatch of model and organisation |
| 10 | [Variety Engineering](assets/templates/cybernetics-vsm/10-variety-engineering.md) | Management overload or information starvation from unbalanced variety |
| 11 | [Algedonic Channels](assets/templates/cybernetics-vsm/11-algedonic-channels.md) | Crisis hidden by normal reporting hierarchy until it is too late |

---

## Formal Supporting Theory

Load [`references/formal-theory-map.md`](references/formal-theory-map.md) when the task needs more than a primitive lookup: defining the system-in-focus, distinguishing first-order vs. second-order cybernetics, proving an Ashby/requisite-variety claim, mapping VSM systems 1-5 across recursion levels, or separating S3 control, S3* audit, S4 intelligence, S5 policy, and algedonic escalation.

## Misuse Boundaries

Load [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md) before turning VSM into an org chart, central control layer, dashboard scheme, escalation policy, or agent hierarchy. It contains operational scenarios, anti-patterns, known traps, and a compact audit sequence.

---

## Anti-Patterns

| Anti-Pattern | Cybernetics/VSM Diagnosis | Fix |
|-------------|--------------------------|-----|
| System 3 collapses System 1 autonomy (micromanagement) | S3 is consuming all operational variety — no recursion depth; Ashby violation | Restore S1 autonomy; S3 sets policy and limits, not execution steps |
| System 4 disconnected from System 3 (strategy-execution gap) | S4 output never reaches S3; no S3/S4 homeostat | Build explicit S3/S4 interface: shared planning cadence, mutual translation layer |
| Ashby's Law violated by under-instrumented control | Controller has fewer variety states than the system it governs | Add attenuators (aggregation, exception-only reporting) or amplifiers (finer-grained sensing) to balance channels |
| Algedonic channel never used — S5 blind to crises | Pain signals absorbed by normal hierarchy; S5 receives filtered reports only | Implement direct bypass route with trigger threshold; test it quarterly |
| Recursion confusion — applying VSM at wrong organisational scale | S1/S3/S5 roles assigned to the wrong recursion level | Re-identify the level of recursion; redraw the system boundary before assigning roles |
| Positive feedback loop with no balancing loop (runaway dynamics) | Reinforcing loop unchecked — growth, debt, or failure cascades | Design an explicit negative feedback loop with a goal variable and measured deviation |
| S2 coordination layer absent — unit thrashing | S1 units interfere without coordination signals | Introduce S2 scheduling, resource-sharing protocols, or synchronisation mechanisms |
| S3* audit channel treated as normal management reporting | Spot-check becomes routine; S1 adapts and Goodharts the signal | Keep S3* sporadic and surprise-based; vary timing and scope |
| Variety amplified without attenuation at higher levels | Upper levels receive raw operational noise; decision paralysis | Apply variety attenuation (aggregation, exception filters) before variety reaches S3/S4 |
| S5 identity undefined — policy vacuum | S3/S4 conflicts escalate without resolution; ad-hoc decisions contradict each other | Define S5 closure: mission, constraints, values; run S3/S4 conflicts through S5 reference frame |

---

## Decision Checklist

- [ ] **Control loop needed**: Is there a variable that must stay within bounds? → feedback loop (#1)
- [ ] **Management layer overwhelmed**: Does control complexity exceed controller capacity? → Ashby's Law audit (#2) + variety engineering (#10)
- [ ] **Operational units defined**: Are execution units autonomous with clear scope? → VSM S1 (#3)
- [ ] **Unit interference observed**: Do operational units conflict or thrash? → VSM S2 coordination (#4)
- [ ] **Optimisation divergence**: Are local optima conflicting with system-level goals? → VSM S3 (#5)
- [ ] **Ground truth distortion**: Is management receiving filtered or misleading data? → VSM S3* audit (#6)
- [ ] **Strategy-execution gap**: Is there no mechanism for environmental change to inform operations? → VSM S4 (#7)
- [ ] **Identity or policy conflict**: Do teams lack a shared frame for resolving disagreements? → VSM S5 (#8)
- [ ] **Model scale mismatch**: Is the VSM being applied to the wrong organisational level? → recursion levels (#9)
- [ ] **Information overload or starvation**: Are channels between levels carrying the wrong amount of variety? → variety engineering (#10)
- [ ] **Crisis hidden in normal reporting**: Do critical alerts get delayed by hierarchy? → algedonic channel (#11)

---

## Composition Recipes

### Agent-Team Topology Audit

**Goal**: diagnose whether an agent hierarchy is viable and where failures will occur.

**Stack**:
1. VSM S1 (#3) — identify operational agent units and verify autonomy
2. VSM S2 (#4) — check for coordination signals between units; absence = thrashing risk
3. VSM S3 (#5) — confirm orchestrator has S3 function: policy-setting, not micro-execution
4. Ashby's Law (#2) — count variety states of orchestrator vs. environment; flag under-instrumented control
5. Variety Engineering (#10) — add attenuators (summarisation, exception routing) if orchestrator is overwhelmed
6. Algedonic channel (#11) — ensure critical failures bypass normal reporting to human-in-the-loop or S5

**Output**: viability gap report with specific role assignments and missing interfaces.

**Inputs:** S1 agent units with scope and autonomy level (e.g., retrieval agent — bounded to knowledge base, no write access); orchestrator control levers (count of independent parameters the operator can adjust, e.g., routing threshold, retry limit, concurrency cap); environment variety estimate (distinct decision states per week = #task types × #tool surfaces × #concurrent pipelines).

**Rules:** Ashby check — if orchestrator lever count < environment variety states, flag a requisite-variety deficit and require attenuators (summarisation, exception routing) or additional levers before deployment; S2 absent if any two S1 units share a resource (queue, tool, memory store) without an explicit coordination protocol — flag as thrashing risk; S3* audit must run ≥1/quarter (surprise sample, not scheduled review); S4 intelligence reports (environment change signals, capability drift) must reach S5 (human-in-the-loop or governance authority) ≥1/cycle; **Conant-Ashby model-adequacy check**: verify that the orchestrator model can represent the full task-domain distinction space — if the model cannot internally represent the distinctions required by the task (e.g., context window too narrow for domain state space, tool count insufficient to cover action space), it cannot be a good regulator regardless of architectural changes (Conant & Ashby 1970); add a domain-model attenuator (task classifier, routing layer) or upgrade the model before applying variety-engineering fixes.

**Outputs:** Viability gap table (Systems 1–5 each: present Y/N, severity H/M/L if absent); Ashby variety delta (environment variety states − orchestrator lever count, positive = deficit); list of missing interfaces (e.g., "no S2 coordination protocol between retrieval and generation agents", "no algedonic bypass to human operator"); recommended structural change per gap (e.g., "add exception-only routing attenuator at S3", "define shared-resource scheduling protocol at S2").

---

### Organisational Design for a Startup

**Goal**: design a lightweight management structure that scales without creating command bottlenecks.

**Stack**:
1. Recursion levels (#9) — identify the two or three levels the startup actually needs (whole company → product area → squad)
2. VSM S1 (#3) — define autonomous squad boundaries with clear operational scope
3. VSM S3* (#6) — establish audit/spot-check mechanism so founders maintain ground truth as company grows
4. VSM S4 (#7) — assign who owns environmental scanning and translates it into strategy
5. VSM S5 (#8) — write a one-page identity document: mission, non-negotiable constraints, value principles
6. Feedback loops (#1) — design at least one balancing loop per key performance variable (burn rate, NPS, lead time)

**Inputs:** Squad list with headcount and operational scope; leadership roles mapped to S3/S4/S5 candidates; strategy and board cadence (meeting frequency, decision latency); environment variety estimate (distinct decision states per week = #customer segments × #product surfaces × #release cadences).

**Rules:** Each of S1–S5 must be present and named — absence at S3* or S4 is critical severity, absence at S2 is high severity when ≥2 squads share any resource; Ashby check — if S3 leadership lever count (e.g., headcount allocation, OKR targets, budget envelopes) < operational variety states, flag deficit and require additional attenuators or lever expansion; S3* audit must run ≥1/quarter as a surprise spot-check; S4 environmental intelligence reports must reach S5 (CEO/board) ≥1 per strategy cycle.

**Outputs:** Role-to-VSM-system mapping table (role name → S1/S2/S3/S3*/S4/S5, present Y/N); variety delta (operational variety states − S3 lever count); missing-system flag list (e.g., "S4 unassigned — no owner for competitive scanning", "S3* cadence undefined"); recommended structural change per gap.

**Worked example:** SaaS company, 4 product squads (S1, variety ≈ 12 product surfaces × 4 release cadences = 48 states) → eng leadership weekly sync (S2, coordination via shared roadmap; attenuates cross-squad scheduling conflicts) → VPE (S3, controls resource allocation + sets OKR policy; S3* audit = monthly on-call review, surprise sample of 3 incidents per squad) → strategy team (S4, scans competitor moves + market shifts, reports quarterly) → CEO/board (S5, identity: "developer-first, no dark patterns"). Variety check: S3 must absorb 48 operational states; if VPE has only 2 levers (headcount, OKR targets), that is a requisite-variety violation — add a third attenuator (e.g., tiered escalation tiers) or push more variety down to S2. Failure signal 1 (S3* gap): if the on-call audit cadence drops below 1/quarter, ground-truth drift accumulates — squads learn to report cleanly upward without S3 knowing actual failure rates. Failure signal 2 (S4-S5 disconnect): if S4 competitor reports never reach a board slot, the org loses adaptive capacity within ~2–3 strategy cycles; S3 optimises the current business model while the market shifts.

---

### Incident Escalation as Algedonic Channel

**Goal**: ensure production crises reach decision authority fast, bypassing normal ticket queues.

**Stack**:
1. Algedonic channel (#11) — define trigger threshold (e.g., p99 latency > 2× baseline for 5 min)
2. VSM S5 (#8) — confirm who holds S5 authority for incident closure decisions
3. Feedback loops (#1) — implement a balancing loop that activates on trigger: alert → diagnosis → rollback → verify recovery
4. VSM S3* (#6) — use the incident post-mortem as the S3* audit: compare what S3 saw vs. ground truth
5. Variety Engineering (#10) — ensure incident dashboards attenuate noise; only deviation-from-normal reaches on-call

**Inputs:** Feedback loops present (count and type — balancing or reinforcing); latency of each loop (time from signal to corrective action, in minutes or hours); S2 coordination protocols in place (count and description, e.g., "on-call handoff protocol", "shared incident channel"); environment change rate (how quickly the production environment can shift state, e.g., deploy frequency × distinct failure modes per week).

**Rules:** Feedback loop latency must be shorter than the environment change rate — if a loop takes 30 min to close and deploys happen every 10 min, flag a latency violation; S2 coordination protocols required when ≥2 S1 units (e.g., on-call teams, services) share a resource (queue, database, API gateway) — absence is a critical gap; S3* post-mortem audit must compare what S3 saw (dashboards, alerts) against ground truth (actual failure timeline) — run after every P1 incident; algedonic trigger threshold must be defined and tested ≥1/quarter.

**Outputs:** Loop diagram (each loop with type, goal variable, latency, and status — active/missing); latency table (loop name, measured latency, environment change rate, pass/fail); missing-protocol list (each shared resource without an S2 coordination protocol flagged as H severity); recommended structural change per gap (e.g., "reduce alert-to-page latency from 15 min to <5 min", "add shared-queue ownership protocol between service A and B").

---

### Scaling a Platform Team

**Goal**: prevent a platform team from becoming a bottleneck as it serves multiple product teams.

**Stack**:
1. Ashby's Law (#2) — measure: how many variety states does the platform team's control surface have vs. the demand variety of consuming teams?
2. Variety Engineering (#10) — apply amplifiers (self-service APIs, documentation, inner-source) to expand platform's effective variety; apply attenuators (standard interfaces, request templates) on the demand side
3. VSM S2 (#4) — add coordination protocol between consuming teams to prevent conflicting platform requests
4. VSM S3 (#5) — platform S3 sets platform-wide policy; individual platform sub-teams are S1 units with autonomy within policy
5. Feedback loops (#1) — measure platform lead time and consumer satisfaction as balancing-loop goal variables

**Output**: platform operating model with variety audit, self-service expansion plan, and S3 policy layer.

**Inputs:** Platform team control levers (count of independent parameters the platform can adjust, e.g., rate limits, API versioning, SLA tiers, capacity allocation); environment variety estimate (distinct decision states per week = #consuming teams × #integration surfaces × #request types); S2 coordination protocols between consuming teams (count); current platform lead time and consumer satisfaction score as baseline.

**Rules:** Ashby check — if platform lever count < consuming-team variety states, flag a requisite-variety deficit; resolve by amplifying platform levers (self-service APIs, inner-source pathways) or attenuating demand variety (standard request templates, tiered SLAs); S2 coordination protocol required when ≥2 consuming teams issue conflicting platform requests — absence flagged as H severity; S3 policy layer must be explicit (written platform policy: what platform decides vs. what consumers decide); feedback loop latency (platform lead time) must be measured and improving — stagnant lead time signals S3 policy or S2 coordination failure.

**Outputs:** Variety audit table (platform lever count vs. consuming-team variety states, delta, pass/fail); self-service expansion plan (list of attenuators and amplifiers to close variety gap); S3 policy layer description (scope of platform decisions vs. consumer decisions); missing coordination protocols flagged per shared resource; recommended structural change per gap.

---

## Workflow

1. Identify the system boundary and the level of recursion you are working at (use recursion levels #9 first).
2. Map the five VSM systems to actual roles, teams, or agent components.
3. Check for missing or collapsed systems — use the [Decision Checklist](#decision-checklist).
4. Apply Ashby's Law (#2) to validate that control capacity matches environmental variety.
5. Design or audit variety engineering (#10) mechanisms on each inter-level channel.
6. Confirm algedonic channels (#11) exist and are tested.
7. For specific failure modes, open the per-primitive playbook in [`assets/templates/cybernetics-vsm/`](assets/templates/cybernetics-vsm/).
8. For multi-failure scenarios, use the [Composition Recipes](#composition-recipes) above.

---

## ASCII Flow

```text
Viability or organizational-control problem
  -> Set system boundary and recursion level
  -> Map Systems 1-5 to real roles, teams, or agents
  -> Check Ashby variety gap
     +-- regulator variety too low -> attenuate demand or amplify control capacity
     +-- variety matched -> audit channels
  -> Verify algedonic alerts and policy/intelligence balance
  -> Return missing systems, channel fixes, and recursion risks
```

---

## Navigation

- Per-primitive playbooks: [`assets/templates/cybernetics-vsm/`](assets/templates/cybernetics-vsm/) (one file per primitive)
- Composition guide: [`assets/templates/cybernetics-vsm/README.md`](assets/templates/cybernetics-vsm/README.md)
- Primitives overview: [`references/primitives-overview.md`](references/primitives-overview.md)
- Formal theory map: [`references/formal-theory-map.md`](references/formal-theory-map.md)
- Patterns, scenarios, and traps: [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md)
- Sources: [`data/sources.json`](data/sources.json)

## Related Skills

<!-- Consumer skills will add cross-links here when their applied recipe layers are built. -->
<!-- Do not add cross-links to this file directly — consumer skills link in, not out. -->

---

## Fact-Checking

- **Stafford Beer**: VSM systems 1–5, algedonic channels, recursion levels, and variety engineering are defined in Beer 1972 (_Brain of the Firm_), Beer 1979 (_Heart of Enterprise_), and Beer 1985 (_Diagnosing the System for Organizations_). Verify claims about specific Beer definitions against these primary texts. **2026-07 correction**: per-primitive playbook citations previously attributed each VSM system to its own numbered chapter of _Brain of the Firm_ (e.g., "Ch. 3: System One," "Ch. 8: System Five"). The verified table of contents shows no such one-system-per-chapter structure — Systems One–Three are treated together in one section ("Autonomics"), System Four in "Environments of Decision," and System Five in "The Multinode"; recursion and algedonic channels are not confined to single dedicated chapters at all. Citations in `assets/templates/cybernetics-vsm/` were corrected to cite by section title rather than a fabricated chapter number. Chapter-level citations to Beer 1985, Hoverstadt 2009, and Schwaninger 2006 have not been independently re-verified against primary copies in this pass — treat their specific chapter numbers as approximate until confirmed.
- **Project Cybersyn** (Chile, 1971–1973): the most-cited real-world VSM deployment is also the most mythologized. Per Medina 2011 (_Cybernetic Revolutionaries_, MIT Press — the primary archival history), Cybersyn was a telex network plus one mainframe with roughly daily-lagged data, not a real-time networked control system; the Opsroom was never fully deployed (its move to the presidential palace was approved only three days before the 11 September 1973 coup); only ~26.7% of nationalized firms were incorporated by May 1973; and the October 1972 truckers'-strike response was a genuine, documented operational success for the S1/S2 layer. See `references/patterns-scenarios-traps.md` → "Historical Grounding: Project Cybersyn" for the full fact-vs-myth table before citing this case as precedent.
- **W. Ross Ashby**: Law of Requisite Variety is from Ashby 1956 (_An Introduction to Cybernetics_, ch. 11). The formal statement is W(error) ≤ V(disturbance) − V(regulator). Verify quantitative claims against the original. Note: Siegenfeld & Bar-Yam (2025, _Entropy_, 27(8), 835, DOI: 10.3390/e27080835; PMC-indexed as PMC12385218) propose a multi-scale generalisation of Ashby's Law showing that variety requirements are scale-dependent — a relevant refinement for hierarchical/recursive agent architectures where the same system exhibits different variety at different recursion levels. Treat as a clarification of application scope, not a revision of the original law.
- **Norbert Wiener**: Feedback and cybernetics foundations from Wiener 1948 (_Cybernetics: Or Control and Communication in the Animal and the Machine_). Positive/negative feedback terminology is consistent with Wiener's original usage.
- **Espinosa & Walker**: VSM applied to complexity and sustainability in _A Complexity Approach to Sustainability_ (2011). Recursion and viable-systems analysis in real organisations.
- **Schwaninger**: Intelligent organisations and VSM application in _Intelligent Organizations_ (2006). Apply numeric claims (e.g., performance improvement percentages) only when derived from primary case studies, not secondary summaries.
- **Hoverstadt**: Practical VSM application in _The Fractal Organization_ (2009). Patterns cited from this source are practitioner heuristics — verify against Beer's original formalism before treating as universal.
- Mechanism effectiveness is context-specific. Test variety-engineering interventions on a constrained scope before rolling out system-wide.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
