# Accessibility Testing Template (WCAG 2.2 AA)

Use this template for ensuring web applications meet WCAG 2.2 Level AA accessibility standards.

## Testing Tools Overview

**axe-core** - Best for:
- Automated accessibility audits
- CI/CD integration
- Catching common, automatable issues (not a replacement for manual testing)
- Component-level testing

**Pa11y** - Best for:
- Command-line accessibility testing
- Batch testing multiple URLs
- CI/CD integration
- Automated monitoring

**Lighthouse** - Best for:
- Overall accessibility score
- Chrome DevTools integration
- Performance + accessibility combo
- Quick initial audits

**Manual Testing** - Required for:
- Keyboard navigation
- Screen reader compatibility
- Color contrast edge cases
- Context and semantics (automation cannot judge intent)

## Automated Testing with axe-core

### Basic Component Testing

```typescript
// components/Button.a11y.test.ts
import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { Button } from './Button'

expect.extend(toHaveNoViolations)

describe('Button Accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(
      <Button variant="primary">Click me</Button>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should be accessible when disabled', async () => {
    const { container } = render(
      <Button disabled>Disabled button</Button>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have proper ARIA attributes', async () => {
    const { container } = render(
      <Button aria-label="Close dialog" aria-pressed="true">
        <span aria-hidden="true">×</span>
      </Button>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should be accessible with icon only', async () => {
    const { container } = render(
      <Button aria-label="Search">
        <SearchIcon aria-hidden="true" />
      </Button>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
```

### Form Accessibility Testing

```typescript
// components/Form.a11y.test.ts
import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { LoginForm } from './LoginForm'

expect.extend(toHaveNoViolations)

describe('Form Accessibility', () => {
  it('should have proper labels for inputs', async () => {
    const { container } = render(<LoginForm />)

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should associate error messages with inputs', async () => {
    const { container } = render(
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          aria-invalid="true"
          aria-describedby="email-error"
        />
        <span id="email-error" role="alert">
          Email is required
        </span>
      </div>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should use fieldset for grouped inputs', async () => {
    const { container } = render(
      <fieldset>
        <legend>Payment Method</legend>
        <label>
          <input type="radio" name="payment" value="card" />
          Credit Card
        </label>
        <label>
          <input type="radio" name="payment" value="paypal" />
          PayPal
        </label>
      </fieldset>
    )

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
```

### Full Page Testing with Playwright

```typescript
// e2e/accessibility.test.ts
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('Page Accessibility', () => {
  test('homepage should be accessible', async ({ page }) => {
    await page.goto('/')

    const accessibilityScanResults = await new AxeBuilder({ page }).analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('dashboard should be accessible', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    const accessibilityScanResults = await new AxeBuilder({ page })
      .exclude('#third-party-widget') // Exclude third-party content
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should check specific WCAG rules', async ({ page }) => {
    await page.goto('/contact')

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa']) // WCAG 2.2 AA (plus earlier tags)
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should test specific regions', async ({ page }) => {
    await page.goto('/dashboard')

    const accessibilityScanResults = await new AxeBuilder({ page })
      .include('[role="main"]') // Only test main content
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })
})
```

## Manual Keyboard Navigation Testing

