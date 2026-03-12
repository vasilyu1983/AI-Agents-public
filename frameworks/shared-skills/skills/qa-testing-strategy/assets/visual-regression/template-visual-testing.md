# Visual Regression Testing Template

Use this template for catching unintended visual changes in UI components, pages, and design systems.

## Framework Selection

**Playwright Visual Comparisons** - Best for:
- Full-page screenshots across browsers
- Component screenshot testing
- Built-in pixel-diff comparison
- CI/CD integration out of the box

**Chromatic (Storybook)** - Best for:
- Design system visual testing
- Component library regression
- Automated visual review workflow
- Cloud-based baseline management

**Percy (BrowserStack)** - Best for:
- Cross-browser visual testing
- Responsive design validation
- Integration with existing E2E tests
- Advanced diff algorithms

**BackstopJS** - Best for:
- Lightweight visual regression
- JSON configuration
- Headless browser testing
- Open-source, self-hosted

## Playwright Visual Testing

### Basic Screenshot Testing

```typescript
// components/Button.visual.test.ts
import { test, expect } from '@playwright/test'

test.describe('Button Visual Tests', () => {
  test('default button renders correctly', async ({ page }) => {
    await page.goto('/components/button')

    // Take screenshot of specific element
    const button = page.locator('[data-testid="default-button"]')
    await expect(button).toHaveScreenshot('button-default.png')
  })

  test('button states', async ({ page }) => {
    await page.goto('/components/button')

    // Hover state
    const button = page.locator('[data-testid="default-button"]')
    await button.hover()
    await expect(button).toHaveScreenshot('button-hover.png')

    // Focus state
    await button.focus()
    await expect(button).toHaveScreenshot('button-focus.png')

    // Disabled state
    const disabledButton = page.locator('[data-testid="disabled-button"]')
    await expect(disabledButton).toHaveScreenshot('button-disabled.png')
  })

  test('button variants', async ({ page }) => {
    await page.goto('/components/button')

    const variants = ['primary', 'secondary', 'outline', 'ghost', 'destructive']

    for (const variant of variants) {
      const button = page.locator(`[data-testid="button-${variant}"]`)
      await expect(button).toHaveScreenshot(`button-${variant}.png`)
    }
  })

  test('button sizes', async ({ page }) => {
    await page.goto('/components/button')

    const sizes = ['sm', 'md', 'lg']

    for (const size of sizes) {
      const button = page.locator(`[data-testid="button-${size}"]`)
      await expect(button).toHaveScreenshot(`button-size-${size}.png`)
    }
  })
})
```

### Full Page Screenshots

```typescript
// pages/Dashboard.visual.test.ts
import { test, expect } from '@playwright/test'

test.describe('Dashboard Visual Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Setup: Login and navigate
    await page.goto('/login')
    await page.fill('[name="email"]', 'test@example.com')
    await page.fill('[name="password"]', 'password')
    await page.click('button[type="submit"]')
    await page.waitForURL('/dashboard')
  })

  test('dashboard initial state', async ({ page }) => {
    // Wait for dynamic content to load
    await page.waitForLoadState('networkidle')

    // Take full page screenshot
    await expect(page).toHaveScreenshot('dashboard-initial.png', {
      fullPage: true,
      animations: 'disabled' // Disable animations for consistent screenshots
    })
  })

  test('dashboard with filters applied', async ({ page }) => {
    // Apply filters
    await page.click('[data-testid="filter-button"]')
    await page.click('[data-testid="filter-last-30-days"]')
    await page.click('[data-testid="apply-filters"]')

    // Wait for filtered data
    await page.waitForResponse(resp => resp.url().includes('/api/analytics'))
    await page.waitForLoadState('networkidle')

    await expect(page).toHaveScreenshot('dashboard-filtered.png', {
      fullPage: true
    })
  })

  test('dashboard responsive layouts', async ({ page }) => {
    const viewports = [
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1920, height: 1080 }
    ]

    for (const viewport of viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height })
      await page.waitForLoadState('networkidle')

      await expect(page).toHaveScreenshot(`dashboard-${viewport.name}.png`, {
        fullPage: true
      })
    }
  })
})
```

