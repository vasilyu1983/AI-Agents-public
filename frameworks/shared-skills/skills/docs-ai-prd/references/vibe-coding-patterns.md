# Vibe Coding Patterns

*Purpose: Operational patterns for running "vibe coding" workflows with GenAI and coding agents. Focus on copy-ready patterns, iterative loops, and team/agent collaboration for rapid software delivery.*

## Contents

- Vibe coding loop
- Progressive disclosure
- Human/agent role split
- Decision matrices and hygiene
- Anti-patterns

---

## Core Patterns

### Pattern 1: Vibe Coding Loop

**Use when:** Generating software via conversational, iterative prompt–agent cycles. Useful for prototyping, fast iteration, and agent-led refactoring.

**Structure:**
1. **Describe intent and vibe** (function, style, tone, constraints)
2. **Generate code/artifacts with agent** (GenAI, LLM, coding agent)
3. **Observe outcome** (run/test/preview)
4. **Provide outcome-based feedback** (e.g., "Make this more playful", "Add tests", "Support edge case X")
5. **Repeat loop until satisfied**

**Checklist:**
- [ ] High-level prompt: what, how it should feel, any constraints
- [ ] Output copy-pasted or previewed without line-by-line review
- [ ] Test/validate outcome, not just code
- [ ] Feedback is outcome-focused (“Change this part”, “Fix the error”)
- [ ] Loop continues until function and "vibe" meet needs

---

### Pattern 2: Progressive Disclosure

**Use when:** Gradually refining software through incremental agent prompts, not upfront full specs.

**Structure:**
- Start with minimal viable request (e.g., “Create a React login form, keep it playful”)
- Test/observe result
- Add/refine requirements iteratively (e.g., “Add OAuth, more color”, “Test error state”)
- Focus on functional & stylistic feedback per iteration

**Checklist:**
- [ ] Start with minimum viable prompt
- [ ] Provide iterative, incremental feedback (not a full spec up front)
- [ ] Validate/adjust after each cycle
- [ ] Document key requirements as they emerge

---

### Pattern 3: Human–Agent Role Split

**Use when:** Collaborating with agents on complex tasks; human owns intent, agent handles implementation.

**Structure:**
- Human specifies: goals, constraints, vibe/style
- Agent: generates code, runs tests, proposes options
- Human: evaluates, requests high-level adjustments, never re-codes by hand unless stuck

**Checklist:**
- [ ] Human provides intent, context, constraints, vibe
- [ ] Agent generates code/artifacts and runs checks
- [ ] Human reviews outcomes, not internals
- [ ] Agent iterates on feedback
- [ ] If agent is stuck for >30 mins or >3 failed cycles, human steps in or resets context

---

### Pattern 4: Vibe-Driven Acceptance

**Use when:** Judging code based on look/feel/behavior, not just passing tests.

**Checklist:**
- [ ] Output “feels right” (tone, style, user experience)
- [ ] Works for core happy path
- [ ] Passes basic functional checks
- [ ] Style/tone matches user’s intent or prompt

---


### Pattern 5: Production Vibe Loop (Ship Discipline)

**Use when:** Vibe coding moves from prototype to merge-ready production work.

**Structure:**
1. Isolate work in one feature worktree/branch
2. Run iterative vibe loop (intent -> generate -> observe -> feedback)
3. Run project quality gate(s)
4. Open one focused PR
5. Merge, then clean up worktree

**Checklist:**
- [ ] One feature per worktree/branch
- [ ] Tests/checks passed (at minimum repo gate)
- [ ] PR describes functional + vibe outcomes
- [ ] No unrelated refactors in the feature PR

## Decision Matrices

| Situation                   | Approach                | Validation                 |
|-----------------------------|-------------------------|----------------------------|
| Prototype, new idea         | Vibe coding loop        | Outcome-based feedback     |
| Production feature          | Agentic loop + QA       | QA checklist + review      |
| Refactor/migrate            | Progressive disclosure  | Test/run each iteration    |
| Stuck agent, blocked cycle  | Human intervention      | Manual review/adjustment   |

---

## Common Mistakes

- AVOID: Reviewing every line of agent code (not trusting the agent)  
  - BEST: Accept/observe outcomes, focus on feedback.

- AVOID: Giving full, complex specs at once  
  - BEST: Use progressive disclosure, one requirement at a time.

- AVOID: Ignoring user vibe or style (just functional requests)  
  - BEST: Specify tone, style, “how it should feel” in prompts.

- AVOID: Letting the agent loop endlessly on errors  
  - BEST: Step in if more than three cycles fail; reset or break down the problem.

---

## Quick Reference

### Vibe Coding Loop Example

```

1. Prompt: "Build a dark-mode to-do app that feels welcoming, uses emojis."
2. Agent: Generates React app, styled, emoji use
3. User: Runs app, says "Add confetti when completing a task"
4. Agent: Adds confetti, re-generates code
5. User: "Test offline support"
6. Agent: Adds service worker, enables offline mode
7. User: "Good! Make copy more encouraging"
8. Agent: Adjusts messages: "Awesome job! [CELEBRATE]"
9. User: All happy? Finalize and export code

```

---

### Vibe Coding Hygiene

- [ ] Always state intent AND desired “vibe” (tone, look, experience)
- [ ] Use short, focused prompts; iterate after each output
- [ ] Validate results by outcome (does it “work and feel right”?)
- [ ] Only deep-dive code if agent is truly stuck or for critical bugs

---

### Anti-Patterns

- Writing line-by-line specs up front (slows vibe coding, wastes agent cycles)
- Letting agent “run wild” with no feedback/validation or no pre-PR quality gate
- Accepting agent output without *any* validation (leads to broken or off-vibe software)

---

> **Pro Tip:** Vibe coding is outcome-driven, not code-driven. Use it for fast prototypes, playful features, rapid style tweaks, or to unlock new directions quickly. For production, combine with agentic QA and manual review.
