# Integration Testing Template: API Integration Tests

Decisions to record before writing API + database integration tests. Library syntax (Supertest, Testcontainers, MSW, WireMock) is in their docs; contract suites belong to [qa-api-testing-contracts](../../../qa-api-testing-contracts/SKILL.md).

## Decisions

| Decision | Default | Record why if you deviate |
|---|---|---|
| Boundary under test | HTTP handler → service → real database, in one process | |
| Database | Real engine in a container (Testcontainers), same major version as production; never SQLite in-memory as a stand-in for PostgreSQL | |
| State reset | Per test: transaction rollback or truncate; unique data per test when workers run in parallel | |
| External services | Stub at the network edge (MSW, WireMock); keep a separate scheduled contract/smoke check against the real provider's test mode | |
| Assertions | Response status, body and headers **and** persisted state **and** side effects (events published, emails queued) | |
| Auth | Exercise real token validation with test keys; test the 401/403 paths, not just the happy path | |
| Failure paths | Timeouts, dependency 5xx, retries exhausted, transaction rollback | |
| Queues | Real broker in a container for publish/consume tests; assert idempotent handling of a redelivered message | |

## Example

```typescript
import { PostgreSqlContainer, type StartedPostgreSqlContainer } from '@testcontainers/postgresql'
import request from 'supertest'
import { buildApp } from '../src/app'

let pg: StartedPostgreSqlContainer
let app: ReturnType<typeof buildApp>

beforeAll(async () => {
  pg = await new PostgreSqlContainer('postgres:16').start()
  app = buildApp({ databaseUrl: pg.getConnectionUri() })
  await app.migrate()
}, 60_000)

afterAll(async () => { await app.close(); await pg.stop() })
beforeEach(async () => { await app.db.query('TRUNCATE orders RESTART IDENTITY CASCADE') })

it('creates an order and persists it exactly once', async () => {
  const res = await request(app.server)
    .post('/orders')
    .set('Idempotency-Key', 'k-1')
    .send({ sku: 'sku-1', qty: 2 })
  expect(res.status).toBe(201)

  const retry = await request(app.server).post('/orders').set('Idempotency-Key', 'k-1').send({ sku: 'sku-1', qty: 2 })
  expect(retry.status).toBe(201)

  const { rows } = await app.db.query('SELECT count(*)::int AS n FROM orders')
  expect(rows[0].n).toBe(1) // persisted state, not just the response
})
```

## Related Resources

- [../../references/test-environment-management.md](../../references/test-environment-management.md) — when to virtualise a dependency
- [../../references/synthetic-test-data.md](../../references/synthetic-test-data.md) — seed data without real customer data
