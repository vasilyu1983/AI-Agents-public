# Discovery Protocol

How to find public GitHub repos for a given domain, across all three modes (skill / practice / code). The ranking signals differ per mode; the triage workflow doesn't.

## Table of Contents

- [Mode-Specific Targeting](#mode-specific-targeting)
- [Universal Quality Signals](#universal-quality-signals-rank-candidates-by-these)
- [Anti-Signals](#anti-signals-deprioritize-or-skip)
- [Discovery Commands](#discovery-commands)
- [Triage Workflow](#triage-workflow)
- [April 2026 Discovery Gotchas](#april-2026-discovery-gotchas)
- [Common Discovery Mistakes](#common-discovery-mistakes)

## Mode-Specific Targeting

| Mode | Primary signal | Secondary signals | Typical query |
|------|---------------|-------------------|---------------|
| `skill` | `topic:agent-skills` + `topic:claude-skills` + `topic:codex-skills` | SKILL.md at root or in subdir; `references/` directory; known authors | `--topic claude-skills ios` |
| `practice` | Stars >= 500 + active `.github/workflows/` + `CODEOWNERS` | Merge queue use, release-please/changesets, Renovate/Dependabot | `"monorepo" stars:>500 archived:false` |
| `code` | Stars >= 1000 + target language/framework | OpenSSF Scorecard ≥ 5, commit-signing ratio, `pushed:>2026-01-01` | `"react query" language:typescript stars:>1000` |

## Universal Quality Signals (rank candidates by these)

| Signal | Why it matters |
|--------|---------------|
| Stars sufficient for mode | Community validation proxy (but not alone — see anti-signals) |
| Last commit < 90 days | Active maintenance, recent patterns |
| OpenSSF Scorecard ≥ 5 | Maintenance + security hygiene proxy (April 2026 standard) |
| CODEOWNERS file | Ownership signal, usually correlates with disciplined process |
| Commits signed (`>50%`) | Real contributors, not CI-bot-only or LLM-generated noise |
| Multiple active contributors (last 90d) | Reduces single-person bus factor |
| Specific, informative description | "Swift concurrency patterns for iOS apps" beats "AI skills for everything" |
| Permissive license (MIT / Apache-2.0 / BSD / CC-BY-4.0) | Extractable with attribution |

## Anti-Signals (deprioritize or skip)

| Anti-signal | Why to skip |
|-------------|-------------|
| Archived repo | Stale patterns, abandoned |
| Last commit > 12 months | Likely stale |
| Fork with no independent activity | Extract from upstream instead |
| Description ends "...for Claude" / "...for Codex" with thin content | April 2026 LLM-generated tell |
| Zero commit history before 2025-09 + single author + uniform file sizes | LLM-generated content farm |
| Star growth spike with zero issue/PR activity | Likely mutual-follow / bot-farm stars |
| No LICENSE file | Cannot legally extract |
| GPL / AGPL / CC-BY-SA license | Viral copyleft — cannot merge into permissive catalog |
| Wrapper/aggregator repo (just links) | Already in awesome lists, no original content |

## Discovery Commands

### `gh` CLI (preferred — fast, structured output)

```bash
# Mode: skill — narrower topics tend to be higher signal in April 2026
gh search repos --topic claude-skills --sort stars --limit 30 --archived=false
gh search repos --topic codex-skills  --sort stars --limit 30 --archived=false
gh search repos --topic agent-skills  --stars '>100' --archived=false

# Mode: practice — high-star repos with active workflows
gh search repos "monorepo" --stars '>=500' --archived=false \
  --sort updated --limit 30

# Mode: code — language + framework
gh search repos "i18n" --language typescript --stars '>=1000' --archived=false

# Author-scoped (all modes)
gh search repos --owner twostraws --limit 50

# Filter by push date for recency
gh search repos "react query" --language typescript \
  --updated '>2026-01-01' --archived=false
```

### Awesome-List Scan

Useful when `gh search` doesn't surface enough. Triage is mandatory in April 2026 — many awesome-lists are LLM-curated and list dead/LLM-spam repos.

```bash
gh api repos/VoltAgent/awesome-agent-skills/contents/README.md \
  --jq '.content' | base64 -d | grep -i "<domain>"
```

Always spot-check 3 random entries before trusting an awesome-list as a registry.

### Author Follow-Up

For trusted maintainers (see `data/sources.json` → `high_signal_authors`):

```bash
gh repo list twostraws --limit 50 --json name,description \
  --jq '.[] | select(.name | test("[Ss]kill"))'
```

## Triage Workflow

After discovery, run these checks on each candidate before adding to the shortlist:

1. **License check** — `gh api repos/<owner>/<repo>/license --jq '.license.spdx_id'` — confirm MIT / Apache / BSD / CC-BY
2. **Structure check** — does it have the mode-specific assets?
   - `skill`: SKILL.md + references/
   - `practice`: `.github/workflows/` + (CODEOWNERS | CONTRIBUTING.md | SECURITY.md)
   - `code`: representative configs + tests + source
3. **Recency check** — last commit date
4. **Activity check** — open issues/PRs, real contributors, signed commits
5. **LLM-spam check** (April 2026) — commit history before 2025-09, varied file sizes, issue/PR discussion
6. **OpenSSF Scorecard** (practice/code) — `https://api.scorecard.dev/projects/github.com/<owner>/<repo>`
7. **Domain match** — does the repo description actually match what you're researching?

Output a ranked shortlist of 3–5 repos with one-line rationale per repo. Bigger lists waste extraction time.

## April 2026 Discovery Gotchas

- **Topic `agent-skills` is noisy**: ~60% of topic results are stale or LLM-generated. Prefer `claude-skills` / `codex-skills` topics, or author-curated lists.
- **`gh search` star filters sort but don't filter**: low-star repos still appear on page 2+. Use `--limit 30 --sort stars` and truncate.
- **Archived repos leak into results**: always pass `--archived=false` and re-verify in triage.
- **Awesome-list stars are misleading**: a 50k-star awesome-list can still point to dead repos — check the linked repos, not the list's stars.
- **Scorecard may be missing** for smaller repos or private-forked-public repos: fall back to CODEOWNERS + commit-signing ratio.

## Velocity & Dependency Signals

When discovery quality signals (stars, forks, Scorecard) are ambiguous, use velocity and dependency data to break ties.

| Signal needed | Best source | When to use |
| ------------- | ----------- | ----------- |
| Star growth curve (is growth organic?) | star-history.com (visual) or OSS Insight API (`api.ossinsight.io/v1/repos/{owner}/{repo}/stars/history`) | Any time a repo has unusual star count vs. fork ratio |
| Star-spike day with zero activity (fake stars) | GH Archive via BigQuery (`bigquery-public-data.github_archive_day`) | When a repo jumped 1,000+ stars in a single day |
| How many projects depend on this package | deps.dev (`api.deps.dev/v3alpha/systems/{ecosystem}/packages/{pkg}`) | Mode C — assessing whether an idiom is widely adopted or niche |
| Package quality score across ecosystems | Libraries.io SourceRank | When comparing two similar packages with similar star counts |
| Recent contributor + commit velocity | OSS Insight repo analytics | Mode B — checking whether a practice repo is still actively maintained |

Decision tree:

1. Fork ratio passes (> 5%)? → proceed with normal triage.
2. Fork ratio fails? → check star-history.com for spike. Organic spike (viral post) is acceptable; cliff spike is not.
3. Star history ambiguous? → run GH Archive query for WatchEvent vs PushEvent correlation.
4. Repo is a library? → check deps.dev dependents count. > 100 dependents = widely adopted, worth extracting. < 10 = niche.

## Beyond GitHub

GitHub is the dominant host for agent skills (Mode A) and most OSS practice repos (Mode B), but high-signal content exists on other platforms.

**Sourcegraph** (`sourcegraph.com/search`) enables cross-host code search across GitHub, GitLab, and Bitbucket public repos in one query. Query syntax: `repo:`, `file:`, `content:`, `lang:`, `patternType:regexp`. No authentication required for public repos. Useful when a code pattern is spread across many orgs on different hosts — one Sourcegraph query replaces multiple GitHub code-search calls.

**GitLab** (`gitlab.com/api/v4/projects?order_by=stars&sort=desc`) hosts a distinct CI-template ecosystem (GitLab CI `.yml` templates, Auto DevOps patterns) not well-represented on GitHub. Relevant for Mode B when the team uses or is evaluating GitLab CI. See `data/sources.json` → `cross_host_registries` for the endpoint and rate limit.

**Codeberg and SourceHut** are niche but high-signal for systems-tooling and privacy-focused communities (Rust, C, Go minimal-dependency libraries). Worth a spot-check during Mode C when targeting low-dependency systems code. Both are rare enough that a single `curl` to their search API is sufficient before falling back to GitHub.

## Common Discovery Mistakes

- **Searching by keyword only** — misses repos without the keyword in the name
- **Trusting star count alone** — high-star repos can be stale or bot-farmed
- **Skipping the awesome-list spot-check** — feeds LLM-spam repos into the shortlist
- **Ignoring archived-repo filter** — dead patterns in the output
- **Including everything in the shortlist** — pick 3–5 to extract, not 20
- **Defaulting to `topic:agent-skills` in 2026** — too noisy; use the narrower topics or authors
