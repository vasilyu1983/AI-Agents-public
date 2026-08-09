# Prompt Engineering Patterns

Purpose: current prompt patterns for chat models, reasoning models, and coding agents.

Last verified: 2026-03-13

## Table of Contents

- [Core Rule](#core-rule)
- [Pattern 1: Task Contract](#pattern-1-task-contract)
- [Pattern 2: Context Packaging](#pattern-2-context-packaging)
- [Pattern 3: Output Contract](#pattern-3-output-contract)
- [Pattern 4: Tool Boundary](#pattern-4-tool-boundary)
- [Pattern 5: Eval-Driven Iteration](#pattern-5-eval-driven-iteration)
- [Pattern 6: Reasoning Models](#pattern-6-reasoning-models)
- [Decision Matrix](#decision-matrix)
- [Copy-Ready Skeletons](#copy-ready-skeletons)
- [Spec Drafting](#spec-drafting)
- [Agent Handoff](#agent-handoff)
- [Review Prompt](#review-prompt)
- [Anti-Patterns](#anti-patterns)

## Core Rule

Optimize for:
- clear task contract
- relevant context only
- explicit output shape
- explicit tool and approval boundaries
- measurable evaluation criteria

Do not rely on hidden chain-of-thought prompts as a default pattern.

## Pattern 1: Task Contract

Use when: any prompt that should produce a reliable deliverable.

Specify:
- objective
- audience or target user
- constraints
- definition of done
- what to avoid

Example:

```text
Goal: Draft a PRD section for onboarding analytics.
Audience: PM and implementation team.
Constraints: Keep it under 250 words, name metrics explicitly, do not invent baseline data.
Done when: output includes problem, goals, acceptance criteria, and open questions.
```

## Pattern 2: Context Packaging

Use when: the model needs repo, product, or workflow context.

Prefer:
- short summaries
- linked file paths
- canonical docs
- only the slices needed for the task

Avoid:
- dumping entire threads or docs
- mixing live behavior and target behavior without labels
- pasting untrusted user content without marking it as untrusted

## Pattern 3: Output Contract

Use when: format matters.

Specify:
- exact format
- section order
- maximum length
- whether code blocks, tables, or JSON are allowed

Example:

```text
Return Markdown only.
Sections: Summary, Risks, Acceptance Criteria.
Keep it under 12 bullets total.
```

## Pattern 4: Tool Boundary

Use when: the assistant can call tools or take actions.

Specify:
- what tools are allowed
- what requires approval
- what must remain read-only
- what evidence is needed before action

Example:

```text
Read files and run tests freely.
Do not edit files or run migrations until the implementation approach is confirmed.
Ask before destructive commands or production-impacting actions.
```

## Pattern 5: Eval-Driven Iteration

Use when: prompts or system behavior will be reused.

Define:
- representative examples
- failure cases
- scorer or rubric
- pass/fail bar

For AI features, prefer a written eval plan over prompt tuning by feel.

## Pattern 6: Reasoning Models

Use when: the target model is a reasoning model.

Current best practice:
- keep prompts simple and direct
- ask for the answer, plan, or checklist you actually need
- request a concise rationale or decision log if humans need it
- do not ask for full hidden reasoning traces as a default instruction

Good:

```text
Return the final plan plus a short rationale for tradeoffs.
```

Bad:

```text
Think step by step and reveal every intermediate thought before answering.
```

## Decision Matrix

| Situation | Preferred pattern |
|-----------|-------------------|
| Drafting a PRD section | Task contract + output contract |
| Repo-aware coding task | Context packaging + tool boundary |
| Reusable workflow prompt | Task contract + eval-driven iteration |
| High-stakes analysis | Task contract + concise rationale + explicit constraints |

## Copy-Ready Skeletons

### Spec Drafting

```text
You are drafting a spec for [feature].

Context:
- Users: [who]
- Problem: [what is broken or missing]
- Constraints: [latency/compliance/timeline]

Task:
Write [section or full doc].

Output:
- Format: Markdown
- Sections: [list]
- Keep it under [limit]
- Do not invent metrics or baseline data
```

### Agent Handoff

```text
Goal: [objective]
Current state: [repo or product state]
Constraints: [approvals, compatibility, timebox]
Validation required: [tests, reviews, checks]
Output: [plan, patch summary, checklist]
```

### Review Prompt

```text
Review this PRD for ambiguity, missing acceptance criteria, unsupported metrics, and rollout risk.
Return findings first.
Quote the exact line or section name for each finding.
Do not rewrite the whole document unless a finding requires it.
```

## Anti-Patterns

- Multiple unrelated tasks in one prompt
- Vague instructions such as "improve this"
- Output format left unspecified
- Prompting for chain-of-thought when a concise rationale would do
- Tuning prompts without a test set or review rubric
