# Visual Regression Testing with Playwright

Visual regression testing strategies -- native screenshots, threshold tuning, cross-platform baselines, third-party integrations, and CI workflows for catching unintended UI changes.

## Contents

- Native toHaveScreenshot API
- Full-Page vs Element Screenshots
- Masking Dynamic Content
- Threshold Tuning
- Cross-Platform Baseline Management
- Third-Party Integrations
- Update Workflow
- CI Integration
- Responsive Visual Testing
- Dark Mode Visual Testing
- Component Visual Testing
- Anti-Patterns
- Related Resources

---

## Native toHaveScreenshot API

Playwright's built-in visual comparison uses pixel-level diffing with configurable thresholds.

### Basic Usage

```typescript
import { test, expect } from '@playwright/test';

test('homepage visual regression', async ({ page }) => {
  await page.goto('/');
  // Wait for dynamic content to settle
  await page.waitForLoadState('networkidle');
  await expect(page).toHaveScreenshot('homepage.png');
});

test('login form visual', async ({ page }) => {
  await page.goto('/login');
  const form = page.getByRole('form');
  await expect(form).toHaveScreenshot('login-form.png');
});
```

### First Run: Generate Baselines

```bash
# Generate baseline screenshots (first time)
npx playwright test --update-snapshots

# Generated files:
# tests/homepage.spec.ts-snapshots/
#   homepage-chromium-linux.png
#   homepage-firefox-linux.png
#   homepage-webkit-linux.png
```

### Configuration

```typescript
// playwright.config.ts
export default defineConfig({
  expect: {
    toHaveScreenshot: {
      maxDiffPixels: 50,           // Allow up to 50 different pixels
      maxDiffPixelRatio: 0.01,     // Or 1% of total pixels
      threshold: 0.2,              // Per-pixel color difference (0-1)
      animations: 'disabled',       // Disable CSS animations
    },
  },
  use: {
    screenshot: 'only-on-failure', // Capture on test failure
  },
});
```

---

## Full-Page vs Element Screenshots

### Full-Page Screenshots

```typescript
test('full page visual', async ({ page }) => {
  await page.goto('/dashboard');

  // Entire viewport
  await expect(page).toHaveScreenshot('dashboard-viewport.png');

  // Full scrollable page
  await expect(page).toHaveScreenshot('dashboard-full.png', {
    fullPage: true,
  });
});
```

### Element-Level Screenshots

```typescript
test('component visual regression', async ({ page }) => {
  await page.goto('/components');

  // Specific component
  const card = page.getByTestId('pricing-card');
  await expect(card).toHaveScreenshot('pricing-card.png');

  // Navigation bar
  const nav = page.getByRole('navigation');
  await expect(nav).toHaveScreenshot('navigation.png');

  // Footer
  const footer = page.getByRole('contentinfo');
  await expect(footer).toHaveScreenshot('footer.png');
});
```

### When to Use Each

| Approach | Best For | Drawbacks |
|----------|----------|-----------|
| Full viewport | Landing pages, marketing pages | Brittle with dynamic content |
| Full page (scrollable) | Long-form content, documentation | Large file size, slow comparison |
| Element-level | Components, forms, cards | Must identify right elements |
| Combined | Critical pages with dynamic areas masked | More test code |

---

## Masking Dynamic Content

Mask elements that change between runs to prevent false positives.

### Built-In Masking

```typescript
test('dashboard with masked dynamic content', async ({ page }) => {
  await page.goto('/dashboard');

  await expect(page).toHaveScreenshot('dashboard.png', {
    mask: [
      page.getByTestId('current-time'),           // Clock/timestamp
      page.getByTestId('user-avatar'),             // Profile image
      page.getByTestId('activity-feed'),           // Live feed
      page.getByRole('img', { name: /avatar/i }),  // All avatar images
      page.locator('.advertisement'),               // Ads
    ],
    maskColor: '#FF00FF', // Visible mask color for debugging
  });
});
```

### CSS-Based Masking

