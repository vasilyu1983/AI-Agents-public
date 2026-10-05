---
name: dev-git-commit-message
description: "Generates or validates Conventional Commits messages from staged diffs. Use when drafting commit messages, checking repo rules, or inferring scope from changed files."
compatibility: Target runtime is repo-local skill frontmatter with `argument-hint` support.
argument-hint: "[--validate 'msg' | --tier short|detailed]"
version: "1.3"
last_validated: 2026-07-11
---

# Git Commit Message Generator

Default posture: subject line first; body only when risk, rationale, or breaking-change detail is needed; standard types only unless the repo already defines custom ones; never claim behavior not visible in the diff.

Rule: `rules/common/git.md` loads this invariant in every coding session.

## Quick Reference

| Need | Default | Reference |
|------|---------|-----------|
| Pick a type | `feat`/`fix`/`perf`/`refactor`/`docs`/`test`/`build`/`ci`/`chore`/`style`/`revert` | Type Selection table below |
| Format a subject | `type(scope): imperative summary`, ≤72 chars (50 ideal), no trailing period | Repo Policy Checks below |
| Mark a breaking change | `!` after type/scope, or a `BREAKING CHANGE:` footer | Breaking Change Format table below |
| Decide on a body | Only for risk, non-obvious rationale, or breaking-change detail | Body Required? table below |
| Handle AI-authored commits | No attribution in subject or body; `Assisted-by:` trailer is the default, `Claude-Session:` and `Audit-*` also accepted | AI-Authored Commits below |
| Pick a release/changelog tool | release-please for reviewed PR releases; semantic-release for full automation; changesets for monorepos | [references/changelog-generation-guide.md](references/changelog-generation-guide.md) |
| Scope a monorepo commit | package/app/service directory name, one level deep, stable over time | [references/monorepo-commit-conventions.md](references/monorepo-commit-conventions.md) |
| Validate a message locally | `python scripts/commit_validator.py validate --message "..."` | Scripts section below |

## Decision Tables

### Mode Selection

| Trigger | Mode | Action |
|---------|------|--------|
| User provides staged diff or asks to commit | Generate | Inspect staged surface, produce primary + alternatives |
| User provides an existing message string | Validate | Check rules, return PASS/WARN/FAIL + exact rewrite |
| Staged diff mixes unrelated areas | Split | Recommend split commits before generating |
| No staged changes | Stop | Report "no staged changes" |

### Type Selection

