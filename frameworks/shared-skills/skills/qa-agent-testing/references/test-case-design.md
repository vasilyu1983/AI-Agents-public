# Test Case Design

Patterns for designing the starter 10-task harness and expanding it into a stronger regression suite.

## Contents

- [Task Category Framework](#task-category-framework)
- [Designing Each Task](#designing-each-task)
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

### Task 1: Core Deliverable

**Purpose:** Verify the agent's primary function works correctly.

**Design criteria:**
- Use the most common request type
- Provide typical, well-formed input
- Expect standard output format

**Template:**
```text
[Primary action] [typical input] [standard context]
```

**Examples by agent type:**
- Content writer: "Write a LinkedIn post about remote work benefits"
- Code reviewer: "Review this Python function for bugs"
- Data analyst: "Analyze this sales dataset"
- PM assistant: "Draft a PRD for user authentication"

---

### Task 2: Consistency (Same Format, Different Input)

**Purpose:** Verify output consistency across varied inputs.

**Design criteria:**
- Same format as Task 1
- Different domain/topic
- Expect same structure, similar quality

**Template:**
```text
[Same action as Task 1] [different input]
```

**Examples:**
- Content writer: "Write a LinkedIn post about AI in healthcare"
- Code reviewer: "Review this JavaScript function for bugs"
- Data analyst: "Analyze this customer churn dataset"

---

### Task 3: Boundary Handling

**Purpose:** Test behavior at edge conditions.

**Design criteria:**
- Unusual or extreme input
- Edge case data (empty, very long, special characters)
- Boundary constraint values

**Template:**
```text
[Action] with [edge condition]
```

**Edge conditions to test:**
- Empty input: "Write about nothing specific"
- Very long input: [2000+ word document]
- Special characters: Unicode, emojis, code snippets
- Minimum viable: "Write with exactly 10 words"
- Maximum stretch: "Cover 20 topics in one response"

---

### Task 4: Tight Limits (Conciseness)

**Purpose:** Verify agent respects strict constraints.

**Design criteria:**
- Explicit word/character/bullet limits
- Must be verifiable
- Tests prioritization ability

**Template:**
```text
[Action] in exactly [N] [units]
```

**Examples:**
- "Summarize this article in exactly 50 words"
- "List top 3 recommendations only"
- "Explain in 2 sentences"
- "Create a 5-bullet executive summary"

**Scoring:**
- 3: Exact limit met, quality high
- 2: Within 10% of limit
- 1: Significantly over/under
- 0: Limit ignored

---

### Task 5: Multi-Step Reasoning

**Purpose:** Test complex analysis requiring multiple steps.

**Design criteria:**
- Requires logical chain of thought
- Multiple considerations to weigh
- Cite evidence for conclusions

**Template:**
```text
[Analyze] [complex input] and [derive conclusion]
```

**Examples:**
- "Analyze these three options and recommend the best one with justification"
- "Review this codebase architecture and identify the top 3 technical debt items"
- "Evaluate this market entry strategy and predict likely outcomes"

---

### Task 6: Tool/Data Lookup

**Purpose:** Test integration with external resources.

**Design criteria:**
- Requires accessing external data
- May involve web search, database, or API
- Tests information synthesis

**Template:**
```text
[Research/lookup] [topic] and [synthesize]
```

**Examples:**
- "Search for recent [topic] trends and summarize key findings"
- "Look up the current [data point] and incorporate into analysis"
- "Find 3 relevant sources on [topic] and cite them"

**Note:** Skip if agent has no external tool access.

---

### Task 7: Tone/Style Adaptation

**Purpose:** Test voice and register flexibility.

**Design criteria:**
- Explicit tone requirement
- Different from default style
- Tests audience awareness

**Template:**
```text
[Rewrite/create] for [audience] with [tone]
```

**Tone variations:**
- Formal <-> Casual
- Technical <-> Layman
- Concise <-> Detailed
- Serious <-> Playful
- Executive <-> Practitioner

**Examples:**
- "Rewrite this technical doc for a non-technical executive"
- "Convert this formal report into a casual blog post"
- "Explain this concept to a 5-year-old"

---

### Task 8: Structured Output

**Purpose:** Test ability to produce machine-readable formats.

**Design criteria:**
- Explicit format requirement (JSON, YAML, table)
- Verifiable structure
- Tests precision

**Template:**
```text
[Action] and output as [format]
```

**Formats to test:**
- JSON with specific schema
- Markdown table
- YAML configuration
- CSV data
- Numbered/bulleted lists

**Examples:**
```text
Analyze this and output as JSON with fields: summary, findings, recommendations, confidence_score
```

**Scoring:**
- 3: Valid format, correct schema, accurate content
- 2: Valid format, minor schema issues
- 1: Format attempted but malformed
- 0: Wrong format or plain text

---

### Task 9: Extract/Summarize (Synthesis)

**Purpose:** Test information extraction and distillation.

**Design criteria:**
- Long or complex input
- Specific extraction target
- Tests signal vs noise filtering

**Template:**
```text
[Extract/summarize] [specific elements] from [input]
```

**Extraction types:**
- Key quotes from transcript
- Main arguments from document
- Action items from meeting notes
- KPIs from report
- Requirements from email thread

**Examples:**
- "Extract the top 5 customer complaints from these reviews"
- "Summarize the key decisions from this meeting transcript"
- "Pull all action items and owners from this email chain"

---

### Task 10: Conflicting Requirements (Trade-offs)

**Purpose:** Test judgment when requirements conflict.

**Design criteria:**
- Two or more competing priorities
- No perfect solution exists
- Tests explicit trade-off reasoning

**Template:**
```text
[Action] balancing [priority A] with [priority B]
```

**Common conflicts:**
- Speed vs quality
- Security vs usability
- Cost vs features
- Brevity vs completeness
- Accuracy vs creativity

**Examples:**
- "Write engaging content that's also compliant with [regulations]"
- "Recommend a solution that's both cost-effective and scalable"
- "Design a process that's thorough but doesn't slow down the team"

**Expected response:**
- Acknowledge the trade-off
- Explain reasoning
- Make a clear recommendation
- Note limitations

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