```typescript
test('mask via CSS injection', async ({ page }) => {
  await page.goto('/dashboard');

  // Hide dynamic elements via CSS
  await page.addStyleTag({
    content: `
      .timestamp, .live-indicator, .random-greeting {
        visibility: hidden !important;
      }
      .animated-element {
        animation: none !important;
        transition: none !important;
      }
    `,
  });

  await expect(page).toHaveScreenshot('dashboard-stable.png');
});
```

### Common Elements to Mask

```text
ALWAYS MASK:
  - Timestamps and clocks
  - User avatars (may vary by test account)
  - Live activity feeds
  - Advertisements
  - Random/rotating content (testimonials, tips)
  - Analytics badges / counters
  - Notification badges

CONSIDER MASKING:
  - Charts with real-time data
  - Maps (tile loading can vary)
  - Video thumbnails
  - Relative dates ("3 minutes ago")
```

---

## Threshold Tuning

### Pixel-Level Thresholds

```typescript
// Strict: exact match (component library, design system)
await expect(component).toHaveScreenshot('button.png', {
  maxDiffPixels: 0,
  threshold: 0.1,
});

// Moderate: small rendering differences allowed (most UI tests)
await expect(page).toHaveScreenshot('page.png', {
  maxDiffPixels: 50,
  threshold: 0.2,
});

// Lenient: layout check only (pages with variable content)
await expect(page).toHaveScreenshot('layout.png', {
  maxDiffPixelRatio: 0.05,  // 5% of pixels can differ
  threshold: 0.3,
});
```

### Threshold Reference

| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| `maxDiffPixels` | Absolute | 0-N | Max number of different pixels |
| `maxDiffPixelRatio` | Relative | 0-1 | Max ratio of different pixels |
| `threshold` | Per-pixel | 0-1 | Color difference sensitivity (0 = exact, 1 = any) |

### Tuning Strategy

```text
Start strict, loosen as needed:
  1. Begin with maxDiffPixels: 0
  2. Run tests 10x — note the max diff observed
  3. Set threshold to 2x the observed max
  4. If still flaky, investigate root cause before loosening further

Red flags for excessive loosening:
  - maxDiffPixels > 500 → likely masking real issues
  - maxDiffPixelRatio > 0.05 → screenshot probably too broad
  - threshold > 0.3 → missing meaningful visual changes
```

---

## Cross-Platform Baseline Management

### The OS Rendering Problem

Playwright screenshots differ across operating systems due to font rendering, anti-aliasing, and sub-pixel differences. The same page renders differently on Linux, macOS, and Windows.

### Strategy 1: Platform-Specific Baselines (Default)

```text
tests/visual.spec.ts-snapshots/
  homepage-chromium-linux.png       # CI baseline (Linux)
  homepage-chromium-darwin.png      # macOS baseline
  homepage-chromium-win32.png       # Windows baseline
```

```typescript
// Playwright auto-suffixes with platform
// No extra config needed — each OS gets its own baseline
await expect(page).toHaveScreenshot('homepage.png');
// Resolves to: homepage-chromium-{linux|darwin|win32}.png
```

### Strategy 2: Docker for Consistent Baselines

```dockerfile
# Dockerfile.playwright
FROM mcr.microsoft.com/playwright:v1.50.0-noble
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
CMD ["npx", "playwright", "test"]
```

```bash
# Generate baselines in Docker (matches CI)
docker build -t playwright-tests -f Dockerfile.playwright .
docker run --rm -v $(pwd)/tests:/app/tests playwright-tests npx playwright test --update-snapshots

# Run tests locally in same environment
docker run --rm -v $(pwd):/app playwright-tests
```

### Strategy 3: CI-Only Visual Tests

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    {
      name: 'visual-regression',
      testMatch: /.*\.visual\.spec\.ts/,
      // Only run in CI where baselines are generated
      ...(process.env.CI ? {} : { testIgnore: /.*/ }),
    },
  ],
});
```

---

## Third-Party Integrations

### Percy (BrowserStack)

```bash
npm install --save-dev @percy/cli @percy/playwright
```

```typescript
import { test } from '@playwright/test';
import percySnapshot from '@percy/playwright';

