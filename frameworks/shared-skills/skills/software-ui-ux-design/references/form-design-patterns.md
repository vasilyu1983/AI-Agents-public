# Form Design Patterns — UX Best Practices (Jan 2026)

Evidence-based form design patterns covering layout, validation, multi-step flows, error handling, accessibility, and mobile optimization. Forms are where users exchange value with your product; every friction point costs conversions.

---

## Form Layout Fundamentals

### Single-Column vs Multi-Column

**Data-backed recommendation: Use single-column layout for most forms.**

Research from Baymard Institute and CXL shows that single-column forms are completed 15-25% faster than multi-column forms. Multi-column layouts cause visual scanning confusion and increase error rates.

| Layout | When to Use | When to Avoid |
|--------|------------|---------------|
| **Single column** | Signup, checkout, contact, any mobile form | Wide-screen data entry with related field pairs |
| **Two column** | Related field pairs only (first/last name, city/state) | Forms with more than 2 columns |
| **Adaptive** | Desktop: grouped pairs; Mobile: single column | Never three or more columns on mobile |

### Visual Hierarchy

```text
FORM STRUCTURE (top to bottom):
┌─────────────────────────────────────────┐
│ Form Title                               │  ← Clear purpose statement
│ Brief description (optional)            │
├─────────────────────────────────────────┤
│                                         │
│ ┌─ Section: Personal Info ────────────┐ │  ← Logical grouping with
│ │  Label                              │ │     fieldset/legend
│ │  [Input field                    ]  │ │
│ │  Helper text                        │ │
│ │                                     │ │
│ │  Label                              │ │
│ │  [Input field                    ]  │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─ Section: Contact ──────────────────┐ │
│ │  ...                                │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [Secondary Action]    [Primary Action]  │  ← Actions at bottom
└─────────────────────────────────────────┘
```

### Field Sizing

Field width should indicate expected input length:

| Input | Width | Example |
|-------|-------|---------|
| Full name | Full width | 100% of form width |
| Email | Full width | 100% of form width |
| Phone | Medium (60-70%) | Shorter than email |
| Zip/postal code | Small (30-40%) | 5-10 characters |
| State/province | Small (30-40%) | Dropdown or 2-letter code |
| Credit card number | Full width | 16+ characters with spaces |
| CVV | Small (20%) | 3-4 characters |
| Textarea | Full width, 4-6 rows | Multi-line input |

---

## Progressive Disclosure

Show fields as they become relevant. Reduce cognitive load by presenting only what the user needs right now.

### Techniques

| Technique | How It Works | Example |
|-----------|-------------|---------|
| **Conditional fields** | Show fields based on prior selection | "Shipping address different from billing?" reveals second address block |
| **Optional section toggle** | Expandable section for optional info | "Add a gift message" expander |
| **Smart defaults** | Pre-fill based on context | Country from IP geolocation, currency from locale |
| **Deferred collection** | Collect non-essential data after primary action | Ask for profile photo after account creation |
| **Typeahead/autocomplete** | Reduce input to selection | Address autocomplete via Google Places |

### Decision Framework

```text
For each field, ask:
  ├─ Is it required to complete the primary action?
  │   ├─ YES → Show in main form
  │   └─ NO → Can it be deferred?
  │       ├─ YES → Collect later (post-completion, settings, profile)
  │       └─ NO → Use conditional display or optional section
  └─ Does the user expect this field?
      ├─ YES → Show with clear label
      └─ NO → Explain why you need it (helper text or tooltip)
```

---

## Inline Validation

### Timing

| Timing | When to Use | Implementation |
|--------|------------|---------------|
| **On blur** (focus leaves field) | Most fields, especially required fields | Validate after user finishes input |
| **On input** (keystroke) | Only for format constraints (phone, credit card) | Format as user types |
| **On submit** | Complex cross-field validation, server-side checks | Scroll to first error |
| **Never on focus** (entering field) | Never validate when user first enters a field | Creates anxiety before input |

### Visual Feedback

```text
DEFAULT STATE:
  Label
  ┌────────────────────────────┐
  │ Placeholder text           │
  └────────────────────────────┘
  Helper text (optional)

SUCCESS STATE:
  Label                        ✓
  ┌────────────────────────────┐
  │ valid@email.com            │  ← Green border
  └────────────────────────────┘

ERROR STATE:
  Label                        ✗
  ┌────────────────────────────┐
  │ invalid-email              │  ← Red border
  └────────────────────────────┘
  ⚠ Please enter a valid email   ← Error below field, red text

LOADING STATE (async validation):
  Label                        ⟳
  ┌────────────────────────────┐
  │ username-being-checked     │  ← Subtle loading indicator
  └────────────────────────────┘
  Checking availability...
```

