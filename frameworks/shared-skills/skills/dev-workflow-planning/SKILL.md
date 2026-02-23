---
name: dev-workflow-planning
description: Structured development workflows using /brainstorm, /write-plan, and /execute-plan patterns. Transform ad-hoc conversations into systematic project execution with hypothesis-driven planning, incremental implementation, and progress tracking.
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

## Worktree-First Delivery

For production coding sessions, wrap `/execute-plan` with a delivery guardrail:

1. Create one isolated worktree per feature.
2. Execute only the approved plan scope in that worktree.
3. Run repo-defined quality gate(s) before PR (example: `npm run test:analytics-gate`).
4. Open one focused PR per feature branch.

Example flow:

```bash
./scripts/git/feature-workflow.sh start <feature-slug>
cd .worktrees/<feature-slug>
# implement plan steps
../../scripts/git/feature-workflow.sh gate
../../scripts/git/feature-workflow.sh pr --title "feat: <summary>"
```

---

## Agent Session Management (Lessons Learned)

Real-world evidence from production coding sessions (Feb 2026):

### Context Exhaustion Is the Dominant Constraint

A single session covering 5 workstreams (i18n, auth, products, retention, docs) ran to 121MB / 33 context continuations. Each continuation lost detail from prior context, causing:
- Repeated investigation of known pre-existing test failures
- Redundant file reads that were already in earlier context
- Solutions that contradicted decisions made earlier in the same session

**Rule: One feature per session.** If scope creep appears during execution, checkpoint progress and start a fresh session for the new scope.

| Session Style | Messages | Context Continuations | Errors | Outcome |
|--------------|----------|----------------------|--------|---------|
| Focused (chart gating) | 5 | 0 | 0 | Clean, zero rework |
| Medium (crush UI + BirthTimeInput) | 8 | 0 | 1 rewrite | Good after UX audit |
| Sprawling (3D + retention + quota + crush + i18n + docs) | 38 | 3+ | Multiple | Several errors, context loss |
| Massive (full redesign implementation) | 100+ | 33 | Many | Completed but costly |

### Pre-Written Plans Eliminate Rework

Sessions with pre-written, numbered step plans had near-zero rework:
- Docs actualization (11 steps, 10 files): zero rework, linear execution
- i18n refactor (5 phases, 7 tasks): systematic, minimal rework

Sessions without plans had 1-3 rewrites:
- BirthTimeInput: v1 (3 dropdowns) → v2 (hybrid with numeric input) after UX skill audit
- Phase 3 CTAs: multiple pivots as bugs were discovered during testing

**Rule:** For any task touching 3+ files, write a plan first. The plan should include:
1. Numbered steps with specific file paths
2. Verification criteria per step
3. Dependencies between steps

### Verify Plans Against Actual SDK Types

Plans written from documentation may reference APIs that don't match the actual SDK TypeScript types:
- Plan said `stripe.customers.list().total_count` → SDK has `data.length`
- Plan assumed `invoice.subscription` → API changed to `invoice.parent.subscription_details.subscription`

**Rule:** Before executing a plan step that calls an external SDK, grep the actual TypeScript definitions:
```bash
# Verify Stripe SDK types before using planned API calls
grep -r "total_count" node_modules/stripe/types/ || echo "NOT FOUND — check actual type"
```

### Checkpoint Protocol for Long Sessions

If a session must span multiple features:
1. After completing each feature, summarize: what changed, what was verified, what's pending
2. Commit completed work before starting next feature
3. If context starts feeling thin (repeating file reads, losing track of changes), start a new session
4. Transfer context via a written summary in the plan file, not by relying on conversation history

---

## Command Preflight Protocol (Lessons Learned)

Use this preflight before running broad edits/tests/reviews to avoid avoidable tool churn.

### 60-Second Preflight

1. Confirm context:
   - `pwd`
   - `git branch --show-current`
   - `ls -la`
2. Verify target paths before running heavy commands:
   - `test -e <path>` or `rg --files <root> | head`
   - Prefer discovery first, then exact-path commands.
3. Validate command flags against actual tool version:
   - Example: run `npx eslint --help` before assuming legacy flags like `--file`.
4. Quote glob-sensitive paths (especially App Router segments):
   - Use `'app/src/app/ask/[category]/page.tsx'` to avoid shell glob expansion errors.