test('homepage Percy snapshot', async ({ page }) => {
  await page.goto('/');
  await page.waitForLoadState('networkidle');

  await percySnapshot(page, 'Homepage', {
    widths: [375, 768, 1280],      // Responsive widths
    minHeight: 1024,                // Minimum capture height
    percyCSS: '.ad-banner { display: none; }', // Hide dynamic elements
  });
});
```

```bash
# Run with Percy token
PERCY_TOKEN=your_token npx percy exec -- npx playwright test
```

### Chromatic

```bash
npm install --save-dev chromatic @chromatic-com/playwright
```

```typescript
// Replace Playwright import with Chromatic wrapper
import { test, expect } from '@chromatic-com/playwright';

test('dashboard visual', async ({ page }) => {
  await page.goto('/dashboard');
  // Chromatic captures automatically at end of test
});
```

```bash
# Run visual tests via Chromatic
npx chromatic --playwright -t your_project_token
```

### Argos CI

```bash
npm install --save-dev @argos-ci/playwright
```

```typescript
import { test } from '@playwright/test';
import { argosScreenshot } from '@argos-ci/playwright';

test('product page visual', async ({ page }) => {
  await page.goto('/products/1');
  await argosScreenshot(page, 'product-page');
});
```

### Tool Comparison

| Tool | Approach | Cross-Browser | Pricing | Review UI | CI Integration |
|------|----------|---------------|---------|-----------|----------------|
| **Playwright native** | Pixel diff | Per-project | Free | Diff files in PR | Manual |
| **Percy** | AI-powered diff | Chrome, Firefox, Safari, Edge | $199+/mo | Web dashboard | GitHub, GitLab, Bitbucket |
| **Chromatic** | TurboSnap (changed only) | Chrome, Firefox, Safari, Edge | Free tier + paid | Web dashboard | GitHub, GitLab |
| **Argos CI** | Pixel diff + stabilization | Per-project | Free OSS, paid | Web dashboard | GitHub |
| **Lost Pixel** | Pixel diff | Per-project | Free self-hosted | Web UI | GitHub Actions |

---

## Update Workflow

### Reviewing and Approving Diffs

```bash
# 1. Run tests — failures generate diff images
npx playwright test

# 2. Review diffs in test-results/
# Each failed screenshot produces:
#   - expected.png    (baseline)
#   - actual.png      (current)
#   - diff.png        (highlighted differences)

# 3. If changes are intentional, update baselines
npx playwright test --update-snapshots

# 4. Commit updated baselines
git add tests/**/*-snapshots/
git commit -m "Update visual baselines for redesigned header"
```

### PR Workflow

```yaml
# .github/workflows/visual-tests.yml
name: Visual Regression
on: pull_request

jobs:
  visual:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx playwright install --with-deps

      - name: Run visual tests
        run: npx playwright test --project=visual-regression
        continue-on-error: true

      - name: Upload diff artifacts
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: visual-diffs
          path: test-results/
          retention-days: 7

      - name: Comment PR with diff summary
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '**Visual regression detected.** Download diff artifacts to review changes. If intentional, run `npx playwright test --update-snapshots` and commit updated baselines.'
            })
```

---

## CI Integration

### Baselines in Git vs Artifact Storage

| Approach | Pros | Cons |
|----------|------|------|
| **Git (recommended)** | Versioned, reviewable in PR, simple | Increases repo size |
| **Artifact storage** (S3, GCS) | Small repo | Complex setup, harder to review |
| **Git LFS** | Best of both | Requires LFS setup |

### Git LFS for Screenshots

```bash
# Track screenshot baselines with Git LFS
git lfs track "tests/**/*-snapshots/*.png"
git add .gitattributes
git commit -m "Track visual baselines with Git LFS"
```

### Blob Report with Visual Diffs

```typescript
// playwright.config.ts
export default defineConfig({
  reporter: [
    ['html', { open: 'never' }],
    ['blob'],  // Merge sharded results including screenshots
  ],
});
```

---

## Responsive Visual Testing

### Multiple Viewports

```typescript
const viewports = [
  { name: 'mobile', width: 375, height: 812 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1280, height: 800 },
  { name: 'wide', width: 1920, height: 1080 },
];

