# Git Bisect for Regression Debugging

Use binary search across commit history to find the exact commit that introduced a bug or regression.

## Contents

- When to Use Bisect
- Manual Bisect Workflow
- Automated Bisect with Test Scripts
- Writing a Bisect Test Script
- Handling Merge Commits
- Bisect Log and Replay
- Tips for Faster Bisects
- Integration with Debugging Workflow
- Quick Command Reference
- Do / Avoid
- Related Resources

---

## When to Use Bisect

Use `git bisect` when:
- Something worked before and now it does not ("it was fine last week")
- You cannot identify the breaking change by reading recent commits
- The regression is in a range of many commits (10+)
- You need proof of which commit introduced the issue

**How it works**: Binary search over commit history. For N commits, bisect finds the culprit in ~log2(N) steps. 1000 commits takes about 10 steps.

---

## Manual Bisect Workflow

```bash
# 1. Start bisect session
git bisect start

# 2. Mark current commit as bad (has the bug)
git bisect bad

# 3. Mark a known good commit (before the bug existed)
git bisect good v2.3.0
# Or use a commit hash:
git bisect good a1b2c3d

# Git checks out a middle commit. Test it manually.
# Bisecting: 47 revisions left to test after this (roughly 6 steps)

# 4. Test the current checkout and mark it
git bisect good    # If this commit works fine
# OR
git bisect bad     # If this commit has the bug

# Git checks out another commit. Repeat step 4.

# 5. Eventually Git identifies the first bad commit:
# abc1234 is the first bad commit
# commit abc1234
# Author: ...
# Date: ...
#     feat(api): change response serialization

# 6. End bisect and return to your original branch
git bisect reset
```

---

## Automated Bisect with Test Scripts

Let Git run a script at each step instead of testing manually. Fully hands-off.

```bash
# Start and define range
git bisect start
git bisect bad HEAD
git bisect good v2.3.0

# Run automated bisect with a test command
git bisect run npm test -- --testPathPattern="user-api"

# Or with a custom script
git bisect run ./scripts/bisect-test.sh

# Git runs the script at each step, marks good/bad automatically,
# and reports the first bad commit when done.
```

### One-liner form

```bash
git bisect start HEAD v2.3.0 -- && git bisect run npm test
```

---

## Writing a Bisect Test Script

The script must use specific exit codes:

| Exit Code | Meaning |
|-----------|---------|
| `0` | Good commit (no bug) |
| `1-124`, `126-127` | Bad commit (bug present) |
| `125` | Skip (cannot test this commit, e.g. build failure) |

### Example: Test a specific behavior

```bash
#!/bin/sh
# scripts/bisect-test.sh

# Build the project; skip if build fails (unrelated breakage)
npm run build 2>/dev/null || exit 125

# Run the specific test that catches the regression
npm test -- --testPathPattern="user-serialization" --bail 2>/dev/null
# Exit code 0 = tests pass = good commit
# Exit code 1 = tests fail = bad commit
```

### Example: Check for a runtime condition

```bash
#!/bin/sh
# scripts/bisect-check-output.sh

npm run build 2>/dev/null || exit 125

# Run the app and check output
OUTPUT=$(node dist/index.js --dry-run 2>&1)

# If output contains the error string, this is a bad commit
echo "$OUTPUT" | grep -q "undefined is not a function" && exit 1

# Otherwise it is good
exit 0
```

### Example: Test a compiled language

```bash
#!/bin/sh
# scripts/bisect-test-go.sh

# Build; skip commits that don't compile
go build ./... 2>/dev/null || exit 125

# Run specific test
go test ./pkg/serializer/ -run TestUserJSON -count=1
```

Make the script executable:

```bash
chmod +x scripts/bisect-test.sh
```

---

## Handling Merge Commits

Merge commits can confuse bisect by leading you down the wrong branch of history. Use `--first-parent` to follow only the mainline.

```bash
# Bisect following only first-parent (mainline) commits
git bisect start --first-parent
git bisect bad HEAD
git bisect good v2.3.0
git bisect run ./scripts/bisect-test.sh
```

**When to use `--first-parent`**:
- Repository uses merge commits (no rebase workflow)
- You want to find which PR/merge introduced the regression
- Feature branch internals are not relevant to the search

**When to skip `--first-parent`**:
- Repository uses squash merges (each commit is already atomic)
- You need to find the exact commit within a feature branch

---

## Bisect Log and Replay

