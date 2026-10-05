---
name: dev-contribution-quality-analysis
description: "Scores team or opt-in individual contribution quality from commit and PR history. Use when building engineering scorecards or coaching; for AI impact use dev-ai-coding-metrics."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-07-11
---

# Developer Contribution Quality Analysis

Multi-dimensional analysis of code contribution quality from git data. Produces team calibration comparisons and, under the individual-data policy below, opt-in person reports.

## Quick Reference

| Task | Tool / Reference | Command / Path | When |
|------|-----------------|----------------|------|
| Extract contribution profiles | `extract-contribution-profile.py` | `python scripts/extract-contribution-profile.py --config config.json` | First step after CSV extraction |
| Sample code quality | `sample-code-quality.py` | `python scripts/sample-code-quality.py --config config.json` | When repo checkouts available |
| Generate quality report | `generate-quality-report.py` | `python scripts/generate-quality-report.py --config config.json --mode person` | After profile extraction |
| Understand scoring model | `scoring-model.md` | `references/scoring-model.md` | Before interpreting results |
| Map findings to CC-* rules | `code-quality-sampling-rubric.md` | `references/code-quality-sampling-rubric.md` | During code sampling |
| Calibrate against industry | `industry-benchmarks.md` | `references/industry-benchmarks.md` | When comparing to external norms |

## When to Use This Skill

- Engineering managers assessing individual contribution patterns
- Tech leads reviewing code quality trends across a team
- CTOs building engineering scorecards
- Calibrating what "good" looks like for a role across a team (calibration and coaching, not ranking)
- Opt-in self-review or coaching for one person
- Identifying skill gaps or coaching targets

## When NOT to Use This Skill

- Governed multi-signal review prioritization -> the project-scoped counterpart skill
- Defining code quality rules -> `software-clean-code-standard`
- AI coding tool impact, ROI, or adoption tracking -> `dev-ai-coding-metrics`
- Repository-level code health (not person-level) -> `qa-refactoring`
- General code review workflow -> `software-code-review`

## Defaults

