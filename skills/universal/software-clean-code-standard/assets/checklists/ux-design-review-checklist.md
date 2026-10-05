# UX Design Review Checklist

**Feature/Page**: [Name]
**Reviewer**: [Name]
**Date**: YYYY-MM-DD

---

## Usability (Core)

### Nielsen Heuristics

- [ ] **Visibility of system status**: User knows what's happening
- [ ] **Match with real world**: Language users understand
- [ ] **User control**: Easy to undo, exit, cancel
- [ ] **Consistency**: Same patterns throughout
- [ ] **Error prevention**: Prevents mistakes before they happen
- [ ] **Recognition over recall**: Options visible, not memorized
- [ ] **Flexibility**: Shortcuts for experts
- [ ] **Aesthetic design**: Minimal, relevant information
- [ ] **Error recovery**: Clear error messages with solutions
- [ ] **Help**: Documentation accessible when needed

### Interaction Design

- [ ] Primary action is obvious
- [ ] Loading states shown (skeletons, not spinners)
- [ ] Empty states guide user to action
- [ ] Form validation inline (on blur, not every keystroke)
- [ ] Confirmation for destructive actions

---

## Accessibility (Core)

- [ ] Color contrast meets WCAG 2.2 AA (4.5:1 / 3:1)
- [ ] Touch targets meet WCAG 2.2 SC 2.5.8 target size (24x24 CSS px; exceptions apply) https://www.w3.org/TR/WCAG22/#target-size-minimum
- [ ] Touch targets follow platform guidance where relevant (e.g., 44x44 on iOS) https://developer.apple.com/design/human-interface-guidelines/
- [ ] Focus states visible
- [ ] Screen reader experience tested
- [ ] Reduced motion respected

---

## Responsiveness (Core)

- [ ] Works at 320px wide without horizontal scrolling for primary flows (WCAG reflow) https://www.w3.org/TR/WCAG22/#reflow
- [ ] Breakpoints are content-driven and documented (not framework defaults) [Inference]
- [ ] Touch-friendly on mobile (no hover-only interactions)
- [ ] Content readable without horizontal scroll

---

## Design System Alignment

- [ ] Uses approved components from design system
- [ ] Colors from design tokens
- [ ] Typography from design tokens
- [ ] Spacing from design tokens (4px/8px grid)

---

## Performance UX

- [ ] Perceived load time optimized (skeleton screens)
- [ ] Large images lazy loaded
- [ ] Optimistic UI for user actions
- [ ] No layout shifts during load

---

## Optional: AI/Automation Section

> Include only for AI-powered UI features.

- [ ] AI processing status visible (tool calls, streaming)
- [ ] User can stop, undo, retry AI actions
- [ ] Confidence cues for uncertain AI outputs
- [ ] Citations/sources provided where applicable
- [ ] Graceful fallback when AI unavailable
