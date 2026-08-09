# iOS Accessibility Patterns

Use this reference for accessibility decisions embedded in design — VoiceOver, Dynamic Type, Reduce Motion, Reduce Transparency, contrast, and the iOS 26 Accessibility Nutrition Labels that App Store reviewers now check.

This is iOS-specific. For broader, cross-platform accessibility remediation see [software-accessibility](../../software-accessibility/SKILL.md).

## Table of Contents

- [The Four Accessibility Settings You Must Test](#the-four-accessibility-settings-you-must-test)
- [VoiceOver](#voiceover)
- [Dynamic Type](#dynamic-type)
- [Reduce Motion](#reduce-motion)
- [Reduce Transparency and Increase Contrast](#reduce-transparency-and-increase-contrast)
- [Haptics and Non-Visual Feedback](#haptics-and-non-visual-feedback)
- [Accessibility Nutrition Labels (iOS 26)](#accessibility-nutrition-labels-ios-26)
- [Verification Checklist](#verification-checklist)
- [Anti-Patterns](#anti-patterns)

## The Four Accessibility Settings You Must Test

Before shipping any screen, verify behavior with each of these toggled on:

| Setting | Where | Catches |
|---|---|---|
| Dynamic Type → AX5 | Settings → Accessibility → Display & Text Size → Larger Text | Clipped text, fixed-height layouts, untranslated images |
| Reduce Motion | Settings → Accessibility → Motion | Animations that disorient (parallax, scale-bounce, Canvas autoplay) |
| Reduce Transparency | Settings → Accessibility → Display & Text Size | Materials/glass dropping to opaque — text contrast regressions |
| VoiceOver ON | Settings → Accessibility → VoiceOver | Missing labels, broken focus order, uncombined rows |

"Design complete" is not complete until the screen survives all four.

## VoiceOver

### Labels, Traits, and Hints

Every interactive element needs at minimum a label. Add traits and hints when the control behavior is non-obvious.

```swift
Button { openDetail() } label: {
    Image(systemName: "info.circle")
}
.accessibilityLabel("Details")
.accessibilityHint("Opens the full reading")  // optional; describes *what happens*, not *what it is*
```

Trait rules:

- SwiftUI infers traits from container type (`Button` = `.isButton`, `Toggle` = `.isToggle`). Don't re-add.
- Add `.accessibilityAddTraits(.isHeader)` to section labels so VoiceOver users can navigate by heading.
- Add `.accessibilityAddTraits(.isSelected)` to currently-active items (segmented control, filter chip, tab).
- Remove `.isImage` trait from decorative images: `.accessibilityHidden(true)`.

### Combining Complex Rows

A row of label + value + chevron reads as three separate elements by default. Combine them:

```swift
HStack {
    Image(systemName: "sun.max.fill")
    Text("Today")
    Spacer()
    Text(summary)
    Image(systemName: "chevron.right")
}
.accessibilityElement(children: .combine)
.accessibilityLabel("Today, \(summary)")
.accessibilityHint("Opens today's detail")
```

Use `.combine` when the row is one conceptual unit. Use `.contain` when children should remain individually navigable (e.g., a card with its own buttons inside).

### Custom Actions and Rotor

For rows with multiple interactions (swipe-to-delete, long-press menu), expose them as actions:

```swift
.accessibilityAction(named: "Delete") { delete() }
.accessibilityAction(named: "Archive") { archive() }
```

VoiceOver users reach these through the rotor — they can't swipe custom swipe-actions.

For custom rotor categories (e.g., "Links" rotor on a text-heavy screen):

```swift
.accessibilityRotor("Articles") {
    ForEach(articles) { article in
        AccessibilityRotorEntry(article.title, id: article.id)
    }
}
```

### accessibilityRepresentation

When you build a custom control that mimics a system control, hand VoiceOver the native representation instead of reinventing labels:

```swift
CustomPillToggle(isOn: $enabled, label: "Dark Mode")
    .accessibilityRepresentation {
        Toggle("Dark Mode", isOn: $enabled)   // VoiceOver sees a real Toggle
    }
```

This is the cleanest way to get a custom visual control to read correctly.

### Focus Order

Default focus order is leading→trailing, top→bottom. Override when the visual order differs:

```swift
.accessibilitySortPriority(1)   // higher = earlier in focus order
```

Always prefer redesigning the layout so default order is correct. Manual sort priority is a last resort.

## Dynamic Type

Dynamic Type isn't "support large fonts." It's "every layout must survive XXL → AX5 without truncation or overlap."

### Failure modes

1. **Fixed-height rows.** `.frame(height: 44)` clips text at AX3+. Use `.frame(minHeight: 44)` or let content size drive.
2. **Side-by-side label columns.** `HStack { Text(label); Spacer(); Text(value) }` wraps ugly at AX5. Use `LabeledContent` (adaptive) or stack vertically at large sizes.
3. **Icons that don't scale with their label.** An 11pt SF Symbol next to a `.body` label stays 11pt while the label grows to 53pt — visually broken. Use `.imageScale(.large)` or `@ScaledMetric` for icon size.
4. **Truncation as a fix.** `.lineLimit(1)` + `minimumScaleFactor(0.5)` hides the problem. At AX5 the text becomes unreadable at half-size instead of wrapping.
5. **Modals and sheets that don't scroll.** At AX5, sheet content may exceed screen height. Wrap sheet bodies in `ScrollView`.
6. **Images without text alternatives at large sizes.** An icon-only button has nothing to grow; screen-reader users and users who can't distinguish the glyph are stuck.

### `@ScaledMetric` for non-text sizing

Scale spacing, icon sizes, and row heights with Dynamic Type:

```swift
@ScaledMetric(relativeTo: .body) private var rowHeight: CGFloat = 56
@ScaledMetric(relativeTo: .body) private var iconSize: CGFloat = 20

HStack {
    Image(systemName: "sun.max.fill")
        .font(.system(size: iconSize))
    Text("Today")
}
.frame(minHeight: rowHeight)
```

### Limiting Dynamic Type

In rare cases where a custom layout cannot absorb AX5, clamp the range:

```swift
.dynamicTypeSize(.xSmall ... .accessibility2)
```

Only do this when you've tried everything else. Clamping is disclosed in Accessibility Nutrition Labels.

### Testing

- Use the Dynamic Type preview in Xcode canvas: `.previewDynamicTypeSize(.accessibility5)`
- Use the Accessibility Inspector's Dynamic Type slider live against the simulator.

## Reduce Motion

Motion that reads as "playful" to most users can trigger vestibular discomfort. When `@Environment(\.accessibilityReduceMotion)` is true, suppress or soften animations.

### Global modifier pattern (recommended)

Build one modifier that kills motion for its entire descendant tree, and apply it once at the app root:

```swift
struct MotionSensitive: ViewModifier {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    func body(content: Content) -> some View {
        content.transaction { tx in
            if reduceMotion { tx.animation = nil }
        }
    }
}

extension View {
    func motionSensitive() -> some View { modifier(MotionSensitive()) }
}

// At the app root:
ContentView().motionSensitive()
```

Per-screen `@Environment(\.accessibilityReduceMotion)` checks scattered across features is the anti-pattern — every new feature must remember the check, and one missed file fails App Review.

### Suppress at the ButtonStyle layer

Press-bounce animations also need Reduce Motion awareness:

```swift
struct BounceButtonStyle: ButtonStyle {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed && !reduceMotion ? 0.94 : 1)
            .animation(reduceMotion ? nil : .easeOut(duration: 0.1), value: configuration.isPressed)
    }
}
```

### Canvas auto-animations

Canvas views that animate on appear (score rings, terrain reveals, Gantt bars) must start in their final state under Reduce Motion — don't animate from zero.

## Reduce Transparency and Increase Contrast

### Reduce Transparency

Materials and Liquid Glass fall back to opaque when this is on. Verify:

- Text contrast in the opaque state (materials often hide poor contrast behind blur).
- Layering still reads correctly — if your sheet background is `.ultraThinMaterial`, the opaque fallback needs to be a clear semantic color (`Color(.systemBackground)`), not your brand tint.

```swift
@Environment(\.accessibilityReduceTransparency) private var reduceTransparency

var background: some View {
    Group {
        if reduceTransparency {
            Color(.systemBackground)
        } else {
            Rectangle().fill(.ultraThinMaterial)
        }
    }
}
```

### Increase Contrast

The system auto-adjusts semantic colors when this is on. If you hardcoded colors, you miss the adjustment.

- Use `Color(.label)`, `Color(.secondaryLabel)`, not `.black`/`.gray`.
- Re-verify custom accent colors in Increase Contrast — many brand accents drop below 3:1.

## Haptics and Non-Visual Feedback

For VoiceOver and low-vision users, haptics and audio cues carry more weight than visual affordances.

- Confirm destructive actions with `.sensoryFeedback(.warning, trigger:)`.
- Confirm success with `.sensoryFeedback(.success, trigger:)`.
- Use `.selection` for picker/segmented changes.
- Use `.impact(flexibility: .soft, intensity: 0.4)` for subtle tap confirmation on rows.

Don't stack haptics — one haptic per user action. Rapid-fire haptics (e.g., during a scroll scrub) are fine at `.selection`.

iOS 26 expanded haptic-as-primary-feedback guidance for vision-impaired users. When a control's only confirmation is visual (e.g., "button briefly glows"), add a haptic so VoiceOver users feel the same confirmation.

## Accessibility Nutrition Labels (iOS 26)

The App Store now displays developer-declared accessibility features per app. Each declaration commits you to actually supporting that feature — reviewers verify.

The labels cover:

- VoiceOver support
- Voice Control support
- Larger Text (Dynamic Type)
- Sufficient Contrast
- Differentiate Without Color Alone
- Captions
- Audio Descriptions
- Dark Interface

Design implication: decide what you support *before* marketing copy or App Store screenshots. If you commit to "Larger Text" but ship screens that clip at AX3, you risk rejection under App Store Guideline 4.0 Design or user-reported accessibility complaints.

## Verification Checklist

For every user-facing screen:

1. **VoiceOver ON, swipe through** — every control reads a meaningful label; focus order matches reading order; no "Button" without context.
2. **Dynamic Type AX3 + AX5** — no clipping, no overlap, no horizontal scroll forced.
3. **Reduce Motion** — animations softened or suppressed; no parallax/scale-bounce.
4. **Reduce Transparency** — materials fall back to opaque; contrast still passes.
5. **Increase Contrast** — text still readable; accent elements still distinguishable.
6. **Dark Mode + Light Mode** — contrast and hierarchy hold in both.
7. **Differentiate Without Color** — status isn't color-only (add icon, pattern, or text label for green/red states).
8. **Accessibility Inspector audit** — runs the automatic contrast and label checks; fix everything flagged.

## Anti-Patterns

- `.accessibilityLabel("")` to silence elements — use `.accessibilityHidden(true)` instead.
- Passing the visible text as the label when it's redundant — SwiftUI already uses the visible text.
- Adding `.isButton` trait to non-buttons.
- `minimumScaleFactor(0.5)` as a Dynamic Type fix.
- Hardcoded `.black`/`.white` in Canvas without passing colorScheme.
- "Supports VoiceOver" marketing claim without actually walking the app with VoiceOver.
- Per-screen Reduce Motion checks instead of a shared global modifier.
- Swipe-to-delete as the only way to delete — expose as `.accessibilityAction`.
- Icon-only controls with no label.
- Progress indicators with no `.accessibilityValue` — VoiceOver reads "ProgressView" without the percentage.
- Stacking multiple haptics on one action — feels broken to VoiceOver users who rely on haptics as signal.
