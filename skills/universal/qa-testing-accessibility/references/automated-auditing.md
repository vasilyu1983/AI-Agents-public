# Automated Accessibility Auditing

Integration guide for axe-core, Lighthouse CI, and Pa11y. Covers web framework integration, rule configuration, result interpretation, and false positive handling.

## Table of Contents

- [axe-core Integration](#axe-core-integration)
- [Playwright + axe-core](#playwright-axe-core)
- [Cypress + axe-core](#cypress-axe-core)
- [Jest + jsdom (Component Level)](#jest-jsdom-component-level)
- [Storybook Accessibility Addon](#storybook-accessibility-addon)
- [Lighthouse CI](#lighthouse-ci)
- [Setup](#setup)
- [GitHub Actions Integration](#github-actions-integration)
- [Pa11y](#pa11y)
- [Rule Configuration](#rule-configuration)
- [axe-core Tags](#axe-core-tags)
- [Disabling Rules](#disabling-rules)
- [Custom Rules](#custom-rules)
- [Result Interpretation](#result-interpretation)
- [Impact Levels](#impact-levels)
- [Violation Structure](#violation-structure)
- [Reading Results](#reading-results)
- [False Positive Handling](#false-positive-handling)

## Baseline: WebAIM Million 2026

The annual WebAIM Million scan of 1,000,000 home pages (report last updated 30 Mar 2026) is a benchmark for the prevalence of automatically detectable (WAVE) errors, not a conformance measure:

| Finding | 2026 | 2025 |
|---------|------|------|
| Home pages with detected WCAG 2 failures | 95.9% | 94.8% |
| Average detected errors per page | 56.1 (up 10.1%) | 51 |
| Pages with low-contrast text | 83.9% | 79.1% |
| ARIA attributes per page | over 133 (up 27% in one year) | ~106 |
| Errors on pages with vs without ARIA | 59.1 vs 42 | 57 vs 27 |

WebAIM notes the ARIA correlation does not prove ARIA caused the errors (ARIA-heavy pages are also more complex). The practical rule still holds: prefer native HTML semantics first.

Sources: [WebAIM Million (2026)](https://webaim.org/projects/million/), [WebAIM Million 2025](https://webaim.org/projects/million/2025)

## axe-core Integration

axe-core (check npm for the current version) is the default recommendation: mature rule coverage, low false-positive noise in common stacks, and integrations for most major test frameworks.

### Playwright + axe-core

```bash
npm install -D @axe-core/playwright
```

```typescript
// tests/accessibility/homepage.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('homepage passes axe accessibility checks', async ({ page }) => {
  await page.goto('/');

  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
    .analyze();

  expect(results.violations).toEqual([]);
});

test('homepage passes axe with baseline exclusions', async ({ page }) => {
  await page.goto('/');

  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
    .exclude('#legacy-widget')  // exclude known legacy component
    .analyze();

  expect(results.violations.filter(v =>
    v.impact === 'critical' || v.impact === 'serious'
  )).toEqual([]);
});
```

### Cypress + axe-core

```bash
npm install -D cypress-axe axe-core
```

```javascript
// cypress/support/e2e.js
import 'cypress-axe';

// cypress/e2e/accessibility.cy.js
describe('Accessibility', () => {
  it('homepage has no critical violations', () => {
    cy.visit('/');
    cy.injectAxe();
    cy.checkA11y(null, {
      runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'],
      },
    }, (violations) => {
      const critical = violations.filter(v =>
        v.impact === 'critical' || v.impact === 'serious'
      );
      expect(critical).to.have.length(0);
    });
  });
});
```

### Jest + jsdom (Component Level)

```bash
npm install -D jest-axe
```

```javascript
import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

test('button component is accessible', async () => {
  const { container } = render(<Button label="Submit" />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

### Storybook Accessibility Addon

```bash
npm install -D @storybook/addon-a11y
```

```javascript
// .storybook/main.js
export default {
  addons: ['@storybook/addon-a11y'],
};
```

The addon runs axe-core on every story in the Storybook panel. For CI, Storybook's docs recommend the Vitest addon (`npx storybook add @storybook/addon-vitest`); accessibility checks then run with the component tests, and only stories with `parameters.a11y.test = 'error'` fail in CI:

```javascript
// .storybook/preview.js
export default {
  parameters: {
    a11y: {
      test: 'error', // 'todo' = warn in the UI only (no CI output); 'off' = skip
      options: {
        runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'] },
      },
    },
  },
};
```

Mark known-bad components with `parameters.a11y.test = 'todo'` in their `meta` as the baseline, then remove the `todo` as each is fixed. The addon's default ruleset is WCAG 2.0/2.1 A/AA plus best practices; WCAG 2.2 rules need the `runOnly` above. Storybook disables the `region` rule by default for stories. If the Vitest addon is not usable, `@storybook/test-runner` honours the same `parameters.a11y.test`. (`axe-storybook-testing` is a separate CLI, not a helper library; `checkA11y`/`injectAxe` come from `axe-playwright`.) Source: [Storybook accessibility testing](https://storybook.js.org/docs/writing-tests/accessibility-testing).

## Lighthouse CI

Lighthouse includes accessibility as one of its audit categories. Good for broad CI gates that also track performance.

### Setup

```bash
npm install -D @lhci/cli
```

```json
// lighthouserc.json
{
  "ci": {
    "collect": {
      "url": ["http://localhost:3000/", "http://localhost:3000/login"],
      "startServerCommand": "npm run start",
      "numberOfRuns": 1
    },
    "assert": {
      "assertions": {
        "categories:accessibility": ["error", { "minScore": 0.9 }],
        "categories:best-practices": ["warn", { "minScore": 0.8 }]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

```bash
npx lhci autorun
```

The accessibility category score is a weighted average, so a page can clear `minScore: 0.9` while failing a serious audit. For a blocking gate, assert individual audits (for example `"color-contrast": "error"`, `"label": "error"`) or gate with axe directly and keep the category score as a trend signal.

### GitHub Actions Integration

```yaml
- name: Lighthouse CI
  run: |
    npm install -g @lhci/cli
    lhci autorun
  env:
    LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
```

## Pa11y

CLI-focused tool, good for simple CI pipelines without a test framework dependency.

```bash
npm install -D pa11y pa11y-ci
```

```json
// .pa11yci.json
{
  "defaults": {
    "standard": "WCAG2AA",
    "timeout": 30000,
    "wait": 1000,
    "runners": ["axe", "htmlcs"]
  },
  "urls": [
    "http://localhost:3000/",
    "http://localhost:3000/login",
    "http://localhost:3000/dashboard"
  ]
}
```

```bash
npx pa11y-ci
```

Do not copy a global `ignore` for a contrast code (for example `…1_4_3.G18.Fail`) into the defaults; scope any ignore to a documented URL or selector.

## Rule Configuration

### axe-core Tags

| Tag | Coverage |
|-----|----------|
| `wcag2a` | WCAG 2.0 Level A |
| `wcag2aa` | WCAG 2.0 Level AA |
| `wcag21a` | WCAG 2.1 Level A additions |
| `wcag21aa` | WCAG 2.1 Level AA additions |
| `wcag22aa` | WCAG 2.2 Level AA additions |
| `best-practice` | Non-WCAG best practices (optional; label results as non-conformance) |

Recommended default: `['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']` for Level AA targeting WCAG 2.2. Each axe rule carries only the tag of the WCAG version that introduced it, so dropping `wcag21a`/`wcag21aa` silently skips 2.1 rules; see [Canonical axe tag set](../SKILL.md#canonical-axe-tag-set).

### Disabling Rules

Disable only with documented justification:

```typescript
const results = await new AxeBuilder({ page })
  .disableRules(['color-contrast'])  // disabled: custom theme handles contrast
  .analyze();
```

### Custom Rules

axe-core supports custom rules for organization-specific requirements:

```javascript
axe.configure({
  rules: [{
    id: 'custom-focus-visible',
    selector: '[tabindex]',
    tags: ['custom', 'wcag2aa'],
    any: ['custom-focus-check'],
  }],
});
```

## Result Interpretation

### Impact Levels

| Impact | Action | CI Gate |
|--------|--------|---------|
| critical | Blocks assistive technology completely | Block merge |
| serious | Significant barrier for AT users | Block merge |
| moderate | Degraded experience for some users | Warn (block at staging) |
| minor | Inconvenience, not a barrier | Warn only |

### Violation Structure

```json
{
  "id": "color-contrast",
  "impact": "serious",
  "description": "Ensures foreground/background contrast meets WCAG 2 AA ratio",
  "help": "Elements must meet minimum color contrast ratio thresholds",
  "helpUrl": "https://dequeuniversity.com/rules/axe/4.13/color-contrast",
  "nodes": [
    {
      "html": "<span class='muted'>Low contrast text</span>",
      "target": [".muted"],
      "failureSummary": "Fix any: Element has insufficient contrast ratio of 2.5:1 (minimum 4.5:1)"
    }
  ]
}
```

### Reading Results

1. Check `impact` to determine severity and CI gate action.
2. Read `helpUrl` for the rule explanation and remediation guidance.
3. Look at `nodes[].target` to find the specific elements.
4. Use `nodes[].failureSummary` for the exact failure reason.

## False Positive Handling

Common false positive scenarios and how to handle them:

| Scenario | Approach |
|----------|----------|
| Color contrast on overlapping elements | Exclude the container or disable `color-contrast` with justification |
| Hidden elements flagged | Verify `aria-hidden` or `display: none` is applied correctly |
| Dynamic content not yet loaded | Add a wait for the content before scanning |
| Third-party embedded widgets | Exclude the widget container from scans |
| Custom component with valid ARIA | Verify ARIA is correct, then exclude the specific rule if truly false |

Document all exclusions in the test file with a comment explaining why.

## States, Frames, and Needs-Review Results

- axe does not test hidden regions (inactive menus, closed modals). Open each menu, dialog, validation-error state, and theme (for example dark mode) in the test, then scan again.
- `@axe-core/playwright` injects axe into all frames, and axe reaches open shadow roots (closed ones are invisible to it). Check the `frame-tested` rule's output for frames axe could not enter and record them as untested.
- `results.incomplete` holds checks axe could not decide (for example contrast over images). Route them to manual review; do not block CI on them and do not count them as passes.
- Do not disable `color-contrast` globally to silence false positives; exclude the specific selector with a comment.
