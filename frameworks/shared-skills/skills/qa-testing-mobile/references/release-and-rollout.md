# Mobile Release And Rollout

Beta-channel validation and rollout controls are part of mobile QA, not a separate afterthought.

## Use This Reference For

- Pre-release beta validation
- Store-side automated checks
- Staged rollout planning
- Rollback trigger design

## iOS Beta Flow

- Use TestFlight for internal and external beta validation before broad release.
- Define beta exit criteria before uploading the candidate build.
- Track crash, auth, payments, onboarding, and push/deep-link regressions during the soak window.

Beta exit criteria should usually include:

- No open P0/P1 regressions
- Crash-free and key-flow metrics within guardrails
- Support/review team aware of the release scope and known issues

## Android Pre-Release Flow

- Use Google Play testing tracks and review pre-launch reports when they are part of the release path.
- Treat store-side automated findings as triage input, then confirm locally on representative devices.
- Keep Play-only checks additive to your own CI/device-cloud gates.

## Staged Rollout Defaults

- Roll out in defined increments instead of 100% immediately.
- Attach owners and thresholds to each increment.
- Prefer explicit rollback triggers over ad-hoc judgment.

Common rollback triggers:

- Crash or ANR spike
- Authentication or payment failures
- Material drop in activation or conversion
- Region-specific device regressions on top cohorts

## iOS pre-submission verification gates

Three quality checks to run before uploading any iOS archive. Each catches a common "works on my machine, broken on the store" failure class:

- **Fresh-clone CI gate.** Before merging a release branch, run the full archive step in a clean checkout (`git clone --depth 1 <origin> /tmp/fresh && cd /tmp/fresh && bash ci_scripts/ci_post_clone.sh && xcodebuild archive …`). Catches files that are present locally but never committed, gitignored folders with partially-tracked files, and generators that silently depend on a sibling repo.
- **Entitlement-parity check.** After archiving, run `codesign -d --entitlements - /path/to/<App>.app` and confirm every `com.apple.developer.*` key in the output corresponds to a capability enabled on the App ID in Apple Developer → Identifiers. A `.entitlements` key with no matching App ID capability causes an Archive failure at upload; a capability enabled on the App ID but not in `.entitlements` is harmless but indicates drift. Run this before TestFlight upload, not after.
- **Per-device APNs environment check.** Local `Xcode → Run` builds register with APNs **sandbox**; TestFlight and App Store builds register with APNs **production**. If your backend records the environment per device, verify a given physical device flips correctly between `sandbox` (on local install) and `production` (on TestFlight install). A device row persisted with the wrong `environment` string silently drops every push because the backend sends to the wrong APNs gateway. Verify before running any TestFlight push-validation, not after.

See also [`app-store-connect-checklist.md → Phase 6-7`](../../software-mobile/references/app-store-connect-checklist.md) for the full submission workflow and [`ios-ci-general.md → Release-CI on top of test-CI`](../../qa-testing-ios/references/ios-ci-general.md) for Xcode Cloud specifics.

## App Install Race Conditions in CI

Concurrent CI runs that install an app to the same simulator or device slot can produce queue failures that look like test failures.

**Root causes:**

- Two jobs target the same simulator UDID simultaneously; the second `xcrun simctl install` arrives before the first boot cycle completes.
- `adb install` races against a device that is mid-reboot or still mounting a previous install; a partial install corrupts the package manifest and causes launch failures that are not retried.
- Incremental installs (`adb install` without `--no-incremental`) leave stale dex/odex caches that misidentify a clean install as having prior state.

**Mitigations:**

- Use `adb install -r --no-incremental <apk>` for every CI install. `-r` replaces any existing install; `--no-incremental` forces a full package push, preventing cache poisoning from prior runs on shared devices.
- For iOS, boot the simulator before installing: `xcrun simctl boot <udid> && xcrun simctl install booted <app.app>`. Do not call `install` before the simulator reaches `Booted` state.
- Verify install before launching: poll `adb shell pm path <package>` (non-empty output = installed) or check `xcrun simctl listapps booted | grep <bundle-id>` before invoking the test runner.
- In GitHub Actions or other CI platforms with matrix jobs, pin each matrix leg to a distinct simulator UDID or a dedicated emulator AVD name. Never share a simulator slot across parallel jobs in the same workflow.
- Make test entry points idempotent: tests should not assume a clean install state unless the harness explicitly uninstalls first. Use `adb uninstall <package> || true` or `xcrun simctl uninstall booted <bundle-id>` at the start of the job, not the end, so interrupted runs clean up on next entry.

**Detection:** A queued install failure typically surfaces as "Unable to launch" or `ActivityNotFoundException` on Android, or `Failed to install the requested application` on iOS — before any test code runs. If these errors appear only on parallel CI runs but not local runs, install sequencing is the likely cause.

## Release-Train Cadence and Testing Scope

Mobile release trains are fundamentally different from continuous web deploys: a rejected or buggy build cannot be silently rolled back once users have it installed, and store review adds latency you cannot bypass. Match testing depth to train cadence rather than running the same test scope every cycle:

| Cadence | Typical fit | Testing scope implication |
|---|---|---|
| Weekly train | High-velocity consumer apps with strong feature-flag discipline | Full regression must complete within days, not weeks — invest early in parallelized device-farm runs and a tight flake budget, since there is no slack to chase flakes between trains |
| Biweekly / 3-week train | Most product teams; common default | Standard cadence for the workflow in this skill: smoke on every PR, full regression pre-branch-cut, beta soak of several days, staged rollout over the remaining days |
| Monthly+ train | Regulated, enterprise, or low-change-tolerance apps | More time for exploratory and accessibility passes, but also more risk accumulated per release — consider an accelerated hotfix train as a separate, lighter-weight path so P0 fixes do not wait for the next full cycle |

**Judgment calls a cadence table cannot make for you:**

- **Feature flags decouple code-ship from feature-ship.** If most new behavior ships dark behind a flag and is enabled server-side after the fact, the release train's *test* scope can stay narrow (does the build install and run safely) while the *feature* validation happens separately, on-demand, when the flag flips. Conflating "the build shipped" with "the feature is validated" is a common mistake that leads to over-testing every train.
- **A hotfix path is not optional past a certain size.** Any team shipping a mobile app to real users needs a lighter-weight emergency train (skip the full regression matrix, run only the smoke suite + the specific regression under fix + a signing/entitlement check) that can reach TestFlight/Play within hours, not the normal cycle's days. Without one, a P0 crash sits in production for the length of a full train.
- **Train length should track store review latency, not just internal test time.** If review adds 1-2 unpredictable days, build that slack into the train's exit date, not the rollout's start date — teams that forget this end up either rushing final QA or missing the intended ship date.

## Monitoring Checklist

- Crash dashboard and alert thresholds ready
- Key funnel metrics visible by app version
- Feature-flag or remote-config kill switch identified where available
- Hotfix ownership and decision path documented

## Primary Sources

- Apple TestFlight docs
- Google Play pre-launch report docs
- Verify current rollout controls and store behavior with official docs before citing them
