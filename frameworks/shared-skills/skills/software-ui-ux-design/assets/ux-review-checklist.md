# UI/UX Design Review Checklist

Comprehensive checklist for reviewing UI/UX design quality across all platforms.

---

## Core Review (All Products)

### 1. Interaction Design Fundamentals

| Check | Pass | Notes |
|-------|------|-------|
| **Affordances visible**: Interactive elements look clickable/tappable | [ ] | |
| **Feedback immediate**: Every action produces visible response (aim ~0.1s for direct manipulation) | [ ] | |
| **System status visible**: User always knows what's happening | [ ] | |
| **Error prevention**: Constraints prevent invalid states | [ ] | |
| **Error recovery**: Clear error messages with fix instructions | [ ] | |
| **Undo available**: Destructive actions are reversible or confirmed | [ ] | |
| **Consistency**: Same action = same result throughout | [ ] | |

### 2. Information Architecture

| Check | Pass | Notes |
|-------|------|-------|
| **Primary action obvious**: Clear on first scan [Inference] | [ ] | |
| **Navigation supports scale**: Search/filter/saved views for large content | [ ] | |
| **Breadcrumbs/back navigation**: User can always return | [ ] | |
| **Labels plain language**: No jargon, domain terms explained | [ ] | |
| **Search/filter available**: For content-heavy views | [ ] | |
| **Empty states actionable**: Guide user to populate | [ ] | |

### 3. State Handling

| Check | Pass | Notes |
|-------|------|-------|
| **Loading states**: Placeholder/progress for noticeable waits | [ ] | |
| **Empty states**: Illustration + message + CTA | [ ] | |
| **Error states**: Specific message + recovery action | [ ] | |
| **Partial data**: Graceful handling of incomplete data | [ ] | |
| **Offline state**: Clear indication + cached content | [ ] | |
| **Success confirmation**: Toast/inline for completed actions | [ ] | |

### 4. Form Design

| Check | Pass | Notes |
|-------|------|-------|
| **Labels visible**: Every input has associated label | [ ] | |
| **Validation on blur**: Not on keystroke, not only on submit | [ ] | |
| **Error messages inline**: Next to the problem field | [ ] | |
| **Required fields marked**: Asterisk or explicit text | [ ] | |
| **Input types correct**: Email, tel, number where appropriate | [ ] | |
| **Autocomplete attributes**: For user data fields | [ ] | |
| **Progress indicator**: For multi-step forms | [ ] | |
| **No redundant entry**: Avoid re-entering known info (WCAG 3.3.7) | [ ] | |
| **Accessible auth**: Avoid cognitive tests-only (WCAG 3.3.8) | [ ] | |

### 5. Accessibility (WCAG 2.2 AA)

| Check | Pass | Notes |
|-------|------|-------|
| **Color contrast ≥4.5:1**: Text on background | [ ] | |
| **Focus visible**: Clear focus indicator (WCAG 2.4.7/2.4.13) | [ ] | |
| **Focus not obscured**: Sticky UI doesn’t hide focus (WCAG 2.4.11) | [ ] | |
| **Focus order logical**: Matches visual reading order | [ ] | |
| **Keyboard navigable**: All features work without mouse | [ ] | |
| **Target size**: Meets WCAG 2.5.8 minimum (24×24 CSS px) | [ ] | |
| **Screen reader compatible**: ARIA labels, semantic HTML | [ ] | |
| **Reduced motion**: Respects `prefers-reduced-motion` | [ ] | |
| **Skip links**: "Skip to main content" present | [ ] | |
| **Dragging alternatives**: Non-drag option exists (WCAG 2.5.7) | [ ] | |
| **Consistent help**: Help is placed consistently (WCAG 3.2.6) | [ ] | |

### 6. Performance UX

| Check | Pass | Notes |
|-------|------|-------|
| **LCP <2.5s**: Largest content loads quickly | [ ] | |
| **Responsive to input**: INP ≤200ms | [ ] | |
| **No layout shift**: CLS ≤0.1 | [ ] | |
| **Images optimized**: Responsive, lazy-loaded, compressed | [ ] | |
| **Skeleton matches content**: Loading placeholders reflect final layout | [ ] | |
| **Optimistic UI**: For high-confidence actions | [ ] | |

