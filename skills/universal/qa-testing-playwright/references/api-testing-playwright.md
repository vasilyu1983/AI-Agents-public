# API Testing with Playwright

The `request` fixture (`APIRequestContext`) drives HTTP calls without a browser. Use it for two things inside this skill: fast setup/teardown for E2E tests, and hybrid API+UI assertions. For contract testing, schema validation, and consumer-driven contracts, use [qa-api-testing-contracts](../../qa-api-testing-contracts/SKILL.md).

Docs: https://playwright.dev/docs/api-testing, https://playwright.dev/docs/api/class-apirequestcontext

## Contents

- [Standalone requests](#standalone-requests-no-browser)
- [Typed responses](#typed-responses-163)
- [UI auth state](#reusing-ui-auth-state-in-api-calls)
- [API setup, UI verification](#api-setup-ui-verification-fast-fixtures)
- [UI action, API verification](#ui-action-api-verification)
- [Response timing](#response-timing-162)
- [Scope exclusions](#when-not-to-use-this-fixture)

## Standalone requests (no browser)

```typescript
import { test, expect } from '@playwright/test';

test('GET /api/products returns 200', async ({ request }) => {
  const response = await request.get('/api/products');
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(Array.isArray(body.items)).toBe(true);
});
```

`request` is an `APIRequestContext` fixture scoped per test; `playwright.request.newContext({ baseURL, extraHTTPHeaders })` creates an independent one when a test needs different auth or headers than the rest of the suite.

## Typed responses (1.63+)

`request.get`/`.post`/etc. accept a type argument so `response.json()` is typed instead of `any`:

```typescript
const response = await request.get<Product>('/api/products/42');
const product = await response.json(); // typed as Product
```

## Reusing UI auth state in API calls

The standalone `request` fixture has an isolated cookie jar. Use `page.request` or `context.request` when API calls must share live browser cookies. Loading the same saved `storageState` into separate contexts copies the initial state; later cookie changes are independent.

```typescript
test('API uses saved UI login', async ({ playwright, baseURL }) => {
  const apiContext = await playwright.request.newContext({
    baseURL,
    storageState: 'playwright/.auth/user.json',
  });
  try {
    const response = await apiContext.get('/api/me');
    expect(response.ok()).toBeTruthy();
  } finally {
    await apiContext.dispose();
  }
});
```

## API setup, UI verification (fast fixtures)

Use the API to create and tear down state so the UI test only exercises what it is meant to prove:

```typescript
test('create item via API, verify in UI', async ({ request, page }) => {
  const createResponse = await request.post('/api/products', {
    data: { name: 'Test Product', price: 29.99 },
  });
  expect(createResponse.ok()).toBeTruthy();
  const product = await createResponse.json();
  try {
    await page.goto('/products');
    await expect(page.getByText('Test Product')).toBeVisible();
  } finally {
    const cleanup = await request.delete(`/api/products/${product.id}`);
    expect(cleanup.ok()).toBeTruthy();
  }
});
```

## UI action, API verification

```typescript
test('form submission creates correct API record', async ({ page, request }) => {
  await page.goto('/products/new');
  await page.getByRole('textbox', { name: 'Name' }).fill('New Widget');
  await page.getByRole('button', { name: 'Create' }).click();
  await page.waitForURL(/\/products\/[\w-]+/);

  const productId = page.url().split('/').pop();
  const response = await request.get(`/api/products/${productId}`);
  const product = await response.json();
  expect(product.name).toBe('New Widget');
});
```

## Response timing (1.62+)

`APIResponse.timing()` returns resource-timing data for an API response — useful when an E2E test needs to assert a backend call stayed within budget without pulling in a separate load-testing tool:

```typescript
const response = await request.get('/api/products');
const duration = response.timing().responseEnd;
expect(duration).toBeGreaterThanOrEqual(0); // -1 means timing unavailable
expect(duration).toBeLessThan(500); // example budget: choose for this endpoint
```

## When NOT to use this fixture

- Schema/contract validation, mock-server-based consumer contracts, or cross-team API drift: use [qa-api-testing-contracts](../../qa-api-testing-contracts/SKILL.md) — a UI click-path proxy is the wrong tool for contract drift.
- Pure backend correctness with no UI branching: test the API directly in a backend test suite; do not route it through Playwright just to reuse fixtures.
- Load/soak testing: use [qa-testing-performance](../../qa-testing-performance/SKILL.md) (k6, Locust, Artillery).

## Related Resources

- [Playwright API Testing Guide](https://playwright.dev/docs/api-testing)
- [APIRequestContext API Reference](https://playwright.dev/docs/api/class-apirequestcontext)
- [qa-api-testing-contracts](../../qa-api-testing-contracts/SKILL.md)
