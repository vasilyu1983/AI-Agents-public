# Playwright Authentication Patterns

Authentication patterns and session management in Playwright tests -- storageState, global setup, multi-user flows, OAuth handling, and API-based login for fast, reliable auth.

## Contents

- StorageState Pattern
- Global Setup for Authentication
- Project Dependencies for Auth
- Multi-User Authentication
- Multi-Factor Auth Handling
- OAuth/OIDC Flow Testing
- API-Based Login
- Token Refresh Handling
- Session Expiry Testing
- Auth Fixture Patterns
- Persistent Auth Across Test Files
- Security Considerations
- Auth Pattern Decision Matrix
- Related Resources

---

## StorageState Pattern

StorageState saves and restores cookies and localStorage, eliminating redundant login flows across tests.

### Save Storage State

```typescript
// auth.setup.ts
import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '../.auth/user.json');

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
  await page.getByRole('textbox', { name: 'Password' }).fill('secure-password');
  await page.getByRole('button', { name: 'Sign in' }).click();

  // Wait for redirect to confirm login succeeded
  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

  // Save signed-in state
  await page.context().storageState({ path: authFile });
});
```

### Load Storage State

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  projects: [
    // Setup project runs first
    { name: 'setup', testMatch: /.*\.setup\.ts/ },

    // All test projects depend on setup
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: '.auth/user.json',
      },
      dependencies: ['setup'],
    },
  ],
});
```

### What StorageState Captures

| Captured | Not Captured |
|----------|-------------|
| Cookies (all domains) | IndexedDB |
| localStorage (all origins) | sessionStorage |
| | Service worker registrations |
| | In-memory state |

---

## Global Setup for Authentication

### When Global Setup Is Better Than StorageState

Use global setup when authentication requires actions outside the browser (API calls, database seeding).

```typescript
// global-setup.ts
import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto('http://localhost:3000/login');
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
  await page.getByRole('textbox', { name: 'Password' }).fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  // Save for all workers
  await context.storageState({ path: '.auth/user.json' });
  await browser.close();
}

export default globalSetup;
```

```typescript
// playwright.config.ts
export default defineConfig({
  globalSetup: require.resolve('./global-setup'),
  use: {
    storageState: '.auth/user.json',
  },
});
```

---

## Project Dependencies for Auth

Project dependencies let you chain setup projects and ensure auth runs before tests.

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    // Auth setup
    {
      name: 'auth-setup',
      testMatch: /auth\.setup\.ts/,
    },

    // Tests that need auth
    {
      name: 'authenticated-tests',
      testMatch: /.*\.spec\.ts/,
      dependencies: ['auth-setup'],
      use: { storageState: '.auth/user.json' },
    },

    // Tests that run without auth (public pages)
    {
      name: 'public-tests',
      testMatch: /.*\.public\.spec\.ts/,
      // No dependencies, no storageState
    },
  ],
});
```

### Dependency Chain for Complex Setups

```typescript
// Setup: database seed → auth → tests
projects: [
  {
    name: 'db-seed',
    testMatch: /db\.setup\.ts/,
  },
  {
    name: 'auth-setup',
    testMatch: /auth\.setup\.ts/,
    dependencies: ['db-seed'],
  },
  {
    name: 'e2e-tests',
    dependencies: ['auth-setup'],
    use: { storageState: '.auth/user.json' },
  },
],
```

---

## Multi-User Authentication

### Multiple Auth Files

```typescript
// auth.setup.ts
import { test as setup } from '@playwright/test';

const users = [
  { name: 'admin', email: 'admin@example.com', password: 'admin-pass', file: '.auth/admin.json' },
  { name: 'regular', email: 'user@example.com', password: 'user-pass', file: '.auth/user.json' },
  { name: 'guest', email: 'guest@example.com', password: 'guest-pass', file: '.auth/guest.json' },
];

for (const user of users) {
  setup(`authenticate as ${user.name}`, async ({ page }) => {
    await page.goto('/login');
    await page.getByRole('textbox', { name: 'Email' }).fill(user.email);
    await page.getByRole('textbox', { name: 'Password' }).fill(user.password);
    await page.getByRole('button', { name: 'Sign in' }).click();
    await page.waitForURL('/dashboard');
    await page.context().storageState({ path: user.file });
  });
}
```

