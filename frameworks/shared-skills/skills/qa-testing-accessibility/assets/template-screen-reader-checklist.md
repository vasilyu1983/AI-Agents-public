# Screen Reader Testing Checklist

Per-flow checklist for manual screen reader verification. Copy and fill out for each critical user flow.

## Flow Metadata

| Field | Value |
|-------|-------|
| Flow Name | {{flow_name}} |
| Screen Reader | VoiceOver / NVDA / TalkBack |
| Platform | macOS / iOS / Windows / Android |
| Browser / App | {{browser_or_app}} |
| Tester | {{tester}} |
| Date | {{date}} |

## Page Structure

| Check | Pass | Fail | N/A | Notes |
|-------|------|------|-----|-------|
| Page title announced on load | | | | |
| Skip navigation link present and functional | | | | |
| Landmarks announced (banner, nav, main, contentinfo) | | | | |
| Heading hierarchy logical (h1 → h2 → h3) | | | | |
| Heading navigation reaches all major sections | | | | |

## Images and Media

| Check | Pass | Fail | N/A | Notes |
|-------|------|------|-----|-------|
| Informational images have descriptive alt text | | | | |
| Decorative images are hidden from AT (`alt=""` or `aria-hidden`) | | | | |
| Complex images have long description or equivalent text | | | | |
| Video/audio has captions or transcript | | | | |

## Forms

| Check | Pass | Fail | N/A | Notes |
|-------|------|------|-----|-------|
| All form fields announce labels on focus | | | | |
| Required fields indicated audibly | | | | |
| Input type/format hints announced | | | | |
| Validation errors announced when they appear | | | | |
| Error messages associated with specific fields | | | | |
| Error summary reachable and lists all errors | | | | |
| Submit confirmation announced | | | | |

## Navigation and Links

| Check | Pass | Fail | N/A | Notes |
|-------|------|------|-----|-------|
| All links have descriptive text (not "click here") | | | | |
| Links that open new windows announce behavior | | | | |
| Breadcrumbs navigable and announce current page | | | | |
| Navigation menus operable via keyboard | | | | |
| Dropdown menus announce expanded/collapsed state | | | | |

## Dynamic Content

| Check | Pass | Fail | N/A | Notes |
|-------|------|------|-----|-------|
| Loading states announced | | | | |
| Content updates announced via live regions | | | | |
| Toast/notification messages announced | | | | |
| Search results announced when updated | | | | |
| Infinite scroll or pagination accessible | | | | |

## Modals and Overlays

| Check | Pass | Fail | N/A | Notes |
|-------|------|------|-----|-------|
| Modal title announced on open | | | | |
| Focus moves inside modal on open | | | | |
| Tab cycles within modal only (focus trap) | | | | |
| Escape key closes modal | | | | |
| Focus returns to trigger element on close | | | | |
| Background content inert while modal is open | | | | |

## Custom Widgets

| Check | Pass | Fail | N/A | Notes |
|-------|------|------|-----|-------|
| Tabs: role and selected state announced | | | | |
| Tabs: arrow keys switch tabs | | | | |
| Accordion: expanded/collapsed state announced | | | | |
| Combobox: options announced during navigation | | | | |
| Datepicker: navigable and announces selected date | | | | |
| Carousel: controls announced, auto-play pauseable | | | | |

## Flow Completion

| Check | Pass | Fail | N/A | Notes |
|-------|------|------|-----|-------|
| Entire flow completable with screen reader only | | | | |
| No unexpected focus loss during the flow | | | | |
| Success/confirmation state announced clearly | | | | |
| Error recovery path accessible | | | | |

## Summary

| Category | Pass | Fail | N/A |
|----------|------|------|-----|
| Page Structure | | | |
| Images and Media | | | |
| Forms | | | |
| Navigation and Links | | | |
| Dynamic Content | | | |
| Modals and Overlays | | | |
| Custom Widgets | | | |
| Flow Completion | | | |
| **Total** | | | |

## Issues Found

| # | Category | Description | Severity | WCAG Criterion |
|---|----------|-------------|----------|----------------|
| 1 | | | Critical / Serious / Moderate | |
