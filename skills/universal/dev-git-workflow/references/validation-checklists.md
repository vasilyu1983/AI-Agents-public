# Git Workflow Validation Checklists

Short, Git-specific checklists for the moments where workflow mistakes happen. Code-review content checks belong to [software-code-review](../../software-code-review/SKILL.md); release-day and post-deploy checks are in [release-management.md](release-management.md#release-checklist).

## Contents

- [Before Opening a PR](#before-opening-a-pr)
- [Before Merging](#before-merging)
- [Before Rewriting History](#before-rewriting-history)
- [Stacked PRs](#stacked-prs)
- [Hotfix](#hotfix)
- [Release Branch](#release-branch)
- [Agent Handoff](#agent-handoff)

## Before Opening a PR

- [ ] Branch starts from a freshly fetched target branch; if it is older than a day or two, updated and retested
- [ ] One concern per PR; behavior-preserving refactors split from behavior changes ([pr-best-practices.md](pr-best-practices.md#sizing))
- [ ] The repo's local gate passes on the exact commit being pushed
- [ ] Commits follow the repo's convention; if the repo squash-merges, the PR title does ([dev-git-commit-message](../../dev-git-commit-message/SKILL.md))
- [ ] Only intended files are in the diff (`git diff --stat origin/main...HEAD`); no generated, local-config, or secret files
- [ ] Description answers what/why, risk, verification, rollout/rollback, and where to look ([pr-best-practices.md](pr-best-practices.md#description-contract))

## Before Merging

- [ ] Approved by someone other than the author (for agent-authored PRs, a human), and approvals are not stale
- [ ] All required checks green on the current head, or the PR is in the merge queue
- [ ] Every `blocker:` comment resolved; open questions answered
- [ ] The repo's single merge method is used; for squash, the final title and body are edited into a good commit message
- [ ] Migrations, flags, and config needed for rollout are in place, and rollback is written down
- [ ] Dependent PRs (stack children, other repos in the same feature) know the merge order

## Before Rewriting History

- [ ] The branch is yours alone, or every collaborator agreed (SKILL.md History-Rewrite Risk Judgment)
- [ ] Review state checked; if approvals exist, add commits instead
- [ ] Old tip SHA recorded (`git rev-parse HEAD`) or a backup branch created
- [ ] Working tree clean; no stash in a tree shared with other agents
- [ ] After the rewrite: tests rerun, `git range-diff` shared with reviewers, push with `--force-with-lease=<branch>:<old-remote-sha>`

## Stacked PRs

- [ ] Each layer is independently reviewable and passes CI on its own
- [ ] The dependency order is real; independent changes are parallel PRs, not a stack
- [ ] Each PR states its position in the stack and its base
- [ ] After a lower layer merges (especially by squash), the next layer is rebased with `--onto` and retargeted to main ([stacked-diffs-guide.md](stacked-diffs-guide.md))

## Hotfix

- [ ] Severity justifies the fast path; the fix is minimal with a regression test
- [ ] Fix lands on main first, then `cherry-pick -x` to each supported release branch (or the forward-port PR is opened immediately)
- [ ] Required checks run; any review bypass is recorded with a follow-up review ([automated-quality-gates.md](automated-quality-gates.md#emergency-bypass))
- [ ] Released through the normal tag and publish path; version bumped
- [ ] GitFlow repos: back-merged into `develop` and any open `release/*` the same day

## Release Branch

- [ ] Cut from a commit that passed the full pipeline; branch protected like main
- [ ] Only fixes enter the branch, each landed upstream first
- [ ] Release tag created by the release process on the tested commit
- [ ] After the release, fixes made on the branch are confirmed present on main (`git cherry -v main release/x.y` lists commits missing upstream)

## Agent Handoff

- [ ] Assigned worktree, branch, owned paths, and do-not-touch paths are stated
- [ ] The agent's Git target was verified before any mutation (`git -C <path> rev-parse --show-toplevel`, `branch --show-current`)
- [ ] The agent's claimed test results are backed by the repo gate's actual output
- [ ] Any history rewrite is reported with old tip, new tip, and affected branches