- Measure contribution quality through outcomes (churn, duplication, test coverage), not presence or working hours
- Never rank or tier people by commits, LOC or PR counts; volume is context, normalized per role, never a quality score
- Person-level data follows the one [Individual-Data Policy](../dev-ai-coding-metrics/SKILL.md#individual-data-policy): team level by default; person-level output only as opt-in self-review or coaching, shown to the person first, with sampled evidence and a correction path; D6 AI annotations are never shown to managers
- Before calling two people different, compare uncertainty intervals (Wilson for rates); if they overlap, report "no detectable difference"
- Attribute at PR level: parse `Co-authored-by`, account for squash merges, and name pairing, mentoring and incident work as invisible in git
- Quality is multi-dimensional; no single number replaces the 6-dimension profile
- Compare against personal baseline first, then team, then industry
- AI-assisted code is normal and quality-neutral; score the output, not the authorship. Treat commits and PRs authored end-to-end by an autonomous coding agent as a distinct evidence class (see Known Traps)
- For external calibration figures, use the dated citations in `references/industry-benchmarks.md` and name the source year
- Git data is necessary but not sufficient; always note what evidence is missing
- CC-* rules from `software-clean-code-standard` are the code quality rubric
- Minimum sample for a tier: 30 commits in the analysis window; active days are context, not eligibility or quality
- Scripts consume the same CSV format as the project-scoped counterpart skill extraction
- Ingest dedupes on `(repo, commit_hash)` and cancels `Revert "X"` + original pairs (both flagged `net_cancel`) so churn-rate and net_lines do not double-count multi-root scans or self-reverting churn
- Code volume is measured as `code_loc` (extension-filtered: drops `.json`, `.yaml`, `.md`, snapshots, generated paths). Raw `net_loc` and `churn_loc` are kept for context only.
- `compute-code-rating.py` reports a complexity-weighted volume band (V1-V4 against the team median, alphabetical). It is activity context shown beside the profile, never part of D1-D5 or the tier, and it has no role calibration: read it against each person's role.
- Unmeasured signals are unknowns, not zeroes: they score nothing, leave the achievable maximum, and are listed. Below the data minimum there is no tier.

## Workflow

1. **Define the question** — quality audit, growth tracking, team calibration, or opt-in coaching
2. **Set scope** — person(s), time window, repo roots
3. **Extract git + MR data** — use the project-scoped counterpart skill extraction scripts or provide CSVs in the same format
4. **Run contribution profile analysis** — `extract-contribution-profile.py` computes all Tier 1 signals
5. **Run code quality sampling** (optional) — `sample-code-quality.py` maps sampled commits to CC-* rules
6. **Generate quality report** — `generate-quality-report.py` in `person` or `team` mode
7. **Present findings** with explicit limitations and calibration context

## Decision Tree: Assessment Type

```text
What is the assessment goal?
├── Individual quality audit?
│   ├── Point-in-time snapshot → person quality report
│   └── Trend over time → person trend report (multiple windows)
├── Team quality comparison?
│   ├── Role-expectation calibration (no ranking) → team calibration report
│   └── Quality trend monitoring → team trend report
└── AI-tool impact assessment?
    └── Route to dev-ai-coding-metrics (team-level study design and ROI)
```

## Scoring Model (Summary)

Six dimensions, 66 nominal points across D2-D5. D1 and D6 are context only. See `references/scoring-model.md` for full detail.

| # | Dimension | Weight | Primary Signals |
|---|-----------|--------|-----------------|
| D1 | Delivery cadence context | — | Weekly commit pattern and trend; never scored |
| D2 | Code Quality Signals | 21 | Churn rate (14d), duplication, refactoring ratio, CC-* compliance |
| D3 | Commit Craft | 15 | Message quality, scope discipline, PR size, self-merge rate |
| D4 | Review & Collaboration | 20 | Review participation (forge review events, not merges), responsiveness, depth, cross-repo contribution |
| D5 | Test & Safety Practices | 10 | Test-to-code ratio, test presence in features, security-file awareness |
| D6 | AI Development Quality context | — | Annotation only: AI code survival, quality parity, verification burden |

**Quality Tiers (share of the measured D2-D5 maximum)**: A (≥80% Exemplary), B (60-79% Solid), C (40-59% Developing), D (<40% Concerning). No tier below the sample minimum; A is blocked while D2 is unmeasured.

D1 and D6 carry no points and are excluded from tier assignment. Volume (active days, MR throughput, merges, weighted LOC) is context only. See `references/scoring-model.md` for rationale.

### Evidence sufficiency and abstention

Score a dimension only when its evidence window, eligible contribution count, review coverage, and provenance coverage are stated. Missing review comments, incident links, or AI provenance are unknowns, not zeroes. Report confidence per dimension because test evidence may be strong while maintainability or production-outcome evidence is sparse.

If the sampled work is too small, dominated by one incident or generated migration, or cannot be joined reliably to review and outcome data, return `insufficient evidence` for the affected dimension and show what additional sample would resolve it. Do not roll an unknown dimension into a composite score, and do not give it neutral credit. Any person-level report must include the sampled items and an appeal/correction path so mistaken attribution can be fixed before the result informs coaching or staffing decisions.

## Output Modes

- **Person quality report** — individual deep-dive with 6-dimension breakdown, sampled commit quality, CC-* findings
- **Team calibration report** — alphabetical comparison matrix, tier distribution, team strengths/gaps; no ranking
- **Quality scorecard** — one-page quick reference for presentations
- **Machine-readable JSON** — contribution-profiles.json for dashboards and downstream tools

## Known Traps

- Treating commit frequency or online presence as contribution quality when the actual question is code-health and delivery outcomes.
- Comparing developers across very different repo types, support load, or code ownership without first calibrating those constraints.
- Interpreting AI-heavy contribution patterns as automatically higher or lower quality without reviewing churn, survival, and verification burden.
- Building a score from sparse data windows that do not meet the minimum threshold for stable signal extraction.
- Sampling code quality from convenience commits instead of representative work, which biases the conclusions toward visible or recent changes.
- Scoring a PR that was generated end-to-end by an autonomous coding agent (Devin, Codex cloud tasks, Claude Code background/delegated sessions) as if it reflects the human's craft. When a repo's provenance data shows fully agent-authored diffs merged under a human identity, D3 (Commit Craft) and D2 code-surface signals measure the agent's output and the human's review/orchestration judgment, not their hand-written code quality — say so explicitly in the report and do not fold it into an unqualified craft score.
- Letting a rising headline number go unquestioned when the underlying behavior could be gamed: churn can be suppressed by avoiding risky files instead of writing more durable code; PR-size discipline can be gamed by artificially splitting one change into many trivial PRs; test-to-code ratio can be inflated with low-value snapshot or no-op tests. Cross-check any single improving metric against at least one adjacent signal before crediting it.

## Common Anti-Patterns

- Turning a multi-dimensional quality model into a hidden ranking engine and pretending the composite number is objective truth.
- Using the analysis for attendance policing or concurrent-employment inference when the skill is supposed to measure contribution quality.
- Treating one period’s score as a permanent trait rather than a snapshot with scope, context, and missing evidence.
- Comparing people on absolute numbers without anchoring against their own baseline and the team’s expected role shape.
- Letting the report imply causality or promotion readiness when the evidence only supports calibration and coaching discussion.
- Crediting merges as reviews: merge queues and bots zero them out and maintainers inflate them; D4 needs forge review events or it is `insufficient evidence`.
- Letting duplicate `(repo, commit_hash)` rows or `Revert "X"` pairs inflate churn and net_lines; the ingest layer must dedupe and cancel revert pairs before D2 scoring.

## Integration

### Data Pipeline (supplier: the project-scoped counterpart skill)

This skill consumes the same CSV format produced by:
- `extract-commits.sh` → `raw-commits.csv`
- `extract-mr-acceptances.sh` → `mr-acceptances.csv`

It also reuses the `identity-aliases.json` format and `email_to_person` config pattern. If the project-scoped extractors are unavailable, use the local-git fallback from this skill's directory:

```bash
python3 scripts/export-git-numstat.py --repo /path/to/repo --since YYYY-MM-DD \
  --out-commits /path/to/raw-commits.csv --out-mr /path/to/mr-acceptances.csv
```

The [exporter](scripts/export-git-numstat.py) reads non-merge commits with `git rev-list` and `git show --numstat`, validates rows before writing, and requires unused output paths. Its MR CSV contains only a header: local git does not establish forge review or reliable MR authorship events. Report those signals as unavailable; this fallback does not perform authenticity triage.

### Code Quality Rubric (consumer: software-clean-code-standard)

Sampled commit findings reference CC-* rule IDs (CC-NAM-01 through CC-DOC-04) and use the same P0-P3 priority system. No rule definitions are duplicated.

## Navigation

### Resources
- [Scoring Model](references/scoring-model.md) — D2-D5 point model, D1/D6 context, volume as context; weights, thresholds, tier override rules
- [Contribution Signals Catalog](references/contribution-signals-catalog.md) — all signals grouped by extraction tier (git-only, static analysis, AI attribution) with confounders
- [Code Quality Sampling Rubric](references/code-quality-sampling-rubric.md) — P0-P3 CC-* rule mapping for sampled commits; automated check confidence levels
- [AI Attribution Patterns](references/ai-attribution-patterns.md) — ground-truth tooling, detection heuristics, quality metrics for AI-assisted code (all context-only)
- [MR/PR Quality Signals](references/mr-pr-quality-signals.md) — rubber-stamp detection, size/review-speed benchmarks, 48-hour follow-up fix rate
- [Industry Benchmarks](references/industry-benchmarks.md) — dated calibration citations (GitClear, DORA, METR, Denisov-Blanch et al. 2024); AI-impact evidence lives in [dev-ai-coding-metrics evidence](../dev-ai-coding-metrics/references/evidence-update.md)
- Primary sources live in [data/sources.json](data/sources.json).

### Templates
- [Person Quality Report](assets/person-quality-report-template.md)
- [Team Calibration Report](assets/team-calibration-template.md)
- [Quality Scorecard](assets/quality-scorecard-template.md)

### Scripts
- [Pipeline README](scripts/README.md) — setup, CSV format spec, usage
- [Config Example](scripts/config-example.json)
- [Extract Contribution Profile](scripts/extract-contribution-profile.py)
- [Sample Code Quality](scripts/sample-code-quality.py)
- [Generate Quality Report](scripts/generate-quality-report.py)
- [Compute Volume Band](scripts/compute-code-rating.py) — context only
- [Script Tests](scripts/test_contribution_scripts.py)

### Related Skills
- the project-scoped counterpart skill — authenticity triage and governed signal convergence (upstream)
- `software-clean-code-standard` — CC-* rule definitions and code review standards (rubric source)
- `dev-ai-coding-metrics` — AI-tool impact, adoption and ROI at team level; owns the [Individual-Data Policy](../dev-ai-coding-metrics/SKILL.md#individual-data-policy) this skill follows
- `software-code-review` — review workflow and judgment (process)

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
