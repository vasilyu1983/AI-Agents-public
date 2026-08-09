# Commit Message Template + Examples (Good/Bad)

Use this template to keep history readable and automation-friendly.

---

## Core

### Template

```
type(scope): summary

Why:
- ...

What:
- ...

Notes:
- Risks/rollback: ...
- Tests: ...
```

Rules:

- Summary is imperative mood, no trailing period, <= 72 chars.
- `scope` is optional; use a stable module name.
- Body explains intent and impact; avoid implementation trivia.

### Conventional Commit Types (Common)

- `feat`: new user-visible capability
- `fix`: bug fix
- `perf`: measurable performance improvement
- `refactor`: code change without behavior change
- `docs`: documentation only
- `test`: tests only
- `chore`: maintenance, tooling, deps
- `ci`: pipeline and build config

### Good Examples

```
feat(api): add cursor pagination for /users

Why:
- Prevent unbounded scans on large tenants

What:
- Add cursor param + stable ordering
- Document response meta and examples

Notes:
- Tests: unit + contract
```

```
fix(auth): reject expired refresh tokens

Why:
- Prevent session extension past TTL

What:
- Validate token expiry before rotation

Notes:
- Tests: added regression case
```

### Bad Examples (Avoid)

```
fix: stuff
```

```
update
```

```
chore: generated with <assistant>
```

---

## Do / Avoid

### Do

- Do describe intent and impact (what and why)
- Do split unrelated changes into separate commits
- Do include tests/rollback notes for risky changes

### Avoid

- Avoid vague summaries (“fix”, “update”, “changes”)
- Avoid mixing refactors and features in one commit
- Avoid attribution strings in commit messages (repository policy)

---

## Optional: AI/Automation

- Generate initial suggestions from staged diff (human-edited)
- Draft a changelog-friendly summary for `feat`/`fix` (human-verified)

### Bounded Claims

- Automated suggestions can misclassify changes; humans own correctness.