5. Fail fast on path errors:
   - If command reports missing path/pattern, stop and re-derive repository shape before continuing.

### Git/Branch Safety Preflight

Run before `checkout`, `merge`, and `commit`:

- `git status --porcelain` (must be clean or intentionally scoped)
- `test -f .git/index.lock && ps aux | rg "[g]it"` (lock/process check)
- If switching branches with local changes, commit or stash first.

### E2E/Server Preflight

Before Playwright/full E2E:

- Verify target app dir exists (`test -d app`)
- Verify web server port is free (`lsof -i :3001`)
- Ensure test file/glob exists before running (`rg --files tests/e2e | rg <pattern>`)

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
[IN PROGRESS] Step 3: Add frontend form
[ ] Step 4: Write tests
[ ] Step 5: Deploy to staging

Current: Step 3 of 5 (60% complete)
Blockers: None
Next: Complete form validation
```

### Work in Progress (WIP) Limits

```text
PATTERN: Limit concurrent work to improve flow

WIP limits restrict maximum items in each workflow stage.
Benefits: Makes blockers visible, reduces context switching,
often increases throughput.

RECOMMENDED LIMITS:
| Level | Limit | Rationale |
|-------|-------|-----------|
| Individual | 2-3 tasks | Minimize context switching |
| Team (stories) | Team size + 1 | Allow pairing without blocking |
| In Progress column | 3-5 items | Force completion before starting |
| Code Review | 2-3 PRs | Prevent review bottleneck |

SETTING WIP LIMITS:
1. Start with team size + 1
2. Monitor for 2-4 weeks
3. If limits never reached -> lower them
4. If constantly blocked -> investigate bottleneck, don't raise limit
5. Adjust based on actual flow data

