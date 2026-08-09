# Git History Forensics (Verifying Claims Against Real History)

Static files lie. A `CODEOWNERS` file, a merge-queue config, or a "we squash-merge" line in `CONTRIBUTING.md` describes *policy*, not *practice*. Before citing a Mode B practice or a Mode C pattern as real signal, use these `git` commands against a **shallow local clone** of the candidate repo (or `git log` over the GitHub API commit endpoints for a lighter check) to confirm the policy is actually followed at HEAD, not just declared.

This reference is single-repo forensics — it complements, not replaces, the multi-repo discovery/triage workflow in [discovery-protocol.md](discovery-protocol.md) and the "is it followed?" quality-filter checks in [practice-scan-targets.md](practice-scan-targets.md) and [code-pattern-mining.md](code-pattern-mining.md).

## Table of Contents

- [When to Reach for This](#when-to-reach-for-this)
- [Pickaxe: `-S` vs `-G` — Decision Framework](#pickaxe--s-vs--g--decision-framework)
- [`git log -L` — Line-Range History](#git-log--l--line-range-history)
- [`git blame` Done Right](#git-blame-done-right)
- [`git bisect run` — Automated Regression Verification](#git-bisect-run--automated-regression-verification)
- [`git range-diff` — Auditing Rebase-Based Workflows](#git-range-diff--auditing-rebase-based-workflows)
- [When `git log` Lies](#when-git-log-lies)
- [Current Git Facts (verify-at pointers)](#current-git-facts-verify-at-pointers)
- [Common Mistakes](#common-mistakes)

## When to Reach for This

| Question you're trying to answer | Use |
|---|---|
| "Did this exact string/config value get added or removed, and when?" | `git log -S` |
| "When did this *kind* of change happen?" (a pattern's structure, not one literal string) | `git log -G` |
| "What's the history of this one function/block, ignoring the rest of the file's churn?" | `git log -L` |
| "Is the CODEOWNERS entry actually who touches this code, or a stale formality?" | `git blame -w -C -M --ignore-revs-file` |
| "Does this repo's CI actually catch the regression class it claims to guard against?" | `git bisect run` against a reproducer |
| "Did this 'clean rebase workflow' the repo advertises actually stay clean across a real rebase?" | `git range-diff` |
| "Is this merge-heavy history hiding the real order of changes?" | `git log --first-parent` vs full history |

## Pickaxe: `-S` vs `-G` — Decision Framework

Both flags search diffs across history, but they answer different questions and are frequently confused:

- **`git log -S<string>`** ("pickaxe"): finds commits where the **number of occurrences** of the literal string changed — i.e., it was added or removed, not just moved within a changed line. Best for: "when was this exact identifier/flag/dependency introduced or dropped?" Add `--pickaxe-regex` to treat the argument as a regex instead of a literal string while keeping `-S`'s occurrence-count semantics.
- **`git log -G<regex>`**: finds commits where a diff **hunk** matches the regex — i.e., any added or removed line matching the pattern, regardless of whether the net occurrence count changed. Best for: "when did the shape of this code change?" (renames, refactors, signature changes) where an exact string match would miss variants.

Rule of thumb: reach for `-S` when mining Mode C "when was this idiom introduced" (e.g., `git log -S"useOptimistic" -- src/`) because you want the introduction/removal event, not every touch. Reach for `-G` when the pattern has variants (e.g., `git log -G"merge_group:" -- .github/workflows/` to catch a merge-queue trigger being added under any key ordering or formatting). `-G` is noisier — always pair with `--patch` and skim before trusting a hit.

```bash
# Mode C: find when React Query's queryClient.setQueryData pattern first appeared
git log -S"setQueryData" --oneline -- src/

# Mode B: find every commit that touched the merge-queue trigger structurally
git log -G"merge_group" --oneline -- .github/workflows/
```

## `git log -L` — Line-Range History

When you've already found the file and approximate line range (from `blame` or a code-search hit) and want the full commit history of just that block, not the whole file:

```bash
git log -L 120,160:src/queryClient.ts
git log -L :setQueryData:src/queryClient.ts   # range = the named function's body
```

This is the right tool once pickaxe has narrowed you to a file — pickaxe finds *which commit*, `-L` shows *the block's evolution* including refactors that didn't change the pickaxe string.

## `git blame` Done Right

Naive `git blame file.ts` over-attributes: it credits whoever last touched a line even if that touch was a mass reformat, a mechanical rename, or a bulk license-header update — none of which reflect real ownership or expertise.

```bash
git blame -w -C -M --ignore-revs-file .git-blame-ignore-revs -- src/queryClient.ts
```

- `-w` — ignore whitespace-only changes (reformats don't count as authorship)
- `-C` — detect lines moved/copied from other files (credits the original author, not whoever moved the file)
- `-M` — detect lines moved within the same file
- `--ignore-revs-file <file>` — skip specific commits entirely (mass-reformat commits, `prettier --write` sweeps, license-header bots) when attributing blame; many mature repos already ship a `.git-blame-ignore-revs` file for this — check for one before assuming naive blame is trustworthy

**Practice-scan application**: before trusting a `CODEOWNERS` entry as a real ownership signal (per the [practice-scan-targets.md quality filter](practice-scan-targets.md#quality-filter-per-candidate-practice)), run `-w -C -M` blame on 2-3 files the entry claims to own and confirm the named owner (or team) actually appears in real (non-mechanical) authorship — not just in a `CODEOWNERS` line nobody has revisited since the file was created.

## `git bisect run` — Automated Regression Verification

`git bisect run <script>` automates the binary search: the script's exit code drives the bisection — `0` means good, any other code (except `125`, which means "skip, untestable," and `>127`, which aborts the bisect) means bad.

```bash
git bisect start HEAD v1.2.0
git bisect run ./repro-test.sh
```

**Practice-scan application**: when a candidate repo's CI story claims "required checks catch regressions of class X," don't take it on faith — clone shallowly, write a 5-line reproducer for a known regression class, and `git bisect run` it against a range of the repo's own history. If the reproducer never flags a real historical regression that should have failed a "required" check, the check is decorative, not load-bearing — downgrade the practice's confidence rating.

## `git range-diff` — Auditing Rebase-Based Workflows

`git range-diff <base>..<old-tip> <base>..<new-tip>` (or the two-argument form `git range-diff <old-tip>...<new-tip>` when both share a base) compares two commit ranges commit-by-commit and shows what actually changed between the old and new version of each rebased/amended commit — the tool for reviewing "did this rebase actually stay clean" rather than re-reading a full diff.

```bash
git range-diff main~5..main@{1} main~5..main
```

**Practice-scan application**: repos that advertise a stacked-diff / Graphite workflow (see `data/sources.json` → `practice_hot_list.stacked_diffs`) are claiming their rebases are clean and reviewable. Spot-check by running `range-diff` across a PR's force-push history (available via `gh api repos/<owner>/<repo>/pulls/<n>/commits` at each push, or via the PR's own reflog if you have a local clone) — if consecutive force-pushes show wholesale rewrites rather than small fixups, the "clean stacked diff" claim doesn't hold up and shouldn't be extracted as a transferable pattern.

## When `git log` Lies

`git log` output is a projection of history, not history itself — several conditions make naive reads misleading:

| Condition | What it distorts | Mitigation |
|---|---|---|
| **Merge commits** (default `--topo-order` traversal) | Interleaves parallel branches; the order you see is not necessarily the order features shipped | Use `--first-parent` to see only the mainline story (what actually landed on the target branch, in landing order); use full traversal only when you need the branch structure itself |
| **Squash-merges** | Collapses N commits' worth of authorship and intermediate history into one commit — `blame` and pickaxe both lose the intermediate story | Check for the PR's original commits via `gh api repos/<owner>/<repo>/pulls/<n>/commits` (GitHub retains them even after a squash-merge lands) rather than relying on the squashed commit alone |
| **Force-pushes / history rewrites** | Old commit SHAs cited in a prior research pack may no longer exist on any ref (`git cat-file -e <sha>` fails) | Re-resolve citations by content (PR number, file path + date) rather than assuming a cited SHA is still reachable; this is also why [attribution-rules.md](attribution-rules.md) mandates pinning to a commit SHA at extraction time, not a branch |
| **Shallow / partial clones** (`--depth`, promisor remotes, `git clone --filter=blob:none`) | `git log`, `blame`, and pickaxe all silently truncate or fail past the fetch boundary — a shallow clone can make a repo *look* newer/smaller than it is | Confirm clone depth (`git log --oneline | wc -l` vs. the repo's true commit count from the GitHub API `contributors_url`/commit-count) before trusting a "this repo has thin history" read; `git fetch --unshallow` before deep forensics |
| **`git replay`-style history rewrites** (experimental as of Git 2.55, mid-2026) | Rewrites commits onto a new base while leaving the working tree untouched — same blame/pickaxe truncation risk as any rebase, but easy to miss since the working tree doesn't visibly change | Treat any repo using `git replay` in automation (rare, but check `.github/workflows/` for it) as a signal that ref history may be rewritten more often than blame naively assumes |

## Current Git Facts (verify-at pointers)

Git itself moves fast enough that specific version claims age out within months — treat the following as dated snapshots, not evergreen facts, and re-check at the linked source before citing a specific version number in a research pack:

- **Latest stable line as of 2026-07-11**: Git 2.55 (released late June 2026); Git 3.0 is targeted for late 2026 and is expected to default new repos to the `reftable` ref-storage backend. Verify at [git-scm.com/docs](https://git-scm.com/docs) and the [Git release notes tree](https://github.com/git/git/tree/master/Documentation/RelNotes) before citing.
- **SHA-256 repos**: experimental "compat" object-format interop between SHA-1 and SHA-256 has been landing since Git 2.45, but as of mid-2026 no major forge (GitHub, GitLab, Bitbucket) hosts SHA-256 repos — this skill's GitHub-first scanning surface is entirely SHA-1 in practice regardless of a target repo's local git version. Verify at [git-scm.com/docs/hash-function-transition](https://git-scm.com/docs/hash-function-transition).
- **`git replay`**: still marked experimental in its own man page as of Git 2.55 — useful for understanding *why* a repo might rewrite history programmatically (e.g., branch-forwarding automation), but don't assume it's in wide production use yet.
- **`reftable`**: production-ready as an opt-in backend since Git 2.51 (large perf wins on repos with 10k+ refs); not yet the default outside repos that explicitly opted in via `git init --ref-format=reftable` or `init.defaultRefFormat`.

## Common Mistakes

- **Trusting a policy doc over the commits** — `CONTRIBUTING.md` says "we always rebase"; the reflog says otherwise. The commits are ground truth.
- **Running naive `blame` and citing the top name as "the owner"** — without `-w -C -M` and an ignore-revs file, blame frequently credits a formatter bot or a mass-rename commit.
- **Using `-S` when you meant `-G` (or vice versa)** — `-S` on a pattern with many textual variants returns nothing useful; `-G` on a simple literal returns every incidental touch, not just add/remove events.
- **Citing a commit SHA from a force-pushed branch** — re-verify the SHA is still reachable (`git cat-file -e <sha>^{commit}`) before shipping a research pack; if it's gone, re-resolve by PR number or content.
- **Assuming a shallow clone (`--depth=1`, the default for many CI checkouts) has full history** — pickaxe and blame across a shallow clone silently stop at the fetch boundary with no error, producing a falsely thin history.
- **Skipping `git bisect run` in favor of manually eyeballing commits** — manual bisection on a 200-commit range is exactly the class of task the automation exists to remove; use it whenever you have a scriptable pass/fail check.
