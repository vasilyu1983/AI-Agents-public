# Mobile Release Readiness Checklist

Pre-release validation checklist for iOS and Android apps.

## Build and Signing

- [ ] Build signed with production certificate
- [ ] App version and build number incremented
- [ ] Bundle ID / package name correct for production
- [ ] Entitlements and capabilities configured correctly
- [ ] ProGuard/R8 obfuscation enabled (Android)
- [ ] Third-party SDK versions reviewed (crash/analytics/ads)

## Functional Testing

- [ ] All critical user journeys pass on release build
- [ ] Smoke test suite passes (login, core features, checkout)
- [ ] Deep links and universal links work
- [ ] Push notifications deliver and open correctly
- [ ] In-app purchases complete successfully
- [ ] Analytics events fire correctly

## Stability

- [ ] Crash-free rate meets threshold (target: 99.5%+)
- [ ] No new crashes in beta/TestFlight testing
- [ ] Memory usage within acceptable limits
- [ ] No memory leaks detected in critical flows
- [ ] App launch time within target (<2s cold start)
- [ ] Android ANR rate within SLO (if tracked)

## Device Coverage

- [ ] Tested on minimum supported OS version
- [ ] Tested on smallest supported screen size
- [ ] Tested on largest supported screen size
- [ ] Tested on tablet if supported
- [ ] Tested on low-end device representative

## Network and Offline

- [ ] Offline mode works correctly
- [ ] Poor network (2G/3G) handling verified
- [ ] Network transitions (WiFi to cellular) handled
- [ ] API timeout handling tested
- [ ] Retry logic works for transient failures

## Permissions and Privacy

- [ ] All permission prompts display correctly
- [ ] Permission denial handled gracefully
- [ ] Privacy manifest updated (iOS)
- [ ] Required-reason APIs (iOS) documented and justified
- [ ] Data collection disclosure accurate
- [ ] GDPR/CCPA consent flows work

## Platform-Specific (iOS)

- [ ] App Transport Security exceptions documented
- [ ] Background modes configured correctly
- [ ] App Tracking Transparency prompt if needed
- [ ] Sign in with Apple compliance (if any third-party login)
- [ ] Widget extensions work if applicable
- [ ] Watch app syncs if applicable

## Platform-Specific (Android)

- [ ] Target SDK meets Play Store requirements
- [ ] Adaptive icons display correctly
- [ ] Split APKs / App Bundle configured
- [ ] Battery optimization handling tested
- [ ] Accessibility services compatibility checked
- [ ] Play Console Data safety form reviewed (if applicable)
- [ ] App links verified (Android App Links / Digital Asset Links)

## Store Metadata

- [ ] Screenshots updated for new features
- [ ] App description updated
- [ ] What's New / Release Notes drafted
- [ ] Keywords and categories reviewed
- [ ] Privacy policy URL valid
- [ ] Support URL valid
- [ ] App Review / Play review notes include required test credentials (if needed)

## Rollout Plan

- [ ] Staged rollout percentage defined (5% -> 20% -> 50% -> 100%)
- [ ] Rollback plan documented
- [ ] Monitoring dashboards ready
- [ ] On-call schedule confirmed
- [ ] Hotfix process documented

## Sign-Off

| Role | Name | Date | Approved |
|------|------|------|----------|
| QA Lead | | | [ ] |
| Dev Lead | | | [ ] |
| Product Owner | | | [ ] |
| Release Manager | | | [ ] |
