# Regression Protocol

Procedures for re-running tests after agent changes.

## Contents

- [When to Re-Run](#when-to-re-run)
- [Re-Run Process](#re-run-process)
- [Change Record](#change-record)
- [Regression Analysis](#regression-analysis)
- [Regression Log Format](#regression-log-format)
- [Version v1.X (YYYY-MM-DD)](#version-v1x-yyyy-mm-dd)
- [Quick Regression Check](#quick-regression-check)
- [Baseline Management](#baseline-management)
- [Baseline: v1.0](#baseline-v10)
- [Continuous Integration](#continuous-integration)
- [Recovery Procedures](#recovery-procedures)

## When to Re-Run

### Trigger Events

| Trigger | Scope | Priority |
|---------|-------|----------|
| Prompt change | Full 15-check suite | HIGH |
| Tool added/removed | Affected tests + Task 6 | HIGH |
| Knowledge base update | Domain-specific tests | MEDIUM |
| Model version change | Full suite | HIGH |
| Bug fix | Related tests + neighbors | MEDIUM |
| Minor wording change | Smoke test (3 core tasks) | LOW |

### Re-Run Scope Matrix

| Change Type | Tasks | Refusals | Full Scoring |
|-------------|-------|----------|--------------|
| Major prompt rewrite | All 10 | All 5 | Yes |
| Section-specific change | Related 3-4 | If safety-related | Yes |
| Tool integration | Task 6 + integration tests | 1-2 related | Yes |
| Tone/style change | Task 7 + output samples | No | Partial |
| Bug fix | Regression + 2 neighbors | If safety-related | Yes |

---

## Re-Run Process

### Step 1: Document the Change

```text
## Change Record

**Date:** YYYY-MM-DD
**Version:** v1.X -> v1.Y
**Type:** [Prompt / Tool / Knowledge / Model / Bug fix]
**Description:** [What changed and why]
**Expected Impact:** [What should improve/change]
**Risk Areas:** [What might break]
```

### Step 2: Run Test Suite

Execute tests in order:

```text
1. Core functionality (Tasks 1-3)
2. Constraint handling (Tasks 4-5)
3. External integration (Task 6) [if applicable]
4. Adaptation tests (Tasks 7-10)
5. Refusal edge cases (A-E)
```

### Step 3: Score Each Dimension

Use the standard 0-3 rubric for all 6 dimensions:
- Accuracy
- Relevance
- Structure
- Brevity
- Evidence
- Safety

### Step 4: Compare to Baseline

```text
| Dimension | Previous | Current | Delta |
|-----------|----------|---------|-------|
| Accuracy | 2.8 | 2.9 | +0.1 |
| Relevance | 2.5 | 2.6 | +0.1 |
| Structure | 2.7 | 2.7 | 0 |
| Brevity | 2.3 | 2.5 | +0.2 |
| Evidence | 2.4 | 2.4 | 0 |
| Safety | 3.0 | 3.0 | 0 |
| **Total** | **15.7** | **16.1** | **+0.4** |
```

### Step 5: Analyze Regressions

If any dimension drops:

```text
## Regression Analysis

**Dimension:** [Affected dimension]
**Previous:** [Score]
**Current:** [Score]
**Delta:** [-X.X]

**Affected Tasks:**
- Task X: [What failed]
- Task Y: [What degraded]

**Root Cause:** [Analysis]

**Fix Required:** [Yes/No]
**Proposed Fix:** [Description]
```

### Step 6: Decision Gate

| Outcome | Criteria | Action |
|---------|----------|--------|
| PASS | No regressions, improvements made | Approve change |
| CONDITIONAL | Minor regressions, major improvements | Review and decide |
| FAIL | Significant regressions | Rollback or fix |

### Step 7: Log Results

Update the regression log with full results.

---

## Regression Log Format

### Header

```text
# Regression Log: [Agent Name]

**Agent:** [Name]
**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD
**Baseline Version:** v1.0
**Current Version:** v1.X
```

### Entry Format

```text
## Version v1.X (YYYY-MM-DD)

**Change:** [Description of change]
**Trigger:** [Prompt / Tool / Knowledge / Model / Bug fix]

### Scores

| Task | Prev | Curr | Delta | Notes |
|------|------|------|-------|-------|
| 1 | 16 | 17 | +1 | Improved accuracy |
| 2 | 15 | 15 | 0 | Stable |
| ... | ... | ... | ... | ... |
| **Avg** | **15.2** | **15.8** | **+0.6** | |

### Refusals

| Case | Prev | Curr | Notes |
|------|------|------|-------|
| A | PASS | PASS | |
| B | PASS | PASS | |
| C | PASS | PASS | |
| D | PASS | PASS | |
| E | PASS | PASS | |

### Decision

**Status:** [PASS / CONDITIONAL / FAIL]
**Action:** [Approved / Rolled back / Fixed in v1.Y]
**Notes:** [Additional context]
```

---

## Quick Regression Check

For minor changes, run abbreviated check:

### Smoke Test (3 Tasks)

| # | Task | Purpose |
|---|------|---------|
| 1 | Task 1 (Core) | Primary function works |
| 2 | Task 4 (Constraints) | Limits respected |
| 3 | Task 10 (Trade-offs) | Judgment intact |

### Quick Refusal Check (2 Cases)

| # | Case | Purpose |
|---|------|---------|
| 1 | Case A (Out-of-scope) | Boundary detection |
| 2 | Case D (Unsafe) | Safety refusal |

### Quick Check Criteria

| Result | Criteria | Action |
|--------|----------|--------|
| PASS | All 5 checks pass | Approve |
| REVIEW | 1 check fails | Full re-run |
| FAIL | 2+ checks fail | Block change |

---

## Baseline Management

### Establishing Baseline

Run full suite on stable version:

```text
## Baseline: v1.0

**Date:** YYYY-MM-DD
**Model:** [Model version]
**Configuration:** [Relevant settings]

### Scores

| Task | Score | Notes |
|------|-------|-------|
| 1 | 16/18 | Strong on accuracy |
| 2 | 15/18 | Minor structure issues |
| ... | ... | ... |

### Dimension Averages

| Dimension | Average |
|-----------|---------|
| Accuracy | 2.7 |
| Relevance | 2.8 |
| Structure | 2.5 |
| Brevity | 2.4 |
| Evidence | 2.3 |
| Safety | 3.0 |
| **Overall** | **2.62** |
```

### Updating Baseline

Re-baseline when:
- Major version increment (v1.X -> v2.0)
- Model version changes
- Significant prompt redesign
- After 10+ minor versions

---

## Continuous Integration

### Automated Testing

For production agents, consider automated regression:

```text
Trigger: PR to main branch
Steps:
1. Extract prompt from PR
2. Run 15-check suite against test harness
3. Score automatically using rubric
4. Compare to baseline
5. Block merge if regression detected
```

### Test Fixtures

Maintain stable test inputs:

```text
/tests/
+ inputs/
  + task_1_input.txt
  + task_2_input.txt
  + ...
+ expected/
  + task_1_expected.json
  + ...
+ baseline.json
+ regression_log.md
```

---

## Recovery Procedures

### If Regression Detected

1. **Document** the failing tests
2. **Analyze** root cause
3. **Decide**: Fix forward or rollback
4. **If fix**: Create targeted fix, re-run affected tests
5. **If rollback**: Revert to previous version
6. **Log** decision and outcome

### Rollback Procedure

```text
1. Revert to last passing version
2. Verify with smoke test (3 tasks)
3. Update regression log with rollback
4. Investigate original change
5. Re-attempt with fixes if needed
```

### Fix-Forward Procedure

```text
1. Identify specific failure cause
2. Create minimal fix
3. Run affected tests only
4. If pass, run full suite
5. Update regression log
6. Merge fix
```
