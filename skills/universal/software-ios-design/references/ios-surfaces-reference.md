# iOS Surfaces Reference

Choose the surface by the user's task. API availability and supported presentation contexts must be checked against the deployment target and installed SDK; tool release numbers do not establish OS support. Implementation belongs to [software-ios-native](../../software-ios-native/SKILL.md).

## Charts

Default to Swift Charts for marks it can express, including standard statistical and time-series displays. Use Canvas when custom geometry is essential, such as free-form radar or graph layouts; provide a separate accessible summary and inspectable values because drawn paths do not become accessible controls automatically. Keep selection feedback, units, and empty/error states consistent with the in-app display. Chart proxy and hit-testing implementation belongs to the native skill.

## Dynamic Island

Design compact, minimal, expanded, and Lock Screen layouts separately. Compact has leading/trailing regions around the camera; minimal prioritizes one recognizable signal; expanded can show the task's next useful action. Use Apple's [Live Activities HIG](https://developer.apple.com/design/human-interface-guidelines/live-activities) specifications for the target presentation rather than fixed pixel estimates.

People tap compact/minimal presentations to open the app and touch and hold to expand. Supported buttons and toggles can provide focused actions in the richer presentations; don't treat the entire surface as arbitrary in-app navigation chrome. Check the destination and action in each supported context. Avoid layout that relies on programmatic expansion.

## Widgets

Choose size families that add information or functionality, rather than stretching the same small design across every size. Read the current [Widgets HIG](https://developer.apple.com/design/human-interface-guidelines/widgets) context/family tables before promising a specific platform combination.

### Rendering modes and images

Read `widgetRenderingMode` from the environment and design for each applicable `WidgetRenderingMode`:

| Mode | Design decision |
|---|---|
| `.fullColor` | Preserve the app's semantic colors while checking light/dark contrast. |
| `.accented` | Separate primary and accent groups with `widgetAccentable(_:)`; the system recolors them. Both clear and tinted appearances can use this mode, so it is not a synonym for one appearance. |
| `.vibrant` | Expect monochrome/desaturated content; encode status with shape, text, and hierarchy as well as color. |

Inspect photos, logos, and gradient charts with `widgetAccentedRenderingMode(_:)` where supported. Select the image treatment by whether luminance or original color carries essential meaning, then preview the result; forcing every image to full color can undermine the system appearance. Mark backgrounds with `containerBackground(for: .widget)` so the system can remove them without removing meaningful content. Verify the background-free design as well as the full-color screenshot.

Sources: [Preparing widgets for additional contexts and appearances](https://developer.apple.com/documentation/widgetkit/preparing-widgets-for-additional-contexts-and-appearances), [WidgetRenderingMode](https://developer.apple.com/documentation/widgetkit/widgetrenderingmode), and [widgetAccentedRenderingMode(_:)](https://developer.apple.com/documentation/swiftui/image/widgetaccentedrenderingmode(_:)). Check availability and rendering behavior for the actual target OS at this decision.

### Content and interaction

Widgets are glanceable summaries with focused buttons/toggles and relevant deep links, rather than continuously updating miniature app screens. Show stale-data context when refresh timing affects meaning. System font styles and scaling custom fonts support Dynamic Type; test the largest supported text sizes and avoid fixed-size custom fonts.

Design gallery previews, loading, signed-out, unavailable, and failed-action states as deliberate content. A button may execute an intent without opening the app; don't imply every interaction opens it. Intent execution, timeline providers, refresh budgets, and storage belong to the native skill.

## Controls (ControlWidget)

Use a `ControlWidget` for a focused action or two-state toggle in Control Center, the Lock Screen, or the Action button. Use the system's button/toggle templates with concise text and symbol images; templates adapt the control to its space. A custom widget layout is not interchangeable with a control template.

Choose a symbol that conveys the action and a label that distinguishes configured targets. Check inactive gallery preview, current state, configuration choices, and the resulting app destination if it opens the app. For sensitive actions, specify authentication and locked-device redaction requirements before implementation. Verify device behavior rather than assuming a preview demonstrates a locked-device action.

Sources: [ControlWidget](https://developer.apple.com/documentation/swiftui/controlwidget) and [Creating controls to perform actions across the system](https://developer.apple.com/documentation/widgetkit/creating-controls-to-perform-actions-across-the-system). Look up the target SDK's supported templates and contexts; App Intent/value-provider implementation belongs to the native skill.

## App icons and Icon Composer

Use layered artwork in Icon Composer when adopting the system's icon material. Separate silhouettes that must remain recognizable from optional material highlights. Preview small-size legibility and each appearance offered by the target OS/tool, including dark and monochrome treatments where supported; avoid relying on color alone to distinguish the app.

Read [Icon Composer](https://developer.apple.com/icon-composer/) for supported appearance modes, host requirements, and Xcode integration before producing the asset. Use its official product name; don't infer numbered editions from WWDC summaries. Keep the editable layered asset; a flattened marketing export is a separate deliverable. Asset packaging and deployment compatibility belong to the native skill.

## App Clips

Design for one immediate task: clear invocation context, concise card copy, and completion without unnecessary onboarding. Offer continuation into the full app after the task, preserving what the user just did. Read Apple's App Clip documentation for invocation and size constraints; don't estimate an upload limit with the uncompressed `.app` size. Entitlements, invocation URLs, and packaging belong to the native skill and [software-mobile](../../software-mobile/SKILL.md).

## App Intents and Shortcuts

Name actions by their user-visible outcome. Use concise titles, meaningful symbols, clear parameter prompts, and an understandable confirmation/result. Preserve the same terminology across Siri, Shortcuts, controls, and the app. Decide which actions need authentication or an app destination. Donation, indexing, and intent implementation belong to the native skill; do not promise when system suggestions will appear.

## Drag and Drop with Transferable

The drag preview should preserve the object's identity without obscuring its destination. Make valid drop targets discoverable and provide visible success/failure feedback, including for multi-item drops. Offer a non-drag path for the same task. Transferable representations and UIKit interoperability belong to the native skill.

## ShareLink vs UIActivityViewController

Default to the standard share sheet. Verify item title, preview, and content against what the receiver obtains. Use a UIKit bridge only when the required share-sheet behavior cannot be expressed through ShareLink; don't silently replace system affordances with a custom chooser. Sharing implementation belongs to the native skill.

## NavigationSplitView for iPad

Use a split view for a persistent list/detail relationship. Preserve selected content, back navigation, and recovery from deleted items when the layout collapses to compact width or expands again. Test narrow windows and keyboard navigation as well as full-screen iPad. Do not assume a collapse inherently resets all state or that one split-view style produces equal columns; let content priorities drive the layout.

## Swipe Actions

Expose a small set of recognizable actions and give them text labels. Confirm they fit at supported widths and translated lengths. A destructive full swipe needs an undo or deliberate confirmation; turn it off when recovery is impossible. Leading/trailing placement and action count are design choices to test, not fixed character limits or a blanket rule that full swipe is destructive-only.

## Photo / Document Picker

Prefer system pickers for choosing existing content without unnecessary library-wide permission requests. Design cancellation, unavailable/remote assets, unsupported types, progress, and load failure. A selected item is not proof that its contents have loaded. Security-scoped access and transfer handling belong to the native skill.

## Camera Surface

Keep capture controls stable while the viewfinder starts, and show a useful denied/unavailable/interrupted state. Focus/exposure feedback must follow the selected point without covering the subject. Preserve captured work across review, retake, and cancellation. Session lifecycle, permission handling, format selection, and preview-layer bridging belong to the native skill; measure startup on target hardware instead of promising a universal latency.

## Live Activities

Choose an activity with a defined start and end. Prioritize its progress, current state, next useful action, and completion; avoid promotions and sensitive Lock Screen content. Check the compact, minimal, expanded, and Lock Screen layouts plus any Mac menu-bar, Apple Watch Smart Stack, CarPlay, or StandBy contexts the target OS supports. Cross-device presentation can reuse layouts in unexpected ways, so an iPhone screenshot alone is incomplete proof.

Read the [Live Activities HIG](https://developer.apple.com/design/human-interface-guidelines/live-activities) and ActivityKit documentation for applicable presentation and lifecycle constraints before choosing the duration and update promise. Include stale, failed, canceled, and completed states. Lifecycle, APNs budgets, and activity reconnection belong to the native skill.

## Universal Links + Handoff

Continuation should open the relevant content and preserve the user's task. Design signed-out, missing/deleted content, permission denial, and unsupported-destination fallbacks. Make returning to the previous context predictable. Associated domains, routing, and Handoff advertisement implementation belong to the native skill.

## Multitasking Awareness

Test resizing, compact/regular transitions, and supported multi-window arrangements rather than assuming full-screen device dimensions. Each window should retain its own selected content and navigation context. Verify keyboard focus, sheets, and inspector visibility during resize. Scene configuration and persistence implementation belong to the native skill.
