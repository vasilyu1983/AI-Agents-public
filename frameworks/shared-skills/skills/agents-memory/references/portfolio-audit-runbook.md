# Portfolio Audit Runbook

How to validate AGENTS.md / CLAUDE.md across multiple repos and find alignment opportunities. Use this when you own more than one repo and want to keep their hot memory honest, fresh, and consistent.

## Table of Contents

- [The Three Scripts](#the-three-scripts)
- [Quick Start](#quick-start)
- [What audit_repo.sh Checks](#what-audit_reposh-checks)
- [Path-Resolution Conventions](#path-resolution-conventions)
- [Suppressing False Positives](#suppressing-false-positives)
- [Recommended Cadence](#recommended-cadence)
- [What compare_blocks.sh Tells You](#what-compare_blockssh-tells-you)
- [Worked Example: Four-Repo Product Portfolio](#worked-example-four-repo-product-portfolio)
- [Limitations](#limitations)

## The Three Scripts

| Script | Purpose | Use When |
|--------|---------|----------|
| `scripts/audit_repo.sh` | Validate one repo's AGENTS.md | Pre-commit, single-repo CI gate |
| `scripts/audit_portfolio.sh` | Run audit across N repos with summary | Periodic portfolio review, post-merge sweep |
| `scripts/compare_blocks.sh` | Find shared sections; classify identical / near / divergent | Looking for alignment candidates or intentional divergence |

All three are bash, no extra dependencies beyond `grep`/`awk`/`md5`/`md5sum`/`wc`.

## Quick Start

Single repo:

```bash
./scripts/audit_repo.sh /path/to/repo
```

Portfolio:

```bash
./scripts/audit_portfolio.sh /path/to/repo1 /path/to/repo2 /path/to/repo3
```

From a list file (one repo path per line, `#` for comments):

```bash
./scripts/audit_portfolio.sh --from-file repos.txt
```

Find shared/divergent sections:

```bash
./scripts/compare_blocks.sh /path/to/repo1 /path/to/repo2 /path/to/repo3
./scripts/compare_blocks.sh --section "Agent Routing" repo1 repo2 repo3
```

## What audit_repo.sh Checks

1. **Stale paths**: every backticked, path-shaped token in AGENTS.md must resolve on disk. Catches references to deleted/renamed/never-existed files (the most common hallucination-bait).
2. **Script executability**: `./scripts/foo.sh` references must exist *and* be executable.
3. **Size budget**: warns when AGENTS.md exceeds 300 lines (instruction-budget risk per Anthropic Opus 4.7 guidance).
4. **Lint integration**: delegates symlink/mirror, secrets, and `@import` checks to `lint_claude_memory.sh`.
5. **Hallucination-bait heuristics**:
   - **Wrong-layer**: `authoritative in ` `policy.ts` ` flagged when sibling `policy.json` exists.
   - **Scaffold-tense**: present-tense enforcement in scaffold-stage repos (no `src/`, `app/`, `package.json`, `Package.swift`, etc.).
   - **Platitudes**: `## Agent Execution Style` sections (typically copy-pasted boilerplate).

Severity ladder: HIGH (block agents), MED (fix soon), LOW (cleanup).

Exit codes: 0 if clean or only MED/LOW; 1 if any HIGH issue.

## Path-Resolution Conventions

The validator handles four common path styles automatically:

| Path style | Example | Resolution |
|------------|---------|------------|
| Repo-rooted | `` `scripts/foo.sh` `` | Tries `<repo>/scripts/foo.sh` |
| Explicit relative | `` `./scripts/foo.sh` `` | Same |
| Sibling repo | `` `../mobile-ios/x.md` `` | Resolves at parent dir; treated valid if sibling repo path exists |
| Prefix-relative | `` `lib/stripe/` `` (when convention is "all `lib/` paths under `app/src/`") | Auto-tries `app/`, `app/src/`, `app/lib/`, `src/`, `lib/`, `docs/context/` prefixes |

For non-default prefix conventions, declare them explicitly in the AGENTS.md header:

```markdown
<!-- audit-path-prefix: ../mobile-ios/docs/context/ -->
<!-- audit-path-prefix: app/src/, app/lib/ -->
```

Multiple directives accumulate. Comma-separated within one directive also works.

## Suppressing False Positives

For paths that intentionally don't exist (DON'T-do-this examples, future tooling references), use:

```markdown
<!-- audit-ignore: ./gradlew, res/values/strings.xml -->
```

Glob patterns work (`*.tmp`, `dir/*`).

For scaffold-stage repos: add a "Pre-Code Caveat" section or `<!-- pre-code -->` directive — this auto-suppresses the scaffold-tense MED warning. Recommended over `audit-ignore` because it documents the situation in-line for human readers.

## Recommended Cadence

- **Per-repo pre-commit hook**: `audit_repo.sh .` blocks commits with HIGH issues.
- **Weekly portfolio sweep**: `audit_portfolio.sh` over the whole portfolio. Cheap (a few seconds per repo).
- **Quarterly alignment review**: `compare_blocks.sh` to find sections that have drifted apart silently. Decide explicitly which are alignment candidates and which are intentionally divergent — both are valid outcomes.

## What compare_blocks.sh Tells You

For each H2 section that appears in 2+ repos:

- **IDENTICAL** — md5-identical body across all repos. Strong candidate for a shared file or symlink (`ln -sf shared/agent-routing.md AGENTS-section.md`).
- **ALIGNMENT CANDIDATE** (>80% line overlap) — high similarity with drift. Reconcile to a single source.
- **REVIEW** (40–80% line overlap) — moderate overlap. Decide intentional divergence vs. drift.
- **DIVERGENT** (<40% line overlap) — likely intentionally different per repo. Probably a section title accidentally collides; not an alignment opportunity.

The output is informational, not an enforcement gate. Use it as input to a quarterly review.

## Worked Example: Four-Repo Product Portfolio

An illustrative run across `mobile-ios`, `web-app`, `landing-site`, and `mobile-android` surfaced:

- 42 false-positive HIGH issues from prefix-relative paths in `web-app` — fixed by adding `<!-- audit-path-prefix: ../mobile-ios/docs/context/ -->` and the auto-prefix list.
- 4 real stale-path HIGH issues in `landing-site` — references to PRD/design/strategy docs that didn't exist. Fixed by replacing them with real existing doc paths.
- 2 expected stale-path HIGH issues in `mobile-android` — `./gradlew`, `res/values/strings.xml`. The first is scaffold-stage tooling; the second is a "DON'T do this" anti-pattern example. Suppressed via `<!-- audit-ignore: ./gradlew, res/values/strings.xml -->`.
- 1 scaffold-tense MED in `mobile-android` — auto-suppressed by the existing Pre-Code Caveat section.

Final state: 0 HIGH / 0 MED / 0 LOW across all four repos.

`compare_blocks.sh` then identified `## Agent Routing` as an ALIGNMENT CANDIDATE (96–100% pairwise overlap across all four repos) — a clear next step for converting to a shared file.

## Limitations

- Only validates backticked, path-shaped tokens. URLs, command invocations, and prose claims are not checked.
- Wrong-identifier detection (e.g., wrong Xcode scheme) is not yet automated. Use the parallel-subagent recipe in [cross-doc-audit.md](cross-doc-audit.md).
- Cross-doc consistency (AGENTS.md vs README.md vs roadmap docs) is not automated. Same recipe applies.
- The alignment classifier uses line-by-line overlap and won't catch semantic divergence with rephrased content.
