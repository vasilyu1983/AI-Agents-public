# Contribution Signals Catalog

## Table of Contents

- [Tier 1: Git-Extractable Signals](#tier-1-git-extractable-signals)
- [Tier 2: Static Analysis Signals](#tier-2-static-analysis-signals)
- [Tier 3: AI Attribution Signals](#tier-3-ai-attribution-signals)
- [Signal Dependencies and Graceful Degradation](#signal-dependencies-and-graceful-degradation)

Complete catalog of signals used in contribution quality analysis, organized by extraction tier. Each signal includes its definition, extraction method, scoring dimension, and known confounders.

---

## Tier 1: Git-Extractable Signals

These signals can be computed from `raw-commits.csv` and `mr-acceptances.csv` without access to repository checkouts or external APIs.

### Commit Frequency and Temporal Distribution

| Signal | Definition | Dimension | Extraction |
|--------|-----------|-----------|------------|
| Weekly commit count | Number of commits per ISO week | D1 | Count rows in raw-commits.csv grouped by person + ISO week |
| Commit frequency CV | Coefficient of variation of weekly counts | D1 | std(weekly_counts) / mean(weekly_counts) |
| Active days | Count of distinct dates with >= 1 commit | D1 | Count distinct date(datetime) per person |
| Active days coverage | Active days / expected working days in window | D1 | Exclude weekends and configured non_working_date_ranges |
| Burst pattern detection | Clusters of high activity separated by gaps | D1 | Identify weeks with > 2x mean followed by weeks with < 0.3x mean |
| Working hours distribution | Histogram of commit hours in local time | Context | Use person_timezone config to convert UTC offset |

**Confounders**: Vacation periods, parental leave, conference attendance. Check against `non_working_date_ranges` config before scoring gaps.

### Code Volume and Churn

| Signal | Definition | Dimension | Extraction |
|--------|-----------|-----------|------------|
| Total insertions | Sum of insertions across all commits | Context | Sum insertions column per person |
| Total deletions | Sum of deletions across all commits | Context | Sum deletions column per person |
| Net lines contributed | insertions - deletions | Context | Aggregate per person |
| Churn rate (14-day) | % of own lines modified/deleted within 14 days | D2 | Same-author commits touching same repo within 14-day window. Approximate: (deletions in re-touch commits) / (total insertions in initial commits) |
| Churn rate (30-day) | % of own lines modified/deleted within 30 days | Context | Extended window for trend comparison |

**Confounders**: Legitimate refactoring increases churn. Large feature branches may show artificial churn on merge. Filter out merge commits when calculating churn.

### Duplication and Refactoring

| Signal | Definition | Dimension | Extraction |
|--------|-----------|-----------|------------|
| Duplication ratio | Duplicate blocks as % of total additions | D2 | Tier 2 (requires repo checkout for accurate detection). Approximate from CSV: commits with very similar insertion counts touching the same files |
| Refactoring ratio | Moved/renamed lines as % of total changed lines | D2 | Proxy: commits where deletions > 60% of insertions and subject contains "refactor", "rename", "move", "extract", "reorganize" |
| Net-new code ratio | Additions that are genuinely new (not moved) | Context | 1 - refactoring_ratio (approximate) |

**Confounders**: File renames register as full-file deletion + addition in numstat. Some git configurations handle renames differently. Cross-reference with commit subjects.

### MR/PR Activity

| Signal | Definition | Dimension | Extraction |
|--------|-----------|-----------|------------|
| MR throughput | MRs merged per week (as author) | D1 | Count rows in mr-acceptances.csv where source branch author matches person |
| PR size (LOC) | insertions + deletions per MR | D3 | Sum insertions + deletions per MR commit |
| PR size distribution | Percentile breakdown of PR sizes | D3 | P50, P90 of (insertions + deletions) per MR |
| Small PR ratio | % of MRs under 250 LOC | D3 | Count(MRs < 250 LOC) / total MRs |
| Self-merge rate | % of MRs where author = merger | D3 | Compare author identity (from branch commits) to merger identity in mr-acceptances.csv after alias resolution |
| Review participation rate | MRs merged as non-author reviewer per week | D4 | Count MRs where merger != any branch commit author, per person per week |

**Confounders**: Squash-and-merge hides individual commit granularity. Some teams use auto-merge bots. Self-merge may be legitimate for approved hotfixes.

### Commit Message Quality

| Signal | Definition | Dimension | Extraction |
|--------|-----------|-----------|------------|
| Message length | Character count of subject line | D3 | len(subject) from raw-commits.csv |
| Conventional format | Matches `type(scope): description` pattern | D3 | Regex: `^(feat|fix|refactor|test|docs|chore|style|perf|ci|build)(\(.+\))?: .+` |
| Verb-first | Subject starts with an imperative verb | D3 | Check first word against verb list |
| What/why presence | Subject explains what changed and why, not just how | D3 | Heuristic: length > 30 chars AND not generic ("update", "fix bug", "changes") |
| Generic message ratio | % of commits with low-information subjects | D3 | Match against: "update", "fix", "changes", "wip", "temp", "misc", "stuff", single-word subjects |

**Confounders**: Some teams use issue-tracker IDs in commit messages (e.g., "PROJ-1234"), which are short but reference detailed context. Check for ticket ID patterns before penalizing short messages.

### Cross-Repository Activity

| Signal | Definition | Dimension | Extraction |
|--------|-----------|-----------|------------|
| Distinct repos | Number of repos with >= 5 commits | D4 | Count distinct repo values per person |
| Repo concentration | % of commits in primary repo | Context | max(repo_count) / total_commits per person |
| Cross-team contribution | Repos outside person's primary team area | Context | Requires team-to-repo mapping in config |

---

## Tier 2: Static Analysis Signals

These signals require access to actual repository checkouts for file-level analysis.

### Complexity Metrics

| Signal | Definition | Dimension | Extraction |
|--------|-----------|-----------|------------|
| Cyclomatic complexity delta | Net change in cyclomatic complexity per commit | D2 | Parse AST before/after for modified files. Currently supported: Python (ast module) |
| Cognitive complexity delta | Net change in cognitive complexity per commit | D2 | Weight nested structures more heavily. SonarSource methodology |
| Function length delta | Net change in average function/method line count | D2 | AST analysis on modified functions |
| Max nesting depth | Deepest nesting level in modified code | D2 | AST walk tracking depth |

**Confounders**: Large files have high absolute complexity that a single commit may not have caused. Always measure delta, not absolute. Compare to file's historical complexity.

### Test Coverage Signals

| Signal | Definition | Dimension | Extraction |
|--------|-----------|-----------|------------|
| Test-to-code ratio | % of code-touching commits that also modify test files | D5 | Match file paths against test patterns |
| Test presence in features | % of feature commits with test changes | D5 | Classify commits by subject (feat/fix/chore) then check for test file changes |
| New test file creation | Whether new feature files have corresponding new test files | D5 | Compare created file paths to test path conventions |

**File path patterns for test detection**:
- `**/test/**`, `**/tests/**`, `**/spec/**`, `**/__tests__/**`
- `**/*_test.*`, `**/*_spec.*`, `**/*.test.*`, `**/*.spec.*`
- `**/test_*.*`

### Security-Sensitive File Detection

| Signal | Definition | Dimension | Extraction |
|--------|-----------|-----------|------------|
| Security file touch rate | % of security-sensitive file changes with review signals | D5 | Identify changes to auth/crypto/middleware paths and check for review in MR data |
| Config file change rate | Frequency of changes to configuration and environment files | Context | Match against config path patterns |

**Security-sensitive path patterns**:
- `**/auth/**`, `**/security/**`, `**/crypto/**`, `**/middleware/**`
- `**/*.env*`, `**/secrets/**`, `**/credentials/**`
- `**/jwt/**`, `**/oauth/**`, `**/saml/**`

### CC-* Rule Compliance (Code Sampling)

| Signal | Definition | Dimension | Extraction |
|--------|-----------|-----------|------------|
| CC-* compliance rate | % of sampled commits without P0-P1 findings | D2 | Run sample-code-quality.py on N random commits per person |
| Most common violations | Top 3 CC-* rule IDs violated | Context | Aggregate findings across sampled commits |
| Security rule compliance | % of samples passing CC-SEC-01 through CC-SEC-08 | D2 | Focused check on security-related rules |

See `references/code-quality-sampling-rubric.md` for the full sampling methodology and CC-* rule mapping.

---

## Tier 3: AI Attribution Signals

These signals require AI attribution tooling (Agent Blame, Git AI, Agent Trace, or manual tagging). They are always context-only and do not affect the quality tier.

### Attribution Metrics

| Signal | Definition | Dimension | Extraction |
|--------|-----------|-----------|------------|
| AI authorship ratio | % of commits flagged as AI-assisted | D6 | From AI attribution metadata (git notes, Agent Trace JSON) |
| AI code survival rate (30-day) | % of AI-attributed lines surviving 30 days without rewrite | D6 | Cross-reference AI attribution with churn analysis |
| AI quality parity | D2-D3 scores for AI-tagged vs. human-only commits | D6 | Segment quality scores by AI flag |
| AI verification burden | Churn rate on AI-heavy commits vs. personal baseline | D6 | Compare churn rates segmented by AI attribution |

### Detection Heuristics (When No Attribution Tooling)

| Signal | Definition | Confidence | Extraction |
|--------|-----------|------------|------------|
| Commit message fingerprint | Multiline ratio, conventional commit adherence | Low | Statistical: AI agents have distinctive commit message patterns (multiline ratio 44.7% importance per arxiv 2601.17406) |
| Change concentration | Files modified per commit vs. directory depth | Low | High change concentration + deep directory traversal suggests AI agent |
| Comment density anomaly | Unusually high inline comment density | Low | Claude Code signature: 19.8% comment density vs. human baseline |

**Important**: These heuristics have high false-positive rates. They should inform investigation, never be used as evidence. See `references/ai-attribution-patterns.md` for full methodology.

---

## Signal Dependencies and Graceful Degradation

| Available Data | Tier 1 Signals | Tier 2 Signals | Max Possible Score |
|---|---|---|---|
| CSV only (no repo checkout) | All | None | ~70/90 (D1-D5 without repo-dependent sub-signals) |
| CSV + repo checkout | All | Complexity, test paths, CC-* sampling | 90/90 (full D1-D5) |
| CSV + repo + AI attribution | All | All | 100/100 (D1-D6) |
| CSV + API data (review comments) | All Tier 1 + D4 review depth | None | ~80/90 |

The report MUST note which tiers of data were available and which sub-signals could not be computed. Never present a partial score as if it were a complete assessment.
