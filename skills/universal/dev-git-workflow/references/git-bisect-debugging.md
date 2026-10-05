# Git Bisect for Regression Hunting

Finding the commit that introduced (or fixed) a behavior change. Assumes you know `git bisect start/good/bad/reset`. Root-cause analysis after the commit is found belongs to the debugging skills.

## Contents

- [When Bisect Pays Off](#when-bisect-pays-off)
- [Automated Bisect](#automated-bisect)
- [Exit Codes](#exit-codes)
- [Writing the Test Script](#writing-the-test-script)
- [History Shape: Squash, Merges, First-Parent](#history-shape-squash-merges-first-parent)
- [Flaky Symptoms](#flaky-symptoms)
- [Finding a Fix Instead of a Break](#finding-a-fix-instead-of-a-break)
- [Speed and Bookkeeping](#speed-and-bookkeeping)

## When Bisect Pays Off

Use it when a behavior worked at a known commit and fails at a later one, and reading the log does not reveal the cause. Cost is about log2(N) test runs for N commits, so the range size barely matters; what matters is a fast, reliable test and a trustworthy "good" commit. Confirm the good commit really is good (run the test there first) before starting; a wrong endpoint wastes the whole session.

## Automated Bisect

```bash
git bisect start <bad> <good>          # e.g. HEAD v2.3.0
git bisect run /tmp/bisect-test.sh     # script outside the repo
git bisect log > /tmp/bisect.log       # keep the evidence
git bisect reset                       # always, even after failures
```

Restrict to paths when you know where the change must be: `git bisect start <bad> <good> -- src/billing/`. Only commits touching those paths are tested, so this is fast but misses causes elsewhere (a dependency bump, a config change).

## Exit Codes

`git bisect run` interprets the script's exit status:

| Exit status | Meaning |
|-------------|---------|
| 0 | good |
| 1 to 127, except 125 | bad |
| 125 | skip: this commit cannot be tested |
| above 127 (for example killed by a signal) | abort the bisect |

Most bugs in bisect scripts come from this table: a build failure exits 1 and gets marked bad, pointing at an unrelated commit that broke the build. Map "cannot build or cannot set up" to 125, and only the actual symptom to 1.

## Writing the Test Script

```sh
#!/bin/sh
# /tmp/bisect-test.sh (kept outside the tracked tree)
make build >/dev/null 2>&1 || exit 125          # unrelated breakage: skip
timeout 300 ./run-one-test.sh billing_rounding   # the specific symptom
status=$?
[ "$status" -eq 124 ] && exit 125                # timeout: treat as untestable
[ "$status" -eq 0 ] && exit 0
exit 1
```

- **Keep the script outside the tracked tree** (or untracked and ignored). Bisect checks out old commits; a script inside the repo may not exist, or may be an older version, at those commits.
- **Test the symptom, not the suite.** Run the one test or reproduction that shows the regression; unrelated failing tests at old commits mislead the search.
- **Rebuild from clean state** when build artifacts or dependency caches can leak between commits (for example reinstall dependencies when the lockfile changed).
- **The test must exist at old commits.** If the regression test was written after the break, keep it outside the tree and copy it in during the script.

## History Shape: Squash, Merges, First-Parent

- **Squash-merged repos:** each PR is one commit on main, so bisect identifies the PR, not the line. Continue inside the PR's original branch if it still exists, or read the PR diff.
- **Merge-commit repos:** bisect may step into feature-branch commits that never built on their own. Use `git bisect start --first-parent` to test only mainline commits (one per merged PR), then bisect inside the offending PR's branch if needed.
- **Rebase-merged repos:** every commit landed individually, so bisect is precise only if every commit built and passed; this is the main argument for testing each commit before rebase-merging.

## Flaky Symptoms

If the symptom is intermittent, one passing run does not prove a commit good. Run the reproduction several times per step and call the commit good only if all runs pass; the number of runs follows from how often the failure appears at the known-bad commit. Bisect is not worth running until the symptom reproduces reliably at the bad commit.

## Finding a Fix Instead of a Break

To find the commit that fixed something (for example, which upstream commit to backport), rename the states so the logic stays readable:

```bash
git bisect start --term-old=broken --term-new=fixed
git bisect fixed <commit-with-fix>
git bisect broken <commit-without-fix>
```

With `bisect run`, exit 0 still means the old term (`broken`) and 1 to 127 the new term (`fixed`), so write the script to exit 0 when the bug is present.

## Speed and Bookkeeping

- Narrow the range cheaply first (release tags, CI history, deploy log) before bisecting.
- `git bisect skip` on untestable commits; a long run of skipped commits leaves an ambiguous range that bisect reports as a list of candidates.
- `git bisect log` / `git bisect replay <file>` let you correct one wrong mark without starting over: edit the log, reset, replay.
- Attach the bisect log and the first-bad commit to the bug report, then write the regression test before the fix.
- In a shared working tree, run bisect in a separate worktree so it does not check out old commits under other agents or people: `git worktree add --detach /tmp/bisect-wt <bad>`.
