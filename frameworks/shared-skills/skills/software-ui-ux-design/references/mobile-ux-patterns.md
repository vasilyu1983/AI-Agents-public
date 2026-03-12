# Mobile UX Patterns — Platform-Specific Design Guide (Jan 2026)

Comprehensive mobile UX patterns covering thumb zone ergonomics, navigation patterns, gestures, forms, onboarding, permissions, and platform-specific differences between iOS and Android. Designed for practitioners building production mobile experiences.

---

## Thumb Zone and Reachability

Modern mobile screens range from 5.4" to 6.9". Users hold phones differently, but one-handed thumb operation is the dominant mode for quick interactions.

### Thumb Reach Zones

```text
┌─────────────────────┐
│  HARD TO REACH      │  ← Top bar, overflow menus
│  (stretch zone)     │
│                     │
├─────────────────────┤
│                     │
│  MODERATE REACH     │  ← Content area, secondary actions
│  (ok zone)          │
│                     │
├─────────────────────┤
│                     │
│  EASY TO REACH      │  ← Primary actions, navigation
│  (natural zone)     │
│                     │
└─────────────────────┘
```

### Design Implications

| Principle | Implementation | Platform Reference |
|-----------|---------------|-------------------|
| Primary actions at bottom | Bottom navigation bar, FAB, action sheets | iOS tab bar, Android bottom navigation |
| Avoid top-left for critical actions | Hamburger menus are hard to reach one-handed | Place key actions bottom-right or center |
| Large phones: pull-down gestures | Pull-to-refresh, swipe-down menus bring content closer | iOS large title collapse, Android search bar pull |
| Contextual actions near content | Action buttons below or beside their related content | Inline actions, swipe-to-reveal |

### Floating Action Button (FAB) Placement

| Position | When to Use | When to Avoid |
|----------|------------|---------------|
| Bottom-right | Primary creation action (new message, new item) | When it obscures important content |
| Bottom-center | Single primary action per screen | Multi-action screens |
| Extended FAB | Action needs a label for clarity | Space-constrained layouts |
| Speed dial FAB | Multiple related creation actions | More than 6 options |

---

## Mobile Navigation Patterns

### Pattern Comparison

| Pattern | Best For | Max Items | iOS | Android |
|---------|----------|-----------|-----|---------|
| **Tab bar** | 3-5 top-level destinations, flat hierarchy | 5 | UITabBarController | BottomNavigationView |
| **Drawer (hamburger)** | 5+ destinations, infrequent navigation | 8-10 | Not recommended natively | NavigationDrawer |
| **Stack navigation** | Linear flows, drill-down content | N/A | UINavigationController | NavHost + Fragments |
| **Bottom sheet** | Contextual actions, filters, detail preview | N/A | UISheetPresentationController | BottomSheetBehavior |
| **Top tabs** | Sibling categories within a section | 3-5 visible | Not native, use sparingly | TabLayout + ViewPager |
| **Hub and spoke** | Independent task areas with no cross-linking | 4-8 | Tab bar + stack per tab | Bottom nav + NavGraph |

### Tab Bar Best Practices

```text
DO:
  ✓ Use 3-5 tabs maximum
  ✓ Show icons + short labels
  ✓ Highlight active tab clearly (color + label change)
  ✓ Preserve scroll position when switching tabs
  ✓ Use badge indicators for notifications/updates

AVOID:
  ✗ More than 5 tabs (use "More" tab sparingly)
  ✗ Scrollable tab bars for primary navigation
  ✗ Icon-only tabs (except universally recognized: home, search, profile)
  ✗ Nesting tab bars within tab bars
  ✗ Hiding the tab bar on scroll (users lose navigation context)
```

### Bottom Sheet Patterns

| Type | Behavior | Use Case |
|------|----------|----------|
| Modal bottom sheet | Blocks background interaction, has dismiss handle | Filters, share sheet, payment selection |
| Persistent bottom sheet | Background remains interactive, sheet overlays | Map detail preview, media player mini controls |
| Expanding bottom sheet | Starts collapsed, expands to full screen | Ride-sharing detail, search results |

---

## Gesture Patterns

### Common Gestures

| Gesture | Action | Implementation Notes |
|---------|--------|---------------------|
| **Tap** | Select, activate | Default interaction; ensure 44pt/48dp touch target |
| **Long press** | Context menu, selection mode | Provide haptic feedback; show preview on iOS |
| **Swipe horizontal** | Delete, archive, navigate between items | Reveal action buttons; support undo for destructive |
| **Swipe vertical** | Pull-to-refresh, dismiss | Standard spring physics; show loading indicator |
| **Pinch** | Zoom in/out | Images, maps; maintain focal point |
| **Double tap** | Zoom to fit, like/favorite | Context-dependent; be consistent within app |
| **Drag** | Reorder, move elements | Show drag handle affordance; provide haptic feedback |

