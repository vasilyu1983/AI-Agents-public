# CI Accessibility Gates

Design patterns for integrating accessibility checks into CI pipelines. Covers gate thresholds, violation severity mapping, baseline management, and reporting.

## Table of Contents

- [Gate Design Principles](#gate-design-principles)
- [Violation Severity Mapping](#violation-severity-mapping)
- [Baseline Management](#baseline-management)
- [How Baselines Work](#how-baselines-work)
- [axe-core Baseline with Playwright](#axe-core-baseline-with-playwright)
- [Generating the Baseline](#generating-the-baseline)
- [Baseline Reduction Schedule](#baseline-reduction-schedule)
- [Per-Component vs Full-Page Scanning](#per-component-vs-full-page-scanning)
- [Component Scanning Strategy](#component-scanning-strategy)
- [GitHub Actions example](#github-actions-example)
- [GitHub Actions Integration](#github-actions-integration)
- [Lighthouse CI Gate](#lighthouse-ci-gate)
- [Reporting](#reporting)
- [PR Comments](#pr-comments)
- [Dashboard Tracking](#dashboard-tracking)
- [Escalation Policy](#escalation-policy)

## Gate Design Principles

- Start with an explicit team policy for which severities block vs warn; common starters block critical and serious, warn on moderate, and report minor.
- Treat tool impact levels as prioritization inputs, not as a substitute for manual accessibility judgment.
- Never block all PRs on all existing violations in a legacy codebase — use baselines.
- Prioritize by user impact, not raw violation count: a single blocker on checkout outranks fifty
  minor findings on a footer. Weight by (1) absolute blocker vs. workaround exists, (2) centrality
  of the flow, (3) breadth — a shared design-system component defect affects every consuming page.
- Never recommend an accessibility overlay/widget as a gate-passing shortcut — it does not
  resolve underlying violations, and its compliance claims are not evidence of conformity (see
  [regulatory-landscape.md](regulatory-landscape.md#accessibility-overlays-and-legal-exposure)).

## Violation Severity Mapping

axe-core impact levels commonly map to CI gate actions like this:

| axe Impact | WCAG Severity | CI Action | Examples |
|------------|---------------|-----------|----------|
| critical | Blocks AT completely | Block merge | Missing form labels on login, keyboard trap in modal |
| serious | Significant barrier | Block merge | Insufficient contrast on primary text, missing alt on informational images |
| moderate | Degraded experience | Warn (block at staging) | Missing skip navigation, heading level skip |
| minor | Inconvenience | Report only | Redundant ARIA roles, suboptimal tabindex values |

## Baseline Management

For existing projects with many violations, use a baseline approach to avoid blocking all development.

### How Baselines Work

1. Run a full accessibility scan on the current codebase.
2. Record all existing violations as a baseline snapshot.
3. CI gate compares current scan against baseline.
4. Block only on *new* violations not in the baseline.
5. Periodically reduce the baseline as violations are fixed.

### axe-core Baseline with Playwright

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import baseline from './a11y-baseline.json';

// rule|path|target — must match scripts/generate-a11y-baseline.ts
const fingerprint = (id: string, path: string, target: unknown) =>
  `${id}|${path}|${JSON.stringify(target)}`;
const known = new Set(baseline.flatMap((b: { fingerprints: string[] }) => b.fingerprints));

test('no new accessibility violations', async ({ page }) => {
  const path = '/';
  await page.goto(path);

  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
    .analyze();

  // Compare per node, not per-rule node counts: with a count diff, fixing one
  // old node and adding one new node of the same rule nets to zero and passes.
  const newNodes = results.violations.flatMap(v =>
    v.nodes
      .map(n => fingerprint(v.id, path, n.target))
      .filter(fp => !known.has(fp))
  );

  expect(newNodes).toEqual([]);
});
```

### Generating the Baseline

> A runnable version of this script is available at
> [`scripts/generate-a11y-baseline.ts`](../scripts/generate-a11y-baseline.ts).
> See [`scripts/README.md`](../scripts/README.md) for setup and usage
> (supports multiple paths, configurable axe tag set, and severity summary).
>
> Quick start:
> ```bash
> npx tsx scripts/generate-a11y-baseline.ts
> ```

The script below is the reference excerpt. The runnable file adds multi-page
support, environment-variable configuration, and a severity summary printout.

```typescript
// scripts/generate-a11y-baseline.ts (excerpt — see full file in scripts/)
import { chromium } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { writeFileSync } from 'fs';

async function generateBaseline() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(process.env.BASE_URL || 'http://localhost:3000');

  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
    .analyze();

  const baseline = results.violations.map(v => ({
    id: v.id,
    impact: v.impact,
    description: v.description,
    nodeCount: v.nodes.length,
    fingerprints: v.nodes.map(n => `${v.id}|/|${JSON.stringify(n.target)}`),
    snapshotDate: new Date().toISOString(),
  }));

  writeFileSync('tests/a11y-baseline.json', JSON.stringify(baseline, null, 2));
  await browser.close();
}

generateBaseline();
```

### Baseline Reduction Schedule

- Review baseline monthly.
- Set a quarterly reduction target (for example 20% per quarter; a policy default, not a sourced benchmark).
- Prioritize critical and serious violations first.
- Track baseline size as a team metric.

## Per-Component vs Full-Page Scanning

| Scope | When | Speed | Coverage |
|-------|------|-------|----------|
| Component scan | PR gate | Fast (< 5s per component) | Narrow — catches component-level issues |
| Page scan | PR gate (smoke) | Medium (< 30s per page) | Medium — catches page-level structure |
| Full-site scan | Staging deploy | Slow (minutes) | Broad — catches cross-page consistency |

### Component Scanning Strategy

Scan only changed components in PRs. With the Storybook Vitest addon (stories set `parameters.a11y.test = 'error'`), Vitest's `--changed` flag limits the run to stories affected by the diff:

```yaml
# GitHub Actions example
- name: Run accessibility checks on changed components
  run: npx vitest run --project=storybook --changed origin/main
```

## GitHub Actions Integration

```yaml
name: Accessibility Gate
on: [pull_request]

jobs:
  a11y:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: npm ci
      - run: npm run build
      - name: Start server
        run: npm run start &
      - name: Wait for server
        run: npx wait-on http://localhost:3000
      - name: Run axe checks
        run: npx playwright test tests/accessibility/
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: accessibility-report
          path: playwright-report/
```

## Lighthouse CI Gate

```yaml
- name: Lighthouse CI
  run: |
    npm install -g @lhci/cli
    lhci autorun
  env:
    LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
```

With `lighthouserc.json`. The accessibility category score is weighted, so `minScore: 0.9` can pass with a serious failure. Assert the audits you care about and keep the category score as a warning-level trend:

```json
{
  "ci": {
    "assert": {
      "assertions": {
        "color-contrast": "error",
        "label": "error",
        "button-name": "error",
        "image-alt": "error",
        "categories:accessibility": ["warn", { "minScore": 0.9 }]
      }
    }
  }
}
```

## Reporting

### PR Comments

Use axe report formatters to post violation summaries as PR comments:
- axe results → markdown table → GitHub PR comment via API
- Include: rule ID, impact, element count, help URL

### Dashboard Tracking

Track these metrics over time:
- Total violations by severity
- Baseline size trend
- New violations introduced per sprint
- Time to remediate critical violations
- Pages/components with zero violations (coverage percentage)

## Escalation Policy

| Situation | Action |
|-----------|--------|
| Critical violation in PR | Block merge; fix required before approval |
| Serious violation in PR | Block merge; fix or document exception with ticket |
| Moderate violation in PR | Warn in PR; create backlog ticket |
| Baseline growing instead of shrinking | Escalate to team lead; review quarterly target |
| False positive blocking PR | Add exclusion with comment; review in next baseline refresh |
