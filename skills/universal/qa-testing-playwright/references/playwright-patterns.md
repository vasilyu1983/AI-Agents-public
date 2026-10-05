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
# Split the suite into 4 shards (machines/jobs); workers are processes inside each shard
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

Since 1.62, component testing is a stable, built-in **stories and galleries** model: a story (`*.story.tsx`, one named export per scenario) wraps the component with its props, mocks and providers; a gallery page served by **your own dev server** renders stories on demand; the built-in `mount` fixture from plain `@playwright/test` navigates to the gallery and returns a Locator scoped to the story root. It is framework-agnostic (React, Vue, Svelte, Solid — anything your dev server renders). `npx playwright init-skills` installs an agent skill that scaffolds the gallery.

```typescript
// src/components/Button.story.tsx — the story owns state and records effects into the DOM
import { useState } from 'react';
import { Button } from './Button';

export const CountsClicks = () => {
  const [clicks, setClicks] = useState(0);
  return <>
    <Button title='Submit' onClick={() => setClicks(c => c + 1)} />
    <form hidden><input data-testid='click-count' readOnly value={String(clicks)} /></form>
  </>;
};
```

```typescript
// tests/components/button.spec.ts
import { test, expect } from '@playwright/test';

test('counts clicks', async ({ mount }) => {
  const component = await mount('components/Button/CountsClicks'); // story id = path under src/ + export name
  await component.getByRole('button').click();
  await expect(component.getByTestId('click-count')).toHaveValue('1');
});
```

Config: a `components` project whose `baseURL` points at the gallery page (e.g. `http://localhost:5173/playwright/gallery/index.html`), `serviceWorkers: 'block'`, `reuseContext: true`, and a `webServer` running your dev server.

**Migrating off `@playwright/experimental-ct-*`:** 1.63 announced that `experimental-ct-react`, `-react17` and `-vue` will no longer be updated, and the component-testing docs now say they "have been removed and are no longer published". `experimental-ct-svelte` was removed in 1.59. Stay on 1.62 while migrating: run the gallery project alongside the old CT project, port spec by spec (inline JSX → one story export per composition; callbacks → story state recorded into a hidden input; `hooksConfig` → story props; `ctViteConfig` → gone), then drop the ct dependency, `playwright/index.html`, `playwright/index.ts` and `playwright/.cache`, and upgrade. Watch for story ids being strings: a renamed story breaks at runtime, so type props with `mount<typeof Story>`.

Docs: https://playwright.dev/docs/test-components (migration table under "Migration from the experimental packages").

---

## Accessibility Testing

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('page has no accessibility violations', async ({ page }) => {
  await page.goto('/');

  // No tags = every axe rule, including non-WCAG best-practice rules.
  const results = await new AxeBuilder({ page }).analyze();

  expect(results.violations).toEqual([]);
});

test('form has proper labels', async ({ page }) => {
  await page.goto('/signup');

  const results = await new AxeBuilder({ page })
    .include('form')
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']) // WCAG 2.2 AA; add 'best-practice' only as a labelled non-WCAG check
    .analyze();

  expect(results.violations).toEqual([]);
});
```

Tag-set rationale, manual checks and audit scope: [qa-testing-accessibility](../../qa-testing-accessibility/SKILL.md).

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
| Percy | Staging environments, cross-browser | Paid, tiered (verify current pricing at https://www.browserstack.com/pricing — vendor pricing changes without notice) | Low |
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

  // Jump forward 30 days: ms, or a string in 'ss', 'mm:ss' or 'hh:mm:ss' form ('720:00:00')
  await page.clock.fastForward(30 * 24 * 60 * 60 * 1000);

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
| `page.clock.fastForward(ms\|'hh:mm:ss')` | Jump forward; fires due timers at most once (like reopening a laptop lid) |
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

`page.pickLocator()` (v1.59) enters an interactive picker that highlights elements with their locator and returns the clicked element's Locator; `page.cancelPickLocator()` exits.

## Newer Locator Primitives (1.62–1.63)

- `locator.visible()` (1.63) matches only visible elements; the recommended replacement for the `:visible` pseudo-class: `page.locator('button').visible().click()`.
- `page.frameLocator()` with no selector (1.63) searches every frame of the subtree: `page.frameLocator().getByRole('button').click()`. It throws if matches exist in several frames.
- `signal` option (1.62) on most actions and web-first assertions accepts an `AbortSignal` to cancel them; it does not disable the default timeout (`timeout: 0` does).

---

## Related Resources

- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright Locators Guide](https://playwright.dev/docs/locators)
- [Playwright Fixtures](https://playwright.dev/docs/test-fixtures)
- [Playwright Release Notes](https://playwright.dev/docs/release-notes)
- [Chromatic Playwright Docs](https://www.chromatic.com/docs/playwright/)
- [Percy Playwright](https://www.browserstack.com/docs/percy/integrate/playwright)
