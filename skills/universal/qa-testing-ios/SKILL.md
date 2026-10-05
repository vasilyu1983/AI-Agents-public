---
name: qa-testing-ios
description: "Guides iOS testing with XCTest, XCUITest, Swift Testing, simctl, and xcresult. Use when choosing destinations, controlling flakes, or parsing test artifacts for native apps."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# QA Testing (iOS)

High-signal iOS test execution and flake control for XCTest, XCUITest, Swift Testing, `xcodebuild`, `xcresult`, and `simctl`.

Pair this skill with [software-ios-native](../software-ios-native/SKILL.md) when the work is part of a native iOS rewrite or a Codex / Claude Code implementation loop.

Core docs:
- https://developer.apple.com/documentation/xctest
- https://developer.apple.com/documentation/testing
- https://developer.apple.com/documentation/xcode/testing-your-apps-in-xcode
- https://developer.apple.com/documentation/xcode/simctl
- https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes

## Quick Reference

| Need | Go to |
|------|-------|
| Run the iOS test workflow | `## Workflow` |
| Load current defaults and command patterns | `## Defaults` and `## xcodebuild Patterns` |
| Control flakes and destinations | `## Flake Control` |
| Load templates and references | `## Navigation` |

## Release Validation Boundary

- Do not treat simulator green or archive green as full iOS release proof when the feature depends on distribution signing, real hardware, APNs, camera, biometrics, purchases, or background execution.
- For those cases, require the release path that matches production behavior: signed archive, beta/distribution channel validation where relevant, and a real-device user-visible outcome.
- Keep project-specific rollout procedures, backend endpoints, tester-account cleanup, and internal runbooks out of this portable core. Put them in project docs or scoped references.
- Use [references/ios-ci-general.md](references/ios-ci-general.md) for release-CI and archive-path checks, and [qa-testing-mobile/references/release-and-rollout.md](../qa-testing-mobile/references/release-and-rollout.md) for distribution-channel planning.

## Defaults