```typescript
// e2e/keyboard-navigation.test.ts
import { test, expect } from '@playwright/test'

test.describe('Keyboard Navigation', () => {
  test('should navigate form with Tab key', async ({ page }) => {
    await page.goto('/contact')

    // Tab through form fields
    await page.keyboard.press('Tab')
    await expect(page.locator('[name="name"]')).toBeFocused()

    await page.keyboard.press('Tab')
    await expect(page.locator('[name="email"]')).toBeFocused()

    await page.keyboard.press('Tab')
    await expect(page.locator('[name="message"]')).toBeFocused()

    await page.keyboard.press('Tab')
    await expect(page.locator('button[type="submit"]')).toBeFocused()
  })

  test('should navigate backwards with Shift+Tab', async ({ page }) => {
    await page.goto('/contact')

    // Focus submit button
    await page.locator('button[type="submit"]').focus()

    // Shift+Tab backwards
    await page.keyboard.press('Shift+Tab')
    await expect(page.locator('[name="message"]')).toBeFocused()

    await page.keyboard.press('Shift+Tab')
    await expect(page.locator('[name="email"]')).toBeFocused()
  })

  test('should submit form with Enter key', async ({ page }) => {
    await page.goto('/contact')

    await page.fill('[name="name"]', 'Test User')
    await page.fill('[name="email"]', 'test@example.com')
    await page.fill('[name="message"]', 'Test message')

    await page.keyboard.press('Enter')

    await expect(page.locator('.success-message')).toBeVisible()
  })

  test('should close modal with Escape key', async ({ page }) => {
    await page.goto('/dashboard')

    // Open modal
    await page.click('[data-testid="open-modal"]')
    await expect(page.locator('[role="dialog"]')).toBeVisible()

    // Close with Escape
    await page.keyboard.press('Escape')
    await expect(page.locator('[role="dialog"]')).not.toBeVisible()
  })

  test('should trap focus in modal', async ({ page }) => {
    await page.goto('/dashboard')

    await page.click('[data-testid="open-modal"]')

    const modal = page.locator('[role="dialog"]')
    await expect(modal).toBeVisible()

    // Focus should start on close button
    await expect(modal.locator('button[aria-label="Close"]')).toBeFocused()

    // Tab through modal elements
    await page.keyboard.press('Tab')
    await expect(modal.locator('input[name="name"]')).toBeFocused()

    await page.keyboard.press('Tab')
    await expect(modal.locator('button[type="submit"]')).toBeFocused()

    // Tab should cycle back to close button (focus trap)
    await page.keyboard.press('Tab')
    await expect(modal.locator('button[aria-label="Close"]')).toBeFocused()
  })

  test('should navigate menu with arrow keys', async ({ page }) => {
    await page.goto('/')

    // Open dropdown menu
    await page.click('[aria-haspopup="true"]')

    const menu = page.locator('[role="menu"]')
    await expect(menu).toBeVisible()

    // Arrow down to first item
    await page.keyboard.press('ArrowDown')
    await expect(menu.locator('[role="menuitem"]').first()).toBeFocused()

    // Arrow down to second item
    await page.keyboard.press('ArrowDown')
    await expect(menu.locator('[role="menuitem"]').nth(1)).toBeFocused()

    // Arrow up back to first
    await page.keyboard.press('ArrowUp')
    await expect(menu.locator('[role="menuitem"]').first()).toBeFocused()
  })
})
```

## Color Contrast Testing

```typescript
// e2e/color-contrast.test.ts
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('Color Contrast (WCAG AA)', () => {
  test('should meet contrast requirements', async ({ page }) => {
    await page.goto('/')

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['cat.color']) // Only color contrast rules
      .analyze()

    // Filter for contrast violations
    const contrastViolations = accessibilityScanResults.violations.filter(
      v => v.id === 'color-contrast'
    )

    expect(contrastViolations).toEqual([])
  })

  test('should test contrast in dark mode', async ({ page }) => {
    await page.goto('/')

    // Enable dark mode
    await page.evaluate(() => {
      document.documentElement.setAttribute('data-theme', 'dark')
    })

    await page.waitForTimeout(300)

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['cat.color'])
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('should validate button contrast', async ({ page }) => {
    await page.goto('/components/button')

    const accessibilityScanResults = await new AxeBuilder({ page })
      .include('[data-testid="button-showcase"]')
      .withTags(['cat.color'])
      .analyze()

    expect(accessibilityScanResults.violations).toEqual([])
  })
})
```

## Screen Reader Testing (Automated)

