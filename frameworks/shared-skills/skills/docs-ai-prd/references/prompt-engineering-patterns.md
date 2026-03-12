# Prompt Engineering Patterns

*Purpose: Actionable prompt engineering patterns, checklists, and templates for GenAI and agentic coding. For Claude Code, Copilot, Cursor, Codex, and any LLM-driven tool. Everything here is ready for use in production and workflow automation.*

## Contents

- Structured prompt format
- Decomposition and sequencing
- Context hygiene and progressive disclosure
- Self-checks and anti-patterns

---

## Core Patterns

### Pattern 1: Structured Prompt Format

**Use when:** You want reproducible, reliable results from an LLM or coding agent.

**Structure:**
```

[System/role statement] (if supported)
[Context block: what the agent needs to know]
[Instruction: what to do, constraints, desired style/tone]
[Output requirements: format, length, code blocks, etc.]

```

**Checklist:**
- [ ] Set the role/context (“You are a senior Python dev…”)
- [ ] Include only relevant background (avoid overload)
- [ ] Explicitly state what you want (“Generate a REST API for X…”)
- [ ] Specify any required style or format (e.g., “Return in Gherkin”, “Output Markdown only”)
- [ ] Keep each prompt focused on a single task

---

### Pattern 2: Chain-of-Thought (CoT) Prompting

**Use when:** Multi-step reasoning, debugging, or process generation is needed.

**Structure:**
```

[Prompt] + “Think step by step:”

```
or  
“Show your reasoning and intermediate steps before the answer.”

**Checklist:**
- [ ] Add “think step by step” for complex problems
- [ ] Request intermediate outputs if needed
- [ ] Use CoT for code generation, test writing, debugging, or requirements analysis

---

### Pattern 3: Few-Shot/Example-Driven Prompting

**Use when:** Output consistency or format is critical (e.g., generating specs, PRDs, code snippets).

**Structure:**
- Provide 1–3 example prompts and expected outputs
- Then, “Now do the same for this new input: ...”

**Checklist:**
- [ ] Supply at least one complete example
- [ ] Align the example with the new task
- [ ] Use for templates (specs, tests, user stories, etc.)

---

### Pattern 4: Prompt Hygiene

**Use when:** Any prompt—applies everywhere.

**Checklist:**
- [ ] Prompt is focused (single instruction, no ambiguity)
- [ ] No excessive or irrelevant context
- [ ] Explicit format and output length
- [ ] Avoid open-ended “improve” or “make better” unless exploring options
- [ ] Confirm prompt is copy-paste ready for team use

---

## Decision Matrices

| Situation                        | Pattern/Approach          | Checklist                        |
|-----------------------------------|---------------------------|----------------------------------|
| New/novel task                    | Chain-of-thought          | Request reasoning, debug steps   |
| Repetitive, formatted outputs     | Structured + Few-shot     | Provide examples + output specs  |
| API/codegen for known structure   | Structured prompt         | Role + context + format          |
| Troubleshooting/gen QA            | Prompt hygiene + CoT      | Specific, step by step, single   |

---

## Common Mistakes

- AVOID: Long, open-ended prompts with mixed requests  
  - BEST: Focus each prompt on a single goal or output.

- AVOID: No output format or structure specified  
  - BEST: Always state required output format and length.

- AVOID: Providing more context than needed (overloads model, loses focus)  
  - BEST: Use only what is relevant for the task.

- AVOID: Not providing examples when exact output matters  
  - BEST: Include one or two concrete examples if reproducibility is required.

---

## Quick Reference

### Copy-Ready Prompt Skeletons

**Standard Structured Prompt**
```

You are a senior [role]. Here is the context: [insert relevant background/requirements].

Instruction: [Insert clear, focused instruction or question].

Output: [Specify format, style, code block requirements, length limits].

```

**Chain-of-Thought Debug**
```

Debug this function. Think step by step:
[Insert code or bug description here]

```

**Few-Shot Example**
```

Example 1:
Input: [Requirement]
Output: [Expected PRD snippet]

Now do the same for:
Input: [New requirement]
Output:

```

---

### Prompt Engineering QA Checklist

- [ ] Prompt is focused and clear
- [ ] Output format is specified
- [ ] No irrelevant or excessive context
- [ ] Example(s) included if needed
- [ ] Copy-paste ready for your LLM/agent

---

### Anti-Patterns

- Multiple instructions in one prompt (“Do X and also Y and maybe Z”)
- Vague prompts (“Make this better”, “Improve the code”)
- Unstructured requests (“Tell me everything about X”)
- Leaving output format up to the agent (can lead to unusable answers)

---

> **Pro Tip:** Save working prompt patterns for your team as templates. Always validate agent output before merging into production.
