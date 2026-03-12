# API Testing with Playwright

API testing using Playwright's APIRequestContext -- standalone API tests without a browser, response validation, combining API setup with UI verification, and advanced patterns for complete API coverage.

## Contents

- Standalone API Testing
- APIRequestContext Creation
- Request Methods
- Header and Auth Management
- Response Validation Patterns
- JSON Schema Validation
- Combining API and UI Tests
- File Upload and Download
- Multipart Form Data
- API Test Fixtures
- Parallel API Testing
- Mocking External APIs
- API Test Organization
- Related Resources

---

## Standalone API Testing

Playwright can run API tests without launching a browser, making it fast and efficient for backend validation.

```typescript
import { test, expect } from '@playwright/test';

test('GET /api/users returns user list', async ({ request }) => {
  const response = await request.get('/api/users');

  expect(response.ok()).toBeTruthy();
  expect(response.status()).toBe(200);

  const users = await response.json();
  expect(users).toHaveLength(expect.any(Number));
  expect(users[0]).toHaveProperty('id');
  expect(users[0]).toHaveProperty('email');
});
```

### Why Use Playwright for API Tests?

| Advantage | Description |
|-----------|-------------|
| Same toolchain | One framework for UI + API tests |
| Shared auth | Reuse storageState cookies/tokens |
| Mixed tests | API setup + UI verification in one test |
| Parallel execution | Built-in parallelism via workers |
| Rich assertions | `expect` API works on responses |
| Trace viewer | API calls visible in Playwright traces |

---

## APIRequestContext Creation

### Using the Built-In `request` Fixture

```typescript
// Uses baseURL from playwright.config.ts
test('simple API call', async ({ request }) => {
  const response = await request.get('/api/health');
  expect(response.ok()).toBeTruthy();
});
```

### Creating a Custom Context

```typescript
import { test, expect, APIRequestContext } from '@playwright/test';

let apiContext: APIRequestContext;

test.beforeAll(async ({ playwright }) => {
  apiContext = await playwright.request.newContext({
    baseURL: 'https://api.example.com',
    extraHTTPHeaders: {
      'Authorization': `Bearer ${process.env.API_TOKEN}`,
      'Accept': 'application/json',
      'X-Request-Source': 'playwright-tests',
    },
  });
});

test.afterAll(async () => {
  await apiContext.dispose();
});

test('custom context API call', async () => {
  const response = await apiContext.get('/users/me');
  expect(response.ok()).toBeTruthy();
});
```

