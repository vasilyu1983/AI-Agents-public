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

_Why it works_: under high information cost and low coupling, Sah–Stiglitz / Radner conditions favor decentralized form. PBPO (#3) is sufficient here only if the payoff is additively separable across agents' actions (no interaction terms); otherwise it is only necessary.

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

_Information structure_: action-dependent; check nestedness before invoking #6. _Form_: decentralized peers. _Communication_: shared write-read store.

_Why it works (when it does)_: signaling is the regime where Witsenhausen's counterexample shows linear policies can be beaten. With careful design, peer signaling may beat orchestrator-led patterns; test it.

_Watch for_: this is the highest-risk pattern. Optimal policies may be nonlinear (#6); naive prompting may leave value on the table. The MAST paper itself makes no topology comparison (Cemri et al. 2025, arXiv:2503.13657); the closest supported claim is Kim et al. (arXiv:2512.08296): "architectures without centralized verification tend to propagate errors more than those with centralized coordination." Default to orchestrator-led when verification is centralized and evidence for peer-to-peer signaling is absent, not on an unsupported MAST comparison.

### Virtual team design by task type

Human-team material (Sinnemann & Weiss virtual-team meta-analysis) is out of scope for this skill. The evidence lives in `team-effectiveness-evidence.md`.

---

## Mapping MAST Failure Modes to Team Theory

The MAST taxonomy (Cemri et al. 2025, NeurIPS) groups multi-agent failures into three categories. Each maps to a team-theoretic primitive:

| MAST category | Share of failures | Team-theory primitive | Diagnostic |
|---|---|---|---|
| System design issues | Dataset-specific; verify locally | Common-task condition (#10) violated implicitly — agents infer different `U` | Did each agent receive an explicit shared payoff? Or did each receive a different sub-goal? |
| Inter-agent misalignment | Dataset-specific; verify locally | Information structure (#2) misdesigned; value of communication (#4) miscomputed | What does each agent observe? Where do channels exist? Is each channel paying its cost? |
| Task verification gaps | Dataset-specific; verify locally | PBPO (#3) accepted as team-optimum; no joint-deviation check | Does any process verify the joint output, not just per-agent output? |

The lesson: many multi-agent failures are team-design failures that team theory names directly, not only weak individual agents — check the design before swapping models.

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

Orchestrator-led is the default in modern agent frameworks but isn't always optimal. Under high information cost and low coupling, decentralized forms with end-stage synthesis can match centralized payoff at lower cost; confirm with a matched-budget local comparison.

**Fix**: classify the coupling and the observation cost regime first; pick the form second.

### Trap: Linear policies in non-classical info structures

Witsenhausen (#6) provides a specific non-classical counterexample to linear-policy optimality. Action-dependent observations alone do not establish non-classical structure: check whether the later decision-maker knows the relevant earlier information (partial nestedness). A planner writing for an executor is not automatically a counterexample setting.

**Fix**: don't assume "more careful prompting" will get you to optimum — the optimum may require a qualitatively different policy class. Allow nonlinear behavior (e.g., conditional branching on the upstream output).

### Trap: Calling it a team when payoffs diverge

If subagent A is rewarded for code that compiles and subagent B is rewarded for tests that pass, and the joint goal is "shipped feature," the agents may pursue locally-optimal-but-divergent paths. The common-task condition (#10) fails.

**Fix**: either align payoffs (force `U_A = U_B = U`) or move to game theory and add mechanism design.

### Trap: Treating psychological safety as monotonically beneficial (human teams)

Human-team material (psychological-safety curvilinear boundary and misreads) is out of scope for this skill. The evidence lives in `team-effectiveness-evidence.md`. Practice guidance lives in `software-code-review/references/psychological-safety-guide.md`.

### Trap: Assuming human-AI teaming automatically adds value over AI alone

Human-AI teams outperform humans alone in the majority of studies. However, exceeding the *AI alone* (complementary team performance, CTP) is rare in practice. CTP requires at least one of: (a) information asymmetry — the human holds local context or tacit knowledge that the AI cannot access or infer; (b) capability asymmetry — the human provides reliable judgment on novel cases outside AI training distribution. If neither condition holds, human-in-the-loop design adds latency and cost without payoff.

**Source**: Hemmer et al. (2024/2025). "Complementarity in Human-AI Collaboration: Concept, Sources, and Evidence." *European Journal of Information Systems* (arXiv:2404.00029). Two empirical studies confirm information asymmetry and capability asymmetry as CTP conditions.

**Fix**: assess whether human review adds information or capability, and separately assess required authority, accountability and escalation duties. Lack of an accuracy benefit alone does not justify removing a required human role.

### Trap: Assuming a team will use the expertise it contains

Adding a strong specialist does not establish that aggregation uses their evidence. Pappu et al. report expertise dilution in controlled tasks. Their Table 2 ML synergy gaps instead compare teams to an At Least One Correct oracle bound; the maximum 41.1% is HLE Text-Only, Expert Not Mentioned, not loss against the best fixed individual or a revealed-expert condition. Use the appropriate comparator before diagnosing aggregation failure.

**Source**: Pappu, El, Cao, di Nolfo, Sun, Cao & Zou (2026). "Multi-Agent Teams Hold Experts Back." arXiv:2602.01011, ICML 2026.

**Fix**: make deference structural rather than emergent — route the decision to the competent agent, or weight contributions by a verifiable competence signal (past accuracy on the task class, a test the agent can pass), not by conversational assertiveness. Always benchmark the team against its single-best-member baseline; a team that loses to one good agent is paying coordination cost for negative return.

**Countervailing consideration**: the same consensus-seeking that suppresses expertise is what makes these teams resistant to adversarial or compromised members. Where an untrusted agent could poison the output, pooling is the correct rule and the expertise loss is the price of robustness. Decide which regime you are in before removing the consensus step.

### Trap: Treating "collective intelligence" as a tunable team property (human teams)

Human-team material (contested c-factor) is out of scope for this skill. The evidence lives in `team-effectiveness-evidence.md`. For agent teams, design the observation partition (#2) and the aggregation rule (#11) first.

### Trap: Over-applying mechanism design when payoffs do align

Symmetric trap: adding auctions, payments, or incentive-compatibility scaffolding to a system where agents already share `U` — wasted complexity. Aggregation itself (voting, weighting, routing; #11) is legitimate team-theory design; only the anti-misreporting machinery is unnecessary.

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
- **Modern multi-agent LLM layer (verify before using)**: MAST (Cemri et al. 2025), orchestration-trace work (arXiv:2605.02801, arXiv:2605.03310; see `data/sources.json`), and coordination-layer papers. Empirical percentages are dataset-specific — re-verify against your own production traces before treating as priors.
- **MARL approximation methods (rapidly evolving)**: MAPPO, QMIX, MADDPG. Check arXiv for current state-of-the-art when implementing.
- **Human-team empirical layer (contested)**: see `team-effectiveness-evidence.md`. Cite those findings as contested hypotheses with the countervailing evidence attached, never as settled effects.

When in doubt, primary sources before secondary. When a finding is contested, say so in the same sentence that states it — a hedge in a footnote does not survive being quoted.