### Cross-Browser Visual Testing

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] }
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] }
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] }
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 13'] }
    }
  ],

  // Visual comparison settings
  expect: {
    toHaveScreenshot: {
      maxDiffPixels: 100, // Allow up to 100 pixels difference
      threshold: 0.2, // 20% threshold for pixel color difference
      animations: 'disabled'
    }
  }
})
```

### Advanced Visual Testing Techniques

```typescript
// components/Chart.visual.test.ts
import { test, expect } from '@playwright/test'

test.describe('Chart Visual Tests', () => {
  test('chart with stable mock data', async ({ page }) => {
    // Mock API to return consistent data
    await page.route('**/api/chart-data', route => {
      route.fulfill({
        status: 200,
        body: JSON.stringify({
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
          data: [10, 20, 15, 25, 30]
        })
      })
    })

    await page.goto('/dashboard/charts')

    // Wait for chart to render
    await page.waitForSelector('canvas.chart-canvas')

    // Take screenshot with mask for dynamic elements
    await expect(page).toHaveScreenshot('chart-stable.png', {
      mask: [page.locator('[data-testid="timestamp"]')] // Hide timestamp
    })
  })

  test('chart with animations complete', async ({ page }) => {
    await page.goto('/dashboard/charts')

    // Wait for animations to complete
    await page.waitForTimeout(1000) // Wait for chart animation

    await expect(page.locator('.chart-container')).toHaveScreenshot('chart-animated.png')
  })

  test('chart theme variations', async ({ page }) => {
    const themes = ['light', 'dark', 'high-contrast']

    for (const theme of themes) {
      await page.goto('/dashboard/charts')
      await page.evaluate((t) => {
        document.documentElement.setAttribute('data-theme', t)
      }, theme)

      await page.waitForTimeout(500) // Wait for theme transition

      await expect(page.locator('.chart-container')).toHaveScreenshot(`chart-${theme}.png`)
    }
  })
})
```

## Chromatic Visual Testing (Storybook)

### Story Configuration

```typescript
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react'
import { Button } from './Button'

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  parameters: {
    chromatic: {
      viewports: [375, 768, 1200], // Test multiple viewports
      delay: 300, // Wait 300ms before screenshot
      pauseAnimationAtEnd: true
    }
  }
}

export default meta
type Story = StoryObj<typeof Button>

export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Click me'
  }
}

export const AllVariants: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem', flexDirection: 'column' }}>
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="destructive">Destructive</Button>
    </div>
  ),
  parameters: {
    chromatic: { disableSnapshot: false }
  }
}

export const InteractiveStates: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem' }}>
      <Button>Default</Button>
      <Button className="hover">Hover</Button>
      <Button className="focus">Focus</Button>
      <Button disabled>Disabled</Button>
    </div>
  ),
  parameters: {
    pseudo: { hover: ['.hover'], focus: ['.focus'] } // Simulate states
  }
}

export const DarkMode: Story = {
  args: {
    variant: 'primary',
    children: 'Dark Mode'
  },
  parameters: {
    backgrounds: { default: 'dark' },
    chromatic: { modes: { dark: { theme: 'dark' } } }
  }
}
```

### Chromatic Configuration

```javascript
// .storybook/main.js
module.exports = {
  stories: ['../src/**/*.stories.@(ts|tsx)'],
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-interactions'
  ],
  framework: {
    name: '@storybook/react-vite',
    options: {}
  }
}
```

```javascript
// chromatic.config.json
{
  "projectToken": "your-project-token",
  "buildScriptName": "build-storybook",
  "exitZeroOnChanges": true,
  "exitOnceUploaded": true,
  "onlyChanged": true, // Only test changed components
  "skip": "dependabot/**", // Skip bot PRs
  "ignoreLastBuildOnBranch": "main"
}
```

## Percy Visual Testing

### Percy with Playwright

```typescript
// tests/visual/HomePage.percy.test.ts
import { test } from '@playwright/test'
import percySnapshot from '@percy/playwright'

