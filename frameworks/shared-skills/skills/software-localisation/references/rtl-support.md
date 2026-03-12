# Right-to-Left (RTL) Language Support

Production patterns for Arabic, Hebrew, Persian, and other RTL languages.

---

## Core Concepts

### RTL Languages

| Language | Code | Script Direction | Notes |
|----------|------|------------------|-------|
| Arabic | ar | RTL | Most common RTL language |
| Hebrew | he | RTL | Israel, Jewish communities |
| Persian (Farsi) | fa | RTL | Iran, Afghanistan |
| Urdu | ur | RTL | Pakistan, India |
| Pashto | ps | RTL | Afghanistan, Pakistan |
| Kurdish (Sorani) | ckb | RTL | Iraq, Iran |
| Yiddish | yi | RTL | Jewish diaspora |
| Sindhi | sd | RTL | Pakistan, India |

### Bidirectional (BiDi) Text

Mixed LTR and RTL content in the same document:

```text
RTL sentence: "مرحبا بك في موقعنا"
LTR in RTL: "مرحبا بك في React 19"
Numbers: "السعر: $99.99" (numbers stay LTR)
```

---

## CSS Logical Properties

Replace physical properties (left/right) with logical ones (start/end).

### Property Mapping

| Physical (LTR) | Logical | RTL Equivalent |
|----------------|---------|----------------|
| `margin-left` | `margin-inline-start` | `margin-right` |
| `margin-right` | `margin-inline-end` | `margin-left` |
| `padding-left` | `padding-inline-start` | `padding-right` |
| `padding-right` | `padding-inline-end` | `padding-left` |
| `left` | `inset-inline-start` | `right` |
| `right` | `inset-inline-end` | `left` |
| `text-align: left` | `text-align: start` | `text-align: right` |
| `text-align: right` | `text-align: end` | `text-align: left` |
| `border-left` | `border-inline-start` | `border-right` |
| `float: left` | `float: inline-start` | `float: right` |

### Implementation

```css
/* FAIL Physical properties (breaks RTL) */
.sidebar {
  margin-left: 1rem;
  padding-right: 2rem;
  border-left: 1px solid #ccc;
  text-align: left;
}

/* PASS Logical properties (works for LTR and RTL) */
.sidebar {
  margin-inline-start: 1rem;
  padding-inline-end: 2rem;
  border-inline-start: 1px solid #ccc;
  text-align: start;
}
```

### Flexbox and Grid

```css
/* Flexbox automatically respects direction */
.nav {
  display: flex;
  gap: 1rem;
}

/* Grid with logical alignment */
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  justify-items: start; /* Logical, respects RTL */
}
```

---

## HTML dir Attribute

### Document-Level

```html
<!DOCTYPE html>
<html lang="ar" dir="rtl">
  <head>
    <meta charset="UTF-8" />
  </head>
  <body>
    <!-- All content flows RTL -->
  </body>
</html>
```

### Dynamic Direction (React)

```tsx
// components/RootLayout.tsx
import { useLocale } from 'next-intl';

const rtlLocales = ['ar', 'he', 'fa', 'ur'];

export function RootLayout({ children }: { children: React.ReactNode }) {
  const locale = useLocale();
  const dir = rtlLocales.includes(locale) ? 'rtl' : 'ltr';

  return (
    <html lang={locale} dir={dir}>
      <body>{children}</body>
    </html>
  );
}
```

### Dynamic Direction (Vue)

```vue
<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { computed, watchEffect } from 'vue';

const { locale } = useI18n();
const rtlLocales = ['ar', 'he', 'fa'];

const dir = computed(() => (rtlLocales.includes(locale.value) ? 'rtl' : 'ltr'));

watchEffect(() => {
  document.documentElement.dir = dir.value;
  document.documentElement.lang = locale.value;
});
</script>
```

### Element-Level Override

```html
<!-- RTL document with LTR code block -->
<html dir="rtl">
  <body>
    <p>هذا نص عربي</p>
    <pre dir="ltr"><code>const x = 1;</code></pre>
  </body>
</html>
```

---

## Tailwind CSS RTL Support

### Built-in RTL Variants (v3.3+)

```html
<!-- Automatic with dir="rtl" on parent -->
<div class="ml-4 rtl:mr-4 rtl:ml-0">
  Content with RTL-aware margins
</div>

<!-- Or use logical utilities -->
<div class="ms-4">
  <!-- margin-inline-start: 1rem -->
</div>
```

### Logical Utility Classes

```html
<!-- Logical spacing -->
<div class="ps-4 pe-2 ms-auto me-0">
  <!-- padding-inline-start/end, margin-inline-start/end -->
</div>

<!-- Logical borders -->
<div class="border-s-2 border-e-0 rounded-s-lg">
  <!-- border-inline-start/end, border-radius -->
</div>

<!-- Logical positioning -->
<div class="start-0 end-auto">
  <!-- inset-inline-start/end -->
</div>
```