```typescript
// e2e/screen-reader.test.ts
import { test, expect } from '@playwright/test'

test.describe('Screen Reader Compatibility', () => {
  test('should have proper heading hierarchy', async ({ page }) => {
    await page.goto('/about')

    // Check h1 exists and is unique
    const h1Count = await page.locator('h1').count()
    expect(h1Count).toBe(1)

    // Check heading order
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').allTextContents()

    // Validate no heading levels are skipped
    const levels = await page.locator('h1, h2, h3, h4, h5, h6').evaluateAll(elements =>
      elements.map(el => parseInt(el.tagName.substring(1)))
    )

    for (let i = 1; i < levels.length; i++) {
      expect(levels[i] - levels[i - 1]).toBeLessThanOrEqual(1)
    }
  })

  test('should use semantic landmarks', async ({ page }) => {
    await page.goto('/')

    // Check for semantic HTML5 landmarks
    await expect(page.locator('header')).toBeVisible()
    await expect(page.locator('nav')).toBeVisible()
    await expect(page.locator('main')).toBeVisible()
    await expect(page.locator('footer')).toBeVisible()
  })

  test('should have alt text for images', async ({ page }) => {
    await page.goto('/gallery')

    const images = await page.locator('img').all()

    for (const img of images) {
      const alt = await img.getAttribute('alt')
      const ariaLabel = await img.getAttribute('aria-label')
      const role = await img.getAttribute('role')

      // Image must have alt text, or be decorative (role="presentation")
      const isAccessible = alt !== null || ariaLabel !== null || role === 'presentation'
      expect(isAccessible).toBe(true)
    }
  })

  test('should announce dynamic content updates', async ({ page }) => {
    await page.goto('/dashboard')

    // Check for live regions
    const liveRegion = page.locator('[aria-live="polite"]')
    await expect(liveRegion).toBeVisible()

    // Trigger update
    await page.click('[data-testid="refresh-data"]')

    // Verify live region content updates
    await expect(liveRegion).toContainText('Data updated')
  })

  test('should provide text alternatives for icons', async ({ page }) => {
    await page.goto('/')

    const iconButtons = await page.locator('button:has(svg)').all()

    for (const button of iconButtons) {
      const ariaLabel = await button.getAttribute('aria-label')
      const title = await button.getAttribute('title')
      const textContent = await button.textContent()

      // Button must have accessible name
      const hasAccessibleName =
        (ariaLabel && ariaLabel.length > 0) ||
        (title && title.length > 0) ||
        (textContent && textContent.trim().length > 0)

      expect(hasAccessibleName).toBe(true)
    }
  })
})
```

## ARIA Attributes Testing

```typescript
// components/Modal.a11y.test.ts
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Modal } from './Modal'

describe('Modal ARIA Attributes', () => {
  it('should have proper dialog role', () => {
    render(
      <Modal isOpen onClose={() => {}}>
        <h2>Dialog Title</h2>
        <p>Dialog content</p>
      </Modal>
    )

    const dialog = screen.getByRole('dialog')
    expect(dialog).toBeInTheDocument()
  })

  it('should have aria-modal attribute', () => {
    render(
      <Modal isOpen onClose={() => {}}>
        <h2>Dialog Title</h2>
      </Modal>
    )

    const dialog = screen.getByRole('dialog')
    expect(dialog).toHaveAttribute('aria-modal', 'true')
  })

  it('should have aria-labelledby pointing to title', () => {
    render(
      <Modal isOpen onClose={() => {}}>
        <h2 id="modal-title">Dialog Title</h2>
      </Modal>
    )

    const dialog = screen.getByRole('dialog')
    expect(dialog).toHaveAttribute('aria-labelledby', 'modal-title')
  })

  it('should have aria-describedby for description', () => {
    render(
      <Modal isOpen onClose={() => {}}>
        <h2 id="modal-title">Dialog Title</h2>
        <p id="modal-description">This is the dialog description</p>
      </Modal>
    )

    const dialog = screen.getByRole('dialog')
    expect(dialog).toHaveAttribute('aria-describedby', 'modal-description')
  })
})
```

## Accessibility Testing Checklist

### Automated Tests (axe-core)
- [ ] Run axe-core on all pages
- [ ] Test all interactive components (buttons, forms, modals)
- [ ] Test color contrast (normal and dark mode)
- [ ] Verify no duplicate IDs
- [ ] Check image alt text
- [ ] Validate ARIA attributes
- [ ] Test heading hierarchy

