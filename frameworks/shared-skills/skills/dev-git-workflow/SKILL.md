---
name: dev-git-workflow
description: "Designs team Git workflows for branching, PRs, and releases. Use when choosing branching models, stacked PRs, merge queues, worktree isolation for agents, or collaboration rules."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# Git Workflow

Use this skill to choose a team Git model, define PR discipline, standardize commit and release rules, and set safe defaults for human and AI-assisted collaboration.

Bias toward modern delivery: GitHub Flow or trunk-based development for most teams, merge queues for busy repositories, worktrees for agent isolation, and release branches only when version support actually requires them. Git 2.55 (June 2026) is the current stable release; verify latest at git-scm.com. GitHub native stacked PRs (`gh stack`) remain private-preview and waitlist-gated as of this writing (entered preview April 2026, no GA date announced) — verify current status before recommending it as a default over Graphite, ghstack, or manual stacking.

## Quick Reference

| Need | Default | Reference |
|------|---------|-----------|
| Pick a branching model | GitHub Flow for most teams; trunk-based for high-concurrency teams | [references/branching-strategies.md](references/branching-strategies.md) |
| Run parallel agent or feature work safely | one worktree per branch or agent | [references/ai-agent-worktrees.md](references/ai-agent-worktrees.md) |
| Implement repo-local agent delivery | standardize `start` / `gate` / `pr` / `finish` plus worktree-safe scripts | this skill, [references/ai-agent-worktrees.md](references/ai-agent-worktrees.md) |
| Keep PRs reviewable | small focused PRs or stacked diffs | [references/pr-best-practices.md](references/pr-best-practices.md), [references/stacked-diffs-guide.md](references/stacked-diffs-guide.md) |
| Standardize commits and releases | Conventional Commits plus automated release tooling | [references/commit-conventions.md](references/commit-conventions.md), [references/release-management.md](references/release-management.md) |
| Keep merge safety high | required checks, approvals, rulesets, merge queue | [references/automated-quality-gates.md](references/automated-quality-gates.md) |
| Debug bad merges or regressions | conflict discipline, rebase hygiene, bisect | [references/conflict-resolution.md](references/conflict-resolution.md), [references/git-bisect-debugging.md](references/git-bisect-debugging.md) |

## When to Use This Skill

Use this skill when the main question is about:

- branching strategy selection
- PR sizing, review rules, and merge policy
- merge queue, ruleset, or branch protection design
- stacked diffs and history cleanup
- worktree-based collaboration for multiple agents or parallel streams
- standardizing repos on a `start` / `gate` / `pr` / `finish` delivery loop
- release workflow and commit conventions

Route elsewhere when the main task is:

- code review of a specific change set
- CI/CD or platform design beyond Git workflow
- debugging a product issue rather than the collaboration process

## Defaults

- GitHub Flow is the default for most small and medium teams shipping one production line.
- Trunk-based development is the default when concurrency is high and CI runs in under 10 minutes with a failure rate low enough that main stays green (target: < 5% build failures on the default branch).
- Use release branches or GitFlow-style stabilization only when multiple supported versions or heavy scheduled releases justify the overhead.
- Use one worktree per agent or parallel feature branch.
- Prefer explicit staging in dirty worktrees.
- Prefer `--force-with-lease` over `--force`.
- Treat current hosting-platform features and workflow advice as volatile and verify when users ask for the latest best practice.

## Workflow

1. Identify constraints:
   - team size and merge concurrency
   - release cadence and version-support burden
   - CI strength and branch protection maturity
   - compliance or audit expectations
2. Choose the simplest branching model that fits those constraints.
3. Set the repository baseline: approvals, required checks, merge strategy, CODEOWNERS, release rules.
4. Define the local loop for contributors and agents.
5. Use references and templates to implement the chosen pattern rather than improvising repo policy from scratch.

## ASCII Flow

```text
Git workflow request
  -> identify team, concurrency, release, CI, and audit constraints
  -> choose branching model: GitHub Flow, trunk-based, release branches, or GitFlow
  -> set repo baseline: checks, approvals, CODEOWNERS, merge queue, release rules
  -> define local loop
     +-- human work -> branch, commit, PR, review, merge
     +-- agent work -> worktree, scoped files, gate, PR, cleanup
  -> apply safety preflight before checkout, merge, rebase, amend, reset, or push
  -> document exact repo-local commands and verification gates
```

