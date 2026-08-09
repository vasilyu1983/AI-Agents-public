# Complexity-Only Review Pass

**Attribution**: Pattern from [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail), commit `2ed6c52`, `skills/ponytail-review/SKILL.md` and `skills/ponytail-audit/SKILL.md`. MIT license. Recorded 2026-08-09 in `docs/research/2026-08-09-skill-ponytail-scan.md`.

## What This Is

A deliberately narrow review pass that looks only for over-engineering — and explicitly nothing else. `references/review-checklist-comprehensive.md` treats "code is not over-engineered" as one line among ~350 lines covering correctness, security, performance, and testing; this is the opposite shape — a single-axis pass that is fast and cheap enough to run every diff, not just the ones that warrant a full review.

**Out of scope, by design**: correctness bugs, security holes, and performance. A finding in any of those categories does not belong in this pass's output — route it to the normal review flow (`references/operational-playbook.md`) instead. Mixing over-engineering critique into a general review dilutes both: the reviewer's attention splits across axes, and a cheap, single-purpose pass stops being cheap once it grows a second job. Keeping the scope narrow is what makes it viable to run frequently.

The underlying smells this pass looks for are not new — they are the same ones cataloged in [`qa-refactoring/references/code-smells-guide.md`](../../qa-refactoring/references/code-smells-guide.md) (Dead Code, Speculative Generality, Lazy Class, and related Bloaters/Dispensables categories) and in this skill's own `review-checklist-comprehensive.md` Design Patterns section. What's novel here is the packaging: a fixed five-tag vocabulary, a one-line-per-finding format anchored to a location, and a single net-lines-saved metric at the end — not a new taxonomy of complexity problems.

## Tag Vocabulary

Five tags, each mapped to a specific complexity smell:

| Tag | Smell | What it flags |
|-----|-------|----------------|
| `delete:` | Dead code | Code with no live caller or reachable path — safe to remove outright. |
| `stdlib:` | Reinvented wheel | A hand-rolled implementation of something the language or framework standard library already provides. |
| `native:` | Unnecessary dependency | A third-party package pulled in for something a native/built-in API already covers. |
| `yagni:` | Speculative generality | Configurability, abstraction layers, or extension points built for a use case that doesn't exist yet. |
| `shrink:` | Compressible logic | Correct code that does the job in more lines/branches/indirection than the job requires. |

## Finding Format

One line per finding, no prose paragraph, no severity label (this pass has no severity axis — a finding is in scope or it isn't):

```text
L<line>: <tag> <what>. <replacement>.
```

Example:

```text
L142: yagni: StrategyFactory supports 4 pluggable backends; only 1 is ever instantiated. Inline the single implementation.
L58: stdlib: hand-rolled deep-merge helper duplicates structuredClone/lodash.merge already in use elsewhere in this repo. Replace with the existing utility.
```

Location-anchored and self-contained: a reader should be able to act on the line without needing the rest of the review as context.

## Two Variants

- **Diff-scoped** (`ponytail-review` equivalent): review only the changed lines in a PR/diff. Use this as a fast pre-merge complexity check, independent of the main correctness/security review.
- **Whole-repo-scoped** (`ponytail-audit` equivalent): review an entire codebase or module, ranked biggest-cut-first (the finding with the largest net-lines-saved potential listed first). Use this for periodic complexity debt sweeps, not as a per-PR gate.

## Output: A Single Net Metric

End the pass with one number: `net: -N lines` (or `+N` if a `yagni:`/`shrink:` fix would require adding lines to un-abstract something, which is rare but possible). This is the pass's only scoreboard — it does not produce a P0–P3 severity breakdown, because severity implies a risk judgment this pass is not making. A large negative net number is a signal the pass is earning its keep; it is not, on its own, a merge blocker.

## When to Use This Instead of the Full Checklist

Use this pass when:

- The change is not touching correctness-, security-, or performance-sensitive paths, and a full `review-checklist-comprehensive.md` pass would be overkill for what's actually being reviewed.
- You want a cheap, repeatable check that can run on every diff without the reviewer-time cost of the full checklist.
- A codebase has accumulated abstraction debt and needs a dedicated sweep that isn't diluted by also hunting for bugs.

Do not use it as a substitute for the full review on anything touching auth, money movement, migrations, or public APIs — this pass has no security or correctness coverage at all, and treating a clean `net: -N` result as "reviewed" for those changes is a false signal.