### Custom Tailwind Config

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      // Add custom RTL-aware utilities if needed
    },
  },
  plugins: [
    // Plugin for additional RTL utilities
    function ({ addUtilities }) {
      addUtilities({
        '.flip-horizontal': {
          transform: 'scaleX(-1)',
        },
        '.rtl\\:flip-horizontal': {
          '[dir="rtl"] &': {
            transform: 'scaleX(-1)',
          },
        },
      });
    },
  ],
};
```

---

## Icons and Images

### When to Mirror

| Element | Mirror? | Example |
|---------|---------|---------|
| Directional arrows | Yes | <- -> navigation arrows |
| Back/forward icons | Yes | Browser navigation |
| Progress indicators | Yes | Step wizards, progress bars |
| Sliders | Yes | Range inputs, carousels |
| Checkmarks | No | Checkmarks are widely understood |
| Logos | No | Brand identity stays fixed |
| Photos | No | Real-world images stay fixed |
| Icons with text | Depends | Clock with numbers? No. Arrow with "Next"? Yes |

### CSS Mirroring

```css
/* Mirror specific icons in RTL */
[dir='rtl'] .icon-arrow-right {
  transform: scaleX(-1);
}

/* Or use a utility class */
.mirror-rtl {
  [dir='rtl'] & {
    transform: scaleX(-1);
  }
}
```

### React Component

```tsx
interface DirectionalIconProps {
  icon: React.ComponentType<{ className?: string }>;
  className?: string;
}

export function DirectionalIcon({ icon: Icon, className }: DirectionalIconProps) {
  return (
    <Icon
      className={cn(
        className,
        'rtl:scale-x-[-1]' // Tailwind RTL variant
      )}
    />
  );
}

// Usage
<DirectionalIcon icon={ArrowRightIcon} className="w-5 h-5" />
```

---

## Form Inputs

### Input Direction

```html
<!-- Email/URL always LTR (even in RTL context) -->
<input type="email" dir="ltr" class="text-left" />
<input type="url" dir="ltr" class="text-left" />

<!-- Phone numbers LTR -->
<input type="tel" dir="ltr" class="text-left" />

<!-- Text inputs follow document direction -->
<input type="text" />
<!-- dir inherited from parent -->
```

### React Form Component

```tsx
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  type?: string;
}

export function Input({ type = 'text', ...props }: InputProps) {
  // Force LTR for specific input types
  const forceLtr = ['email', 'url', 'tel', 'number'].includes(type);

  return (
    <input
      type={type}
      dir={forceLtr ? 'ltr' : undefined}
      className={cn(
        'w-full rounded-md border px-3 py-2',
        forceLtr && 'text-left'
      )}
      {...props}
    />
  );
}
```

### Placeholder Direction

```css
/* RTL placeholder styling */
[dir='rtl'] input::placeholder {
  text-align: right;
}

/* LTR inputs in RTL context */
[dir='rtl'] input[dir='ltr']::placeholder {
  text-align: left;
}
```

---

## Tables

### RTL Table Layout

```css
/* Tables automatically reverse in RTL */
[dir='rtl'] table {
  /* Columns flow right-to-left automatically */
}

/* Explicit text alignment */
[dir='rtl'] th,
[dir='rtl'] td {
  text-align: right; /* Or use text-align: start */
}

/* Numbers stay LTR */
[dir='rtl'] .numeric-column {
  direction: ltr;
  text-align: right; /* Align to start of RTL flow */
}
```

### React Table Component

```tsx
interface TableCellProps {
  children: React.ReactNode;
  numeric?: boolean;
}

export function TableCell({ children, numeric }: TableCellProps) {
  return (
    <td
      className={cn('px-4 py-2 text-start', numeric && 'font-mono')}
      dir={numeric ? 'ltr' : undefined}
    >
      {children}
    </td>
  );
}
```

---

## Testing RTL

### Browser DevTools

```javascript
// Toggle RTL in browser console
document.documentElement.dir = 'rtl';
document.documentElement.lang = 'ar';

// Toggle back
document.documentElement.dir = 'ltr';
document.documentElement.lang = 'en';
```

### Storybook RTL Decorator

```tsx
// .storybook/preview.tsx
import { useEffect } from 'react';

const withRTL = (Story, context) => {
  const { globals } = context;
  const dir = globals.locale === 'ar' ? 'rtl' : 'ltr';

  useEffect(() => {
    document.documentElement.dir = dir;
  }, [dir]);

  return <Story />;
};

export const decorators = [withRTL];

