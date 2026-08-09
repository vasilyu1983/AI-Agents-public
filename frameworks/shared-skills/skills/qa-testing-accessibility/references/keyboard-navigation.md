# Keyboard Navigation Testing

Keyboard accessibility is foundational — if a user cannot operate your interface with a keyboard alone, screen readers and switch devices will also fail. This guide covers verification steps and common patterns.

## Table of Contents

- [Core Requirements](#core-requirements)
- [Tab Order Verification](#tab-order-verification)
- [Manual Test](#manual-test)
- [Common Issues](#common-issues)
- [Rule: Never Use Positive tabindex](#rule-never-use-positive-tabindex)
- [Focus Visibility](#focus-visibility)
- [WCAG 2.2 Focus Appearance (2.4.13 AAA / 2.4.11 AA)](#wcag-22-focus-appearance-2413-aaa-2411-aa)
- [Testing Focus Visibility](#testing-focus-visibility)
- [Skip Navigation](#skip-navigation)
- [Verify](#verify)
- [Modal / Dialog Focus Trapping](#modal-dialog-focus-trapping)
- [Implementation Pattern](#implementation-pattern)
- [Verify](#verify)
- [ARIA APG Keyboard Patterns](#aria-apg-keyboard-patterns)
- [Testing Checklist](#testing-checklist)

## Core Requirements

1. **All interactive elements reachable via Tab** (or Shift+Tab for reverse).
2. **Focus indicator visible** on every focusable element.
3. **Logical tab order** matching visual layout (left-to-right, top-to-bottom for LTR languages).
4. **No keyboard traps** — user can always Tab or Escape out of any component.
5. **Skip navigation** link as the first focusable element on every page.
6. **Custom components** follow ARIA APG keyboard patterns.

## Tab Order Verification

### Manual Test

1. Load the page.
2. Press `Tab` repeatedly from the address bar.
3. Verify focus moves through elements in a logical order.
4. Verify no elements are skipped that should be interactive.
5. Verify no non-interactive elements receive focus unnecessarily.
6. Press `Shift+Tab` to verify reverse order.

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Focus skips visible element | `tabindex="-1"` or `display: none` applied incorrectly | Remove negative tabindex or fix visibility |
| Non-interactive element receives focus | `tabindex="0"` on a `<div>` without a role | Remove tabindex or add appropriate role + keyboard handler |
| Focus order does not match visual order | CSS reordering (flexbox `order`, grid placement, absolute positioning) | Adjust DOM order to match visual order |
| Focus jumps unexpectedly | Positive `tabindex` values (`tabindex="1"`, `tabindex="2"`) | Remove positive tabindex values — use DOM order |

### Rule: Never Use Positive tabindex

Positive `tabindex` values override natural DOM order and create maintenance nightmares. Use `tabindex="0"` (add to tab order) or `tabindex="-1"` (programmatically focusable only). Control order through DOM structure.

## Focus Visibility

Every focusable element must have a visible focus indicator. The default browser outline is acceptable; removing it is not.

```css
/* BAD — removes focus indicator */
*:focus { outline: none; }

/* GOOD — custom focus indicator */
*:focus-visible {
  outline: 2px solid #005fcc;
  outline-offset: 2px;
}
```

### WCAG 2.2 Focus Appearance (2.4.13 AAA / 2.4.11 AA)

- **2.4.11 (AA)**: focused element must not be entirely obscured by other content (sticky headers, footers, modals).
- **2.4.13 (AAA)**: focus indicator must have sufficient size and contrast (at least 2px outline with 3:1 contrast against adjacent colors).

### Testing Focus Visibility

1. Tab through the page.
2. At each stop, verify the focus indicator is clearly visible.
3. Check that sticky headers/footers do not obscure the focused element.
4. Verify focus indicator works in both light and dark modes.

## Skip Navigation

The first focusable element on every page should be a skip link that jumps to the main content.

```html
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>
  <header>...</header>
  <nav>...</nav>
  <main id="main-content" tabindex="-1">
    <!-- main content -->
  </main>
</body>
```

```css
.skip-link {
  position: absolute;
  left: -9999px;
}
.skip-link:focus {
  position: static;
  /* or position: fixed; top: 0; left: 0; */
}
```

### Verify

1. Press `Tab` once from the address bar.
2. The skip link should appear visually.
3. Press `Enter` — focus should move to the main content area.
4. Next `Tab` press should land on the first interactive element inside main content.

## Modal / Dialog Focus Trapping

When a modal dialog opens:
1. Focus moves to the first focusable element inside the modal (or the modal title).
2. `Tab` and `Shift+Tab` cycle through elements *within the modal only*.
3. `Escape` closes the modal.
4. On close, focus returns to the element that triggered the modal.

### Implementation Pattern

```javascript
function trapFocus(modal) {
  const focusable = modal.querySelectorAll(
    'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex="0"]'
  );
  const first = focusable[0];
  const last = focusable[focusable.length - 1];

  modal.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
    if (e.key === 'Escape') {
      closeModal();
    }
  });

  first.focus();
}
```

Use `<dialog>` element where possible — it handles focus trapping and Escape natively.

### Verify

1. Open the modal.
2. Verify focus is inside the modal.
3. `Tab` to the last element, then `Tab` again — focus should wrap to the first element.
4. `Shift+Tab` from the first element should wrap to the last.
5. Press `Escape` — modal closes.
6. Verify focus returns to the trigger element.

## ARIA APG Keyboard Patterns

Custom components must follow the keyboard patterns defined in the ARIA Authoring Practices Guide.

| Component | Key Interactions |
|-----------|-----------------|
| Tabs | Arrow keys switch tabs; Tab moves to tab panel content |
| Accordion | Enter/Space toggles section; Arrow keys move between headers |
| Menu | Arrow keys navigate items; Enter/Space activates; Escape closes |
| Combobox | Arrow keys navigate options; Enter selects; Escape closes listbox |
| Tree view | Arrow keys navigate nodes; Enter/Space expand/collapse; Home/End |
| Listbox | Arrow keys navigate; Space selects/deselects; Shift for multi-select |
| Slider | Arrow keys adjust value; Home/End for min/max |
| Tooltip | Appears on focus; Escape dismisses; does not trap focus |

Reference: https://www.w3.org/WAI/ARIA/apg/patterns/

## Testing Checklist

- [ ] All interactive elements reachable via Tab
- [ ] Tab order matches visual layout
- [ ] No positive tabindex values used
- [ ] Focus indicator visible on every focusable element
- [ ] Focus not obscured by sticky elements
- [ ] Skip navigation link present and functional
- [ ] Modals trap focus correctly
- [ ] Modal close returns focus to trigger
- [ ] Escape key closes overlays and menus
- [ ] Custom components follow ARIA APG keyboard patterns
- [ ] No keyboard traps anywhere in the application
