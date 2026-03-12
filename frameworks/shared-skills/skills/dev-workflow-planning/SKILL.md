---
name: dev-workflow-planning
description: Structured dev workflows via /brainstorm, /write-plan, /execute-plan. Use when breaking down complex projects into systematic steps.
---

# Workflow Planning Skill - Quick Reference

This skill enables structured, systematic development workflows. The assistant should apply these patterns when users need to break down complex projects, create implementation plans, or execute multi-step development tasks with clear checkpoints.

**Inspired by**: Obra Superpowers patterns for structured agent workflows.

---

## Quick Reference

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/brainstorm` | Generate ideas and approaches | Starting new features, exploring solutions |
| `/write-plan` | Create detailed implementation plan | Before coding, after requirements clarification |
| `/execute-plan` | Implement plan step-by-step | When plan is approved, ready to code |
| `/checkpoint` | Review progress, adjust plan | Mid-implementation, after major milestones |
| `/summarize` | Capture learnings, document decisions | End of session, before context reset |

## When to Use This Skill

The assistant should invoke this skill when a user requests:

- Break down a complex feature into steps
- Create an implementation plan
- Brainstorm approaches to a problem
- Execute a multi-step development task
- Track progress on a project
- Review and adjust mid-implementation

---

## The Three-Phase Workflow

### Phase 1: Brainstorm

**Purpose**: Explore the problem space and generate potential solutions.

```text
/brainstorm [topic or problem]

OUTPUT:
1. Problem Understanding
   - What are we solving?
   - Who is affected?
   - What are the constraints?

2. Potential Approaches (3-5)
   - Approach A: [description, pros, cons]
   - Approach B: [description, pros, cons]
   - Approach C: [description, pros, cons]

3. Questions to Resolve
   - [List of unknowns needing clarification]

4. Recommended Approach
   - [Selected approach with justification]
```

### Phase 2: Write Plan

**Purpose**: Create a detailed, actionable implementation plan.

```text
/write-plan [feature or task]

OUTPUT:
## Implementation Plan: [Feature Name]

### Goal
[Single sentence describing the outcome]

### Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

### Steps (with estimates)

#### Step 1: [Name] (~Xh)
- What: [specific actions]
- Files: [files to modify/create]
- Dependencies: [what must exist first]
- Verification: [how to confirm done]

### Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Risk 1 | Medium | High | Plan B if... |

### Open Questions
- [Questions to resolve before starting]
```

#### Dependency Graph for Parallel Execution

When a plan will be executed with multiple subagents, each task **must** declare its dependencies explicitly. This enables the orchestrator to determine which tasks can run in parallel.

```text
### Task Dependency Graph

