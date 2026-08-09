# Advanced Playwright Testing Patterns

Deep-dive reference for complex testing scenarios. Use alongside the main SKILL.md.

---
## Table of Contents

- [Role-Based Locators (Recommended)](#role-based-locators-recommended)
- [Priority Order](#priority-order)
- [Examples](#examples)
- [When to Use Test IDs](#when-to-use-test-ids)
- [Advanced Fixtures](#advanced-fixtures)
- [Database Seeding Fixture](#database-seeding-fixture)
- [Storage State Fixture](#storage-state-fixture)
- [Network Interception Patterns](#network-interception-patterns)
- [Conditional Mocking](#conditional-mocking)
- [Request Modification](#request-modification)
- [Response Delay Simulation](#response-delay-simulation)
- [Parallel Test Sharding](#parallel-test-sharding)
- [Local Sharding](#local-sharding)
- [Split tests across 4 workers](#split-tests-across-4-workers)
- [CI Sharding Matrix](#ci-sharding-matrix)
- [.github/workflows/playwright.yml](#githubworkflowsplaywrightyml)
- [Component Testing](#component-testing)
- [Accessibility Testing](#accessibility-testing)
- [Visual Testing Integration](#visual-testing-integration)
- [Native Playwright Visual Testing](#native-playwright-visual-testing)
- [Percy Integration](#percy-integration)
- [Chromatic Integration](#chromatic-integration)
- [Visual Testing Decision Matrix](#visual-testing-decision-matrix)
- [WebSocket Mocking (v1.49+)](#websocket-mocking-v149)
- [Playwright vs Cypress (Comparison)](#playwright-vs-cypress-comparison)
- [Aria Snapshots (v1.49+)](#aria-snapshots-v149)
- [Related Resources](#related-resources)


## Role-Based Locators (Recommended)

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

Component testing is experimental and does not respect semver. `@playwright/experimental-ct-svelte` was discontinued in v1.59. Use React, Vue, or Solid adapters. Pin the version and upgrade deliberately.

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

## Visual Testing Integration

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
| Percy | Staging environments, cross-browser | Paid, tiered (verify current pricing at https://www.browserstack.com/pricing as of 2026-07-11 — vendor pricing changes without notice) | Low |
| Chromatic | Component libraries, Storybook users | Paid, tiered (verify at https://www.chromatic.com/pricing) | Low |
| Lost Pixel | Open source alternative | Free/Paid | Medium |

---

## Clock API (Fake Timers)

Control browser time deterministically without sleeps or `setInterval` races. Install the clock before page navigation for best results.

```typescript
test('subscription banner appears after 30-day trial', async ({ page }) => {
  // Install fake clock at a specific date
  await page.clock.install({ time: new Date('2026-01-01T10:00:00') });
  await page.goto('/dashboard');

  // Jump forward 30 days
  await page.clock.fastForward('30d');

  await expect(page.getByRole('banner', { name: /trial expired/i })).toBeVisible();
});

test('countdown timer counts down correctly', async ({ page }) => {
  await page.clock.install({ time: 0 });
  await page.goto('/countdown?seconds=10');

  await page.clock.runFor(5000); // advance 5 seconds
  await expect(page.getByTestId('countdown')).toHaveText('5');
});
```

### Clock API methods

| Method | Purpose |
|--------|---------|
| `page.clock.install({ time })` | Replace Date, setTimeout, setInterval, etc. with fakes |
| `page.clock.setFixedTime(time)` | Fix `Date.now()` without stopping timers |
| `page.clock.fastForward(ms\|'Xd')` | Advance time and fire all elapsed timers |
| `page.clock.pauseAt(time)` | Advance to a point and pause |
| `page.clock.runFor(ms)` | Run timers for a duration |
| `page.clock.resume()` | Resume after `pauseAt` |

Docs: https://playwright.dev/docs/clock

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

## Playwright vs Cypress (Comparison)

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

**Recommendation:**
- **Choose Playwright** for cross-browser, multi-language, CI scalability
- **Choose Cypress** for JavaScript teams prioritizing developer experience

---

## Aria Snapshots (v1.49+, expanded in v1.60)

Enhanced accessibility snapshot properties. As of v1.60, `toMatchAriaSnapshot` works on both locators and the full page, and a new `boxes` option appends bounding-box coordinates for each element — useful for AI-driven automation that needs spatial coordinates alongside the semantic tree.

```typescript
test('verify navigation accessibility', async ({ page }) => {
  await page.goto('/nav');

  // Match against a page-level snapshot (v1.60+)
  await expect(page).toMatchAriaSnapshot(`
    - navigation:
      - link "Home" /url: "/"
      - link "About" /url: "/about"
      - link "Contact" /url: "/contact"
  `);
});

test('aria snapshot with bounding boxes for AI tools (v1.60)', async ({ page }) => {
  await page.goto('/');
  // boxes option appends [box=x,y,width,height] to each element
  const snapshot = await page.ariaSnapshot({ boxes: true });
  // snapshot string now includes spatial coordinates alongside roles/names
  console.log(snapshot);
});
```

`page.pickLocator()` (v1.59) opens an interactive element picker and copies the stable locator to the clipboard — useful during authoring.

---

## Related Resources

- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright Locators Guide](https://playwright.dev/docs/locators)
- [Playwright Fixtures](https://playwright.dev/docs/test-fixtures)
- [Playwright Release Notes](https://playwright.dev/docs/release-notes)
- [Chromatic Playwright Docs](https://www.chromatic.com/docs/playwright/)
- [Percy Playwright](https://www.browserstack.com/docs/percy/integrate/playwright)
