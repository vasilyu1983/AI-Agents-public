# Cognitive Accessibility

Testing and implementation patterns for cognitive accessibility. Covers the
WCAG 2.2 cognitive success criteria, reading-level checks, error-prevention
patterns, plain-language guidelines, and W3C COGA (Cognitive Accessibility Task
Force) guidance.

## Table of Contents

- [WCAG 2.2 Cognitive Criteria](#wcag-22-cognitive-criteria)
- [Focus Not Obscured (2.4.11 / 2.4.12)](#focus-not-obscured-2411--2412)
- [Redundant Entry (3.3.7)](#redundant-entry-337)
- [Accessible Authentication (3.3.8 / 3.3.9)](#accessible-authentication-338--339)
- [Reading-Level Checks](#reading-level-checks)
- [Error-Prevention Patterns](#error-prevention-patterns)
- [Plain-Language Guidelines](#plain-language-guidelines)
- [Attention and Memory Load Reduction](#attention-and-memory-load-reduction)
- [W3C COGA Guidance](#w3c-coga-guidance)
- [Testing in CI](#testing-in-ci)
- [Manual Review Checklist](#manual-review-checklist)

---

## WCAG 2.2 Cognitive Criteria

WCAG 2.2 added four new success criteria that are directly relevant to cognitive
accessibility. All four apply at Level AA or AAA.

| SC | Level | Title | What it requires |
|----|-------|-------|-----------------|
| 2.4.11 | AA | Focus Not Obscured (Minimum) | When a UI component receives keyboard focus it is not entirely hidden by author-created content (e.g. a sticky header) |
| 2.4.12 | AAA | Focus Not Obscured (Enhanced) | The focused component is not obscured *at all* by author-created content |
| 3.3.7 | A | Redundant Entry | Information previously entered by the user in the same session is either auto-populated or available to select — users should not have to re-type it |
| 3.3.8 | AA | Accessible Authentication (Minimum) | Cognitive function tests (e.g. transcribing characters, solving puzzles) are not required unless an alternative or assistance is provided |
| 3.3.9 | AAA | Accessible Authentication (Enhanced) | No cognitive function test is required at any step of authentication |

> Source: [WCAG 2.2 — What's New](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/)

---

## Focus Not Obscured (2.4.11 / 2.4.12)

### What to Test

- Sticky/fixed headers and footers do not fully cover a focused element.
- Cookie banners, chat widgets, and notification toasts do not sit on top of focused controls.
- Scroll-anchoring or `scroll-margin-top` compensates for sticky chrome height.

### How to Test

```typescript
// Playwright: verify focused element is not obscured by sticky header
test('focused element is not obscured by sticky header', async ({ page }) => {
  await page.goto('/');
  await page.keyboard.press('Tab');

  const focused = page.locator(':focus');
  const focusedBox = await focused.boundingBox();
  const headerBox = await page.locator('header').boundingBox();

  if (focusedBox && headerBox) {
    // Top of focused element must be below the bottom of the sticky header
    expect(focusedBox.y).toBeGreaterThanOrEqual(headerBox.y + headerBox.height);
  }
});
```

### CSS Remedy

```css
/* Ensure focused elements scroll clear of fixed headers */
:target,
:focus {
  scroll-margin-top: calc(var(--header-height, 60px) + 8px);
}
```

---

## Redundant Entry (3.3.7)

### What to Test

- Multi-step forms do not ask for the same information twice in the same session
  (e.g. email on step 1, then again on step 3).
- Where information must appear again, it is pre-filled or offered as a selectable
  option.
- Exceptions: re-entering a password for security confirmation is allowed.

### Testing Approach

This criterion requires manual review and session-aware integration tests.
Automated rule detectors cannot infer "same information" semantics.

```typescript
// Integration test pattern: verify billing address pre-fill from shipping
test('billing address is pre-filled from shipping when checkbox is checked', async ({ page }) => {
  await page.goto('/checkout');

  await page.fill('[name="shipping-address"]', '123 Main St');
  await page.check('[data-testid="same-as-shipping"]');

  await expect(page.locator('[name="billing-address"]')).toHaveValue('123 Main St');
});
```

---

## Accessible Authentication (3.3.8 / 3.3.9)

### What to Test

- Login flows do not solely rely on: memorising characters, solving puzzles, or
  transcribing distorted text (CAPTCHAs without alternatives).
- If a cognitive function test is present, at least one of these alternatives
  exists:
  - Object recognition (click all images of a bus)
  - Personal content (user-uploaded image recognition)
  - Email/SMS OTP (no cognitive function test in the flow)
  - Passkey / biometric (OS-level, no cognitive test)
- Password managers and browser autofill are not blocked (`autocomplete` attributes
  present on credential fields).

### autocomplete Attributes for Credential Fields

```html
<!-- Enable password-manager autofill — required for 3.3.8 compliance -->
<input type="email"    name="email"    autocomplete="email" />
<input type="password" name="password" autocomplete="current-password" />

<!-- New password on registration/reset -->
<input type="password" name="new-password" autocomplete="new-password" />
```

### axe-core Automated Check

`autocomplete-valid` rule catches missing or invalid `autocomplete` values on
credential fields. This is partially automatable.

---

## Reading-Level Checks

WCAG 3.1.5 (Level AAA) recommends content readable without lower-secondary
education. Plain language is also a COGA best practice at all conformance levels.

### Hemingway App (Manual)

Paste body copy into [hemingwayapp.com](https://hemingwayapp.com/).
Target: Grade 8 or below for general audiences; Grade 6 for health/legal content.

### Flesch-Kincaid in CI

Use `textstat` (Python) or `text-readability` (Node) to gate on Flesch Reading
Ease score in automated content pipelines.

```bash
# Node — add to package.json scripts or CI step
npm install --save-dev text-readability
```

```typescript
// scripts/check-reading-level.ts
import { textReadability } from 'text-readability';
import { readFileSync } from 'fs';

const content = readFileSync(process.argv[2], 'utf8');
const score = textReadability.fleschReadingEase(content);
const grade = textReadability.fleschKincaidGrade(content);

console.log(`Flesch Reading Ease: ${score.toFixed(1)} (target ≥ 60)`);
console.log(`Flesch-Kincaid Grade: ${grade.toFixed(1)} (target ≤ 8)`);

if (score < 60) {
  console.error('FAIL: reading ease below threshold');
  process.exit(1);
}
```

---

## Error-Prevention Patterns

WCAG 3.3.4 (AA) — for pages that cause legal or financial commitments, require
one of: reversible, checked, or confirmed.

### Implementation Checklist

- **Reversible**: provide undo/cancel for destructive actions (delete, submit
  order) within a reasonable window.
- **Checked**: validate inputs server-side *and* client-side before final
  submission; surface all errors before the final state change.
- **Confirmed**: display a review screen before irreversible submission (checkout
  confirmation, account deletion dialog).

### Error Message Quality

- Identify *what* went wrong, not just that it did.
- Suggest a *correction* where possible.
- Never use error codes as the sole error description.
- Associate error messages with the specific input field via `aria-describedby`.

```html
<label for="email">Email address</label>
<input
  id="email"
  type="email"
  aria-describedby="email-error"
  aria-invalid="true"
/>
<span id="email-error" role="alert">
  Enter a valid email address — for example, name@example.com
</span>
```

---

## Plain-Language Guidelines

Based on W3C COGA guidance and US Plain Language Act principles:

- Use active voice and direct address ("You can…" not "Users are able to…").
- Lead with the most important information (inverted pyramid).
- One idea per sentence; target ≤ 20 words per sentence on average.
- Prefer common words: "use" not "utilise", "help" not "assist", "start" not "initiate".
- Define acronyms and technical terms on first use.
- Use consistent terminology — do not refer to the same concept by multiple names.
- Use numbered lists for sequential steps; bullet lists for unordered items.
- Avoid metaphors and idioms that may not translate across cultures.

---

## Attention and Memory Load Reduction

COGA design patterns for reducing cognitive burden:

| Pattern | Implementation |
|---------|---------------|
| Chunking | Break long forms into steps; show progress indicator |
| Persistent context | Show what the user entered in previous steps; do not clear state on back navigation |
| Consistent navigation | Keep navigation, header, and footer in the same position across all pages |
| Avoid time limits | Do not auto-expire sessions during active use; warn before expiry with extension option |
| Reduce distractions | Auto-play media off by default; do not use blinking or flashing elements |
| Simple visual hierarchy | Limit heading levels to what the content requires; do not use headings for styling |
| Visible status | Always show the current state of interactive elements (loading, success, error) |
| Recognise rather than recall | Use autocomplete, saved addresses, recent searches — reduce reliance on memory |

---

## W3C COGA Guidance

The [W3C Cognitive Accessibility Task Force (COGA)](https://www.w3.org/WAI/cognitive/)
produces non-normative guidance that extends beyond WCAG. Key publications:

| Document | Use When |
|----------|----------|
| [Making Content Usable for People with COGA Disabilities](https://www.w3.org/TR/coga-usable/) | Designing for dyslexia, ADHD, memory impairment, mental health conditions |
| [Cognitive Accessibility Roadmap and Gap Analysis](https://www.w3.org/TR/coga-gap-analysis/) | Identifying gaps between WCAG and COGA user needs |
| [COGA Design Guide](https://www.w3.org/WAI/WCAG2/supplemental/patterns/) | 8 COGA design goals with testable patterns |

### 8 COGA Design Goals (summary)

1. Help users understand what things are and how to use them.
2. Help users find what they need.
3. Use clear and understandable content and text.
4. Prevent users from making mistakes and make it easy to correct them.
5. Help users focus and restore context if distracted.
6. Ensure processes do not rely on memory.
7. Provide help and support.
8. Support adaptation and personalisation.

---

## Testing in CI

| Check | Tool | Automate? |
|-------|------|-----------|
| `autocomplete` on credential fields | axe-core `autocomplete-valid` | Full |
| Focus obscured by sticky chrome | Playwright bounding-box check | Partial |
| Redundant entry across form steps | Session-aware integration test | Partial |
| Reading level of body copy | `text-readability` in content pipeline | Full (for content files) |
| Error message associated with input | axe-core `label`, `aria-required-attr` | Partial |
| CAPTCHA has accessible alternative | Manual review | Manual |
| Plain-language compliance | Hemingway score review | Manual |

---

## Manual Review Checklist

- [ ] No required cognitive function test in authentication without an alternative.
- [ ] Password managers and autofill are not blocked (correct `autocomplete` values).
- [ ] No information previously entered in the session must be re-typed.
- [ ] Focused elements are never fully hidden by sticky headers or overlays.
- [ ] All error messages identify the field and suggest a correction.
- [ ] Destructive actions have a confirmation, undo, or review step.
- [ ] Reading level is Grade 8 or below for general-audience content.
- [ ] No auto-playing media without user consent.
- [ ] Session timeouts warn the user and offer an extension.
- [ ] Navigation is consistent across all pages.
