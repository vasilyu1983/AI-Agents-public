# Testing Localised Applications

Systematic testing strategies for internationalised applications. Covers pseudo-localisation, visual regression, RTL automation, pluralisation edge cases, format testing, missing translation detection, and CI integration.

---

## Why i18n Testing Is Different

Localisation bugs are invisible to monolingual development teams. A passing English test suite says nothing about Arabic layout, Polish pluralisation, or Japanese character truncation. i18n testing requires intentional, locale-aware test design.

| Bug Category | Impact | Detection Method |
|-------------|--------|-----------------|
| Truncated text | UI overflow, hidden CTAs | Visual regression, pseudo-loc |
| Wrong plural form | Grammatical errors | Plural rule testing per locale |
| Broken RTL layout | Unusable UI for ~400M users | RTL screenshot comparison |
| Hardcoded strings | Untranslated UI fragments | Static analysis, pseudo-loc |
| Format errors | Wrong date/currency display | Format assertion tests |
| Missing translations | English leaking into locale pages | CI extraction diff |

---

## Pseudo-Localisation

Pseudo-localisation replaces English strings with accented, expanded versions to expose i18n issues without waiting for real translations.

### What It Detects

- **Hardcoded strings** — untouched text stands out against accented pseudo text
- **Truncation** — expanded strings (30-50% longer) reveal overflow
- **Concatenation bugs** — broken pseudo strings expose concatenated segments
- **Character encoding** — accented characters expose UTF-8 failures
- **BiDi issues** — bracketed pseudo text reveals embedding problems

### Pseudo-Locale Formats

| Style | Example | Best For |
|-------|---------|----------|
| Accented | `[Ĥéĺĺö Ŵöŕĺð]` | Hardcoded string detection |
| Expanded | `[Heeellloooo Wooorrrllldd]` | Truncation testing |
| Mirrored | `[dlroW olleH]` | RTL layout simulation |
| Bracketed | `[Hello World]` | Missing translation detection |

### Tools and Integration

```bash
# i18next pseudo-locale plugin
npm install i18next-pseudo

# formatjs pseudo-locale generation
npx formatjs compile --pseudo-locale en-XA messages/en.json -o messages/en-XA.json
```

```typescript
// i18next configuration with pseudo-locale
import i18next from 'i18next';
import pseudo from 'i18next-pseudo';

i18next.use(pseudo).init({
  lng: 'en',
  postProcess: ['pseudo'],
  pseudo: {
    enabled: process.env.NODE_ENV === 'development',
    languageToPseudo: 'en-XA',
    letterMultiplier: 2, // 2x expansion for truncation testing
    repeatedLetters: ['a', 'e', 'i', 'o', 'u'],
    wrapped: true, // Add brackets [...]
  },
});
```

### CI Integration

```yaml
# GitHub Actions: run pseudo-locale visual tests
- name: Pseudo-locale visual regression
  run: |
    NEXT_PUBLIC_PSEUDO_LOCALE=true npx playwright test --project=pseudo-loc
  env:
    CI: true
```

---

## Visual Testing for Truncation and Layout Overflow

### Expansion Ratios by Language

| Source Length | Typical Expansion | Worst Case Languages |
|-------------|-------------------|---------------------|
| 1-10 chars | +200-300% | German, Finnish, Greek |
| 11-20 chars | +80-200% | German, Russian, French |
| 21-70 chars | +40-80% | German, Portuguese, Dutch |
| 70+ chars | +30-40% | Most European languages |

CJK languages (Chinese, Japanese, Korean) are typically shorter in character count but may be wider in pixel width due to full-width characters.

### Playwright Visual Regression Per Locale

