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
- https://developer.apple.com/documentation/xcode-release-notes/xcode-26-release-notes

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
- XCTest interop with Swift Testing is off by default in Xcode 26. If CI shows unexpected test-count drops after upgrading, set `SWIFT_TESTING_XCTEST_INTEROP_MODE=limited` in your test plan environment.
- Snapshot baselines recorded before iOS 26 must be regenerated after adopting the iOS 26 SDK due to Liquid Glass visual changes. Review each diff before accepting.

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
| `xcrun xcresulttool get --path TestResults.xcresult --format json` | Inspect results programmatically |
| `xcodebuild ... -destination "generic/platform=iOS" build` | Compile-only build without a simulator | Use when simulator services are unavailable or you only need compile/link proof |
| `xcodebuild archive -scheme MyApp -destination 'generic/platform=iOS'` | Exercise archive/signing path | Use before calling a release candidate ready |

## Workflow

- Resolve the build inputs first: workspace or project, scheme, test plan, destination, and required launch hooks.
- Make the environment repeatable: simulator boot, permissions, locale, region, and app state reset.
- If the task depends on whether the current binary is really on screen, do a fresh uninstall/install/launch smoke pass before interpreting screenshots or UI-test failures.
- If a simulator screenshot path is missing or expired, treat it as a tooling artifact, not as no evidence. Re-capture from the current simulator or use the reported visible symptom plus source inspection to choose the next focused check.
- If the task includes push, purchases, deep links, or other distribution-channel behavior, split transport proof from user-visible outcome proof and use a real-device pass when required.
- Run with artifacts enabled: `-resultBundlePath`, and add coverage or diagnostics only when they serve the task.
- Triage from `xcresult` first, then reproduce a single failing test with `-only-testing`.
- Treat rerun-pass as a flake that needs ownership and a root-cause fix.

## Runtime Proof Boundary

- Use this skill for test execution, `xcresult`, destinations, and flake control after the app is buildable and installable.
- If the core problem is stale installs, simulator drift, malformed `.app` bundles, missing executables, or install/launch failures, route to [software-ios-runtime-debugging](../software-ios-runtime-debugging/SKILL.md).
- If the app cannot be installed or launched reliably, that is a runtime-debugging problem first and a test problem second.

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

## Localization and Visual Regression Proof

- Missing-key crashes such as `LocalizationStore.text` / generated-catalog lookups are testable defects, not acceptable runtime assertions. Add or run catalog coverage before returning to UI polish.
- Verify both key presence and translated value quality. A locale file containing the English fallback is still a failed localization gate for user-visible copy.
- When new UI copy is added for a feature, run a focused key/value check for the new keys across every shipped locale, then run the broader static-key coverage suite.
- Pair locale coverage with narrow-width visual smoke for high-risk locales such as German, Russian, Japanese, and Arabic. Container width, wrapping, and overlay occlusion are part of the localization test, not a separate design nicety.
- For dense chart or diagram screens, include a targeted smoke pass that proves controls, help/info cards, and detail affordances do not cover the primary diagram and remain usable after zoom/filter changes.

## Deterministic E2E Harness

For auth, onboarding, billing, referral, and other backend-coupled flows, prefer a fixture-backed launch-environment harness over live credentials. Keep user variants explicit, keep the fixture branch in the same function as the real path, and treat `.accessibilityIdentifier()` strings as part of the test contract.

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

AI-native tools now generate, execute, and maintain iOS UI tests with minimal manual scripting. Use them as a complement to XCUITest, not a replacement.

Current positioning:

- `Maestro + MaestroGPT + Maestro MCP`: fast smoke and onboarding flow authoring
- `TestSprite`: self-healing AI-owned test generation and maintenance
- `Drizz`: visual validation for design-heavy iOS apps

### When to use AI-native vs XCUITest

