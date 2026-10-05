# Code Quality Sampling Rubric

## Table of Contents

- [Sampling Methodology](#sampling-methodology)
- [Automated Check Mapping](#automated-check-mapping)
- [Manual Review Rubric](#manual-review-rubric)
- [Aggregation](#aggregation)
- [Limitations](#limitations)

Methodology for sampling and evaluating actual code quality from commits. Maps findings to CC-* rules from `software-clean-code-standard`.

---

## Sampling Methodology

### Selection

1. **Sample size**: Default 5 commits per person. Increase to 10 for formal assessments.
2. **Selection method**: Random sampling from non-merge commits in the analysis window.
3. **Stratification** (optional): When commit subjects are classifiable, sample proportionally from feature, fix, and refactoring categories.
4. **Exclusions**: Merge commits, automated commits (detected by bot patterns), commits with 0 file changes.

### Scope Limits

- Maximum 300 diff lines per commit (truncate larger diffs)
- Maximum 5 files for AST analysis per commit
- Skip binary files and generated files (lock files, compiled assets)

---

## Automated Check Mapping

### P0 — Critical (Security)

| Check | CC-* Rule | Detection Method | Confidence |
|-------|-----------|-----------------|------------|
| Hardcoded secrets in added lines | CC-SEC-03 | Regex: password/api_key/secret/token assignments, AWS key patterns | High |
| SQL injection via string interpolation | CC-SEC-08 | Regex: f-strings or .format() with SQL keywords | Medium |
| Unvalidated input at trust boundary | CC-SEC-01 | Heuristic: route handlers without input validation | Low |

### P1 — High (Correctness)

| Check | CC-* Rule | Detection Method | Confidence |
|-------|-----------|-----------------|------------|
| Silent failure (empty except) | CC-ERR-01 | Regex: `except.*: pass` or `except.*: ...` | High |
| Bare except clause | CC-ERR-01 | Regex: `except:` without exception type | High |
| New code without tests | CC-TST-01 | File path analysis: code files changed without test file changes | Medium |
| Missing error context | CC-ERR-02 | Heuristic: re-raise without wrapping or logging | Low |

### P2 — Medium (Maintainability)

| Check | CC-* Rule | Detection Method | Confidence |
|-------|-----------|-----------------|------------|
| Significant complexity increase | CC-FLOW-01 | AST: cyclomatic complexity delta > +5 per file | High |
| Deep nesting (> 4 levels) | CC-FLOW-01 | AST: max nesting depth analysis | High |
| Long function (> 50 lines) | CC-FUN-01 | AST: function body line count | High |
| Many parameters (> 5) | CC-FUN-03 | AST: parameter count analysis | High |
| Obvious N+1 or O(n²) pattern | CC-PERF-02 | Heuristic: nested loops with DB/API calls | Low |

### P3 — Low (Clarity)

| Check | CC-* Rule | Detection Method | Confidence |
|-------|-----------|-----------------|------------|
| Commented-out code | CC-DOC-04 | Regex: comment lines matching code patterns (def, class, import, if, for) | Medium |
| Non-descriptive names | CC-NAM-01 | Heuristic: single-letter variables outside loops, `temp`/`data`/`result` overuse | Low |
| Magic numbers/strings | CC-TYP-04 | Heuristic: repeated literal values in logic | Low |

---

## Manual Review Rubric

When automated checks are supplemented by human or LLM review, use this rubric per sampled commit:

### Commit Scope Assessment

| Rating | Criteria |
|--------|----------|
| Focused | Single purpose, touches related files only, easy to review in isolation |
| Acceptable | Primary purpose clear, minor tangential changes, reviewable |
| Unfocused | Multiple purposes mixed, unrelated file changes, hard to review |
| Sprawling | No clear purpose, touches many unrelated areas, should be split |

### Message Quality Assessment

| Rating | Criteria |
|--------|----------|
| Excellent (5/5) | Conventional format, imperative verb, explains what and why, > 30 chars |
| Good (3-4/5) | Clear subject, explains what changed, adequate length |
| Adequate (2/5) | Understandable but terse or generic |
| Poor (0-1/5) | Generic ("fix bug"), single word, or meaningless |

### Code Surface Assessment

| Rating | Criteria |
|--------|----------|
| Clean | No CC-* violations, good naming, appropriate abstractions |
| Minor issues | 1-2 P3 findings, mostly clean |
| Moderate issues | P2 findings present, maintainability concerns |
| Significant issues | P1 findings, correctness or safety gaps |
| Critical issues | P0 findings, security vulnerabilities or data-loss risks |

---

## Aggregation

Per person, aggregate sampled commit assessments into:

1. **CC-* compliance rate**: % of commits with no P0-P1 findings
2. **Most common violations**: Top 3 CC-* rule IDs by frequency
3. **Mean message quality**: Average score across samples (0-5)
4. **Mean complexity delta**: Average cyclomatic complexity change
5. **Test co-change rate**: % of samples with test file changes alongside code changes
6. **Overall quality label**: Based on finding distribution:
   - **High quality**: > 80% clean, no P0, max 1 P1
   - **Acceptable**: > 60% clean, no P0
   - **Needs improvement**: < 60% clean or any P0
   - **Concerning**: Multiple P0-P1 findings, pattern of issues

---

## Limitations

- Automated checks have varying confidence levels (noted in the mapping table). Low-confidence findings should be treated as hints, not evidence.
- AST analysis currently supports Python only. Other languages use diff-based analysis only.
- Commit-level analysis cannot detect cross-commit architectural issues or integration problems.
- Code quality sampling is a statistical estimate, not a complete audit. Sample size affects confidence.
- The rubric measures code quality at the commit level, not the overall health of the files being changed.