test.describe('Home Page Visual Tests', () => {
  test('homepage renders correctly', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // Take Percy snapshot
    await percySnapshot(page, 'Homepage - Desktop')
  })

  test('homepage responsive', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // Percy automatically tests configured breakpoints
    await percySnapshot(page, 'Homepage - Responsive', {
      widths: [375, 768, 1280, 1920]
    })
  })

  test('homepage with user logged in', async ({ page, context }) => {
    // Set auth cookie
    await context.addCookies([{
      name: 'session',
      value: 'test-session-token',
      domain: 'localhost',
      path: '/'
    }])

    await page.goto('/')
    await page.waitForLoadState('networkidle')

    await percySnapshot(page, 'Homepage - Logged In')
  })

  test('homepage dark mode', async ({ page }) => {
    await page.goto('/')
    await page.evaluate(() => {
      document.documentElement.setAttribute('data-theme', 'dark')
    })
    await page.waitForTimeout(300) // Theme transition

    await percySnapshot(page, 'Homepage - Dark Mode')
  })
})
```

### Percy Configuration

```yaml
# .percy.yml
version: 2
static:
  cleanUrls: true
  include: '**/*.{html,htm}'
  exclude: '**/node_modules/**'

snapshot:
  widths:
    - 375  # Mobile
    - 768  # Tablet
    - 1280 # Desktop
    - 1920 # Large Desktop

  min-height: 1024

  # Enable Percy-specific features
  enable-javascript: true

  # CSS for stabilizing screenshots
  percy-css: |
    * {
      animation-duration: 0s !important;
      transition-duration: 0s !important;
    }
    [data-percy-hide] {
      visibility: hidden !important;
    }

discovery:
  allowed-hostnames:
    - localhost
    - '*.yourdomain.com'

  network-idle-timeout: 750
```

## BackstopJS Visual Regression

### BackstopJS Configuration

```javascript
// backstop.config.js
module.exports = {
  id: 'visual_regression_test',
  viewports: [
    {
      label: 'phone',
      width: 375,
      height: 667
    },
    {
      label: 'tablet',
      width: 768,
      height: 1024
    },
    {
      label: 'desktop',
      width: 1920,
      height: 1080
    }
  ],

  scenarios: [
    {
      label: 'Homepage',
      url: 'http://localhost:3000',
      delay: 1000,
      misMatchThreshold: 0.1,
      requireSameDimensions: true
    },
    {
      label: 'Button Component',
      url: 'http://localhost:3000/components/button',
      selectors: ['[data-testid="button-showcase"]'],
      delay: 500,
      hoverSelector: '[data-testid="button-primary"]',
      clickSelector: '[data-testid="button-toggle"]'
    },
    {
      label: 'Dashboard - Logged In',
      url: 'http://localhost:3000/dashboard',
      cookiePath: 'backstop_data/cookies.json',
      delay: 2000,
      removeSelectors: [
        '[data-testid="timestamp"]', // Hide dynamic timestamp
        '[data-testid="live-data"]'   // Hide live updating data
      ]
    },
    {
      label: 'Form Validation',
      url: 'http://localhost:3000/contact',
      onBeforeScript: 'puppet/onBefore.js',
      onReadyScript: 'puppet/fillForm.js',
      delay: 500
    }
  ],

  paths: {
    bitmaps_reference: 'backstop_data/bitmaps_reference',
    bitmaps_test: 'backstop_data/bitmaps_test',
    engine_scripts: 'backstop_data/engine_scripts',
    html_report: 'backstop_data/html_report',
    ci_report: 'backstop_data/ci_report'
  },

  report: ['browser', 'CI'],
  engine: 'puppeteer',
  engineOptions: {
    args: ['--no-sandbox']
  },

  asyncCaptureLimit: 5,
  asyncCompareLimit: 50,

  debug: false,
  debugWindow: false
}
```

### BackstopJS Custom Scripts

```javascript
// backstop_data/engine_scripts/puppet/fillForm.js
module.exports = async (page, scenario, viewport) => {
  console.log('Filling form for scenario:', scenario.label)

  // Fill form fields
  await page.type('[name="email"]', 'test@example.com')
  await page.type('[name="name"]', 'Test User')
  await page.type('[name="message"]', 'This is a test message')

  // Trigger validation by clicking submit
  await page.click('button[type="submit"]')

  // Wait for validation messages
  await page.waitForSelector('.validation-message', { timeout: 1000 })
}
```

```javascript
// backstop_data/engine_scripts/puppet/onBefore.js
module.exports = async (page, scenario, viewport) => {
  console.log('Running onBefore for:', scenario.label)

  // Set cookies for authenticated scenarios
  if (scenario.cookiePath) {
    const cookies = require(scenario.cookiePath)
    await page.setCookie(...cookies)
  }

  // Hide dynamic elements
  await page.evaluateOnNewDocument(() => {
    window.localStorage.setItem('disable-animations', 'true')
  })
}
```

## CI/CD Integration

### GitHub Actions with Playwright

```yaml
# .github/workflows/visual-tests.yml
name: Visual Regression Tests