### Gesture Design Principles

- **Discoverable**: Gestures must not be the only way to perform an action. Always provide a visible alternative (button, menu item).
- **Reversible**: Destructive swipe actions (delete, archive) must show an undo option.
- **Consistent**: Same gesture should do the same thing throughout the app.
- **Accessible**: Provide non-gesture alternatives for motor-impaired users (WCAG 2.5.1 Pointer Gestures).
- **Haptic feedback**: Confirm gesture recognition with appropriate haptic response.

### Swipe-to-Action Pattern

```text
┌──────────────────────────────────────────┐
│ Item content                        ← →  │  Default state
├──────────────────────────────────────────┤
│ ████ Archive │ Item content    │ Delete ██│  Partially swiped
├──────────────────────────────────────────┤
│ ██████████ ARCHIVED ██████████████████████│  Full swipe (threshold met)
└──────────────────────────────────────────┘

Rules:
- Left swipe: destructive action (delete, remove)
- Right swipe: positive action (archive, complete)
- Partial swipe: reveal action buttons
- Full swipe: execute primary action
- Always show undo snackbar for destructive actions
```

---

## Mobile Forms

### Input Type Optimization

| Data Type | HTML Input Type | iOS Keyboard | Android Keyboard | Notes |
|-----------|----------------|-------------|-----------------|-------|
| Email | `type="email"` | Email keyboard | Email keyboard | Shows @ and .com |
| Phone | `type="tel"` | Phone keypad | Phone keypad | Numbers only |
| Number | `type="number"` or `inputmode="numeric"` | Number pad | Number pad | Use `inputmode` for better control |
| URL | `type="url"` | URL keyboard | URL keyboard | Shows / and .com |
| Credit card | `inputmode="numeric"` + `autocomplete="cc-number"` | Number pad | Number pad | Enable autofill |
| Currency | `inputmode="decimal"` | Decimal pad | Decimal pad | Shows decimal point |
| Date | Native date picker | UIDatePicker | MaterialDatePicker | Avoid text input for dates |
| Password | `type="password"` + toggle | Standard + toggle | Standard + toggle | Always show/hide toggle |

### Autofill Optimization

```html
<!-- Enable platform autofill with correct autocomplete values -->
<form autocomplete="on">
  <input type="text" autocomplete="name" />
  <input type="email" autocomplete="email" />
  <input type="tel" autocomplete="tel" />
  <input type="text" autocomplete="street-address" />
  <input type="text" autocomplete="address-level2" /> <!-- city -->
  <input type="text" autocomplete="postal-code" />
  <input type="text" autocomplete="cc-name" />
  <input type="text" autocomplete="cc-number" inputmode="numeric" />
  <input type="text" autocomplete="cc-exp" /> <!-- MM/YY -->
  <input type="password" autocomplete="new-password" /> <!-- signup -->
  <input type="password" autocomplete="current-password" /> <!-- login -->
</form>
```

### Mobile Form Layout Rules

- **Single column only**: Multi-column forms increase completion time by 50%+ on mobile
- **Top-aligned labels**: Fastest scanning speed (Baymard Institute)
- **Full-width inputs**: Tap targets span screen width
- **Sticky submit button**: Visible without scrolling, above keyboard
- **Real-time validation**: Validate on field blur, not on submit
- **Progress indicator**: For multi-step forms (step 2 of 4)

---

## Touch Target Sizing

### Platform Requirements

| Standard | Minimum Size | Recommended Size | Spacing |
|----------|-------------|-----------------|---------|
| **iOS (Apple HIG)** | 44 x 44 pt | 44 x 44 pt | 8pt between targets |
| **Android (Material)** | 48 x 48 dp | 48 x 48 dp | 8dp between targets |
| **WCAG 2.5.8** (Level AAA) | 44 x 44 CSS px | 44 x 44 CSS px | — |
| **WCAG 2.5.5** (Level AA) | 24 x 24 CSS px | 44 x 44 CSS px | — |

### Common Violations

| Component | Typical Problem | Fix |
|-----------|----------------|-----|
| Text links in paragraphs | Tap target too small, overlaps adjacent links | Add padding, increase line-height, or use buttons |
| Icon-only buttons | Visual icon is 24px but tap target is also 24px | Increase tap area with padding to 44/48 minimum |
| Close/dismiss buttons | Tiny X in corner | Minimum 44x44 tap area, consider gesture dismiss |
| Checkbox/radio | Native element too small | Custom styling with larger hit area |
| Dense lists | Items too close together | Minimum 48dp row height, 8dp vertical spacing |

---

## Mobile Onboarding Patterns