| Scenario | Use |
|----------|-----|
| PR gate smoke tests (fast, deterministic) | XCUITest |
| Broad flow coverage with low authoring effort | Maestro + MaestroGPT |
| Self-healing test maintenance | TestSprite or Appium MCP |
| Visual correctness validation | Drizz |
| Deep state/network assertions | XCUITest |
| Release-candidate E2E sweep | Drizz + real device matrix |

For fuller tool coverage, MCP integration patterns, and the decision framework, load [qa-testing-mobile/references/ai-native-testing.md](../qa-testing-mobile/references/ai-native-testing.md).

## When To Use

- Choosing the right iOS test layer
- Running or debugging XCTest, XCUITest, or Swift Testing from CLI
- Stabilizing flaky UI tests
- Parsing `xcresult` bundles and deciding the next reproduction step
- Setting up or reviewing iOS test execution in CI
- Acting as the testing and evidence layer for a native iOS rewrite
- Proving a fresh uninstall/install/launch smoke loop before trusting UI-test observations
- Evaluating AI-native testing tools for iOS (Maestro MCP, TestSprite, Drizz)

## When NOT To Use

| Scenario | Use Instead |
|----------|-------------|
| Product architecture, app implementation, SwiftUI rewrite, or Xcode agent workflow | [software-ios-native](../software-ios-native/SKILL.md) |
| Build/install failures, stale app suspicion, bundle executable missing, or simulator/package debugging | [software-ios-runtime-debugging](../software-ios-runtime-debugging/SKILL.md) |
| Cross-platform mobile test strategy | [qa-testing-mobile](../qa-testing-mobile/SKILL.md) |
| Release-wide quality strategy | [qa-testing-strategy](../qa-testing-strategy/SKILL.md) |

## Do / Avoid

### Do

- Use `waitForExistence` and expectations over sleeps
- Pin `-testLanguage` and `-testRegion` when locale affects assertions
- Reset permissions and app state between tests
- Keep UI suites thin; push business logic coverage to lower layers
- Capture `-resultBundlePath` artifacts for every CI run
- Use `generic/platform=iOS` destination when simulator service is crashed or unavailable — validates Swift compilation without requiring a running simulator
- Test `Codable` decoders with hand-crafted JSON payloads for missing, null, and unexpected fields — especially for API response models where the backend has evolved. Use `JSONDecoder().decode(T.self, from: json)` with minimal payloads that omit optional fields and payloads that include unknown keys. Focus on fields the backend has changed or may omit.
- Add explicit localization coverage when the app ships multiple locales; use [qa-testing-mobile/references/localization-testing.md](../qa-testing-mobile/references/localization-testing.md) for the layered pattern.
- Add a release-path real-device pass when the feature depends on APNs, purchases, camera, biometrics, or background execution.

### Avoid

- Depending on live external services in UI tests
- Using retries as a success criterion; treat rerun-pass as a flake signal
- Inflating global timeouts instead of fixing root-cause flakiness
- Running full UI suites on every PR when smoke coverage is sufficient
- Do not retry xcodebuild with the same simulator destination when CoreSimulatorService returns "Connection refused" — switch to generic iOS destination instead
- Keeping project-specific release runbooks, backend QA endpoints, or tester-account cleanup steps in this shared skill

### Backend-Coupled Edge Cases

- Exercise multi-account and backend-parity scenarios before calling a backend-heavy flow "stable".
- Typical checks: onboarding after account recreation, cache leakage across sign-out/sign-in, web-vs-API tier parity, OTP confirmation flow behavior, Apple Sign-In on a physical device, and hybrid email-template parity.
- Use [references/e2e-harness-and-selectors.md](references/e2e-harness-and-selectors.md) for the concrete scenario checklist.

## Resources

