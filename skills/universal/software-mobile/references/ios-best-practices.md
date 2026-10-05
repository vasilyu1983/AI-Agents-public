# Native iOS Handoff

Load this when a platform-selection task turns into native iOS work. Implementation facts have one owner:

| Need | Owner |
|------|-------|
| Architecture, SwiftUI state, concurrency, networking, persistence and release pipelines | [software-ios-native](../../software-ios-native/SKILL.md) |
| Build/install/launch proof, stale artifacts, crashes and profiling | [software-ios-runtime-debugging](../../software-ios-runtime-debugging/SKILL.md) |
| HIG, visual review and accessibility design | [software-ios-design](../../software-ios-design/SKILL.md) |
| Unit/UI tests and device proof | [qa-testing-ios](../../qa-testing-ios/SKILL.md) |
| Secure storage and mobile threat modeling | [software-security-appsec](../../software-security-appsec/SKILL.md) |

Keep platform-choice tradeoffs and shared auth, push, deep links and store-policy decisions in [software-mobile](../SKILL.md). Handoff the chosen minimum OS, native capabilities, lifecycle requirements and release constraints rather than copying implementation defaults here.
