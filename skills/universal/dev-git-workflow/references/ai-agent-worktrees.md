# AI Agent Worktrees

Isolating parallel agents (and agents working next to a human) with `git worktree`: one actor per worktree. A manually managed worktree gets its own branch; a native agent worktree may begin detached and needs a branch before a PR. How a specific coding agent creates worktrees changes between releases and is owned by [ai-coding-agents](../../ai-coding-agents/SKILL.md); orchestration and handoffs are owned by [agents-subagents](../../agents-subagents/SKILL.md). This file covers the Git policy shared by those tools.

## Contents

- [When to Use a Worktree](#when-to-use-a-worktree)
- [Placement](#placement)
- [Native Agent Worktrees](#native-agent-worktrees)
- [Creating a Worktree](#creating-a-worktree)
- [Parallel Agents](#parallel-agents)
- [Shared-Repository Hazards](#shared-repository-hazards)
- [Cleanup](#cleanup)
- [Repo-Local Delivery Contract](#repo-local-delivery-contract)
- [Anti-Patterns](#anti-patterns)

## When to Use a Worktree

| Situation | Worktree? |
|-----------|-----------|
| More than one actor (agents, or an agent and a human) edits the repo at the same time | Required: one per actor |
| One agent, human not working in the repo | Optional; a branch checkout is fine |
| Agent runs in its own remote or cloud sandbox | Not for the agent itself; create one locally to review or test its branch |
| Local CI or long builds run while you develop | Yes, so builds do not see half-edited files |

The core reason is that a working tree and index belong to whoever is using them. Two actors in one checkout overwrite each other's edits, stage each other's files, and `git stash` sweeps up everyone's uncommitted work at once. Do not use `git stash` in a tree shared with other agents; commit, move the work to its own worktree, or stop.

## Placement

For a manually created worktree, default to a project-local, ignored directory, `.worktrees/<slug>`, with branch `feature/<slug>`. A tool-managed worktree follows its tool's documented location and branch behavior.

1. If the repo already has a worktree directory or documents one in `AGENTS.md`/`CLAUDE.md`, use it.
2. Otherwise use `.worktrees/` and confirm it is ignored before creating anything: `git check-ignore -q .worktrees/x || echo "add .worktrees/ to .gitignore"`. An unignored worktree directory shows up as untracked files, and `git add .` stages the whole nested checkout.
3. Use a directory outside the repo (for example `../<repo>-worktrees/<slug>`) only when you cannot change `.gitignore`.

Run the manual setup below from the main checkout so the paths resolve as shown.

## Native Agent Worktrees

- Claude Code supports `claude --worktree <name>` for a session (under `.claude/worktrees/` by default) and `isolation: worktree` for a custom subagent. Ignore its worktree directory and check the installed version's [worktree documentation](https://code.claude.com/docs/en/worktrees) before relying on path or cleanup behavior.
- The Codex desktop app can start a chat in a managed worktree. Its [worktree documentation](https://learn.chatgpt.com/docs/environments/git-worktrees) says these start at detached HEAD; use its **Create branch here** action before publishing a PR, or use **Handoff** to move the chat to the local checkout. Do not apply the manual `-b` creation recipe to a Codex-managed worktree.
- Native isolation separates files, but refs and repository metadata remain shared. Assign disjoint files and leave integration to the owner; check each tool's current worktree docs before writing repo-local automation around its directory layout.

## Creating a Worktree

```bash
git fetch origin
git worktree add --no-track -b feature/auth .worktrees/auth origin/main   # new branch from fresh main; no upstream to main
git -C .worktrees/auth push -u origin feature/auth                       # set the branch's own upstream on first push
git worktree add --track -b feature/auth .worktrees/auth origin/feature/auth   # existing remote branch
```

`git worktree add .worktrees/auth origin/feature/auth` without `-b` checks out a detached HEAD; commits made there belong to no branch and are easy to lose.

Before the agent edits anything:

- Install dependencies in the worktree (dependency directories such as `node_modules` or virtual environments are per worktree).
- Run the baseline tests. If they fail before any change, report that first; otherwise the agent's work will be blamed for a pre-existing failure.
- Check that local config the build needs (`.env` files, generated code) exists; untracked files do not come with the worktree.

## Parallel Agents

- **One worktree per actor.** Manually managed agent worktrees use separate branches. A tool-managed detached worktree is valid while work is in progress; create a branch or hand off before publishing, following that tool's documented flow. Git refuses to check out the same branch in two worktrees.
- **Disjoint file ownership in every handoff:** the owned paths, the do-not-touch paths, and the worktree path. When two agents must change the same file, run them in sequence, not in parallel.
- **The orchestrator stays in the main checkout** and reviews, integrates, and resolves conflicts; subagents do not resolve conflicts in files they do not own.
- **Check overlap before integrating.** Use three-dot diffs so each branch is compared with its merge base, not with the current tip of main:

  ```bash
  comm -12 <(git diff --name-only main...feature/auth | sort) \
           <(git diff --name-only main...feature/payments | sort)
  ```

- **Integrate upstream-first.** Merge the branch others depend on (schema, contract, shared library) first, then rebase or update the dependents and rerun their tests after each merge.

## Shared-Repository Hazards

All worktrees share one object database and one set of refs.

| Operation | Safe while agents are active? |
|-----------|-------------------------------|
| commits, staging, checkouts inside a worktree | Yes (each worktree has its own index and HEAD) |
| `git fetch` | Yes |
| `git gc`, `git prune`, `git worktree prune`, `git worktree add/remove` | Serialize: run only from the orchestrator when no agent is mid-operation |
| `git stash`, `git reset --hard`, `git checkout -- .`, `git clean` | Never across worktrees; stash is repo-wide, and the others destroy uncommitted work |
| force-pushing a branch another agent builds on | Never |

Before any history or state mutation (amend, reset, rebase, push), an agent verifies its target: `git rev-parse --show-toplevel` and `git branch --show-current` match the assignment, and it uses explicit paths (`git add -- <paths>`), never `git add -A` in a shared repo.

## Cleanup

After the PR merges:

```bash
git worktree remove .worktrees/auth        # refuses if the worktree has uncommitted changes; do not force
git branch -d feature/auth                 # -d refuses unmerged branches; see note on squash merges
git worktree prune                         # only needed if a worktree directory was deleted by hand
git worktree list                          # confirm only active worktrees remain
```

- **Squash and rebase merges defeat `git branch --merged` and `git branch -d`.** The branch's own commits never reach main, so Git reports the branch as unmerged. Decide what is merged from the host's PR state (for example the PR is closed as merged, and the branch has no commits pushed after the merge), then delete with `git branch -D`.
- Some Git releases offer `git branch --delete-merged` for branches merged into their tracked upstream. Check the installed `git branch --help` before using it; it does not replace the host PR-state check after a squash or rebase merge ([release notes](https://github.com/git/git/blob/master/Documentation/RelNotes/2.56.0.adoc)).
- Never auto-remove a worktree that has uncommitted or unpushed work; report it instead.
- Delete remote branches through the host's "delete branch on merge" setting rather than by script.

## Repo-Local Delivery Contract

When a user wants the worktree-first loop built into a real repository, standardize the repo around it instead of relying on each agent to improvise.

**Contract:**

- No feature work directly on `dev` or `main`. Worktrees live at `.worktrees/<slug>` on branch `feature/<slug>`.
- A feature that touches several repos uses the same slug in every repo and one PR per repo, kept in draft until every touched repo passes its gate. Merge the repo that owns the contract (API, schema) first, then update and merge dependents.
- Run the repo gate from the worktree before opening the PR; the gate is defined as the repo's real pre-merge checks.
- When branch protection requires approvals, the approver is a different user from the PR author. Two agents operating under one account are not independent reviewers. A solo-account repo documents its merge path explicitly: a second reviewer account, required approvals off with manual human review, or an intentional, audited admin bypass.

**Implementation:**

- One repo-local script (for example `scripts/git/feature-workflow.sh`) exposing `start <slug>`, `gate`, `pr --title "..."`, and `finish <slug>`.
- `AGENTS.md` records the exact commands, the review and merge policy (including reviewer-identity rules), and the Git safety rule: explicit-path Git mutations, and target verification before amend, reset, rebase, or push.
- Scripts that assume fixed sibling-repo paths accept an environment override first and fall back to the old path:

  ```bash
  DEFAULT_OTHER_REPO_DIR="$(cd "$ROOT_DIR/.." && pwd)/other-repo"
  OTHER_REPO_DIR="${OTHER_REPO_DIR_ENV:-$DEFAULT_OTHER_REPO_DIR}"
  ```

**Multi-repo verification loop:** pick one slug; create one worktree per touched repo; export each worktree path for integration scripts; start backend or shared services from the matching worktree, never from `dev`; run each repo's gate from its own worktree.

**Portfolio session command.** When the same multi-repo flow repeats, add one thin orchestrator above the per-repo scripts (for example `scripts/git/feature-session.sh` with `start <slug> --repos a,b`, `dev`, `test --level repo-gate|integration|full`, `pr`, `finish`, and state in `.feature-sessions/<slug>.env`). It calls the per-repo scripts rather than reimplementing branch and PR logic. It automates mechanics (create worktrees, save state, run gates, start services, open draft PRs), not judgment: it never merges automatically, deletes dirty worktrees, or hides failing checks. When such a command exists, agents use it instead of replaying the steps by hand.

**Minimum validation of the scripts:** `bash -n` on every changed shell script, new scripts marked executable, every command in `AGENTS.md` run from the path it documents, and `git status --short` inspected in every touched repo.

## Anti-Patterns

| Anti-pattern | Fix |
|--------------|-----|
| Two agents in one worktree | One worktree per agent |
| Worktree directory not ignored | `git check-ignore` before creating |
| Worktree created from a remote branch without `-b` (detached HEAD) | `--track -b <branch>` |
| No file ownership in the handoff | Owned and do-not-touch paths per agent |
| Skipping dependency install and baseline tests | Set up and verify before the first edit |
| Two-dot diffs for overlap checks | Three-dot (`main...branch`) |
| `git gc` or `worktree prune` while agents run | Only from the orchestrator when idle |
| Cleanup script keyed on `git branch --merged` in a squash-merge repo | Use the host's merged-PR state |
| Worktrees left after merge | Remove the worktree and branch as part of `finish` |
