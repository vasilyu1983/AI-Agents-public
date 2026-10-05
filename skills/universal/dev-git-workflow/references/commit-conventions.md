# Commit Conventions

Commit-message format, SemVer type mapping, commitlint setup, changelog/release
tooling comparison, and AI-attribution trailers are owned by
[dev-git-commit-message](../../dev-git-commit-message/SKILL.md) — that skill
covers the full Conventional Commits grammar, scope selection, breaking-change
footers, and the `Assisted-by:`/`Co-authored-by:` attribution rules.

This skill (`dev-git-workflow`) owns branching, PR, hook, and release-*process*
workflow — not commit-message standards. Use dev-git-commit-message for the
message itself; use this skill's [references/release-management.md](release-management.md)
for release *sequencing* once messages are already correct.

For commit-scope conventions in a monorepo, see
[dev-git-commit-message/references/monorepo-commit-conventions.md](../../dev-git-commit-message/references/monorepo-commit-conventions.md).

The sections below are workflow practices that dev-git-commit-message does not cover.

## Atomic Commits

Each commit should be one logical change, so it can be reviewed, reverted, and bisected on its own.

```bash
# Good: one logical change per commit
git commit -m "feat: add user authentication"
git commit -m "test: add auth integration tests"
git commit -m "docs: document auth API"

# Bad: several unrelated changes in one commit
git commit -m "Add auth, fix bug, update docs"
```

Clean up WIP and typo commits before pushing with `git commit --amend` or `--fixup` plus `rebase --autosquash` (see [interactive-rebase-guide.md](interactive-rebase-guide.md)).

## Team Adoption: Gradual Rollout

1. **Education.** Share the commit convention, demo the linter and release tooling, and show what the team gains (generated changelogs, version bumps).
2. **Soft enforcement.** Run the commit linter as a non-blocking warning and review examples together in PRs.
3. **Hard enforcement.** Make the linter a blocking CI check and require conforming commits (or conforming squash-merge titles) on every PR.

Move to the next phase only when the warning rate from the previous phase is low; a blocking gate introduced too early gets bypassed.

## Commit Message Templates

A local template reminds authors of the format every time `git commit` opens the editor:

```bash
cat > ~/.gitmessage <<'TEMPLATE'
# <type>[optional scope]: <description>
#
# [optional body: why, not what]
#
# [optional footer(s): BREAKING CHANGE:, Refs:, trailers]
TEMPLATE
git config --global commit.template ~/.gitmessage
```

Use `git config commit.template <path>` (no `--global`) to ship a repo-specific template.