### Projects Per User Role

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /auth\.setup\.ts/ },

    {
      name: 'admin-tests',
      testMatch: /.*\.admin\.spec\.ts/,
      dependencies: ['setup'],
      use: { storageState: '.auth/admin.json' },
    },
    {
      name: 'user-tests',
      testMatch: /.*\.user\.spec\.ts/,
      dependencies: ['setup'],
      use: { storageState: '.auth/user.json' },
    },
    {
      name: 'guest-tests',
      testMatch: /.*\.guest\.spec\.ts/,
      dependencies: ['setup'],
      use: { storageState: '.auth/guest.json' },
    },
  ],
});
```

### Multi-User Within a Single Test

```typescript
// collaboration.spec.ts
import { test } from '@playwright/test';

test('admin invites user to project', async ({ browser }) => {
  // Admin context
  const adminContext = await browser.newContext({
    storageState: '.auth/admin.json',
  });
  const adminPage = await adminContext.newPage();

  await adminPage.goto('/projects/123/settings');
  await adminPage.getByRole('textbox', { name: 'Invite email' }).fill('user@example.com');
  await adminPage.getByRole('button', { name: 'Send invite' }).click();

  // User context - check for invitation
  const userContext = await browser.newContext({
    storageState: '.auth/user.json',
  });
  const userPage = await userContext.newPage();

  await userPage.goto('/notifications');
  await expect(userPage.getByText('You have been invited to Project 123')).toBeVisible();

  // Cleanup
  await adminContext.close();
  await userContext.close();
});
```

---

## Multi-Factor Auth Handling

### TOTP (Time-Based One-Time Password)

```typescript
import { test as setup } from '@playwright/test';
import { authenticator } from 'otplib';

setup('authenticate with MFA', async ({ page }) => {
  // Step 1: Username/password
  await page.goto('/login');
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
  await page.getByRole('textbox', { name: 'Password' }).fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();

  // Step 2: TOTP code
  await page.waitForURL('/mfa');
  const totpSecret = process.env.TEST_TOTP_SECRET!;
  const code = authenticator.generate(totpSecret);

  await page.getByRole('textbox', { name: 'Verification code' }).fill(code);
  await page.getByRole('button', { name: 'Verify' }).click();

  await page.waitForURL('/dashboard');
  await page.context().storageState({ path: '.auth/mfa-user.json' });
});
```

### SMS/Email MFA (Test Environment)

```typescript
setup('authenticate with email MFA', async ({ page, request }) => {
  await page.goto('/login');
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
  await page.getByRole('textbox', { name: 'Password' }).fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();

  await page.waitForURL('/mfa');

  // Retrieve MFA code from test API (backend must expose this in test env)
  const codeResponse = await request.get('/api/test/mfa-code?email=user@example.com');
  const { code } = await codeResponse.json();

  await page.getByRole('textbox', { name: 'Verification code' }).fill(code);
  await page.getByRole('button', { name: 'Verify' }).click();
  await page.waitForURL('/dashboard');
  await page.context().storageState({ path: '.auth/user.json' });
});
```

---

## OAuth/OIDC Flow Testing

### Strategy: Bypass OAuth UI in Tests

```typescript
// RECOMMENDED: Use API-based auth to skip OAuth UI entirely
setup('authenticate via OAuth API', async ({ request }) => {
  // Exchange test credentials for token directly with your backend
  const response = await request.post('/api/auth/test-login', {
    data: {
      provider: 'google',
      email: 'testuser@example.com',
      testSecret: process.env.TEST_AUTH_SECRET,
    },
  });

  const { token } = await response.json();

  // Build storageState manually
  const storageState = {
    cookies: [
      {
        name: 'session',
        value: token,
        domain: 'localhost',
        path: '/',
        httpOnly: true,
        secure: false,
        sameSite: 'Lax' as const,
        expires: Date.now() / 1000 + 86400,
      },
    ],
    origins: [],
  };

  const fs = await import('fs');
  fs.writeFileSync('.auth/oauth-user.json', JSON.stringify(storageState));
});
```

### When You Must Test the Full OAuth Flow

```typescript
// Only for OAuth provider integration validation (rare, flaky by nature)
test('full Google OAuth flow', async ({ page }) => {
  await page.goto('/login');
  await page.getByRole('button', { name: 'Sign in with Google' }).click();

  // Google login page
  await page.waitForURL(/accounts\.google\.com/);
  await page.getByRole('textbox', { name: 'Email' }).fill(process.env.GOOGLE_TEST_EMAIL!);
  await page.getByRole('button', { name: 'Next' }).click();
  await page.getByRole('textbox', { name: 'Password' }).fill(process.env.GOOGLE_TEST_PASSWORD!);
  await page.getByRole('button', { name: 'Next' }).click();

  // Consent screen (may not appear on subsequent logins)
  const consentButton = page.getByRole('button', { name: 'Allow' });
  if (await consentButton.isVisible({ timeout: 3000 }).catch(() => false)) {
    await consentButton.click();
  }

  // Back to app
  await page.waitForURL('/dashboard');
});
```

---

## API-Based Login

The fastest and most reliable auth approach. Bypass the login UI entirely.

### Direct API Authentication

```typescript
// fixtures/auth.fixture.ts
import { test as base, APIRequestContext } from '@playwright/test';