### Pattern Comparison

| Pattern | When to Use | Retention Impact | Example |
|---------|------------|-----------------|---------|
| **Progressive disclosure** | Complex apps with many features | High (learn as needed) | Slack: introduces channels after first message |
| **Coach marks / tooltips** | Highlighting specific UI elements | Medium (contextual) | Point to a specific button on first visit |
| **Onboarding carousel** | Communicating value proposition | Low (often skipped) | 3-4 screens with Skip button |
| **Interactive tutorial** | Task-based apps with unique interactions | High (learn by doing) | Duolingo: complete first lesson during onboarding |
| **Empty state guidance** | Content-driven apps | High (just-in-time) | Notion: template suggestions on empty page |
| **Personalization flow** | Apps with diverse use cases | Medium-High | Spotify: genre selection for recommendations |

### Onboarding Decision Framework

```text
Is your app's core action obvious?
  ├─ YES → Skip onboarding, use empty state guidance
  │   (e.g., calculator, timer, notes app)
  ├─ MOSTLY → Progressive disclosure + contextual tooltips
  │   (e.g., email client, social media)
  └─ NO → Interactive tutorial for core workflow
      (e.g., design tools, project management)

Does your app need personalization to be useful?
  ├─ YES → Personalization flow first, then value delivery
  │   (e.g., news app, fitness tracker)
  └─ NO → Get to value immediately, personalize later
```

### Onboarding Anti-Patterns

- Carousel with 5+ slides (users skip after 2)
- Mandatory account creation before showing value
- Feature tours that explain UI elements without context
- Non-skippable tutorials
- Onboarding that cannot be revisited later

---

## Permission Request Patterns

### Best Practices by Type

| Permission | When to Ask | Pre-Prompt? | Fallback if Denied |
|-----------|------------|-------------|-------------------|
| **Push notifications** | After user sees value | Yes (explain benefit) | In-app notification center |
| **Camera** | When user taps camera button | Optional (context is clear) | Manual file upload |
| **Location** | When user initiates location-based action | Yes (explain why) | Manual address entry |
| **Contacts** | When user explicitly tries to invite/share | Yes (explain data handling) | Manual entry or share link |
| **Microphone** | When user initiates voice/audio feature | Optional (context is clear) | Text input alternative |
| **Photos** | When user selects image picker | Optional | Limited photo picker (iOS 14+) |

### Pre-Prompt Pattern

```text
WRONG: Immediately on app launch
┌────────────────────────┐
│ "App" would like to    │  ← User has no context
│ send you notifications │     for why this matters
│ [Don't Allow] [Allow]  │
└────────────────────────┘

RIGHT: After demonstrating value, with context screen
┌────────────────────────┐
│ Stay updated on your   │  ← Custom screen explains
│ order delivery status  │     the specific benefit
│                        │
│ [Enable Notifications] │  ← User taps, THEN system
│ [Not Now]              │     prompt appears
└────────────────────────┘
```

### iOS 16+ Provisional Notifications

iOS supports provisional push notifications (delivered silently to notification center). Consider this for lower-friction notification adoption. The user sees a "Keep" or "Turn Off" prompt inline.

---

## Mobile Empty States and Loading Patterns

### Empty State Design

| State | Content | Action |
|-------|---------|--------|
| **First use** | Welcome message + clear next step | Primary CTA to create first item |
| **No results** | Helpful message + search suggestions | Modify filters, clear search, browse categories |
| **Error** | What went wrong + how to fix | Retry button, check connection prompt |
| **Completed** | Celebration + next logical action | "All caught up" + explore related content |

### Loading Pattern Hierarchy

| Pattern | When to Use | Perceived Speed |
|---------|------------|----------------|
| **Skeleton screens** | Content layout is predictable | Fastest perceived |
| **Progressive loading** | Images, feeds (load text first, then media) | Fast |
| **Pull-to-refresh spinner** | User-initiated refresh | Expected |
| **Inline spinner** | Button action, partial load | Acceptable |
| **Full-screen spinner** | Only if < 2 seconds and no layout to skeleton | Slowest perceived |
| **Shimmer effect** | Lists and cards with known layout | Fast (animation adds life) |

### Skeleton Screen Implementation

```text
┌─────────────────────────────────────┐
│ ████████████  ░░░░░░░░░░░░          │  ← Avatar + name placeholder
│                                     │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │  ← Content line 1
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░         │  ← Content line 2
│ ░░░░░░░░░░░░░░░░░░                  │  ← Content line 3
│                                     │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │  ← Image placeholder
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
├─────────────────────────────────────┤

Rules:
- Match actual content layout dimensions
- Use subtle pulse/shimmer animation (prefers-reduced-motion aware)
- Transition to real content without layout shift
- Show skeleton for minimum 300ms to avoid flash
```