### Save a bisect session

```bash
# During or after bisect, save the log
git bisect log > bisect-session.log
```

### Replay a saved session

```bash
# Replay on the same or different machine
git bisect replay bisect-session.log
```

### View current bisect state

```bash
# Show remaining commits to test
git bisect visualize --oneline

# Show bisect log so far
git bisect log
```

Useful for sharing a bisect investigation with a teammate or resuming after interruption.

---

## Tips for Faster Bisects

### Narrow the range first

```bash
# Check git log to find a rough good commit
git log --oneline --since="2 weeks ago" --until="1 week ago" -- src/api/

# Use that as your good commit instead of going back months
git bisect start
git bisect bad HEAD
git bisect good abc1234   # Last known good from log review
```

### Restrict bisect to specific paths

```bash
# Only consider commits that touched specific files
git bisect start -- src/api/ src/models/

# Combined with good/bad
git bisect start HEAD v2.3.0 -- src/api/
```

### Skip commits you cannot test

```bash
# If the current checkout is broken for unrelated reasons
git bisect skip

# Skip a range of known-broken commits
git bisect skip v2.4.0..v2.4.3
```

### Use exit code 125 in automated scripts

When a commit fails to build or is untestable for reasons unrelated to the bug, return 125 so bisect skips it automatically rather than marking it bad.

---

## Integration with Debugging Workflow

Bisect is one step in a systematic debugging process:

```
1. Reproduce the bug reliably
   └─ Write a failing test or manual repro steps

2. Identify the regression range
   └─ "It worked in v2.3, broken in v2.5"

3. Run git bisect
   └─ git bisect start HEAD v2.3.0
   └─ git bisect run ./scripts/bisect-test.sh

4. Analyze the identified commit
   └─ git show <bad-commit>
   └─ Read the diff, understand the change

5. Root cause analysis
   └─ Why did this change break things?
   └─ Was the original code relying on undocumented behavior?

6. Fix and verify
   └─ Write a regression test first
   └─ Apply the fix
   └─ Confirm the bisect test script now passes across the range

7. Prevent recurrence
   └─ Add the regression test to CI
   └─ Update documentation if behavior was ambiguous
```

---

## Quick Command Reference

```bash
# Start bisect
git bisect start

# Mark commits
git bisect bad [commit]       # Current or specified commit has the bug
git bisect good [commit]      # Current or specified commit is clean
git bisect skip [commit]      # Cannot test this commit

# Automated bisect
git bisect run <script>       # Run script at each step
git bisect run npm test       # Use any command

# One-liner start
git bisect start HEAD v2.3.0 --    # Bad=HEAD, good=v2.3.0
git bisect start --first-parent    # Follow mainline only

# Restrict to paths
git bisect start -- src/api/       # Only commits touching src/api/

# Session management
git bisect log                     # Show current session
git bisect log > session.log       # Save session
git bisect replay session.log      # Replay saved session
git bisect visualize --oneline     # Show remaining commits

# End bisect
git bisect reset                   # Return to original branch
git bisect reset <branch>          # Return to specific branch
```

---

## Do / Avoid

**DO**:
- [OK] Write a reliable repro script before starting bisect
- [OK] Use `exit 125` in scripts for untestable commits (build failures)
- [OK] Narrow the good/bad range with `git log` before bisecting
- [OK] Use `--first-parent` in merge-heavy repos to find the offending PR
- [OK] Save bisect logs for complex investigations (`git bisect log > file`)
- [OK] Add the regression test to CI after finding and fixing the bug
- [OK] Use path restrictions (`-- src/`) when you know which area regressed

**AVOID**:
- [FAIL] Running bisect without a reproducible test (manual "does it feel right" is unreliable)
- [FAIL] Marking a commit as bad when the failure is unrelated (use skip instead)
- [FAIL] Bisecting across thousands of commits without narrowing first
- [FAIL] Forgetting `git bisect reset` (leaves repo in detached HEAD state)
- [FAIL] Using bisect for non-regression issues (if it never worked, bisect will not help)
- [FAIL] Ignoring the identified commit without understanding why it broke things

---

## Related Resources

- [Common Mistakes](common-mistakes.md) - Git workflow pitfalls and fixes
- [Interactive Rebase Guide](interactive-rebase-guide.md) - History cleanup after finding the issue
- [Conflict Resolution](conflict-resolution.md) - Handling conflicts during bisect rebase
