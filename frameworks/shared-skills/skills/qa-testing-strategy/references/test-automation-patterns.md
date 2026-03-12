# Test Automation Patterns

Modern patterns and anti-patterns for reliable, maintainable test automation.

## Contents

- Pattern: Page Object Model (POM)
- Pattern: Test Data Factories
- Pattern: Fixture Management
- Pattern: Test Doubles (Mocks, Stubs, Fakes)
- Pattern: Arrange-Act-Assert (AAA)
- Pattern: Test Isolation
- Pattern: Contract Testing
- Pattern: Retry Logic
- Pattern: Snapshot Testing
- Pattern: Test Categorization (Tags)
- Pattern: Parameterized Tests
- Anti-Pattern: Testing Implementation Details
- Anti-Pattern: Flaky Tests
- Anti-Pattern: Excessive Mocking
- Anti-Pattern: Brittle Selectors
- Anti-Pattern: Testing Multiple Things
- Pattern Decision Tree
- Related Resources

## Pattern: Page Object Model (POM)

**Use when:** Writing E2E tests with multiple page interactions.

**Benefits:**
- Encapsulates page structure
- Reduces code duplication
- Easier maintenance when UI changes
- Improves test readability

**Structure:**

```typescript
// pages/checkout.page.ts
export class CheckoutPage {
  constructor(private page: Page) {}

  // Locators (lazy evaluation)
  get addressInput() { return this.page.getByLabel('Address') }
  get cityInput() { return this.page.getByLabel('City') }
  get submitButton() { return this.page.getByRole('button', { name: 'Submit' }) }

  // Actions
  async fillShippingInfo(address: string, city: string) {
    await this.addressInput.fill(address)
    await this.cityInput.fill(city)
    await this.submitButton.click()
  }

  // Assertions
  async expectSuccessMessage() {
    await expect(this.page.getByText('Order placed')).toBeVisible()
  }
}
```

**When NOT to use:** Simple one-page tests, component tests.

---

## Pattern: Test Data Factories

**Use when:** Creating test data with complex structures.

**Benefits:**
- Consistent test data
- Easy to create variations
- Reduces magic values
- Supports factories with defaults

**Example:**

```typescript
export class UserFactory {
  static create(overrides: Partial<User> = {}): User {
    return {
      id: faker.string.uuid(),
      email: faker.internet.email(),
      name: faker.person.fullName(),
      role: 'user',
      createdAt: new Date(),
      ...overrides
    }
  }

  static createAdmin() {
    return this.create({ role: 'admin', permissions: ['all'] })
  }

  static createMany(count: number, overrides = {}) {
    return Array.from({ length: count }, () => this.create(overrides))
  }
}
```

---

## Pattern: Fixture Management

**Use when:** Tests need consistent setup data.

**Benefits:**
- Predictable test state
- Reusable across tests
- Easier debugging
- Version-controlled test data

**Example:**

```typescript
// fixtures/products.ts
export const testProducts = {
  laptop: {
    id: 'prod-1',
    name: 'MacBook Pro',
    price: 2499,
    stock: 10
  },
  mouse: {
    id: 'prod-2',
    name: 'Logitech MX',
    price: 99,
    stock: 50
  }
}

// Usage
import { testProducts } from './fixtures/products'

test('add product to cart', async () => {
  await addToCart(testProducts.laptop)
  expect(getCartTotal()).toBe(2499)
})
```

---

## Pattern: Test Doubles (Mocks, Stubs, Fakes)

**Use when:** Isolating tests from external dependencies.

**Types:**

**Mock** - Verify interactions (how many times called, with what args)
```typescript
const emailService = {
  send: jest.fn().mockResolvedValue({ success: true })
}

await service.createUser(userData)
expect(emailService.send).toHaveBeenCalledWith({
  to: 'user@example.com',
  template: 'welcome'
})
```

**Stub** - Provide predefined responses
```typescript
const paymentGateway = {
  charge: () => Promise.resolve({ transactionId: 'TX123', status: 'success' })
}
```

**Fake** - Working implementation (in-memory DB, mock server)
```typescript
class FakeDatabase {
  private data = new Map()

  async save(key, value) {
    this.data.set(key, value)
  }

  async get(key) {
    return this.data.get(key)
  }
}
```

**Guideline:** Use mocks sparingly. Prefer real implementations for internal code, use test doubles for external services.

---

## Pattern: Arrange-Act-Assert (AAA)

**Use when:** Writing any test.

**Structure:**

