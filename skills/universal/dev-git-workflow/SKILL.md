---
name: dev-git-workflow
description: "Designs team Git workflows for branching, PRs, and releases. Use when choosing branching models, stacked PRs, merge queues, worktree isolation for agents, or collaboration rules."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.4"
last_validated: 2026-09-25
---

# Git Workflow

Use this skill to choose a team Git model, set merge and review policy, and define safe defaults for human and AI-assisted collaboration. It assumes the reader knows Git commands; it carries the decisions.

Default bias: GitHub Flow or trunk-based development, one merge method per repository, a merge queue once PRs routinely go stale before landing, one worktree per agent, and release branches only when version support requires them. Hosting-platform features (stacked PRs, merge-queue options, ruleset fields) and Git itself change several times a year: before recommending a version-gated Git feature, check the release notes on git-scm.com; before recommending a platform feature, check that platform's docs for availability on the user's plan.

## Quick Reference

| Need | Default | Reference |
|------|---------|-----------|
| Pick a branching model | GitHub Flow; trunk-based plus merge queue at high merge concurrency | [references/branching-strategies.md](references/branching-strategies.md) |
| Pick a merge method | squash for small-PR flows; merge commits for release branches | [Merge Method](#merge-method), [references/pr-best-practices.md](references/pr-best-practices.md) |
| Keep main green under concurrency | merge queue or merge train | [Merge Queue](#merge-queue), [references/automated-quality-gates.md](references/automated-quality-gates.md) |
| Land dependent changes fast | stacked PRs | [references/stacked-diffs-guide.md](references/stacked-diffs-guide.md) |
| Run parallel agent or feature work | one worktree and branch per agent | [references/ai-agent-worktrees.md](references/ai-agent-worktrees.md) |
| Release and hotfix | upstream-first fixes, tags from main | [references/release-management.md](references/release-management.md) |
| Commit messages and changelogs | owned by dev-git-commit-message | [dev-git-commit-message](../dev-git-commit-message/SKILL.md), [references/commit-conventions.md](references/commit-conventions.md) |
| Debug bad merges or regressions | conflict discipline, bisect | [references/conflict-resolution.md](references/conflict-resolution.md), [references/git-bisect-debugging.md](references/git-bisect-debugging.md) |

Route elsewhere: review of a specific change set → [software-code-review](../software-code-review/SKILL.md); CI/CD platform design beyond merge gates → [ops-devops-platform](../ops-devops-platform/SKILL.md); commit-message format, trailers, and changelog tooling → [dev-git-commit-message](../dev-git-commit-message/SKILL.md).

## Workflow

1. Identify constraints: concurrently open branches (not headcount), release cadence and number of supported versions, CI duration and default-branch failure rate, contributor model (shared push vs forks), compliance or audit requirements.
2. Choose the simplest branching model that fits (table below).
3. Set the repository baseline: rulesets, approvals, required checks, one merge method, CODEOWNERS, release and tag rules.
4. Define the local loop for humans and agents, including the safety preflight.
5. Implement with the references and templates rather than improvising repo policy.

## Branching Choice

| Situation | Default |
|-----------|---------|
| one production line, frequent deploys | GitHub Flow |
| high merge concurrency, fast and stable CI, main must stay green | trunk-based plus merge queue |
| incomplete work must merge early | trunk-based plus feature flags |
| one supported version with scheduled releases | GitHub Flow or trunk-based with release tags |
| several supported versions or long stabilization | release branches cut from main (GitFlow only if a separate integration branch pays for itself) |

Trunk-based development needs CI that answers fast (roughly under 10 minutes) and a default branch that is rarely red (roughly under 5% of builds failing); treat both as heuristics to calibrate locally, not standards.

Headcount is a proxy for merge concurrency, not the real variable:

- **Agent-heavy teams.** Five humans running ten parallel agent worktrees have the merge concurrency of a much larger team. Size the model and the merge-queue decision to the number of concurrently open branches.
- **Fork-based open source.** Trunk-based development assumes push access. For fork-and-PR contribution, use GitHub Flow and count only core maintainers as "the team".
- **Regulated or audited work.** Signed commits, mandatory independent approval, and an immutable trail are often the binding constraint. A four-person regulated team may need stricter rulesets than a forty-person SaaS team.
- **Distributed, async teams.** Same-day review cannot be assumed. Favor draft PRs, auto-merge on required checks, and stacked PRs over strict branch-age limits.

## Merge Method

Pick one method per repository and enforce it in the ruleset's allowed merge methods. Mixed methods make `git log`, bisect, and revert behave differently from PR to PR.

| Method | Choose when | Costs |
|--------|-------------|-------|
| Squash | small PRs; commits inside a PR are not individually meaningful | one revertable unit per PR, but intermediate history is lost; the PR title becomes the commit subject, so enforce the convention on PR titles; squashing the base of a stack orphans the descendants' copies of its commits |
| Rebase-merge | authors curate commits and every commit builds and passes tests | linear and bisectable, but the landed SHAs differ from the SHAs CI and reviewers saw; check the host's docs on how rebase-merge treats commit signatures before combining it with required signed commits |
| Merge commit | release branches, back-merges, long-lived integration branches, or when the exact tested SHAs must be preserved | noisier history; use `--first-parent` in log and bisect |

Release-branch back-merges and forward-ports use merge commits or `cherry-pick -x` regardless of the repository's PR method.

## Merge Queue

Adopt a merge queue (GitHub) or merge train (GitLab) when PRs regularly need more than one "update branch" cycle before landing, or when main breaks from semantic conflicts between individually green PRs. Below that, "require branch up to date" plus auto-merge is simpler.

- Throughput ceiling ≈ build concurrency × average group size ÷ CI duration. With 25-minute CI and one PR per build, a serial queue lands about 2.4 PRs an hour; if the team opens more than that, raise concurrency or group size, or cut CI time first.
- Larger groups cut CI runs, but one failure invalidates the group and forces re-tests; flaky tests are the main throughput killer, so fix or quarantine them before enabling the queue.
- Every required check must also run on the queue's event (`merge_group` on GitHub Actions; the queue's temporary branches on third-party CI). A required workflow with path filters that never runs for a queue entry blocks the queue.
- Required checks are matched by name: renaming a CI job leaves the old required check pending forever.

## Protected Branches and Rulesets

- Use rulesets where the host offers them: several can layer on one branch and they can be defined org-wide. Migrate classic branch protection when you next touch the policy.
- Require PRs into protected branches, approval by someone other than the author, dismissal of stale approvals on new pushes, CODEOWNERS review for sensitive paths, and required status checks.
- Block force-push and deletion on `main`, release branches, and release tags. Keep the bypass list short, named, and audited; an emergency bypass still gets post-merge CI and review.
- Turn on secret scanning with push protection where available.
- Two agents on one account are not two reviewers. In solo-account repos, document the allowed merge path explicitly (second reviewer account, required approvals off with manual review, or an intentional admin bypass).

## Release and Hotfix Flow

- Tag releases from main (or from the release branch that ships them). Protect release tags.
- **Upstream first:** land the fix on main, then `cherry-pick -x` it to each supported release branch. A fix applied only to a release branch returns as a regression in the next release.
- If main has diverged so far that the fix cannot land there first, fix the release branch and open a tracked forward-port PR immediately.
- Hotfix under GitHub Flow: branch from main, expedited review, full CI. If main holds unreleased work you cannot ship, branch from the release tag instead.
- Versioning scheme, release triggers, and rollback are in [references/release-management.md](references/release-management.md).

## Local Safety Preflight

Before checkout, merge, rebase, amend, reset, or push:

1. Check for a dirty tree with `git status --porcelain`. Decide explicitly: commit, move the work to its own worktree, or stop. Never `git stash` in a tree other agents share: it sweeps every agent's uncommitted changes, and `refs/stash` is shared by all worktrees.
2. If `.git/index.lock` exists, confirm no Git process is running before removing it.
3. On conflicts, stop new edits, resolve file by file, rerun the relevant tests, then continue.
4. Stage only intended files in agent-driven work.
5. In multi-repo or long-lived shells, do not rely on the shell's `cwd`: use `git -C <path>` for mutations, and verify the target with `git -C <path> rev-parse --show-toplevel` and `branch --show-current` first. If a mutation hits the wrong repo or branch, stop and inspect before any recovery.

### History-Rewrite Risk Judgment

Risk depends on who else depends on the ref, not on the command:

- **Safe by default:** a branch only you or one agent has pushed, before a PR exists.
- **Check first:** a branch with an open PR that carries reviews or approvals. Force-push (even `--force-with-lease`) dismisses approvals in most configurations, and re-review often costs more than the cleanup was worth. Check review state (`gh pr view --json reviews,reviewDecision`); if approvals exist, add a commit instead of rewriting. Give reviewers `git range-diff` output when a rewrite is unavoidable.
- **Never without an explicit, communicated exception:** `main`, `develop`, release branches, release tags, or any branch other people or agents build on.
- **Secrets in history:** rotate the credential first; that closes the exposure. Rewrite only if still needed, with `git filter-repo` (Git's own docs deprecate `filter-branch`). Clones, forks, and host-side PR refs keep the old objects, so rotation is never optional.
- **Agent failure mode:** an agent "cleaning up" its history can destroy a human's push made since the agent's last fetch. Require `--force-with-lease` against the remote tip the agent recorded, and treat a lease rejection as a stop condition: fetch, inspect, involve a human. Never retry with bare `--force`.

The handoff for an authorized rewrite records the old tip, new tip, branch, affected dependent branches or PRs, and the command collaborators run to realign.

## Agent-Authored Work

- Keep agent commits distinguishable. Only a dedicated bot author identity changes `git log --author` and blame; a `Co-authored-by:` or `Assisted-by:` trailer does not. Whether to add an AI trailer, and which one, follows the repo's policy and [dev-git-commit-message](../dev-git-commit-message/SKILL.md). Never commit under a human identity without that person's knowledge.
- Sign agent commits whenever the repo requires signed commits; an agent identity is no exemption.
- An agent's summary of its change is not review, and its "tests pass" is not verified until the repo's real gate has run. Require human review of agent PRs; an AI reviewer can comment but does not count as an approver.
- Never let an agent approve or merge its own PR.
- One agent, one worktree, one branch. A shared working tree between agents produces commits that silently overwrite each other's intent.

Rule: `rules/common/git.md` loads this invariant in every coding session.

### Worktree-First Loop and Repo-Local Contract

1. Create one worktree per feature or agent (confirm its directory is ignored).
2. Verify dependencies and baseline tests in that worktree before editing.
3. Keep edits inside the assigned files.
4. Run the repository gate from the worktree before opening the PR.
5. Merge through the repo's policy; remove the worktree and delete the branch after merge.

When a user wants this loop in a real repo, standardize it in repo-local scripts (`start <slug>`, `gate`, `pr`, `finish <slug>`), record the exact commands and the review/merge policy in `AGENTS.md`, and use one shared slug and one PR per repo for multi-repo features, merging the contract-owning repo first. Full contract, multi-repo session command, env-override pattern, and validation steps: [references/ai-agent-worktrees.md](references/ai-agent-worktrees.md#repo-local-delivery-contract).

## Failure Modes

- Choosing a branching model from ideology instead of release-support burden, merge concurrency, and CI capability.
- Long-lived branches without a release reason; environment branches (`dev`/`staging`/`prod`) that drift instead of promoting one build artifact.
- Enabling a merge queue while required checks are flaky, path-filtered, or slow; the queue amplifies all three.
- Rebasing or force-pushing during active review without an agreed policy, losing reviewer context and approval state.
- Stacking changes whose dependency order is unclear; independent changes belong in parallel PRs.
- Worktrees and stacks without repo-local scripts, leaving cleanup and verification inconsistent; automation that assumes fixed sibling paths.
- Skipping CI or review "to merge faster"; the bypass becomes the process.

## Navigation

- [references/branching-strategies.md](references/branching-strategies.md): model selection, hotfix paths per model, migrations
- [references/pr-best-practices.md](references/pr-best-practices.md): PR sizing, description contract, review etiquette, merge-method details
- [references/stacked-diffs-guide.md](references/stacked-diffs-guide.md): when to stack, tool choice, squash-merge recovery, merge order
- [references/automated-quality-gates.md](references/automated-quality-gates.md): required checks, merge queue and merge train settings, emergency bypass
- [references/release-management.md](references/release-management.md): versioning scheme, release triggers, hotfix, rollback
- [references/ai-agent-worktrees.md](references/ai-agent-worktrees.md): worktree setup, parallel agents, cleanup, repo-local delivery contract
- [references/interactive-rebase-guide.md](references/interactive-rebase-guide.md): autosquash, `--update-refs`, range-diff, recovery
- [references/conflict-resolution.md](references/conflict-resolution.md): prevention, resolution traps, rerere, undoing merges
- [references/git-bisect-debugging.md](references/git-bisect-debugging.md): automated bisect, exit codes, first-parent
- [references/git-hooks-automation.md](references/git-hooks-automation.md): hook managers, pre-push exact-tip checks, bypass policy
- [references/monorepo-workflows.md](references/monorepo-workflows.md): partial clone, sparse checkout, CODEOWNERS, affected-only CI
- [references/validation-checklists.md](references/validation-checklists.md): pre-PR, pre-merge, hotfix, rebase, stack, release checklists
- [references/common-mistakes.md](references/common-mistakes.md): mistake-to-fix index
- [references/commit-conventions.md](references/commit-conventions.md): pointer to dev-git-commit-message, plus atomic commits and templates
- Assets: [PR template](assets/pull-requests/pr-template.md), [workflow guide template](assets/template-git-workflow-guide.md), [release workflow template](assets/releases/release-workflow.md), [GitHub checks](assets/ci-cd/github-pr-checks.yml), [GitLab checks](assets/ci-cd/gitlab-mr-checks.yml)
- [data/sources.json](data/sources.json)

Related skills: [software-code-review](../software-code-review/SKILL.md), [qa-debugging](../qa-debugging/SKILL.md), [ops-devops-platform](../ops-devops-platform/SKILL.md), [qa-testing-strategy](../qa-testing-strategy/SKILL.md), [docs-codebase](../docs-codebase/SKILL.md), [dev-git-commit-message](../dev-git-commit-message/SKILL.md), [ai-coding-agents](../ai-coding-agents/SKILL.md).

## Lookups

- Verify platform feature status (stacked PRs, merge-queue settings, ruleset options) in the platform's own docs and changelog before presenting it; prefer those and git-scm.com over blogs.
- Verify Git feature availability in the release notes for the user's installed version; label experimental commands as experimental.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