WHEN TO VIOLATE (thoughtfully):
- Emergency production fix
- Unblocking another team
- Document the exception and review in retro
```

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

## Definition of Ready / Done (DoR/DoD)

**[assets/template-dor-dod.md](assets/template-dor-dod.md)** - Checklists for work readiness and completion.

**[assets/template-work-item-ticket.md](assets/template-work-item-ticket.md)** - Ticket template with DoR/DoD and testable acceptance criteria.

### Key Sections

- **Definition of Ready** - User story, bug, technical task checklists
- **Definition of Done** - Feature, bug fix, spike completion criteria
- **Acceptance Criteria Templates** - Gherkin (Given/When/Then), bullet list, rule-based
- **Estimation Guidelines** - Story point reference scale (1-21+), slicing strategies
- **Planning Levels** - Roadmap -> Milestone -> Sprint -> Task hierarchy
- **Cross-Functional Coordination** - RACI matrix, handoff checklists

---

## Do / Avoid

### GOOD: Do

- Check DoR before pulling work into sprint
- Verify DoD before marking complete
- Size stories using reference scale
- Slice large stories (>8 points)
- Document acceptance criteria upfront
- Include risk buffer in estimates
- Coordinate handoffs explicitly

### BAD: Avoid

- Starting work without clear acceptance criteria
- Declaring "done" without testing
- Estimating without understanding scope
- Working on stories too big to finish in sprint
- Skipping code review "to save time"
- Deploying without staging verification
- Assuming handoffs happen automatically

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

## Optional: AI/Automation

> **Note**: AI can assist but should not replace human judgment on priorities and acceptance.

- **Generate acceptance criteria** - Draft from story description (needs review)
- **Suggest story slicing** - Based on complexity analysis
- **Dependency mapping** - Identify blocking relationships
- **AI-augmented planning** - Use LLMs to draft plans, but validate assumptions

### AI-Assisted Planning Best Practices

1. Planning first - Create a plan before coding
2. Scope management - Keep tasks small and verifiable
3. Iterative steps - Ship in increments with checkpoints
4. Human oversight - Validate assumptions and outputs (tests, logs, metrics)

### Bounded Claims

- AI-generated acceptance criteria need human review
- Story point estimates require team calibration
- Dependency mapping suggestions need validation
- AI impact on delivery stability requires monitoring

---

## Navigation

### Resources

- [references/planning-templates.md](references/planning-templates.md) - Plan templates for common scenarios
- [references/session-patterns.md](references/session-patterns.md) - Multi-session project management
- [references/flow-metrics.md](references/flow-metrics.md) - DORA metrics, WIP limits, flow optimization
- [references/agile-ceremony-patterns.md](references/agile-ceremony-patterns.md) - Sprint ceremonies, retrospectives, facilitation patterns
- [references/technical-debt-management.md](references/technical-debt-management.md) - Debt classification, prioritization, remediation workflows
- [references/remote-async-workflows.md](references/remote-async-workflows.md) - Async-first patterns, distributed team coordination
- [assets/template-dor-dod.md](assets/template-dor-dod.md) - DoR/DoD checklists, estimation, cross-functional coordination
- [assets/template-work-item-ticket.md](assets/template-work-item-ticket.md) - Work item ticket template (DoR/DoD + acceptance criteria)
- [data/sources.json](data/sources.json) - Workflow methodology references

### Related Skills

- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md) - System design planning
- [../docs-ai-prd/SKILL.md](../docs-ai-prd/SKILL.md) - Requirements to plan conversion
- [../qa-testing-strategy/SKILL.md](../qa-testing-strategy/SKILL.md) - TDD workflow integration
- [../qa-debugging/SKILL.md](../qa-debugging/SKILL.md) - Systematic debugging plans

---

## Operational Addendum (Feb 2026)

### Shell Safety Gate (Run Before Any File/CLI Operation)

1. Path check: `test -e <path>` (or `ls <path>`) before `sed/cat/rg` on a file.
2. Quote dynamic paths and patterns.
3. For multi-pattern ripgrep, always use `-e` form:

```bash
rg -n -e "pattern one" -e "pattern two" <targets>
```

4. For paths with glob chars (`[]`, `*`, `?`) or spaces, use quoting/escaping.

### CLI Compatibility Probe (First Use Per Tool)

Before first use in a session, run one capability probe and cache syntax for the rest of the task:

```bash
npx eslint --help
npx vitest --help
npx tsc --help
```

Use probed syntax, not assumed flags.

### Tiered Verification Protocol

Run checks in this order:

1. Edited-file lint/type checks.
2. Feature-scope tests.
3. Full lint/type/build gate once before handoff.

If the same baseline failure repeats unchanged twice, stop re-running broad checks and either:
- narrow scope, or
- record a baseline waiver in the handoff.

### Failure Ledger (Mandatory on Nonzero Exit)

After every failed command, capture:
- Command
- Failure class (path/glob/flag/env/baseline)
- What changed before retry

Do not retry an identical command without changing inputs/environment.

### Done/Not Done Closure Contract

Every execution summary must end with:
- `Done`: completed acceptance criteria
- `Not done`: remaining items/blockers
- `Checks run`: exact commands run + pass/fail/skip
- `Next required action`: one concrete next step

### Session Scope Guard

At session start, define a maximum scope boundary:

1. State 1-2 deliverables for this session (not a wishlist).
2. If scope creeps beyond the boundary, stop and split into a follow-up session.
3. Prefer completing one feature fully over starting three partially.

A session that exhausts context with half-finished work is worse than a session that ships one clean change.

### Proactive Plan-Doc Reading

Before implementing any feature step:

1. Check if a plan/spec doc exists for the current feature (e.g., `docs/redesign/`, `docs/product/`, project plan files).
2. Read the relevant section of the plan before writing code.
3. Do not rely on user to paste plan context into the conversation — proactively find and load it.

This prevents building features that contradict the agreed plan or miss requirements documented elsewhere.

## Ops Session Control: Keep LLM Execution Reliable

### Scope Limits (Default)

- One feature stream per execution session.
- If work spans more than 3 independent domains (for example i18n + pricing + analytics + UI), split into separate sessions.
- For tasks touching 3+ files, require a numbered plan before edits.

### Fan-Out Limits for Subtasks

- Max 3 active subagents at once.
- Assign each subagent a file ownership boundary.
- Merge after each batch before spawning new subagents.

### Practical Batch Pattern

```text
Batch 1: discovery + plan
Batch 2: implementation in one domain
Batch 3: verification + fixups
Batch 4: handoff summary
```

### Checkpoint Contract (every batch)

Report in one block:
- what changed,
- what was verified,
- what is blocked,
- exact next command.

