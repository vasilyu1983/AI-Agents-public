# Playwright CI/CD Configurations

Production-ready CI/CD configurations for running Playwright tests in various environments.

---
## Table of Contents

- [GitHub Actions](#github-actions)
- [Standard Configuration](#standard-configuration)
- [.github/workflows/playwright.yml](#githubworkflowsplaywrightyml)
- [Sharded Configuration (Parallel CI)](#sharded-configuration-parallel-ci)
- [With Container Service (Database)](#with-container-service-database)
- [GitLab CI](#gitlab-ci)
- [.gitlab-ci.yml](#gitlab-ciyml)
- [Azure DevOps](#azure-devops)
- [azure-pipelines.yml](#azure-pipelinesyml)
- [CircleCI](#circleci)
- [.circleci/config.yml](#circleciconfigyml)
- [Docker Configuration](#docker-configuration)
- [Dockerfile for CI](#dockerfile-for-ci)
- [Dockerfile.playwright](#dockerfileplaywright)
- [Docker Compose for Local CI Simulation](#docker-compose-for-local-ci-simulation)
- [docker-compose.test.yml](#docker-composetestyml)
- [playwright.config.ts for CI](#playwrightconfigts-for-ci)
- [Trace Viewer in CI](#trace-viewer-in-ci)
- [Download artifact and run](#download-artifact-and-run)
- [Playwright v1.57+ Features (CI Conveniences)](#playwright-v157-features-ci-conveniences)
- [Browser Channels (Chrome/Edge)](#browser-channels-chromeedge)
- [Speedboard (HTML Reporter)](#speedboard-html-reporter)
- [Generate report with speedboard](#generate-report-with-speedboard)
- [Navigate to "Speedboard" tab to identify slow tests](#navigate-to-speedboard-tab-to-identify-slow-tests)
- [webServer wait Option](#webserver-wait-option)
- [Fail CI on Rerun-Pass Flakes (Recommended)](#fail-ci-on-rerun-pass-flakes-recommended)
- [Service Worker Network Routing (Chromium)](#service-worker-network-routing-chromium)
- [Real Device Testing](#real-device-testing)
- [BrowserStack Integration](#browserstack-integration)
- [LambdaTest Integration](#lambdatest-integration)
- [Android Real Device via ADB](#android-real-device-via-adb)
- [Real Device Testing Decision Matrix](#real-device-testing-decision-matrix)
- [CI Image Inputs](#ci-image-inputs)
- [GitLab CI](#gitlab-ci)
- [GitHub Actions](#github-actions)
- [Or use container](#or-use-container)
- [Related Resources](#related-resources)


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
  image: $PLAYWRIGHT_IMAGE
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

parameters:
  playwright-image:
    type: string
    default: ""  # supply the reviewed full image reference when triggering CI

orbs:
  node: circleci/node@5

jobs:
  playwright:
    docker:
      - image: << pipeline.parameters.playwright-image >>
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

Read the installed `@playwright/test` version from the lockfile or `npm ls @playwright/test --depth=0`, then select the matching OS-tagged image at https://mcr.microsoft.com/en-us/artifact/mar/playwright/tags. Store the reviewed full image reference in CI's `PLAYWRIGHT_IMAGE` input (CircleCI: `playwright-image` pipeline parameter). Package/image mismatch can leave the expected browser executable unavailable; see https://playwright.dev/docs/docker. Re-check the release notes before upgrading both together.

### Dockerfile for CI

```dockerfile
# Dockerfile.playwright
ARG PLAYWRIGHT_IMAGE
FROM ${PLAYWRIGHT_IMAGE}

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
      args:
        PLAYWRIGHT_IMAGE: ${PLAYWRIGHT_IMAGE:?set the reviewed package-matched image}
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
  // Deliberate override of the vendor default: playwright.dev/docs/ci
  // recommends workers: 1 in CI for stability. On sharded, adequately
  // provisioned runners with isolated tests, '50%' buys throughput; fall back
  // to 1 on small runners (2 vCPU) or when interference flakes appear, and use
  // test locks (1.63+) for the few tests that share a resource.
  workers: process.env.CI ? '50%' : undefined,

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

## Playwright Version Notes

Check https://playwright.dev/docs/release-notes and `npm view @playwright/test version` for the current release before pinning a version in CI images or Docker tags — this table will drift. Keep the Docker tag equal to the installed `@playwright/test` version.

| Version | Key CI-relevant changes |
|---------|-------------------------|
| 1.63 | Test locks (`{ lock: 'name' }`) for shared-resource tests; `frameLocator()` without selector searches all frames; `locator.visible()`; step `subtitle`/`params`; aria + screen snapshots in traces (`trace: { mode, snapshots: { dom, aria, screen } }`); `--add-reporter`; built-in `perfetto` reporter; `storageState({ opfs })`; typed `request.get<T>()` |
| 1.62 | Stable stories/gallery component testing (`mount('id')` from `@playwright/test`); `retryStrategy: 'isolated'`; `Reporter.preprocess()`; AbortSignal `signal` option; WebP screenshots/baselines; `storageState({ credentials })` for passkeys; `APIResponse.timing()`; bundled `npx playwright mcp` / `npx playwright cli`; headless clipboard isolated from the OS |
| 1.61 | Native passkey/virtual-authenticator testing; first-class WebStorage API; network parity (`securityDetails()`/`serverAddr()` on API responses); new `retain-on-failure-and-retries` video mode; `testInfo.errors` splits `AggregateError` into separate entries |
| 1.60 | `tracing.startHar()` / `tracing.stopHar()`; `locator.drop()` for file drag-and-drop; `test.abort()` for fixture/hook-level test termination; page-level `toMatchAriaSnapshot()`; `boxes` option on `ariaSnapshot()`; removed `Locator.ariaRef()`, `videosPath`, `videoSize` |
| 1.59 | `page.screencast` API for agentic video receipts; `browser.bind(name)` for shared browser sessions; `--debug=cli` agent debugger; `npx playwright trace open/actions/action/snapshot/close`; `retain-on-failure-and-retries` trace mode; `await using` async disposables |
| 1.58 | Removal release (see below) |
| 1.57 | Speedboard HTML reporter tab (slowest-tests view); switch to Chrome-for-Testing builds (`chrome` headed / `chrome-headless-shell` headless) |

**Breaking changes to watch:**
- v1.63: `@playwright/experimental-ct-react`, `-react17`, `-vue` no longer updated (docs say removed; last published 1.62.1 — stay on 1.62 until migrated to the stories model); Ubuntu 20.04 unsupported
- v1.62: Debian 11 unsupported
- v1.61: no breaking changes listed in the release notes
- v1.60: `Locator.ariaRef()` removed; `videosPath`/`videoSize` context options removed
- v1.59: macOS 14 WebKit support removed; `@playwright/experimental-ct-svelte` removed (last published at 1.58.2); `junit` reporter now reports some failures as `<error>`
- v1.58: `_react` and `_vue` selectors removed; `:light` selector suffix removed; `devtools` option in `browserType.launch()` removed (use `args: ['--auto-open-devtools-for-tabs']`); macOS 13 WebKit support removed

Also useful and not yet reflected in this table: `test.step(name, fn, { timeout, box })` — per-step timeout and call-site "boxing" for cleaner error attribution (see https://playwright.dev/docs/api/class-test); `--only-changed[=ref]` to run only tests affected by uncommitted/branch changes (heuristic over the import graph — always follow with a full run before a release gate).

---

## Playwright v1.57+ Features (CI Conveniences)

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

### Speedboard (HTML Reporter, v1.57+)

The "Speedboard" tab in the HTML reporter shows all tests sorted by execution time — use it to find and fix (or shard away) the slowest tests before scaling worker count:

```bash
# Generate report with speedboard
npx playwright test
npx playwright show-report
# Navigate to "Speedboard" tab to identify slow tests
```

### webServer wait Option

Use log readiness when HTTP readiness is unavailable. With both `url` and `wait`, either condition starts the run; omit `url` when the log is the required condition.

```typescript
// playwright.config.ts
export default defineConfig({
  webServer: {
    command: 'npm run dev',
    // Object with optional stdout/stderr regexes; named groups become env vars
    wait: { stdout: /ready in \d+ms/ },
  },
});
```

### Fail CI on Rerun-Pass Flakes (Recommended)

Goal: keep retries in CI (to capture traces) but still fail if a test only passes on retry.

Default pattern: use Playwright's built-in `failOnFlakyTests`.

```typescript
// playwright.config.ts
export default defineConfig({
  retries: 2,
  failOnFlakyTests: !!process.env.CI,
  reporter: [
    ['html', { open: 'never' }],
    ['junit', { outputFile: 'test-results/results.xml' }],
  ],
});
```

Legacy fallback (Playwright < 1.52 only; `failOnFlakyTests` shipped in 1.52):
1) Copy `assets/template-playwright-fail-on-flaky-reporter.js` into your repo.
2) Register it as an additional reporter.

Pair with `retryStrategy: 'isolated'` (1.62+) so retries run last in a single worker, and `trace: 'retain-on-failure-and-retries'` so the failing and passing attempts can be diffed.

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

## Real Device Testing

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

## CI Image Inputs

Use the reviewed package-matched image input from Docker Configuration:

```yaml
# GitLab CI
playwright:
  image: $PLAYWRIGHT_IMAGE

# GitHub Actions
- name: Install Playwright
  run: npx playwright install --with-deps

# Or use container
container:
  image: ${{ vars.PLAYWRIGHT_IMAGE }}
```

---

## Related Resources

- [Playwright CI](https://playwright.dev/docs/ci)
- [Playwright Docker Images](https://playwright.dev/docs/docker)
- [Trace Viewer](https://playwright.dev/docs/trace-viewer)
- [Playwright Release Notes](https://playwright.dev/docs/release-notes)
- [BrowserStack Playwright iOS](https://www.browserstack.com/guide/playwright-ios-automation)
- [LambdaTest Playwright iOS](https://www.lambdatest.com/blog/playwright-testing-on-ios-real-devices/)
