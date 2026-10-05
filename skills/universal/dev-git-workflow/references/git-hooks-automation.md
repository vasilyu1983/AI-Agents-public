# Git Hooks and Automation

What belongs in local hooks, how to distribute them, and the pre-push and secret-scan recipes. Commit-message linting (commitlint config, `commit-msg` wiring) is owned by [dev-git-commit-message](../../dev-git-commit-message/SKILL.md). Hooks are feedback, not enforcement: `--no-verify` skips them, so every rule that must hold runs again in CI ([automated-quality-gates.md](automated-quality-gates.md)).

## Contents

- [What Goes in Which Hook](#what-goes-in-which-hook)
- [Choosing a Hook Manager](#choosing-a-hook-manager)
- [Pre-Push: Check the Exact Tip Being Pushed](#pre-push-check-the-exact-tip-being-pushed)
- [Secret Scanning](#secret-scanning)
- [Other Useful Hooks](#other-useful-hooks)
- [Bypass Policy](#bypass-policy)
- [Pitfalls](#pitfalls)

## What Goes in Which Hook

| Hook | Put here | Keep out |
|------|----------|----------|
| `pre-commit` | formatters and linters on staged files, secret scan, large-file guard | full test suites, network calls; aim for a few seconds or people bypass it |
| `commit-msg` | message format check | anything slow |
| `pre-push` | tests and type-check for what is being pushed, push-to-protected-branch guard | checks that depend on running services |
| `post-checkout` / `post-merge` | reminders or dependency install when the lockfile changed | anything that edits tracked files |

**Repo checks versus runtime readiness.** Hooks should verify the commit: it builds, tests pass, no secrets, format holds. Whether local services, databases, or credentials are up is a separate readiness check with its own command; mixing the two makes the hook fail for reasons unrelated to the code and trains people to bypass it.

## Choosing a Hook Manager

| Repo | Default |
|------|---------|
| Node/TypeScript | Husky plus lint-staged, installed by the `prepare` script so hooks arrive with `npm install` |
| Polyglot or non-Node, want one config | lefthook (single YAML, parallel commands, built-in staged-file globs) |
| Python-centric, or you want pinned, versioned hook repos | the `pre-commit` framework (`.pre-commit-config.yaml` with pinned `rev`s) |
| No tooling allowed | committed `scripts/hooks/` plus `git config core.hooksPath scripts/hooks` |

Husky changed its setup at v9: hooks are plain scripts in `.husky/` and `prepare` runs `husky`. Guides that use `husky install` or `husky add` describe earlier majors. Check the installed major before copying setup commands.

lint-staged runs commands only on staged files and re-stages files the commands fixed. A hook that modifies files without re-staging produces a commit that differs from what was checked.

Recent Git versions support named, config-defined hooks alongside `.git/hooks` and `core.hooksPath`; use the installed `git hook list` and [Git's hook reference](https://git-scm.com/docs/git-hook) before adopting them. Parallel execution is opt-in for safe events and hooks; commit and working-tree hooks such as `pre-commit` and `commit-msg` remain serial. Keep required enforcement in CI regardless of hook manager.

## Pre-Push: Check the Exact Tip Being Pushed

A pre-push hook that runs tests on the working tree tests the wrong thing when the tree has uncommitted edits, or when the push sends a branch other than the one checked out (`git push origin other-branch`). Git passes the refs being pushed on stdin, one line per ref: `<local-ref> <local-sha> <remote-ref> <remote-sha>`. Use them:

```sh
#!/bin/sh
# pre-push: run checks only against the commit actually being pushed
head=$(git rev-parse HEAD)
while read -r local_ref local_sha remote_ref remote_sha; do
  case "$local_sha" in *[!0]*) ;; *) continue ;; esac     # deletion: nothing to test
  case "$remote_ref" in
    refs/heads/main|refs/heads/release/*)
      echo "pre-push: direct push to $remote_ref is not allowed; open a PR" >&2; exit 1 ;;
  esac
  if [ "$local_sha" != "$head" ] || [ -n "$(git status --porcelain --untracked-files=no)" ]; then
    echo "pre-push: $local_ref ($local_sha) is not the clean checked-out HEAD; checks would test the wrong tree." >&2
    echo "Commit or discard local edits, or check out the branch being pushed, then push again." >&2
    exit 1
  fi
done
exec make check    # or the repo's gate command
```

Git sends an all-zero SHA as `local_sha` for a deletion and as `remote_sha` for a new remote branch; the recipe matches "only zeros" rather than a fixed-length literal so it also works in SHA-256 repositories. For expensive checks, an alternative to refusing is to create a temporary detached worktree at `$local_sha`, run the checks there, and remove it.

## Secret Scanning

Scan staged changes before commit, and again in CI plus host-side push protection; the local scan is the cheapest place to catch a secret, but not the only one.

- gitleaks is a common default. Its subcommand for scanning staged changes has changed between major versions; check `gitleaks --help` (or the project's README) for the installed version's pre-commit invocation and pin the version in the hook manager's config.
- Keep an allowlist file for known false positives, reviewed like code.
- A secret that reached a commit is rotated first, even if the commit was never pushed to a shared remote; see SKILL.md History-Rewrite Risk Judgment.

## Other Useful Hooks

- **Large-file guard:** reject staged files above a size the repo chooses, and point to Git LFS or artifact storage.
- **Branch naming:** enforce only if tooling depends on names (release automation, ticket linking); otherwise it is friction.
- **Protected-branch guard:** refuse local commits or pushes to `main` and release branches (included in the pre-push recipe above); the ruleset remains the real control.

## Bypass Policy

- Acceptable: WIP commits on a private branch that will be cleaned before review; a hook broken by a tool outage, with an issue filed.
- Not acceptable: skipping the secret scan, bypassing on shared or protected branches, or routinely skipping to avoid fixing lint.
- Agents do not use `--no-verify` unless the human explicitly asked for it in this task.

## Pitfalls

| Pitfall | Fix |
|---------|-----|
| Full test suite in `pre-commit` | Move it to `pre-push` or CI; keep pre-commit fast |
| Hook config not committed, or hooks not installed on clone | Commit `.husky/`, `lefthook.yml`, or `.pre-commit-config.yaml`; install via `prepare` or a documented setup command |
| Hooks treated as enforcement | Repeat every required check in CI |
| Pre-push tests the working tree, not the pushed commit | Read the stdin refs and check the exact tip |
| Hook depends on local services | Separate runtime readiness from repo checks |
