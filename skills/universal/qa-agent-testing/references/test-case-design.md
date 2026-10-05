# Test Case Design

Patterns for designing the starter 10-task harness and expanding it into a stronger regression suite.

## Contents

- [Task Category Framework](#task-category-framework)
- [Designing Each Task](#designing-each-task)
- [Task Record](#task-record)
- [Task Design Checklist](#task-design-checklist)
- [Task Set Validation](#task-set-validation)
- [Metamorphic Add-On](#metamorphic-add-on)
- [Example: Complete Task Set](#example-complete-task-set)

## Task Category Framework

### The 10 Starter Categories

| # | Category | Tests | Example |
|---|----------|-------|---------|
| 1 | Core deliverable | Primary output | "Write a blog post" |
| 2 | Consistency | Same format, different input | "Write another blog post" |
| 3 | Boundaries | Edge data/constraints | "Write with only 50 words" |
| 4 | Conciseness | Tight limits | "Summarize in 3 bullets" |
| 5 | Reasoning | Multi-step analysis | "Analyze and recommend" |
| 6 | External data | Tool/lookup use | "Research and report" |
| 7 | Adaptation | Tone/style shifts | "Rewrite for executives" |
| 8 | Structured output | JSON/YAML/tables | "Output as JSON" |
| 9 | Synthesis | Extract/summarize | "Pull key insights" |
| 10 | Trade-offs | Conflicting requirements | "Balance X and Y" |

---

## Designing Each Task

The 10 categories above are the design guidance — each is a well-understood test category (functional correctness, consistency, boundary handling, conciseness, reasoning, tool use, tone adaptation, structured output, synthesis, trade-off judgment) that the base model can generate a concrete example for once you name the agent's domain. Two design rules matter more than per-category templates:

- Each task must have an objective, checkable success criterion — not "the output should be good," but a specific structural or factual condition a reviewer (human or automated) can verify.
- Each task must be distinct from the other 9 — if two tasks would pass or fail together, one of them isn't testing anything the other doesn't already cover.

For trade-off tasks (category 10) specifically: score the response on whether it acknowledges the tension, explains its reasoning, commits to a recommendation, and states the limitation — not on which side of the trade-off it picks.

Category-specific notes that are easy to miss:

- **Boundaries (3):** cover empty input, very long input, special characters (Unicode, emoji, code snippets), and minimum/maximum constraint values.
- **Conciseness (4):** limits must be countable. Score 3 = limit met with high quality, 2 = within 10% of the limit, 1 = significantly over or under, 0 = limit ignored.
- **External data (6):** skip or replace this task if the agent has no tool access; do not score a tool task against a tool-less agent.
- **Structured output (8):** name the schema. Score 3 = valid format, correct schema, accurate content; 2 = valid format, minor schema issues; 1 = format attempted but malformed; 0 = wrong format or plain text.

---


## Task Record

Every suite task, whatever its category, is stored as one record. A field left empty is a task that is not ready to gate on.

```yaml
id: reg-041
source: "prod trace 2026-09-12, ticket #482"     # where the case came from; "invented" is allowed but flagged
input: "..."                                     # frozen user turn(s)
fixtures: [customer_db.snapshot, calendar.mock]  # every tool response pinned or mocked
allowed_tools: [lookup_order, send_email]
forbidden_side_effects: [refund, delete, external_http]
oracles:                                         # each one runnable without a model
  - type: schema        ; spec: order_summary.json
  - type: trace_contains; tool: lookup_order ; args: {order_id: "A-1"}
  - type: trace_absent  ; tool: send_email
  - type: claim_join    ; every action claim in the answer maps to a tool call
judged_dimensions: [user_communication]          # the only dimensions a calibrated judge may score
blocking: true                                   # blocking cases fail on any trial; quality cases report pass rate
k: 1                                             # trials per run; raise for known-nondeterministic paths
```

Sourcing rules: a regression pack is built from real failures first (production traces, tickets, red-team findings), then padded with category coverage. An invented case is a hypothesis; a case from a trace is evidence. Keep the source field so a later reviewer can tell them apart.

---

## Task Design Checklist

For each task, verify:

```text
[ ] Clear, unambiguous request
[ ] Specific enough to evaluate objectively
[ ] Tests a distinct capability
[ ] Has measurable success criteria
[ ] Represents real user needs
[ ] Reasonable complexity for the agent
[ ] Different from other 9 tasks
```

---

## Task Set Validation

Before finalizing your starter 10 tasks:

| Check | Pass? |
|-------|-------|
| All 10 categories covered | |
| No two tasks test same thing | |
| Tasks match agent's stated scope | |
| Real user scenarios represented | |
| Success criteria are objective | |
| Scoring is unambiguous | |

---

## Metamorphic Add-On

For a few important tasks, define a source case, a controlled input transformation, and the expected relation between observable outputs. This follows the original metamorphic-testing pattern: derive follow-up cases from successful source cases when a complete output oracle is hard to provide. The relation itself still needs justification; a plausible rephrase is not automatically meaning-preserving.

Variant ideas:

- Rephrase the task with different wording but same intent
- Reorder constraints without changing them
- Add irrelevant but harmless context ("noise")
- Change formatting requirements (prose vs bullets) while keeping required fields

Exact checks that may hold on every trial:

- Output schema remains valid (JSON/YAML/table structure)
- Hard constraints are still satisfied (word/char limits, required sections)
- Required citations still resolve to the frozen evidence set
- Forbidden tool calls and side effects remain absent
- Safety or refusal category remains consistent when the policy-relevant facts are unchanged

Do not require exact text equality from a nondeterministic language model. Rephrasing may legitimately change wording, ordering, or a recommendation near a decision boundary. Use one of these contracts instead:

| Boundary | Oracle | Evidence |
|---|---|---|
| Structural | Schema, required fields, length, tool allowlist, side-effect ledger | Deterministic check on every trial |
| Semantic | Predeclared required/forbidden claims or calibrated human/model rubric | Paired source/follow-up scores with disagreements retained |
| Statistical | A predeclared rate or score difference across repeated paired trials | Trial count, pairing, model/settings, interval or test, and raw outcomes |

For semantic checks, state which meaning-bearing facts must remain and which presentation features may vary. Calibrate model judges against a small human-labeled slice and retain a human escalation path for consequential disagreements. For statistical checks, freeze the task evidence and tool state, pair source and follow-up trials, and choose the tolerance before seeing results. One passing pair is a smoke check, not stability evidence.

Example contract:

```yaml
source: "Rank A and B using the supplied latency and cost table. Return JSON."
transform: "Reorder the table rows and rephrase the request; change no values."
per_trial_oracles:
  - valid_json_with_keys: [ranking, evidence]
  - cited_values_equal_frozen_table: true
  - forbidden_side_effects: []
semantic_relation:
  required: "same ranking unless the source run is within the declared tie margin"
  allowed: "wording and evidence order may vary"
statistical_contract:
  paired_trials: "<predeclared count>"
  metric: "rate of oracle-complete outputs"
  tolerance: "candidate lower by no more than the preregistered margin"
```

The numbers above illustrate a contract shape; set trial count, tie margin, and tolerance from the decision risk and measurement plan. Record raw paired outcomes so a failed relation can be reproduced or reviewed.

If variants cause swings beyond the declared semantic or statistical boundary, retain the failing pair as a regression case and investigate prompt ambiguity, evidence order effects, tool errors, or grader instability. If the transformation changed relevant evidence or policy facts, reject the metamorphic relation rather than blaming the agent.

For deterministic parsers, calculators, and config adapters used by an agent, run the reusable [property and metamorphic contract workflow](../../qa-testing-strategy/references/property-based-testing.md#runnable-contract-workflow) before agent-level trials. That runner is for deterministic code contracts; it does not turn exact output equality into a valid language-model oracle.

---

## Example: Complete Task Set

**Agent:** Marketing Researcher for B2B SaaS

| # | Task |
|---|------|
| 1 | Build TAM/SAM/SOM for UK sole-trader tax app; show assumptions + calc steps |
| 2 | Rank top 5 EU corridors for FX pay-ins with KPIs, fees, schemes, risks |
| 3 | Compare UK EMI vs PI for Phase-1 entry: pros/cons, costs, timeline |
| 4 | 200-word exec brief on Turkiye entry (FAST/TR-QR), with sources list |
| 5 | Competitor teardown (3 firms): pricing table + wedge opportunities |
| 6 | 30/60/90 day entry plan: partners, licenses, KPIs, kill criteria |
| 7 | Build "visa waiver" quick matrix (regions, BIN usage constraints) with notes |
| 8 | Create JSON extract of assumptions for Metabase ingestion |
| 9 | Draft stakeholder slide headlines (6) with one-line evidence per slide |
| 10 | Risk register (top-10): likelihood * impact, mitigations, owner |