```typescript
// tests/visual-i18n.spec.ts
import { test, expect } from '@playwright/test';

const VISUAL_TEST_LOCALES = ['en', 'de', 'ar', 'ja', 'ru'];
const CRITICAL_PAGES = ['/dashboard', '/settings', '/checkout'];

for (const locale of VISUAL_TEST_LOCALES) {
  for (const page of CRITICAL_PAGES) {
    test(`visual: ${page} in ${locale}`, async ({ page: p }) => {
      await p.goto(`/${locale}${page}`);
      await p.waitForLoadState('networkidle');

      await expect(p).toHaveScreenshot(
        `${page.replace('/', '')}-${locale}.png`,
        {
          maxDiffPixelRatio: 0.01,
          fullPage: true,
        }
      );
    });
  }
}
```

### Overflow Detection Script

```typescript
// tests/helpers/overflow-detector.ts
export async function detectOverflow(page: Page): Promise<OverflowResult[]> {
  return page.evaluate(() => {
    const overflows: Array<{ selector: string; text: string; overflow: string }> = [];

    document.querySelectorAll('*').forEach((el) => {
      const style = window.getComputedStyle(el);
      if (
        el.scrollWidth > el.clientWidth &&
        style.overflow !== 'scroll' &&
        style.overflow !== 'auto' &&
        style.overflow !== 'hidden'
      ) {
        overflows.push({
          selector: el.tagName + (el.id ? `#${el.id}` : ''),
          text: (el.textContent || '').slice(0, 50),
          overflow: `${el.scrollWidth - el.clientWidth}px`,
        });
      }
    });

    return overflows;
  });
}
```

---

## RTL Layout Testing Automation

### Automated RTL Structural Tests

```typescript
// tests/rtl-layout.spec.ts
import { test, expect } from '@playwright/test';

test.describe('RTL Layout Validation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/ar/dashboard');
  });

  test('document direction is set', async ({ page }) => {
    await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
    await expect(page.locator('html')).toHaveAttribute('lang', 'ar');
  });

  test('sidebar is on the right side', async ({ page }) => {
    const sidebar = page.locator('[data-testid="sidebar"]');
    const box = await sidebar.boundingBox();
    const viewport = page.viewportSize()!;
    expect(box!.x).toBeGreaterThan(viewport.width * 0.5);
  });

  test('no physical CSS properties leak', async ({ page }) => {
    const violations = await page.evaluate(() => {
      const issues: string[] = [];
      document.querySelectorAll('*').forEach((el) => {
        const style = window.getComputedStyle(el);
        // Check for non-zero margin-left that should be margin-inline-start
        if (el.getAttribute('style')?.includes('margin-left')) {
          issues.push(`${el.tagName}: inline style uses margin-left`);
        }
      });
      return issues;
    });
    expect(violations).toHaveLength(0);
  });

  test('directional icons are mirrored', async ({ page }) => {
    const arrows = page.locator('[data-directional="true"]');
    const count = await arrows.count();

    for (let i = 0; i < count; i++) {
      const transform = await arrows.nth(i).evaluate((el) =>
        window.getComputedStyle(el).transform
      );
      expect(transform).toContain('-1'); // scaleX(-1)
    }
  });
});
```

### Storybook RTL Testing

```typescript
// .storybook/test-runner.ts
import { getStoryContext } from '@storybook/test-runner';

