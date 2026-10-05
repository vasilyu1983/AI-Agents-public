# Mobile Release Readiness Checklist

**App**: [Name]
**Version**: [X.Y.Z]
**Platform**: iOS / Android / Both
**Release Date**: YYYY-MM-DD

---

## Standards (Core)

- Clean code standard (single source of truth): [../../references/clean-code-standard.md](../../references/clean-code-standard.md)
- Review comments: if feedback is primarily about clean code, cite `CC-*` IDs; do not restate the standard.

## Pre-Release (Core)

### Code Quality

- [ ] All tests passing (unit, integration, UI)
- [ ] No critical or high-severity bugs open
- [ ] Code review completed for all changes
- [ ] Static analysis clean (SwiftLint/detekt)

### iOS Specific

- [ ] Privacy manifest updated (app + third-party SDKs) https://developer.apple.com/documentation/bundlereferences/privacy_manifest_files
- [ ] Required-reason APIs declared with approved justifications https://developer.apple.com/documentation/bundlereferences/privacy_manifest_files
- [ ] App Transport Security configured (or exceptions documented) https://developer.apple.com/documentation/bundlereferences/information_property_list/nsapptransportsecurity
- [ ] Minimum deployment target and device matrix are documented and tested [Inference]

### Android Specific

- [ ] Target SDK meets Google Play target API requirements https://support.google.com/googleplay/android-developer/answer/11926878
- [ ] Data safety form updated
- [ ] ProGuard/R8 rules tested
- [ ] 64-bit APK/AAB included

### Performance

- [ ] Cold start performance meets product SLO (measure on low-end device) [Inference]
- [ ] Memory usage within budget
- [ ] No battery drain issues
- [ ] Network calls optimized (batching, caching)

### Security

- [ ] Sensitive data in Keychain/Keystore only
- Baseline `CC-*` to apply (cite IDs if violated): `CC-SEC-03`
- [ ] Android: R8/ProGuard enabled and verified (release builds) [Inference]
- [ ] Certificate pinning used only with rotation strategy and fail-open/fail-closed decision documented [Inference]

---

## App Store Submission

For the comprehensive field-by-field App Store Connect walkthrough (metadata, privacy declarations, age rating, subscriptions, screenshots, agreements, TestFlight, and review preparation), see [../../../software-mobile/references/app-store-connect-checklist.md](../../../software-mobile/references/app-store-connect-checklist.md).

### Assets

- [ ] App icons (1024×1024 in asset catalog — Xcode auto-generates all sizes and uploads with the build)
- [ ] Screenshots for all required device classes (iPhone 6.7", 6.5"; iPad 12.9" if supporting iPad)
- [ ] Marketing text overlays and device frames for professional appearance
- [ ] Preview video (optional)
- [ ] App description, keywords, subtitle, and promotional text updated

### Compliance

- [ ] Privacy policy URL valid and publicly accessible
- [ ] Terms of service URL valid
- [ ] Age rating questionnaire completed
- [ ] App Privacy data collection declarations completed and published
- [ ] Export compliance documentation (if applicable)

### Subscriptions (if applicable)

- [ ] Subscription group and products created in App Store Connect
- [ ] Localized display names and descriptions for each product
- [ ] Review screenshot uploaded for each product
- [ ] App Store Server Notifications URL configured (v2)
- [ ] "Missing Metadata" status cleared on all products

### Agreements & Finance

- [ ] Paid Apps Agreement accepted
- [ ] Tax information completed
- [ ] Banking information completed

### Testing

- [ ] TestFlight/Internal testing complete
- [ ] Beta feedback addressed
- [ ] Regression test on release candidate
- [ ] Push notifications verified on TestFlight build (production APNs)
- [ ] Sandbox purchase flow verified on physical device

---

## Post-Release

- [ ] Monitoring dashboards configured
- [ ] Crash reporting active (Crashlytics, Sentry)
- [ ] Analytics tracking verified
- [ ] Rollback plan documented

---

## Optional: AI/Automation Section

> Include only for apps shipping AI/automation features.

- [ ] iOS: Apple Foundation Models integration tested (on-device behavior, privacy expectations) https://developer.apple.com/documentation/foundationmodels
- [ ] Android: ML Kit integration tested (offline/online behavior, performance) https://developers.google.com/ml-kit
- [ ] Model size, startup impact, and memory budget verified [Inference]
- [ ] AI feature degradation is graceful (timeouts, cancel, fallback) [Inference]
