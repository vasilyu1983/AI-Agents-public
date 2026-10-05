# Code Commenting Guide

Decision rules for inline comments and docstrings. Docstring syntax (JSDoc, TSDoc, Google/NumPy-style Python, godoc) follows each language's convention and the repo's existing style; match what the codebase already uses rather than introducing a second convention.

## Table of Contents

- [What Earns a Comment](#what-earns-a-comment)
- [Docstrings for Public APIs](#docstrings-for-public-apis)
- [Business Rules and External Constraints](#business-rules-and-external-constraints)
- [TODO and FIXME Markers](#todo-and-fixme-markers)
- [Comment Anti-Patterns](#comment-anti-patterns)
- [Enforcement](#enforcement)
- [Comment Review Checklist](#comment-review-checklist)

---

## What Earns a Comment

Code shows what it does; a comment earns its place by saying something the code cannot:

- **Why** this approach, when the obvious one was rejected ("iterative, not recursive: recursion overflows the stack for n > ~1000").
- **Constraints from outside the code:** a contract clause, a regulation, a vendor quirk, a performance budget.
- **Non-obvious invariants and edge cases** the next editor could break without noticing.
- **Workarounds**, with the condition under which they can be removed.

Before writing a comment that explains *what*, try renaming the variable or extracting a well-named function instead. An outdated comment is worse than none: readers and agents trust it over the code.

## Docstrings for Public APIs

- Every public function, class, and module in a library or shared package gets a docstring; internal helpers get one only when the name and signature are not enough.
- Document the contract, not the implementation: parameters (units, ranges, nullability), return value, raised errors, side effects, and thread-safety or idempotency when relevant.
- Include a short usage example for non-trivial APIs; in languages with doctests, make it an executable doctest so it cannot drift.
- Docstrings are the source for generated API reference; do not duplicate them by hand in `docs/`.

## Business Rules and External Constraints

Business rules in code are the comments most worth writing and the most likely to rot. For each one:

- State the rule and its source (policy doc, ticket, contract clause) with a link or ID.
- If the rule has an expiry or review date, put it in the comment **and** in a tracked place (ticket, config with a date check). A date that lives only in a comment is never acted on.
- Prefer moving volatile values (rates, thresholds, campaign dates) into configuration with an owner, and comment the config entry instead of the arithmetic.

```javascript
// Premium members get 20% off shipping: loyalty policy LP-12 (docs/policies/loyalty.md).
// Value lives in config so pricing can change without a deploy.
if (user.tier === 'premium') baseCost *= config.premiumShippingMultiplier;
```

## TODO and FIXME Markers

- Every marker carries a tracking reference: `// TODO(#123): add pagination`. A TODO without an issue is a wish, and nobody schedules wishes.
- Use a small fixed set of markers (`TODO`, `FIXME`, `HACK`) so they can be searched and counted.
- `HACK`/workaround comments state the removal condition ("remove when upstream fixes #456").
- Periodically report markers without issue references; fail CI on new ones if the team agrees.

## Comment Anti-Patterns

- **Commented-out code:** delete it; version control keeps history.
- **Redundant comments** that restate the line below.
- **Changelog comments** (`// 2025-11-22: fixed bug - Sarah`): history belongs in git.
- **Divider banners** (`// =====`): split the file or use the language's structure instead.
- **Names of individuals** as the owner of a rule: use a team, doc, or ticket.
- **Comments that contradict the code:** fix or delete during the same change that made them wrong.

## Enforcement

Use the linter plugin for the repo's language to require docstrings on public APIs and check parameter names against signatures; look up the currently maintained plugin for your toolchain, since several older doc linters have been deprecated. Do not gate on comment density; it rewards noise.

## Comment Review Checklist

- [ ] Comments explain why, constraints, or invariants, not what
- [ ] Public APIs have docstrings describing the contract
- [ ] Business rules cite their source; dated rules are also tracked outside the comment
- [ ] Every TODO/FIXME has an issue reference
- [ ] No commented-out code, changelog comments, or dividers
- [ ] Comments changed alongside the code they describe
