# Advanced Playwright Testing Patterns

Deep-dive reference for complex testing scenarios. Use alongside the main SKILL.md.

---

## Role-Based Locators (2026 Best Practice)

Role locators are the **recommended primary approach** for element selection. They test from the user's perspective and are more resilient to implementation changes.

### Priority Order

1. **Role locators** (primary) - `getByRole()`
2. **Label/text locators** - `getByLabel()`, `getByText()`
3. **Test IDs** (fallback) - `getByTestId()`

### Examples

```typescript
import { test, expect } from '@playwright/test';

test('login with role locators', async ({ page }) => {
  await page.goto('/login');

  // Primary: Role-based (preferred)
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
  await page.getByRole('textbox', { name: 'Password' }).fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();

  // Assertions with role locators
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await expect(page.getByRole('navigation')).toContainText('Welcome');
});

test('form interactions', async ({ page }) => {
  await page.goto('/settings');

  // Checkboxes and radios
  await page.getByRole('checkbox', { name: 'Email notifications' }).check();
  await page.getByRole('radio', { name: 'Dark mode' }).check();

  // Dropdowns
  await page.getByRole('combobox', { name: 'Language' }).selectOption('en');

  // Links
  await page.getByRole('link', { name: 'Privacy Policy' }).click();
});
```

### When to Use Test IDs

Use `data-testid` when:
- Element has no accessible role or label
- Multiple identical elements need distinction
- Dynamic content without stable text

```typescript
// Fallback to test IDs for complex scenarios
await page.getByTestId('user-avatar-dropdown').click();
await page.getByTestId('chart-container').screenshot();
```

---

## Advanced Fixtures

### Database Seeding Fixture

```typescript
// fixtures/database.fixture.ts
import { test as base } from '@playwright/test';
import { prisma } from '../lib/prisma';

type DatabaseFixtures = {
  seedUser: { id: string; email: string };
  cleanupAfterTest: void;
};

export const test = base.extend<DatabaseFixtures>({
  seedUser: async ({}, use) => {
    // Create user before test
    const user = await prisma.user.create({
      data: {
        email: `test-${Date.now()}@example.com`,
        password: 'hashed_password',
      },
    });

    await use({ id: user.id, email: user.email });

    // Cleanup after test
    await prisma.user.delete({ where: { id: user.id } });
  },

  cleanupAfterTest: [async ({}, use) => {
    await use();
    // Cleanup all test data
    await prisma.user.deleteMany({
      where: { email: { contains: 'test-' } },
    });
  }, { auto: true }],
});
```

### Storage State Fixture

```typescript
// fixtures/auth.setup.ts
import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '../.auth/user.json');

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
  await page.getByRole('textbox', { name: 'Password' }).fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();

  await page.waitForURL('/dashboard');
  await page.context().storageState({ path: authFile });
});

// playwright.config.ts
export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      dependencies: ['setup'],
      use: { storageState: authFile },
    },
  ],
});
```

---

## Network Interception Patterns

### Conditional Mocking

```typescript
test('mock only specific endpoints', async ({ page }) => {
  // Mock analytics but let other requests through
  await page.route('**/api/analytics/**', route => route.abort());

  // Mock specific response
  await page.route('**/api/feature-flags', route => {
    route.fulfill({
      status: 200,
      body: JSON.stringify({ newFeature: true }),
    });
  });

  // Let everything else pass
  await page.goto('/');
});
```

### Request Modification

```typescript
test('modify request headers', async ({ page }) => {
  await page.route('**/api/**', route => {
    route.continue({
      headers: {
        ...route.request().headers(),
        'X-Test-Mode': 'true',
        'Authorization': 'Bearer test-token',
      },
    });
  });
});
```

### Response Delay Simulation

```typescript
test('handle slow network', async ({ page }) => {
  await page.route('**/api/data', async route => {
    await new Promise(resolve => setTimeout(resolve, 3000));
    route.fulfill({
      status: 200,
      body: JSON.stringify({ data: 'loaded' }),
    });
  });

  await page.goto('/data');
  await expect(page.getByRole('progressbar')).toBeVisible();
  await expect(page.getByText('loaded')).toBeVisible({ timeout: 5000 });
});
```

---

## Parallel Test Sharding

### Local Sharding

```bash
# Split tests across 4 workers
npx playwright test --shard=1/4
npx playwright test --shard=2/4
npx playwright test --shard=3/4
npx playwright test --shard=4/4
```

### CI Sharding Matrix

```yaml
# .github/workflows/playwright.yml
jobs:
  test:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - run: npx playwright test --shard=${{ matrix.shard }}/4
```

---

## Component Testing

```typescript
// tests/components/Button.spec.tsx
import { test, expect } from '@playwright/experimental-ct-react';
import { Button } from '../src/components/Button';

test('button renders with text', async ({ mount }) => {
  const component = await mount(<Button>Click me</Button>);
  await expect(component).toContainText('Click me');
});

test('button handles click', async ({ mount }) => {
  let clicked = false;
  const component = await mount(
    <Button onClick={() => { clicked = true; }}>Click</Button>
  );

  await component.click();
  expect(clicked).toBe(true);
});
```

---