export async function postRender(page, context) {
  const storyContext = await getStoryContext(page, context);

  if (storyContext.globals.locale === 'ar') {
    const dir = await page.evaluate(() => document.documentElement.dir);
    expect(dir).toBe('rtl');
  }
}
```

---

## Pluralisation Testing

### Language Plural Rule Categories

Languages have different plural rules defined by CLDR. Testing with just 0, 1, 2 is insufficient.

| Language | Forms | Categories | Test Values |
|----------|-------|------------|-------------|
| English | 2 | one, other | 0, 1, 2, 5, 100 |
| French | 2 | one, other | 0, 1, 2, 1000000 |
| Polish | 4 | one, few, many, other | 1, 2, 5, 12, 22, 0.5 |
| Arabic | 6 | zero, one, two, few, many, other | 0, 1, 2, 3, 11, 100 |
| Russian | 3 | one, few, many | 1, 2, 5, 21, 11, 111 |
| Japanese | 1 | other | 0, 1, 100 |
| Czech | 3 | one, few, other | 1, 2, 5 |

### Plural Test Matrix Generator

```typescript
// tests/helpers/plural-test-data.ts
export const PLURAL_TEST_CASES: Record<string, number[]> = {
  en: [0, 1, 2, 5, 21, 100],
  ar: [0, 1, 2, 3, 11, 100],
  pl: [0, 1, 2, 5, 12, 22],
  ru: [0, 1, 2, 5, 11, 21, 101, 111],
  ja: [0, 1, 5, 100],
  fr: [0, 1, 2, 1000000],
  cs: [0, 1, 2, 5],
};

export function getPluralTestValues(locale: string): number[] {
  const lang = locale.split('-')[0];
  return PLURAL_TEST_CASES[lang] || PLURAL_TEST_CASES['en'];
}
```

### Automated Plural Validation

```typescript
// tests/plurals.spec.ts
import { test, expect } from '@playwright/test';
import { PLURAL_TEST_CASES } from './helpers/plural-test-data';

for (const [locale, values] of Object.entries(PLURAL_TEST_CASES)) {
  for (const count of values) {
    test(`plural: ${locale} with count=${count}`, async ({ page }) => {
      await page.goto(`/${locale}/items?count=${count}`);

      const text = await page.locator('[data-testid="item-count"]').textContent();

      // No raw ICU syntax should leak
      expect(text).not.toContain('{count');
      expect(text).not.toContain('plural,');

      // No empty or undefined text
      expect(text?.trim().length).toBeGreaterThan(0);
    });
  }
}
```

---

## Date, Number, and Currency Format Testing

### Format Expectations by Locale

| Locale | Date (medium) | Number (1234.5) | Currency ($1234.50) |
|--------|--------------|-----------------|---------------------|
| en-US | Jan 15, 2026 | 1,234.5 | $1,234.50 |
| de-DE | 15.01.2026 | 1.234,5 | 1.234,50 $ |
| fr-FR | 15 janv. 2026 | 1 234,5 | 1 234,50 $ |
| ja-JP | 2026/01/15 | 1,234.5 | $1,234 |
| ar-SA | 15/01/2026 | 1,234.5 | 1,234.50 $ |
| hi-IN | 15 Jan 2026 | 1,234.5 | $1,234.50 |

### Format Assertion Tests

```typescript
// tests/formatting.spec.ts
import { test, expect } from '@playwright/test';

const FORMAT_CASES = [
  {
    locale: 'en-US',
    date: /Jan\s+15,\s+2026/,
    number: /1,234/,
    currency: /\$1,234\.50/,
  },
  {
    locale: 'de-DE',
    date: /15\.\s*01\.\s*2026|15\.\s*Jan/,
    number: /1\.234/,
    currency: /1\.234,50/,
  },
  {
    locale: 'ar-SA',
    date: /١٥|15/,
    number: /١٬٢٣٤|1,234/,
    currency: /١٬٢٣٤|1,234/,
  },
];

for (const { locale, date, number, currency } of FORMAT_CASES) {
  test(`formatting: ${locale}`, async ({ page }) => {
    await page.goto(`/${locale}/formatting-test`);

    const dateText = await page.locator('[data-testid="date-display"]').textContent();
    expect(dateText).toMatch(date);

    const numberText = await page.locator('[data-testid="number-display"]').textContent();
    expect(numberText).toMatch(number);

    const currencyText = await page.locator('[data-testid="currency-display"]').textContent();
    expect(currencyText).toMatch(currency);
  });
}
```

---

## Screenshot Comparison Across Locales

### Multi-Locale Screenshot Pipeline

```typescript
// playwright.config.ts — locale-specific projects
import { defineConfig } from '@playwright/test';

