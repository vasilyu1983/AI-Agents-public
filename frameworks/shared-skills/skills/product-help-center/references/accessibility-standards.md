# Accessibility Standards

Accessibility requirements and operational checklists for help center content.

## Contents

- WCAG 2.2 AA requirements for help centers
- Content structure
- Media accessibility
- Color and contrast
- Interactive elements
- Screen reader compatibility
- Testing tools
- Platform accessibility features
- Legal context
- Checklist: help center accessibility audit
- Do/Avoid

## WCAG 2.2 AA Requirements for Help Centers

WCAG 2.2 AA is the standard to target. It covers perceivable, operable, understandable, and robust content.

Key criteria most relevant to help centers:

| WCAG Criterion | ID | What It Means for Help Centers |
|----------------|-----|-------------------------------|
| Non-text Content | 1.1.1 | All images need alt text |
| Captions (Prerecorded) | 1.2.2 | Videos need captions |
| Info and Relationships | 1.3.1 | Use semantic HTML (headings, lists, tables) |
| Contrast (Minimum) | 1.4.3 | 4.5:1 for text, 3:1 for large text |
| Resize Text | 1.4.4 | Content usable at 200% zoom |
| Keyboard | 2.1.1 | All functionality via keyboard |
| Focus Visible | 2.4.7 | Visible focus indicator on interactive elements |
| Headings and Labels | 2.4.6 | Descriptive headings that convey topic |
| Target Size | 2.5.8 | Minimum 24x24px for touch targets (new in 2.2) |
| Consistent Navigation | 3.2.3 | Navigation in same relative order across pages |
| Error Identification | 3.3.1 | Form errors clearly described |
| Parsing | 4.1.1 | Valid HTML |

## Content Structure

Structure is the foundation of accessible help content.

```
HEADINGS

- Use one H1 per page (the article title)
- Follow heading hierarchy: H1 > H2 > H3 — never skip levels
- Make headings descriptive: "Reset your password" not "Step 2"
- Do not use bold text as a fake heading — use actual heading tags

LISTS

- Use ordered lists for sequential steps
- Use unordered lists for non-sequential items
- Do not use dashes or asterisks as visual bullets in plain text — use <ul>/<ol>

LINK TEXT

- Descriptive: "Read the billing FAQ" — not "click here"
- Unique: two different links on the same page should not both say "Learn more"
- Indicate when a link opens a new window or downloads a file

TABLES

- Use <th> for header cells with scope="col" or scope="row"
- Add a <caption> describing the table purpose
- Do not use tables for layout — only for tabular data
- Keep tables simple: avoid merged cells when possible
```

## Media Accessibility

```
IMAGES

- Every informational image needs alt text describing its content
- Decorative images: use alt="" (empty alt) so screen readers skip them
- Screenshots: describe the key element shown, not every pixel
  Good: "Settings page with the Security tab highlighted"
  Bad: "Screenshot" or "Image of the settings page showing the left sidebar with..."
- Do not embed text in images — screen readers cannot read it

VIDEO

- Provide captions for all video content (auto-captions need human review)
- Provide a text transcript as an alternative
- Do not autoplay video with sound
- Include audio descriptions if visual content is not conveyed by narration

AUDIO

- Provide a transcript for podcasts and audio content
- Ensure audio player controls are keyboard accessible
```

## Color and Contrast

```
TEXT CONTRAST

- Normal text (<18px): minimum 4.5:1 contrast ratio against background
- Large text (18px+ or 14px+ bold): minimum 3:1 contrast ratio
- Use WebAIM Contrast Checker or browser DevTools to verify

COLOR AS INFORMATION

- Never use color alone to convey meaning
  Bad: "Required fields are in red"
  Good: "Required fields are marked with an asterisk (*) and red border"
- Status indicators need icon + color (not color only)
- Links must be distinguishable from body text by more than color
  (underline or 3:1 contrast difference from surrounding text)

UI COMPONENTS

- Form input borders: minimum 3:1 contrast against background
- Focus indicators: minimum 3:1 contrast
- Buttons: text on button must meet contrast requirements
- Disabled elements: no contrast requirement, but avoid relying on them
```

