# Reasoning Prompt Template

*Purpose: Scaffold prompts for tasks that need multi-step reasoning without defaulting to full visible chain-of-thought. Default to internal reasoning and a concise final answer; expose steps only when the task or user explicitly requires them.*

---

## When to Use

Use this template when:

- The task requires reasoning, planning, diagnosis, or calculation
- You want reliable final answers with a short explanation
- The task benefits from structured decomposition but not necessarily a full visible trace
- You need an audit-friendly or educational variant that shows steps explicitly

---

## Structure

This template has 3 modes:

1. **Default mode** - internal reasoning, final answer only
2. **Brief-justification mode** - final answer plus 1-3 concise bullets
3. **Visible-steps mode** - explicit steps only for education, audit, or user-requested walkthroughs

---

# TEMPLATE STARTS HERE

## Mode A: Default (Recommended)

```text
TASK:
{user_question}

RULES:
- Think through the task internally before answering.
- Return only the final answer unless a short explanation is needed.
- If information is missing, say what is missing instead of guessing.

OUTPUT:
{final_answer_format}
```

## Mode B: Final Answer + Brief Justification

```text
TASK:
{user_question}

RULES:
- Think through the task internally before answering.
- Return the final answer first.
- Then provide a brief justification in 1-3 bullets.
- Do not reveal a full hidden reasoning trace.

OUTPUT:
Final answer: {answer}
Why:
- {brief_reason_1}
- {brief_reason_2}
```

## Mode C: Visible Steps (Only When Needed)

```text
TASK:
{user_question}

RULES:
- Show the reasoning steps explicitly because the task is educational, auditable, or the user asked for them.
- Keep the steps factual and concise.
- Finish with a clearly marked final answer.

OUTPUT:
Steps:
1. ...
2. ...
3. ...

Final answer: {answer}
```

---

# COMPLETE EXAMPLES

## Concise Decision Support

```text
TASK:
Should we add retrieval before fine-tuning for this internal documentation assistant?

RULES:
- Think through the task internally before answering.
- Return the final answer first.
- Then provide a brief justification in 1-3 bullets.
- Do not reveal a full hidden reasoning trace.

OUTPUT:
Final answer: Yes, add retrieval first.
Why:
- The requirement is current/private knowledge, which retrieval handles directly.
- Fine-tuning will not keep changing documentation current.
- Retrieval is lower-risk and easier to evaluate before model adaptation.
```

## Educational Walkthrough

```text
TASK:
If a service handles 12 requests per second and each request takes 250 ms of CPU time, what is the steady-state CPU demand?

RULES:
- Show the reasoning steps explicitly because this is an educational walkthrough.
- Keep the steps factual and concise.
- Finish with a clearly marked final answer.

OUTPUT:
Steps:
1. Each request consumes 0.25 CPU-seconds.
2. At 12 requests per second, demand is 12 x 0.25 = 3 CPU-seconds per second.
3. That equals 3 fully utilized CPU cores of steady-state demand.

Final answer: About 3 CPU cores.
```

---

## Quality Checklist

Before finalizing:

- [ ] Pick the lightest reasoning mode that satisfies the task
- [ ] Default to internal reasoning unless visible steps are clearly required
- [ ] If using visible steps, keep them concise and task-relevant
- [ ] Final answer is clearly separated from explanation
- [ ] Missing information is called out explicitly instead of filled in by guesswork

---

*For tool-use workflows, see [template-react.md](template-react.md). For broader prompt design guidance, see [../../references/prompt-engineering-patterns.md](../../references/prompt-engineering-patterns.md).*
