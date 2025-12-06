---
name: dev-workflow-planning
description: Structured development workflows using /brainstorm, /write-plan, and /execute-plan patterns. Transform ad-hoc conversations into systematic project execution with hypothesis-driven planning, incremental implementation, and progress tracking.
---

# Workflow Planning Skill — Quick Reference

This skill enables structured, systematic development workflows. Claude should apply these patterns when users need to break down complex projects, create implementation plans, or execute multi-step development tasks with clear checkpoints.

**Inspired by**: Obra Superpowers patterns for structured Claude Code workflows.

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

Claude should invoke this skill when a user requests:

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

#### Step 2: [Name] (~Xh)
...

### Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Risk 1 | Medium | High | Plan B if... |

### Open Questions
- [Questions to resolve before starting]
```

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

```text
PATTERN: Build in verifiable increments

For complex features:
1. Identify smallest testable unit
2. Implement and verify
3. Expand scope incrementally
4. Verify at each expansion
5. Integrate and verify whole

Example:
Feature: User authentication
- Increment 1: Basic login form (no backend)
- Increment 2: API endpoint (hardcoded response)
- Increment 3: Database integration
- Increment 4: Session management
- Increment 5: Password reset flow
```

### Progress Tracking

```text
PATTERN: Maintain visible progress

After each action:
[X] Step 1: Create database schema
[X] Step 2: Implement API endpoints
[→] Step 3: Add frontend form (IN PROGRESS)
[ ] Step 4: Write tests
[ ] Step 5: Deploy to staging

Current: Step 3 of 5 (60% complete)
Blockers: None
Next: Complete form validation
```

---

## Session Management

### Starting a Session

```text
/session-start [project context]

OUTPUT:
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
- [ ] [Second task]

### Context to Preserve
[Critical information for continuity]
```

---

## Decision Framework

```text
When faced with choices:

1. State the decision clearly
2. List options (2-4)
3. For each option:
   - Pros
   - Cons
   - Effort estimate
   - Risk level
4. Recommendation with justification
5. Reversibility assessment

Example:
Decision: How to implement authentication?

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

## Navigation

**Resources**
- [resources/planning-templates.md](resources/planning-templates.md) — Plan templates for common scenarios
- [resources/session-patterns.md](resources/session-patterns.md) — Multi-session project management
- [data/sources.json](data/sources.json) — Workflow methodology references

**Related Skills**
- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md) — System design planning
- [../product-prd-for-agents/SKILL.md](../product-prd-for-agents/SKILL.md) — Requirements to plan conversion
- [../testing-automation/SKILL.md](../testing-automation/SKILL.md) — TDD workflow integration
- [../quality-debugging-troubleshooting/SKILL.md](../quality-debugging-troubleshooting/SKILL.md) — Systematic debugging plans