## Interactive Elements

Help centers have search bars, navigation menus, feedback forms, and expandable sections. All must be keyboard accessible.

```
KEYBOARD ACCESSIBILITY

- Tab order follows visual reading order (left to right, top to bottom)
- All interactive elements reachable via Tab key
- Visible focus indicator on every focusable element
- Enter/Space activates buttons and links
- Escape closes modals, dropdowns, and overlays
- Arrow keys navigate within menus, tabs, and carousels

SEARCH

- Search input has a visible label or accessible name (aria-label)
- Search results announce count to screen readers
- Zero-result state is announced, not just visually displayed
- Autocomplete suggestions are navigable by keyboard

FORMS (feedback, contact)

- Every input has a visible <label> or aria-label
- Required fields indicated in label text (not just color)
- Error messages associated with the input via aria-describedby
- Error summary listed at top of form on submission failure
- Success confirmation announced to screen readers

EXPANDABLE/COLLAPSIBLE CONTENT (FAQ toggles, accordions)

- Use <button> with aria-expanded="true/false"
- Content region uses aria-controls linking to the content ID
- Keyboard: Enter/Space toggles open/close
```

## Screen Reader Compatibility

```
SEMANTIC HTML

- Use <nav> for navigation
- Use <main> for primary content
- Use <aside> for sidebar
- Use <header> and <footer> for page header/footer
- Use <article> for self-contained content (each help article)

ARIA LANDMARKS

- Banner: <header role="banner"> (once per page)
- Navigation: <nav role="navigation" aria-label="Main">
- Main: <main role="main">
- Search: <form role="search">
- Complementary: <aside role="complementary">
- Content info: <footer role="contentinfo">

ARIA BEST PRACTICES

- Prefer native HTML elements over ARIA when possible
  (<button> over <div role="button">)
- Use aria-label for elements without visible text
- Use aria-live="polite" for dynamic content updates (search results, notifications)
- Use aria-current="page" on the active navigation item
- Do not use aria-hidden="true" on visible content
```

## Testing Tools

| Tool | Type | What It Catches | Cost |
|------|------|----------------|------|
| axe DevTools | Browser extension | Automated WCAG violations | Free (core) |
| WAVE | Browser extension | Visual accessibility overlay | Free |
| Lighthouse | Built into Chrome | Accessibility score + audit | Free |
| Pa11y | CLI / CI integration | Automated scanning, CI pipelines | Free (open source) |
| NVDA | Screen reader (Windows) | Real screen reader testing | Free |
| VoiceOver | Screen reader (macOS/iOS) | Real screen reader testing | Built-in |
| JAWS | Screen reader (Windows) | Enterprise screen reader testing | $90/yr |
| WebAIM Contrast Checker | Web tool | Color contrast ratios | Free |

```
TESTING PROCESS

1. Automated scan (axe or Lighthouse)
   - Run on every page template (home, category, article, search results)
   - Fix all Critical and Serious issues
   - Automated tools catch ~30-40% of issues

2. Keyboard testing (manual)
   - Tab through entire page — can you reach everything?
   - Can you use search, navigation, and forms without a mouse?
   - Is focus visible at all times?

3. Screen reader testing (manual)
   - Test with VoiceOver (macOS) or NVDA (Windows)
   - Navigate an article by headings — do they make sense?
   - Read a how-to article — are steps clear without seeing the page?
   - Submit a feedback form — are errors announced?

4. Zoom testing
   - Zoom to 200% — is all content still usable?
   - No horizontal scrolling at 320px viewport width (reflow)
```

## Platform Accessibility Features