| Task ID | Name | depends_on | Files | Agent Scope |
|---------|------|------------|-------|-------------|
| T1 | Setup database schema | [] | db/schema.sql | db-engineer |
| T2 | Create API routes | [T1] | src/routes/*.ts | backend-dev |
| T3 | Build auth middleware | [T1] | src/middleware/auth.ts | backend-dev |
| T4 | Frontend components | [] | src/components/*.tsx | frontend-dev |
| T5 | Integration tests | [T2, T3, T4] | tests/integration/*.test.ts | qa-agent |
```

**Rules for dependency graphs:**
- Every task declares `depends_on: []` with explicit task IDs (empty array = no blockers).
- Tasks with no dependencies can start immediately (in parallel).
- No circular dependencies — the graph must be a DAG (directed acyclic graph).
- Each task should specify its file ownership to prevent parallel conflicts.

#### Parallel Execution Strategies

**Swarm Waves (Accuracy-First)** — Launch one subagent per unblocked task, in dependency-respecting waves. Wait for each wave to complete before launching the next. Best for production code and complex interdependencies.

**Super Swarms (Speed-First)** — Launch as many subagents as possible at once, regardless of dependencies. Best for prototypes and greenfield scaffolding. Expect merge conflicts.

See [references/planning-templates.md](references/planning-templates.md) for the full swarm-ready plan template.

### Phase 3: Execute Plan

**Purpose**: Implement the plan systematically with checkpoints.

```text
/execute-plan [plan reference]

EXECUTION PATTERN:
1. Load the plan
2. For each step:
   a. Announce: "Starting Step X: [name]"
   b. Execute actions
   c. Verify completion
   d. Report: "Step X complete. [brief summary]"
3. After completion:
   a. Run all verification criteria
   b. Report final status
```

---

## Worktree-First Delivery

For production coding sessions, wrap `/execute-plan` with a delivery guardrail:

1. Create one isolated worktree per feature.
2. Execute only the approved plan scope in that worktree.
3. Run repo-defined quality gate(s) before PR (example: `npm run test:analytics-gate`).
4. Open one focused PR per feature branch.

```bash
./scripts/git/feature-workflow.sh start <feature-slug>
cd .worktrees/<feature-slug>
# implement plan steps
../../scripts/git/feature-workflow.sh gate
../../scripts/git/feature-workflow.sh pr --title "feat: <summary>"
```

---

## Agent Session Management

**Key rules from production experience (Feb 2026):**

- **One feature per session.** Context exhaustion causes rework. A sprawling session (38 messages, 3+ continuations) produced multiple errors; a focused session (5 messages) shipped clean.
- **Write a plan before touching 3+ files.** Sessions with pre-written numbered plans had near-zero rework.
- **Verify SDK types before executing plan steps.** Documentation may describe APIs that no longer match actual TypeScript definitions.

See [references/session-patterns.md](references/session-patterns.md) for the full production evidence table and checkpoint protocol for long sessions.

---

## Command Preflight Protocol

Before broad edits, tests, or reviews — run a 60-second preflight:
1. `pwd` / `git branch --show-current` / `ls -la`
2. `test -e <path>` to verify target paths before heavy commands
3. `npx <tool> --help` to validate flags before first use
4. Quote paths containing `[]`, `*`, `?`, or spaces

See [references/operational-checklists.md](references/operational-checklists.md) for the full git/branch safety preflight, E2E/server preflight, shell safety gate, and SDK type verification.

---

## Structured Patterns

### Hypothesis-Driven Development

```text
PATTERN: Test assumptions before committing

Before implementing:
1. State hypothesis: "If we [action], then [expected outcome]"
2. Define experiment: "To test this, we will [minimal test]"
3. Execute experiment
4. Evaluate: "Hypothesis confirmed/rejected because [evidence]"
5. Proceed or pivot based on result
```

### Incremental Implementation

Build in verifiable increments: smallest testable unit → implement and verify → expand scope → verify at each expansion → integrate and verify whole.

See [references/planning-templates.md](references/planning-templates.md) for an authentication feature example with 5 increments.

### Progress Tracking

```text
PATTERN: Maintain visible progress

[X] Step 1: Create database schema
[X] Step 2: Implement API endpoints
[IN PROGRESS] Step 3: Add frontend form
[ ] Step 4: Write tests

Current: Step 3 of 4 (75% complete)
Blockers: None
Next: Complete form validation
```

### Work in Progress (WIP) Limits

Limit concurrent work: individual (2-3 tasks), team stories (team size + 1), in-progress column (3-5 items), code review (2-3 PRs). If limits are never reached, lower them. If constantly blocked, investigate the bottleneck.

See [references/planning-templates.md](references/planning-templates.md) for the full WIP limits reference and setting guidelines.

---

## Milestone Checkpointing and Scope Budgeting

For multi-step execution, constrain scope and checkpoint progress at milestone boundaries.

- Define explicit session scope at start: `1-2` deliverables only.
- If a new request expands beyond scope, create a follow-up milestone.

### Milestone Checkpoint Contract

At each milestone, record:
- completed outputs (files/features/tests)
- verification results (commands + pass/fail)
- unresolved blockers
- next bounded action

### Stop Conditions

Stop and rescope when any occur:
- repeated nonzero failures without new evidence
- context churn (re-reading same files repeatedly)
- more than 3 independent domains active in one session

See [references/session-scope-budgeting.md](references/session-scope-budgeting.md) for full scope budgeting model and enforcement rules.

---

## Session Management

### Starting a Session

```text
Session initialized.
- Project: [name]
- Goal: [today's objective]
- Context loaded: [files, previous decisions]
- Plan status: [steps remaining]

Ready to continue from: [last checkpoint]
```

### Ending a Session

```text
/summarize

OUTPUT:
## Session Summary

### Completed
- [List of completed items]

### In Progress
- [Current state of incomplete work]

### Decisions Made
- [Key decisions with rationale]

### Next Session
- [ ] [First task for next time]

### Context to Preserve
[Critical information for continuity]
```

---

## Decision Framework

```text
When faced with choices:

1. State the decision clearly
2. List options (2-4)
3. For each option: Pros / Cons / Effort / Risk
4. Recommendation with justification
5. Reversibility assessment

Example:
| Option | Pros | Cons | Effort | Risk |
|--------|------|------|--------|------|
| JWT | Stateless, scalable | Token management | 2 days | Low |
| Sessions | Simple, secure | Server state | 1 day | Low |
| OAuth only | No passwords | External dependency | 3 days | Medium |

Recommendation: Sessions for MVP, plan JWT migration for scale.
```

---

## Integration with Other Skills

### With Testing Skill

```text
/write-plan with TDD:

Step 1: Write failing test
Step 2: Implement minimal code
Step 3: Verify test passes
Step 4: Refactor
Step 5: Add edge case tests
```

### With Architecture Skill

```text
/brainstorm system design:

1. Requirements clarification
2. Component identification
3. Interface definition
4. Data flow mapping
5. Implementation plan
```

---

## Definition of Ready / Done (DoR/DoD)

**[assets/template-dor-dod.md](assets/template-dor-dod.md)** - Checklists for work readiness and completion.

**[assets/template-work-item-ticket.md](assets/template-work-item-ticket.md)** - Ticket template with DoR/DoD and testable acceptance criteria.

Key sections: Definition of Ready / Done checklists, Acceptance Criteria templates (Gherkin), Estimation Guidelines (story point scale 1-21+), Planning Levels (Roadmap → Sprint → Task), Cross-Functional RACI.

---

## Do / Avoid

### GOOD: Do

- Check DoR before pulling work into sprint
- Verify DoD before marking complete
- Size stories using reference scale
- Slice large stories (>8 points)
- Document acceptance criteria upfront
- Include risk buffer in estimates

### BAD: Avoid

- Starting work without clear acceptance criteria
- Declaring "done" without testing
- Working on stories too big to finish in sprint
- Skipping code review "to save time"
- Deploying without staging verification

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **No DoR** | Unclear requirements discovered mid-sprint | Gate sprint entry with DoR |
| **Soft DoD** | "Done" means different things | Written DoD checklist |
| **Mega-stories** | Never finish, hard to track | Slice to <8 points |
| **Missing AC** | Built wrong thing | Gherkin format AC |
| **No ownership** | Work falls through cracks | RACI for every epic |
| **Hope-based estimates** | Always late | Use reference scale + buffer |

---

## AI/Automation

> **Note**: AI can assist but should not replace human judgment on priorities and acceptance.

- **Generate acceptance criteria** - Draft from story description (needs review)
- **Suggest story slicing** - Based on complexity analysis
- **Dependency mapping** - Identify blocking relationships
- **AI-augmented planning** - Use LLMs to draft plans, but validate assumptions

AI-generated criteria and estimates require human calibration before committing to them.

---

## Navigation

### Resources

- [references/planning-templates.md](references/planning-templates.md) - Plan templates, incremental implementation, WIP limits
- [references/session-patterns.md](references/session-patterns.md) - Multi-session management, production lessons (Feb 2026)
- [references/session-scope-budgeting.md](references/session-scope-budgeting.md) - Scope budgeting rules and stop/rescope criteria
- [references/operational-checklists.md](references/operational-checklists.md) - Preflight protocols, verification, failure ledger, subagent limits
- [references/flow-metrics.md](references/flow-metrics.md) - DORA metrics, WIP limits, flow optimization
- [references/agile-ceremony-patterns.md](references/agile-ceremony-patterns.md) - Sprint ceremonies, retrospectives, facilitation patterns
- [references/technical-debt-management.md](references/technical-debt-management.md) - Debt classification, prioritization, remediation workflows
- [references/remote-async-workflows.md](references/remote-async-workflows.md) - Async-first patterns, distributed team coordination
- [assets/template-dor-dod.md](assets/template-dor-dod.md) - DoR/DoD checklists, estimation, cross-functional coordination
- [assets/template-work-item-ticket.md](assets/template-work-item-ticket.md) - Work item ticket template
- [assets/template-milestone-checkpoint.md](assets/template-milestone-checkpoint.md) - Milestone checkpoint record
- [data/sources.json](data/sources.json) - Workflow methodology references

### Related Skills

- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md) - System design planning
- [../docs-ai-prd/SKILL.md](../docs-ai-prd/SKILL.md) - Requirements to plan conversion
- [../qa-testing-strategy/SKILL.md](../qa-testing-strategy/SKILL.md) - TDD workflow integration
- [../qa-debugging/SKILL.md](../qa-debugging/SKILL.md) - Systematic debugging plans