---

## Platform-Specific Patterns: iOS vs Android

### Navigation Differences

| Pattern | iOS | Android |
|---------|-----|---------|
| Back navigation | Left edge swipe or back button in nav bar | System back button / gesture |
| Primary navigation | Bottom tab bar | Bottom navigation or navigation drawer |
| Contextual actions | Trailing nav bar buttons, swipe actions | AppBar actions, overflow menu (three dots) |
| Modal dismiss | Swipe down, X button, or Done button | Back gesture/button, X button |
| Search | Pull-down search bar in navigation | Search icon in AppBar expanding to search field |
| Share | System share sheet (bottom) | System share sheet (bottom) |

### Visual and Interaction Differences

| Aspect | iOS | Android |
|--------|-----|---------|
| Typography | SF Pro, Dynamic Type | Roboto, Material type scale |
| Corner radius | Continuous (squircle) | Rounded rectangle |
| Elevation | Subtle, blur-based | Drop shadow with defined elevation levels |
| Switches | Green toggle (system color) | Material switch with track + thumb |
| Action sheets | Bottom sheet with cancel | Bottom sheet or dialog |
| Alerts | Centered dialog, 2 buttons max typical | Material dialog, flexible button count |
| Haptics | Taptic Engine (UIFeedbackGenerator) | Vibration API (limited granularity) |
| Pull-to-refresh | Native UIRefreshControl | SwipeRefreshLayout |

### When to Follow Platform Conventions vs Unify

| Scenario | Recommendation |
|----------|---------------|
| Navigation structure | Follow platform conventions |
| Core interaction patterns (back, share, search) | Follow platform conventions |
| Brand identity (colors, typography, imagery) | Unify across platforms |
| Content layout and information architecture | Unify across platforms |
| Settings and preferences UI | Follow platform conventions |
| Custom interactions (app-specific gestures) | Unify but respect platform gesture conflicts |

---

## Mobile Checkout and Payment UX

### Checkout Flow Optimization

| Step | Mobile Best Practice | Impact |
|------|---------------------|--------|
| Cart review | Sticky total bar at bottom, easy quantity edit | -5-10% abandonment |
| Guest checkout | Prominent guest option, no forced signup | -25-30% abandonment |
| Address entry | Autofill + autocomplete (Google Places) | -15-20% time to complete |
| Payment | Apple Pay / Google Pay as first option | +20-30% conversion on supported devices |
| Confirmation | Clear success state + order number + delivery estimate | Trust and satisfaction |

### Mobile Payment Hierarchy

```text
Priority order for payment methods (conversion impact):
1. Platform native: Apple Pay / Google Pay (1-2 tap checkout)
2. Saved card (returning customers)
3. Express checkout: Shop Pay, PayPal Express, Klarna
4. Card entry: with camera scan + autofill
5. Alternative: bank transfer, BNPL, crypto (market-specific)
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|-------------|-------------|------------------|
| Full-screen interstitials on load | 70% of users leave (Google data) | Inline promotions or delayed modal |
| Hiding navigation on scroll | Users lose orientation, harder to switch context | Keep bottom navigation persistent |
| Custom gestures without visible alternatives | Undiscoverable, accessibility barrier | Always provide button alternative |
| Infinite scroll with no save state | Users lose position on back navigation | Preserve scroll position, offer "Jump to top" |
| Non-native date pickers | Slower than platform pickers, accessibility issues | Use native date/time pickers |
| Landscape mode ignored | App breaks or shows mobile layout stretched | Either support landscape properly or lock portrait |
| Splash screen as ad space | Delays time-to-content, user frustration | Minimal splash (branding only), < 2 seconds |

---

## References

- [Apple Human Interface Guidelines — iOS](https://developer.apple.com/design/human-interface-guidelines/)
- [Material Design 3](https://m3.material.io/)
- [WCAG 2.2 — Target Size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html)
- [Baymard Institute — Mobile UX](https://baymard.com/blog/mobile-ux)
- [Nielsen Norman Group — Mobile UX](https://www.nngroup.com/topic/mobile-usability/)
- [Luke Wroblewski — Touch Gesture Reference Guide](https://www.lukew.com/touch/)

---

## Cross-References

- [SKILL.md](../SKILL.md) — Parent skill overview and platform constraints
- [wcag-accessibility.md](wcag-accessibility.md) — WCAG 2.2 compliance including mobile targets
- [cro-framework.md](cro-framework.md) — Checkout optimization and conversion patterns
- [design-systems.md](design-systems.md) — Component patterns for mobile design systems
- [nielsen-heuristics.md](nielsen-heuristics.md) — Heuristic evaluation applicable to mobile
