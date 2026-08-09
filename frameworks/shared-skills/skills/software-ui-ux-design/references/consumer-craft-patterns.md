# Consumer Craft Patterns

How elite consumer products win on craft. This is the playbook that separates generic SaaS from products people actually love — Linear, Things, Duolingo, Notion, Arc, Instagram, Booking.com, Airbnb, Apple Photos.

Craft is not decoration. Every pattern below has a measurable effect on retention, conversion, or task completion when done well.

---

## Table of Contents

- [The Craft Bar](#the-craft-bar)
- [First-60-Seconds Onboarding](#first-60-seconds-onboarding)
- [Microcopy That Carries Voice](#microcopy-that-carries-voice)
- [Perceived Performance Craft](#perceived-performance-craft)
- [Empty, Loading, Error: The Three States That Decide Trust](#empty-loading-error-the-three-states-that-decide-trust)
- [Delight Moments](#delight-moments)
- [Conversion Craft](#conversion-craft)
- [Habit and Gamification Done Right](#habit-and-gamification-done-right)
- [Optical Polish](#optical-polish)
- [Sound and Haptics in UX](#sound-and-haptics-in-ux)
- [Anti-Patterns](#anti-patterns)
- [Specific Interaction Anti-Patterns](#specific-interaction-anti-patterns)
- [Frictionless Craft Patterns](#frictionless-craft-patterns)
- [Sources](#sources)

---

## The Craft Bar

A consumer-grade product hits all of these. Use as the screen-by-screen review checklist.

| Dimension | Pass | Fail |
|-----------|------|------|
| **Time to first value** | <60s for primary user | "Set up your workspace" wizard with 7 steps |
| **Empty state** | Models the populated state with one CTA | Grey illustration + "No items yet" |
| **Loading state** | Skeleton matches the populated layout | Centered spinner |
| **Error recovery** | Names the error, offers a specific next step in user voice | "Something went wrong" + reload |
| **Microcopy** | One distinct voice; no system-speak; numbers are humanised | Form labels generated from field names |
| **Optical alignment** | Icons, numbers, capitals optically balanced | Pixel-grid alignment that *measures* equal but reads off |
| **Motion** | Functional (origin → destination, hierarchy) | Decorative bounces on every state change |
| **Touch feedback** | Every interactive surface has press + success states | Buttons that "just work" silently |
| **Ergonomics** | Primary actions in thumb arc on phone | Top-right primary on 6.5" device |
| **First-run delight** | One non-functional moment that makes a user smile | None |
| **Numbers** | Currency, units, durations formatted to locale and rounded for scan | "1,234.567890123" or "12345" no separator |
| **Recovery without restart** | Back, undo, edit-without-redo for any decision | "Are you sure?" gating every action |

If a screen fails three or more rows, it's not consumer-grade yet, regardless of how the metrics look — you're shipping debt.

---

## First-60-Seconds Onboarding

The decision to use the product is usually made before signup completes. Spending 30 seconds *teaching* the user is a choice to lose them.

### Patterns that work

1. **Show, don't gate.** Let the user *see* the product working before asking for an account. Linear, Arc, and Notion all let you click through canonical content without auth.
2. **Borrow time-to-value with a sample workspace.** Pre-populate one demo project/note/playlist on first run. The user sees the populated state, not the empty one. Notion's templates, Things' sample To-Dos, Duolingo's first lesson are this pattern.
3. **One question, one answer.** When you must ask the user something (goal, role, language), ask one thing per screen with large tap targets and no skip-back-skip-forward. Replace 5-question setup with 1-question + smart defaults.
4. **Defer permissions to the moment of need.** Notifications, location, photos — never request on first launch. Request inline, with a custom pre-prompt explaining *why now*. iOS's denial is permanent; getting a "no" pre-needs is a permanent loss.
5. **Make the first action small and successful.** The first thing the user does should succeed visibly. Duolingo's first lesson is unmissable. Photos' first-import previews work without setup. Strava's first run logs without configuration.
6. **No empty home screen ever.** If the user lands on an empty home screen on day one, you've wasted the visit. Pre-populate, demo-fill, or jump straight to the creation flow.

### Numbers to hit

- Time to first meaningful action: <60s (B2C), <120s (productivity)
- Steps before first value: ≤2
- Permissions on first run: 0
- Forms: 0 on first run if possible; ≤1 short form if not

### Onboarding tour anti-pattern

Carousel tours and lottie-illustrated "Welcome → Create → Share → Done" sequences are a known anti-pattern. Users skip them. The data is unambiguous (NN/g, Appcues benchmarks). Replace tours with *progressive in-app coaching*: contextual tooltips that appear at the moment a feature is about to be useful.

---

## Microcopy That Carries Voice

Microcopy is the difference between a product that feels human and one that feels like SAP. It is design, not copywriting.

### Rules

- **One voice across the surface.** If the success toast says "Nice — saved" and the error says "An unexpected error occurred (E502)", the product has split-personality syndrome. Pick a register and hold it.
- **Write to a person, not a permission group.** "Allow notifications" is a system prompt, not a value statement. "Get a ping when [name] replies" is.
- **Never use system error codes in user-facing copy.** Map every backend error class to a human sentence. "Network unavailable — we'll retry when you reconnect" beats "ECONNRESET".
- **Numbers are content.** "2 hours, 14 minutes" beats "134 min". "$24" beats "$24.00". "Last Tuesday" beats "Apr 28". "3 friends are here too" beats "3 connected".
- **Confirmation copy = the verb of what just happened.** "Sent", "Added", "Saved", "Done" — not "Operation completed successfully."
- **Empty states speak to motivation.** "Save your first note — they sync everywhere" not "No notes yet."
- **Buttons are verbs, never nouns.** "Save changes" / "Delete photo" / "Add friend" — not "OK" / "Submit" / "Done."
- **Localise tone.** Formal vs casual register varies by market. Do not ship a single English voice translated literally.

### Voice exemplars to study

- **Mailchimp** — friendly, slightly absurd, never patronising. The Voice & Tone guide is the canonical reference.
- **Slack** — terse, kind, professional. Empty states are quietly motivating.
- **Linear** — minimal, technical, high-confidence. No exclamation marks.
- **Duolingo** — expressive, characterful, uses owl personality without being childish.
- **Stripe** — precise, calm, technical. Documentation reads like microcopy.

---

## Perceived Performance Craft

Real performance is measured. Perceived performance is *designed*. Both matter.

### Patterns

1. **Skeleton screens that match the populated layout exactly.** Same heights, same spacing, same number of rows. The user's eye should not jump when content arrives. Generic centered spinners feel slower than skeletons even when actual load is faster.
2. **Optimistic UI for any user-initiated mutation.** Like, follow, archive, complete-todo, send-message — render the result immediately, reconcile in the background, undo on failure. The user feels instant; the network has 5 seconds to catch up.
3. **Stale-while-revalidate in the UI layer.** Show the last cached state; refresh in the background; cross-fade in changes. Used by Twitter, Apollo, Linear, Reeder.
4. **Predictive prefetch on hover/long-press.** When the user expresses intent (hover on web, long-press on mobile), prefetch the destination. Most clicks are signalled 100–500ms before they happen.
5. **Inline progress for long operations.** Imports, encodes, uploads should show real progress and a meaningful sub-status ("Compressing video", "Uploading 3 of 12") — not an indeterminate bar.
6. **Background completion + arrival notification.** For >10s operations, let the user leave; ping when done. iOS Background Tasks, web Service Workers + push.
7. **Animation = bridge.** A 250ms transition between two states is shorter than the perceived gap of teleporting. Used right, motion *reduces* felt latency.

### What kills perceived speed

- centered spinners with no indication of what's loading
- white flash between routes (use cross-fade or view transition)
- jumping content as data arrives (reserve space; size everything)
- modal blocking dialogs for any operation that *could* run in background
- "Please wait" / "Loading..." text — never carry information

---

## Empty, Loading, Error: The Three States That Decide Trust

These three states are where most products betray their lack of craft. Elite consumer products treat them as primary surfaces.

### Empty state

The empty state is the *first impression of every feature*. It must:
- model what the populated state looks like (preview the value)
- offer one specific, verb-driven CTA
- not use generic illustrations that have nothing to do with the data shape
- speak to motivation, not state ("Capture your first idea — they sync to all your devices" not "No notes")
- offer a sample/template path for users who don't have content yet

### Loading state

- skeleton, not spinner, when the layout is known
- match the actual layout's heights and column structure
- **don't show a skeleton if the response will arrive in <100ms** — the flash is worse than a brief delay
- for unknown-duration loads, show progress with substatus
- never combine loading state with disabled UI without explaining why

### Error state

The error state is where trust is built or destroyed. It must:
- name the actual error category in user words (not status codes)
- offer a specific recovery action ("Retry", "Reconnect to Wi-Fi", "Use offline mode")
- preserve the user's input and partial work
- never use "Something went wrong" — that's the engineering equivalent of "?"
- log the technical cause in observability without surfacing it
- distinguish *transient* (retry helps) from *permanent* (retry won't help) errors and word the recovery accordingly

---

## Delight Moments

Delight is the non-functional moment that exceeds expectation. One per onboarding, one per main loop, used surgically.

### Patterns

- **First-success celebration.** First message sent, first run logged, first photo imported. A 600ms haptic + visual flourish. Strava confetti, Apple Photos memory cards, Slack hi-five emoji.
- **Easter eggs at invisible thresholds.** 100th run, 1000th note, anniversary. Not visible to new users; rewards loyalty.
- **Anticipated character.** Notion's emoji picker for any heading. Linear's keyboard shortcut palette. Duolingo's owl. The character does *not* explain the product; it lives alongside it.
- **Weather/time-of-day awareness.** Subtle theme shifts at sunset, weather-aware home screen, contextual greetings. Apple Weather, Things, Streaks all do this.
- **Hidden but discoverable interactions.** Long-press to peek, drag to scrub, swipe with momentum. Reward exploration without requiring it.
- **Personalised milestones.** "You've journaled 30 days in a row." Not a leaderboard, not a comparison — a personal recognition.

### Rules of delight

1. Delight after success, never before. Celebrating before completion is patronising.
2. Delight should be skippable. If a celebration steals focus from the next action, redesign.
3. One delight per flow, max. More than one and the moments cancel each other out.
4. Reduce-Motion users see a static alternative. Don't punish accessibility settings.
5. Cultural calibration matters. American confetti reads as gauche in Japan; Japanese subtle bow reads as cold in the US.

---

## Conversion Craft

For commerce, signup, and any flow where the user must complete N steps to give you money, every screen is a conversion surface.

### The Booking.com / Airbnb / Stripe playbook

1. **Single-column forms, top-down.** Users complete single-column forms 15–30% faster than multi-column. Multi-column survives only for narrow paired fields (city + zip, exp month + year).
2. **Field labels above inputs, never inside.** Floating labels save space but kill usability for older users, screen readers, and re-edit flows. Label above is canonical.
3. **Inline validation on blur, not on every keystroke.** Validate the moment the field loses focus. Real-time character validation feels accusatory.
4. **Make optional fields actually optional and label them.** Required is the default; mark optional explicitly. Reduce required fields ruthlessly — every field is a conversion tax.
5. **Show what you'll do with sensitive data inline.** "We use your email to send your booking confirmation" beneath the email field. Trust delta is measurable.
6. **Address autocomplete, never type-it-yourself.** Google Places, Loqate, Stripe's address element. Address typing has the worst error rates in any flow.
7. **One primary CTA per screen, sticky on mobile.** The CTA should be visible without scrolling. On mobile, a sticky bottom bar that stays in thumb arc.
8. **Show progress, but only if it's earned.** Step indicators ("Step 2 of 5") help when the user trusts the flow length; they hurt when the count is high.
9. **Express checkout above the form.** Apple Pay, Google Pay, Shop Pay, Link, PayPal — let returning users skip the form entirely. Express paths convert 2–5× the form path.
10. **Defer account creation to after first value.** "Create account to save" beats "Create account to start" by a wide margin. Strava, Notion, Figma all use this.

### What Baymard's research shows kills conversion

- guest checkout buried below "Sign in" (50% of leading sites get this wrong)
- forced account creation before checkout
- unclear delivery cost / total / tax until last step
- missing trust signals near payment fields (security badges, return policy, contact)
- generic CTAs ("Continue", "Submit") instead of value-carrying CTAs ("Place order — $42.18")

---

## Habit and Gamification Done Right

Habit-forming consumer apps rely on patterns that are easy to do badly. The line between a delightful streak and a manipulative dark pattern is thin.

### What works

- **Progress bars toward meaningful milestones.** Duolingo's lesson XP, Strava's monthly distance, Apple Health rings. Always *self-comparison*, not peer-comparison.
- **Streaks with grace.** Streaks build habit when missing one day doesn't reset everything to zero. Duolingo's "streak freeze", Apple Fitness's mercy day. Streaks without grace cause anxiety, then churn.
- **Variable reward only where the variance is intrinsic.** Match results in dating apps, news feed updates, social notifications — variance is real. Manufactured variance (fake "new!" badges, false "limited time" timers) is a dark pattern.
- **Surfaceable progress, not forced.** Show the streak; don't gate features behind it. Show the level; don't make level the primary status.
- **Loss aversion only for user-owned things.** Reminders that the *user* asked for ("Your meditation reminder is at 7pm"), not loss-aversion designed by the company ("You'll lose your streak!").

### What doesn't work / dark patterns to refuse

- countdown timers with no real urgency
- fake scarcity ("Only 2 left at this price!")
- ranking against friends without consent
- public-by-default activity feeds
- streaks that double as guilt tools
- variable reward on engagement metrics the user has no agency over
- "You'll lose 3 days of progress" as a re-engagement notification

DSA Article 25 covers many of these for EU users — see `wcag-accessibility.md`.

---

## Optical Polish

The difference between "merely fine" and "obviously crafted" is mostly optical adjustment, not measurement.

### Optical alignment

- **Icons in lists**: align by *optical centre*, not bounding box. A circular icon and a square icon at the same y need different y values to *look* aligned.
- **Numbers in tables**: right-align (or use `font-variant-numeric: tabular-nums`) so columns scan. Left-align for reading prose.
- **Capital-only labels**: add tracking (letter-spacing) — uppercase reads tighter than mixed case. Apple uses 0.5–1pt tracking on all-caps eyebrow labels.
- **Buttons of different shapes adjacent**: align to baseline of label, not centre of pill. A capsule and a rounded-rect button next to each other need optical, not pixel, alignment.
- **Asymmetric padding around glyphs**: an "X" close button needs more right-pad than left because the glyph is heavier on the left.

### Density tuning

- Comfortable, default, compact — design three densities for any list-heavy interface (mail, music, files). Default for most users; compact for power users.
- Touch targets are 44pt iOS / 48dp Android *minimum*. For primary actions, 56–64pt feels confident.
- Line height 1.4–1.6 for body, 1.1–1.25 for headlines. Lower for editorial, higher for UI text.

### Numbers and units

- Round to scan length: `$1,247` not `$1,247.00` for scrollable lists. Show full precision on detail.
- Use locale-correct separators (`1,234.56` US vs `1.234,56` EU).
- Currency symbols before in en-US, after in many EU locales — let `Intl.NumberFormat` decide, don't hardcode.
- Durations: `2h 14m` for timers; `2 hours ago` for past events; `Yesterday at 3pm` for recent.
- "Just now" / "2 min ago" / "3 hours ago" / "Yesterday" / "Last Tuesday" / "Apr 28" — relative until a week, then absolute.

---

## Sound and Haptics in UX

Sound and haptics carry attention, confirm action, and add craft signal — but most products under-use both.

### When haptics help

- confirmation of a discrete action: send, save, complete, like, swipe-confirm
- error or warning: a single firm thump
- progress milestones during a long press or scrub
- arrival at a snap point (date wheel, value picker)

### When haptics hurt

- on every tap of every button (fatiguing)
- with no audible/visual companion (interpretation ambiguous)
- without honouring the system "Haptic Touch" setting (iOS) or "Vibration" toggle (Android)
- triggered by state changes the user didn't initiate

### Sound design

Most apps should ship silent by default and only sound when explicitly toggled on. Exceptions:

- alarms and notifications (system handles)
- creative tools where sound is part of the medium (camera, voice memo)
- accessibility — sounds as a non-visual confirmation channel

When sound is on, three rules: short (<150ms), tonally neutral (no major-key chime), composable (multiple sounds played close together must not feel like a chord).

---

## Anti-Patterns

- **Generic loading spinners** when the layout is known. Skeleton.
- **"Something went wrong"** errors. Always name the cause and offer recovery.
- **Empty states with cartoon illustrations and no CTA**. The empty state is your sales pitch; treat it as one.
- **Onboarding carousels** with 4 lottie illustrations. Skipped by everyone; replace with first-action UI.
- **Permissions wall on first launch**. Defer; explain in-context.
- **Form labels inside fields** that disappear on focus. Labels above, always.
- **Required asterisks on every field** when the optional fields could just be marked "Optional". Less visual noise, better scan.
- **CTA copy as nouns or system verbs**: "OK", "Submit", "Done", "Continue". Verbs that name the action.
- **Confetti on every save**. Use surgically; once everywhere = nowhere.
- **Decorative motion on every state change**. Spring-bouncing into existence is not joy; it's noise.
- **Robot voice in error and confirmation copy**. "Operation completed successfully" — say what happened in user words.
- **Streaks designed to punish rather than reward**. Grace days, freezes, mercy modes are non-negotiable for habit features.
- **Hidden critical functions behind long-press only.** Long-press is a power-user accelerator; never the *only* way to reach a function.
- **Dense info architecture without progressive disclosure**. Settings screens with 47 toggles need grouping, search, and defaults.
- **Modals for things that should be inline edits.** Editing a single field rarely needs a modal.

---

## Specific Interaction Anti-Patterns

Each entry: the failure mode, then the fix. No exceptions, no "it depends."

**Infinite scroll without scroll restoration.** Back-button loses position; user is dropped at the top of a feed they scrolled 200 items into. Fix: store `firstVisibleItemId` + pixel offset in `history.state` on scroll; restore via `IntersectionObserver` on mount. Works in both SPA and SSR contexts.

**Modal stacks (sheet over sheet over modal).** Focus management collapses — `aria-modal` on the second sheet traps focus but the first sheet is still mounted. `Esc` behaviour is ambiguous. On mobile the third sheet is offscreen. Fix: architectural ban on stacking. A second action either navigates to a new route, replaces the current sheet, or opens inline. Never stacks.

**Autocomplete that fights typing.** Late-arriving XHR responses overwrite the user's current input or reset cursor position to end. Fix: suggestions list updates freely; the input value is *never* touched by suggestion logic; cancel in-flight requests on each keystroke with `AbortController`; debounce ≥150ms before firing.

**Sticky headers consuming the hero.** Sticky nav + sticky sub-nav + sticky table header = 40%+ of viewport on a phone. Fix: collapse to icon-only or hide sub-nav on scroll-down; reveal on scroll-up (hide-on-scroll pattern). Aggregate sticky region ≤56px on mobile.

**Password fields that block paste.** Breaks password managers, increases typos, increases failure rate. WCAG 3.3.8 explicitly requires paste support for authentication fields. Fix: never call `event.preventDefault()` on `paste` events in password inputs. Masking is fine; blocking paste is not.

**Date pickers that fail keyboard input.** Wheel-only on mobile and click-only on desktop exclude touch-typists, AT users, and anyone entering a date of birth from memory. Fix: `<input type="text">` as primary with real-time parsing; picker as augment only. Parse both `MM/DD/YYYY` and `DD/MM/YYYY` and pick by locale; display the interpreted date inline before commit.

**Toast positions blocking primary CTA.** Bottom-anchored toasts appear over a sticky checkout or compose button — user must wait or miss the action. Fix: audit the toast bounding box against every sticky region; offset toasts above sticky bars or switch to top-right on web, top-center on mobile.

**Search-as-you-type with no debounce.** Every keystroke fires a request; responses arrive out of order; results flicker. Fix: 150ms minimum debounce; cancel in-flight with `AbortController`; render the last *stable* result during typing (stale-while-debouncing). Never render intermediate race results.

**Disabled submit buttons with no explanation.** Users stare at a grey button with no path forward. Fix: enable the button; show validation errors only on submit attempt; move focus to the first failing field. The only exception is a confirmed-destructive second step where context is already clear.

**Loaders that block the whole screen.** Full-screen overlay prevents navigation, hides partial state, and punishes slow connections. Fix: scoped skeleton in the region being loaded. The rest of the screen stays interactive. For background operations, no blocking UI at all — just a subtle inline indicator.

**Error-as-toast for form validation.** Toast disappears in 4 seconds; user hasn't found the field yet. Fix: inline field error beneath the input, persistent until corrected, with focus moved to the first error on submit. Toast is for system-level, non-field errors only.

**Confirm dialog spam.** Every archive, delete, move, and dismiss gates on "Are you sure?" — training users to click through without reading. Fix: optimistic action + undo toast for anything reversible (delete email, archive, reorder). Reserve confirm modals for destructive, irreversible, rare operations: delete account, transfer funds, leave team.

---

## Frictionless Craft Patterns

### Undo vs confirm decision rule

Two-axis decision: **cost of recovery** × **frequency of action**.

| | Reversible | Irreversible |
|---|---|---|
| **Frequent** | Optimistic + undo toast | Soft-undo window |
| **Rare** | No friction needed | Confirm modal |

- **Optimistic + undo toast** — delete email, archive item, mark read, move card. Render result immediately; undo available for 5–10s. Linear, Gmail, Superhuman.
- **Soft-undo window** — actions that can be undone for a window but not forever. Gmail Send Undo (30s), iOS Recently Deleted album (30 days), Notion 3-second banner. Use when frequency is high but the action has non-trivial downstream effects.
- **Confirm modal** — delete account, transfer money above a threshold, leave a team, revoke an API key. Never more than two of these in any user session.
- **No friction** — reversible, rare. Reordering a list, changing a theme, toggling a preference. Just do it.

Examples in the wild: Gmail (undo send), Linear (undo move, no confirm on archive), Notion (undo banner, no modal), Stripe (test-mode actions need no confirm, live-mode destructive actions do).

### Paste and drag-drop affordances

These are the invisible table-stakes of a high-craft product. Most products ship none of them.

- **Paste-to-upload**: paste an image from clipboard into a rich-text field, comment box, or attachment area. Listen for `paste` event, check `event.clipboardData.items` for `image/*`. Show inline preview before commit.
- **Paste-as-link with metadata fetch**: paste a URL → fetch OG metadata server-side → render title + domain chip (Slack, Linear, Notion). Never render a raw URL when metadata is available.
- **Drag-drop with visual drop target**: highlight the drop zone with a border + background change — not just a cursor change. Cursor changes are invisible on touch. Drop zones that change only cursor are functionally invisible to 30%+ of users.
- **Drag-drop accessibility** (WCAG 2.5.7): every drag-and-drop interaction requires a keyboard/pointer alternative. Minimum viable: an upload button for files, cut/paste for reordering. Drag is an accelerator, never the only path.
- **Cross-app drag on iPad/desktop**: iOS uses `Transferable` (SwiftUI) / `UIDragInteraction` (UIKit); web uses `DataTransfer` API. Support both typed data (text, URL) and files in the same drop handler.

### Offline behavior model

Offline is not an edge case on mobile. Design it first.

- **Offline indicator**: subtle, non-blocking banner or connection-status dot. Not a modal. Not a full-screen wall. The user should be able to continue reading and queuing writes.
- **Optimistic mutations with sync queue**: writes succeed locally first; queue to sync on reconnect. Use a persistent queue (IndexedDB, SQLite on device) so a force-quit doesn't lose work.
- **Conflict resolution UI**: when two writes conflict (user edited on phone while offline; same record edited on desktop), surface both versions explicitly. Never silently overwrite. Show "Your version" vs "Server version" with a merge or pick option.
- **Read-only graceful degradation**: if sync isn't possible, cached reads stay available. Mark stale data with a timestamp ("Last synced 2h ago"), not an error state.
- Examples: Linear (full offline write support, syncs on reconnect with no visible seam), Notion (cache + sync, conflict shown as duplicate blocks), Apple Notes (transparent iCloud sync, last-write-wins with version history accessible).

### Keyboard shortcut discoverability

Shortcuts that exist but are never surfaced only help users who find them by accident. That is not a feature; it's a secret.

- **`?` modal as the canonical surface**: every keyboard shortcut in one place, grouped by context, searchable. Linear, GitHub, Slack, Figma all ship this. If you have ≥5 shortcuts and no `?` modal, you have undiscoverable debt.
- **Tooltip with keyboard hint on hover**: show the shortcut alongside the action label — `Delete  Bksp` or `Archive  E`. Copy Slack's and Linear's tooltip format exactly.
- **Command palette as the discoverable index**: every action in the app is invocable via the command palette (`⌘K` / `Ctrl+K`). The palette *is* the keyboard shortcut system for users who haven't memorised bindings yet.
- **Shortcuts in menu items**: native menus and context menus show the binding. Web context menus (custom) should do the same.
- **Anti-pattern**: shortcuts that exist but appear nowhere in the UI. They compound over time into an undocumented oral tradition that only tenured users know. Audit and surface or remove.

---

## Sources

- [Baymard Institute — Checkout UX research](https://baymard.com/research)
- [NN/g — UX research and writing](https://www.nngroup.com/articles/)
- [Mailchimp Voice & Tone](https://styleguide.mailchimp.com/voice-and-tone/)
- [Shopify Polaris — content guidelines](https://polaris.shopify.com/content)
- [Material Design 3 — motion guidelines](https://m3.material.io/styles/motion/overview)
- [Apple HIG — Inclusion and design quality](https://developer.apple.com/design/human-interface-guidelines/)
- [Stripe Design — patterns](https://stripe.com/blog/online-payment-methods)
- [Refactoring UI — Adam Wathan, Steve Schoger](https://www.refactoringui.com/)
- [Designing for Performance — Lara Hogan](https://designingforperformance.com/)
- [Hooked — Nir Eyal](https://www.nirandfar.com/hooked/)
- [Continuous Discovery Habits — Teresa Torres](https://www.producttalk.org/)
