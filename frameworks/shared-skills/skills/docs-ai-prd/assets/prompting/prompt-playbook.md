```markdown
# Prompt Playbook Template

*Purpose: Copy-paste ready prompt playbook for GenAI/agentic coding. Use this to standardize high-quality, reproducible prompts for coding agents (Claude Code, Copilot, Cursor, Codex, etc). Includes skeletons for common operational tasks and best-practice checklist.*

---

## When to Use

Use this playbook when:
- Creating new prompts for code generation, refactoring, testing, documentation, or planning
- Standardizing your team’s or project’s prompts for reuse by humans or agents
- Need consistent, reliable, and safe outputs from LLMs or agentic workflows

---

## Structure

This playbook contains:
1. **Prompt Skeletons for Core Tasks**
2. **Quick Reference: Prompt Hygiene**
3. **Prompt QA Checklist**

---

# TEMPLATE STARTS HERE

## 1. Prompt Skeletons for Core Tasks

**A. Feature/Component Generation**
```

You are a senior [role] working on [project/type].  
Context: [Insert 1–2 sentences of what the system/feature does, any relevant constraints].  
Instruction: Generate [component/code/class/API] that [describes key requirement], using [tech/language/framework].  
Output: Reply ONLY with the code in a single [file/block], no explanations.  
Format: [Markdown/code block/JSON/etc.]

```

**B. Bug Fixing / Refactoring**
```

Context: Here is the code that needs fixing/refactoring:  
[Insert code or link]  
Instruction: [e.g., "Fix the off-by-one error in the loop", "Refactor to improve testability"]  
Output: Return only the modified code and a summary of the change (2 sentences max).

```

**C. Test Generation**
```

Context: Here is the function/class that requires tests:  
[Insert code block or API signature]  
Instruction: Generate unit tests covering edge cases, invalid inputs, and typical use.  
Output: [Language]/[Framework]-formatted test code, with comments.  

```

**D. Documentation/Spec Generation**
```

Context: The following code/feature needs doc/spec:  
[Insert code or PRD snippet]  
Instruction: Generate concise [docstring/README/spec] summarizing function, inputs, outputs, and usage examples.  
Output: Only the documentation block in [format].

```

**E. Planning/Task Decomposition**
```

You are planning a new [feature/refactor/agentic session].  
Context: [PRD summary, goals, constraints, user stories].  
Instruction: Break this down into actionable tasks and phases, listing dependencies and edge cases.  
Output: Markdown table or checklist; do not start implementation yet.

```

---

## 2. Quick Reference: Prompt Hygiene

- [ ] Role and context specified (who/what/where/constraints)
- [ ] Explicit task/instruction (single, unambiguous)
- [ ] Desired output format stated (code block, JSON, Markdown, etc.)
- [ ] Examples included (for reproducibility or structure)
- [ ] Request for “no explanation” or “code only” if applicable
- [ ] No irrelevant information or theory

---

## 3. Prompt QA Checklist

- [ ] Prompt is focused (single clear goal)
- [ ] Context is just enough—no overload or missing info
- [ ] Output format is explicit
- [ ] Copied and pasted into LLM/agent and works as intended
- [ ] Team or agent reviewed and signed off for reuse
- [ ] If output matters: add 1–2 examples for reference

---

# COMPLETE EXAMPLE

**Feature Generation**
```

You are a senior TypeScript developer.  
Context: Building a dashboard that displays user tasks, using React.  
Instruction: Generate a reusable `TaskStatusIndicator` component that shows a color-coded icon for completed/pending tasks, supporting screen readers.  
Output: Reply only with the complete React component, using TypeScript and Markdown code block.

```

**Test Generation**
```

Context: This is the `sumArray` function:  

```python
def sumArray(arr):
    return sum(arr)
```

Instruction: Generate Python unit tests for edge cases, invalid input, and typical use.  
Output: Python test code in a Markdown code block.

```

---

## Quality Checklist

Before using or sharing:
- [ ] Chosen skeleton fits the use case
- [ ] All hygiene/QA checklist items are complete
- [ ] Copy-paste works with the intended LLM or agent
- [ ] Results are validated before merging into production
```
