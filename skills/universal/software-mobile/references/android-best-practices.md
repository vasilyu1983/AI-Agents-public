# Native Android Handoff

Load this when a platform-selection task turns into native Android work. Implementation facts have one owner:

| Need | Owner |
|------|-------|
| Architecture, Compose state, coroutines, networking, persistence and release pipelines | [software-android-native](../../software-android-native/SKILL.md) |
| Gradle/build/install/launch proof, crashes, ANRs and profiling | [software-android-runtime-debugging](../../software-android-runtime-debugging/SKILL.md) |
| Material design, visual review and accessibility design | [software-android-design](../../software-android-design/SKILL.md) |
| Unit/UI tests and device proof | [qa-testing-android](../../qa-testing-android/SKILL.md) |
| Secure storage and mobile threat modeling | [software-security-appsec](../../software-security-appsec/SKILL.md) |

Keep platform-choice tradeoffs and shared auth, push, deep links and store-policy decisions in [software-mobile](../SKILL.md). Handoff native SDK dependencies, target/minimum API requirements, lifecycle constraints and signing/distribution needs rather than copying implementation defaults here.
