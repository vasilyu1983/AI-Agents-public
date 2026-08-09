# Team Theory — Patterns, Scenarios, Traps


Applied patterns and traps for using team theory in subagent / multi-agent LLM design. The 2025–2026 literature on multi-agent failure, orchestration traces, and coordination layers maps cleanly onto team-theoretic concepts; this file is the translation.

## Table of Contents

- [Scenario Patterns](#scenario-patterns)
- [Mapping MAST Failure Modes to Team Theory](#mapping-mast-failure-modes-to-team-theory)
- [Traps](#traps)
- [Choosing an Organizational Form for Subagents](#choosing-an-organizational-form-for-subagents)
- [Source Quality and Verification](#source-quality-and-verification)

---

## Scenario Patterns

### Split-and-merge (decentralized parallel)

_When_: independent subtasks, low coupling, cheap aggregation.

_Information structure_: decentralized — each subagent observes its slice. _Form_: decentralized + final orchestrator synthesis. _Communication_: zero between subagents during work.

_Why it works_: under high information cost and low coupling, Sah–Stiglitz / Radner conditions favor decentralized form. PBPO (#3) is sufficient because actions don't interact in the payoff function.

_Watch for_: false independence — if the synthesis depends on subagents having the *same* interpretation of an ambiguous brief, you have hidden coupling. Add a brief-grounding pass before fanout (see [foundations-grounding-communication](../../foundations-grounding-communication/SKILL.md)).

### Orchestrator-led (centralized)

_When_: high coupling between subtasks, low information cost, fast feedback needed.

_Information structure_: centralized — orchestrator observes everything and decides. _Form_: centralized. _Communication_: one-way down; results bubble back up.

_Why it works_: when coupling is high, joint optimization beats decentralized; centralizing the decision avoids the Witsenhausen (#6) signaling pathologies.

_Watch for_: orchestrator becoming a context bottleneck. Information cost (#7) compounds — every subagent's observation runs through the orchestrator's context window. Re-evaluate when token cost dominates wall-clock cost.

### Hierarchical (planner → architect → workers)

_When_: layered abstraction; each level decides at its own granularity.

_Information structure_: nested. _Form_: hierarchical. _Communication_: down-the-tree by default, with explicit upward escalation channels.

_Why it works_: matches problems with natural recursion (system → service → file). Each level handles a team problem at its own scale.

_Watch for_: information loss at each summarization step. Without an algedonic / escalation channel, lower-level signal dies before reaching the top — exactly the failure [foundations-cybernetics-vsm](../../foundations-cybernetics-vsm/SKILL.md) names.

### Peer agents with shared scratchpad

_When_: agents need each other's intermediate results.

_Information structure_: non-classical (#6 territory). _Form_: decentralized peers. _Communication_: shared write-read store.

_Why it works (when it does)_: signaling is exactly the regime Witsenhausen showed has nonlinear-optimal policies. With careful design, peer signaling can dominate orchestrator-led patterns.

_Watch for_: this is the highest-risk pattern. Optimal policies are nonlinear (#6); naive prompting will leave value on the table. Empirically, MAST data shows peer-agent patterns have higher coordination-failure rates than orchestrator-led for the same task class. Default to orchestrator-led unless you have evidence the signaling pays off.

### Virtual team design by task type

_When_: human team members are geographically distributed or fully remote; team needs to choose communication medium and meeting structure.

_Finding (Sinnemann & Weiss 2025, Journal of Organizational Behavior, meta-analysis of 132 samples, N=7,004 teams)_: team virtuality has **no significant main effect** on team innovation. The relationship is entirely mediated by two moderators:

| Task type | Virtuality effect | Communication medium |
|---|---|---|
| Divergent / generative (brainstorming, ideation) | Neutral or slight positive | Any medium acceptable |
| Convergent / evaluative (decision-making, synthesis, judgment) | Negative — virtuality hurts | Video-first required |

_Applied rule_: match medium to task phase, not to team type. A remote team running a convergent design review should use synchronous video; the same team generating ideas can use async text tools.

_Information-structure framing_: convergent tasks require agents to update their beliefs on shared state (high coupling, Primitive #8); the communication medium determines the effective bandwidth of the shared observation. Text-only is a bandwidth-restricted channel for high-coupling tasks.

_Kill criteria_: if a subsequent meta-analysis with N > 10,000 reverses the task-type moderation finding, demote to domain-specific note.

---

## Mapping MAST Failure Modes to Team Theory

The MAST taxonomy (Cemri et al. 2025, NeurIPS) groups multi-agent failures into three categories. Each maps to a team-theoretic primitive:

| MAST category | Share of failures | Team-theory primitive | Diagnostic |
|---|---|---|---|
| System design issues | Dataset-specific; verify locally | Common-task condition (#10) violated implicitly — agents infer different `U` | Did each agent receive an explicit shared payoff? Or did each receive a different sub-goal? |
| Inter-agent misalignment | Dataset-specific; verify locally | Information structure (#2) misdesigned; value of communication (#4) miscomputed | What does each agent observe? Where do channels exist? Is each channel paying its cost? |
| Task verification gaps | Dataset-specific; verify locally | PBPO (#3) accepted as team-optimum; no joint-deviation check | Does any process verify the joint output, not just per-agent output? |

The lesson: most multi-agent failures aren't "the agents are bad" — they're team-design failures that team theory names directly.

---

## Traps

### Trap: Treating verbose context as free

Every additional observation in a subagent's context is paid for in tokens. The orchestrator that "gives every subagent the full repo just in case" is paying observation cost for the full cross product. Information cost (#7) is non-trivial.

**Fix**: partition observations to what each subagent's *action* depends on. If an observation never changes the action, it shouldn't be in the prompt.

### Trap: PBPO masquerading as team-optimum

"I tuned each subagent's prompt and they each work better individually" is a person-by-person claim, not a team-optimum claim. Two prompts can each be locally optimal while a joint redesign improves the team.

**Fix**: when iterating, vary two prompts at once. If you find a joint change that improves payoff while neither single change does, you were at PBPO not team-optimum.

### Trap: Conflating value of information with value of communication

VoI (foundations-decision-theory) asks "should *this agent* observe more?" VoC (foundations-team-theory #4) asks "should *agent A tell agent B* what it observed?" Different question, different math, different answer.

**Fix**: separate the two computations. Most "let's add observability" decisions are mixing them.

### Trap: Defaulting to orchestrator-led

Orchestrator-led is the default in modern agent frameworks but isn't always optimal. Under high information cost and low coupling, decentralized forms with end-stage synthesis match centralized payoff at lower cost.

**Fix**: classify the coupling and the observation cost regime first; pick the form second.

### Trap: Linear policies in non-classical info structures

Witsenhausen (#6) shows nonlinear policies can strictly dominate linear policies whenever one agent's action affects another's observation. In practice this means: any time a subagent writes something another subagent reads, you're in non-classical territory.

**Fix**: don't assume "more careful prompting" will get you to optimum — the optimum may require a qualitatively different policy class. Allow nonlinear behavior (e.g., conditional branching on the upstream output).

### Trap: Calling it a team when payoffs diverge

If subagent A is rewarded for code that compiles and subagent B is rewarded for tests that pass, and the joint goal is "shipped feature," the agents may pursue locally-optimal-but-divergent paths. The common-task condition (#10) fails.

**Fix**: either align payoffs (force `U_A = U_B = U`) or move to game theory and add mechanism design.

### Trap: Treating psychological safety as monotonically beneficial (human teams)

High psychological safety robustly benefits learning, innovation, and adaptive tasks. For *routine in-role tasks*, the relationship is curvilinear (inverted-U): very high psychological safety can redirect attention toward exploration at the expense of execution, degrading routine performance. The moderation variable is task type; accountability structures are the mechanism that prevents the downside in execution-heavy contexts.

**Source**: Edmondson & Bransby (2023, Annual Review of Organizational Psychology and Organizational Behavior 10:55–78). The nonlinear/curvilinear claim's primary empirical source is Eldor, Hodor & Cappelli (2023, Organizational Behavior and Human Decision Processes 177; five independent studies) — author names confirmed 2026-07-11 via secondary listings after the primary ScienceDirect URL returned 403; full text remains paywalled, so the specific effect sizes are still hedged pending direct access.

**Fix**: segment psychological safety interventions by task type. Apply to learning/adaptive contexts by default; pair with explicit accountability structures for execution-heavy phases.

**Common misreads of "psychological safety" worth naming explicitly** (these are conceptual-clarity points from Edmondson's own corrective writing — e.g. *The Fearless Organization*, 2018 — not new empirical claims, and are widely uncontested within the literature even where effect sizes are contested):

- **Mistaking it for comfort or niceness.** Psychological safety is the belief that speaking up (disagreeing, flagging a mistake, asking a "dumb" question) will not be punished — it is not an absence of candor, conflict, or performance pressure. A "safe but low-standards" team is a distinct (and worse) quadrant from a psychologically safe, high-standards team; conflating the two is the single most common misapplication in practice.
- **Treating it as an individual trait.** Psychological safety is measured and theorized as a team-level (or leader-relationship-level) climate property, not a personality trait of individual members. "This person doesn't feel safe" is a symptom; the diagnosis and the fix are usually at the team-climate level, not the individual.
- **Assuming a single team-wide score describes everyone equally.** Psychological safety climate is not uniformly distributed within a team — subgroups (by tenure, status, demographic minority position) routinely report different levels within the same team. A team-average score can mask a low-safety subgroup whose silence is exactly the failure mode leaders most need to catch.
- **Assuming the survey instrument travels cleanly across contexts.** Most psychological-safety measurement is validated on Western, white-collar, English-language samples; applying the same instrument and thresholds to a different industry, culture, or high-stakes physical-risk context (e.g., surgical or aviation teams) without re-validation risks a false read in either direction.
- **Ignoring the curvilinear boundary above** — treating "more is always better" as if it were the field's consensus finding when the current authoritative review (Edmondson & Bransby 2023) explicitly frames it as bounded by task type.

### Trap: Assuming human-AI teaming automatically adds value over AI alone

Human-AI teams outperform humans alone in the majority of studies. However, exceeding the *AI alone* (complementary team performance, CTP) is rare in practice. CTP requires at least one of: (a) information asymmetry — the human holds local context or tacit knowledge that the AI cannot access or infer; (b) capability asymmetry — the human provides reliable judgment on novel cases outside AI training distribution. If neither condition holds, human-in-the-loop design adds latency and cost without payoff.

**Source**: Hemmer et al. (2024/2025). "Complementarity in Human-AI Collaboration: Concept, Sources, and Evidence." *European Journal of Information Systems* (arXiv:2404.00029). Two empirical studies confirm information asymmetry and capability asymmetry as CTP conditions.

**Fix**: before adding a human review step, verify which CTP condition it satisfies. If neither, remove the human from the loop.

### Trap: Over-applying mechanism design when payoffs do align

Symmetric trap: adding voting, auctions, or incentive-compatibility scaffolding to a system where agents already share `U`. Wasted complexity.

**Fix**: verify the common-task condition first. If it holds, stay in team theory; mechanism design overhead isn't earning its keep.

---

## Choosing an Organizational Form for Subagents

| Coupling | Information cost | Recommended form | Reason |
|---|---|---|---|
| Low | Low | Centralized OR decentralized — pick by ops simplicity | Both forms are near-optimal; orchestrator-led is simpler ops |
| Low | High | Decentralized + late synthesis | Don't pay observation cost twice; agents work in parallel on disjoint slices |
| High | Low | Centralized | Joint optimization needed; observation is cheap so route through one decider |
| High | High | Hierarchical with escalation | Can't decentralize (coupling); can't centralize (cost); compromise via decomposition |
| Mixed | Mixed | Match topology to coupling structure | If coupling is locally high but globally low, group tightly-coupled agents into a sub-team |

---

## Source Quality and Verification

- **Foundational layer (high confidence)**: Marschak (1955), Radner (1962), Witsenhausen (1968), Marschak & Radner (1972). These are stable; results haven't changed.
- **Computational layer (high confidence)**: Bernstein et al. (2002) Dec-POMDP complexity; Oliehoek & Amato (2016) textbook treatment.
- **Modern multi-agent LLM layer (verify before using)**: MAST (Cemri et al. 2025), May 2026 orchestration-trace work, and coordination-layer papers. Empirical percentages are dataset-specific — re-verify against your own production traces before treating as priors.
- **MARL approximation methods (rapidly evolving)**: MAPPO, QMIX, MADDPG. Check arXiv for current state-of-the-art when implementing.

When in doubt, primary sources before secondary.
