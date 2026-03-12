# Playwright CI/CD Configurations

Production-ready CI/CD configurations for running Playwright tests in various environments.

---

## GitHub Actions

### Standard Configuration

```yaml
# .github/workflows/playwright.yml
name: Playwright Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    timeout-minutes: 30
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright Browsers
        run: npx playwright install --with-deps

      - name: Run Playwright tests
        run: npx playwright test

      - uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
```

### Sharded Configuration (Parallel CI)

```yaml
name: Playwright Tests (Sharded)

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright Browsers
        run: npx playwright install --with-deps

      - name: Run Playwright tests
        run: npx playwright test --shard=${{ matrix.shard }}/${{ strategy.job-total }}

      - uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with:
          name: blob-report-${{ matrix.shard }}
          path: blob-report/
          retention-days: 1

  merge-reports:
    if: ${{ !cancelled() }}
    needs: [test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Download blob reports
        uses: actions/download-artifact@v4
        with:
          path: all-blob-reports
          pattern: blob-report-*
          merge-multiple: true

      - name: Merge reports
        run: npx playwright merge-reports --reporter html ./all-blob-reports

      - uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 30
```

### With Container Service (Database)

```yaml
name: E2E Tests with Database

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22

      - run: npm ci

      - name: Run migrations
        run: npx prisma migrate deploy
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/testdb

      - name: Seed database
        run: npx prisma db seed
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/testdb

      - run: npx playwright install --with-deps

      - name: Run E2E tests
        run: npx playwright test
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/testdb
          BASE_URL: http://localhost:3000
```

---

## GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - test

playwright:
  stage: test
  image: mcr.microsoft.com/playwright:v1.57.0-jammy
  script:
    - npm ci
    - npx playwright test
  artifacts:
    when: always
    paths:
      - playwright-report/
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

---

## Azure DevOps

```yaml
# azure-pipelines.yml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: NodeTool@0
    inputs:
      versionSpec: '22.x'
    displayName: 'Install Node.js'

  - script: npm ci
    displayName: 'Install dependencies'

  - script: npx playwright install --with-deps
    displayName: 'Install Playwright browsers'

  - script: npx playwright test
    displayName: 'Run Playwright tests'
    env:
      CI: 'true'

  - task: PublishTestResults@2
    condition: succeededOrFailed()
    inputs:
      testResultsFiles: 'test-results/results.xml'
      testRunTitle: 'Playwright Tests'

  - publish: playwright-report
    artifact: playwright-report
    condition: succeededOrFailed()
```

---

## CircleCI

```yaml
# .circleci/config.yml
version: 2.1

orbs:
  node: circleci/node@5

jobs:
  playwright:
    docker:
      - image: mcr.microsoft.com/playwright:v1.57.0-jammy
    steps:
      - checkout
      - node/install-packages
      - run:
          name: Run Playwright tests
          command: |
            mkdir -p test-results
            npx playwright test
      - store_artifacts:
          path: playwright-report
      - store_test_results:
          path: test-results

workflows:
  test:
    jobs:
      - playwright
```

---

## Docker Configuration

### Dockerfile for CI

```dockerfile
# Dockerfile.playwright
FROM mcr.microsoft.com/playwright:v1.57.0-jammy

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

CMD ["npx", "playwright", "test"]
```

### Docker Compose for Local CI Simulation

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  playwright:
    build:
      context: .
      dockerfile: Dockerfile.playwright
    environment:
      - CI=true
      - BASE_URL=http://app:3000
    depends_on:
      - app
      - db
    volumes:
      - ./playwright-report:/app/playwright-report

  app:
    build: .
    ports:
      - '3000:3000'
    environment:
      - DATABASE_URL=postgresql://test:test@db:5432/testdb
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=test
      - POSTGRES_PASSWORD=test
      - POSTGRES_DB=testdb
```

---

## playwright.config.ts for CI

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,

  // CI-specific settings
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  reporter: [
    ['html', { open: 'never' }],
    ['junit', { outputFile: 'test-results/results.xml' }],
    ...(process.env.CI ? [['github'] as const] : []),
  ],

  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',

    // Capture traces on first retry
    trace: 'on-first-retry',

    // Screenshots and video on failure
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  // Start app server before tests
  webServer: process.env.CI
    ? undefined // CI handles app startup separately
    : {
        command: 'npm run dev',
        url: 'http://localhost:3000',
        reuseExistingServer: true,
      },
});
```

---

## Trace Viewer in CI

Always enable traces in CI for debugging failures:

```typescript
// playwright.config.ts
use: {
  trace: 'on-first-retry', // Captures trace on first retry
  // Or for all failures:
  trace: 'retain-on-failure',
}
```

View traces locally:
```bash
# Download artifact and run
npx playwright show-trace trace.zip
```

---

## Playwright v1.57+ Features

### Browser Channels (Chrome/Edge)

