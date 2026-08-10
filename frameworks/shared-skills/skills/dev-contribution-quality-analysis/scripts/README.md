# Dev Contribution Quality Analysis — Scripts

Pipeline for analyzing developer contribution quality from git commit and MR/PR data.

## Prerequisites

- Python 3.10+ (stdlib only — no pip install needed)
- Input CSVs in the format produced by the project-scoped counterpart skill extraction scripts

## Pipeline

```text
[extract-commits.sh]          → raw-commits.csv      ─┐
[extract-mr-acceptances.sh]   → mr-acceptances.csv    ├→ extract-contribution-profile.py → contribution-profiles.json
[identity-aliases.json]       → identity resolution   ─┘                                           │
                                                                                                    ▼
[repo checkouts (optional)]   → sample-code-quality.py → sample-quality.json ──┐
                                                                                ├→ generate-quality-report.py → quality-report.md
                                                                                │                              quality-scores.json
                                    contribution-profiles.json ─────────────────┘
```

Extraction scripts (`extract-commits.sh`, `extract-mr-acceptances.sh`) live in the project-scoped counterpart skill's `scripts/`. This skill consumes their output.

## CSV Format

### raw-commits.csv

```csv
repo,commit_hash,author_name,author_email,datetime,weekday,hour,timezone,subject,files_changed,insertions,deletions,is_merge,is_move,code_ins,code_del,test_ins,test_del,config_ins,config_del,docs_ins,docs_del,other_ins,other_del
```

| Column | Type | Description |
|--------|------|-------------|
| repo | string | Repository name or relative path |
| commit_hash | string | Full 40-char SHA |
| author_name | string | Git author name |
| author_email | string | Git author email |
| datetime | ISO 8601 | Author date with timezone (e.g., `2026-03-15T14:30:00+01:00`) |
| weekday | string | Day name (e.g., `Monday`) |
| hour | int | Hour (0-23) from the author date |
| timezone | string | UTC offset (e.g., `+01:00`) or `Z` |
| subject | string | First line of commit message (quoted, `""` escaping) |
| files_changed | int | Number of files in the commit |
| insertions, deletions | int | Total lines (all file types). Equal to the sum of the per-class columns below. |
| is_merge, is_move | 0/1 | Merge commit (parent count > 1) and rename detected (`=>` in numstat) |
| code_ins, code_del | int | Source-code lines only (`.py .js .ts .go .rs ...`); excludes tests |
| test_ins, test_del | int | Test files (`/test/`, `/tests/`, `_test.*`, `.spec.*`, etc.) |
| config_ins, config_del | int | Config and IaC (`.json .yaml .toml .ini .env Dockerfile .tf ...`) |
| docs_ins, docs_del | int | Markdown and prose (`.md .mdx .rst .txt .adoc`) |
| other_ins, other_del | int | Data, lockfiles, generated, vendored, snapshots, minified |

D2 sub-signals that reference "lines" or "code volume" use `code_ins + code_del` (`code_loc` / `code_churn`), not raw `insertions + deletions`. Reports must show `support_share = (test+config+docs+other) / total` next to the headline number so readers can see how much of the diff is supporting activity vs. authored code. The classification rules and the complexity-weighted rating formula live in the project-scoped counterpart skill's `packs/it-insider-risk/references/loc-measurement-best-practices.md`.

For the rating itself, use this skill's vendored `compute-code-rating.py`. It reads the same CSV and produces `code-rating.csv` and `code-rating.md` keyed on the resolved person identity. This skill's `extract-contribution-profile.py` should consume those outputs rather than reimplement classification.

### mr-acceptances.csv

```csv
repo,commit_hash,merger_name,merger_email,datetime,weekday,hour,timezone,source_branch,subject,files_changed,insertions,deletions
```

Same columns as raw-commits.csv plus `source_branch` (the branch merged) and `merger_name`/`merger_email` (who performed the merge) instead of `author_name`/`author_email`.

## Usage

### Step 1: Extract contribution profiles

```bash
python scripts/extract-contribution-profile.py --config config/report-config.json
```

Reads CSVs, merges identities, computes Tier 1 signals per person. Outputs `contribution-profiles.json`.

### Step 2: Sample code quality (optional, requires repo checkouts)

```bash
python scripts/sample-code-quality.py --config config/report-config.json
```

Samples N commits per person, analyzes diffs, maps findings to CC-* rules. Outputs `sample-quality.json`.

### Step 3: Generate quality report

```bash
# Person mode (individual deep-dive)
python scripts/generate-quality-report.py --config config/report-config.json --mode person

# Team mode (calibration comparison)
python scripts/generate-quality-report.py --config config/report-config.json --mode team
```

## Configuration

Copy `config-example.json` into your run directory and customise. Key settings:

- `target_persons` / `target_teams`: limit analysis scope
- `quality_sampling.enabled`: toggle Tier 2 code sampling
- `repo_roots`: paths to git checkouts for Tier 2 analysis
- `role_calibration`: per-person role adjustments (lead, manager, CTO)
- `thresholds`: scoring thresholds (see `references/scoring-model.md`)

## Identity Resolution

Identity is resolved in this order:
1. Shared `identity_alias_matrix_json` (from the project-scoped counterpart skill)
2. Config-local `email_to_person` overrides
3. Machine-local email patterns (`.local`, `Mac.fritz.box`, `@users.noreply.github.com`) are flagged as context-only

The same canonical name is used across all outputs.

## Relationship to the project-scoped counterpart skill

This skill is a **quality analysis** tool. the project-scoped counterpart skill is a **risk triage** tool.

- **Shared**: CSV format, identity alias format, config patterns
- **Not shared**: extraction scripts (reuse from the project-scoped counterpart skill), authenticity triage, risk scoring
- **Boundary**: the project-scoped counterpart skill handles governed convergence and review prioritization; this skill handles contribution quality.
