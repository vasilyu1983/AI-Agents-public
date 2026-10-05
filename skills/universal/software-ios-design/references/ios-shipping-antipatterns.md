# iOS Shipping Anti-Patterns

Load this for design-facing failures before handoff. Release mechanics, SDK upload requirements, entitlements, and store metadata rules belong to [software-mobile](../../software-mobile/SKILL.md) and [software-ios-native](../../software-ios-native/SKILL.md); this reference retains interaction decisions.

## Permission and purchase UX

- Request access when the feature makes its purpose clear, with specific copy and a useful denied-state path. A tracking pre-prompt must explain the request without incentives, pressure, or a misleading imitation of the system dialog. Design notification permission around the benefit the user chose, and provide preference controls.
- Default to a value preview before a purchase decision as a team product choice. A first-launch paywall is not automatically prohibited by Guideline 3.1.1. Show the offer, actual billing period, trial/renewal terms, and a clear exit where the product permits one; subscription and storefront eligibility checks belong to the release owner.
- Keep consent, purchase, and account-deletion controls discoverable in localized and accessibility layouts. Don't make refusal look like an error or bury it in decorative copy.

Read the applicable [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) when specifying the flow. Do not infer universal rejection or conversion rates from these design defaults.

## Toolbar overcrowding

Prioritize the task's main action and move less frequent actions into a labeled menu. A three-item toolbar is a team starting point, not a platform limit. Verify actual fit on the smallest supported width, translated labels, and large text; the smallest device currently sold is not the smallest device your app supports.

## Alerts and confirmation dialogs

Use an alert for critical information or a concise confirmation that needs immediate attention. Use a confirmation dialog for choices associated with an intentional action, such as selecting how to handle an item. Irreversible deletion can warrant an alert; destructive intent alone does not dictate the presentation. Check [Alerts](https://developer.apple.com/design/human-interface-guidelines/alerts) and [Action sheets](https://developer.apple.com/design/human-interface-guidelines/action-sheets) for the specific task.

## Navigation and dismissal

Preserve standard back navigation and edge-swipe behavior after any custom chrome change. Check horizontal paging for gesture conflicts, and test return paths rather than assuming a hidden system button preserves them. Navigation-stack implementation belongs to the native skill.

Allow sheet dismissal unless it would lose work without recovery. When blocking dismissal, provide a visible cancel/discard/save route. Choose detents by content and task: medium/large are common choices, not a requirement for every sheet. Verify drag dismissal, scroll/drag arbitration, large-title transitions, and compact adaptation on the target OS.

## Destructive swipe actions

A full swipe that permanently deletes content needs deliberate confirmation or a real undo path. Disable immediate destructive full swipe when recovery is unavailable. Confirm undo persists long enough for the task and accessibility users; no universal timeout guarantees that.

## Picker craft

Use a native picker when it expresses the choice clearly. Select wheel, menu, segmented, or another system presentation by option count, meaning, and available width. Test adjustment with VoiceOver and large text. A custom strip is justified only when it improves the task and provides equivalent semantics; ordering alone does not require a wheel.

## Store screenshots and previews

Use real, achievable app states with fictional data. Captions should explain the visible benefit without hiding the interface; frames and a particular screenshot count are optional design choices. Check that localization, price/offer copy, and the actual build agree. Preview videos should explain the task with the sound off and show real UI; look up current asset constraints through the release owner rather than storing them here.

## Review handoff

Provide before/after images tied to the build, meaningful populated and failure states, and the smallest supported layout with large text. Record intentional departures from system conventions and the task evidence for them. Carry the design decisions into the release checklist owned by software-mobile; a screenshot review does not prove store eligibility, privacy declarations, or runtime reliability.