| Resource | Purpose |
|----------|---------|
| [references/e2e-harness-and-selectors.md](references/e2e-harness-and-selectors.md) | Deterministic fixture harnesses, selector discipline, and E2E landing rules |
| [references/swift-testing.md](references/swift-testing.md) | Comprehensive Swift Testing: assertions, parameterized tests, tags, traits, async patterns, confirmations, Swift 6.2 features, Xcode 26 additions (image attachments, severity levels, XCTest interop change), and XCTest migration |
| [references/xctest-patterns.md](references/xctest-patterns.md) | XCTest patterns for unit, integration, and performance tests |
| [references/xcuitest-patterns.md](references/xcuitest-patterns.md) | XCUITest authoring and flake control |
| [references/simulator-commands.md](references/simulator-commands.md) | Current `simctl` commands worth using in automation |
| [references/snapshot-testing-ios.md](references/snapshot-testing-ios.md) | Snapshot testing with current caveats |
| [references/ios-ci-general.md](references/ios-ci-general.md) | Provider-neutral iOS CI guidance, including archive-path and fresh-clone checks |
| [references/ios-ci-github-actions.md](references/ios-ci-github-actions.md) | GitHub Actions specifics and runner drift checks |
| [references/ios-ci-optimization.md](references/ios-ci-optimization.md) | Compatibility index for the CI reference split |
| [references/ios-version-and-vision-pro.md](references/ios-version-and-vision-pro.md) | iOS 26 Liquid Glass snapshot impact, iOS 18 predictive back and Apple Intelligence testing, visionOS 26 destination syntax, Reality Composer Pro asset testing, hand-tracking simulator limits |
| [../qa-testing-mobile/references/localization-testing.md](../qa-testing-mobile/references/localization-testing.md) | Layered localization coverage for mobile UI and backend-served content |
| [../qa-testing-accessibility/SKILL.md](../qa-testing-accessibility/SKILL.md) | Accessibility-specific QA gates, screen-reader coverage, and conformance boundary guidance |
| [data/sources.json](data/sources.json) | Curated external references |

## Scripts

| Script | Purpose |
|--------|---------|
| [scripts/xcresult_to_junit.py](scripts/xcresult_to_junit.py) | Convert `.xcresult` bundle to JUnit XML for CI publishing (Xcode 16+, stdlib only) |
| [scripts/README.md](scripts/README.md) | Usage guide and CI integration examples (GitHub Actions, Bitrise) |

## Templates

| Template | Purpose |
|----------|---------|
| [assets/template-ios-ui-test-stability-checklist.md](assets/template-ios-ui-test-stability-checklist.md) | Review checklist for UI-test determinism |

## ASCII Flow

```text
iOS testing request
  -> Classify layer: Swift Testing, XCTest, XCUITest, snapshot, or release smoke
  -> Pick exact scheme, destination, simulator/device, OS, and runner mode
  -> Stabilize fixtures, accessibility identifiers, permissions, and time/locale
  -> Run the smallest targeted test or xcresult-producing command
  -> Parse artifacts, screenshots, logs, and xcresult failures
  -> Widen to CI, matrix, or release gate only after targeted evidence is green
```

## Navigation

- `## Workflow`, `## xcodebuild Patterns`, and `## Flake Control` for the baseline sequence
- `## Resources` and `## Templates` for deeper materials
- `## Related Skills` for mobile QA and native-platform handoffs

## Related Skills

| Skill | Purpose |
|-------|---------|
| [software-ios-native](../software-ios-native/SKILL.md) | Native iOS implementation, rewrites, and Xcode agent workflows |
| [software-ios-runtime-debugging](../software-ios-runtime-debugging/SKILL.md) | Build/install/launch proof and stale-build triage before test interpretation |
| [software-mobile](../software-mobile/SKILL.md) | Platform choice and broader mobile guidance |
| [qa-testing-strategy](../qa-testing-strategy/SKILL.md) | Risk-based test strategy |
| [qa-testing-mobile](../qa-testing-mobile/SKILL.md) | Cross-platform mobile QA |

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Use web search or web fetch to verify current external facts, versions, pricing, deadlines, regulations, or platform behavior before final answers.
- Prefer primary sources; report source links and dates for volatile information.
- If web access is unavailable, state the limitation and mark guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

