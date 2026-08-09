# Screen Reader Testing Protocol

Manual screen reader testing is essential because most experience-level and
assistive-technology-specific WCAG criteria cannot be verified by automation alone — see
[references/wcag-automation-matrix.md](wcag-automation-matrix.md) for the criterion-level
breakdown; do not treat any fixed percentage of "automatable" criteria as a standards-grade
figure. This guide covers VoiceOver, NVDA, and TalkBack testing workflows.

## Table of Contents

- [General Principles](#general-principles)
- [VoiceOver (macOS)](#voiceover-macos)
- [Setup](#setup)
- [Key Commands](#key-commands)
- [Testing Checklist](#testing-checklist)
- [VoiceOver (iOS)](#voiceover-ios)
- [Key Gestures](#key-gestures)
- [Testing Additions for iOS](#testing-additions-for-ios)
- [NVDA (Windows)](#nvda-windows)
- [Setup](#setup)
- [Key Commands](#key-commands)
- [Testing Checklist](#testing-checklist)
- [TalkBack (Android)](#talkback-android)
- [Setup](#setup)
- [Key Gestures](#key-gestures)
- [Testing Checklist](#testing-checklist)
- [What to Verify Across All Screen Readers](#what-to-verify-across-all-screen-readers)
- [Landmarks](#landmarks)
- [Dynamic Content](#dynamic-content)
- [Custom Widgets](#custom-widgets)
- [Forms](#forms)

## Recommended Testing Matrix (2026)

Minimum coverage for web and hybrid products:

| Screen Reader | OS | Browser | Priority |
|---------------|----|---------|----------|
| NVDA (latest) | Windows | Chrome or Firefox | Default for Windows web |
| JAWS (latest annual) | Windows | Chrome | Enterprise/government products |
| VoiceOver | macOS | Safari | Default for macOS/Apple targets |
| VoiceOver | iOS | Safari | Mobile Apple targets |
| TalkBack | Android | Chrome | Mobile Android targets |

Basis: [WebAIM Screen Reader User Survey #10](https://webaim.org/projects/screenreadersurvey10/)
(fielded Dec 2023–Jan 2024, published Feb 2024, 1,539 respondents — the latest published
edition as of 2026-07-11; Survey #11 was open in the field with results not yet published).
Desktop *primary* screen reader share: JAWS 41%, NVDA 38%, VoiceOver 8.2% (up from 5.5% in
2021). Desktop *commonly-used* share (respondents use 71.6% more than one): NVDA 65.6%, JAWS
60.5%, VoiceOver 43.9%. Mobile: VoiceOver 70.6%, TalkBack 34.6%. JAWS leads NVDA in North
America and Australia specifically; NVDA leads in Europe, Africa/Middle East, and Asia — do not
assume NVDA-only coverage is sufficient for a US-heavy or enterprise audience where JAWS remains
dominant. VoiceOver + Safari is the only reliably supported combination on Apple platforms.

**Tool notes (verify version-specific behavior before relying on it — these move fast):**
- NVDA 2026.1 upgrades the internals to 64-bit — expect installation size and add-on compatibility changes; verify your pinned version after this release.
- JAWS 2025 introduced FSCompanion (AI-assisted learning) and productivity improvements; no breaking changes to web testing behavior.
- TalkBack gesture shortcuts changed in Android 14+; verify on a device running Android 14 or later.

## General Principles

- Test critical user flows, not every page.
- Use the screen reader as a primary input method — no mouse, no visual confirmation.
- Record findings with the specific screen reader output (what was announced vs what was expected).
- Test with the browser/OS combination your users actually use.

## VoiceOver (macOS)

### Setup

- Enable: `System Settings → Accessibility → VoiceOver → On` or press `Cmd + F5`.
- Practice: complete the VoiceOver tutorial from System Settings first.
- Browser: Safari is the primary target; Chrome has VoiceOver support but Safari is authoritative.

### Key Commands

| Action | Keys |
|--------|------|
| Start/stop VoiceOver | `Cmd + F5` |
| Move to next item | `VO + Right Arrow` (VO = `Ctrl + Option`) |
| Move to previous item | `VO + Left Arrow` |
| Activate item | `VO + Space` |
| Read page from top | `VO + A` |
| Open rotor | `VO + U` |
| Navigate headings | Rotor → Headings, then `Up/Down Arrow` |
| Navigate landmarks | Rotor → Landmarks, then `Up/Down Arrow` |
| Navigate links | Rotor → Links, then `Up/Down Arrow` |
| Navigate form controls | Rotor → Form Controls, then `Up/Down Arrow` |
| Tab to next focusable | `Tab` |
| Interact with group | `VO + Shift + Down Arrow` |
| Stop interacting | `VO + Shift + Up Arrow` |

### Testing Checklist

- [ ] Page landmarks announced correctly (banner, navigation, main, contentinfo)
- [ ] Heading hierarchy navigable and logical (h1 → h2 → h3)
- [ ] All images have meaningful alt text (decorative images are hidden)
- [ ] Form fields have associated labels announced on focus
- [ ] Required fields indicated audibly
- [ ] Error messages announced when they appear
- [ ] Buttons and links have descriptive names (not "click here")
- [ ] Dynamic content updates announced via live regions
- [ ] Modal dialogs trap focus and announce title on open
- [ ] Modal close returns focus to trigger element
- [ ] Custom widgets (tabs, accordions, menus) follow ARIA APG patterns

## VoiceOver (iOS)

### Key Gestures

| Action | Gesture |
|--------|---------|
| Move to next item | Swipe right |
| Move to previous item | Swipe left |
| Activate item | Double tap |
| Scroll | Three-finger swipe |
| Open rotor | Two-finger twist |
| Navigate by rotor setting | Swipe up/down |
| Dismiss/go back | Two-finger scrub (Z gesture) |

### Testing Additions for iOS

- [ ] Touch targets are at least 44x44 points
- [ ] Swipe navigation order matches visual layout
- [ ] Custom gestures have accessible alternatives
- [ ] Notifications and alerts are announced

## NVDA (Windows)

### Setup

- Download from https://www.nvaccess.org/download/
- Default browser target: Chrome or Firefox (both well-supported).
- NVDA modifier key: `Insert` (or `Caps Lock` if configured).

### Key Commands

| Action | Keys |
|--------|------|
| Start NVDA | Run from Start Menu or shortcut |
| Stop speech | `Ctrl` |
| Read from cursor | `NVDA + Down Arrow` |
| Next heading | `H` |
| Previous heading | `Shift + H` |
| Next landmark | `D` |
| Previous landmark | `Shift + D` |
| Next form field | `F` |
| Next link | `K` |
| Next list | `L` |
| Elements list (like rotor) | `NVDA + F7` |
| Toggle browse/focus mode | `NVDA + Space` |
| Tab to next focusable | `Tab` |

### Testing Checklist

- [ ] Browse mode allows quick navigation by headings, landmarks, and links
- [ ] Focus mode activates correctly inside forms and interactive widgets
- [ ] All form fields announce labels and required state
- [ ] Error messages are associated with fields and announced
- [ ] Tables announce row/column headers during navigation
- [ ] Live regions announce dynamic content updates
- [ ] Modal dialogs announce correctly and trap focus
- [ ] Custom widgets are operable in both browse and focus modes

## TalkBack (Android)

### Setup

- Enable: `Settings → Accessibility → TalkBack → On`.
- Practice: complete the TalkBack tutorial from Settings.

### Key Gestures

| Action | Gesture |
|--------|---------|
| Move to next item | Swipe right |
| Move to previous item | Swipe left |
| Activate item | Double tap |
| Scroll | Two-finger swipe |
| Open local context menu | Swipe up then right |
| Open global context menu | Swipe down then right |
| Navigate by heading | Set granularity (swipe up/down), then swipe left/right |
| Back | Two-finger swipe down then left |

### Testing Checklist

- [ ] Content descriptions are meaningful for all interactive elements
- [ ] Touch targets are at least 48x48 dp
- [ ] Swipe navigation order is logical
- [ ] Custom views announce roles and states
- [ ] RecyclerView items are individually focusable
- [ ] Toast and Snackbar messages are announced
- [ ] Bottom sheets and dialogs are focusable and dismissible
- [ ] Dynamic list updates are announced

## What to Verify Across All Screen Readers

### Landmarks

All pages should have at minimum: banner (header), navigation, main content, and contentinfo (footer). Screen readers use these for quick navigation.

### Dynamic Content

Content that updates without a page reload must use ARIA live regions:
- `aria-live="polite"` for non-urgent updates (search results, status messages)
- `aria-live="assertive"` for urgent updates (error messages, time-sensitive alerts)
- Verify the update is announced without interrupting the user's current task (polite) or immediately (assertive)

### Custom Widgets

Any component that is not a native HTML element must follow the ARIA Authoring Practices Guide (APG):
- Correct `role` attribute
- Correct keyboard interaction pattern
- State changes announced (`aria-expanded`, `aria-selected`, `aria-checked`)
- See https://www.w3.org/WAI/ARIA/apg/patterns/

### Forms

- Labels announced on focus (not just visually adjacent)
- Required state communicated (`aria-required` or native `required`)
- Validation errors associated with fields (`aria-describedby` pointing to error message)
- Error summary reachable and announced