async function apiLogin(request: APIRequestContext, email: string, password: string): Promise<string> {
  const response = await request.post('/api/auth/login', {
    data: { email, password },
  });

  expect(response.ok()).toBeTruthy();
  const { token } = await response.json();
  return token;
}

// Use in setup
setup('API-based auth', async ({ request, browser }) => {
  const token = await apiLogin(request, 'user@example.com', 'password');

  // Create context with auth header
  const context = await browser.newContext({
    extraHTTPHeaders: {
      Authorization: `Bearer ${token}`,
    },
  });

  await context.storageState({ path: '.auth/user.json' });
  await context.close();
});
```

### Cookie-Based API Auth

```typescript
setup('API-based cookie auth', async ({ request }) => {
  const response = await request.post('/api/auth/login', {
    data: { email: 'user@example.com', password: 'password' },
  });

  // Cookies are automatically captured by the request context
  // Save the state directly
  await request.storageState({ path: '.auth/user.json' });
});
```

---

## Token Refresh Handling

### Testing Token Expiry and Refresh

```typescript
test('handles expired token gracefully', async ({ page, context }) => {
  // Start authenticated
  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

  // Simulate expired token by clearing cookies
  await context.clearCookies();

  // Trigger a navigation that requires auth
  await page.goto('/settings');

  // App should redirect to login or refresh silently
  // Option A: redirects to login
  await expect(page).toHaveURL(/\/login/);
  // Option B: refreshes token automatically
  // await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
});

test('refresh token flow works', async ({ page }) => {
  await page.goto('/dashboard');

  // Intercept token refresh
  let refreshCalled = false;
  await page.route('**/api/auth/refresh', route => {
    refreshCalled = true;
    route.fulfill({
      status: 200,
      body: JSON.stringify({ token: 'new-valid-token', expiresIn: 3600 }),
    });
  });

  // Simulate expiry by modifying cookie
  await page.evaluate(() => {
    document.cookie = 'access_token=expired; path=/; max-age=0';
  });

  // Trigger authenticated request
  await page.getByRole('button', { name: 'Load data' }).click();
  await expect(page.getByText('Data loaded')).toBeVisible();

  expect(refreshCalled).toBe(true);
});
```

---

## Session Expiry Testing

```typescript
test('session expiry shows re-login prompt', async ({ page, context }) => {
  await page.goto('/dashboard');

  // Simulate session expiry on the server side
  await page.route('**/api/**', route => {
    route.fulfill({ status: 401, body: JSON.stringify({ error: 'Session expired' }) });
  });

  // Trigger an API call
  await page.getByRole('button', { name: 'Refresh' }).click();

  // Expect session expiry UI
  await expect(page.getByText('Your session has expired')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Sign in again' })).toBeVisible();
});

test('remember me extends session duration', async ({ page }) => {
  await page.goto('/login');
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
  await page.getByRole('textbox', { name: 'Password' }).fill('password');
  await page.getByRole('checkbox', { name: 'Remember me' }).check();
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  // Verify long-lived cookie
  const cookies = await page.context().cookies();
  const sessionCookie = cookies.find(c => c.name === 'session');
  expect(sessionCookie).toBeDefined();
  // Remember-me cookie should expire in 30 days, not session-scoped
  expect(sessionCookie!.expires).toBeGreaterThan(Date.now() / 1000 + 86400 * 7);
});
```

---

## Auth Fixture Patterns

### Reusable Auth Fixture

```typescript
// fixtures/auth.ts
import { test as base, Page, BrowserContext } from '@playwright/test';

type AuthFixtures = {
  authenticatedPage: Page;
  adminPage: Page;
};

export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: '.auth/user.json',
    });
    const page = await context.newPage();
    await use(page);
    await context.close();
  },

  adminPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: '.auth/admin.json',
    });
    const page = await context.newPage();
    await use(page);
    await context.close();
  },
});