### Config-Level BaseURL

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    baseURL: 'http://localhost:3000',
    extraHTTPHeaders: {
      'Accept': 'application/json',
    },
  },
  projects: [
    {
      name: 'api-tests',
      testMatch: /.*\.api\.spec\.ts/,
      use: {
        baseURL: process.env.API_BASE_URL || 'http://localhost:3000',
      },
    },
  ],
});
```

---

## Request Methods

### Full CRUD Example

```typescript
test.describe('Users API CRUD', () => {
  let userId: string;

  test('POST - create user', async ({ request }) => {
    const response = await request.post('/api/users', {
      data: {
        name: 'Jane Smith',
        email: 'jane@example.com',
        role: 'editor',
      },
    });

    expect(response.status()).toBe(201);
    const body = await response.json();
    expect(body.id).toBeDefined();
    expect(body.name).toBe('Jane Smith');
    userId = body.id;
  });

  test('GET - read user', async ({ request }) => {
    const response = await request.get(`/api/users/${userId}`);

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.email).toBe('jane@example.com');
  });

  test('PUT - replace user', async ({ request }) => {
    const response = await request.put(`/api/users/${userId}`, {
      data: {
        name: 'Jane Doe',
        email: 'jane.doe@example.com',
        role: 'admin',
      },
    });

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.name).toBe('Jane Doe');
  });

  test('PATCH - partial update', async ({ request }) => {
    const response = await request.patch(`/api/users/${userId}`, {
      data: { role: 'viewer' },
    });

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.role).toBe('viewer');
    expect(body.name).toBe('Jane Doe'); // unchanged
  });

  test('DELETE - remove user', async ({ request }) => {
    const response = await request.delete(`/api/users/${userId}`);
    expect(response.status()).toBe(204);

    // Verify deletion
    const getResponse = await request.get(`/api/users/${userId}`);
    expect(getResponse.status()).toBe(404);
  });
});
```

---

## Header and Auth Management

### Per-Request Headers

```typescript
test('request with custom headers', async ({ request }) => {
  const response = await request.get('/api/data', {
    headers: {
      'Authorization': 'Bearer specific-token',
      'X-Request-ID': `test-${Date.now()}`,
      'Accept-Language': 'en-US',
    },
  });
  expect(response.ok()).toBeTruthy();
});
```

### Auth Patterns

```typescript
// Pattern 1: Bearer token
test('bearer token auth', async ({ request }) => {
  const loginResponse = await request.post('/api/auth/login', {
    data: { email: 'user@example.com', password: 'password' },
  });
  const { token } = await loginResponse.json();

  const response = await request.get('/api/protected', {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(response.ok()).toBeTruthy();
});

// Pattern 2: Cookie-based auth (automatic with request fixture)
test('cookie auth via login', async ({ request }) => {
  // Login sets cookies automatically
  await request.post('/api/auth/login', {
    data: { email: 'user@example.com', password: 'password' },
  });

  // Subsequent requests include cookies
  const response = await request.get('/api/protected');
  expect(response.ok()).toBeTruthy();
});

// Pattern 3: API key
test('API key auth', async ({ playwright }) => {
  const apiContext = await playwright.request.newContext({
    baseURL: 'https://api.example.com',
    extraHTTPHeaders: {
      'X-API-Key': process.env.API_KEY!,
    },
  });

  const response = await apiContext.get('/data');
  expect(response.ok()).toBeTruthy();
  await apiContext.dispose();
});
```

---

## Response Validation Patterns

### Status Code Validation

```typescript
test('validate error responses', async ({ request }) => {
  // 400 Bad Request
  const badRequest = await request.post('/api/users', {
    data: { email: 'not-an-email' },
  });
  expect(badRequest.status()).toBe(400);
  const errors = await badRequest.json();
  expect(errors.errors).toContainEqual(
    expect.objectContaining({ field: 'email', message: expect.any(String) })
  );

  // 401 Unauthorized
  const unauthorized = await request.get('/api/protected', {
    headers: { Authorization: 'Bearer invalid-token' },
  });
  expect(unauthorized.status()).toBe(401);

  // 404 Not Found
  const notFound = await request.get('/api/users/nonexistent-id');
  expect(notFound.status()).toBe(404);

  // 429 Rate Limited
  const responses = await Promise.all(
    Array.from({ length: 100 }, () => request.get('/api/data'))
  );
  const rateLimited = responses.some(r => r.status() === 429);
  expect(rateLimited).toBe(true);
});
```

### Response Body Assertions

```typescript
test('validate response structure', async ({ request }) => {
  const response = await request.get('/api/users/1');
  const user = await response.json();

  // Structure validation
  expect(user).toMatchObject({
    id: expect.any(String),
    name: expect.any(String),
    email: expect.stringMatching(/.+@.+\..+/),
    createdAt: expect.any(String),
    role: expect.stringMatching(/^(admin|editor|viewer)$/),
  });

  // Negative checks
  expect(user).not.toHaveProperty('password');
  expect(user).not.toHaveProperty('passwordHash');
});

test('validate list response', async ({ request }) => {
  const response = await request.get('/api/users?page=1&limit=10');
  const body = await response.json();

  expect(body.data).toBeInstanceOf(Array);
  expect(body.data.length).toBeLessThanOrEqual(10);
  expect(body.pagination).toMatchObject({
    page: 1,
    limit: 10,
    total: expect.any(Number),
  });
});
```

### Response Headers Validation

```typescript
test('validate response headers', async ({ request }) => {
  const response = await request.get('/api/data');

  expect(response.headers()['content-type']).toContain('application/json');
  expect(response.headers()['cache-control']).toBeDefined();

  // Security headers
  expect(response.headers()['x-content-type-options']).toBe('nosniff');
  expect(response.headers()['x-frame-options']).toBe('DENY');
});
```

---

## JSON Schema Validation

### Using Ajv

```typescript
import Ajv from 'ajv';

const ajv = new Ajv();

const userSchema = {
  type: 'object',
  required: ['id', 'name', 'email', 'role', 'createdAt'],
  properties: {
    id: { type: 'string', format: 'uuid' },
    name: { type: 'string', minLength: 1 },
    email: { type: 'string', format: 'email' },
    role: { type: 'string', enum: ['admin', 'editor', 'viewer'] },
    createdAt: { type: 'string', format: 'date-time' },
  },
  additionalProperties: false,
};

test('response matches JSON schema', async ({ request }) => {
  const response = await request.get('/api/users/1');
  const body = await response.json();

  const validate = ajv.compile(userSchema);
  const valid = validate(body);

  if (!valid) {
    console.error('Schema validation errors:', validate.errors);
  }
  expect(valid).toBe(true);
});
```

### Schema for List Endpoints

```typescript
const userListSchema = {
  type: 'object',
  required: ['data', 'pagination'],
  properties: {
    data: {
      type: 'array',
      items: { $ref: '#/$defs/user' },
    },
    pagination: {
      type: 'object',
      required: ['page', 'limit', 'total'],
      properties: {
        page: { type: 'integer', minimum: 1 },
        limit: { type: 'integer', minimum: 1, maximum: 100 },
        total: { type: 'integer', minimum: 0 },
      },
    },
  },
  $defs: {
    user: userSchema,
  },
};
```

---

## Combining API and UI Tests

### API Setup, UI Verification

```typescript
test('create item via API, verify in UI', async ({ request, page }) => {
  // Setup: create data via API (fast)
  const createResponse = await request.post('/api/products', {
    data: {
      name: 'Test Product',
      price: 29.99,
      description: 'Created by API for UI test',
    },
  });
  const product = await createResponse.json();

  // Verify: check it appears in UI
  await page.goto('/products');
  await expect(page.getByText('Test Product')).toBeVisible();
  await expect(page.getByText('$29.99')).toBeVisible();

  // Cleanup via API
  await request.delete(`/api/products/${product.id}`);
});
```

### UI Action, API Verification

```typescript
test('form submission creates correct API record', async ({ page, request }) => {
  await page.goto('/products/new');

  // UI action
  await page.getByRole('textbox', { name: 'Name' }).fill('New Widget');
  await page.getByRole('spinbutton', { name: 'Price' }).fill('49.99');
  await page.getByRole('button', { name: 'Create' }).click();
  await page.waitForURL(/\/products\/[\w-]+/);

  // Extract ID from URL
  const url = page.url();
  const productId = url.split('/').pop();

  // Verify via API
  const response = await request.get(`/api/products/${productId}`);
  const product = await response.json();
  expect(product.name).toBe('New Widget');
  expect(product.price).toBe(49.99);
});
```

---

## File Upload and Download

### File Upload via API

```typescript
import fs from 'fs';
import path from 'path';

test('upload file via API', async ({ request }) => {
  const filePath = path.join(__dirname, 'fixtures', 'test-image.png');

  const response = await request.post('/api/uploads', {
    multipart: {
      file: {
        name: 'test-image.png',
        mimeType: 'image/png',
        buffer: fs.readFileSync(filePath),
      },
      description: 'Test upload',
    },
  });

  expect(response.status()).toBe(201);
  const body = await response.json();
  expect(body.url).toMatch(/^https?:\/\//);
  expect(body.size).toBeGreaterThan(0);
});
```

### File Download via API

```typescript
test('download file via API', async ({ request }) => {
  const response = await request.get('/api/exports/report.csv');

  expect(response.status()).toBe(200);
  expect(response.headers()['content-type']).toContain('text/csv');

  const body = await response.body();
  expect(body.length).toBeGreaterThan(0);

  // Validate CSV structure
  const text = body.toString();
  const lines = text.split('\n');
  expect(lines[0]).toContain('name,email,role'); // header row
  expect(lines.length).toBeGreaterThan(1);       // at least one data row
});
```

---

## Multipart Form Data

```typescript
test('multipart form submission', async ({ request }) => {
  const response = await request.post('/api/feedback', {
    multipart: {
      name: 'Test User',
      email: 'test@example.com',
      message: 'This is a test feedback message',
      category: 'bug',
      screenshot: {
        name: 'bug-screenshot.png',
        mimeType: 'image/png',
        buffer: Buffer.from('fake-image-data'),
      },
    },
  });

  expect(response.status()).toBe(201);
  const body = await response.json();
  expect(body.ticketId).toBeDefined();
});
```

---

## API Test Fixtures

### Reusable API Client Fixture

```typescript
// fixtures/api.ts
import { test as base, APIRequestContext } from '@playwright/test';

type ApiFixtures = {
  authenticatedApi: APIRequestContext;
  adminApi: APIRequestContext;
};

export const test = base.extend<ApiFixtures>({
  authenticatedApi: async ({ playwright }, use) => {
    const api = await playwright.request.newContext({
      baseURL: process.env.API_BASE_URL || 'http://localhost:3000',
      extraHTTPHeaders: {
        Authorization: `Bearer ${process.env.TEST_USER_TOKEN}`,
      },
    });
    await use(api);
    await api.dispose();
  },

  adminApi: async ({ playwright }, use) => {
    const api = await playwright.request.newContext({
      baseURL: process.env.API_BASE_URL || 'http://localhost:3000',
      extraHTTPHeaders: {
        Authorization: `Bearer ${process.env.TEST_ADMIN_TOKEN}`,
      },
    });
    await use(api);
    await api.dispose();
  },
});

export { expect } from '@playwright/test';
```

```typescript
// tests/admin.api.spec.ts
import { test, expect } from '../fixtures/api';

test('admin can list all users', async ({ adminApi }) => {
  const response = await adminApi.get('/api/admin/users');
  expect(response.ok()).toBeTruthy();
  const users = await response.json();
  expect(users.length).toBeGreaterThan(0);
});
```

### Data Cleanup Fixture

```typescript
export const test = base.extend<{ cleanup: string[] }>({
  cleanup: async ({ request }, use) => {
    const idsToCleanup: string[] = [];
    await use(idsToCleanup);

    // Teardown: delete all created resources
    for (const id of idsToCleanup) {
      await request.delete(`/api/resources/${id}`);
    }
  },
});

// Usage
test('create and track resource', async ({ request, cleanup }) => {
  const response = await request.post('/api/resources', {
    data: { name: 'test-resource' },
  });
  const { id } = await response.json();
  cleanup.push(id); // Automatically cleaned up after test
});
```

---

## Parallel API Testing

### Worker-Isolated Data

```typescript
// Prevent data collisions in parallel workers
test('parallel-safe API test', async ({ request }, testInfo) => {
  const uniqueSuffix = `${testInfo.workerIndex}-${Date.now()}`;

  const response = await request.post('/api/users', {
    data: {
      name: `Test User ${uniqueSuffix}`,
      email: `test-${uniqueSuffix}@example.com`,
    },
  });

  expect(response.status()).toBe(201);
});
```

### Serial API Tests (When Needed)

```typescript
// For tests with ordering dependencies
test.describe.configure({ mode: 'serial' });

test.describe('Order lifecycle', () => {
  let orderId: string;

  test('create order', async ({ request }) => {
    const response = await request.post('/api/orders', {
      data: { items: [{ sku: 'WIDGET-1', quantity: 2 }] },
    });
    orderId = (await response.json()).id;
  });

  test('pay for order', async ({ request }) => {
    const response = await request.post(`/api/orders/${orderId}/pay`, {
      data: { method: 'card', token: 'test-token' },
    });
    expect(response.status()).toBe(200);
  });

  test('ship order', async ({ request }) => {
    const response = await request.post(`/api/orders/${orderId}/ship`);
    expect(response.status()).toBe(200);
  });
});
```

---

## Mocking External APIs

### Route-Based Mocking for Integration Tests

```typescript
test('handles payment gateway failure', async ({ page }) => {
  // Mock external Stripe API
  await page.route('**/api.stripe.com/**', route => {
    route.fulfill({
      status: 500,
      body: JSON.stringify({ error: 'Payment gateway unavailable' }),
    });
  });

  await page.goto('/checkout');
  await page.getByRole('button', { name: 'Pay now' }).click();
  await expect(page.getByText('Payment service is temporarily unavailable')).toBeVisible();
});

test('handles slow external API', async ({ page }) => {
  await page.route('**/api.external-service.com/**', async route => {
    await new Promise(resolve => setTimeout(resolve, 5000));
    route.fulfill({ status: 200, body: '{}' });
  });

  await page.goto('/integration');
  await expect(page.getByText('Loading external data...')).toBeVisible();
});
```

---

## API Test Organization

### Recommended File Structure

```text
tests/
├── api/                         # Standalone API tests
│   ├── auth.api.spec.ts         # Authentication endpoints
│   ├── users.api.spec.ts        # Users CRUD
│   ├── products.api.spec.ts     # Products CRUD
│   ├── orders.api.spec.ts       # Order lifecycle
│   └── health.api.spec.ts       # Health checks
├── e2e/                         # UI tests (may use API for setup)
│   ├── checkout.spec.ts
│   └── dashboard.spec.ts
├── fixtures/
│   ├── api.ts                   # API fixtures
│   └── schemas/                 # JSON schemas
│       ├── user.schema.json
│       └── product.schema.json
└── playwright.config.ts
```

### Project Separation

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    {
      name: 'api',
      testMatch: /.*\.api\.spec\.ts/,
      use: {
        baseURL: process.env.API_URL || 'http://localhost:3000',
      },
    },
    {
      name: 'e2e',
      testMatch: /.*\.spec\.ts/,
      testIgnore: /.*\.api\.spec\.ts/,
      use: {
        baseURL: process.env.APP_URL || 'http://localhost:3000',
        ...devices['Desktop Chrome'],
      },
    },
  ],
});
```

```bash
# Run only API tests
npx playwright test --project=api

# Run only E2E tests
npx playwright test --project=e2e

# Run both
npx playwright test
```

---

## Related Resources

- [playwright-patterns.md](./playwright-patterns.md) -- network interception and mocking patterns
- [playwright-authentication.md](./playwright-authentication.md) -- API-based auth for test setup
- [playwright-ci.md](./playwright-ci.md) -- running API tests in CI pipelines
- [SKILL.md](../SKILL.md) -- parent Playwright testing skill
- [Playwright API Testing](https://playwright.dev/docs/api-testing)
- [Playwright APIRequestContext](https://playwright.dev/docs/api/class-apirequestcontext)
- [Ajv JSON Schema Validator](https://ajv.js.org/)