on:
  pull_request:
    branches: [main, develop]

jobs:
  visual-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright Browsers
        run: npx playwright install --with-deps

      - name: Run visual tests
        run: npm run test:visual

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: visual-test-results
          path: test-results/
          retention-days: 30

      - name: Upload screenshots
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: failed-screenshots
          path: test-results/**/*-diff.png
```

### GitHub Actions with Chromatic

```yaml
# .github/workflows/chromatic.yml
name: Chromatic Visual Tests

on: push

jobs:
  chromatic:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0 # Full git history for Chromatic

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: npm ci

      - name: Run Chromatic
        uses: chromaui/action@v1
        with:
          projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
          buildScriptName: 'build-storybook'
          exitZeroOnChanges: true
          onlyChanged: true # Only test changed stories
```

## Best Practices Checklist

- [ ] Disable animations and transitions in visual tests
- [ ] Wait for network idle before taking screenshots
- [ ] Use data-testid attributes for stable selectors
- [ ] Mask or hide dynamic content (timestamps, live data)
- [ ] Test multiple viewports (mobile, tablet, desktop)
- [ ] Test interactive states (hover, focus, disabled)
- [ ] Test theme variations (light, dark, high-contrast)
- [ ] Use consistent mock data for charts and dynamic content
- [ ] Set appropriate mismatch thresholds (0.1% - 1%)
- [ ] Store reference screenshots in version control or cloud
- [ ] Review visual diffs in CI/CD pipeline
- [ ] Test cross-browser compatibility (Chrome, Firefox, Safari)
- [ ] Isolate component testing with Storybook

## Common Pitfalls

[FAIL] **Not waiting for content to load**:
```typescript
// Bad - Screenshot taken before content loads
await page.goto('/dashboard')
await expect(page).toHaveScreenshot()

// Good - Wait for network idle
await page.goto('/dashboard')
await page.waitForLoadState('networkidle')
await expect(page).toHaveScreenshot()
```

[FAIL] **Testing with animations enabled**:
```typescript
// Bad - Animations cause flaky tests
await expect(page).toHaveScreenshot()

// Good - Disable animations
await expect(page).toHaveScreenshot({
  animations: 'disabled'
})
```

[FAIL] **Not handling dynamic content**:
```typescript
// Bad - Timestamp causes every test to fail
await expect(page).toHaveScreenshot('dashboard.png')

// Good - Mask dynamic elements
await expect(page).toHaveScreenshot('dashboard.png', {
  mask: [page.locator('[data-testid="timestamp"]')]
})
```

[FAIL] **Overly strict thresholds**:
```typescript
// Bad - Fails on minor anti-aliasing differences
await expect(page).toHaveScreenshot({
  maxDiffPixels: 0
})

// Good - Allow minor pixel differences
await expect(page).toHaveScreenshot({
  maxDiffPixels: 100,
  threshold: 0.2
})
```

## Testing Workflow

1. **Initial baseline**: Run tests and accept all screenshots as baseline
```bash
npm run test:visual -- --update-snapshots
```

2. **Development**: Make UI changes and run tests
```bash
npm run test:visual
```

3. **Review diffs**: Check diff images for unintended changes
```bash
open test-results/*-diff.png
```

4. **Update baselines**: Accept intentional changes
```bash
npm run test:visual -- --update-snapshots
```

5. **CI/CD**: Automated visual testing on every PR

## Related Resources

See [../../references/comprehensive-testing-guide.md](../../references/comprehensive-testing-guide.md) for complete testing guide across all layers.