export const globalTypes = {
  locale: {
    name: 'Locale',
    defaultValue: 'en',
    toolbar: {
      icon: 'globe',
      items: ['en', 'ar', 'he'],
    },
  },
};
```

### Playwright RTL Tests

```typescript
// tests/rtl.spec.ts
import { test, expect } from '@playwright/test';

test.describe('RTL Support', () => {
  test('layout mirrors correctly in Arabic', async ({ page }) => {
    await page.goto('/ar/dashboard');

    // Check document direction
    const html = page.locator('html');
    await expect(html).toHaveAttribute('dir', 'rtl');

    // Check sidebar is on the right
    const sidebar = page.locator('[data-testid="sidebar"]');
    const sidebarBox = await sidebar.boundingBox();
    const viewportSize = page.viewportSize();

    expect(sidebarBox?.x).toBeGreaterThan(viewportSize!.width / 2);
  });

  test('navigation arrows are mirrored', async ({ page }) => {
    await page.goto('/ar/products');

    const nextButton = page.locator('[data-testid="next-button"] svg');
    const transform = await nextButton.evaluate((el) => {
      return window.getComputedStyle(el).transform;
    });

    // Check for scaleX(-1) transform
    expect(transform).toContain('-1');
  });
});
```

### Visual Regression Testing

```typescript
// tests/visual-rtl.spec.ts
import { test, expect } from '@playwright/test';

const locales = ['en', 'ar'];

for (const locale of locales) {
  test(`dashboard visual regression - ${locale}`, async ({ page }) => {
    await page.goto(`/${locale}/dashboard`);
    await expect(page).toHaveScreenshot(`dashboard-${locale}.png`);
  });
}
```

---

## Common Issues and Fixes

### Issue: Scrollbar Position

```css
/* Move scrollbar to left in RTL */
[dir='rtl'] {
  /* Most browsers handle this automatically */
  /* For custom scrollbars: */
  &::-webkit-scrollbar {
    /* Scrollbar styling */
  }
}
```

### Issue: Absolute Positioning

```css
/* FAIL Breaks in RTL */
.tooltip {
  position: absolute;
  left: 100%;
}

/* PASS Works in both directions */
.tooltip {
  position: absolute;
  inset-inline-start: 100%;
}
```

### Issue: Border Radius

```css
/* FAIL Physical corners */
.card {
  border-radius: 8px 0 0 8px;
}

/* PASS Logical corners */
.card {
  border-start-start-radius: 8px;
  border-end-start-radius: 8px;
}
```

### Issue: Transitions and Animations

```css
/* Reverse animation direction for RTL */
@keyframes slide-in {
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
}

[dir='rtl'] .slide-in {
  animation-direction: reverse;
}

/* Or use logical values */
@keyframes slide-in-logical {
  from {
    inset-inline-start: -100%;
  }
  to {
    inset-inline-start: 0;
  }
}
```

---

## RTL Checklist

### Initial Setup

- REQUIRED: Add `dir` attribute to `<html>` element dynamically
- REQUIRED: Use CSS logical properties throughout codebase
- REQUIRED: Configure Tailwind RTL variants (if using Tailwind)
- REQUIRED: Set up RTL toggle in Storybook/dev environment

### Components

- REQUIRED: Replace `left`/`right` with `start`/`end` in CSS
- REQUIRED: Mirror directional icons (arrows, chevrons)
- REQUIRED: Keep logos and photos non-mirrored
- REQUIRED: Force LTR for email, URL, phone inputs
- REQUIRED: Handle numeric data direction

### Testing

- REQUIRED: Visual regression tests for RTL locales
- REQUIRED: Manual testing with actual Arabic/Hebrew content
- REQUIRED: Check all interactive elements (dropdowns, modals)
- REQUIRED: Verify form validation message alignment
- REQUIRED: Test keyboard navigation (Tab order reverses)

### Content

- REQUIRED: Professional translation (not just mirrored English)
- REQUIRED: Proper RTL punctuation and formatting
- REQUIRED: Number formatting for RTL locales
- REQUIRED: Date formatting (varies by region)

---

## Browser Support

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| CSS Logical Properties | 89+ | 66+ | 15+ | 89+ |
| `dir` attribute | All | All | All | All |
| BiDi algorithm | All | All | All | All |
| `:dir()` pseudo-class | 120+ | 49+ | 16.4+ | 120+ |

### Fallback for Older Browsers

```css
/* Fallback pattern */
.element {
  margin-left: 1rem; /* Fallback */
  margin-inline-start: 1rem; /* Modern */
}

/* Or use PostCSS plugin */
/* postcss-logical handles this automatically */
```

```bash
npm install postcss-logical
```

```javascript
// postcss.config.js
module.exports = {
  plugins: [require('postcss-logical')({ dir: 'ltr' })],
};
```