const SCREENSHOT_LOCALES = ['en', 'de', 'ar', 'ja', 'pt-BR'];

export default defineConfig({
  projects: SCREENSHOT_LOCALES.map((locale) => ({
    name: `screenshots-${locale}`,
    use: {
      locale,
      baseURL: `http://localhost:3000/${locale}`,
    },
  })),
  expect: {
    toHaveScreenshot: {
      maxDiffPixelRatio: 0.02,
      animations: 'disabled',
    },
  },
});
```

### Targeted Component Screenshots

```typescript
// tests/component-screenshots.spec.ts
const COMPONENTS = [
  { testId: 'header', name: 'header' },
  { testId: 'pricing-table', name: 'pricing' },
  { testId: 'footer', name: 'footer' },
  { testId: 'checkout-form', name: 'checkout' },
];

for (const { testId, name } of COMPONENTS) {
  test(`screenshot: ${name}`, async ({ page }) => {
    await page.goto('/');
    const component = page.locator(`[data-testid="${testId}"]`);
    await expect(component).toHaveScreenshot(`${name}.png`);
  });
}
```

---

## Missing Translation Detection in CI

### i18next-parser: Extract and Diff

```bash
# Extract all translation keys from source code
npx i18next-parser

# Compare extracted keys with existing translations
# Missing keys appear in the output JSON with empty values
```

```javascript
// i18next-parser.config.js
module.exports = {
  locales: ['en', 'de', 'ar', 'ja', 'fr', 'pt-BR'],
  output: 'locales/$LOCALE/$NAMESPACE.json',
  input: ['src/**/*.{ts,tsx}'],
  keepRemoved: false,
  failOnWarnings: true, // CI will fail on missing keys
  defaultValue: '__MISSING__',
};
```

### FormatJS: Extract and Compile

```bash
# Extract message descriptors
npx formatjs extract 'src/**/*.tsx' --out-file lang/en.json --id-interpolation-pattern '[sha512:contenthash:base64:6]'

# Compile with missing check
npx formatjs compile lang/de.json --out-file compiled/de.json --ast
```

### CI Pipeline for Missing Translations

```yaml
# .github/workflows/i18n-check.yml
name: i18n Quality Check
on: [pull_request]

jobs:
  check-translations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: npm ci

      - name: Extract translation keys
        run: npx i18next-parser

      - name: Check for missing translations
        run: |
          node scripts/check-missing-translations.js
          # Exit 1 if any locale has missing keys
```

```javascript
// scripts/check-missing-translations.js
const fs = require('fs');
const path = require('path');

const LOCALES_DIR = path.join(__dirname, '..', 'locales');
const REQUIRED_LOCALES = ['de', 'ar', 'ja', 'fr'];
let hasErrors = false;

for (const locale of REQUIRED_LOCALES) {
  const filePath = path.join(LOCALES_DIR, locale, 'common.json');
  const translations = JSON.parse(fs.readFileSync(filePath, 'utf-8'));

  const missing = Object.entries(translations)
    .filter(([, value]) => value === '__MISSING__' || value === '')
    .map(([key]) => key);

  if (missing.length > 0) {
    console.error(`[${locale}] Missing ${missing.length} translations:`);
    missing.forEach((key) => console.error(`  - ${key}`));
    hasErrors = true;
  }
}

