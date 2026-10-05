---
name: research-git
description: "Scans public GitHub repos for skills, practices, and code patterns. Use when studying how open-source teams configure monorepo CI and PR review, or enriching skills."
compatibility: Claude Code + Codex. Runtime-agnostic; scripts require `gh` CLI + `jq`.
version: "1.2"
last_validated: 2026-07-11
---

# Repo Research

Scan public GitHub repos for **agent skills** (SKILL.md ecosystem), **dev practices** (git/PR/CI workflows from real teams), or **code patterns** (framework idioms, config layouts) — then merge validated insights into the local catalog with full attribution.

Manual extraction is unsustainable. The agent-skill ecosystem is large and still growing (see [data/sources.json](data/sources.json) for named registries and their scale), before counting the repos worth scanning for their CI, testing, or i18n setups. This skill makes the scan repeatable and the merge auditable.

## Navigation

- [Quick Reference](#quick-reference) — entry-point table by need
- [Four Modes](#four-modes) — skill / practice / code / killer-feature targeting
- [When to Use](#when-to-use) and [When NOT to Use](#when-not-to-use)
- [Default Workflow](#default-workflow) — discover → triage → fetch → diff → merge
- [Output Contract](#output-contract) — per-mode scan report shape
- [Promotion Check](#promotion-check) — five checks before a finding is promoted
- [references/discovery-protocol.md](references/discovery-protocol.md) — discovery commands and triage (includes velocity/dependency signals and beyond-GitHub hosts)
- [references/code-pattern-mining.md](references/code-pattern-mining.md) — Mode C extraction
- [references/attribution-rules.md](references/attribution-rules.md) — licensing
- [references/code-search-syntax.md](references/code-search-syntax.md) — code-search qualifiers the API accepts (legacy engine, not the web UI), `gh search code` CLI, rate-limit strategy, example queries per mode
- [references/graphql-triage.md](references/graphql-triage.md) — single-repo health query, batch-alias pattern, repo discovery via `search` connection
- [references/signal-quality.md](references/signal-quality.md) — fake-star/astroturf detection: fork ratio, GH Archive spike queries, contributor account-age checks
- [references/git-history-forensics.md](references/git-history-forensics.md) — single-repo git-history verification: pickaxe `-S`/`-G`, `blame -w -C -M`, `bisect run`, `range-diff`, when `git log` lies
- [data/sources.json](data/sources.json) — registries, authors, hot lists, ecosystem analytics, cross-host registries

## Quick Reference

| Need | Mode | Entry point |
|------|------|-------------|
| Find SKILL.md repos for a domain | `skill` | `scripts/search_repos.sh --kind skill <domain>` |
| Find teams with strong git/CI practice to copy | `practice` | `scripts/search_repos.sh --kind practice <topic>` |
| Find framework idioms in high-signal OSS | `code` | `scripts/search_repos.sh --kind code <language>/<framework>` |
| Find OSS clones of a commercial product (killer-feature signal) | `killer-feature` | `scripts/search_repos.sh --kind killer-feature <commercial-product>` |
| Fetch assets from a known repo | any | `scripts/fetch_repo_assets.sh <owner>/<repo> <out> --kind <mode>` |
| Compare external to local equivalent | any | `scripts/diff_against_local.sh <external> <local>` |
| Verify a claimed practice/pattern against real git history (not just static files) | `practice`, `code` | [references/git-history-forensics.md](references/git-history-forensics.md) |
| License/attribution rules | any | [references/attribution-rules.md](references/attribution-rules.md) |
| Registries + high-signal authors | any | [data/sources.json](data/sources.json) |

## Four Modes

### Mode A — Skill Discovery

**Target**: repos containing `SKILL.md` + `references/` (the agent-skill ecosystem).
**Fetch**: SKILL.md, references/, optionally scripts/.
**Output**: research pack → feeds existing `software-*`, `data-*`, `ai-*`, `ops-*` skills in your catalog.
**Use when**: enriching an existing skill, or auditing what already exists before building one.

### Mode B — Practice Scan

**Target**: real production repos (not skill repos) with strong process signals.
**Fetch**: `.github/` (workflows, PR/issue templates, CODEOWNERS), `CONTRIBUTING.md`, `SECURITY.md`, release notes cadence, `docs/adr/` (architecture decisions).
**Output**: research pack → feeds `dev-git-workflow`, `qa-*`, `ops-*` skills.
**Use when**: redesigning team policy (branching, PR review, CI gates, release cadence) and you want evidence from real teams, not just framework docs.
**Before promoting a practice**: sample about 20 recent merged PRs to confirm it is enforced, not just configured, and compare the source repo's scale (contributors, PR volume, CI size) with the target team's. See the Quality Filter in [references/practice-scan-targets.md](references/practice-scan-targets.md).

### Mode C — Code Pattern Extraction

**Target**: high-signal OSS repos in a specific language/framework.
**Fetch**: configs (tsconfig, biome, eslint, ruff, cargo), representative source modules, test layouts, `scripts/` or `Makefile`.
**Output**: patterns → feeds `software-*` skills.
**Use when**: a local skill covers a domain where mature OSS implementations exist and the team's patterns are better than anything in docs (think: React Query's cache patterns, tRPC's type-safety tricks, Turborepo's build graph).

### Mode D — Killer-Feature Mining

**Target**: OSS clones of a specific commercial product (e.g., `supabase/supabase` clones Firebase, `plausible/analytics` clones Google Analytics).
**Fetch**: README.md, CHANGELOG.md, docs/, landing pages — the marketing surface that reveals which features the OSS author chose to replicate (and which they explicitly didn't).
**Output**: rows on the shared `pay-trigger-ledger.tsv` with `signal_type=oss_clone_focus` → contributes to the bundle's Killer-Feature Convergence Protocol owned by `research-review-mining`.
**Use when**: the bundle is hunting a killer feature for a commercial product, OR you want to know what the OSS world considers the load-bearing feature(s) of a category leader.
**Premise**: OSS authors only reimplement what they think matters. That choice is revealed preference under cost — a strong proxy for monetizable core.
**Reference**: [references/killer-feature-mining.md](references/killer-feature-mining.md) — full extraction protocol + LLM prompts.

## When to Use

- **Enriching a skill**: you have `software-ios-native` and want to steal what other operators learned
- **Pre-build audit**: you're about to author a new skill — has the work already been done?
- **Policy redesign**: your team's PR workflow is breaking — scan how 5 leading OSS repos handle it
- **Framework adoption**: you're committing to a new framework — pull idioms from the repos that stress-test it
- **Periodic refresh**: re-scan of a domain (about quarterly as a starting cadence) to catch new patterns from active maintainers
- **Bundle handoff — killer-feature scan**: `research-review-mining` Killer-Feature Mode asks Mode D for the OSS clone signal on a target commercial product

## When NOT to Use

- Web articles, papers, blog posts → `ai-deep-research`
- Library/package selection or upgrade path → `dev-dependency-management`
- Cross-repo *code context* for your own portfolio → `dev-context-multi-repo`
- Per-commit message generation or commit-policy *implementation* → `dev-git-commit-message`
- Branching-model *design* in isolation (no evidence-gathering needed) → `dev-git-workflow`
- One-off lookup of a specific file → plain `WebFetch`
- Cloning to fork → plain `git clone`
- Validated Q&A answers or known-error solutions → the Stack Overflow corpus (community MCP or the emerging Stack Overflow for Agents exchange), via `qa-debugging` — not repo mining

## Layered opportunity handoff

Use the opportunity evidence layers when this scan supports area discovery. Contribute L7 feasible delivery: inspect code, license, maintenance, dependencies and representative failure modes against the proposed buyer task. Mode D also informs L6 alternatives, but an OSS clone is a developer choice, not proof that customers pay for that feature. Stars and reported stacks are discovery leads; return testable feasibility limits and correction/support effort. Pure repository research stays here without requiring commercial gates.

Carry source and underlying event IDs, dates, scope, supportive/mixed/adverse/unknown direction, evidence basis, counterevidence and the decisive unknown into the comparison worksheet. The same event appearing in several layers remains one event. No scout score, source count or convergence label passes a commercial gate; retain missing and adverse evidence in the handoff.

## Default Workflow

### ASCII Flow

```text
public repo research request
  -> Choose mode: skill, practice, code, or killer-feature
  -> Check prior packs, cached raw extracts, and target sources.json
  -> Discover and shortlist 3-5 high-signal repos
  -> Fetch only mode-specific assets and pin source commit SHAs
  -> Diff external material against the local target
  -> Mine novel patterns and write an attributed research pack
  -> Apply only if the user's request already authorizes target changes; otherwise hand off the pack
```

### Phase 0 — Context Check (always run first)

Before fetching anything from GitHub:

1. **Prior research packs**: `ls docs/research/*-scan.md` — if a recent pack covers this domain + mode, read it first
2. **Cached extractions**: `ls docs/research/*/raw/<owner>__<repo>/` — if a repo was extracted in the last 30 days, reuse unless `HEAD` advanced
3. **Target skill's `data/sources.json`**: if a source is already tracked, compare its `commit_sha` to the current repo to decide refresh vs reuse
4. **Existing pack as Level 1 input** — only re-fetch the delta

Mirrors the [context-first protocol](../agents-subagents/references/context-first-protocol.md): use prepared artifacts before raw fetches.

### Phase 1–9 — Active Research

1. **Frame the goal**: "Enrich `software-ios-native` with novel patterns from the iOS skill ecosystem" *or* "Redesign release workflow using practices from 3 active monorepos" *or* "Improve React i18n patterns in `software-localisation`". Confirm scope, purpose, and the time window (which pushed/updated range counts) before searching; until a scan has run, describe the ecosystem as unmeasured rather than characterising it
2. **Discover**: `scripts/search_repos.sh --kind <mode> <domain>` → ranked shortlist
3. **Triage**: pick 3–5 repos using signals in [references/discovery-protocol.md](references/discovery-protocol.md) — applies to all modes
4. **Extract** (only what's missing or stale): `scripts/fetch_repo_assets.sh <owner>/<repo> docs/research/<scan-id>/raw/ --kind <mode>`
5. **Diff**: `scripts/diff_against_local.sh docs/research/<scan-id>/raw/<repo>/ <target-local-skill>/`
6. **Mine insights**: follow mode-specific guidance
   - Mode A → [references/insight-mining.md](references/insight-mining.md)
   - Mode B → [references/practice-scan-targets.md](references/practice-scan-targets.md)
   - Mode C → [references/code-pattern-mining.md](references/code-pattern-mining.md)
   - Mode D → [references/killer-feature-mining.md](references/killer-feature-mining.md) (output appends to shared bundle ledger, not a local skill)
7. **Synthesize**: research pack at `docs/research/<scan-id>.md`
8. **Authority check**: if the user asked only for research, present the pack and stop. If the same request already asks to improve, apply, or implement, that is the opt-in; do not pause for duplicate approval.
9. **Apply when authorized**: follow [references/apply-protocol.md](references/apply-protocol.md), preserving the target scope and attribution requirements.

Verify repo activity, license, and Scorecard against current GitHub before citing findings. Repo research drifts fast — re-check before merging insights. Always confirm the repo is not LLM-generated (commit history, issue activity, real contributors) before trusting any pattern from it.

This skill pins no rate limits or Git versions. Before a research pack cites one, read it at the source and record the check date: `gh api rate_limit` and <https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api> for GitHub limits; <https://git-scm.com/docs> and the Git release notes for Git versions and defaults (see [references/git-history-forensics.md](references/git-history-forensics.md)).

## Output Contract

Research pack at `docs/research/YYYY-MM-DD-<mode>-<domain>-scan.md`:

```markdown
# <Mode> Scan: <Domain> — <Date>

## Mode
skill | practice | code | killer-feature

## Sources Reviewed
| Repo | Stars | Last commit | License | Scorecard | Quality | Action |
|------|-------|-------------|---------|-----------|---------|--------|

## Insights Extracted
For each insight:
- Source: <repo URL + commit SHA>
- Mode: skill | practice | code
- Pattern: <name and 1-line description>
- Why it matters: <evidence from the source>
- Where it goes: <target skill + reference file>
- Novel vs local: <new / extends existing / duplicates existing>
- Confidence: <high / medium / low + rationale>

## Recommended Merges
| Pattern | Target skill | Action | Approved? |

## Skipped
<insights reviewed and rejected, with reason>

## Attribution Pack
<full source list with URLs, upstream authors, commit SHAs, licenses, extraction dates>
```

## Attribution Rules

Mandatory before any merge:
1. Check the source repo's LICENSE — MIT / Apache-2.0 / BSD / CC-BY-4.0 permit derived work with attribution. No LICENSE file means all rights reserved: do not extract
2. Never copy `SKILL.md`, reference files, or source files verbatim — extract patterns, rewrite in local voice
3. Cite source URL + commit SHA + extraction date + license + author on every merged insight; the author is the upstream original, not the fork you happened to fetch
4. Add the source to the target skill's `data/sources.json`
5. Pin to commit SHA, never `main` — supply-chain drift is real
6. Screen anything copied for secrets, credentials, PII, and organisation-specific details (internal hostnames, people's names, customer data) before it enters the pack; a permissive licence does not make those ingestible

Full rules: [references/attribution-rules.md](references/attribution-rules.md)

## Patterns

| Pattern | Why it works |
|---------|--------------|
| Pin every fetch to commit SHA | Makes extractions reproducible; survives repo renames, branch deletions, force-pushes |
| Filter by OpenSSF Scorecard ≥ 5 (Mode B/C) | This skill's starting heuristic, not an evidence-backed threshold: Scorecard aggregates maintenance and security checks, and 5 is where this skill starts the cut. Read the check breakdown, not the total, before dropping a repo |
| Require CODEOWNERS for practice-scan targets | Repos without ownership signals usually have ad-hoc process — nothing to steal |
| Shortlist to 3–5 repos, not 20 | Extraction is the bottleneck; wide scans dilute signal |
| Apply one skill at a time, one commit per skill | Makes merges reviewable and revertable |
| Always diff-against-local before extracting | Prevents duplication, surfaces real novelty |
| Re-scan about quarterly (not weekly, not yearly) | Starting cadence, not a measured one: weekly scans pay cache costs without new signal, yearly misses drift. Shorten it if a re-scan finds many new patterns, lengthen it if it finds none |
| Sample about 20 recent merged PRs before promoting a practice (Mode B) | Config shows what a repo asks for; merged PRs show whether reviews, required checks, and the merge queue are actually used |
| Match the source repo's scale to the target team before transplanting (Mode B) | A practice that solves a collision problem at many parallel PRs a day is overhead for a small team; record it as scale-dependent when the scales differ |
| Verify high-value practice/pattern claims against real git history, not just static files | `CODEOWNERS`, `CONTRIBUTING.md`, and merge-queue config describe policy; `blame -w -C -M`, `range-diff`, and `bisect run` show whether it's actually followed — see [references/git-history-forensics.md](references/git-history-forensics.md) |

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|--------------|--------------|-----|
| Applying insights during a research-only request | Changes a target the user did not authorize | Hand off the pack; apply only when the request includes implementation or later authorizes it |
| Cloning entire repos by default | Wastes context; most value is in ≤10 files | Default to mode-specific asset list |
| Copying content verbatim | License violation + voice drift | Always rewrite in local voice |
| Extracting without diff-against-local | Duplicates content, creates contradictions | Always run diff first |
| Trusting stars alone | LLM-spam repos farm stars via mutual-follow networks | Cross-check commit signing, Scorecard, contributor count |
| Trusting LLM-generated awesome-lists | Some awesome-lists are LLM-synthesized and list dead repos | Spot-check 3 random entries before using the list as a registry |
| Fetching `main` branch without pinning | Content drifts; citations become unverifiable | Always capture commit SHA, cite it |
| Scanning repos flagged as mirrors/vendors | Duplicates upstream; wastes triage time | Filter `fork=false`, `archived=false`, check for `mirror` in description |
| Treating topic `agent-skills` as a quality signal | Topic can be noisy; inspect dated activity and substantive content | Prefer `claude-skills`, `codex-skills`, or author-curated lists |
| Research pack with no attribution | Cannot re-verify, breaks audit trail | Every insight gets source URL + upstream author + commit SHA + license |
| Claiming ecosystem prevalence before a scan ("the topic is full of generated shells") | No measurement backs the figure; it steers triage and the pack | Say the prevalence is unmeasured; ask for scope, purpose, and time window, then count from the scan's own shortlist |
| Reporting "what people do for X" from unstructured reading of repos | One reader's impression is not a pattern; a second reader would code the same repos differently | Pre-register a codebook, have a second coder (person or model) independently code a sample, report the agreement, then claim the pattern |
| Re-fetching repos extracted in the last 30 days | Wastes API quota + duplicates context | Phase 0: check `docs/research/*/raw/` first |
| Ignoring prior research packs | Loses prior synthesis, agents do duplicate analysis | Phase 0: read existing packs as Level 1 context input |

## Known Issues

| Issue | Impact | Workaround |
|-------|--------|------------|
| The authenticated `gh api` core budget is finite | Bulk scans of 50+ repos can exhaust it | Run `gh api rate_limit` before a large scan and read `resources.core`; batch, pause, or use GraphQL (single call, deeper data) for listings |
| GitHub search has its own limits, separate from the core budget, and code search is lower than repo and issue search | A code-search sweep (e.g. `path:.github/workflows`) throttles quickly even with core budget free | Run `gh api rate_limit --jq '.resources \| {search, code_search}'` and pace below the current figures; prefer one wide query + local filtering over many narrow ones; never parallelise code search — see [references/code-search-syntax.md](references/code-search-syntax.md) |
| Papers with Code is retired | Any inherited workflow that used PwC for reproducibility signal is broken | research-git **is** the replacement reproducibility-signal channel (repo/reimplementation inspection); do not add PwC back as a source |
| Topic `agent-skills` is noisy | Some results are generated shells; no prevalence estimate is established here | Prefer `--owner` filter on known authors; cross-check with awesome-lists |
| LLM-generated SKILL.md repos are visually convincing | Wastes extraction budget on zero-signal content | Red flags: commit history too short or too uniform for the maturity the README claims, single author, uniform file sizes, no issues/PRs/reviews from outside contributors, description ends in "...for Claude" |
| GitHub Search skips archived repos inconsistently | Dead repos appear in ranked output | Always pass `archived:false` in `gh search`; double-check in triage |
| `gh search repos --stars` filters; `--sort stars` only orders | Sorting alone lets low-star repos through | Pass `--stars '>=N'` for a floor and `--sort stars` for order; `search_repos.sh` sets per-mode floors (see its `--help`) |
| Some high-signal repos use nested skill dirs (`skill/`, `<name>-pro/`) | Default fetch misses SKILL.md | Always recursive-tree lookup, not root-only |
| OpenSSF Scorecard results may not be published for a given repo | The Scorecard signal can be missing | Run the `scorecard` CLI against the repo yourself, or fall back to CODEOWNERS + commit-signing ratio |
| REST `git/trees?recursive=1` truncates past a documented entry and size limit and sets `truncated: true` (limits: <https://docs.github.com/en/rest/git/trees>) | Huge monorepos return a partial tree that looks complete | `fetch_repo_assets.sh` walks subtrees when the listing is truncated and records `tree_listing` in `_metadata.json`; for very large repos, fetch the specific subtree by path |
| Attribution strings break when source repo is renamed | Links 404 | Pin the commit SHA; GitHub redirects many old-name URLs, but a redirect may not resolve for every URL form, especially branch refs, so cite the SHA |

## Scenarios

### Scenario 1 — Skill Discovery (Mode A)

*Goal: enrich `software-kafka` with patterns from the agent-skill ecosystem. The shortlist below is illustrative, not real search output: `example/kafka-skill` does not exist, and the real entries must be re-verified live before use.*

```bash
scripts/search_repos.sh --kind skill kafka
# → ranked shortlist (illustrative): example/kafka-skill, redpanda-data/skills, ...

# Triage: keep 3, drop LLM-generated candidates
scripts/fetch_repo_assets.sh example/kafka-skill \
  docs/research/YYYY-MM-DD-skill-kafka/raw/ --kind skill

scripts/diff_against_local.sh \
  docs/research/YYYY-MM-DD-skill-kafka/raw/example__kafka-skill/ \
  skills/universal/software-kafka/
# → diff shows 2 new reference files, 1 new quick-reference row

# Mine, synthesize, present research pack, apply with attribution
```

### Scenario 2 — Practice Scan (Mode B)

*Goal: redesign the team's PR workflow; harvest practices from 3 active monorepos.*

```bash
scripts/search_repos.sh --kind practice monorepo
# → vercel/next.js, microsoft/vscode, nrwl/nx

scripts/fetch_repo_assets.sh vercel/next.js \
  docs/research/YYYY-MM-DD-practice-pr/raw/ --kind practice
# fetches .github/workflows/, CONTRIBUTING.md, CODEOWNERS, PR template, release-please config

# Mine via practice-scan-targets.md rubric: merge queue config, required checks,
# auto-assignment rules, review SLA signals

# Output feeds dev-git-workflow, not this skill
```

### Scenario 3 — Code Pattern Extraction (Mode C)

*Goal: improve `software-localisation` with real React i18n patterns.*

```bash
scripts/search_repos.sh --kind code react i18n
# → lingui/js-lingui, formatjs/formatjs, i18next/i18next

scripts/fetch_repo_assets.sh lingui/js-lingui \
  docs/research/YYYY-MM-DD-code-react-i18n/raw/ --kind code
# fetches: package.json, tsconfig, representative source modules, test layout

# Mine via code-pattern-mining.md: ICU plurals handling, runtime vs build-time,
# type-safe message catalogs

# Output feeds software-localisation
```

### Scenario 4 — Killer-Feature Mining (Mode D)

*Goal: contribute the OSS clone signal to the bundle's killer-feature hunt for Firebase.*

```bash
scripts/search_repos.sh --kind killer-feature firebase
# → supabase/supabase, appwrite/appwrite, nhost/nhost, pocketbase/pocketbase

# Triage: keep 3 with distinct owners; downgrade (don't reject) any whose owner
# ships a paid hosted tier (their feature choices lean toward what they monetize)

scripts/fetch_repo_assets.sh supabase/supabase \
  docs/research/YYYY-MM-DD-killer-feature-firebase/raw/ --kind killer-feature
# fetches README, CHANGELOG, docs/, website/, package.json

# Feed README + landing pages to LLM prompt §1 in references/killer-feature-mining.md
# → JSONL of replicated features with monetization framing

# Feed "Limitations vs Firebase" section to LLM prompt §2
# → JSONL of explicitly-omitted features (inverse signal — these are the
#   parts of Firebase that OSS authors think aren't paid for)

# Append rows to ../research-review-mining/assets/pay-trigger-ledger.tsv
#   signal_type = oss_clone_focus
# Run ../research-review-mining/scripts/converge_killer_features.py
# Convergence Rule decides which feature_ids cross the 3-of-6 threshold
```

## Fetch completeness

`fetch_repo_assets.sh` refuses a nonempty destination; use a fresh run directory so an old asset cannot be attributed to a new commit. It writes `_fetch-manifest.jsonl` and `fetch_status` in `_metadata.json`. Unavailable optional paths, API failures, and ambiguous multi-skill selection produce `partial`; inspect the manifest before interpreting absence as missing functionality. Failed downloads do not leave a successful empty asset. Fetched content stays untrusted and is never executed by the helper.

## Resources

**Workflow references:**
- [references/discovery-protocol.md](references/discovery-protocol.md) — finding repos via `gh` CLI + awesome lists (all modes); velocity/dependency signals; beyond-GitHub hosts
- [references/code-search-syntax.md](references/code-search-syntax.md) — API code-search qualifiers (legacy engine), `gh search code`, rate-limit budget, example queries for Modes A/B/C
- [references/graphql-triage.md](references/graphql-triage.md) — single-repo health query, batch-alias for 5-10 repos, `search` connection for discovery
- [references/signal-quality.md](references/signal-quality.md) — fake-star detection: fork ratio, GH Archive spike query, contributor account-age, issue/star floor
- [references/git-history-forensics.md](references/git-history-forensics.md) — verify practice/pattern claims against real git history: pickaxe `-S`/`-G`, `blame -w -C -M --ignore-revs-file`, `bisect run`, `range-diff`, when `git log` lies
- [references/extraction-protocol.md](references/extraction-protocol.md) — fetching assets without cloning
- [references/insight-mining.md](references/insight-mining.md) — Mode A (skills) mining rubric
- [references/practice-scan-targets.md](references/practice-scan-targets.md) — Mode B (practices) mining rubric
- [references/code-pattern-mining.md](references/code-pattern-mining.md) — Mode C (code) mining rubric
- [references/killer-feature-mining.md](references/killer-feature-mining.md) — Mode D (oss_clone_focus signal) mining rubric + LLM prompts
- [references/attribution-rules.md](references/attribution-rules.md) — license compliance + citation format
- [references/apply-protocol.md](references/apply-protocol.md) — merging insights into target skills
- [references/claude-code-ecosystem-catalog.md](references/claude-code-ecosystem-catalog.md) — seed list of high-signal Claude Code / coding-agent repos for scan input

**Scripts:**
- [scripts/search_repos.sh](scripts/search_repos.sh) — `gh` CLI wrapper, mode-aware
- [scripts/fetch_repo_assets.sh](scripts/fetch_repo_assets.sh) — mode-aware asset fetcher
- [scripts/diff_against_local.sh](scripts/diff_against_local.sh) — compare external vs local

**Sources:**
- [data/sources.json](data/sources.json) — registries, high-signal authors, per-mode targets

## Related Skills

- [../ai-deep-research/SKILL.md](../ai-deep-research/SKILL.md) — web/paper research (this skill is repo research)
- [../dev-context-multi-repo/SKILL.md](../dev-context-multi-repo/SKILL.md) — code context across your own repos (this skill is external-repo pattern extraction)
- [../dev-dependency-management/SKILL.md](../dev-dependency-management/SKILL.md) — library/package selection (this skill is pattern extraction)
- [../dev-git-workflow/SKILL.md](../dev-git-workflow/SKILL.md) — target consumer of Mode B output
- [../dev-git-commit-message/SKILL.md](../dev-git-commit-message/SKILL.md) — per-commit message generation (disjoint scope)
- [../agents-skills/SKILL.md](../agents-skills/SKILL.md) — authoring your own skills (this skill enriches them)

## Promotion Check

Before any finding is promoted, run these five checks:

1. Resolve the primary artifact (the paper, the repo at a pinned commit, or the operator's own page), not a summary of it.
2. Copy the claim verbatim from that artifact, with its number, benchmark, or quote. Never restate it from memory.
3. Confirm an independent origin: a separate study, reproduction, or team, not a re-post or second channel for the same release.
4. Record the date you checked the artifact.
5. If any check fails, label the finding "unverified" and do not promote it.

For a contested or high-stakes claim, hand off to `ai-deep-research` for its verifier pass.

When the finding is a qualitative pattern across repos ("teams doing X mostly do Y"), treat it as coded data: write the codebook (categories and decision rules) before reading the repos, have a second coder or an independent model run code a sample against it, and report the agreement alongside the claim. A pattern with no codebook and one coder is an impression, not a finding.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
