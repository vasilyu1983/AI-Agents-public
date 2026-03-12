# Planning Templates

Copy-paste templates for common planning scenarios.

---

## Feature Implementation Plan

```markdown
## Implementation Plan: [Feature Name]

### Goal
[Single sentence describing the outcome]

### Success Criteria
- [ ] Criterion 1: [Measurable outcome]
- [ ] Criterion 2: [Measurable outcome]
- [ ] Criterion 3: [Measurable outcome]

### Prerequisites
- [ ] [Dependency or setup required before starting]

### Steps

#### Step 1: [Name]
- **What**: [Specific actions to take]
- **Files**: [Files to modify/create]
- **Verification**: [How to confirm done]

#### Step 2: [Name]
- **What**: [Specific actions to take]
- **Files**: [Files to modify/create]
- **Verification**: [How to confirm done]

#### Step 3: [Name]
- **What**: [Specific actions to take]
- **Files**: [Files to modify/create]
- **Verification**: [How to confirm done]

### Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Risk 1] | Low/Med/High | Low/Med/High | [Plan B] |

### Open Questions
- [ ] [Question to resolve before/during implementation]
```

---

## Bug Fix Plan

```markdown
## Bug Fix Plan: [Issue Title]

### Problem Statement
[What's broken and how it manifests]

### Reproduction Steps
1. [Step to reproduce]
2. [Step to reproduce]
3. [Expected vs actual behavior]

### Root Cause Hypothesis
[What you believe is causing the issue]

### Fix Strategy
1. [Approach to fix]
2. [Files to modify]
3. [Testing approach]

### Verification
- [ ] Bug no longer reproducible
- [ ] Existing tests pass
- [ ] New regression test added
- [ ] No side effects observed
```

---

## Refactoring Plan

```markdown
## Refactoring Plan: [Component/Module]

### Current State
[What exists now and why it's problematic]

### Target State
[What it should look like after refactoring]

### Constraints
- [ ] Must maintain backward compatibility
- [ ] No behavior changes
- [ ] All tests must pass

### Steps (in order of execution)

#### Phase 1: Preparation
- [ ] Add missing test coverage
- [ ] Document current behavior

#### Phase 2: Refactoring
- [ ] [Specific refactoring step]
- [ ] [Specific refactoring step]

#### Phase 3: Verification
- [ ] Run full test suite
- [ ] Manual smoke test
- [ ] Performance comparison

### Rollback Plan
[How to revert if something goes wrong]
```

---

## Spike/Research Plan

```markdown
## Spike: [Research Topic]

### Question to Answer
[Specific question this spike will answer]

### Time Box
[Maximum time to spend: e.g., 2 hours]

### Success Criteria
- [ ] Question answered with evidence
- [ ] Recommendation documented
- [ ] Next steps identified

### Research Approach
1. [What to investigate first]
2. [What to investigate second]
3. [How to validate findings]

### Output
- Summary of findings
- Recommendation with justification
- Proof of concept (if applicable)
```

---

## Migration Plan

```markdown
## Migration Plan: [From X to Y]

### Scope
- **Affected systems**: [List]
- **Affected users**: [Count/groups]
- **Data to migrate**: [Type and volume]

### Pre-Migration
- [ ] Backup existing data
- [ ] Notify stakeholders
- [ ] Set up rollback procedure

### Migration Steps
1. [ ] [Step with specific commands/actions]
2. [ ] [Verification checkpoint]
3. [ ] [Next step]

### Post-Migration
- [ ] Verify data integrity
- [ ] Run smoke tests
- [ ] Monitor for errors (24h)

### Rollback Procedure
[Exact steps to revert if needed]

### Communication Plan
| When | What | Who |
|------|------|-----|
| Before | Migration notice | All users |
| During | Status updates | Stakeholders |
| After | Completion notice | All users |
```

---

## Daily/Sprint Planning

```markdown
## [Date] Planning

### Today's Goal
[One sentence: what success looks like today]

### Priority Tasks
1. [ ] [Highest priority task]
2. [ ] [Second priority]
3. [ ] [Third priority]

### Blockers
- [Any blockers to address first]

### Carry-over from Yesterday
- [Incomplete items from previous session]

### End of Day Checkpoint
- [ ] Goal achieved?
- [ ] What blocked progress?
- [ ] What's first tomorrow?
```

---

## Swarm-Ready Implementation Plan

Use this template when the plan will be executed by multiple parallel subagents.

```markdown
## Implementation Plan: [Feature Name]

### Goal
[Single sentence describing the outcome]

### Success Criteria
- [ ] Criterion 1: [Measurable outcome]
- [ ] Criterion 2: [Measurable outcome]

### Task Dependency Graph

| Task ID | Name | depends_on | Files (owned) | Agent Role |
|---------|------|------------|----------------|------------|
| T1 | [Task name] | [] | [file paths] | [role] |
| T2 | [Task name] | [T1] | [file paths] | [role] |
| T3 | [Task name] | [] | [file paths] | [role] |
| T4 | [Task name] | [T1, T3] | [file paths] | [role] |

### Execution Strategy
- [ ] **Swarm Waves** (accuracy-first: launch unblocked tasks per wave)
- [ ] **Super Swarms** (speed-first: launch all tasks, resolve conflicts after)

### Task Details

#### T1: [Name]
- **What**: [specific actions]
- **Files to create/modify**: [full paths]
- **Interface contracts**: [what this task exposes for dependent tasks]
- **Acceptance criteria**: [how to verify done]
- **Implementation steps**:
  1. [Step]
  2. [Step]

#### T2: [Name]
- **What**: [specific actions]
- **Depends on**: T1 (needs [specific output/file from T1])
- **Files to create/modify**: [full paths]
- **Acceptance criteria**: [how to verify done]
- **Implementation steps**:
  1. [Step]
  2. [Step]

### Shared Interfaces
[Document any files, types, or contracts that multiple tasks depend on.
Define these before launching parallel work.]

### Conflict Resolution
[If using Super Swarms: which agent's output takes priority for shared files?
What's the merge strategy?]

### Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Merge conflict on shared types | Medium | Medium | Define interfaces upfront |
```

---

## Incremental Implementation Pattern

Build in verifiable increments — identify the smallest testable unit, implement and verify, then expand scope.

**Example — User Authentication feature:**

| Increment | What to Build | Verify By |
|-----------|---------------|-----------|
| 1 | Basic login form (no backend) | Form renders, submits |
| 2 | API endpoint (hardcoded response) | Returns 200 |
| 3 | Database integration | Reads/writes real users |
| 4 | Session management | Session persists across requests |
| 5 | Password reset flow | Full reset cycle works |

---

## WIP Limits Reference

WIP limits restrict maximum items in each workflow stage. Benefits: makes blockers visible, reduces context switching, often increases throughput.

### Recommended Limits

| Level | Limit | Rationale |
|-------|-------|-----------|
| Individual | 2-3 tasks | Minimize context switching |
| Team (stories) | Team size + 1 | Allow pairing without blocking |
| In Progress column | 3-5 items | Force completion before starting |
| Code Review | 2-3 PRs | Prevent review bottleneck |

### Setting WIP Limits

1. Start with team size + 1
2. Monitor for 2-4 weeks
3. If limits never reached → lower them
4. If constantly blocked → investigate bottleneck, don't raise limit
5. Adjust based on actual flow data

### When to Violate (thoughtfully)

- Emergency production fix
- Unblocking another team
- Document the exception and review in retro

---

## Navigation

- [Back to SKILL.md](../SKILL.md)
- [Session Patterns](session-patterns.md)