if (hasErrors) process.exit(1);
```

---

## End-to-End Locale Switching Tests

```typescript
// tests/locale-switching.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Locale Switching', () => {
  test('switches from English to German', async ({ page }) => {
    await page.goto('/en/dashboard');

    // Switch locale via UI
    await page.click('[data-testid="locale-switcher"]');
    await page.click('[data-testid="locale-de"]');

    // URL should update
    await expect(page).toHaveURL(/\/de\/dashboard/);

    // Content should be in German
    const heading = await page.locator('h1').textContent();
    expect(heading).not.toBe('Dashboard'); // Should be translated
  });

  test('persists locale preference across navigation', async ({ page }) => {
    await page.goto('/de/dashboard');

    // Navigate to another page
    await page.click('[data-testid="nav-settings"]');
    await expect(page).toHaveURL(/\/de\/settings/);

    // Reload — locale should persist
    await page.reload();
    await expect(page).toHaveURL(/\/de\/settings/);
  });

  test('respects Accept-Language header', async ({ page, context }) => {
    await context.setExtraHTTPHeaders({
      'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
    });

    await page.goto('/');
    await expect(page).toHaveURL(/\/de\//);
  });

  test('falls back gracefully for unsupported locale', async ({ page }) => {
    await page.goto('/zz/dashboard');
    // Should redirect to default locale
    await expect(page).toHaveURL(/\/en\/dashboard/);
  });
});
```

---

## Accessibility Testing Across Locales

### Screen Reader Validation

```typescript
// tests/a11y-i18n.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const A11Y_LOCALES = ['en', 'ar', 'ja'];

for (const locale of A11Y_LOCALES) {
  test(`accessibility: ${locale} dashboard`, async ({ page }) => {
    await page.goto(`/${locale}/dashboard`);

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();

    expect(results.violations).toHaveLength(0);
  });

  test(`lang attribute: ${locale}`, async ({ page }) => {
    await page.goto(`/${locale}/dashboard`);
    const lang = await page.locator('html').getAttribute('lang');
    expect(lang).toBe(locale);
  });
}
```

---

## Test Matrix Design

### Locale Coverage Strategy

Not every locale needs every test. Categorise locales by risk profile.

| Tier | Locales | Test Coverage | Rationale |
|------|---------|---------------|-----------|
| **Tier 1: Full** | en, primary market locale | All tests: visual, functional, a11y | Revenue critical |
| **Tier 2: RTL** | ar (or he) | Full + RTL-specific | Layout direction change |
| **Tier 3: Complex script** | ja (or zh, ko) | Visual + formatting + truncation | CJK character width |
| **Tier 4: Complex plural** | pl (or ar, ru) | Plural rules + formatting | Most plural categories |
| **Tier 5: Spot check** | Remaining locales | Missing translation CI + smoke | Coverage without cost |

### Recommended Minimum Test Set

```text
Locale selection for maximum coverage with minimum tests:
  en     — baseline (LTR, simple plurals, Latin script)
  de     — longest strings (expansion testing)
  ar     — RTL + complex plurals (6 forms) + different script
  ja     — CJK characters, single plural form, different formatting
  pl     — complex plural rules (4 forms)
  pt-BR  — emerging market, different from pt-PT
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Testing only in English | Zero locale coverage | Add locale dimension to test matrix |
| Pixel-perfect screenshot thresholds | Constant false positives | Use 1-2% diff ratio, review diffs |
| Hardcoded expected strings in tests | Breaks when translations update | Test structure, not exact text |
| Testing all locales in every run | Slow CI, wasted resources | Tier-based coverage strategy |
| Skipping pseudo-localisation | Hardcoded strings ship to production | Enable pseudo-loc in dev and CI |
| Manual RTL testing only | Regressions between releases | Automate structural RTL checks |
| Ignoring format differences | Wrong dates/currencies in production | Locale-specific format assertions |

---

## Cross-References

- [rtl-support.md](rtl-support.md) — CSS logical properties, Tailwind RTL, icon mirroring
- [icu-message-format.md](icu-message-format.md) — Plural rules, select, number/date formatting
- [locale-handling.md](locale-handling.md) — Date, number, currency formatting by locale
- [translation-workflows.md](translation-workflows.md) — CI/CD pipelines, string extraction, TMS integration
- [framework-guides.md](framework-guides.md) — Framework-specific i18n setup (React, Vue, Angular, Next.js)