## Branching Choice

| Situation | Default |
|-----------|---------|
| small or medium team, single production line, frequent deploys | GitHub Flow |
| larger team, high merge concurrency, strong CI, default branch must stay green | trunk-based plus merge queue |
| incomplete work must merge early | trunk-based plus feature flags |
| one supported version with scheduled releases | GitHub Flow or trunk-based with release tags |
| multiple supported versions or long stabilization cycles | release branches or GitFlow-style structure |

### Judgment Beyond Team Size

Headcount is a proxy for merge concurrency, not the real variable. Look past it in these cases:

- **Agent-heavy teams.** A team of 5 humans running 10 parallel coding-agent worktrees has the merge concurrency of a much larger team, even though headcount looks small. Size the branching model and merge-queue decision to the number of concurrently open branches, not the number of people. Bias toward trunk-based plus feature flags once agent-driven concurrency pushes past what GitHub Flow's simple protected-main model can absorb.
- **Open-source or many-outside-contributor repos.** Trunk-based development assumes push access to a shared repo; it does not fit fork-and-PR contribution models regardless of core-team size. Default to GitHub Flow with fork-based PRs, and treat "team size" as core maintainers only.
- **Regulated or audited environments.** Compliance burden (signed commits, mandatory approvals, immutable audit trail) is often the load-bearing constraint, not team size or release cadence. A 4-person team in a regulated environment may need GitFlow-grade rigor (or trunk-based with stricter rulesets) that a 4-person SaaS team would never require.
- **Distributed, async-heavy teams.** When reviewers span time zones with little overlap, a model that assumes same-day review turnaround (short-lived trunk-based branches) creates idle-branch friction. Favor draft PRs, generous auto-merge on required checks, and stacked diffs over strict branch-age limits.

## Local Safety Preflight

Before checkout, merge, or rebase:

1. check for a dirty worktree with `git status --porcelain`
2. decide explicitly whether to commit, stash, or stop
3. if `.git/index.lock` exists, confirm no active Git process before removing stale locks
4. on conflicts, stop new edits, resolve file-by-file, rerun the relevant tests, then continue
5. in agent-driven workflows, stage only the intended files

For multi-repo or long-lived shell sessions:

1. do not rely on persisted shell `cwd` for Git mutation commands
2. prefer `git -C <explicit-repo-or-worktree-path> ...` for `commit`, `commit --amend`, `reset`, `rebase`, `merge`, `cherry-pick`, `checkout`, `branch`, `push`, `stash`, `tag`, and `worktree` mutations
3. before `commit --amend`, `reset`, `rebase`, `merge`, or `push`, verify the target with `git -C <path> rev-parse --show-toplevel` and `git -C <path> branch --show-current`
4. if a mutation hits the wrong repo or branch, stop and inspect before recovery; do not improvise a destructive fix until the exact state is verified

### History-Rewrite Risk Judgment

Rebase and force-push are not inherently dangerous — the risk is a function of who else depends on the ref, not which command runs:

- **Safe by default:** rebasing a branch only you or one agent has ever pushed, before a PR exists, or inside a worktree no one else reads.
- **Needs a check first:** rebasing a branch with an open PR that already carries review comments or approvals. Force-push (even `--force-with-lease`) dismisses approvals on most platform configurations, and re-review often costs more than the history cleanup was worth. Check the PR's review state (for example `gh pr view --json reviews,reviewDecision`) before rewriting; if approvals exist, prefer a merge commit or a new commit over a rewrite.
- **Never without an explicit, communicated exception:** rewriting `main`, `develop`, a release branch, or any branch other people or other agents are actively building on.
- **Secrets in history:** rotate the exposed credential first — that closes the actual exposure immediately. Only then decide whether a history rewrite is worth the disruption; for large or shared repos, rotation alone is often sufficient and a rewrite is unnecessary collateral damage. If a rewrite is still needed, use `git filter-repo`, not `git filter-branch` — the Git project's own docs deprecate `filter-branch` for correctness and performance reasons and point to `filter-repo` as the replacement.
- **Agent-specific failure mode:** an agent "cleaning up" its own commit history can silently destroy a human's edit pushed to the same branch between the agent's last fetch and its push. Require `--force-with-lease` (never bare `--force`) for any agent-initiated force-push, and treat a lease rejection as a stop condition — fetch, inspect what changed, and involve a human rather than retrying with `--force`.

