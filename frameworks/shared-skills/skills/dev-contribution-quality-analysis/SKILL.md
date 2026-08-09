---
name: dev-contribution-quality-analysis
description: "Analyzes commit and PR history to score contribution quality objectively. Use when building engineering scorecards, calibrating promotions, or measuring AI-assist impact."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# Developer Contribution Quality Analysis

Objective, multi-dimensional analysis of code contribution quality from git data. Produces individual deep-dive reports and team calibration comparisons.

## Modern Best Practices

- Measure contribution quality through outcomes (churn, duplication, test coverage), not presence metrics
- AI-assisted code is normal; score the output, not the authorship
- GitClear Diff Delta and CodeScene Code Health are the established commit-level quality benchmarks
- Stanford ghost engineering research claims commit content analysis predicts expert quality judgments (r=0.82); study is not peer-reviewed — apply with caution
- Agent Trace (Cursor RFC) is an emerging vendor-neutral standard for AI attribution
- DX Core 4 framework consolidates DORA/SPACE into a unified set of four oppositional dimensions
- DORA 2025 itself reports AI adoption now correlates with *higher* throughput and a "mirror and multiplier" pattern (seven team archetypes replace prior elite/high/medium/low clusters); do not confuse it with vendor telemetry reports
- Faros AI's 2026 "Acceleration Whiplash" telemetry report (4,000+ teams, distinct from DORA) found bugs per developer up 54% and incidents per PR up 242.7% where AI adoption outran test/review discipline — cite it as Faros, not DORA
- GitClear Jan 2026 (2,172 developer-weeks): power AI users produced 4.2x more durable code than non-users but also showed 9x more churn — AI widened an existing performance gap and its downside, not evidence of uniform uplift
- GitClear "The Maintainability Gap" 2026 (623M code changes) extends this: refactor/moved-code share collapsed to 3.8% YTD 2026 (13% in 2023), copy/paste 15.7% in H1 2026, error-masking constructs +47%, cross-file reuse -35% — use these as the current structural-quality benchmarks
- Treat commits and PRs authored end-to-end by an autonomous coding agent (not just AI-assisted) as a distinct evidence class — see Known Traps

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
- Pre-promotion or performance-review technical calibration
- Measuring AI-assisted development quality impact
- Identifying skill gaps or coaching targets

## When NOT to Use This Skill

- Governed multi-signal risk triage -> the project-scoped counterpart skill
- Defining code quality rules -> `software-clean-code-standard`
- AI coding tool ROI or adoption tracking -> `dev-ai-coding-metrics`
- Repository-level code health (not person-level) -> `qa-refactoring`
- General code review workflow -> `software-code-review`

## Defaults

- Measure contribution quality, not presence or working hours
- Quality is multi-dimensional; no single number replaces the 6-dimension profile
- Compare against personal baseline first, then team, then industry
- AI-assisted code is quality-neutral; measure outcomes (churn, duplication, test coverage) regardless of authorship
- Git data is necessary but not sufficient; always note what evidence is missing
- CC-* rules from `software-clean-code-standard` are the code quality rubric
- Minimum data: 30 commits and 20 active days in the analysis window
- Scripts consume the same CSV format as the project-scoped counterpart skill extraction
- Ingest dedupes on `(repo, commit_hash)` and cancels `Revert "X"` + original pairs (both flagged `net_cancel`) so churn-rate and net_lines do not double-count multi-root scans or self-reverting churn
- Code volume is measured as `code_loc` (extension-filtered: drops `.json`, `.yaml`, `.md`, snapshots, generated paths). Raw `net_loc` and `churn_loc` are kept for context but never feed the headline rating.
- The D2 headline rating is complexity-weighted: `code_loc × (1 + α·ΔCC + β·novelty)`, banded against team median with role calibration. Definition is shared with the project-scoped counterpart skill; both skills must produce identical ratings from the same CSV input.

## Workflow

1. **Define the question** — quality audit, growth tracking, team calibration, or promotion case
2. **Set scope** — person(s), time window, repo roots
3. **Extract git + MR data** — use the project-scoped counterpart skill extraction scripts or provide CSVs in the same format
4. **Run contribution profile analysis** — `extract-contribution-profile.py` computes all Tier 1 signals
5. **Run code quality sampling** (optional) — `sample-code-quality.py` maps sampled commits to CC-* rules
6. **Generate quality report** — `generate-quality-report.py` in `person` or `team` mode
7. **Present findings** with explicit limitations and calibration context

## ASCII Flow

