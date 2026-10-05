# Unit Testing Template: Jest / Vitest

Decisions to record before writing unit tests for a JavaScript/TypeScript module. Syntax and API details are in the Jest and Vitest docs; this template only fixes the choices that affect gate quality.

## Decisions

| Decision | Default | Record why if you deviate |
|---|---|---|
| Runner | Vitest for Vite/ESM projects; stay on Jest where it is already established (migration cost rarely pays back on its own) | |
| What counts as a unit | A domain rule, validator or pure function reachable without I/O | |
| Test doubles | Fakes/mocks only at external boundaries; real collaborators inside the module | |
| Oracle | Assert observable outputs and thrown errors, never private helpers | |
| Generated inputs | Add a property test for invariants (round-trip, idempotence, bounds); see [property-based-testing.md](../../references/property-based-testing.md) | |
| Snapshots | Only for stable serialised output, reviewed as diffs | |
| Gate | Changed-file mutation score, not line coverage, for AI-authored tests; see [quality-metrics-dashboard.md](../../references/quality-metrics-dashboard.md#operationalising-mutation-coverage) | |
| Order independence | Run with randomised order periodically (Jest `--randomize`, or a Vitest `sequence.shuffle` config) to catch shared state | |

## Example (AAA, one behaviour per test)

```typescript
// user.service.test.ts
import { describe, it, expect, beforeEach } from 'vitest' // or '@jest/globals'
import { UserService } from './user.service'
import { InMemoryUserRepo } from './testing/in-memory-user-repo'

describe('UserService.createUser', () => {
  let service: UserService

  beforeEach(() => {
    service = new UserService(new InMemoryUserRepo()) // fresh state per test
  })

  it('stores a hash, never the plain password', async () => {
    const user = await service.createUser({ email: 'a@example.com', password: 'Plain-123', name: 'A' })
    expect(user.password).not.toBe('Plain-123')
    expect(user.password).toMatch(/^\$2[aby]\$/) // bcrypt prefix
  })

  it('rejects a duplicate email', async () => {
    const input = { email: 'a@example.com', password: 'p', name: 'A' }
    await service.createUser(input)
    await expect(service.createUser(input)).rejects.toThrow('Email already exists')
  })
})
```

Revert check: each test above must fail if the rule it names is removed (hashing skipped, uniqueness check deleted). If it would still pass, the oracle is too weak.

## Related Resources

- [../../references/test-automation-patterns.md](../../references/test-automation-patterns.md) — retry, snapshot and mocking rules
- [../../SKILL.md](../../SKILL.md) — layer decision rules