for (const vp of viewports) {
  test(`homepage at ${vp.name} (${vp.width}x${vp.height})`, async ({ page }) => {
    await page.setViewportSize({ width: vp.width, height: vp.height });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot(`homepage-${vp.name}.png`);
  });
}
```

### Project-Based Viewports

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    {
      name: 'mobile-visual',
      testMatch: /.*\.visual\.spec\.ts/,
      use: { ...devices['iPhone 14'], },
    },
    {
      name: 'tablet-visual',
      testMatch: /.*\.visual\.spec\.ts/,
      use: { ...devices['iPad Pro 11'], },
    },
    {
      name: 'desktop-visual',
      testMatch: /.*\.visual\.spec\.ts/,
      use: { viewport: { width: 1280, height: 800 } },
    },
  ],
});
```

---

## Dark Mode Visual Testing

```typescript
test('supports dark mode', async ({ page }) => {
  await page.goto('/');

  // Light mode baseline
  await page.emulateMedia({ colorScheme: 'light' });
  await expect(page).toHaveScreenshot('homepage-light.png');

  // Dark mode baseline
  await page.emulateMedia({ colorScheme: 'dark' });
  await expect(page).toHaveScreenshot('homepage-dark.png');
});

test('high contrast mode', async ({ page }) => {
  await page.emulateMedia({ forcedColors: 'active' });
  await page.goto('/');
  await expect(page).toHaveScreenshot('homepage-high-contrast.png');
});
```

---

## Component Visual Testing

### With Playwright Component Testing

```typescript
// tests/components/Button.visual.spec.tsx
import { test, expect } from '@playwright/experimental-ct-react';
import { Button } from '../../src/components/Button';

const variants = ['primary', 'secondary', 'danger', 'ghost'] as const;
const sizes = ['sm', 'md', 'lg'] as const;

for (const variant of variants) {
  for (const size of sizes) {
    test(`Button ${variant} ${size}`, async ({ mount }) => {
      const component = await mount(
        <Button variant={variant} size={size}>Click me</Button>
      );
      await expect(component).toHaveScreenshot(`button-${variant}-${size}.png`);
    });
  }
}

test('Button states', async ({ mount }) => {
  const component = await mount(<Button disabled>Disabled</Button>);
  await expect(component).toHaveScreenshot('button-disabled.png');
});
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Full-page screenshots of dynamic dashboards | Constant false positives | Element-level screenshots + masking |
| No `waitForLoadState` before screenshot | Captures loading states | Always wait for `networkidle` or specific element |
| Same baseline for all OS | Cross-platform rendering diffs | Platform-specific baselines or Docker |
| Overly loose thresholds | Misses real regressions | Start strict, loosen intentionally |
| Visual tests blocking every PR | Slow feedback, developer friction | Run visual suite on schedule, smoke on PR |
| No review process for baseline updates | Regressions slip in as "updates" | Require reviewer approval for baseline changes |

---

## Related Resources

- [playwright-patterns.md](./playwright-patterns.md) -- visual testing integration overview and Percy/Chromatic patterns
- [playwright-ci.md](./playwright-ci.md) -- CI setup for visual test suites
- [playwright-authentication.md](./playwright-authentication.md) -- authenticated visual testing
- [SKILL.md](../SKILL.md) -- parent Playwright testing skill
- [Playwright Visual Comparisons](https://playwright.dev/docs/test-snapshots)
- [Percy Playwright SDK](https://docs.percy.io/docs/playwright)
- [Chromatic Playwright](https://www.chromatic.com/docs/playwright/)
- [Argos CI](https://argos-ci.com/docs)
- [Lost Pixel](https://docs.lost-pixel.com/)
