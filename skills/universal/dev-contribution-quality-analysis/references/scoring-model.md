# Contribution Quality Scoring Model

## Table of Contents

- [Calibration Rules](#calibration-rules)
- [Dimension 1: Delivery Cadence (context only)](#dimension-1-delivery-cadence-context-only)
- [Dimension 2: Code Quality Signals (21 points)](#dimension-2-code-quality-signals-21-points)
- [Dimension 3: Commit Craft (15 points)](#dimension-3-commit-craft-15-points)
- [Dimension 4: Review & Collaboration (20 points)](#dimension-4-review--collaboration-20-points)
- [Dimension 5: Test & Safety Practices (10 points)](#dimension-5-test--safety-practices-10-points)
- [Dimension 6: D6 Context-Only Signal — AI Development Quality](#dimension-6-d6-context-only-signal--ai-development-quality)
- [Volume Context (not scored)](#volume-context-not-scored)
- [Tier Assignment](#tier-assignment)
- [Team Calibration](#team-calibration)

Six dimensions from git and MR/PR data. D2-D5 carry 66 nominal quality points; D1 delivery cadence and D6 AI development quality are context only. Volume signals (active days, MR throughput, merges, weighted LOC) are never scored — see [Volume Context](#volume-context-not-scored).

---

## Calibration Rules

Before interpreting scores:

1. **Personal baseline first** — trend matters more than absolute score. A developer moving from 45 to 60 is progressing well.
2. **Role adjustment** — leads/managers may need reduced expectations on D2 and increased expectations on D4. Apply `role_calibration` config overrides.
3. **Tenure adjustment** — new joiners need context for D4; do not read onboarding cadence as quality.
4. **Window size** — require at least 30 commits for the current sample contract; active days never gate eligibility. Below the sample minimum, mark the assessment as "insufficient data" and do not assign a tier.
5. **D6 is context-only** — AI development quality informs understanding but does not affect the overall tier.
6. **Unknowns are not zeroes** — an unmeasured sub-signal scores nothing and is removed from the achievable maximum; it never gets neutral or imputed credit. A dimension with no measured sub-signal is `insufficient evidence` and is left out of the tier.
7. **Uncertainty before comparison** — person-level rates (self-merge, small-PR share, test ratio, churn) on fewer than ~30 changes are wide. Report a 95% interval (Wilson for proportions; the script emits `*_ci95`). Never call two people different, or name anyone an outlier, unless their intervals separate; otherwise write "no detectable difference".
8. **Attribute at PR level** — in squash-merge repos the merger or squasher owns the commit. Parse `Co-authored-by` trailers and map commits to PR authors before scoring D3. Pairing, mentoring and incident work are invisible in git, so state that gap; seniors and reviewers are usually under-credited otherwise.

---

## Dimension 1: Delivery Cadence (context only)

Weekly commit counts, coefficient of variation, active days, MR throughput, and within-window trend describe when recorded work occurred. They cannot establish quality or individual effort and earn no points. Do not interpret a gap as poor performance; pairing, reviews, incidents, leave, and squash-merge practice change the pattern.

**Data source**: raw-commits.csv for cadence and mr-acceptances.csv for authored MR counts. The output keeps `scores.d1` as a context-only entry for caller compatibility (`score: null`, `max: 0`).

---

## Dimension 2: Code Quality Signals (21 points)

Measures the durability and quality of contributed code.

| Sub-Signal | Points | How to Measure | Threshold |
|---|---|---|---|
| Code churn rate | 0-8 | % of own `code_loc` rewritten within 14 days (same file, any author; see [Churn Calculation](#churn-calculation)), capped at 100%. < 8% = 8pts, < 15% = 5pts, < 25% = 2pts, >= 25% = 0pts | GitClear 2024 average: 5.7% overall |
| Duplication ratio | 0-5 | Duplicate/cloned blocks as % of total additions. < 5% = 5pts, < 10% = 3pts, < 15% = 1pt | GitClear 2024: 12.3% average |
| Refactoring ratio | 0-5 | Moved/renamed lines vs. net-new additions. > 15% = 5pts, > 8% = 3pts, > 3% = 1pt | GitClear 2024: 9.5% (down from 24.1%) |
| CC-* rule compliance | 0-3 | Proportion of sampled commits passing CC-ERR, CC-SEC, CC-TST checks. > 80% = 3pts, > 60% = 2pts, > 40% = 1pt | Tier 2: requires code sampling |

**Data source**: per-file numstat or repo checkout (churn, duplication, refactoring, CC-* sampling). The aggregate raw-commits.csv has no file paths, so from CSV alone these are `insufficient evidence`, never estimated. The commit-subject keyword share is reported as context only; it is not the refactoring ratio.

### Code-Only LOC

Every D2 sub-signal that references "lines" or "additions" is computed against `code_loc`, not raw `net_loc`. `code_loc` excludes `.json`, `.yaml`, `.yml`, `.toml`, `.md`, `.rst`, `.txt`, `.csv`, lockfiles, snapshots, generated paths, and editor metadata. Test files are tagged `test_loc` so churn and duplication ratios can separate test from product code.

Bucket rules used by the extraction CSV and `compute-code-rating.py`:

| Bucket | Include |
|---|---|
| Code | source extensions (`.py .js .ts .go .rs .java .swift .sql .css .sh` and similar) outside test paths |
| Test | `/test/`, `/tests/`, `/spec/`, `/__tests__/`, `*_test.*`, `*.test.*`, `*.spec.*` |
| Config | `.json .yaml .yml .toml .ini .xml .env`, `Dockerfile`, IaC (`.tf` and similar) |
| Docs | `.md .mdx .rst .txt .adoc` |
| Other | lockfiles, snapshots, minified, generated, vendored, binary, data files |

### Complexity-Weighted Volume (context only)

A volume / activity measure, not a quality score and not a rating of the person. It is computed by `compute-code-rating.py` and reported beside the profile, never inside D2-D5 or the tier. It multiplies code lines by a per-file complexity factor before banding:

```text
weighted_code_lines = Σ over touched code files:
    net_code_lines(file) × (1 + α · max(0, ΔCC(file)) + β · novelty(file))
```

with `α ≈ 0.05`, `β ≈ 1.0`, `ΔCC` capped at +20, `novelty ∈ {0, 0.25, 0.5}`. Aggregate per person over the window and band against the team median: V1 (≥1.5×), V2 (0.7–1.5×), V3 (0.3–0.7×), V4 (<0.3×). The V-prefix exists so the bands cannot be read as A-D quality tiers. Output is alphabetical, never sorted by volume.

Refactors that *lower* complexity keep credit (ΔCC is floored at zero, not negative). Mega-commits where one commit contains > 30% of window `code_loc` fall back to manual review — the band is non-robust under squash-merge until the diff is split.

### Churn Calculation

Churn = `code_loc` lines in file F authored by person P at commit C1 that are modified or deleted by anyone in a commit C2 where C2.date - C1.date <= 14 days. Expressed as a percentage of `code_loc` authored by P in the window, capped at 100%. (This is the one churn definition; "same-author" was an earlier inconsistent variant.)

This requires line history per file (blame or per-file diffs from a checkout). When only the aggregate CSV is available, churn is `insufficient evidence`. Do not approximate it by pairing commit totals within a repo: that proxy grows with the number of commits, so it penalises small-commit discipline and can exceed 100%.

**Pre-filter before computing churn.** The ingest layer must:

1. Dedupe `(repo, commit_hash)` rows to neutralize multi-root / submodule scans that would otherwise double-count the same commit.
2. Detect `Revert "X"` + original pairs in the same repo whose ins/del are the inverse (prior.ins == revert.del and prior.del == revert.ins) and mark both with `net_cancel=True`.

Cancelled commits are excluded from `total_insertions`, `total_deletions`, `net_lines`, and 14-day churn. They remain visible in the raw commit stream for audit, but their self-cancelling churn must not drive a D2 deduction — treat them as a data-quality artefact, not a quality signal.

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
| Review participation rate | 0-7 | Review events (approvals, comments, requested changes) on others' MRs per week, from the forge API. >= 2/week = 7pts, >= 1/week = 5pts, >= 0.5/week = 3pts, < 0.5 = 0pts | Role-adjusted: leads expected higher. Merges are not reviews |
| Review responsiveness | 0-5 | Median time between MR creation and first review action. < 2h = 5pts, < 4h = 3pts, < 24h = 1pt | Tier 2: requires API data or timestamps |
| Review depth proxy | 0-4 | Average comments per MR reviewed (when API data available). > 3 = 4pts, > 1 = 2pts, else 0pts | Tier 2: requires API data |
| Cross-repo contribution | 0-4 | Distinct repos with meaningful commits (>= 5 commits each). >= 3 repos = 4pts, 2 repos = 2pts, 1 repo = 1pt | From raw-commits.csv repo column |

**Data source**: forge API review events (participation, responsiveness, depth), raw-commits.csv (cross-repo)

### Graceful Degradation

Merge events are not review: merge queues and bots zero them, and maintainers inflate them. When review events are unavailable, the three review sub-signals are `insufficient evidence` and D4 scores only cross-repo contribution (max 4/20). Merges of others' MRs are shown as volume context. The report must note this limitation.

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

> D6 carries no point allocation and is excluded from tier assignment. D1 is also context only; total scored points = 66 nominal (D2-D5).

Measures the quality outcomes of AI-assisted development. These signals are **annotations only** — they do not contribute to the scored total or tier calculation.

| Sub-Signal | Annotation | How to Measure | Threshold |
|---|---|---|---|
| AI code survival rate | qualitative | % of AI-attributed lines surviving 30 days without rewrite. > 90% = Strong, > 75% = Good, > 60% = Fair | Requires AI attribution data |
| AI-assisted quality parity | qualitative | Whether AI-tagged commits match or exceed D2-D3 scores of human-only commits. Parity or better = Strong, within 10% = Good, significantly worse = Weak | Cross-reference AI tags with quality |
| Verification burden | qualitative | 14-day churn on AI-flagged commits vs. personal baseline. <= baseline = Strong, <= 1.5x = Moderate, > 1.5x = High | Churn rate segmented by AI flag |

**Data source**: AI attribution tags (Agent Blame, Git AI, or manual tagging), raw-commits.csv (churn segmentation)

### When AI Attribution is Unavailable

If no AI attribution data exists, D6 is reported as "not available" with no annotation. The overall tier is computed from measured D2-D5 evidence only.

### Who Sees D6

D6 follows the individual-data policy owned by `dev-ai-coding-metrics` ([Individual-Data Policy](../../dev-ai-coding-metrics/SKILL.md#individual-data-policy)): the person sees it first, it is never shown to managers, and it never feeds promotion or performance decisions.

---

## Volume Context (not scored)

Active-days coverage, MR throughput, merges of others' MRs, `code_loc` and the complexity-weighted volume band are activity context. They appear in the profile's `volume_context` block and never in D2-D5 or the tier. Never rank or tier people by commits, LOC, PR counts or presence; if volume is shown at all, normalize it per role and label it context.

---

## Tier Assignment

The tier is the share of the **measured** maximum (unmeasured sub-signals and dimensions are excluded and listed):

| Tier | Share of measured D2-D5 maximum | Label |
|---|---|---|
| A | >= 80% | Exemplary |
| B | 60-79% | Solid |
| C | 40-59% | Developing |
| D | < 40% | Concerning |

Below the data minimum, no tier is assigned (`tier: null`).

> D6 is a context-only annotation and is never included in tier calculation.

### Tier Override Rules

- If any measured dimension scores 0, the overall tier cannot be A (regardless of total)
- If D2 (Code Quality) is unmeasured, or fully measured and below 8/21, the tier cannot be A
- If D4 (Review & Collaboration) scores 0 and role expects review participation, drop one tier
- Trend direction (improving vs. declining) should be noted alongside the tier

---

## Team Calibration

When running in team mode, the scoring model produces:

1. **Per-person scores** across all 6 dimensions
2. **Team medians** for each dimension (the team baseline)
3. **Tier distribution** — count of A/B/C/D across the team
4. **Dimension heatmap** — which dimensions are strongest/weakest across the team

People are listed alphabetically, not ranked. Team calibration highlights:
- Dimension gaps (team median below industry benchmark)
- Individual differences only where the rate intervals separate (Calibration Rule 7); otherwise "no detectable difference"
