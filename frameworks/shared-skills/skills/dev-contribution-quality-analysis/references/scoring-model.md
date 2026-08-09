# Contribution Quality Scoring Model

## Table of Contents

- [Calibration Rules](#calibration-rules)
- [Dimension 1: Delivery Consistency (20 points)](#dimension-1-delivery-consistency-20-points)
- [Dimension 2: Code Quality Signals (25 points)](#dimension-2-code-quality-signals-25-points)
- [Dimension 3: Commit Craft (15 points)](#dimension-3-commit-craft-15-points)
- [Dimension 4: Review & Collaboration (20 points)](#dimension-4-review--collaboration-20-points)
- [Dimension 5: Test & Safety Practices (10 points)](#dimension-5-test--safety-practices-10-points)
- [Dimension 6: D6 Context-Only Signal — AI Development Quality](#dimension-6-d6-context-only-signal--ai-development-quality)
- [Tier Assignment](#tier-assignment)
- [Team Calibration](#team-calibration)

Six dimensions measuring contribution quality from git and MR/PR data. Higher scores are better. Total: 90 points across D1-D5 (scored). D6 carries no points and does not affect tier assignment; it is a separate annotation that provides context on AI-assisted development quality.

---

## Calibration Rules

Before interpreting scores:

1. **Personal baseline first** — trend matters more than absolute score. A developer moving from 45 to 60 is progressing well.
2. **Role adjustment** — leads/managers get reduced expectations on D1-D2, increased expectations on D4. Apply `role_calibration` config overrides.
3. **Tenure adjustment** — new joiners (< 3 months) get grace period on D1 and D4. Ramp-up patterns are normal.
4. **Window size** — minimum 30 commits and 20 active days. Below this, mark the assessment as "insufficient data" and do not assign a tier.
5. **D6 is context-only** — AI development quality informs understanding but does not affect the overall tier.

---

## Dimension 1: Delivery Consistency (20 points)

Measures whether the person delivers work steadily over time.

| Sub-Signal | Points | How to Measure | Threshold |
|---|---|---|---|
| Commit frequency stability | 0-7 | Coefficient of variation (CV) of weekly commit counts. CV < 0.5 = 7pts, < 0.8 = 5pts, < 1.2 = 3pts, >= 1.2 = 0pts | Lower CV = more consistent |
| Active days coverage | 0-5 | % of expected working days with >= 1 meaningful commit. > 70% = 5pts, > 50% = 3pts, > 30% = 1pt | Role-adjusted expected days |
| MR throughput | 0-5 | MRs merged per week vs. role-calibrated baseline. >= baseline = 5pts, >= 0.7x = 3pts, >= 0.4x = 1pt | Default baseline: 2 MRs/week for IC |
| Delivery trend | 0-3 | Linear regression slope over the window. Positive/flat = 3pts, slight decline = 1pt, significant decline = 0pts | Compare first half to second half |

**Data source**: raw-commits.csv (commit frequency, active days), mr-acceptances.csv (MR throughput)

---

## Dimension 2: Code Quality Signals (25 points)

Measures the durability and quality of contributed code.

| Sub-Signal | Points | How to Measure | Threshold |
|---|---|---|---|
| Code churn rate | 0-8 | % of own lines rewritten within 14 days (same-file, same-author). < 8% = 8pts, < 15% = 5pts, < 25% = 2pts, >= 25% = 0pts | GitClear 2024 average: 5.7% overall |
| Duplication ratio | 0-5 | Duplicate/cloned blocks as % of total additions. < 5% = 5pts, < 10% = 3pts, < 15% = 1pt | GitClear 2024: 12.3% average |
| Refactoring ratio | 0-5 | Moved/renamed lines vs. net-new additions. > 15% = 5pts, > 8% = 3pts, > 3% = 1pt | GitClear 2024: 9.5% (down from 24.1%) |
| Complexity-weighted rating | 0-4 | `code_loc × (1 + α·ΔCC + β·novelty)` against team median (see below). ≥1.5× median or net-decreasing CC = 4pts, 0.7–1.5× = 2pts, < 0.7× and rising CC = 0pts | Tier 2: requires repo checkout or static-analysis pass |
| CC-* rule compliance | 0-3 | Proportion of sampled commits passing CC-ERR, CC-SEC, CC-TST checks. > 80% = 3pts, > 60% = 2pts, > 40% = 1pt | Tier 2: requires code sampling |

**Data source**: raw-commits.csv (churn, duplication, refactoring), repo checkout (complexity, CC-* sampling)

### Code-Only LOC

Every D2 sub-signal that references "lines" or "additions" is computed against `code_loc`, not raw `net_loc`. `code_loc` excludes `.json`, `.yaml`, `.yml`, `.toml`, `.md`, `.rst`, `.txt`, `.csv`, lockfiles, snapshots, generated paths, and editor metadata — see the project-scoped counterpart skill's `packs/example-pack/references/loc-measurement-best-practices.md` → "Code LOC" for the full include / exclude lists. Test files count as `code_loc` but are tagged `test_loc` so churn and duplication ratios can separate test from product code.

### Complexity-Weighted Rating

The D2 complexity sub-signal multiplies code lines by a per-file complexity factor before banding:

```text
weighted_code_lines = Σ over touched code files:
    net_code_lines(file) × (1 + α · max(0, ΔCC(file)) + β · novelty(file))
```

with `α ≈ 0.05`, `β ≈ 1.0`, `ΔCC` capped at +20, `novelty ∈ {0, 0.25, 0.5}`. Aggregate per person over the window, compare against team median, and assign the four-band rating used in the sub-signal table. This is the same rating defined in the project-scoped counterpart skill's `packs/example-pack/references/loc-measurement-best-practices.md` → "Complexity-Weighted Rating"; both skills must produce identical numbers from the same CSV input.

Refactors that *lower* complexity keep credit (ΔCC is floored at zero, not negative). Mega-commits where one commit contains > 30% of window `code_loc` fall back to manual review — the rating is non-robust under squash-merge until the diff is split.

### Churn Calculation

Churn = lines in file F authored by person P at commit C1 that are modified or deleted by person P (or anyone) in a commit C2 where C2.date - C1.date <= 14 days. Expressed as a percentage of total lines authored by P in the window.

This requires comparing diffs across commits touching the same files. When repo checkouts are unavailable, approximate from CSV data using insertions/deletions on the same file by the same author within the 14-day window.

**Pre-filter before computing churn.** The ingest layer must:

1. Dedupe `(repo, commit_hash)` rows to neutralize multi-root / submodule scans that would otherwise double-count the same commit.
2. Detect `Revert "X"` + original pairs in the same repo whose ins/del are the inverse (prior.ins == revert.del and prior.del == revert.ins) and mark both with `net_cancel=True`.

Cancelled commits are excluded from `total_insertions`, `total_deletions`, `net_lines`, and the 14-day churn pairing loop. They remain visible in the raw commit stream for audit, but their self-cancelling churn must not drive a D2 deduction — treat them as a data-quality artefact, not a quality signal.

---

## Dimension 3: Commit Craft (15 points)

Measures the discipline and clarity of individual contributions.

| Sub-Signal | Points | How to Measure | Threshold |
|---|---|---|---|
| Commit message quality | 0-5 | Composite: length >= 10 chars (1pt), conventional format (1pt), starts with verb (1pt), explains what/why not just how (2pts) | Manual or heuristic scoring |
| Commit scope discipline | 0-4 | Mean files per commit. <= 5 = 4pts, <= 10 = 3pts, <= 20 = 1pt, > 20 = 0pts | Google Small CLs guidance |
| PR size discipline | 0-4 | % of MRs under 250 LOC. > 70% = 4pts, > 50% = 3pts, > 30% = 1pt | Elite: < 250 LOC per PR |
| Merge hygiene | 0-2 | Self-merge rate. 0% = 2pts, < 5% = 1pt, >= 5% = 0pts | Self-merge = author is also merger |

**Data source**: raw-commits.csv (messages, file counts), mr-acceptances.csv (PR size, self-merge detection)

### Self-Merge Detection

Compare `author_name`/`author_email` from the original commits in a branch to `merger_name`/`merger_email` in mr-acceptances.csv. When they match (after identity alias resolution), it is a self-merge.

---

## Dimension 4: Review & Collaboration (20 points)

Measures participation in the team's review and collaboration workflow.

| Sub-Signal | Points | How to Measure | Threshold |
|---|---|---|---|
| Review participation rate | 0-7 | MRs merged where person is the merger but not the author, per week. >= 2/week = 7pts, >= 1/week = 5pts, >= 0.5/week = 3pts, < 0.5 = 0pts | Role-adjusted: leads expected higher |
| Review responsiveness | 0-5 | Median time between MR creation and first review action. < 2h = 5pts, < 4h = 3pts, < 24h = 1pt | Tier 2: requires API data or timestamps |
| Review depth proxy | 0-4 | Average comments per MR reviewed (when API data available). > 3 = 4pts, > 1 = 2pts, else 0pts | Tier 2: requires API data |
| Cross-repo contribution | 0-4 | Distinct repos with meaningful commits (>= 5 commits each). >= 3 repos = 4pts, 2 repos = 2pts, 1 repo = 1pt | From raw-commits.csv repo column |

**Data source**: mr-acceptances.csv (review participation, responsiveness proxy), raw-commits.csv (cross-repo)

### Graceful Degradation

When API data (review comments, exact timestamps) is unavailable, D4 scores only the sub-signals derivable from CSV data: review participation rate and cross-repo contribution. The maximum possible D4 score without API data is 11/20. The report must note this limitation.

---

## Dimension 5: Test & Safety Practices (10 points)

Measures whether contributions include appropriate testing and safety awareness.

| Sub-Signal | Points | How to Measure | Threshold |
|---|---|---|---|
| Test-to-code ratio | 0-4 | % of code-touching commits that also touch test files. > 40% = 4pts, > 25% = 3pts, > 15% = 1pt | Test files: paths containing `test`, `spec`, `__tests__` |
| Test presence in features | 0-3 | % of feature commits (non-fix, non-chore, non-merge) with test changes. > 50% = 3pts, > 30% = 2pts, > 15% = 1pt | Classify via commit subject heuristics |
| Security-sensitive file awareness | 0-3 | Commits touching auth/crypto/config paths that have corresponding test or review signals. > 80% = 3pts, > 50% = 2pts, > 30% = 1pt | Security paths: `auth`, `crypto`, `security`, `middleware`, `.env` |

**Data source**: raw-commits.csv (file paths via numstat, commit subjects)

### File Path Heuristics

Test files are identified by path patterns: `**/test/**`, `**/tests/**`, `**/spec/**`, `**/__tests__/**`, `**/*_test.*`, `**/*_spec.*`, `**/*.test.*`, `**/*.spec.*`.

Security-sensitive files are identified by directory or filename patterns: `**/auth/**`, `**/security/**`, `**/crypto/**`, `**/middleware/**`, `**/*.env*`, `**/secrets/**`.

Note: File-level path data requires `--numstat` output in the CSV extraction. The standard `extract-commits.sh` produces aggregate `files_changed,insertions,deletions` counts but not individual file paths. When file paths are unavailable, D5 uses only aggregate heuristics and the maximum score is 4/10.

---

## Dimension 6: D6 Context-Only Signal — AI Development Quality

> **Design rationale (option b):** D6 carries no point allocation and is excluded from tier assignment. The original design intent was context-only, but the earlier 10-pt label created confusion about whether D6 influenced tiers. Points removed; total scored points = 90 (D1-D5). D6 is a separate annotation appended to reports for interpretive context.

Measures the quality outcomes of AI-assisted development. These signals are **annotations only** — they do not contribute to the scored total or tier calculation.

| Sub-Signal | Annotation | How to Measure | Threshold |
|---|---|---|---|
| AI code survival rate | qualitative | % of AI-attributed lines surviving 30 days without rewrite. > 90% = Strong, > 75% = Good, > 60% = Fair | Requires AI attribution data |
| AI-assisted quality parity | qualitative | Whether AI-tagged commits match or exceed D2-D3 scores of human-only commits. Parity or better = Strong, within 10% = Good, significantly worse = Weak | Cross-reference AI tags with quality |
| Verification burden | qualitative | Rework rate on AI-heavy commits vs. personal baseline. <= baseline = Strong, <= 1.5x = Moderate, > 1.5x = High | Churn rate segmented by AI flag |

**Data source**: AI attribution tags (Agent Blame, Git AI, or manual tagging), raw-commits.csv (churn segmentation)

### When AI Attribution is Unavailable

If no AI attribution data exists, D6 is reported as "not available" with no annotation. The overall tier is always computed from D1-D5 only (90-point scale: A >= 72, B >= 54, C >= 36, D < 36).

---

## Tier Assignment

| Tier | Score Range (D1-D5, 90 pts total) | Label |
|---|---|---|
| A | 72-90 | Exemplary |
| B | 54-71 | Solid |
| C | 36-53 | Developing |
| D | 0-35 | Concerning |

> D6 is a context-only annotation and is never included in tier calculation.

### Tier Override Rules

- If any single dimension scores 0, the overall tier cannot be A (regardless of total)
- If D2 (Code Quality) scores below 8/25, the tier cannot be A
- If D4 (Review & Collaboration) scores 0 and role expects review participation, drop one tier
- Trend direction (improving vs. declining) should be noted alongside the tier

---

## Team Calibration

When running in team mode, the scoring model produces:

1. **Per-person scores** across all 6 dimensions
2. **Team medians** for each dimension (the team baseline)
3. **Relative positioning** — each person's score as % of team median
4. **Tier distribution** — count of A/B/C/D across the team
5. **Dimension heatmap** — which dimensions are strongest/weakest across the team

Team calibration highlights:
- Outliers (> 1.5x or < 0.5x team median on any dimension)
- Dimension gaps (team median below industry benchmark)
- Improvement candidates (individuals with one low dimension dragging overall score down)