### Keyboard Navigation
- [ ] Tab through all interactive elements
- [ ] Shift+Tab backwards navigation works
- [ ] Enter/Space activates buttons and links
- [ ] Arrow keys navigate menus and lists
- [ ] Escape closes modals and dropdowns
- [ ] Focus is visible at all times
- [ ] Focus trapped in modals
- [ ] Skip to main content link works

### Screen Reader Testing (Manual)
- [ ] Test with NVDA (Windows) or VoiceOver (macOS)
- [ ] Headings announce correctly
- [ ] Landmarks identified properly
- [ ] Form labels read with inputs
- [ ] Error messages announced
- [ ] Dynamic content updates announced (aria-live)
- [ ] Images have descriptive alt text
- [ ] Links have descriptive text (no "click here")

### Color and Visual
- [ ] Text contrast ratio ≥ 4.5:1 (normal text)
- [ ] Text contrast ratio ≥ 3:1 (large text 18pt+)
- [ ] UI component contrast ≥ 3:1
- [ ] Focus indicators visible (3:1 contrast)
- [ ] Information not conveyed by color alone
- [ ] Text resizable up to 200% without loss of functionality
- [ ] Content readable without horizontal scrolling

### Forms
- [ ] All inputs have associated labels
- [ ] Required fields marked with aria-required or required
- [ ] Error messages associated with inputs (aria-describedby)
- [ ] Error messages use role="alert" for announcements
- [ ] Fieldsets used for grouped inputs (radio, checkbox)
- [ ] Autocomplete attributes used appropriately

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/accessibility.yml
name: Accessibility Tests

on:
  pull_request:
    branches: [main]

jobs:
  a11y-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: npm ci

      - name: Run accessibility tests
        run: npm run test:a11y

      - name: Upload axe results
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: axe-violations
          path: axe-results.json
```

### Pa11y CI Configuration

```json
// .pa11yci.json
{
  "defaults": {
    "standard": "WCAG2AA",
    "runners": ["axe", "htmlcs"],
    "timeout": 30000,
    "chromeLaunchConfig": {
      "args": ["--no-sandbox"]
    }
  },
  "urls": [
    "http://localhost:3000/",
    "http://localhost:3000/about",
    "http://localhost:3000/contact",
    {
      "url": "http://localhost:3000/dashboard",
      "actions": [
        "set field #username to testuser",
        "set field #password to password",
        "click element button[type='submit']",
        "wait for url to be http://localhost:3000/dashboard"
      ]
    }
  ]
}
```

## Best Practices

- [ ] Test accessibility early in development (shift-left)
- [ ] Combine automated tools with manual testing
- [ ] Test with real assistive technologies
- [ ] Include users with disabilities in user testing
- [ ] Document accessibility features
- [ ] Train team on WCAG standards
- [ ] Make accessibility part of Definition of Done
- [ ] Monitor accessibility in production

## Common Violations and Fixes

### Missing Alt Text
```typescript
// Bad
<img src="logo.png" />

// Good
<img src="logo.png" alt="Company Logo" />

// Decorative image
<img src="decoration.png" alt="" role="presentation" />
```

### Poor Form Labels
```typescript
// Bad
<input type="text" placeholder="Email" />

// Good
<label htmlFor="email">Email</label>
<input id="email" type="text" />
```

### Low Contrast
```css
/* Bad - 3:1 contrast */
.text {
  color: #757575;
  background: #ffffff;
}

/* Good - 4.6:1 contrast */
.text {
  color: #595959;
  background: #ffffff;
}
```

### Non-Semantic Buttons
```typescript
// Bad
<div onClick={handleClick}>Click me</div>

// Good
<button onClick={handleClick}>Click me</button>
```

## Related Resources

- [WCAG 2.2 Guidelines](https://www.w3.org/WAI/WCAG22/quickref/)
- [axe-core Rules](https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md)
- [A11y Project Checklist](https://www.a11yproject.com/checklist/)
- [WebAIM Contrast Checker](https://webaim.org/references/contrastchecker/)
