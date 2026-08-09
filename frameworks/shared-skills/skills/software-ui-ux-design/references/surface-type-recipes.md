# Surface-Type Recipes

Craft patterns for elite consumer product UX. Audience: senior designers and engineers at Linear-tier product companies. Terse, opinionated, specific.

---

## Table of Contents

- [1. Data Tables (1k–100k rows)](#1-data-tables-1k100k-rows)
- [2. Command Palette (Cmd-K)](#2-command-palette-cmd-k)
- [3. Settings Pages](#3-settings-pages)
- [4. Search Experiences](#4-search-experiences)
- [5. Notifications / Inbox](#5-notifications--inbox)
- [6. Pricing Pages](#6-pricing-pages)
- [7. Paywalls and Subscriptions](#7-paywalls-and-subscriptions)
- [8. Comparison Tables](#8-comparison-tables)
- [9. Comments and Threads](#9-comments-and-threads)
- [10. Forms](#10-forms)
- [11. Onboarding](#11-onboarding)
- [12. Modals and Dialogs](#12-modals-and-dialogs)
- [Cross-Cutting Notes](#cross-cutting-notes)

---

## 1. Data Tables (1k–100k rows)

Single-purpose surface for structured data manipulation at scale.

**Required states:** empty (zero data, not zero results), loading (skeleton rows), partial-loading (streamed rows arriving), populated, error (fetch failed), no-results (filtered to zero), offline-cached (stale banner, data still readable), permission-denied (row-level or table-level).

**Key craft moves:**

1. **Virtualize from row 1.** Don't virtualize "after 200 rows." Overscan 3–5 rows. On scroll restoration, store pixel offset + first-visible-index; restore both on navigation back.
2. **Column pinning is user-configured, not designer-configured.** Allow pinning left/right via column header context menu. Pinned columns get a subtle shadow separator, not a border.
3. **Sticky bulk-action bar appears on first checkbox select**, anchors to the bottom of the viewport (not top), includes count, primary action, and dismiss. Disappears on deselect-all. Linear does this correctly.
4. **Density toggle** (compact / default / comfortable) is a user preference, persisted to profile. Default is almost never comfortable—start at default.
5. **Sort + filter chips on the table header bar**—not a sidebar. Sidebars hide state. Each active filter gets a removable chip. Complex filters (grouping, advanced predicates) open a filter builder in a sheet, but the active state surfaces as chips.
6. **Row expansion** renders inline below the row, not in a drawer. Drawer kills context. Expansion height is bounded with a "show more" if content exceeds ~300px.
7. **Col show/hide** via a Columns button that opens a popover checklist. Column order is drag-reorderable in the same popover.
8. **Copy support:** Cmd+C on selected cells copies as TSV. Cmd+Shift+C copies as CSV. Don't fight the user's expectation of spreadsheet behavior.
9. **Keyboard navigation:** arrow keys move cell focus; Enter opens row detail; Space toggles row selection; Tab cycles editable cells. Selection follows focus unless Shift is held.
10. **Optimistic inline editing:** click a cell, edit in place, save on blur. Revert indicator (undo icon) persists for 5s.

**Anti-patterns:**

- **Pagination instead of virtual scroll.** Breaks context, hides data, and forces unnecessary decisions. Acceptable only for exports.
- **Filter sidebar that collapses.** State that hides is state that gets forgotten. Chips are always visible.
- **Checkbox column always visible.** Show it on row hover or keyboard focus, not always. Permanent checkboxes read as "please select things."
- **Re-fetching on tab return.** If data is <5 min stale, serve cache. Forced refreshes mid-task break flow.
- **Bulk action as top toolbar item.** Far from the data and from thumbs on touch.
- **Column resize by px only.** Support fit-to-content double-click on resize handle.

**Elite examples:** Linear (issue list), Airtable (grid view), Retool (table component).

---

## 2. Command Palette (Cmd-K)

Global, keyboard-first action surface that replaces navigation for power users.

**Required states:** open-empty (recent commands or suggestions), loading (async search), populated (ranked results), no-results (helpful fallback action), closed.

**Key craft moves:**

1. **Focus the input on open with no delay.** A 16ms animation delay before focus is noticeable and wrong.
2. **Fuzzy ranking that respects acronyms.** "gc" should match "Git Commit" before "Grace Callaghan." Acronym matching beats substring matching. Penalize stale results.
3. **Recency weighting.** Commands run in this session rank above globally popular commands. Users repeat themselves.
4. **Group headers** (Navigation / Actions / Recent / Settings) with a separator line, not a box. Max 3 visible groups before scroll.
5. **Keyboard nav:** arrow keys move selection, Enter executes, Esc closes and returns focus to origin element (not body).
6. **Action-as-result vs nav-as-result are visually distinct.** Actions get a verb label (Create issue, Archive, Assign to me). Navigation gets a breadcrumb path (Settings → Billing). Don't mix without visual distinction.
7. **Nested palettes** for multi-step commands (Assign to → [person picker]). Show breadcrumb trail in header.
8. **No-results state** offers a fallback: "Search docs for X" or "Create new item named X." Never a dead end.
9. **Keyboard shortcut hints** shown right-aligned on result rows. Only show top 2–3 most useful shortcuts—don't annotate everything.

**Anti-patterns:**

- **Input delay before focus.** Typing before focus registers swallows characters silently.
- **Search-only, no actions.** The palette should execute, not just navigate.
- **Stale recent commands.** Commands from >7 days ago shouldn't rank higher than contextually relevant current actions.
- **Modal-style backdrop.** Command palettes are non-modal. Dim the background slightly but don't block interaction.
- **No Esc-to-close.** Non-negotiable. Every keystroke layer must have an escape hatch.

**Elite examples:** Linear (Cmd-K), Raycast (primary surface), Vercel dashboard (Cmd-K).

---

## 3. Settings Pages

Organized preference and configuration surface. Low frequency, high consequence.

**Required states:** loading (skeleton sections), populated, saving (inline per-section spinner, not page-level), saved (brief inline confirmation), error (per-field or per-section), permission-denied (section visible but locked with upgrade prompt or role requirement).

**Key craft moves:**

1. **Search within settings** with instant filter that highlights matching sections and fields. Notion and Linear both do this. No search = users file support tickets.
2. **Group by frequency of change**, not by implementation domain. Account, Notifications, and Appearance belong at the top. API keys and Danger Zone belong at the bottom.
3. **Autosave per toggle/select.** Save button is appropriate only for text fields and multi-field forms. Don't mix paradigms within a section—all autosave or all explicit save.
4. **Saved confirmation** is a transient inline indicator next to the field (a checkmark that fades after 2s), not a toast. Toasts for settings changes are noise.
5. **Destructive action zone** ("Delete account," "Remove all data") is at the page bottom, visually separated (border or background tint), with red text labels and a confirmation dialog that requires typing a confirmation string—not just clicking OK.
6. **Deep-link section anchors** (`/settings#notifications`). Every section has an `id`. Power users and support teams share links to specific settings.
7. **Density:** settings pages should be comfortable density. Users are reading and deciding, not scanning.

**Anti-patterns:**

- **Page-level Save button.** Users change one toggle and now must scroll to find Save. Regressive.
- **Settings as modal.** Settings have enough surface area to warrant their own route.
- **No confirmation for destructive actions.** One-click delete is never acceptable for irreversible actions.
- **Hiding advanced settings behind "Advanced" collapse.** Better: show advanced settings in context with a subtle label. Accordion-hidden settings get forgotten.
- **No visual feedback on autosave.** Users retry saves unnecessarily without feedback.

**Elite examples:** Linear (settings), Vercel (project settings), Stripe (developer settings).

---

## 4. Search Experiences

Real-time retrieval with autocomplete, scoping, and graceful empty states.

**Required states:** empty-query (recent/suggested), loading (debounced, skeleton or spinner), populated (results with highlights), no-results (with suggestion), error (backend failure, retry option), offline (cached results with banner).

**Key craft moves:**

1. **Debounce floor is 150ms**, not 300ms. Users on fast connections at 300ms perceive lag. On slow connections, cancel in-flight requests on new keystrokes.
2. **Autocomplete suggestions don't fight typing.** Render suggestions in a dropdown, never inline-completing text that the user then must delete. Inline completion (ghost text) is acceptable only if Tab accepts and any other key dismisses.
3. **Recent searches** shown on focus with empty query. Max 5. Each has an × to remove. Clicking one populates the input and triggers search immediately.
4. **Scopes** (All / Issues / Docs / People) as tabs or chip filters above results. Default to All. Persist last-used scope per user.
5. **No-results state** includes: spelling suggestion if detectable, scope-widening suggestion ("Search in all projects"), and a create-new shortcut where applicable.
6. **Result highlighting** bolds matched substrings. Match is case-insensitive; highlight rendering is not. Don't highlight stop words.
7. **Empty-query state ≠ no-results state.** Empty query shows recent and trending. No-results shows suggestions. They're different affordances for different situations.
8. **Keyboard control:** arrow keys navigate results, Enter opens, Esc clears to recent then closes.

**Anti-patterns:**

- **Search on submit only.** If users must press Enter to trigger search, real-time autocomplete is a lie.
- **Paginated search results.** Infinite scroll or load-more, not pagination with page numbers.
- **Generic "No results found."** Always add the query and suggest an action.
- **Scope that resets per search.** Scope is a filter preference, not a per-query setting.

**Elite examples:** Notion (quick find), GitHub (global search), Raycast (primary search).

---

## 5. Notifications / Inbox

Signal surface for updates requiring attention or awareness.

**Required states:** empty-inbox (zero unread—celebrate it), loading (skeleton rows), populated-unread, populated-read, no-results (filtered to zero), permission-denied (notification type disabled at org level).

**Key craft moves:**

1. **Mark-all-read** is a single action always accessible, never buried. Keyboard shortcut required.
2. **Grouping rules** by thread (not by time). Consecutive notifications from the same thread collapse into one row with a count badge. Expand to see thread history inline.
3. **Unread state** is a filled dot or bold title—not a blue background. Background tints hurt scannability at volume.
4. **Channel preferences** (email, push, in-app, Slack) configurable per notification type, not globally. Per-type granularity is table stakes for power users.
5. **Badge philosophy:** badge count = actionable unread only. Informational updates don't count toward the badge. Users learn to ignore badges that lie.
6. **Ephemeral toast** for non-critical, time-bounded events (file saved, link copied). **Persistent inbox** for events requiring action (assigned, mentioned, due, requires approval). Don't conflate.
7. **Snooze** (resurface at time X) and **archive** (dismiss permanently) are distinct. Archive ≠ mark read.
8. **Notification timestamp** in relative time <24h, absolute date >24h. Never "3 hours ago" for something from last Tuesday.

**Anti-patterns:**

- **Badge count includes read notifications.** Users stop trusting the badge.
- **Toast for every event.** Toast should be rare, not a notification system replacement.
- **No grouping.** 12 comment notifications from one issue is UX violence.
- **Global notification toggle only.** "Turn off all notifications" is not granular enough.
- **Notification list as only entry point.** Deep link every notification to its source content.

**Elite examples:** Linear (notification inbox), GitHub (inbox with grouping), Superhuman (keyboard-driven inbox).

---

## 6. Pricing Pages

Decision surface for plan selection. Conversion-critical, zero tolerance for confusion.

**Required states:** loaded, loading (skeleton keeps layout stable), annual/monthly toggle, mobile layout.

**Key craft moves:**

1. **Highlight one plan** (typically Pro or Growth) with an elevated card and "Most popular" label. Don't highlight your most expensive plan—users smell the manipulation.
2. **Feature row alignment** is exact. Every plan column must answer the same features in the same row. Missing = No. Ambiguous = tooltip with concrete explanation.
3. **Monthly/annual toggle** with annual savings prominently shown (e.g., "Save 20%"). Default to annual if conversion data supports it; default to monthly if not tested.
4. **FAQ accordion** directly below the plan grid. Address: free trial terms, seat definitions, overage billing, cancellation, data portability. Pre-empt the support ticket.
5. **Mobile collapse:** on mobile, show one plan at a time with a swipe carousel or tab switcher. Don't horizontally compress three columns.
6. **Comparison-by-feature view** (toggle from plan-first view) for users who want to evaluate specific capabilities. Stripe Radar pricing does this well.
7. **CTA copy is specific:** "Start free trial" > "Get started." "Upgrade to Pro" > "Upgrade." Match the action to the user's state (new vs existing).

**Anti-patterns:**

- **"Contact sales" as the only CTA for Enterprise.** Fine for enterprise tier; not acceptable if it's also applied to mid-tier plans to extract leads.
- **Feature parity hidden in footnotes.** If a feature is limited (e.g., "Up to 5 seats"), show it inline, not in a * footnote at page bottom.
- **No pricing shown.** "Contact sales" for all tiers signals pricing embarrassment. Quote a range.
- **Vague feature names.** "Advanced analytics" means nothing. "Funnel reports + cohort analysis" means something.

**Elite examples:** Linear (pricing), Vercel (pricing), Loom (pricing with feature matrix).

---

## 7. Paywalls and Subscriptions

Conversion surface at the moment of value friction.

**Required states:** soft-gate (preview with blur/truncation), hard-gate (content fully hidden), trial active (days remaining), trial expired, subscribed, error (payment failed), restore-purchase (mobile).

**Key craft moves:**

1. **Soft gate before hard gate.** Show a preview of the locked content (blurred rows, truncated list) so the user understands what they're buying. Hard gates convert worse and build resentment.
2. **Value preview must be honest.** Blur 3 real rows, not 3 fake rows. Users remember if the preview lied.
3. **Trial-to-paid conversion:** show a countdown starting at day 5 of 7, not day 1. Day-1 urgency is manipulative. Day-5 urgency is useful.
4. **Restore purchase** (mobile) is always accessible from the paywall. App Store reviewers require it; users expect it.
5. **Downgrade path** is clear, non-punitive, and synchronous. Don't bury it. Don't require a call. Show what the user will lose, confirm once, execute immediately. Superhuman's cancel flow is the benchmark.
6. **Cancel without dark patterns.** One confirmation step. No "are you sure you want to lose all your data?" No countdown timer on the cancel button. No 5-step "tell us why" survey before allowing cancel.
7. **Post-purchase celebration** is a single, brief moment (confetti + "You're on Pro") then gets out of the way. Don't make it a modal the user must dismiss.

**Anti-patterns:**

- **Hard gate with no preview.** User doesn't know if the feature is worth paying for.
- **Downgrade requiring email to support.** Automatic churn driver.
- **Roach motel:** easy to subscribe, impossible to cancel. Dark pattern that generates chargebacks and one-star reviews.
- **Trial countdown shown from day 1.** Trains users to ignore the counter.
- **Post-cancel survey before cancel executes.** Cancel must execute before survey; survey is optional and post-confirmation.

**Elite examples:** Notion (soft gates with preview), Linear (trial-to-paid), Superhuman (cancel flow).

---

## 8. Comparison Tables

Side-by-side feature evaluation for purchase decisions.

**Required states:** loaded, loading (skeleton with column placeholders), mobile-collapsed.

**Key craft moves:**

1. **Feature alignment is absolute.** Each row is one feature, evaluated consistently across all columns. If a feature doesn't apply to a tier, say "—" not leave blank.
2. **"Better" highlight is subtle.** A filled circle vs empty circle communicates inclusion. A green check vs red X introduces negative connotation for excluded features. Use inclusion/exclusion language, not pass/fail.
3. **Mobile horizontal scroll with sticky first column.** The feature name column must stay visible as the user scrolls through plans. CSS `position: sticky` on first column. Provide a scroll indicator (fade on the right edge).
4. **Collapse mobile to plan-first view** as an alternative to horizontal scroll for feature sets >20 rows. Let the user choose.
5. **Tooltips on feature names** that explain what the feature is. Assume the reader isn't an expert in your product taxonomy.
6. **Most popular plan gets a persistent column highlight** (background tint or border) that follows vertical scroll.

**Anti-patterns:**

- **Horizontal scroll without sticky first column.** Users lose context immediately.
- **Checkmarks without labels for screen readers.** Every checkmark or cross icon needs an aria-label.
- **More than 4 plans side-by-side.** Exceeds cognitive load and breaks most viewports. Consolidate or paginate.
- **No mobile alternative.** A 4-column table at 375px width is unusable.

**Elite examples:** Stripe (pricing comparison), Notion (plan comparison), Linear (plan feature grid).

---

## 9. Comments and Threads

Asynchronous collaborative discussion attached to content.

**Required states:** empty (no comments yet, invite first comment), loading, populated-unread (unread indicator in thread), populated-read, error (failed to post), soft-deleted (comment removed by author), permission-denied (view-only context).

**Key craft moves:**

1. **Thread collapse** at 3+ replies. Show avatar stack and reply count. Click to expand inline, not in a new panel.
2. **Reply indentation** max 2 levels deep. Beyond 2 levels, flatten and reference the parent by @mention. Deep nesting destroys readability.
3. **@mention autocomplete** triggers on `@` with a popover. Rank: project members first, recent collaborators second. Dismiss on Esc or click-outside. Accept on Enter or click.
4. **Edit history transparency:** edited comments show "(edited)" with a tooltip showing timestamp of last edit. Full edit history accessible via the timestamp link. Don't hide that edits happened.
5. **Soft-delete vs hard-delete:** authors soft-delete their own comments (renders "[Comment removed]", thread structure preserved). Admins can hard-delete. The choice matters for thread coherence.
6. **Unread-in-thread:** individual comments can be unread. Scroll the thread to the first unread comment on open, not to the top.
7. **Optimistic posting.** Comment appears immediately on submit. Failure state adds an error indicator and "Retry" inline, doesn't remove the comment.
8. **Reactions** on hover, not always visible. Emoji picker is a compact popover, not a full-page overlay.

**Anti-patterns:**

- **Unlimited nesting depth.** Notion's block comments and GitHub's PR comments both learned this lesson the hard way.
- **Hard delete without "removed" placeholder.** Breaks reply thread context.
- **No unread threading.** If users can't see what's new, they re-read everything or give up.
- **Comment box always expanded.** Show a condensed "Add a comment…" input. Expand on click or focus.

**Elite examples:** Linear (issue comments), Figma (canvas comments), GitHub (PR review threads).

---

## 10. Forms

Data capture surfaces from simple contact to multi-step wizards.

**Required states:** empty (pristine), touched (user has interacted), invalid (validation error), valid, submitting, success, error (server error), save-and-resume (partial).

**Key craft moves:**

1. **Label position:** above the field, not inside (placeholder). Placeholder disappears on type; label must persist. Exception: search inputs with a magnifier icon.
2. **Error on blur, not on change, not on submit only.** Validate when the user leaves a field. On submit, re-validate all fields and focus the first error.
3. **Inline validation** for format errors (email, phone, URL) on blur. For availability checks (username taken), debounce to 400ms after last keystroke and show a spinner while checking.
4. **Password manager support:** use `autocomplete` attributes correctly (`new-password`, `current-password`, `email`, `username`). Don't intercept paste events. Don't disable autocomplete on sensitive fields.
5. **Autofill:** test with browser autofill. Fields must have `name` and `autocomplete` attributes. Autofilled fields should have a visible highlight so users know they were populated.
6. **Multi-step wizard:** show a progress indicator (step X of N or a step bar). Each step is independently valid before proceeding. Back navigation preserves entries. Step URLs are deep-linkable.
7. **Save-and-resume:** for forms >2 minutes to complete, autosave to localStorage or server after each field blur. Show "Draft saved" at the form bottom.
8. **Abandoned form recovery:** if a user returns to a form URL with draft data, show a banner: "You have an unsaved draft from [date]. Continue or start fresh?"

**Anti-patterns:**

- **Error only on submit.** Users complete 8 fields before discovering field 2 is invalid. Causes high abandonment.
- **Disabling the submit button for invalid forms.** Instead, let them submit and show errors. Disabled submit with no explanation is a dead end.
- **Placeholder as label.** Fails when typing begins and fails accessibility.
- **Mandatory fields with no indicator.** Mark required fields; don't punish on submit.
- **Multi-step wizard with no back button.** Non-negotiable. Users need to correct earlier steps.

**Elite examples:** Stripe (payment forms), Typeform (wizard UX), Linear (issue creation form).

---

## 11. Onboarding

First-60-second experience that delivers the product's core promise.

**Required states:** new-user (zero data), returning-incomplete (setup started but not finished), sample-data mode, permission-prompts-deferred, completed.

**Key craft moves:**

1. **First-60s rule:** the user must reach a moment of genuine value within 60 seconds. Every step before that moment is a liability. Audit ruthlessly.
2. **Defer permissions.** Ask for notifications, contacts, location, camera only when contextually required—not in an upfront permission wall. Permission walls on launch are the leading cause of abandonment.
3. **Sample-data populated state** beats blank slate. Show what the product looks like with real data. "Your issues will appear here" is worse than a sample issue that demonstrates the interface. Linear does this well with a sample project.
4. **Contextual coaching** (tooltip anchored to a UI element) beats carousel tours. Carousels are skipped immediately. Contextual tooltips appear when the user first encounters a feature.
5. **Skip path is always present** and never hidden. Users who skip onboarding come back to it via Settings. Don't trap users in onboarding.
6. **Progress indicator** for multi-step setup shows steps remaining, not steps completed. "3 steps left" motivates completion; "step 2 of 5" doesn't.
7. **Checklist-style onboarding** (Intercom's model) persists in the sidebar until completed and is dismissable. Users work at their own pace.

**Anti-patterns:**

- **Permission wall on first launch.** Asking for 4 permissions before the user has seen the product. Accept rate is near zero.
- **Unskippable onboarding tour.** Disrespects user time. Everyone clicks through without reading.
- **Blank slate with illustration.** Pretty, but users don't know what the product does. Show a sample.
- **No way to return to setup.** Users who skip need a re-entry path. Put it in Settings → Getting Started.
- **Email confirmation before any value.** Let new users explore before requiring verification. Verify before they hit a write action, not before they can see anything.

**Elite examples:** Linear (sample project), Notion (template gallery), Raycast (progressive permission model).

---

## 12. Modals and Dialogs

Interruption patterns for focused, time-bounded tasks.

**Required states:** closed, opening (animation), open-empty (form or confirmation), open-loading (async content), open-error, closing (animation), blocked (unsaved changes on dismiss attempt).

**Key craft moves:**

1. **Modal vs sheet vs inline decision tree:** Modal = blocking, <3 fields, requires explicit decision. Sheet (bottom/side drawer) = complex forms, detail views, multi-step flows. Inline expansion = contextual, no context loss. Drawer on desktop; bottom sheet on mobile.
2. **Focus trapping:** keyboard Tab must cycle within the modal. Focus must move to the modal on open and return to the trigger element on close. This is both accessibility and usability.
3. **Esc behavior:** Esc closes if no unsaved changes. If unsaved changes exist, show "Discard changes?" confirmation. Never silently discard data on Esc.
4. **Click-outside behavior:** same as Esc for low-stakes modals. For forms with data entry, treat click-outside as "are you sure?" Same rule as Esc.
5. **Stacking ban:** one modal at a time. If you need a modal from within a modal, the architecture is wrong. Use a multi-step flow within a single modal or rethink the information architecture.
6. **Scroll lock on body:** apply `overflow: hidden` to `<body>` when modal opens. Prevent background scroll. This is CSS, not optional.
7. **Mobile bottom-sheet variant:** modals on mobile should slide up from the bottom, not appear centered. Centered modals on mobile are unreachable for one-handed use. Support swipe-down to dismiss.
8. **Size discipline:** modals are for focused tasks, not for displaying large amounts of content. If content requires scroll within the modal, it's probably a page.

**Anti-patterns:**

- **Nested modals.** Disorienting, hard to dismiss, and always an architecture smell.
- **Modal that blocks the entire screen on mobile with no dismiss.** Trap-modal is the design equivalent of a EULA.
- **No focus trapping.** Tab escapes the modal into background content. Accessibility failure.
- **Auto-dismissing confirmation modals.** Confirmation dialogs should never close on their own.
- **Using modal for long-form content.** Privacy policy in a modal. Terms in a modal. Don't.
- **Animate open but not close.** Asymmetric animation creates a jarring exit. Both directions need easing.

**Elite examples:** Linear (create issue modal), Stripe (confirmation dialogs), Arc (command palette as bottom sheet on mobile).

---

## Cross-Cutting Notes

**Every surface needs all five core states:** empty, loading, populated, error, and no-results. Audit each surface against this checklist before shipping. The states that get skipped are always empty and error.

**Consistency matters more than perfection.** A slightly suboptimal pattern applied consistently beats a perfect pattern applied to one surface and ignored on all others. Users build mental models from repetition.

**Audit CTAs against thumb reach and sticky regions.** On mobile, primary actions belong in the bottom 30% of the screen. On desktop, they belong at the top-right of a form or surface—not at the bottom of a long scroll. Sticky placement for primary CTAs in forms and wizards is table stakes.

**Keyboard-first is not "accessibility for power users."** It is the design contract for any surface that power users touch frequently. Tables, palettes, search, and inboxes must be fully keyboard-operable. This drives retention at the top of your user pyramid.

**States are designed, not handled.** The difference between average and elite is that average products design the happy path and "handle" edge states. Elite products design every state with the same craft as the primary flow. The empty inbox, the error row, the permission-denied section—all need intentional design.