## Accessibility Testing

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('page has no accessibility violations', async ({ page }) => {
  await page.goto('/');

  const results = await new AxeBuilder({ page }).analyze();

  expect(results.violations).toEqual([]);
});

test('form has proper labels', async ({ page }) => {
  await page.goto('/signup');

  const results = await new AxeBuilder({ page })
    .include('form')
    .withTags(['wcag2a', 'wcag2aa'])
    .analyze();

  expect(results.violations).toEqual([]);
});
```

---

## Visual Testing Integration (2026)

### Native Playwright Visual Testing

```typescript
test('homepage visual regression', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveScreenshot('homepage.png', {
    maxDiffPixels: 100,
  });
});
```

**Limitation**: Headless Chrome renders differently across OS (Mac vs Linux CI). Consider third-party tools for cross-platform consistency.

### Percy Integration

Percy by BrowserStack provides AI-powered visual diff detection:

```typescript
// Install: npm install @percy/playwright
import { test } from '@playwright/test';
import percySnapshot from '@percy/playwright';

test('visual regression with Percy', async ({ page }) => {
  await page.goto('/dashboard');
  await percySnapshot(page, 'Dashboard');
});
```

**Percy Benefits:**
- AI filters visual noise (animations, anti-aliasing)
- Cross-browser snapshots (Chrome, Firefox, Safari, Edge)
- CI/CD integration (GitHub Actions, CircleCI, Jenkins)

### Chromatic Integration

Chromatic extends Playwright with single-import visual testing:

```typescript
// Install: npm install chromatic @chromatic-com/playwright
import { test, expect } from '@chromatic-com/playwright';

test('visual test with Chromatic', async ({ page }) => {
  await page.goto('/components');
  // Chromatic captures automatically
});
```

**Run with:**
```bash
npx chromatic --playwright
```

**Chromatic Benefits:**
- Single import change transforms E2E into visual tests
- Parallel browser testing (Chrome, Firefox, Safari, Edge)
- Storybook integration for component-level testing

### Visual Testing Decision Matrix

| Tool | Best For | Pricing | Integration Effort |
|------|----------|---------|-------------------|
| Playwright native | Simple projects, single OS | Free | Minimal |
| Percy | Staging environments, cross-browser | $199+/mo | Low |
| Chromatic | Component libraries, Storybook users | Paid | Low |
| Lost Pixel | Open source alternative | Free/Paid | Medium |

---

## WebSocket Mocking (v1.49+)

Intercept and mock WebSocket connections:

```typescript
test('mock WebSocket messages', async ({ page }) => {
  await page.routeWebSocket('wss://api.example.com/ws', ws => {
    ws.onMessage(message => {
      if (message === 'ping') {
        ws.send('pong');
      }
    });
  });

  await page.goto('/realtime-dashboard');
  await expect(page.getByText('Connected')).toBeVisible();
});

test('simulate WebSocket server messages', async ({ page }) => {
  const wsRoute = await page.routeWebSocket('wss://api.example.com/ws', ws => {
    // Send mock data after connection
    setTimeout(() => {
      ws.send(JSON.stringify({ type: 'update', data: { value: 42 } }));
    }, 100);
  });

  await page.goto('/realtime-dashboard');
  await expect(page.getByText('Value: 42')).toBeVisible();
});
```

---

## Playwright vs Cypress (2026 Comparison)

| Feature | Playwright | Cypress |
|---------|------------|---------|
| **Cross-browser** | Chromium, Firefox, WebKit | Chrome, Firefox, Edge (no Safari) |
| **Parallelization** | Native, free | Requires Cypress Cloud |
| **Language support** | JS/TS, Python, Java, C# | JavaScript/TypeScript only |
| **Mobile** | Emulation + real devices (via cloud) | Limited emulation |
| **Cross-origin** | Seamless | Requires workarounds |
| **Component testing** | Experimental | Stable |
| **AI/MCP integration** | Official MCP server available | Limited |
| **Speed** | Fast (parallel workers) | Slower (single browser) |
| **Learning curve** | Moderate | Easy |
| **Best for** | Enterprise, multi-browser, CI scale | Small teams, JS-only, DX priority |

**2026 Recommendation:**
- **Choose Playwright** for cross-browser, multi-language, CI scalability
- **Choose Cypress** for JavaScript teams prioritizing developer experience

---

## Aria Snapshots (v1.49+)

Enhanced accessibility snapshot properties:

```typescript
test('verify link accessibility', async ({ page }) => {
  await page.goto('/nav');

  // New /url property for links
  await expect(page.getByRole('link', { name: 'Home' })).toHaveAccessibleName('Home');

  // New /children for strict matching
  const nav = page.getByRole('navigation');
  await expect(nav).toMatchAriaSnapshot(`
    - navigation:
      - /children:
        - link "Home" /url: "/"
        - link "About" /url: "/about"
        - link "Contact" /url: "/contact"
  `);
});
```

---

## Related Resources

- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright Locators Guide](https://playwright.dev/docs/locators)
- [Playwright Fixtures](https://playwright.dev/docs/test-fixtures)
- [Playwright Release Notes](https://playwright.dev/docs/release-notes)
- [Chromatic Playwright Docs](https://www.chromatic.com/docs/playwright/)
- [Percy Playwright](https://docs.percy.io/docs/playwright)