- New unit and integration tests: prefer Swift Testing unless the project is already standardized on XCTest.
- UI and performance tests: keep using XCTest/XCUITest.
- PR gate: thin simulator smoke coverage with `xcresult` artifacts always enabled.
- Release confidence: add a real-device pass only where hardware behavior matters.
- Flake posture: prove the flake first, then fix isolation, waits, or environment drift; retries are a debugging aid, not a success criterion.
- Locale, region, timezone, permissions, and app state must be explicit in automation.
- Cross-framework assertions can lose failures depending on interop mode. Never assume test discovery implies assertion compatibility; use the version-specific modes and CI checks in [references/swift-testing.md](references/swift-testing.md#xctest--swift-testing-interop-st-0021-swift-64).
- After adopting the iOS 26 SDK, compare existing snapshot baselines against Liquid Glass rendering and regenerate affected baselines. Review each diff before accepting.

## Inputs to Gather

- Xcode entrypoint: `-workspace` or `-project`
- `-scheme` and optional `-testPlan`
- Destination strategy: simulator, real device, or both
- Required hooks: launch arguments, launch environment, test data, auth bypass, animation toggles
- Artifact needs: `xcresult`, coverage, screenshots, logs, diagnostics
- CI environment: local, GitHub Actions, Xcode Cloud, or self-hosted macOS
- Whether the task first needs fresh uninstall/install/launch proof before trusting UI observations
- Whether the task includes distribution-channel or hardware-specific behavior that requires a real-device validation pass

## Quick Start

| Command | Purpose |
|---------|---------|
| `xcodebuild -list -workspace MyApp.xcworkspace` | List schemes |
| `xcodebuild -scheme MyApp -showdestinations` | Show valid destinations |
| `xcodebuild -scheme MyApp -showTestPlans` | Show available test plans |
| `xcrun xctrace list devices` | List physical and simulator devices |
| `xcrun simctl list devices available` | List available simulators |
| `xcrun simctl boot "<simulator-name>"` | Boot a simulator |
| `xcrun simctl bootstatus booted -b` | Wait for boot completion |
| `xcrun simctl uninstall booted <bundle-id>` | Remove stale installed app before a smoke pass |
| Persist booted UDID to `.simulator-udid` (gitignored) in the `select-simulator.sh` step | Stop scripts read this file back and call `xcrun simctl shutdown <UDID>` plus `xcrun simctl terminate <UDID> <bundle-id>` — terminating exactly the simulator that was booted. Replaces `pkill -f Simulator`, which shotguns unrelated dev / CI simulators. The UDID file is the contract between run and stop scripts. |
| `xcodebuild test -scheme MyApp -destination 'platform=iOS Simulator,name=<simulator-name>,OS=latest' -resultBundlePath TestResults.xcresult` | Run tests on a simulator |
| `xcodebuild test -scheme MyApp -destination 'platform=iOS,id=<UDID>' -resultBundlePath TestResults.xcresult` | Run tests on a device |
| `xcodebuild build-for-testing ...` then `xcodebuild test-without-building ...` | Faster reruns |
| `xcrun xcresulttool get test-results summary --path TestResults.xcresult` | Pass/fail and counts (`get test-results tests` for the tree). The deprecated object API requires `--legacy`; check `xcrun xcresulttool get object --help` for the selected Xcode |
| `xcodebuild ... -destination "generic/platform=iOS" build` | Compile-only build without a simulator; use when simulator services are unavailable or you only need compile/link proof |
| `xcodebuild archive -scheme MyApp -destination 'generic/platform=iOS' -archivePath MyApp.xcarchive` | Exercise the archive/signing path (produces an `.xcarchive`; `-exportArchive` makes the `.ipa`). Use before calling a release candidate ready |

## Workflow

- Resolve the build inputs first: workspace or project, scheme, test plan, destination, and required launch hooks.
- Make the environment repeatable: simulator boot, permissions, locale, region, and app state reset.
- If the task depends on whether the current binary is really on screen, do a fresh uninstall/install/launch smoke pass before interpreting screenshots or UI-test failures.
- If a simulator screenshot path is missing or expired, treat it as a tooling artifact, not as no evidence. Re-capture from the current simulator or use the reported visible symptom plus source inspection to choose the next focused check.
- If the task includes push, purchases, deep links, or other distribution-channel behavior, split transport proof from user-visible outcome proof and use a real-device pass when required.
- Keep compile, test, archive, install/launch, TestFlight, and user-journey evidence distinct. Record source revision, scheme/configuration, archive or app identity, destination/OS, exact test plan or selector, and result-bundle path; stop the release claim at the last observed stage.
- Run with artifacts enabled: `-resultBundlePath`, and add coverage or diagnostics only when they serve the task.
- Triage from `xcresult` first, then reproduce a single failing test with `-only-testing`.
- If CoreSimulatorService returns “Connection refused”, stop retrying the same destination; use `generic/platform=iOS` for compile-only proof and route service recovery to software-ios-runtime-debugging.
- For backend-coupled flows, exercise the account recreation, cache isolation and web/API parity checklist in [references/e2e-harness-and-selectors.md](references/e2e-harness-and-selectors.md).
- Treat rerun-pass as a flake that needs ownership and a root-cause fix.

## Runtime Proof Boundary

- Use this skill for test execution, `xcresult`, destinations, and flake control after the app is buildable and installable.
- If the core problem is stale installs, simulator drift, malformed `.app` bundles, missing executables, or install/launch failures, route to [software-ios-runtime-debugging](../software-ios-runtime-debugging/SKILL.md).
- If the app cannot be installed or launched reliably, that is a runtime-debugging problem first and a test problem second.
- A simulator or explicitly unsigned build does not exercise device signing. A development-signed device build can prove development signing for that destination, but does not prove distribution signing, export, TestFlight processing, or release-artifact installability. A green archive alone does not prove export, installation, or launch, and a simulator pass does not prove APNs, StoreKit, entitlements, background modes, camera, biometrics, or other device/channel behavior.

## xcodebuild Patterns

```bash
# Enumerate before an expensive run
xcodebuild test \
  -scheme MyApp \
  -testPlan Smoke \
  -destination 'platform=iOS Simulator,name=<simulator-name>,OS=latest' \
  -enumerate-tests \
  -test-enumeration-format json

# Target one test
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=<simulator-name>,OS=latest' \
  -only-testing:MyAppUITests/LoginFlowTests/testHappyPath \
  -resultBundlePath TestResults.xcresult

# Parallelize only when the suite is isolation-safe
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=<simulator-name>,OS=latest' \
  -parallel-testing-enabled YES \
  -maximum-parallel-testing-workers 4 \
  -resultBundlePath TestResults.xcresult

# Controlled retry for CI triage
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=<simulator-name>,OS=latest' \
  -retry-tests-on-failure \
  -test-iterations 2 \
  -test-repetition-relaunch-enabled YES \
  -collect-test-diagnostics on-failure \
  -resultBundlePath TestResults.xcresult

# Prove a flake locally
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=<simulator-name>,OS=latest' \
  -only-testing:MyAppUITests/LoginFlowTests/testHappyPath \
  -run-tests-until-failure \
  -test-iterations 25
```

## Flake Control

- Prefer `waitForExistence`, expectations, and state-based assertions over sleeps.
- Disable or reduce animations in UI-test runs where the app allows it.
- Stub or redirect third-party boundaries; do not depend on live external services in UI tests.
- Reset permissions and app state between tests.
- Pin `-testLanguage` and `-testRegion` when locale affects assertions.
- Use test plans for matrix-style coverage across device classes, locales, and environments.
- Keep UI suites thin. Put most business logic coverage in lower layers.
- For multi-locale apps, use [qa-testing-mobile/references/localization-testing.md](../qa-testing-mobile/references/localization-testing.md) for layered coverage.

## Localization and Visual Regression Proof

- Missing-key crashes in string-catalog or generated-accessor lookups are testable defects, not acceptable runtime assertions. Add or run catalog coverage before returning to UI polish.
- Verify both key presence and translated value quality. A locale file containing the English fallback is still a failed localization gate for user-visible copy.
- When new UI copy is added for a feature, run a focused key/value check for the new keys across every shipped locale, then run the broader static-key coverage suite.
- Pair locale coverage with narrow-width visual smoke for high-risk locales such as German, Russian, Japanese, and Arabic. Container width, wrapping, and overlay occlusion are part of the localization test, not a separate design nicety.
- For dense data-visualization screens, include a targeted smoke pass that proves controls, help/info cards, and detail affordances do not cover the primary diagram and remain usable after zoom/filter changes.

## Deterministic E2E Harness

For auth, onboarding, billing, and other backend-coupled flows, prefer a fixture-backed launch-environment harness over live credentials. Keep user variants explicit, keep the fixture branch in the same function as the real path, and treat `.accessibilityIdentifier()` strings as part of the test contract.

Load [references/e2e-harness-and-selectors.md](references/e2e-harness-and-selectors.md) for:

- the canonical launch-environment fixture pattern
- harness rules and reset-hook discipline
- selector rules for identifiers vs labels
- the atomic-commit pattern for landing a new E2E suite
- multi-account and backend-parity edge cases

## Test Plan Organization

Xcode test plans (`.xctestplan`) control which tests run, with what configuration, and in which environment. Use them to manage matrix-style test execution:

- **Smoke plan**: thin critical-path tests for PR gates. Fast, reliable, minimal device matrix.
- **Full plan**: complete unit + integration + UI suite for nightly or release-candidate runs.
- **Locale plan**: same UI tests with different `-testLanguage` / `-testRegion` overrides per configuration.
- Keep test plans in the project directory alongside the scheme. Reference via `-testPlan PlanName` in xcodebuild.
- Each configuration within a plan can override launch arguments, environment variables, and enabled tests independently.
- Prefer separate plans over complex multi-configuration single plans — easier to run, triage, and maintain.

## AI-Agent Testing for iOS

AI-native test tools (Maestro MCP and others) complement XCUITest; keep deterministic PR-gate smoke in XCUITest. For tool positioning and the decision framework, load [qa-testing-mobile/references/ai-native-testing.md](../qa-testing-mobile/references/ai-native-testing.md). Vendor capability claims change quickly — verify them against the vendor's current docs before recommending one.

## When NOT To Use

| Scenario | Use Instead |
|----------|-------------|
| Product architecture, app implementation, SwiftUI rewrite, or Xcode agent workflow | [software-ios-native](../software-ios-native/SKILL.md) |
| Build/install failures, stale app suspicion, bundle executable missing, or simulator/package debugging | [software-ios-runtime-debugging](../software-ios-runtime-debugging/SKILL.md) |
| Cross-platform mobile test strategy | [qa-testing-mobile](../qa-testing-mobile/SKILL.md) |
| Release-wide quality strategy | [qa-testing-strategy](../qa-testing-strategy/SKILL.md) |

## Resources

| Resource | Purpose |
|----------|---------|
| [references/e2e-harness-and-selectors.md](references/e2e-harness-and-selectors.md) | Deterministic fixture harnesses, selector discipline, and E2E landing rules |
| [references/swift-testing.md](references/swift-testing.md) | Swift Testing assertions, traits, confirmations, SDK-dependent features, and XCTest migration |
| [references/xctest-patterns.md](references/xctest-patterns.md) | XCTest patterns for unit, integration, and performance tests |
| [references/xcuitest-patterns.md](references/xcuitest-patterns.md) | XCUITest authoring and flake control |
| [references/simulator-commands.md](references/simulator-commands.md) | Current `simctl` commands worth using in automation |
| [references/snapshot-testing-ios.md](references/snapshot-testing-ios.md) | Snapshot testing with current caveats |
| [references/ios-ci-general.md](references/ios-ci-general.md) | Provider-neutral iOS CI guidance, including archive-path and fresh-clone checks |
| [references/ios-ci-github-actions.md](references/ios-ci-github-actions.md) | GitHub Actions specifics and runner drift checks |
| [references/ios-version-and-vision-pro.md](references/ios-version-and-vision-pro.md) | iOS 26 Liquid Glass snapshot impact, visionOS 26 destination syntax, Reality Composer Pro asset testing, hand-tracking simulator limits |
| [../qa-testing-mobile/references/localization-testing.md](../qa-testing-mobile/references/localization-testing.md) | Layered localization coverage for mobile UI and backend-served content |
| [../qa-testing-accessibility/SKILL.md](../qa-testing-accessibility/SKILL.md) | Accessibility-specific QA gates, screen-reader coverage, and conformance boundary guidance |
| [data/sources.json](data/sources.json) | Curated external references |

## Scripts

| Script | Purpose |
|--------|---------|
| [scripts/xcresult_to_junit.py](scripts/xcresult_to_junit.py) | Convert `.xcresult` to JUnit XML (Xcode 16+, fixtures from Xcode 27; stdlib only). Counts `Test Case` nodes, reads failures from their children, and exits 4 if its counts disagree with `xcresulttool get test-results summary`. Regression test: `python3 -m unittest discover -s scripts/tests` |
| [scripts/README.md](scripts/README.md) | Usage guide and CI integration examples (GitHub Actions, Bitrise) |

## Templates

| Template | Purpose |
|----------|---------|
| [assets/template-ios-ui-test-stability-checklist.md](assets/template-ios-ui-test-stability-checklist.md) | Review checklist for UI-test determinism |

## Navigation

- `## Workflow`, `## xcodebuild Patterns`, and `## Flake Control` for the baseline sequence
- `## Resources` and `## Templates` for deeper materials

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