`feat` and `fix` have SemVer meaning in the [specification](https://www.conventionalcommits.org/en/v1.0.0/); other types and release behavior depend on the repository's tooling. Read its preset and release rules before claiming a bump. Scope and style rules below are local defaults, not requirements of the specification.

| Change | Type | Notes |
|--------|------|-------|
| New user- or API-visible capability | `feat` | Triggers MINOR bump |
| Incorrect behavior corrected | `fix` | Triggers PATCH bump |
| Measurable speed or memory improvement | `perf` | PATCH with semantic-release's default rules; verify repo rules |
| Structure improved, behavior unchanged | `refactor` | No release by default |
| Documentation only | `docs` | No release by default |
| Tests only | `test` | No release by default |
| Build tooling or packaging | `build` | No release by default |
| CI/CD workflow | `ci` | No release by default |
| Repo hygiene, no product change | `chore` | No release by default |
| Whitespace or formatting only | `style` | No release by default |
| Reverting a prior commit | `revert` | Release effect is tool-specific; the spec leaves revert handling open |
| Security fix | `fix(security):` | Prefer standard type + scope over custom `security:` type |
| Prompt/skill/YAML behavioral change | `feat` or `fix` | Do not classify by file extension alone |

### Scope Selection

| Situation | Action |
|-----------|--------|
| Repo has a scope map in [config.yaml](config.yaml) | Use mapped scope |
| One directory or package clearly dominates | Use that name, lowercase kebab-case |
| Change spans 2+ stable areas equally | Use broader parent scope or omit |
| Repository-wide change | Omit scope |
| Monorepo with independently versioned packages | See [references/monorepo-commit-conventions.md](references/monorepo-commit-conventions.md) |

### Body Required?

| Condition | Include body? |
|-----------|--------------|
| Subject is self-explanatory | No |
| Reason is non-obvious from subject | Yes — one sentence why |
| Security-sensitive or risky change | Yes — risk/rollback note |
| Breaking change | Include migration detail when needed; `!` alone is valid if the subject describes the break |
| Caller requests detailed template | Yes — use [assets/template-commit-message.md](assets/template-commit-message.md) |

### Breaking Change Format

| Signal | Format |
|--------|--------|
| Inline marker | `feat(api)!: change auth to OAuth2` |
| Footer | `BREAKING CHANGE: <migration summary>` |
| Both | Acceptable; footer body gets the detail |

## Before/After Examples

```text
BAD:  update
GOOD: docs(readme): add deployment instructions

BAD:  fix stuff
GOOD: fix(cart): prevent negative quantity on rapid add

BAD:  feat: added user dashboard (past tense)
GOOD: feat(dashboard): add analytics overview panel

BAD:  feat: add search (generated by Copilot)
GOOD: feat(search): add full-text product search

BAD:  feat(api): add comprehensive user search endpoint with full-text search across all profile fields including bio and location
GOOD: feat(api): add full-text user search endpoint

BAD:  feat: add dashboard, fix auth bug, update deps  (mixed concerns)
GOOD: (3 separate commits)
      feat(dashboard): add analytics overview panel
      fix(auth): correct token refresh race condition
      chore(deps): update react to 18.3.0
```

## Workflow

1. Decide mode from the Mode Selection table above.
2. For generate mode, inspect staged changes in this order:
   - `git diff --staged --name-status`
   - `git diff --staged --stat`
   - `git diff --staged --unified=1` only when type, scope, or risk is ambiguous
3. Classify type and scope using the tables above.
4. Detect scope from [config.yaml](config.yaml) first, then from the nearest stable directory.
5. Generate: one primary suggestion, up to two alternatives when scope or emphasis is ambiguous, short rationale.
6. Validate: apply Repo Policy Checks, return PASS/WARN/FAIL with exact rewrite on failure. The bundled validator checks its defaults; review target-repository overrides separately.
7. If the diff mixes unrelated work, recommend split commits before offering a combined message.

### Index is the commit boundary

Generate the message from the staged diff, not the working-tree diff. Before writing, inspect `git diff --cached --name-status` and `git diff --cached`; separately inspect `git diff --name-status` so unstaged edits cannot leak into the summary. If the index is empty, stop instead of describing uncommitted work. If a file is partially staged, describe only the staged hunks and flag that the same path has remaining unstaged changes.

For generated files, lockfiles, and migrations, name the behavioral change that caused them rather than listing them as independent accomplishments. Validate the proposed subject against the staged patch again immediately before commit because the index can change between drafting and execution.

## Output Contract

### Generate

```text
[NOTE] Suggested commit messages (3 files changed)

PRIMARY:
fix(auth): reject expired refresh tokens

ALTERNATIVES:
1. fix(api): reject expired refresh tokens
2. fix: reject expired refresh tokens during rotation

RATIONALE:
- Type: fix
- Scope: auth
- Signals: token validation path, regression test update, no new feature surface
```

### Validate

```text
VALIDATION: WARN

Message:
feat: update stuff

Issues:
- `update stuff` is too vague
- summary should name the changed behavior or surface

Suggested fix:
feat(auth): add refresh token rotation
```

## AI-Authored Commits

The commit message describes the change, not the tool that produced it. Apply the same rules regardless of whether a human or an AI agent drafted the code.

Banned in subject and body prose: `generated by`, `via copilot`, `via claude`, `chatgpt`, `ai assistant`, `bot`. Attribution belongs only in the final trailer block.

When AI-assisted work needs an audit trail, the recommended default is an `Assisted-by:` trailer. `Co-authored-by: <ai-tool>` is not the default and still fails validation. Keep trailers out of the subject line. Example:

```text
feat(search): add full-text product search

Assisted-by: LLM
```

Accepted AI trailers, all in one final paragraph with no blank line between them:

- `Assisted-by:` recommended default; the kernel form lists tools after the model (`Assisted-by: LLM coccinelle sparse`)
- `Claude-Session:` a session link some agent runtimes append
- `Audit-*` (for example `Audit-Batch:` and `Audit-Skill:`) audit-program provenance

Any other trailer that names an AI tool fails. Trailers placed in an earlier paragraph are invisible to `git interpret-trailers`, so the validator warns.

Use the exact format the target project documents; formats differ between projects. `Assisted-by:` is a distinct trailer from `Co-Authored-By:`. Upstream projects have not converged on one format, and their policies change, so read the target project's current contribution policy before adding any AI trailer. Policies worth checking: the Linux kernel's coding-assistants document (an `Assisted-by:` trailer listing the LLM and tools; AI agents must not add `Signed-off-by:`, because only a human can certify the DCO), LLVM's AI tool policy (`Assisted-by:` given as an example trailer), Apache's generative-tooling guidance (`Generated-by:`), and QEMU's code-provenance policy (declines AI-generated contributions). If a repo already uses `Co-Authored-By: <ai-tool>` by convention, do not silently rewrite it to `Assisted-by:` — flag the distinction and let the maintainer choose; changing trailer conventions after history exists breaks blame/provenance tooling that greps for the old trailer.

## Repo Policy Checks

Block or rewrite messages that:

- omit the type prefix (unless the repo's convention is plain imperative subjects, as its contribution guide or AGENTS.md states; then generate `Imperative summary` with no prefix and validate with `--no-type-prefix`, which skips only this rule)
- omit the space after `:` or use an empty scope; scope defaults to lowercase kebab-case
- use vague summaries: `update`, `fix stuff`, `change code`, `WIP`, `misc`
- include assistant/tool attribution outside the accepted trailers (see above)
- overstate impact not visible in the diff
- use past tense or gerund after the type prefix
- exceed 72 characters on the subject line
- end the subject line with a period

- Mark breaking changes with `!`, `BREAKING CHANGE:`, or `BREAKING-CHANGE:`; a footer is optional with `!`.
- Conventional Commits v1.0.0 is the referenced specification.
- commitlint's supported Node range and config format change between major versions; check its docs (see [data/sources.json](data/sources.json)) before writing a config file.
- For legacy `standard-version` setups, read its [repository notice](https://github.com/conventional-changelog/standard-version) before proposing migration; it points to `release-please` or the community fork `commit-and-tag-version`.
- `release-please-action` ships breaking major versions (runner-runtime and input changes). Check its releases page for the current major and its runtime requirement before pinning a workflow, and pin by commit SHA.
- Do not cite a major version for `semantic-release` or any release tool from memory; check its releases page first.

## Scripts

| Script | Purpose |
|--------|---------|
| [scripts/commit_validator.py](scripts/commit_validator.py) | Validate a single message, lint a history file, or generate a Markdown quality report |

```bash
# Validate one message
python scripts/commit_validator.py validate --message "feat(auth): add refresh token rotation"

# Lint a batch history file
python scripts/commit_validator.py lint --input data/sample-commit-history.json

# Generate a full Markdown report
python scripts/commit_validator.py report --input data/sample-commit-history.json --output report.md
```

See [scripts/README.md](scripts/README.md) for the full quick-start, input format, and rule reference.

History input must be a nonempty array of objects with a string `message`; optional `hash`, `author`, and `date` must also be strings. Both history commands reject empty input and malformed records before producing output; file errors name the input or output path. The validator uses bundled policy defaults and does not load `config.yaml`.

## Worktree PR Loop

Use this skill as the commit step inside the broader worktree-first delivery loop defined by [../dev-git-workflow/SKILL.md](../dev-git-workflow/SKILL.md).

In that loop: create or enter feature worktree → make code changes → stage intentionally → use this skill → run repo gate → open PR.

If the staged diff mixes several unrelated surfaces, stop and recommend split commits before the PR step.

## Known Traps

- Inferring scope from filenames alone, producing scopes that do not match the repo's bounded-context map.
- Compressing unrelated changes into one "clean" conventional commit, destroying revert and release-note usefulness.
- Treating AI-generated summaries as authoritative when the diff still contains hidden migrations or breaking changes.
- Optimizing for lint-pass format while losing the operational intent maintainers need for incident archaeology.
- Using `!` or `BREAKING CHANGE` casually and creating noisy downstream automation.

## Navigation

- [config.yaml](config.yaml) — repo-specific scope mapping and validation defaults
- [assets/template-commit-message.md](assets/template-commit-message.md) — optional detailed body template for complex commits
- [assets/template-security-commits.md](assets/template-security-commits.md) — wording guidance for security-sensitive commits
- [references/conventional-commits-guide.md](references/conventional-commits-guide.md) — full spec v1.0.0, type definitions, breaking changes, tooling setup
- [references/commit-message-antipatterns.md](references/commit-message-antipatterns.md) — anti-pattern catalog, regex detection patterns, commitlint config, CI examples
- [references/monorepo-commit-conventions.md](references/monorepo-commit-conventions.md) — scope strategy, per-package changelog generation, affected-package CI routing
- [references/changelog-generation-guide.md](references/changelog-generation-guide.md) — release tooling comparison (standard-version is deprecated; default to release-please for GitHub release PRs, changesets for per-package monorepo changelogs)
- [data/sources.json](data/sources.json) — curated primary sources for tool verification
- [data/sample-commit-history.json](data/sample-commit-history.json) — 20-commit sample dataset for lint and report subcommands
- Related: [../dev-git-workflow/SKILL.md](../dev-git-workflow/SKILL.md) — branching, hooks, PR workflow, release automation; use dev-git-workflow for branching/PR strategy, this skill for commit-message standards

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
