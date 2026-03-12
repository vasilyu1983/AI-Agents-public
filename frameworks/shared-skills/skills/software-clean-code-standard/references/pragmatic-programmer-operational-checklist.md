# The Pragmatic Programmer Operational Checklist

Practical heuristics from Hunt & Thomas for everyday software work.

## Personal Practices
- Take responsibility: own defects, communicate risks early, and keep code releasable.
- Keep knowledge in plain text and under version control; automate repetitive work.
- Invest in learning: katas, reading, and tool mastery; practice tracer bullets to validate direction early.

## Design and Architecture
- DRY: eliminate duplication in logic, data, and documentation; converge on single sources of truth.
- Decouple with clear contracts; use assertions to enforce invariants and fail fast.
- Design for orthogonality: components should do one thing well and be replaceable without ripple effects.
- Use tracer bullets/prototypes to validate requirements; refactor into clean structure afterward.

## Coding Discipline
- Write readable, intention-revealing code; avoid cleverness that obscures behavior.
- Prefer simple, composable structures; keep functions small and cohesive.
- Guard boundaries: wrap external systems; normalize errors, timeouts, and retries in one place.
- Manage state explicitly; avoid global mutable state; prefer immutability and clear ownership.

## Testing and Quality
- Unit test critical paths, edges, and failures; tests must be self-checking and deterministic.
- Treat bug fixes as tests-first: reproduce, add failing test, fix, keep the test.
- Use automated checks (linters/formatters) and continuous integration; keep builds green.

## Pragmatic Error Handling
- Fail fast on bad inputs; handle errors once per layer with context.
- Log actionable information (what, where, context); avoid silent retries without limits.
- Use feature flags and configuration to de-risk rollout; support rollback paths.

## Working with Others
- Communicate clearly: assumptions, constraints, and trade-offs; document decisions close to code.
- Prefer small, frequent integration; avoid big-bang merges.
- Share knowledge via code reviews and pairing; align on standards with checklists and examples.