### 7. Platform Compliance

#### Web

| Check | Pass | Notes |
|-------|------|-------|
| **Semantic HTML**: `<button>`, `<nav>`, `<main>` used correctly | [ ] | |
| **320px viewport**: No horizontal scroll at mobile width | [ ] | |
| **Browser back/forward**: History state preserved | [ ] | |

#### iOS

| Check | Pass | Notes |
|-------|------|-------|
| **Safe areas respected**: Notch/Dynamic Island handled | [ ] | |
| **Dynamic Type supported**: Text scales with system setting | [ ] | |
| **Native patterns**: Tab bar, navigation bar as expected | [ ] | |

#### Android

| Check | Pass | Notes |
|-------|------|-------|
| **Material 3 patterns**: Consistent with platform | [ ] | |
| **Back gesture handled**: Predictive back supported | [ ] | |
| **Edge-to-edge layout**: System bars integrated | [ ] | |

### 8. Design System Alignment

| Check | Pass | Notes |
|-------|------|-------|
| **Tokens used**: Colors, spacing from design system | [ ] | |
| **Components reused**: No one-off implementations | [ ] | |
| **Variants correct**: Appropriate component variant selected | [ ] | |
| **No custom styling**: Overrides documented if necessary | [ ] | |

---

## Optional: AI/Automation Features

> Complete this section ONLY if the product includes AI/ML features.

### AI Transparency

| Check | Pass | Notes |
|-------|------|-------|
| **AI involvement disclosed**: User knows AI is involved | [ ] | |
| **Processing status shown**: AI thinking/generating visible | [ ] | |
| **Source attribution**: AI-generated content cited | [ ] | |
| **Confidence indicated**: Uncertainty communicated visually | [ ] | |
| **Limitations disclosed**: Known limitations documented | [ ] | |

### AI User Control

| Check | Pass | Notes |
|-------|------|-------|
| **Stop/cancel available**: User can interrupt AI | [ ] | |
| **Regenerate option**: User can request alternative | [ ] | |
| **Edit capability**: User can modify AI output | [ ] | |
| **Override possible**: Human decision > AI suggestion | [ ] | |
| **Disable option**: User can turn off AI features | [ ] | |
| **Feedback mechanism**: User can rate AI quality | [ ] | |

### AI Error Handling

| Check | Pass | Notes |
|-------|------|-------|
| **Failure graceful**: AI failure doesn't block workflow | [ ] | |
| **Fallback available**: Manual alternative exists | [ ] | |
| **Error explanation**: Why AI failed is communicated | [ ] | |
| **Retry easy**: User can easily retry failed AI operation | [ ] | |

---

## Review Summary

**Date**: _______________
**Reviewer**: _______________
**Product/Feature**: _______________

### Findings Summary

| Category | Pass | Fail | N/A | Priority Issues |
|----------|------|------|-----|-----------------|
| Interaction Design | /7 | | | |
| Information Architecture | /6 | | | |
| State Handling | /6 | | | |
| Form Design | /7 | | | |
| Accessibility | /8 | | | |
| Performance UX | /5 | | | |
| Platform Compliance | /3 | | | |
| Design System | /4 | | | |
| **AI/Automation** (if applicable) | /15 | | | |

### Top 3 Issues to Address

1. **[Issue]**: [Description] — Severity: Critical/Major/Minor
2. **[Issue]**: [Description] — Severity: Critical/Major/Minor
3. **[Issue]**: [Description] — Severity: Critical/Major/Minor

### Recommendations

[Prioritized action items]

---

## References (Primary Sources)

- WCAG 2.2 (W3C Recommendation, 12 Dec 2024): https://www.w3.org/TR/WCAG22/
- WAI-ARIA Authoring Practices Guide: https://www.w3.org/WAI/ARIA/apg/
- Core Web Vitals (LCP/INP/CLS thresholds): https://web.dev/vitals/
- Response time thresholds (0.1s / 1s / 10s): https://www.nngroup.com/articles/response-times-3-important-limits/
- `prefers-reduced-motion` (Media Queries Level 5): https://www.w3.org/TR/mediaqueries-5/#prefers-reduced-motion