## Agent-Authored Commit Hygiene

Judgment for commits an agent creates on a human's behalf, distinct from generic commit-message style:

- Attribute agent-authored commits distinctly from the human operator's own commits — a `Co-authored-by:` trailer or a dedicated bot author identity keeps `git log --author` and blame meaningful. Do not let an agent commit under a human identity without that person's knowledge.
- Treat an agent's own commit as a draft until a human has reviewed the actual diff. An agent's summary of its own change is not a substitute for review, and an agent's internal "tests pass" claim is not verified until the repo's real gate has run.
- Never let an agent approve or merge its own PR, and never treat two agent-controlled accounts as independent reviewers for branch-protection purposes — see the Repo-Local Delivery Contract for the documented fallback when a repo runs in solo-account mode.
- Apply the same one-agent-one-worktree-one-branch isolation to agent commits as to human work (see Worktree-First Loop below); a shared working tree between two agents produces commits that silently overwrite each other's intent, not just files.
- Sign agent-authored commits the same way as human commits when the repo requires signed commits or tags — an agent identity is not an exemption from provenance requirements.

## Worktree-First Loop for Agents

Default loop for AI-assisted delivery:

1. create one worktree per feature or agent
2. confirm the worktree path is ignored
3. verify dependencies and baseline tests in that worktree
4. keep ownership scoped to the assigned files
5. run the repository quality gates before PR
6. merge through the repo’s defined policy
7. remove the worktree and delete the branch after merge

Use [references/ai-agent-worktrees.md](references/ai-agent-worktrees.md) for the full setup and cleanup patterns.

## Repo-Local Delivery Contract

When the user wants this workflow implemented in a real repo, do not create a separate delivery skill. Use this skill as the source of truth and standardize the repo around one worktree-first loop.

Default contract for real repos:

- never develop new feature work directly on `dev` or `main`
- create repo-local worktrees under `.worktrees/<feature-slug>`
- use `feature/<feature-slug>` as the branch name
- if several repos participate in one feature, keep the same slug in every repo
- open one PR per repo
- run the repo gate from the worktree before opening the PR
- if the target branch requires approving reviews, require that approval from a different GitHub user than the PR author
- do not treat two agents on the same GitHub account as independent reviewers for branch-protection purposes
- if the repo runs in solo mode with one GitHub account, document the allowed merge path explicitly: second reviewer account, disabled required approvals with manual review, or intentional admin/bypass policy
- merge the contract-owning repo first, then rebase dependents

Implementation defaults:

- add or normalize a repo-local workflow script, usually `scripts/git/feature-workflow.sh`
- expose `start <slug>`, `gate`, `pr --title "..."`, and `finish <slug>`
- update `AGENTS.md` with the exact local commands instead of generic Git advice
- update `AGENTS.md` with the repo's review and merge policy, including reviewer-identity constraints when branch protection requires approvals
- update `AGENTS.md` with a multi-repo Git safety rule: explicit-path Git mutations and mandatory target verification before amend/reset/rebase/push
- define `gate` in terms of the repo's real pre-merge checks
- patch local scripts that assume fixed sibling paths so they accept env overrides first and fall back to the old path second

Use this env-override pattern for cross-repo local scripts:

```bash
DEFAULT_OTHER_REPO_DIR="$(cd "$ROOT_DIR/.." && pwd)/other-repo"
OTHER_REPO_DIR="${OTHER_REPO_DIR_ENV:-$DEFAULT_OTHER_REPO_DIR}"
```

For multi-repo features, document the worktree verification loop explicitly:

1. pick one shared feature slug
2. create one worktree per touched repo
3. export worktree paths per repo when local integration scripts need sibling repos
4. start backend or shared services from the matching worktree, not from `dev`
5. run each repo gate from its own worktree
6. keep PRs in draft until every touched repo passes

Minimum validation after implementation:

- run `bash -n` on every changed shell script
- ensure new workflow scripts are executable
- confirm `AGENTS.md` commands are valid from the worktree path they document
- inspect `git status --short` in every touched repo

## Portfolio Session Command

