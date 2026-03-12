# WCAG Accessibility Standards — Detailed Guide

Web Content Accessibility Guidelines (WCAG) 2.2 are international standards for making web content accessible to people with disabilities. WCAG 2.2 is a W3C Recommendation (2024-12-12).

---

## The Four Principles (POUR)

WCAG is organized around four core principles. Web content must be:

1. **Perceivable** — Information and UI components must be presentable to users in ways they can perceive
2. **Operable** — UI components and navigation must be operable
3. **Understandable** — Information and operation of UI must be understandable
4. **Robust** — Content must be robust enough to work with current and future technologies

---

## Conformance Levels

WCAG defines three levels of conformance:

- **Level A** — Minimum level of accessibility (essential)
- **Level AA** — Standard level for most organizations (recommended)
- **Level AAA** — Highest level (not always achievable for all content)

**Industry Standard**: Most organizations target **Level AA compliance** as the baseline.

---

## 1. Perceivable

Users must be able to perceive the information being presented.

### 1.1 Text Alternatives

Provide text alternatives for non-text content.

**1.1.1 Non-text Content (Level A)**
- All images must have alt text
- Decorative images: `alt=""`
- Functional images: Describe purpose
- Complex images: Provide detailed description

```html
<!-- Good: Informative image -->
<img src="chart.png" alt="Sales increased 40% in Q3 2024">

<!-- Good: Decorative image -->
<img src="divider.png" alt="" role="presentation">

<!-- Good: Functional image -->
<img src="search.svg" alt="Search">

<!-- Bad: Missing alt -->
<img src="important-chart.png">
```

### 1.2 Time-based Media

Provide alternatives for audio and video content.

**1.2.1 Audio-only and Video-only (Level A)**
- Audio-only: Provide transcript
- Video-only: Provide audio track or text description

**1.2.2 Captions (Level A)**
- All pre-recorded video must have captions
- Synchronized with audio
- Include speaker identification and sound effects

**1.2.3 Audio Description or Media Alternative (Level A)**
- Provide audio description or full text alternative

**1.2.4 Captions (Live) (Level AA)**
- Live audio content must have captions

**1.2.5 Audio Description (Level AA)**
- All pre-recorded video must have audio description

```html
<!-- Video with captions and audio description -->
<video controls>
  <source src="video.mp4" type="video/mp4">
  <track kind="captions" src="captions-en.vtt" srclang="en" label="English">
  <track kind="descriptions" src="descriptions-en.vtt" srclang="en">
</video>
```

### 1.3 Adaptable

Create content that can be presented in different ways without losing meaning.

**1.3.1 Info and Relationships (Level A)**
- Use semantic HTML (headings, lists, tables)
- Structure content logically
- Use ARIA roles appropriately

```html
<!-- Good: Semantic structure -->
<nav>
  <ul>
    <li><a href="/">Home</a></li>
    <li><a href="/about">About</a></li>
  </ul>
</nav>

<!-- Bad: Non-semantic -->
<div class="nav">
  <span onclick="goTo('/')">Home</span>
  <span onclick="goTo('/about')">About</span>
</div>
```

**1.3.2 Meaningful Sequence (Level A)**
- Reading order makes sense when linearized
- CSS should not change logical order

**1.3.3 Sensory Characteristics (Level A)**
- Don't rely solely on sensory characteristics
- "Click the green button" → "Click the Submit button (green)"
- Don't rely only on shape, size, visual location, or sound

**1.3.4 Orientation (Level AA) — NEW in WCAG 2.1**
- Don't restrict to single orientation (portrait/landscape)
- Unless specific orientation is essential

**1.3.5 Identify Input Purpose (Level AA)**
- Use autocomplete attributes for user information

```html
<input type="email" name="email" autocomplete="email">
<input type="tel" name="phone" autocomplete="tel">
<input type="text" name="name" autocomplete="name">
```

### 1.4 Distinguishable

Make it easier for users to see and hear content.

**1.4.1 Use of Color (Level A)**
- Don't use color as the only means of conveying information
- Add icons, labels, or patterns in addition to color

```html
<!-- Bad: Color only -->
<span style="color: red;">Error</span>

<!-- Good: Icon + color -->
<span style="color: red;">
  <svg aria-hidden="true"><!-- error icon --></svg>
  Error: Email is required
</span>
```