```typescript
test('should calculate discount', () => {
  // Arrange - Setup test data
  const order = { total: 100, items: 5 }
  const discountService = new DiscountService()

  // Act - Execute the operation
  const finalPrice = discountService.apply(order)

  // Assert - Verify the outcome
  expect(finalPrice).toBe(90) // 10% discount
})
```

**Benefits:**
- Clear test structure
- Easy to understand
- Identifies what's being tested

---

## Pattern: Test Isolation

**Use when:** Always.

**Principles:**
- Each test is independent
- No shared mutable state
- Tests can run in any order
- Tests can run in parallel

**Example:**

```typescript
// BAD: Bad - Shared state
let user: User

beforeAll(() => {
  user = createUser() // Shared across all tests
})

test('update user', () => {
  user.name = 'Updated' // Mutates shared state
})

test('delete user', () => {
  deleteUser(user.id) // Now first test will fail if this runs first
})

// GOOD: Good - Isolated state
beforeEach(() => {
  user = createUser() // Fresh user for each test
})

afterEach(() => {
  cleanupUser(user.id) // Clean up after each test
})
```

---

## Pattern: Contract Testing

**Use when:** Testing microservice APIs.

**Benefits:**
- Catches integration issues early
- Faster than E2E tests
- Consumer-driven contracts
- Safe refactoring

**Example (Pact)**:

```typescript
// Consumer test (Frontend)
describe('User API', () => {
  it('should get user by ID', async () => {
    await provider.addInteraction({
      state: 'user with ID 1 exists',
      uponReceiving: 'a request for user 1',
      withRequest: {
        method: 'GET',
        path: '/users/1'
      },
      willRespondWith: {
        status: 200,
        body: { id: 1, email: 'user@example.com' }
      }
    })

    const user = await api.getUser(1)
    expect(user.email).toBe('user@example.com')
  })
})

// Provider verification (Backend)
new Verifier({
  provider: 'UserAPI',
  providerBaseUrl: 'http://localhost:3000',
  pactUrls: ['./pacts/frontend-userapi.json']
}).verifyProvider()
```

---

## Pattern: Retry Logic

**Use when:** Tests have flakiness due to timing issues.

**Caution:** Retries mask instability. Fix root cause when possible.

**Example:**

```typescript
// Playwright (built-in)
await expect(page.getByText('Loaded')).toBeVisible({ timeout: 5000 })

// Jest with custom retry
async function retryOperation(operation, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await operation()
    } catch (error) {
      if (i === maxRetries - 1) throw error
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)))
    }
  }
}

test('fetch data with retry', async () => {
  const data = await retryOperation(() => fetchData())
  expect(data).toBeDefined()
})
```

---

## Pattern: Snapshot Testing

**Use when:** Testing output that changes rarely (config, serialization).

**Benefits:**
- Catches unintended changes
- Quick to write
- Good for regression testing

**Caution:** Easy to blindly approve changes.

**Example:**

```typescript
test('config snapshot', () => {
  const config = getConfig()
  expect(config).toMatchSnapshot()
})

test('user profile snapshot', () => {
  const profile = getUserProfile('user-123')
  expect(profile).toMatchSnapshot({
    createdAt: expect.any(Date), // Dynamic values
    id: expect.any(String)
  })
})
```

**When to update snapshots:** Only when change is intentional. Review diffs carefully.

---

## Pattern: Test Categorization (Tags)

**Use when:** Running different test suites.

**Categories:**
- **@smoke** - Critical paths, run on every commit
- **@regression** - Full suite, run nightly
- **@slow** - Long-running tests
- **@flaky** - Known flaky tests (quarantined)
- **@wip** - Work in progress

**Example (Cucumber)**:

```gherkin
@smoke @critical
Feature: Login

@happy-path
Scenario: Successful login
  # ...

@error-handling @slow
Scenario: Account lockout
  # ...
```

```bash
# Run smoke tests only
npm test -- --tags "@smoke"

# Run all except slow tests
npm test -- --tags "not @slow"
```

---

## Pattern: Parameterized Tests

**Use when:** Testing same logic with different inputs.

**Example (Jest/Vitest)**:

```typescript
describe.each([
  { input: 'hello', expected: 'HELLO' },
  { input: 'world', expected: 'WORLD' },
  { input: '', expected: '' },
  { input: '123', expected: '123' }
])('uppercase($input)', ({ input, expected }) => {
  it(`should return ${expected}`, () => {
    expect(uppercase(input)).toBe(expected)
  })
})
```

**Example (Cucumber Scenario Outline)**:

```gherkin
Scenario Outline: Validate email
  When I enter email "<email>"
  Then validation should be "<result>"

  Examples:
    | email               | result  |
    | user@example.com    | valid   |
    | invalid-email       | invalid |
    | @example.com        | invalid |
```

---

## Anti-Pattern: Testing Implementation Details

**Problem:** Tests break when refactoring, even though behavior unchanged.

**Example:**

```typescript
// BAD: Bad - Tests internal method
test('should call internal helper', () => {
  const spy = jest.spyOn(service, 'internalHelper')
  service.publicMethod()
  expect(spy).toHaveBeenCalled()
})

// GOOD: Good - Tests public behavior
test('should return correct result', () => {
  const result = service.publicMethod()
  expect(result).toBe(expectedValue)
})
```

---

## Anti-Pattern: Flaky Tests

**Problem:** Tests pass/fail randomly, undermining trust.

**Common causes:**
- Race conditions (async timing)
- Shared mutable state
- External dependencies (network, time)
- Test order dependencies

**Solutions:**
- Use explicit waits (not sleep)
- Isolate tests (fresh state per test)
- Mock time and external services
- Run tests in random order locally

```typescript
// BAD: Bad - Sleep (flaky)
await sleep(1000) // Hope data loads in 1 second

// GOOD: Good - Explicit wait
await page.waitForSelector('[data-loaded="true"]')
await expect(page.getByText('Data loaded')).toBeVisible()
```

---

## Anti-Pattern: Excessive Mocking

**Problem:** Tests pass but integration fails.

**Example:**

```typescript
// BAD: Bad - Mocking everything
const database = { save: jest.fn(), find: jest.fn() }
const cache = { get: jest.fn(), set: jest.fn() }
const logger = { log: jest.fn() }
const emailService = { send: jest.fn() }

// Unit test passes, but real integration is untested

// GOOD: Good - Use real implementations for internal code
const database = new InMemoryDatabase() // Real logic
const cache = new InMemoryCache()       // Real logic
const emailService = mockEmailService() // Mock external service
```

**Guideline:** Mock external boundaries, use real implementations internally.

---

## Anti-Pattern: Brittle Selectors

**Problem:** E2E tests break when CSS/HTML changes.

**Example:**

```typescript
// BAD: Bad - Implementation-coupled selectors
await page.locator('.btn.btn-primary.submit-btn-v2').click()
await page.locator('div > div > div > button:nth-child(3)').click()

// GOOD: Good - Semantic selectors
await page.getByRole('button', { name: 'Submit' }).click()
await page.getByTestId('submit-button').click()
await page.getByLabel('Submit form').click()
```

**Best to worst:**
1. data-testid
2. ARIA role + accessible name
3. User-visible text
4. CSS class (avoid)
5. XPath/complex selectors (avoid)

---

## Anti-Pattern: Testing Multiple Things

**Problem:** Unclear what failed when test breaks.

**Example:**

```typescript
// BAD: Bad - Tests multiple behaviors
test('user service', async () => {
  const user = await service.create({ email: 'test@example.com' })
  expect(user.id).toBeDefined()

  const found = await service.findById(user.id)
  expect(found).toBeDefined()

  await service.delete(user.id)
  const deleted = await service.findById(user.id)
  expect(deleted).toBeNull()
})

// GOOD: Good - One behavior per test
test('should create user', async () => {
  const user = await service.create({ email: 'test@example.com' })
  expect(user.id).toBeDefined()
})

test('should find user by ID', async () => {
  const user = await service.create({ email: 'test@example.com' })
  const found = await service.findById(user.id)
  expect(found).toBeDefined()
})

test('should delete user', async () => {
  const user = await service.create({ email: 'test@example.com' })
  await service.delete(user.id)
  const deleted = await service.findById(user.id)
  expect(deleted).toBeNull()
})
```

---

## Pattern Decision Tree

**What should I test?**

```
Is it a UI interaction?
├─ YES → E2E test (Playwright/Cypress)
└─ NO
   ├─ Is it business logic?
   │  └─ YES → Unit test (Jest/Vitest)
   └─ Is it API contract?
      └─ YES → Contract test (Pact) + Integration test
```

**Should I mock this?**

```
Is it an external service (API, payment gateway)?
├─ YES → Mock it
└─ NO
   ├─ Is it a database?
   │  ├─ Unit test → Use in-memory/mock
   │  └─ Integration test → Use real DB (Docker)
   └─ Is it internal code?
      └─ NO → Use real implementation
```

## Related Resources

See [comprehensive-testing-guide.md](comprehensive-testing-guide.md) for test pyramid and strategy, [shift-left-testing.md](shift-left-testing.md) for early testing practices.