When a repo set needs the same multi-repo flow repeatedly, keep the repo-local `feature-workflow.sh` scripts as the primitives and add one thin portfolio orchestrator above them.

Default contract:

- add a portfolio-level command such as `scripts/git/feature-session.sh`
- keep it stateful per feature slug, for example `.feature-sessions/<slug>.env`
- make it call the repo-local workflow scripts instead of reimplementing branch and PR logic differently
- prefer these subcommands:
  - `start <slug> --repos <repo1,repo2,...>`
  - `dev <slug>`
  - `test <slug> --level repo-gate|integration|full`
  - `pr <slug> --title "..."`
  - `finish <slug>`
- wire sibling repos through env overrides instead of hardcoded relative assumptions
- make the skill tell the agent to invoke the portfolio command when it exists, rather than manually replaying the same steps repo by repo

The portfolio command should automate mechanics, not judgment:

- yes: create worktrees, save session state, run gates, start local services, open draft PRs
- no: merge automatically, delete dirty worktrees, or hide failing checks

### Example: Backend + iOS Feature

> **Note:** Replace placeholder paths with your repo locations.

Use a concrete same-slug flow when an iOS client depends on backend changes.

Given:

- repo A: `<backend-repo>`
- repo B: `<ios-repo>`
- slug: `onboarding-paywall`

If the repo set already provides a portfolio session command, prefer it:

```bash
bash ./scripts/git/feature-session.sh start onboarding-paywall --repos <backend-repo>,<ios-repo>
bash ./scripts/git/feature-session.sh dev onboarding-paywall
bash ./scripts/git/feature-session.sh test onboarding-paywall --level full
bash ./scripts/git/feature-session.sh pr onboarding-paywall --title "feat: onboarding paywall"
bash ./scripts/git/feature-session.sh finish onboarding-paywall
```

Under the hood that command should still delegate to each repo's local `feature-workflow.sh`.

Create matching worktrees:

```bash
cd ~/Projects/<your-product>/<backend-repo>
./scripts/git/feature-workflow.sh start onboarding-paywall

cd ~/Projects/<your-product>/<ios-repo>
./scripts/git/feature-workflow.sh start onboarding-paywall
```

Export paths once so every local command targets the correct worktree:

```bash
export SLUG=onboarding-paywall
export BACKEND_WT=~/Projects/<your-product>/<backend-repo>/.worktrees/$SLUG
export IOS_WT=~/Projects/<your-product>/<ios-repo>/.worktrees/$SLUG
```

Run backend and iOS integration from those worktrees, not from `dev`:

```bash
cd "$BACKEND_WT/app"
./tests/dev-server.sh

cd "$IOS_WT"
BACKEND_APP_DIR="$BACKEND_WT/app" bash ./scripts/run-local-ios-dev.sh
```

Run gates and higher-confidence iOS checks from the worktrees:

```bash
cd "$BACKEND_WT"
../../scripts/git/feature-workflow.sh gate

cd "$IOS_WT"
../../scripts/git/feature-workflow.sh gate
bash ./scripts/test-ios.sh ui
```

Then commit and open one PR per repo:

```bash
cd "$BACKEND_WT"
git add -A
git commit -m "feat(paywall): add onboarding paywall backend flow"
../../scripts/git/feature-workflow.sh pr --title "feat: onboarding paywall"

cd "$IOS_WT"
git add -A
git commit -m "feat(paywall): add onboarding paywall screen"
../../scripts/git/feature-workflow.sh pr --title "feat: onboarding paywall"
```

Merge the backend contract repo first, then rebase and merge the iOS repo if it depends on that contract.

## Repository Baseline

Set these defaults before scaling collaboration:

- rulesets for branch and tag safety on GitHub — GitHub is migrating governance from classic protected branches to rulesets (multiple rulesets can apply to the same branch, with org-wide reuse); prefer rulesets for new repos and plan a migration for repos still on classic protected branches only
- required approvals and CODEOWNERS for sensitive paths
- a single documented merge strategy
- signed commits and tags where the team requires stronger provenance
- secret scanning and push protection
- merge queue or merge trains when concurrency is high
- CI cost controls for heavy jobs and untrusted forks

Useful assets:

- [assets/pull-requests/pr-template.md](assets/pull-requests/pr-template.md)
- [assets/template-git-workflow-guide.md](assets/template-git-workflow-guide.md)
- [assets/ci-cd/github-pr-checks.yml](assets/ci-cd/github-pr-checks.yml)
- [assets/ci-cd/gitlab-mr-checks.yml](assets/ci-cd/gitlab-mr-checks.yml)

## Known Traps

- Choosing a branching model from ideology instead of release support burden, merge concurrency, and CI capability.
- Introducing worktrees and stacked branches without repo-local scripts or conventions, which leaves cleanup and verification inconsistent.
- Treating merge queue adoption as enough on its own while required checks, PR sizing, and branch hygiene remain weak.
- Rebasing or force-pushing during active review without an agreed team policy, causing reviewers to lose context or approval state.
- Letting repo-local automation assume fixed sibling paths, which breaks multi-repo worktree setups as soon as someone changes local layout.

## Common Anti-Patterns

- long-lived branches without a release reason
- monolithic PRs that mix unrelated concerns
- rebasing or force-pushing shared public branches
- skipping CI or review to merge faster
- vague commit messages that break release automation
- blanket staging in dirty worktrees
- using stacked diffs when the dependency order is unclear

## Navigation

**Core**

- [references/branching-strategies.md](references/branching-strategies.md) — strategy comparison matrix, GitHub Flow / trunk-based / GitFlow guides, migration paths, team-size recommendations
- [references/pr-best-practices.md](references/pr-best-practices.md) — PR sizing heuristics, description templates, review etiquette, merge strategy decision matrix, metrics targets
- [references/commit-conventions.md](references/commit-conventions.md) — Conventional Commits format, SemVer mapping, commitlint setup, release automation tools
- [references/release-management.md](references/release-management.md) — SemVer, manual/controlled/automated release workflows, hotfix process, changelog standards

**Advanced**

- [references/ai-agent-worktrees.md](references/ai-agent-worktrees.md) — worktree setup/cleanup for Claude Code, Codex, and parallel agents; conflict detection; safety rules; quick command reference
- [references/stacked-diffs-guide.md](references/stacked-diffs-guide.md) — stacked-diff workflow, platform support (GitHub native gh-stack preview, GitLab CLI), Graphite/ghstack/Sapling comparison, best practices
- [references/interactive-rebase-guide.md](references/interactive-rebase-guide.md) — auto-squash workflow, rebase commands, splitting/reordering commits, safe force-push
- [references/conflict-resolution.md](references/conflict-resolution.md) — conflict markers, ours/theirs strategies, rebase vs merge decision, rerere, recovery from mistakes
- [references/git-bisect-debugging.md](references/git-bisect-debugging.md) — manual and automated bisect, test script exit codes, first-parent for merge-heavy repos, integration with debugging workflow

**Automation and repo operations**

- [references/automated-quality-gates.md](references/automated-quality-gates.md) — GitHub Actions merge queue config, GitLab merge trains, quality thresholds, PR status checks
- [references/validation-checklists.md](references/validation-checklists.md) — pre-PR, pre-merge, release, hotfix, and rebase checklists
- [references/git-hooks-automation.md](references/git-hooks-automation.md) — Husky v9, lefthook, lint-staged, commitlint, secrets scanning, branch naming enforcement
- [references/monorepo-workflows.md](references/monorepo-workflows.md) — trunk-based monorepos, sparse checkout, CODEOWNERS per package, affected-only CI with Nx/Turborepo/Bazel
- [references/common-mistakes.md](references/common-mistakes.md) — top-10 anti-patterns with fixes: large PRs, vague commits, public history rewrite, secrets, force push
- [data/sources.json](data/sources.json)

## Related Skills

- [../software-code-review/SKILL.md](../software-code-review/SKILL.md)
- [../qa-debugging/SKILL.md](../qa-debugging/SKILL.md)
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md)
- [../qa-testing-strategy/SKILL.md](../qa-testing-strategy/SKILL.md)
- [../docs-codebase/SKILL.md](../docs-codebase/SKILL.md)
- [../dev-git-commit-message/SKILL.md](../dev-git-commit-message/SKILL.md)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify current GitHub, GitLab, and git-scm guidance when users ask for the latest workflow recommendation.
- Prefer official platform docs and the upstream Git project over blogs and hot takes.
- If live verification is unavailable, mark trend-sensitive guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

