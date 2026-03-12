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

### Assets

- [ ] App icons (all required sizes)
- [ ] Screenshots (all device sizes)
- [ ] Preview video (optional)
- [ ] App description and keywords updated

### Compliance

- [ ] Privacy policy URL valid
- [ ] Terms of service URL valid
- [ ] Age rating questionnaire completed
- [ ] Export compliance documentation (if applicable)

### Testing

- [ ] TestFlight/Internal testing complete
- [ ] Beta feedback addressed
- [ ] Regression test on release candidate

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
