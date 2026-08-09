# Reasoning Patterns (Private Reasoning & Thinking Modes)

## Table of Contents

- [Contents](#contents)
- [0. When to Use Private Reasoning](#0-when-to-use-private-reasoning)
- [0.5 Model-Native Thinking Controls (March 2026)](#05-model-native-thinking-controls-march-2026)
- [1. Private Reasoning Contract](#1-private-reasoning-contract)
- [2. Internal Reasoning Workflow](#2-internal-reasoning-workflow)
- [3. Final-Answer-Only Pattern](#3-final-answer-only-pattern)
- [4. Reasoning Types & Associated Patterns](#4-reasoning-types--associated-patterns)
- [4.1 Deductive Pattern (Internal)](#41-deductive-pattern-internal)
- [4.2 Analytical Pattern (Internal)](#42-analytical-pattern-internal)
- [4.3 Multi-Step Logical Pattern (Internal)](#43-multi-step-logical-pattern-internal)
- [4.4 Evidence-Based Pattern (Internal)](#44-evidence-based-pattern-internal)
- [5. RAG-Compatible Private Reasoning](#5-rag-compatible-private-reasoning)
- [6. Agent-Compatible Private Reasoning](#6-agent-compatible-private-reasoning)
- [7. Classification Reasoning](#7-classification-reasoning)
- [8. Numeric / Computational Reasoning](#8-numeric--computational-reasoning)
- [9. Decision Tree Reasoning (Private)](#9-decision-tree-reasoning-private)
- [10. Handling Uncertainty](#10-handling-uncertainty)
- [11. Anti-Patterns (Forbidden)](#11-anti-patterns-forbidden)
- [12. Quick Reference Table](#12-quick-reference-table)

*Purpose: Provide deterministic reasoning workflows without exposing internal scratchpads or visible chain-of-thought.*

Use private reasoning by default and return **only** the final answer unless the user explicitly asks for visible steps.

## Contents
- When to use private reasoning
- Model-native thinking controls
- Private reasoning contract
- Internal reasoning workflow
- Final-answer-only pattern
- Reasoning types & associated patterns
- RAG-compatible private reasoning
- Agent-compatible private reasoning
- Classification reasoning
- Numeric / computational reasoning
- Decision tree reasoning (private)
- Handling uncertainty
- Anti-patterns
- Quick reference table

---

## 0. When to Use Private Reasoning

Use private reasoning when the task genuinely benefits from multi-step internal work:

- Mathematical or symbolic reasoning
- Complex coding/debugging
- Multi-constraint classification or decisioning
- Tool workflows that require verification before the next action

Avoid explicit visible reasoning prompts for:

- Simple factual retrieval
- Straight extraction or schema filling
- Rewrites and summarization
- Single-step routing/classification

Operational rule:

- Prefer model-native reasoning controls when the provider offers them.
- Prefer final-answer-only prompting for production.
- Ask for visible steps only when the user needs auditability, teaching output, or debugging artifacts.

---

## 0.5 Model-Native Thinking Controls (March 2026)

Use provider-native reasoning controls before inventing visible scratchpad patterns.

| Provider | Preferred Control | Use When | Prompting Note |
|---------|-------------------|-----------|----------------|
| OpenAI | Reasoning models / effort controls | Coding, deep analysis, multi-step planning | Ask for the final artifact and checks, not visible chain-of-thought |
| Anthropic | Adaptive thinking and interleaved thinking where supported | Complex Claude analysis and tool workflows | Keep instructions high-level; avoid repetitive "think step-by-step" language |
| Google | Gemini thinking-capable models and provider defaults | Multimodal or mixed reasoning tasks | Start from provider defaults, then tune after evals |
| Any provider without native controls | Final-answer-only prompt plus explicit output contract | Simpler tasks or fallback paths | Keep reasoning private and keep the prompt compact |

### Model-Native Best Practices

**1. High-Level Over Prescriptive**:

When native thinking is enabled, describe the goal and checks instead of scripting every internal step.

```text
# Good
Solve the problem carefully. Validate the result against the constraints. Return only the final answer in the required format.

# Avoid
Think step-by-step. First analyze X. Then analyze Y. Then explain every intermediate thought.
```

**2. Budget By Eval, Not Habit**:

- Raise effort/thinking only when evals justify the latency and cost
- Lower effort on extractors, deterministic schemas, and trivial routing
- Separate reasoning budget from output-token budget in your rollout criteria

**3. Do Not Require Visible Scratchpads In Production**:

- Avoid `<thinking>` or similar visible reasoning tags unless a provider explicitly documents them for the target workflow
- Do not ask the model to emit its full chain-of-thought as part of normal production output

### Reflection Tool Pattern

For agentic workflows that need auditable checkpoints, add a lightweight reflection tool to pause and verify state:

```json
{
  "name": "think",
  "description": "Use this tool to stop and think about whether you have all the information needed to proceed, or whether you should gather more information first.",
  "input_schema": {
    "type": "object",
    "properties": {
      "thought": {
        "type": "string",
        "description": "Your reflection on the current state and next steps"
      }
    },
    "required": ["thought"]
  }
}
```

**When to call a reflection/think tool**:
- Before making irreversible actions
- When multiple tools could apply
- After receiving unexpected results
- Before completing a complex multi-step task

### Checklist

- [ ] Native thinking controls used when the provider supports them
- [ ] Reasoning effort matches task complexity and eval evidence
- [ ] No redundant step-by-step instructions with native thinking enabled
- [ ] Reflection/think tool added only when an auditable checkpoint is useful
- [ ] Visible scratchpads avoided unless explicitly required

---

## 1. Private Reasoning Contract

Rules:
- Perform all reasoning internally.  
- Output only the final result in the required format.  
- Never include visible scratchpad markers unless the user explicitly demands visible reasoning.  
- Keep answers short, factual, deterministic.  
- No ambiguity, no filler, no narrative.  

Checklist:
- [ ] No visible reasoning markers  
- [ ] Final answer only  
- [ ] Output shape exact  
- [ ] No speculative language  
- [ ] No invented facts  

---

## 2. Internal Reasoning Workflow

Use this multi-step internal workflow for every reasoning task:

1. Parse the task into a single objective  
2. Identify required data  
3. Isolate constraints  
4. Build a silent step-by-step solution  
5. Validate against format + constraints  
6. Produce the final answer only  

**Nothing from steps 1–5 may appear in the output.**

---

## 3. Final-Answer-Only Pattern

### 3.1 Structure

```

{{final_answer_only}}

```

Rules:
- No explanation  
- No intermediate steps  
- No justification unless required by schema  
- Keep the tone operational  

---

## 4. Reasoning Types & Associated Patterns

Below are approved reasoning patterns the model may use internally (never revealed).

---

## 4.1 Deductive Pattern (Internal)
Use when task requires applying rules to facts.

Internal steps (not shown):
- Match fact → rule  
- Apply rule deterministically  
- Produce outcome  

Output:
```

{{final_answer}}

```

---

## 4.2 Analytical Pattern (Internal)
Use for comparisons, evaluations, or transformations.

Internal steps (not shown):
- Break down components  
- Evaluate against criteria  
- Choose deterministic result  

Output:
```

{{final_answer}}

```

---

## 4.3 Multi-Step Logical Pattern (Internal)
Use for multi-operation tasks.

Internal steps (not shown):
- Sequence sub-steps  
- Execute operations  
- Validate intermediate structure  
- Generate final result  

Output:
```

{{result}}

```

---

## 4.4 Evidence-Based Pattern (Internal)
Use when data must be extracted then synthesized.

Internal steps (not shown):
- Identify relevant data  
- Extract verbatim values  
- Produce synthesis strictly from evidence  

Output:
```

{{answer}}

```

---

## 5. RAG-Compatible Private Reasoning

When used with RAG:
- Use evidence-only logic  
- Cite only when required  
- No chain-of-thought about relevance  
- No invented connections  

Output pattern:
```

Answer:
...
Sources:

- [[chunk-1]]

```

Checklist:
- [ ] Evidence matches retrieval  
- [ ] No inference beyond context  

---

## 6. Agent-Compatible Private Reasoning

When using tools:
- All deliberation internal  
- Plans are allowed (operational, short, no reasoning)  
- Tool decisions cannot reveal why  

Allowed plan pattern:
```

Plan:

- step 1
- step 2

Action:
{...}

Answer:
null

```

Checklist:
- [ ] Plan contains actions only, never reasoning  
- [ ] No heuristics or justification  

---

## 7. Classification Reasoning

Reasoning rules:
- Use closed-set logic internally  
- Default to “unknown” when unclear  
- No probability disclosures  

Output pattern:
```

{
  "class": "A|B|C|unknown"
}

```

Checklist:
- [ ] Class deterministic  
- [ ] No “likely/probably”  

---

## 8. Numeric / Computational Reasoning

Allowed:
- Internal arithmetic  
- Internal validation  
- Internal unit consistency  

Not allowed:
- Showing steps  
- Explaining calculations  

Output:
```

{{numeric_result}}

```

---

## 9. Decision Tree Reasoning (Private)

Decision trees must be executed silently.

Internal:
- Evaluate branches in order  
- Pick first true condition  
- Ignore others  

Output:
```

{"class": "..."}

```

Checklist:
- [ ] No branch logic exposed  
- [ ] Result matches deterministic node  

---

## 10. Handling Uncertainty

If input insufficient:
```

"unknown"

```
or schema-defined fallback (e.g., null).

Rules:
- Never guess  
- Never explain  
- Never expose uncertainty rationale  

---

## 11. Anti-Patterns (Forbidden)

Do not:
- Include visible reasoning  
- Mention steps, decisions, logic  
- Say “based on my analysis”  
- Provide long explanations  
- Reveal rule application  
- Reveal evidence selection process  
- Expose internal ambiguity handling  
- Offer probability statements  

---

## 12. Quick Reference Table

| Scenario | Pattern | Output |
|----------|---------|---------|
| Multi-step reasoning | Multi-Step Logical | Final answer only |
| Rule-based | Deductive | Deterministic result |
| Comparison | Analytical | Direct output |
| Evidence-based RAG | RAG private reasoning | Answer + citations |
| Tool use | Agent-Compatible | Plan + action/answer |
| Classification | Closed-set | JSON object |
