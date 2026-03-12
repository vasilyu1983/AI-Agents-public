# Prompt Engineering Patterns & Best Practices

*Purpose: Production-ready patterns, checklists, templates, and validation strategies for designing, testing, and maintaining high-quality prompts for LLMs, RAG, and agentic systems.*

---

## Core Patterns

---

### Pattern 1: Standard Prompt Scaffold

**Use when:** Designing a prompt for a new LLM task (classification, generation, reasoning, RAG, agent, etc.).

**Structure:**

```
[System/Instruction Block]
You are a helpful assistant for [task/domain]. Always [key guardrails/rules].

[Context Block]
Here is background information (docs, facts, retrieved content):

[Input Block]
User question/request: {user_input}

[Output Block]
Format your answer as: [required structure, e.g., JSON, table, step-by-step]
```

**Checklist:**

- [ ] Explicit instructions, task, and constraints included
- [ ] Input clearly separated from context/background
- [ ] Output format defined (JSON, table, bullet list, etc.)
- [ ] Prompt fits within model context window
- [ ] No ambiguous or conflicting instructions

---

### Pattern 2: Chain-of-Thought (CoT) Prompt

**Use when:** Task requires reasoning, multi-step logic, or explanations.

**Inline Example:**

```
Q: If a train leaves at 8:00am and travels 60 miles at 30 mph, what time does it arrive?
A: Let's think step by step. At 30 mph, 60 miles takes 2 hours. 8:00am + 2 hours = 10:00am. The answer is 10:00am.
```

**Checklist:**

- [ ] Add “Let’s think step by step.”
- [ ] Model required to show all intermediate steps
- [ ] Test with both simple and complex tasks

---

### Pattern 3: ReAct (Reason + Act) Prompt

**Use when:** LLM needs to interleave reasoning with actions/tool use (e.g., search, API call).

**Inline Example:**

```
User: What's the latest news about GPT-5?
Assistant:
Thought: I need up-to-date news.
Action: [Search "GPT-5 latest news"]
Observation: [Search results]
Thought: Summarize the main points for the user.
Final Answer: GPT-5 was announced on...
```

**Checklist:**

- [ ] Separate Thought, Action, Observation, and Answer blocks
- [ ] Model required to generate tool invocation when needed
- [ ] Handles failures (tool fails → replan)

---

### Pattern 4: RAG Prompt (Retrieval-Augmented)

**Use when:** LLM grounded in external knowledge via retrieved context.

**Template:**

```
You must answer based only on the provided context. If the answer is not in the context, say "Not found."

Context:
[retrieved_docs]

Question: {user_question}

Answer: [short, faithful, cite sources]
```

**Checklist:**

- [ ] Explicitly instruct to not use prior knowledge
- [ ] Clear fallback for "Not found"
- [ ] Encourage concise, cited answers

---

### Pattern 5: Output-Format Enforcement

**Use when:** Need LLM outputs in structured format for downstream use.

**Template:**

```
Return your answer as a valid JSON object:
{
  "summary": "...",
  "sources": ["...", "..."]
}
```

**Checklist:**

- [ ] Specify format and field requirements
- [ ] Include “valid JSON” or “valid YAML” in instructions
- [ ] Test for model compliance and edge cases

---

## Decision Matrices

### Prompt Pattern Selection

| Task Type      | Pattern to Use   | Checklist           |
|----------------|------------------|---------------------|
| Simple Q/A     | Standard/RAG     | Structure, context  |
| Reasoning      | Chain-of-Thought | Steps, explain      |
| Tool use       | ReAct            | Action, obs, loop   |
| Data extraction| Output-format    | JSON/Table, test    |
| Agentic        | Reflection, ReAct| Step/loop, fallback |

---

## Common Mistakes & Anti-Patterns

---

[FAIL] **Overstuffed context:** Prompt exceeds context window, model ignores late context.  
[OK] **Instead:** Use only the most relevant docs/chunks, summarize, and trim aggressively.

[FAIL] **Ambiguous instructions:** Conflicting or unclear directions cause unpredictable LLM outputs.  
[OK] **Instead:** Specify task, output, and rules as explicitly as possible; avoid “and/or”.

[FAIL] **Output drift:** Model ignores required format, e.g., missing fields or wrong structure.  
[OK] **Instead:** Validate outputs programmatically, enforce format with stricter wording.

[FAIL] **No regression tests:** Prompt changes break downstream tools or results.  
[OK] **Instead:** Version-control all core prompts, run regression suite on every change.

[FAIL] **Missing "Not found" fallback:** LLM hallucinates when info is missing in context.  
[OK] **Instead:** Always instruct model to say “Not found” or abstain when context is insufficient.

---

## Quick Reference

### Prompt Engineering Quality Checklist

- [ ] Instructions explicit and concise
- [ ] Input/context/output blocks clearly separated
- [ ] Output format (JSON, table, steps, etc.) enforced
- [ ] Handles edge/failure cases (not found, ambiguous input)
- [ ] Prompt versioned and regression-tested
- [ ] Prompt fits within model context window

---

### Emergency Playbook

- If LLM output format drifts:
  1. Tighten format spec (valid JSON only, with field names)
  2. Add output examples in prompt
  3. Add post-output validator/parsing

- If hallucinations increase:
  1. Add “Use only context” or “Say Not found if unknown”
  2. Add chain-of-thought block for more faithful reasoning
  3. Reduce/clarify prompt complexity

- If prompt changes break prod:
  1. Rollback to last passing version
  2. Add regression test for missed case

---

## Further Resources

See `data/sources.json` for:

- Anthropic Prompt Library, OpenAI Prompt docs, LangChain prompt patterns, Chain-of-Thought, ReAct, DSPy, prompt test tools

---

**Next:**  
See [references/eval-patterns.md](eval-patterns.md) for operational evaluation, testing, and monitoring playbooks for LLMs.