**1.4.3 Contrast (Minimum) (Level AA)**
- Text contrast ratio: **4.5:1** minimum
- Large text (18pt+): **3:1** minimum
- Test with WebAIM Contrast Checker

**1.4.6 Contrast (Enhanced) (Level AAA)**
- Text contrast ratio: **7:1** minimum
- Large text: **4.5:1** minimum

**1.4.10 Reflow (Level AA) — NEW in WCAG 2.1**
- Content reflows to 320px width without scrolling in two dimensions
- No horizontal scrolling at 400% zoom

**1.4.11 Non-text Contrast (Level AA) — NEW in WCAG 2.1**
- UI components and graphics: **3:1** contrast ratio
- Includes buttons, form borders, focus indicators

**1.4.12 Text Spacing (Level AA) — NEW in WCAG 2.1**
- Content adapts when users adjust text spacing
- Line height: 1.5x font size
- Paragraph spacing: 2x font size

**1.4.13 Content on Hover or Focus (Level AA) — NEW in WCAG 2.1**
- Tooltips/popovers must be:
  - Dismissible (ESC key closes)
  - Hoverable (user can move pointer over it)
  - Persistent (doesn't disappear on its own)

---

## 2. Operable

Users must be able to operate the interface.

### 2.1 Keyboard Accessible

Make all functionality available from a keyboard.

**2.1.1 Keyboard (Level A)**
- All functionality must work with keyboard only
- No keyboard traps
- Tab order is logical

```jsx
// Good: Keyboard accessible custom button
function CustomButton({ onClick, children }) {
  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
    >
      {children}
    </div>
  );
}
```

**2.1.2 No Keyboard Trap (Level A)**
- Users can navigate away using keyboard only
- If focus is trapped (modal), provide clear exit method

**2.1.4 Character Key Shortcuts (Level A) — NEW in WCAG 2.1**
- Single-key shortcuts can be turned off or remapped
- Or only active when component has focus

### 2.2 Enough Time

Provide users enough time to read and use content.

**2.2.1 Timing Adjustable (Level A)**
- User can turn off, adjust, or extend time limits
- Or time limit > 20 hours

**2.2.2 Pause, Stop, Hide (Level A)**
- Auto-updating content can be paused/stopped
- Applies to content that auto-updates > 5 seconds

### 2.3 Seizures and Physical Reactions

Do not design content in a way that is known to cause seizures.

**2.3.1 Three Flashes or Below Threshold (Level A)**
- No content flashes more than 3 times per second
- Or flash is below general flash and red flash thresholds

### 2.4 Navigable

Provide ways to help users navigate and find content.

**2.4.1 Bypass Blocks (Level A)**
- "Skip to main content" link
- Landmarks and headings for navigation

```html
<body>
  <a href="#main" class="skip-link">Skip to main content</a>
  <nav><!-- navigation --></nav>
  <main id="main"><!-- main content --></main>
</body>
```

**2.4.2 Page Titled (Level A)**
- Every page has descriptive title

```html
<title>Contact Us - Acme Corporation</title>
```

**2.4.3 Focus Order (Level A)**
- Focus order preserves meaning and operability
- Tab order matches visual order

**2.4.4 Link Purpose (Level A)**
- Link text describes destination
- Avoid "Click here" or "Read more" without context

```html
<!-- Bad -->
<a href="/report.pdf">Click here</a> for the annual report.

<!-- Good -->
<a href="/report.pdf">Download the 2024 Annual Report (PDF)</a>
```

**2.4.5 Multiple Ways (Level AA)**
- Provide multiple ways to find pages
- Site map, search, navigation menu

**2.4.6 Headings and Labels (Level AA)**
- Headings and labels are descriptive
- Use proper heading hierarchy (h1, h2, h3)

**2.4.7 Focus Visible (Level AA)**
- Keyboard focus indicator is visible
- Don't remove focus outline without replacing it

```css
/* Bad: Removes focus outline */
button:focus {
  outline: none;
}

/* Good: Custom focus style */
button:focus {
  outline: 2px solid #005fcc;
  outline-offset: 2px;
}
```

**2.4.11 Focus Not Obscured (Minimum) (Level AA) — NEW in WCAG 2.2**
- Focused element is at least partially visible
- Not completely hidden by sticky headers/footers

**2.4.13 Focus Appearance (Level AAA) — NEW in WCAG 2.2**
- Focus indicator has sufficient size and contrast

### 2.5 Input Modalities

Make it easier for users to operate functionality through various inputs.

**2.5.1 Pointer Gestures (Level A) — NEW in WCAG 2.1**
- Complex gestures (multi-point, path-based) have single-pointer alternative
- Swipe, pinch, twist must have alternatives

**2.5.2 Pointer Cancellation (Level A) — NEW in WCAG 2.1**
- Action triggered on up-event (not down-event)
- Allows users to cancel by moving pointer away

**2.5.3 Label in Name (Level A) — NEW in WCAG 2.1**
- Visual label matches accessible name
- "Submit" button has aria-label="Submit" (or similar)

**2.5.4 Motion Actuation (Level A) — NEW in WCAG 2.1**
- Functionality triggered by motion (shake, tilt) has UI alternative
- And can be disabled

**2.5.7 Dragging Movements (Level AA) — NEW in WCAG 2.2**
- Dragging actions have single-pointer alternative
- Drag-and-drop must have click-based alternative

**2.5.8 Target Size (Minimum) (Level AA) — NEW in WCAG 2.2**
- Touch targets at least **24x24 CSS pixels**
- Exceptions: inline links, user agent controlled, essential

```css
/* Ensure adequate touch targets */
button, a {
  min-width: 44px;
  min-height: 44px;
  /* WCAG 2.2: 24px minimum, 44px recommended */
}
```

---

## 3. Understandable

Information and operation of UI must be understandable.

### 3.1 Readable

Make text content readable and understandable.

**3.1.1 Language of Page (Level A)**
- Declare primary language

```html
<html lang="en">
```

**3.1.2 Language of Parts (Level AA)**
- Identify language changes within content

```html
<p>The French phrase <span lang="fr">bon appétit</span> means enjoy your meal.</p>
```

### 3.2 Predictable

Make web pages appear and operate in predictable ways.

**3.2.1 On Focus (Level A)**
- Focusing an element doesn't trigger unexpected context change
- No auto-submit on focus

**3.2.2 On Input (Level A)**
- Changing a setting doesn't automatically trigger action
- Unless user is warned beforehand

```html
<!-- Bad: Auto-submit on select -->
<select onchange="this.form.submit()">

<!-- Good: Explicit submit -->
<select id="country">...</select>
<button type="submit">Continue</button>
```

**3.2.3 Consistent Navigation (Level AA)**
- Navigation appears in same location across pages
- Same order unless user initiates change

**3.2.4 Consistent Identification (Level AA)**
- Components with same functionality have consistent labels
- Search icon always labeled "Search"

**3.2.6 Consistent Help (Level A) — NEW in WCAG 2.2**
- Help mechanisms appear in consistent location

### 3.3 Input Assistance

Help users avoid and correct mistakes.

**3.3.1 Error Identification (Level A)**
- Errors are identified in text
- Which field has error and what is wrong

```html
<label for="email">Email *</label>
<input
  type="email"
  id="email"
  aria-invalid="true"
  aria-describedby="email-error"
>
<span id="email-error" role="alert">
  Please enter a valid email address
</span>
```

**3.3.2 Labels or Instructions (Level A)**
- Labels provided for all form inputs
- Instructions for required format

```html
<label for="phone">
  Phone number
  <span class="format">(Format: 555-123-4567)</span>
</label>
<input type="tel" id="phone" required>
```

**3.3.3 Error Suggestion (Level AA)**
- Provide suggestions for fixing errors
- If error can be detected automatically

**3.3.4 Error Prevention (Legal, Financial, Data) (Level AA)**
- Submissions are reversible, verified, or confirmed
- Applies to legal/financial transactions

**3.3.7 Redundant Entry (Level A) — NEW in WCAG 2.2**
- Don't ask for same information twice in same session
- Use autocomplete or pre-fill from previous steps

**3.3.8 Accessible Authentication (Minimum) (Level AA) — NEW in WCAG 2.2**
- Don't require cognitive function tests (CAPTCHAs)
- Support password managers
- Provide alternatives (magic links, biometrics)

```html
<!-- Support password managers -->
<input
  type="password"
  autocomplete="current-password"
  id="password"
>
```

---

## 4. Robust

Content must work with current and future technologies.

### 4.1 Compatible

Maximize compatibility with current and future tools.

**4.1.1 Parsing (Level A) — DEPRECATED in WCAG 2.2**
- (Removed: HTML5 validation handles this)

**4.1.2 Name, Role, Value (Level A)**
- All UI components have accessible name and role
- State communicated to assistive technologies

```html
<!-- Native controls have built-in accessibility -->
<button>Submit</button>

<!-- Custom controls need ARIA -->
<div
  role="button"
  tabIndex={0}
  aria-label="Submit form"
  aria-pressed="false"
>
  Submit
</div>
```

**4.1.3 Status Messages (Level AA)**
- Status messages can be determined by assistive tech
- Use ARIA live regions

```html
<div role="status" aria-live="polite">
  Item added to cart
</div>

<div role="alert" aria-live="assertive">
  Error: Payment failed
</div>
```

---

## ARIA (Accessible Rich Internet Applications)

### When to Use ARIA

**First Rule of ARIA**: Don't use ARIA if you can use native HTML.

```html
<!-- Good: Native HTML -->
<button>Click me</button>

<!-- Bad: Unnecessary ARIA -->
<div role="button" tabindex="0">Click me</div>
```

### Common ARIA Patterns

**Landmarks**
```html
<header role="banner">
<nav role="navigation">
<main role="main">
<aside role="complementary">
<footer role="contentinfo">
```

**Live Regions**
```html
<!-- Polite: Wait for pause in speech -->
<div aria-live="polite">Items found: 42</div>

<!-- Assertive: Interrupt immediately -->
<div aria-live="assertive" role="alert">Error occurred!</div>
```

**Form Labels**
```html
<label id="username-label">Username</label>
<input aria-labelledby="username-label" aria-required="true">

<!-- Additional description -->
<input
  aria-label="Search"
  aria-describedby="search-help"
>
<span id="search-help">Enter product name or SKU</span>
```

**States**
```html
<button aria-pressed="true">Bold</button>
<input type="checkbox" aria-checked="true">
<div role="tab" aria-selected="true">Home</div>
<button aria-expanded="false" aria-controls="menu">Menu</button>
```

**Hiding Content**
```html
<!-- Hidden from everyone -->
<div hidden>Not visible</div>

<!-- Hidden from screen readers only -->
<span aria-hidden="true">[decorative icon]</span>

<!-- Visually hidden, available to screen readers -->
<span class="sr-only">New messages: 3</span>
```

---

## Testing Tools

### Automated Testing

**Browser Extensions**
- axe DevTools (Deque) — Most comprehensive
- WAVE (WebAIM) — Visual feedback
- Lighthouse (Google) — Integrated in Chrome DevTools

**CI/CD Integration**
- axe-core (JavaScript library)
- pa11y (Command-line tool)
- Lighthouse CI

```bash
# Install axe-core for automated tests
npm install --save-dev @axe-core/react

# Run Lighthouse
lighthouse https://example.com --view
```

### Manual Testing

**Keyboard Testing**
- Navigate entire site with Tab, Enter, Arrows, Esc
- No keyboard traps
- All interactive elements reachable
- Focus visible at all times

**Screen Reader Testing**
- NVDA (Windows, free)
- JAWS (Windows, paid)
- VoiceOver (macOS/iOS, built-in)
- TalkBack (Android, built-in)

**Color Contrast**
- WebAIM Contrast Checker
- Colour Contrast Analyser (CCA)
- Browser DevTools (Chrome, Firefox)

**Zoom Testing**
- Test at 200% zoom
- Content still readable and functional
- No horizontal scrolling

---

## Quick Checklist

### Essential (Level A)

- [ ] All images have alt text
- [ ] All functionality works with keyboard
- [ ] No keyboard traps
- [ ] Forms have visible labels
- [ ] Errors are identified and explained
- [ ] Headings are in logical order
- [ ] Page has descriptive title
- [ ] HTML lang attribute set
- [ ] Color is not the only means of conveying information

### Standard (Level AA)

- [ ] Text contrast ratio 4.5:1 (3:1 for large text)
- [ ] UI component contrast 3:1
- [ ] Touch targets minimum 24x24px (44x44px recommended)
- [ ] Focus indicators visible
- [ ] Multiple ways to find pages (menu, search, sitemap)
- [ ] Consistent navigation across site
- [ ] Captions for all video/audio
- [ ] Content reflows at 320px width (no horizontal scroll)
- [ ] Autocomplete attributes on form inputs

### Enhanced (Level AAA)

- [ ] Text contrast ratio 7:1
- [ ] No time limits on content
- [ ] Sign language interpretation for video
- [ ] Context-sensitive help available

---

## Common Accessibility Mistakes

1. **Missing alt text on images**
   - Use meaningful alt text
   - Decorative images: `alt=""`

2. **Low color contrast**
   - Test all text against backgrounds
   - Minimum 4.5:1 for normal text

3. **Keyboard inaccessible components**
   - All interactive elements must be keyboard accessible
   - Use native HTML when possible

4. **Missing form labels**
   - Every input needs a visible label
   - Use `<label>` element

5. **Non-semantic HTML**
   - Use `<button>`, `<nav>`, `<main>` instead of `<div>`
   - Proper heading hierarchy

6. **Auto-playing media**
   - No auto-play with sound
   - Provide pause/stop controls

7. **Unclear error messages**
   - Explain what's wrong and how to fix
   - Associate errors with fields

8. **Small touch targets**
   - Minimum 24x24px (44x44px recommended)
   - Adequate spacing between targets

9. **Removing focus outlines**
   - Always provide visible focus indicator
   - Custom focus styles must meet contrast requirements

10. **CAPTCHAs without alternatives**
    - Provide audio alternative
    - Or use non-cognitive challenges

---

## WCAG 3.0 Preview (Coming 2026+)

W3C is developing WCAG 3.0, a major revision expected to be finalized in 2026-2027. The September 2025 draft introduces significant changes.

### Key Changes from WCAG 2.x

**New Structure**:
- **174 outcomes** (vs 78 success criteria in WCAG 2.2)
- Terminology shift: "outcomes" instead of "success criteria"
- Broader scope: websites, apps, authoring tools, VR/AR

**New Scoring System**:
- **0-4 scale** replaces pass/fail binary
  - 0 = Very poor
  - 1 = Poor
  - 2 = Fair
  - 3 = Good
  - 4 = Excellent

**New Conformance Levels**:
| Level | Description | Comparable To |
|-------|-------------|---------------|
| **Bronze** | Basic accessibility | WCAG 2.2 AA |
| **Silver** | Bronze + assistive tech testing + user testing | Beyond AA |
| **Gold** | Exemplary model of accessibility | Excellence |

### What to Do Now

1. **Continue targeting WCAG 2.2 AA** — remains the legal baseline
2. **Monitor WCAG 3.0 development** — [W3C WCAG 3.0 Draft](https://www.w3.org/TR/wcag-3.0/)
3. **Build accessible foundations** — good 2.2 compliance prepares you for 3.0
4. **Don't wait** — WCAG 2.2 won't be deprecated for years after 3.0 finalizes

### Timeline

- **2025**: Working drafts, public review
- **2026**: Projected timeline announcement (April 2026)
- **2027+**: Expected finalization
- **WCAG 2.2**: Remains valid for several years after 3.0

---

## Resources

**Official WCAG Documentation**
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [Understanding WCAG 2.2](https://www.w3.org/WAI/WCAG22/Understanding/)
- [How to Meet WCAG (Quick Reference)](https://www.w3.org/WAI/WCAG22/quickref/)
- [WCAG 3.0 Working Draft](https://www.w3.org/TR/wcag-3.0/)
- [WCAG 3 Introduction](https://www.w3.org/WAI/standards-guidelines/wcag/wcag3-intro/)

**Testing Tools**
- [WebAIM Contrast Checker](https://webaim.org/references/contrastchecker/)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [WAVE Browser Extension](https://wave.webaim.org/extension/)

**Learning Resources**
- [WebAIM Articles](https://webaim.org/articles/)
- [A11y Project](https://www.a11yproject.com/)
- [Inclusive Components](https://inclusive-components.design/)

**ARIA**
- [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [ARIA in HTML](https://www.w3.org/TR/html-aria/)