```
ZENDESK GUIDE

- Copenhagen theme meets basic accessibility standards
- Customize with accessible color contrast
- Use built-in heading styles (do not override with custom CSS that breaks semantics)
- Article feedback widget is keyboard accessible
- Enable skip-to-content link in theme

INTERCOM

- Help Center articles render in semantic HTML
- Messenger widget supports keyboard navigation
- Fin AI responses are screen-reader compatible
- Custom themes: verify contrast and focus indicators

FRESHDESK

- Portal themes include basic accessibility
- Custom CSS: maintain focus indicators and contrast
- Knowledge base article editor outputs semantic HTML
- Test Freddy widget for keyboard access

GITBOOK

- Outputs semantic HTML by default
- Built-in dark mode and light mode
- Keyboard navigable sidebar and search
- Verify custom themes maintain accessibility
```

## Legal Context

| Regulation | Jurisdiction | Applies To | Key Requirement |
|------------|-------------|------------|-----------------|
| ADA Title III | United States | Public-facing websites | Accessible to people with disabilities; courts apply WCAG 2.1 AA |
| Section 508 | United States | Federal agencies and vendors | WCAG 2.0 AA (being updated to 2.1) |
| European Accessibility Act (EAA) | EU | Products and services sold in EU | WCAG 2.1 AA; enforcement from June 2025 |
| EN 301 549 | EU | ICT products and services | Harmonized standard for EU accessibility |
| AODA | Ontario, Canada | Organizations with 50+ employees | WCAG 2.0 AA |
| Equality Act 2010 | United Kingdom | Service providers | Reasonable adjustments for disabled users |

Practical guidance: target WCAG 2.2 AA. It satisfies all the above regulations and is the current best practice.

## Checklist: Help Center Accessibility Audit

```
CONTENT

- [ ] All images have descriptive alt text (or empty alt for decorative)
- [ ] Videos have captions and transcripts
- [ ] Headings follow H1 > H2 > H3 hierarchy, no skipped levels
- [ ] Link text is descriptive (no "click here")
- [ ] Tables use <th> headers with scope
- [ ] No information conveyed by color alone

DESIGN

- [ ] Text contrast meets 4.5:1 (normal) and 3:1 (large)
- [ ] Focus indicators visible on all interactive elements
- [ ] Touch targets are at least 24x24px
- [ ] Content is usable at 200% zoom without horizontal scrolling
- [ ] Fonts are readable at default size (16px minimum body text)

INTERACTIVE

- [ ] All functionality accessible via keyboard
- [ ] Tab order matches visual order
- [ ] Search input has accessible label
- [ ] Form errors are announced and described
- [ ] Expandable sections use proper ARIA attributes

TECHNICAL

- [ ] Semantic HTML used (nav, main, article, header, footer)
- [ ] ARIA landmarks present and correct
- [ ] Language attribute set on <html> tag
- [ ] Page titles are unique and descriptive
- [ ] Skip-to-content link present

TESTING

- [ ] Automated scan (axe/Lighthouse) — zero Critical/Serious issues
- [ ] Keyboard-only navigation tested on all page types
- [ ] Screen reader tested on at least one article
- [ ] Mobile accessibility tested (touch, zoom, reflow)
```

## Do/Avoid

```
DO

- Write alt text that describes the purpose of the image, not just appearance
- Use native HTML elements before reaching for ARIA
- Test with real screen readers, not just automated tools
- Include accessibility in your content review checklist
- Set up automated accessibility scanning in CI/CD if using docs-as-code
- Train content authors on heading hierarchy and link text

AVOID

- Using images of text instead of actual text
- Removing focus outlines for aesthetic reasons
- Relying on placeholder text as the only label for form inputs
- Using "click here" or "read more" as link text
- Hiding content with display:none when it should be accessible
- Assuming automated tools catch all issues (they catch 30-40%)
- Treating accessibility as a one-time project instead of ongoing practice
```
