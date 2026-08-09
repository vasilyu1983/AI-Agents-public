# Accessibility CI Configuration Template

Example CI configurations for integrating accessibility gates into your pipeline.

## GitHub Actions — axe-core with Playwright

```yaml
name: Accessibility Gate
on:
  pull_request:
    branches: [main]

jobs:
  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - run: npm ci

      - run: npx playwright install --with-deps chromium

      - name: Build application
        run: npm run build

      - name: Start server
        run: npm run start &

      - name: Wait for server
        run: npx wait-on http://localhost:3000 --timeout 30000

      - name: Run accessibility tests
        run: npx playwright test tests/accessibility/ --reporter=html

      - name: Upload accessibility report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: accessibility-report
          path: playwright-report/
          retention-days: 14
```

## GitHub Actions — Lighthouse CI

```yaml
name: Lighthouse Accessibility
on:
  pull_request:
    branches: [main]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - run: npm ci && npm run build

      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli
          lhci autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
```

### lighthouserc.json

```json
{
  "ci": {
    "collect": {
      "url": [
        "http://localhost:3000/",
        "http://localhost:3000/login",
        "http://localhost:3000/dashboard"
      ],
      "startServerCommand": "npm run start",
      "numberOfRuns": 1,
      "settings": {
        "onlyCategories": ["accessibility"]
      }
    },
    "assert": {
      "assertions": {
        "categories:accessibility": ["error", { "minScore": 0.9 }]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

## Playwright Test File — axe-core Page Scan

```typescript
// tests/accessibility/pages.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const pages = [
  { name: 'Homepage', path: '/' },
  { name: 'Login', path: '/login' },
  { name: 'Dashboard', path: '/dashboard' },
  { name: 'Settings', path: '/settings' },
];

for (const { name, path } of pages) {
  test(`${name} has no critical accessibility violations`, async ({ page }) => {
    await page.goto(path);

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
      .analyze();

    const blocking = results.violations.filter(
      (v) => v.impact === 'critical' || v.impact === 'serious'
    );

    if (blocking.length > 0) {
      const summary = blocking
        .map((v) => `[${v.impact}] ${v.id}: ${v.help} (${v.nodes.length} elements)`)
        .join('\n');
      expect.soft(blocking, `Accessibility violations:\n${summary}`).toEqual([]);
    }
  });
}
```

## Playwright Test File — Component-Level with Baseline

```typescript
// tests/accessibility/components.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('navigation component is accessible', async ({ page }) => {
  await page.goto('/');

  const results = await new AxeBuilder({ page })
    .include('nav')
    .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
    .analyze();

  expect(results.violations).toEqual([]);
});

test('login form is accessible', async ({ page }) => {
  await page.goto('/login');

  const results = await new AxeBuilder({ page })
    .include('form')
    .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
    .analyze();

  expect(results.violations).toEqual([]);
});
```

## Pa11y CI Configuration

```json
{
  "defaults": {
    "standard": "WCAG2AA",
    "timeout": 30000,
    "wait": 1000,
    "chromeLaunchConfig": {
      "args": ["--no-sandbox"]
    }
  },
  "urls": [
    "http://localhost:3000/",
    "http://localhost:3000/login",
    "http://localhost:3000/dashboard"
  ]
}
```

```yaml
# GitHub Actions step
- name: Run Pa11y CI
  run: |
    npm run start &
    npx wait-on http://localhost:3000
    npx pa11y-ci
```

## Gate Threshold Configuration

Adjust these thresholds per project maturity:

| Project State | Critical | Serious | Moderate | Minor |
|---------------|----------|---------|----------|-------|
| New project | Block | Block | Warn | Ignore |
| Existing (with baseline) | Block new | Block new | Warn new | Ignore |
| Pre-compliance audit | Block | Block | Block | Warn |
