# Code Pattern Mining (Mode C)

What to look for when scanning high-signal OSS repos for framework idioms, config patterns, and code layouts. Output of a Mode C scan typically feeds `software-*` skills.

## Table of Contents

- [What to Fetch](#what-to-fetch)
- [High-Value Patterns to Mine](#high-value-patterns-to-mine)
- [Patterns Worth Skipping](#patterns-worth-skipping)
- [Quality Filter (per candidate pattern)](#quality-filter-per-candidate-pattern)
- [Extraction Output Format (per pattern)](#extraction-output-format-per-pattern)
- [Version Sensitivity (April 2026)](#version-sensitivity-april-2026)
- [Common Mistakes in Code Pattern Mining](#common-mistakes-in-code-pattern-mining)

## What to Fetch

| Asset | Path | Why it matters |
|-------|------|----------------|
| Package manifest | `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod` | Dependency choices, build scripts, exports map |
| Language config | `tsconfig.json`, `ruff.toml`, `mypy.ini` | Strictness level, target runtime, module resolution |
| Lint/format config | `biome.json`, `eslint.config.js`, `.prettierrc`, `rustfmt.toml` | What the team enforces and what they skip |
| Build scripts | `scripts/`, `Makefile`, `justfile`, `Taskfile.yml` | Real dev workflow vs documented workflow |
| Test layout | `tests/`, `__tests__/`, `*_test.go`, `*_spec.ts` | Test organization, naming, coverage strategy |
| Representative source | Entry modules (e.g. `src/index.ts`, `lib/mod.rs`) | Idioms, abstractions, public API shape |
| README | `README.md` | Positioning — useful as a map, not as extract content |

## High-Value Patterns to Mine

| Pattern class | What to look for | Example |
|---------------|------------------|---------|
| **Public API shape** | Exports map, barrel files, sub-path exports | React Query's `useQuery` factory pattern |
| **Type-level tricks** | Branded types, phantom types, template literal magic | tRPC's router type inference |
| **Error handling** | Error classes, result types, panic vs error patterns | Neon/pg error taxonomy |
| **Concurrency patterns** | Actor isolation, channel usage, task groups | Tokio's task-spawn patterns |
| **Config schema** | Runtime validation of configs (zod, pydantic) | Next.js env validation |
| **Test organization** | Unit/integration split, fixture layout, snapshot policy | Vitest + MSW setup |
| **Build graph** | Turborepo/Nx/Bazel task graph; incremental build strategy | Turborepo pipeline config |
| **Module boundaries** | Workspace config, internal vs public packages | pnpm workspace with `workspace:*` |
| **Framework plugin shape** | Plugin registration, lifecycle hooks | Vite plugin API usage |
| **Performance patterns** | Caching layers, memoization, lazy loading | React Query's queryClient.setQueryData patterns |

## Patterns Worth Skipping

| Skip | Why |
|------|-----|
| Generic utility functions (debounce, throttle, clamp) | Already in every stdlib/utility lib |
| Verbose JSDoc on self-documenting code | Noise, doesn't survive refactors |
| "Hello world" example routes | No production signal |
| Legacy compatibility shims | Rarely transferable; often tied to specific migration |
| Author-opinion comments ("I think this is cleaner") | Opinion without evidence is noise |
| Test fixtures tied to repo-local services | Not transferable |

## Quality Filter (per candidate pattern)

1. **Is it specific to the framework, or generic JS/TS/Python?** Generic patterns are in any tutorial. Framework-specific patterns are the signal.
2. **Is it working code at HEAD, or a proposal?** Check open PRs — "this pattern" might be about to be ripped out. To confirm a pattern is stable rather than mid-experiment, run `git log -S"<distinctive-identifier>"` (pickaxe) on the file — a pattern introduced once and never touched again is stable; one with repeated add/revert/re-add cycles is still being fought over. See [git-history-forensics.md](git-history-forensics.md) for the full `-S` vs `-G` decision framework and using `git log -L` to pull the pattern's full evolution once you've found the introducing commit.
3. **Is it cited in the repo's own docs?** Well-documented patterns are load-bearing; undocumented patterns may be accidental.
4. **Does it compile on the current framework version?** Patterns written for React 18 may not work on React 19.
5. **Does it survive the "any senior dev would write this" test?** If yes, skip. Signal lives in non-obvious abstractions.
6. **Is there a test for it?** Untested patterns in OSS are usually experiments.

## Extraction Output Format (per pattern)

```markdown
### Pattern: <short name>

**Source**: https://github.com/<owner>/<repo>/blob/<sha>/<file-path>
**Extracted**: 2026-04-23
**License**: <SPDX-ID>
**Scorecard**: <n.n>
**Framework/language version**: <e.g. React 19.1, TypeScript 5.6>

**The pattern**:
<1-3 sentence description in your own words — not copy-paste>

**Minimal example** (<10 lines, rewritten):
```<lang>
// short, paraphrased example — not verbatim from source
```

**Why it matters**:
<what problem does this solve? what failure does it prevent?>

**Preconditions**:
- Framework version
- Other libs required
- Constraints (runtime, bundler, target)

**Trade-offs**:
- What you give up

**Where it goes**:
- Target skill: `software-frontend`
- Target file: `references/react-query-patterns.md`
- Action: new section / new file / update existing

**Novel vs local**: new / extends existing / duplicates existing
**Confidence**: high / medium / low
```

## Version Sensitivity (April 2026)

Code patterns decay faster than skill patterns. Record the framework version the pattern was extracted from and flag if the pattern is version-specific. Examples of version-sensitive domains:

| Domain | Current stable (Apr 2026) | Known migration hazards |
|--------|----------------------------|--------------------------|
| React | 19.x | Suspense for data fetching, useOptimistic — pre-19 patterns age out |
| Next.js | 16.x | App Router patterns vs Pages Router; middleware API v2 |
| TypeScript | 5.8.x | `satisfies` operator, `const` type params |
| Python | 3.13 (free-threaded builds emerging) | GIL-optional patterns new; older async patterns still dominant |
| Node.js | 24 LTS | Built-in `fetch`, `test runner`, permissions model |
| Rust | 1.85+ edition | Async traits stable, GAT patterns matured |
| Swift | 6.x | Strict concurrency on by default, `@concurrent` semantics |

If the source repo targets an older version, flag the pattern with an "as of" qualifier and verify it still applies to your target framework version.

## Common Mistakes in Code Pattern Mining

- **Extracting without framework-version context** — patterns age out fast; undated patterns become misinformation
- **Copy-pasting code** — license violation + your codebase drifts from the source
- **Extracting patterns that only work because of the repo's tooling** — Turbopack-specific patterns don't transfer to Webpack repos
- **Ignoring the test** — if the pattern isn't tested in the source, it's an experiment, not a pattern
- **Over-indexing on bleeding edge** — patterns from RC/beta versions may not make it to stable
- **Missing the "why"** — the idiom without the motivation is cargo-culting
- **Ignoring trade-offs** — every pattern has costs; extract them too