```text
contribution quality request
  -> define decision: audit, growth, calibration, promotion, or AI impact
  -> set people, time window, repos, and minimum data threshold
  -> extract and normalize git plus MR/PR evidence
  -> dedupe commits and cancel revert pairs
  -> compute contribution profile and role-aware baselines
  -> sample code quality against CC-* rules when repo checkouts exist
  -> generate person, team, scorecard, or JSON output
  -> present limitations and calibration context
```

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify current external benchmark claims, vendor metrics, and framework standards against primary sources before presenting them as current fact.
- Treat vendor-authored scoring systems, AI attribution standards, and industry benchmark comparisons as volatile unless rechecked against current documentation or published research.
- If web verification is unavailable, label time-sensitive benchmark or standards guidance as unverified.

## Decision Tree: Assessment Type

```text
What is the assessment goal?
├── Individual quality audit?
│   ├── Point-in-time snapshot → person quality report
│   └── Trend over time → person trend report (multiple windows)
├── Team quality comparison?
│   ├── Promotion / review calibration → team calibration report
│   └── Quality trend monitoring → team trend report
└── AI impact assessment?
    └── Before/after or AI-ratio analysis → quality-neutral outcome comparison
```

## Scoring Model (Summary)

Six dimensions, 100 total points. See `references/scoring-model.md` for full detail.

| # | Dimension | Weight | Primary Signals |
|---|-----------|--------|-----------------|
| D1 | Delivery Consistency | 20 | Commit frequency stability, active days, MR throughput, trend |
| D2 | Code Quality Signals | 25 | Churn rate (14d), duplication, refactoring ratio, complexity-weighted rating (code-only LOC × ΔCC + novelty), CC-* compliance |
| D3 | Commit Craft | 15 | Message quality, scope discipline, PR size, self-merge rate |
| D4 | Review & Collaboration | 20 | Review participation, responsiveness, cross-repo contribution |
| D5 | Test & Safety Practices | 10 | Test-to-code ratio, test presence in features, security-file awareness |
| D6 | D6 Context-Only Signal — AI Development Quality | — | Annotation only: AI code survival, quality parity, verification burden |

**Quality Tiers (D1-D5, 90 pts total)**: A (72-90 Exemplary), B (54-71 Solid), C (36-53 Developing), D (0-35 Concerning)

D6 carries no point allocation and is excluded from tier assignment. It is appended to reports as a separate annotation. See `references/scoring-model.md` for rationale.

## Output Modes

- **Person quality report** — individual deep-dive with 6-dimension breakdown, sampled commit quality, CC-* findings
- **Team calibration report** — comparison matrix with heatmap, tier distribution, team strengths/gaps
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
- Letting duplicate `(repo, commit_hash)` rows or `Revert "X"` pairs inflate churn and net_lines; the ingest layer must dedupe and cancel revert pairs before D2 scoring.

## Integration

### Data Pipeline (supplier: the project-scoped counterpart skill)

This skill consumes the same CSV format produced by:
- `extract-commits.sh` → `raw-commits.csv`
- `extract-mr-acceptances.sh` → `mr-acceptances.csv`

It also reuses the `identity-aliases.json` format and `email_to_person` config pattern. It does NOT duplicate extraction scripts or authenticity triage.

### Code Quality Rubric (consumer: software-clean-code-standard)

Sampled commit findings reference CC-* rule IDs (CC-NAM-01 through CC-DOC-04) and use the same P0-P3 priority system. No rule definitions are duplicated.

## Navigation

### Resources
- [Scoring Model](references/scoring-model.md) — 6-dimension point model (D1-D5 scored, D6 annotation only); weights, thresholds, tier override rules
- [Contribution Signals Catalog](references/contribution-signals-catalog.md) — all signals grouped by extraction tier (git-only, static analysis, AI attribution) with confounders
- [Code Quality Sampling Rubric](references/code-quality-sampling-rubric.md) — P0-P3 CC-* rule mapping for sampled commits; automated check confidence levels
- [AI Attribution Patterns](references/ai-attribution-patterns.md) — ground-truth tooling, detection heuristics, quality metrics for AI-assisted code (all context-only)
- [MR/PR Quality Signals](references/mr-pr-quality-signals.md) — rubber-stamp detection, size/review-speed/rework benchmarks and thresholds
- [Industry Benchmarks](references/industry-benchmarks.md) — GitClear (2020-2024 baseline, 2026 cohort), DORA 2024/2025, METR, Stanford calibration data

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

### Related Skills
- the project-scoped counterpart skill — authenticity triage and governed risk signal convergence (upstream)
- `software-clean-code-standard` — CC-* rule definitions and code review standards (rubric source)
- `dev-ai-coding-metrics` — AI tool adoption and ROI measurement (complementary)
- `software-code-review` — review workflow and judgment (process)

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