### Error Message Placement

**Best practice: Place error messages directly below the field they relate to.**

| Placement | Effectiveness | Accessibility |
|-----------|-------------|---------------|
| Below field (inline) | Best: users see error in context | Good: `aria-describedby` links field to error |
| Above field | Acceptable for single-field forms | Good |
| Summary at top | Supplement only; not a substitute for inline | Useful for screen readers as overview |
| Tooltip/popover | Poor: disappears, hard to read | Poor: may be missed by assistive tech |

---

## Multi-Step Forms

### When to Use Multi-Step

| Use Multi-Step When | Stay Single-Page When |
|--------------------|----------------------|
| > 8-10 fields total | ≤ 8 fields |
| Logical sections with different topics | All fields relate to one topic |
| Later steps depend on earlier answers | No conditional logic |
| User needs time between sections (e.g., uploading documents) | Quick form (< 2 minutes) |

### Progress Indication

```text
STEP INDICATOR (numbered, horizontal):
  ① Personal Info  ─────  ② Shipping  ─────  ③ Payment  ─────  ④ Review
       [active]            [upcoming]          [upcoming]        [upcoming]

STEP INDICATOR (after step 2 completed):
  ✓ Personal Info  ─────  ② Shipping  ─────  ③ Payment  ─────  ④ Review
   [completed]             [active]           [upcoming]        [upcoming]
```

| Component | Requirement |
|-----------|------------|
| Step count | "Step 2 of 4" — always show total |
| Step labels | Descriptive names, not just numbers |
| Completed steps | Checkmark + clickable to go back |
| Current step | Highlighted, clearly active |
| Back navigation | Always available; preserve entered data |

### Save State

- Auto-save field values on blur (localStorage or server-side draft)
- Warn before navigating away if unsaved changes exist (`beforeunload` event)
- For long forms: explicit "Save and continue later" with email/link recovery
- Never lose user data on back navigation within the form

### Step Transition

```javascript
// Validate current step before advancing
function goToNextStep(currentStep) {
  const isValid = validateStep(currentStep);
  if (!isValid) {
    // Focus first error field
    const firstError = document.querySelector('[aria-invalid="true"]');
    firstError?.focus();
    return;
  }

  // Save current step data
  saveStepData(currentStep);

  // Animate transition
  setCurrentStep(currentStep + 1);

  // Scroll to top of new step
  window.scrollTo({ top: 0, behavior: 'smooth' });

  // Focus first field in new step (after animation)
  setTimeout(() => {
    document.querySelector(`#step-${currentStep + 1} input`)?.focus();
  }, 300);
}
```

---

## Field Grouping and Visual Hierarchy

### Grouping Principles

| Technique | When to Use | HTML Implementation |
|-----------|------------|-------------------|
| **Fieldset + legend** | Related fields that form a logical group | `<fieldset><legend>Shipping Address</legend>...</fieldset>` |
| **Section headings** | Major form sections | `<h2>` or `<h3>` within form |
| **Whitespace** | Separating groups visually | Margin between groups (24-32px) |
| **Divider lines** | Clear visual separation between sections | `<hr>` or CSS border-top |
| **Cards/panels** | Distinct sections that can collapse | Expandable panels for optional sections |

### Field Order

```text
NATURAL ORDER (match mental model):
1. Personal info (name, email, phone)
2. Address (street, city, state, zip, country)
3. Payment (card number, expiry, CVV)
4. Review and confirm

