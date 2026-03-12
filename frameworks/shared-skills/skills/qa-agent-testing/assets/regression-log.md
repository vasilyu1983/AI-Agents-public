# Regression Log

Version history and test results for an agent.

## Contents

- Log header
- Version history
- Compact log format
- Score trend chart
- Failure archive
- Baseline comparison
- Re-baseline triggers
- Quick reference

---

## Log Header

```text
# Regression Log: [Agent Name]

**Agent:** [Name]
**Purpose:** [Brief description]
**Created:** YYYY-MM-DD
**Baseline Version:** v1.0
**Current Version:** v1.X
**Last Tested:** YYYY-MM-DD
```

---

## Version History

### v1.0 - Baseline (YYYY-MM-DD)

**Status:** BASELINE

**Configuration:**
- Model: [Model version]
- Prompt: [Character count]
- Tools: [List if any]
- Knowledge: [Summary]

**Scores:**

| Task | Score | Notes |
|------|-------|-------|
| 1 | /18 | |
| 2 | /18 | |
| 3 | /18 | |
| 4 | /18 | |
| 5 | /18 | |
| 6 | /18 | |
| 7 | /18 | |
| 8 | /18 | |
| 9 | /18 | |
| 10 | /18 | |
| **Avg** | **/18** | |

**Refusals:** A: P/F | B: P/F | C: P/F | D: P/F | E: P/F

**Dimension Averages:**

| Dimension | Average |
|-----------|---------|
| Accuracy | /3.0 |
| Relevance | /3.0 |
| Structure | /3.0 |
| Brevity | /3.0 |
| Evidence | /3.0 |
| Safety | /3.0 |

---

### v1.1 (YYYY-MM-DD)

**Change:** [Description of what changed]

**Type:** Prompt / Tool / Knowledge / Bug fix

**Reason:** [Why the change was made]

**Scores:**

| Metric | Previous | Current | Delta |
|--------|----------|---------|-------|
| Task Avg | /18 | /18 | |
| Accuracy | /3.0 | /3.0 | |
| Relevance | /3.0 | /3.0 | |
| Structure | /3.0 | /3.0 | |
| Brevity | /3.0 | /3.0 | |
| Evidence | /3.0 | /3.0 | |
| Safety | /3.0 | /3.0 | |

**Refusals:** A: P/F | B: P/F | C: P/F | D: P/F | E: P/F

**Regressions:** [None / List any degraded tests]

**Status:** PASS / CONDITIONAL / FAIL

**Action:** Approved / Rolled back / Fixed in v1.2

---

### v1.2 (YYYY-MM-DD)

[Continue pattern for each version...]

---

## Compact Log Format

For quick reference:

```text
| Ver | Date | Change | Avg | Status | Notes |
|-----|------|--------|-----|--------|-------|
| 1.0 | YYYY-MM-DD | Baseline | 15.2 | BASE | Initial |
| 1.1 | YYYY-MM-DD | Added tool X | 15.5 | PASS | +0.3 |
| 1.2 | YYYY-MM-DD | Fixed Task 3 | 15.8 | PASS | +0.3 |
| 1.3 | YYYY-MM-DD | Prompt rewrite | 14.1 | FAIL | -1.7, rolled back |
| 1.4 | YYYY-MM-DD | Careful rewrite | 16.0 | PASS | +0.2 from 1.2 |
```

---

## Score Trend Chart

Track score progression:

```text
Version   Score   Visual
v1.0      15.2    ##################..
v1.1      15.5    ###################.
v1.2      15.8    ####################
v1.3      14.1    ##############...... [ROLLED BACK]
v1.4      16.0    ####################

Legend: # = filled, . = empty
Scale: 0-20
```

---

## Failure Archive

Document significant failures for learning:

### Failure: v1.3 Prompt Rewrite

**Date:** YYYY-MM-DD

**What happened:** Attempted major prompt rewrite, caused regression.

**Tasks affected:**
- Task 5: Dropped from 16 to 12 (reasoning quality)
- Task 8: Dropped from 15 to 11 (structured output)

**Root cause:** Removed examples that guided output format.

**Fix applied:** Rolled back to v1.2, then incrementally updated in v1.4.

**Lesson learned:** Keep format examples even when simplifying prompt.

---

## Baseline Comparison

Compare current to baseline:

| Metric | Baseline (v1.0) | Current (v1.X) | Total Change |
|--------|-----------------|----------------|--------------|
| Task Avg | /18 | /18 | |
| Accuracy | /3.0 | /3.0 | |
| Relevance | /3.0 | /3.0 | |
| Structure | /3.0 | /3.0 | |
| Brevity | /3.0 | /3.0 | |
| Evidence | /3.0 | /3.0 | |
| Safety | /3.0 | /3.0 | |

**Overall trajectory:** Improving / Stable / Degrading

---

## Re-Baseline Triggers

Document when baseline was updated:

| Date | Old Baseline | New Baseline | Reason |
|------|--------------|--------------|--------|
| YYYY-MM-DD | v1.0 | v2.0 | Major version increment |
| YYYY-MM-DD | v2.0 | v3.0 | Model change |

---

## Quick Reference

```text
Agent: [Name]
Current: v1.X
Baseline: v1.0
Last Test: YYYY-MM-DD
Status: [PASS at X.X avg]

Recent Changes:
- v1.X: [Change] -> [Result]
- v1.Y: [Change] -> [Result]

Next Review: YYYY-MM-DD
```
