# Stacked Diffs Guide

A stack is a chain of small PRs where each PR targets the branch of the one below it. Stacking pays when review latency, not authoring speed, is the bottleneck: the author keeps building while lower PRs are reviewed and land.

## Contents

- [When to Stack](#when-to-stack)
- [Choosing Tooling](#choosing-tooling)
- [Manual Stacks with Plain Git](#manual-stacks-with-plain-git)
- [After the Base Merges](#after-the-base-merges)
- [Stack Design Rules](#stack-design-rules)
- [Common Scenarios](#common-scenarios)
- [Merge Queue Interplay](#merge-queue-interplay)
- [Measuring Whether Stacking Helps](#measuring-whether-stacking-helps)
- [References](#references)

## When to Stack

Stack when:

- the change has a real dependency order (schema, then API, then UI) and each layer can be reviewed and merged on its own;
- one PR would mix concerns that different reviewers own;
- reviewers typically take longer to respond than the author needs to write the next layer.

Do not stack when:

- the changes are independent: open parallel PRs against main instead, so one blocked PR does not block the others;
- the dependency order is still unclear: every reorder costs a cascade of rebases;
- it is a hotfix: land one focused PR;
- the team has no tooling or convention for retargeting and restacking yet: a half-managed stack is worse than one larger PR.

## Choosing Tooling

Default: use the host's native stacking if it is available on your plan and works with your merge queue; otherwise use a stacking CLI; use manual stacks for occasional two- or three-PR chains.

1. **Native host support.** GitHub offers native stacked PRs (a `gh stack` CLI extension plus stack-aware UI); GitLab offers `glab stack` and stacked merge requests. Both have shipped as preview or experimental features whose availability and merge-queue support change. Before standardizing, check the host's stacked-PR docs and changelog for availability on your plan, whether it lands a whole stack in one merge, and whether it works with your merge queue or merge train.
2. **Stacking CLIs** (Graphite, ghstack, spr, git-branchless, Sapling). They restack automatically and retarget PRs. Choose by the constraint that matters: ghstack and spr map one commit to one PR; Graphite adds a hosted review UI and stack-aware merge queue under a commercial plan; git-branchless and Sapling change the local model more deeply. Check each tool's current maintenance status and pricing before adopting it.
3. **Manual stacks** with `git rebase --update-refs` (below). No new tool, but every retarget is a manual step.

Pick one tool per team. Mixed tooling on one repository leaves stacks that only their author can restack.

## Manual Stacks with Plain Git

```bash
git switch -c feat/cart-01-models main
# commit...
git switch -c feat/cart-02-api
# commit...
git switch -c feat/cart-03-ui
# commit...

# PR targets: 01 -> main, 02 -> 01, 03 -> 02
```

After amending a lower branch, restack everything above it in one rebase from the top branch:

```bash
git switch feat/cart-03-ui
git rebase --update-refs main      # moves 01 and 02 refs along with 03
git push --force-with-lease origin feat/cart-01-models feat/cart-02-api feat/cart-03-ui
```

`--update-refs` (Git 2.38 and later) rewrites every branch ref that points into the rebased range, so the whole stack moves together. Set `rebase.updateRefs=true` to make it the default.

## After the Base Merges

How the base PR merges decides the next step:

- **Merge commit or rebase-merge:** retarget the next PR to main; its branch already contains the base commits unchanged (merge commit) or needs a plain rebase onto main.
- **Squash merge:** main now has one new commit whose content equals the base branch, but the next branch still carries the original base commits. A plain `git rebase main` replays them and conflicts with their own squashed copy. Cut them off instead:

```bash
# old-base = the tip of feat/cart-01-models before it was squash-merged
git rebase --onto origin/main old-base feat/cart-02-api
git push --force-with-lease origin feat/cart-02-api
```

Then retarget the PR to main. Hosts and stacking tools that support stacks do this retargeting for you; manual stacks must do it every time. Record the old base tip before merging so the `--onto` command has an exact argument.

## Stack Design Rules

- **Each PR builds and passes tests on its own.** A PR that only compiles with the next PR is not a layer, it is half a change.
- **Size:** each PR fits one reviewer sitting. The 200-400 changed lines often cited for a single review session are a starting point to tune, not a rule.
- **Depth:** keep stacks short (about five PRs or fewer). Deep stacks multiply restack work and hide the eventual integration risk at the top.
- **Order by dependency and risk:** schema and interfaces first, callers after; put the change most likely to draw review churn low, so it settles before much is built on it.
- **Name for order:** `feat/<topic>-01-<step>`, `feat/<topic>-02-<step>`.
- **Describe the stack in every PR:** position ("2 of 4"), links to the PRs below and above, and what this layer adds. Native tooling renders this; manual stacks need it in the description.
- **Review and merge bottom-up.** Approving a higher PR before the lower one merges is fine; merging it first is not.

## Common Scenarios

| Situation | Response |
|-----------|----------|
| Review changes a lower PR | Commit the fix on the lower branch, restack upward (`--update-refs` or the tool's restack), force-push with lease |
| Lower PR is blocked, upper layers are ready | If the upper layers do not really depend on it, cherry-pick them onto main as an independent PR; if they do, wait or merge behind a feature flag |
| Main moved and the bottom PR conflicts | Rebase the bottom onto `origin/main`, resolve once, restack the rest |
| Need to ship part of a feature | Merge the finished lower layers behind a feature flag; keep the flag off until the top lands |
| A large existing PR should become a stack | Cherry-pick logical commit groups onto a chain of new branches from main; close the original PR with links |

## Merge Queue Interplay

- A queued PR is tested against main plus the PRs ahead of it. A stack whose lower PR is still in the queue can only enter the queue as a unit if the host or tool supports landing stacks; otherwise enqueue bottom-up and let each layer land before the next.
- Squash merges inside a queue produce the squash-merge situation above for every layer: use tooling that restacks automatically, or expect a manual `rebase --onto` per layer.
- Each layer runs CI on its own and again in the queue. Deep stacks with slow CI are expensive; watch queue time before recommending stacking to a whole team.

## Measuring Whether Stacking Helps

Compare against your current workflow instead of assuming gains:

- time to first review and time from first PR opened to last PR merged;
- review rounds per PR;
- restacks and force-pushes per stack;
- CI minutes and queue time per stack;
- revert rate for stacked vs non-stacked changes.

Pilot with a few volunteers before a team-wide rule. If restack work or CI cost rises without faster review, stop.

## References

- GitHub stacked PRs: https://docs.github.com/en/pull-requests/get-started/about-stacked-prs
- GitLab stacked diffs: https://docs.gitlab.com/user/project/merge_requests/stacked_diffs/ and `glab stack`: https://docs.gitlab.com/cli/stack/
- The Stacking Workflow (tool-neutral overview): https://www.stacking.dev/
- `git rebase --update-refs`: https://git-scm.com/docs/git-rebase