WRONG: Jumping between topics
1. Email → 2. City → 3. Name → 4. Phone → 5. Street
(Forces user to context-switch repeatedly)
```

---

## Label Patterns

### Pattern Comparison

| Pattern | Speed | Clarity | Space Efficiency | Recommendation |
|---------|-------|---------|-----------------|----------------|
| **Top-aligned** | Fastest scan | Highest | Moderate | Best default choice |
| **Left-aligned** | Slower scan | High | Space-hungry | Dense data entry (desktop only) |
| **Right-aligned** | Moderate | High | Moderate | Tabular forms |
| **Floating labels** | Moderate | Medium (label shrinks) | High | When vertical space is critical |
| **Placeholder-only** | N/A | Low (disappears) | Highest | ANTI-PATTERN: Never use alone |

### Why Placeholder-Only Labels Fail

- Label disappears when user starts typing (memory burden)
- Users cannot verify what a field is for while reviewing
- Screen readers may not announce placeholder text reliably
- Low contrast placeholder text (WCAG violation)
- Autofill replaces placeholder, removing all context

### Floating Label Implementation

```css
/* Floating label pattern */
.form-group {
  position: relative;
  margin-bottom: 1.5rem;
}
.form-group input {
  padding: 1.25rem 0.75rem 0.5rem;
  font-size: 1rem;
}
.form-group label {
  position: absolute;
  top: 1rem;
  left: 0.75rem;
  color: #666;
  transition: all 0.2s ease;
  pointer-events: none;
}
.form-group input:focus + label,
.form-group input:not(:placeholder-shown) + label {
  top: 0.25rem;
  font-size: 0.75rem;
  color: var(--color-primary);
}
```

**Note**: Always include a visually hidden `<label>` element for accessibility even when using floating labels. The `placeholder` attribute should be a space (`" "`) to trigger the `:not(:placeholder-shown)` selector, not actual placeholder text.

---

## Error Recovery

### Error Message Design

| Principle | Implementation |
|-----------|---------------|
| **Specific** | "Password must be at least 8 characters" not "Invalid password" |
| **Actionable** | Tell the user exactly what to do to fix it |
| **Polite** | Avoid blame ("You entered an invalid email" → "Please enter a valid email") |
| **Persistent** | Error stays visible until fixed (no auto-dismiss) |
| **Proximate** | Display directly below the relevant field |
| **Accessible** | `role="alert"` or `aria-live="polite"` for dynamic errors |

### Error Summary (Supplement to Inline)

```html
<!-- Error summary at top of form, shown on submit -->
<div role="alert" aria-labelledby="error-summary-title">
  <h2 id="error-summary-title">There are 2 problems with your submission</h2>
  <ul>
    <li><a href="#email">Enter a valid email address</a></li>
    <li><a href="#password">Password must be at least 8 characters</a></li>
  </ul>
</div>
```

### Prevention-First Patterns

| Prevention | Implementation |
|-----------|---------------|
| Input masking | Format phone numbers, credit cards as user types |
| Constrained input | Date picker instead of text field; dropdown instead of free text |
| Real-time format feedback | Show "Looks like a valid email" before blur |
| Smart suggestions | "Did you mean gmail.com?" for common email typos |
| Character counter | Show remaining characters for limited fields |
| Confirm destructive actions | "Are you sure?" for irreversible form submissions |

---

## Autofill and Autocomplete

### Browser Autofill Best Practices

```html
<form>
  <!-- Use correct autocomplete values for reliable autofill -->
  <input name="given-name" autocomplete="given-name" />
  <input name="family-name" autocomplete="family-name" />
  <input name="email" autocomplete="email" type="email" />
  <input name="tel" autocomplete="tel" type="tel" />
  <input name="street-address" autocomplete="street-address" />
  <input name="address-level2" autocomplete="address-level2" /> <!-- City -->
  <input name="address-level1" autocomplete="address-level1" /> <!-- State -->
  <input name="postal-code" autocomplete="postal-code" />
  <input name="country" autocomplete="country" />

  <!-- Payment autofill -->
  <input name="cc-name" autocomplete="cc-name" />
  <input name="cc-number" autocomplete="cc-number" inputmode="numeric" />
  <input name="cc-exp" autocomplete="cc-exp" />
  <input name="cc-csc" autocomplete="cc-csc" inputmode="numeric" />
</form>
```

### Address Autocomplete

| Provider | Coverage | Cost | Integration |
|----------|----------|------|-------------|
| Google Places Autocomplete | Global, best coverage | Pay-per-use | `@googlemaps/js-api-loader` |
| Mapbox Address Autofill | Global | Pay-per-use | `@mapbox/search-js-react` |
| Loqate (GBG) | Strong UK/EU | Pay-per-use | REST API |
| SmartyStreets | US focus | Free tier available | REST API |

### Autocomplete Accessibility

- Announce autocomplete suggestions to screen readers with `aria-live="polite"` region
- Support keyboard navigation through suggestion list (arrow keys + Enter)
- Allow manual entry bypass (never force autocomplete selection)
- Handle paste events (users paste full addresses)

---

## Accessible Form Patterns

### Required Markup

```html
<form novalidate> <!-- Use custom validation, not browser default -->

  <fieldset>
    <legend>Contact Information</legend>

    <div class="form-group">
      <label for="name">
        Full Name <span aria-hidden="true">*</span>
        <span class="sr-only">(required)</span>
      </label>
      <input
        id="name"
        name="name"
        type="text"
        required
        aria-required="true"
        aria-describedby="name-hint"
        autocomplete="name"
      />
      <p id="name-hint" class="hint">As it appears on your ID</p>
    </div>

    <div class="form-group" aria-live="polite">
      <label for="email">
        Email <span aria-hidden="true">*</span>
        <span class="sr-only">(required)</span>
      </label>
      <input
        id="email"
        name="email"
        type="email"
        required
        aria-required="true"
        aria-describedby="email-error"
        aria-invalid="false"
        autocomplete="email"
      />
      <!-- Error message (hidden until validation fails) -->
      <p id="email-error" class="error" role="alert" hidden>
        Please enter a valid email address
      </p>
    </div>

  </fieldset>