export { expect } from '@playwright/test';
```

```typescript
// Usage in tests
import { test, expect } from '../fixtures/auth';

test('admin can manage users', async ({ adminPage }) => {
  await adminPage.goto('/admin/users');
  await expect(adminPage.getByRole('heading', { name: 'User Management' })).toBeVisible();
});

test('regular user sees dashboard', async ({ authenticatedPage }) => {
  await authenticatedPage.goto('/dashboard');
  await expect(authenticatedPage.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

---

## Persistent Auth Across Test Files

### .gitignore the Auth State

```text
# .gitignore
.auth/
```

### Auth State Lifecycle

```text
1. CI starts → auth.setup.ts runs → writes .auth/*.json
2. Test workers read .auth/*.json via storageState
3. Each worker gets its own browser context with pre-loaded auth
4. Tests run without re-authenticating
5. CI ends → .auth/ discarded (ephemeral)

Key: auth setup runs ONCE per CI run, not per test file.
```

### Handling Auth State Staleness

```typescript
// Validate auth state before test suite
setup('validate auth state', async ({ page }) => {
  // Load existing state
  const authPath = '.auth/user.json';
  const fs = await import('fs');

  if (fs.existsSync(authPath)) {
    const context = await page.context().browser()!.newContext({
      storageState: authPath,
    });
    const checkPage = await context.newPage();
    await checkPage.goto('/api/auth/me');
    const response = await checkPage.evaluate(() => document.body.innerText);

    if (response.includes('Unauthorized')) {
      // State is stale, re-authenticate
      await context.close();
      // ... perform fresh login and save new state
    } else {
      await context.close();
    }
  }
});
```

---

## Security Considerations

### Test Credentials Management

| Approach | Security | Convenience | Recommendation |
|----------|----------|-------------|----------------|
| Hardcoded in test files | Poor | High | Never in production repos |
| `.env` files (git-ignored) | Moderate | High | Local development only |
| CI secrets (GitHub/GitLab) | Good | Moderate | Standard for CI |
| Vault / secrets manager | Best | Lower | Enterprise / regulated |

### Credential Best Practices

```typescript
// .env.test (git-ignored)
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=test-password-123
TEST_ADMIN_EMAIL=admin@example.com
TEST_ADMIN_PASSWORD=admin-password-123
TEST_TOTP_SECRET=JBSWY3DPEHPK3PXP

// Usage in tests
const email = process.env.TEST_USER_EMAIL!;
const password = process.env.TEST_USER_PASSWORD!;
```

### Security Checklist

- [ ] Test credentials are never committed to version control
- [ ] `.auth/` directory is in `.gitignore`
- [ ] Test accounts have minimal permissions (principle of least privilege)
- [ ] Test accounts use separate database/tenant from production
- [ ] OAuth test accounts do not have access to real user data
- [ ] TOTP secrets for test MFA are stored in CI secrets, not code
- [ ] API test keys are scoped to test environment only
- [ ] StorageState files are treated as secrets (contain session tokens)

---

## Auth Pattern Decision Matrix

| Scenario | Recommended Pattern | Why |
|----------|-------------------|-----|
| Single user, simple login | StorageState + project deps | Simple, fast, reliable |
| Multiple user roles | Multiple auth files + projects | Clean separation |
| OAuth/SSO | API-based bypass | Avoids flaky third-party UI |
| MFA enabled | TOTP library + API fallback | Deterministic codes |
| Token refresh needed | Intercepted route tests | Controlled simulation |
| Session expiry testing | Cookie manipulation | Direct state control |
| High security / regulated | Vault + ephemeral credentials | Compliance requirement |

---

## Related Resources

- [playwright-patterns.md](./playwright-patterns.md) -- advanced Playwright patterns including fixtures and network interception
- [playwright-ci.md](./playwright-ci.md) -- CI/CD integration for authenticated test suites
- [SKILL.md](../SKILL.md) -- parent Playwright testing skill
- [Playwright Auth Docs](https://playwright.dev/docs/auth)
- [Playwright Storage State](https://playwright.dev/docs/api/class-browsercontext#browser-context-storage-state)
- [Playwright Project Dependencies](https://playwright.dev/docs/test-projects#dependencies)
