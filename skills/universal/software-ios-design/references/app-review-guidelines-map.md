# App Store Review Guidelines — Design-Facing Map

Use the live [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) when the proposed UI changes moderation, consent, payment, or public claims. These checks inform design; they do not establish release approval. Submission mechanics and full policy eligibility belong to [software-mobile](../../software-mobile/SKILL.md), including its [App Store Connect checklist](../../software-mobile/references/app-store-connect-checklist.md).

## Moderation and safety UI

For UGC/social features under 1.2, provide filtering, reporting, blocking, and a published contact route. Reports need **timely** responses; Apple does not specify a universal 24-hour deadline in 1.2. Verify that the report/block paths can be found and completed, including under VoiceOver. Moderation operations belong to the release/compliance owner.

For AI content, separate UGC/shared-content obligations from private generation. Do not infer that every private model response is automatically UGC under 1.2. Design intelligible refusal and reporting paths for the actual feature; consult [software-ios-ai-engine](../../software-ios-ai-engine/SKILL.md) for generation controls.

## Accurate representations

Screenshots and previews should reflect achievable app behavior with fictional data, consistent with 2.3. Check subscription offer copy against the actual products and terms before capturing screenshots. Do not treat a value-preview recommendation as a blanket 3.1.1 ban on first-launch paywalls.

## 4.3 / 4.2 — the "do not build this way" gate

Compare the concept with existing apps before refining visual polish. A saturated-category entry needs visible differentiation; a cosmetic reskin does not demonstrate useful native functionality. Read the live 4.2/4.3 text for named categories and submission exceptions. Show the reviewer the task that benefits from this app's interaction, personalization, or other distinct capability. Do not promise that any checklist of features guarantees acceptance.

## Live Activities and notifications

Under 4.5.3, Apple services must not become spam or unsolicited messaging surfaces. Keep a Live Activity centered on the user's ongoing task. For promotional notifications, read 4.5.4's separate consent/opt-out requirements; don't equate all authorized notification types with Live Activity content.

## Login, consent, and deletion

When third-party/social login triggers 4.8, design the required equivalent privacy option and check the rule's exceptions. Sign in with Apple is one way to provide that option; the app's own email/password system alone does not automatically trigger it.

Make purpose-specific permission copy, consent withdrawal, and applicable account deletion discoverable. For personal data shared with third-party AI, read 5.1.2(i) before designing the disclosure and permission flow. UI evidence must match the data path implemented by the owning native/AI skill.

## Design handoff

- Record moderation, consent, purchase, and deletion interactions that the release owner must verify.
- Show the real task and distinct value in the reviewed UI.
- Check localized screenshot copy against the built experience.
- Load [ios-shipping-antipatterns.md](ios-shipping-antipatterns.md) for navigation, dialog, swipe, and prompt UX decisions.