</form>
```

### Accessibility Checklist

- [ ] Every input has an associated `<label>` (via `for`/`id` or wrapping)
- [ ] Required fields marked with `aria-required="true"` and visual indicator
- [ ] Error messages linked to fields via `aria-describedby`
- [ ] `aria-invalid="true"` set on fields with errors
- [ ] Error messages use `role="alert"` or `aria-live` for dynamic announcement
- [ ] Form can be completed entirely with keyboard
- [ ] Tab order follows visual order
- [ ] `fieldset`/`legend` used for radio groups and checkbox groups
- [ ] Color is not the only indicator of error state (use icon + text + border)
- [ ] Sufficient contrast on labels, inputs, and error text (4.5:1 minimum)

---

## Mobile Form Optimization

### Mobile-Specific Rules

| Rule | Implementation | Impact |
|------|---------------|--------|
| Use correct `inputmode` | `inputmode="numeric"` for numbers | Shows number keyboard |
| Correct `type` attribute | `type="email"`, `type="tel"` | Optimized keyboard layout |
| Sticky submit button | Position above keyboard with `position: sticky` | Always accessible |
| Avoid dropdowns for < 5 options | Use segmented control or radio buttons | Faster selection |
| Full-width inputs | `width: 100%` on all form fields | Larger tap targets |
| Sufficient spacing | Minimum 8px between fields, 44px tap targets | Prevent mis-taps |
| Disable zoom on focus | `<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">` | Prevent layout shift |

### Keyboard Management

```javascript
// Scroll to active input when keyboard appears (mobile web)
document.querySelectorAll('input, textarea, select').forEach(el => {
  el.addEventListener('focus', () => {
    // Wait for keyboard animation
    setTimeout(() => {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 300);
  });
});
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|-------------|-------------|------------------|
| Placeholder-only labels | Label disappears, memory burden, accessibility fail | Top-aligned labels or floating labels |
| Validate on focus (before typing) | Shows errors before user has a chance to input | Validate on blur or on submit |
| "Clear form" button near "Submit" | Accidental data loss | Remove or move far from submit |
| All fields required without explanation | Users question why you need all this data | Mark optional fields, explain sensitive fields |
| CAPTCHA before form completion | Interrupts flow, high abandonment | Place CAPTCHA at submit, or use invisible reCAPTCHA |
| Reset scroll on validation error | User loses context of what they entered | Scroll to first error, keep other data intact |
| Disabled submit until all valid | User doesn't know what's wrong | Enable submit always; show errors on click |
| Auto-advancing multi-step on valid | User loses control, can't review current step | Explicit "Next" button per step |

---

## References

- [Baymard Institute — Form Usability](https://baymard.com/blog/form-usability)
- [Nielsen Norman Group — Form Design](https://www.nngroup.com/articles/form-design/)
- [GOV.UK Design System — Forms](https://design-system.service.gov.uk/patterns/)
- [WCAG 2.2 — Input Purpose (1.3.5)](https://www.w3.org/WAI/WCAG22/Understanding/identify-input-purpose.html)
- [Web.dev — Best Practices for Form Design](https://web.dev/articles/sign-in-form-best-practices)
- [Wroblewski, Luke. Web Form Design. Rosenfeld Media, 2008.](https://www.lukew.com/resources/web_form_design.asp)

---

## Cross-References

- [SKILL.md](../SKILL.md) — Parent skill overview and interaction checklist
- [mobile-ux-patterns.md](mobile-ux-patterns.md) — Mobile form optimization and input types
- [wcag-accessibility.md](wcag-accessibility.md) — WCAG 2.2 form requirements
- [cro-framework.md](cro-framework.md) — Checkout and signup flow optimization
- [nielsen-heuristics.md](nielsen-heuristics.md) — Error prevention and recovery heuristics