Playwright ships bundled browsers optimized for reliability. If you also want parity checks against stable Chrome/Edge, run an extra project using a browser channel:

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    {
      name: 'chrome',
      use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    },
    {
      name: 'edge',
      use: { ...devices['Desktop Edge'], channel: 'msedge' },
    },
  ],
});
```

### Speedboard (HTML Reporter)

New "Speedboard" tab shows all tests sorted by execution time:

```bash
# Generate report with speedboard
npx playwright test
npx playwright show-report
# Navigate to "Speedboard" tab to identify slow tests
```

### webServer wait Option

Wait for specific log output before starting tests:

```typescript
// playwright.config.ts
export default defineConfig({
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    wait: /ready in \d+ms/, // Wait for this log pattern
  },
});
```

### Fail CI on Rerun-Pass Flakes (Recommended)

Goal: keep retries in CI (to capture traces) but still fail if a test only passes on retry.

Implementation pattern:
1) Copy `assets/template-playwright-fail-on-flaky-reporter.js` into your repo (example: `playwright/fail-on-flaky-reporter.js`).
2) Register it in `reporter`:

```typescript
// playwright.config.ts
export default defineConfig({
  retries: 2,
  reporter: [
    ['html', { open: 'never' }],
    ['junit', { outputFile: 'test-results/results.xml' }],
    ['./playwright/fail-on-flaky-reporter.js'],
  ],
});
```

### Service Worker Network Routing (Chromium)

Network requests from Service Workers are now routable:

```typescript
test('intercept service worker requests', async ({ context }) => {
  await context.route('**/api/**', route => {
    route.fulfill({ status: 200, body: 'mocked' });
  });
  // Service Worker requests are now intercepted
});
```

Opt out with: `PLAYWRIGHT_DISABLE_SERVICE_WORKER_NETWORK=1`

---

## Real Device Testing (2026)

### BrowserStack Integration

BrowserStack supports Playwright on real iOS devices:

```typescript
// browserstack.config.ts
export default defineConfig({
  use: {
    connectOptions: {
      wsEndpoint: `wss://cdp.browserstack.com/playwright?caps=${encodeURIComponent(JSON.stringify({
        browser: 'playwright-webkit',
        os: 'ios',
        os_version: '17',
        device: 'iPhone 15 Pro',
        'browserstack.username': process.env.BROWSERSTACK_USERNAME,
        'browserstack.accessKey': process.env.BROWSERSTACK_ACCESS_KEY,
      }))}`,
    },
  },
});
```

**Supported:**

Cloud providers support a rotating set of iOS versions and devices. Prefer the newest stable iOS Safari available in the provider's device list and pin the capabilities in CI.

### LambdaTest Integration

```typescript
// lambdatest.config.ts
const caps = {
  browserName: 'webkit',
  browserVersion: 'latest',
  'LT:Options': {
    platform: 'ios',
    deviceName: 'iPhone 15',
    isRealMobile: true,
  },
};

export default defineConfig({
  use: {
    connectOptions: {
      wsEndpoint: `wss://cdp.lambdatest.com/playwright?capabilities=${encodeURIComponent(JSON.stringify(caps))}`,
    },
  },
});
```

### Android Real Device via ADB

Connect to real Android devices:

```typescript
import { _android as android } from 'playwright';

const [device] = await android.devices();
const context = await device.launchBrowser();
const page = await context.newPage();

await page.goto('https://example.com');
await expect(page).toHaveTitle(/Example/);

await context.close();
await device.close();
```

### Real Device Testing Decision Matrix

| Platform | Emulation | Real Device (Cloud) | Real Device (Local) |
| --- | --- | --- | --- |
| iOS Safari | WARNING: WebKit proxy | PASS BrowserStack/LambdaTest | FAIL Not supported |
| Android Chrome | PASS Full support | PASS Cloud providers | PASS ADB connection |
| Desktop | PASS Full support | PASS Cloud providers | PASS Local browsers |

**When to use real devices:**

- iOS Safari-specific bugs (WebKit emulation differs)
- Mobile-specific features (camera, GPS, push)
- Performance testing on actual hardware
- Compliance testing requiring real devices

---

## Updated Docker Images

Use latest Playwright Docker images:

```yaml
# GitLab CI
playwright:
  image: mcr.microsoft.com/playwright:v1.57.0-jammy

# GitHub Actions
- name: Install Playwright
  run: npx playwright install --with-deps

# Or use container
container:
  image: mcr.microsoft.com/playwright:v1.57.0-jammy
```

---

## Related Resources

- [Playwright CI](https://playwright.dev/docs/ci)
- [Playwright Docker Images](https://playwright.dev/docs/docker)
- [Trace Viewer](https://playwright.dev/docs/trace-viewer)
- [Playwright Release Notes](https://playwright.dev/docs/release-notes)
- [BrowserStack Playwright iOS](https://www.browserstack.com/guide/playwright-ios-automation)
- [LambdaTest Playwright iOS](https://www.lambdatest.com/blog/playwright-testing-on-ios-real-devices/)
