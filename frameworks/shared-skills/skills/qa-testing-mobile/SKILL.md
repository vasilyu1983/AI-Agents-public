---
name: qa-testing-mobile
description: "Mobile QA for iOS and Android. Use when planning automation frameworks, device matrix, flake control, or CI/CD release gates."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# QA Testing (Mobile)

Design and execute reliable, cost-aware mobile testing across iOS and Android (native + cross-platform).

## Quick Reference

| Need | Go to |
|------|-------|
| Run the mobile QA workflow | `## Workflow` |
| Gather the right scope and inputs | `## Scope` and `## Inputs to Gather` |
| Shape outputs and quality checks | `## Outputs` and `## Quality Checks` |
| Decide native vs. cross-platform, or when NOT to automate | `## Expert Judgment` |
| Load templates and references | `## Navigation` |

## Quick Start

- Fill `assets/mobile-test-plan.md` to define risk, layers, and gates.
- Fill `assets/device-matrix.md` from analytics to pick Tier 1/2/3 coverage.
- Use `references/framework-comparison.md` to choose automation frameworks.
- Use `references/release-and-rollout.md` to define beta, pre-release, staged rollout, and rollback checks.
- Use `references/accessibility-testing.md` to add iOS and Android accessibility coverage.
- Use `references/flake-management.md` to set a flake budget, reruns, and quarantine rules.

## Scope

- Define mobile test strategy across iOS and Android.
- Plan device matrix, OS coverage, and risk tiers.
- Choose automation frameworks and CI + device lab setup.
- Address performance, network/offline, backgrounding, and permissions.
- Define pre-release gates, staged rollout, and store readiness checks.

## When NOT to Use

- Platform-specific iOS test command details -> [qa-testing-ios](../qa-testing-ios/SKILL.md)
- Platform-specific Android test command details -> [qa-testing-android](../qa-testing-android/SKILL.md)

## Inputs to Gather

- Platforms, supported OS versions, and device targets.
- App type (native, cross-platform, hybrid/webview).
- Critical user flows and risk areas.
- Distribution channels and release cadence.
- Beta/release channels (TestFlight, Play internal/closed testing, enterprise distribution if relevant).
- Existing test tooling, CI, and device lab access (Firebase Test Lab, BrowserStack, AWS Device Farm).
- Observability and rollout controls (Crashlytics/Sentry, performance/RUM, feature flags, staged rollout).
- Test data strategy (seed/reset, test accounts, environment parity).

## Workflow

1. Define quality risks and SLIs (crash-free, ANR, startup time, key flow success).
2. Build a device matrix from analytics; keep PR gates emulator/simulator-first.
3. Choose frameworks (default: XCUITest + Espresso/Compose; add app-specific cross-platform only when it reduces total cost).
4. Evaluate AI-native tools for self-healing, NL authoring, or vision-based testing where selector maintenance is a bottleneck.
5. Build test layers: unit, integration/contract, UI smoke, targeted E2E on real devices.
6. Add mobile-specific coverage: permissions, background/foreground, deep links, offline/poor network.
7. Add performance checks (startup, scrolling/jank, memory) and accessibility audits.
8. Set flake budget, rerun limits, quarantine policy, and failure triage (artifacts + reproducibility).
9. Define release gates + store readiness; run beta checks (TestFlight, Play pre-launch reports where relevant) and ship via staged rollout with monitoring + rollback.

## Outputs

- Mobile test strategy and device matrix.
- Automation plan and framework selection.
- Test case inventory with priorities.
- Release readiness checklist.
- CI pipeline and reporting plan.

## Quality Checks

- Keep UI tests focused on critical flows; keep suites small and fast.
- Separate device specific bugs from logic regressions.
- Track flake rate per test/device; quarantine and fix top offenders.
- Verify permissions, notifications, and background behavior.
- Include accessibility, locale/timezone, and upgrade-path coverage when the app depends on them.
- Prefer stable selectors (accessibility IDs/test tags), not localized text. For vision-based tools, use specific visible labels.
- When using AI-native tools, review auto-generated tests for correctness before trusting as gates.
- If a visual report references a missing temporary screenshot path, re-capture the current screen or inspect the UI hierarchy. Do not dismiss the report just because the temp file expired.
- Treat vendor pricing, device availability, and store-policy details as live facts: verify with official docs before finalizing.
- When platform-specific known traps matter, verify the current bug behavior against primary sources and encode the regression in the platform-specific suite rather than relying on cross-platform smoke coverage.
- Add a **fresh-clone CI gate** that catches "works on my machine" failures before they hit Apple's Xcode Cloud or Google Play's CI. Common pattern: developers regenerate files (Info.plist, locale manifests, shader blobs) at local build time, the regenerated outputs live in a gitignored folder, and the committed pbxproj / build files reference paths that are never tracked. The regression test is a disposable CI job that does `git clone` + `xcodebuild build` (or `./gradlew assembleRelease`) on a fresh clone without running any dev-side regenerators. If that job fails, the repo has drift that will fail Xcode Cloud `Archive - iOS` or Play Console uploads silently. Tip: use `git ls-files` not `ls` to verify a file actually reached the remote — a tracked file in a gitignored directory is invisible in `git status` but will still be committed; an untracked file in a gitignored directory is invisible everywhere.
- For iOS release gates, treat **Xcode Cloud Build** and **Xcode Cloud Archive** as two separate signals. Build only validates compile/link; Archive exercises signing, provisioning, and capability entitlements. A green Build + red Archive is a normal failure mode — and Archive is the one that gates TestFlight and App Store submission. Require Archive-green before marking a release branch ready.

## Distribution-Channel Validation

- Mobile release readiness should include the real distribution path, not only local or CI compile success.
- For iOS, archive/signing, TestFlight readiness, and any production-only behaviors such as APNs or StoreKit should be validated on the channel that matches production behavior.
- For Android, include Play-track or equivalent store/device-lab evidence where store-side behavior matters.
- Keep product-specific rollout order, metadata checklists, reviewer accounts, and internal smoke scripts in project docs. Use [references/release-and-rollout.md](references/release-and-rollout.md) for the portable baseline.

## Localization Coverage

Apps with localized UI or backend-served localized content need a layered test plan:

- fast catalog/key coverage to catch missing resources early
- value-quality checks so non-English locales do not silently ship English defaults
- targeted locale-layout smoke on a few high-signal locales
- integration checks for backend-served localized prose when applicable
- selector discipline that avoids locale-dependent element targeting

Localized UI correctness includes layout parity: equal-width peer containers, wrapped labels that do not truncate important terms, no overlays hiding primary content, and usable controls on the narrowest supported phone. AI-native or vision tests can help spot these issues, but deterministic catalog parity and targeted locale-layout smoke remain the gate.

Use [references/localization-testing.md](references/localization-testing.md) for the detailed patterns and tradeoffs.

## Expert Judgment

These are calls a checklist cannot make for you — they require reading the specific team, app, and business context.

### Native vs. cross-platform: the meta-decision

The framework decision matrix (`references/framework-comparison.md`) tells you which tool fits which app type. It does not tell you whether to *build* the app cross-platform in the first place, or whether an already-cross-platform app's test suite should stay cross-platform. Weigh:

- **Team shape drives more than app shape.** A team with one shared engineering org and no dedicated iOS/Android specialists gets more leverage from Detox/Patrol/Maestro (one suite, one skill set) even at some flake/maintenance cost. A team with separate iOS and Android pods with deep native expertise usually gets *more* total velocity from XCUITest + Espresso run in parallel, because native frameworks are faster and lower-flake per test, and the "duplicate the test" cost is smaller than the "maintain a shared abstraction layer" cost for a team that already has two sets of specialists.
- **Maintenance cost compounds; authoring cost does not.** Cross-platform frameworks (Appium especially) look cheaper on day one (one test written, two platforms covered) but the total cost of ownership is dominated by flake triage and selector maintenance over the suite's life, not initial authoring time. Before committing to a shared cross-platform E2E layer for a native (non-RN/Flutter) app, model 12 months of maintenance cost, not the pilot's authoring cost.
- **The app's own architecture usually settles it.** If the app is already React Native or Flutter, fighting the framework's own native test tool (Detox / Patrol) in favor of Appium "for consistency" is rarely worth it — you inherit Appium's flake and lose the tighter JS-bridge or widget-tree synchronization the native-to-the-framework tool gives you for free.
- **Re-evaluate at scale inflection points, not on a fixed schedule.** The right trigger to revisit this decision is a change in team structure (specialist pods forming or dissolving) or a doubling of suite size (maintenance cost scales differently than authoring cost), not a calendar date.

### When NOT to automate mobile E2E

Automating everything is not free, and the default bias in this skill toward automation should be overridden when:

- **The screen or flow changes faster than the test can stabilize.** A screen mid-redesign, an A/B-tested onboarding flow with multiple live variants, or a pre-PMF feature likely to be cut within a quarter is a poor automation target — the maintenance cost is paid before the test ever earns its keep. Cover these with manual exploratory testing and defer automation until the UI stabilizes.
- **The flow is low-traffic and low-blast-radius.** An internal admin tool, a rarely used settings sub-screen, or a flow touched by <1% of sessions rarely justifies a dedicated E2E test; a crash there is caught by crash reporting, not a blocking CI gate. Reserve E2E automation for flows on the critical path (auth, checkout, core value prop) identified in `## Inputs to Gather`.
- **The team cannot commit to fixing flakes.** A UI test suite nobody triages degrades into noise that gets ignored, then bypassed, then actively distrusted — at that point it provides *negative* value (false confidence) versus no suite at all. If there is no owner and no flake SLA, do not add more E2E coverage; fix the existing suite's trust first.
- **A cheaper layer already covers the risk.** Business logic, validation rules, and API contracts are almost always better (faster, more deterministic, cheaper to maintain) covered at the unit/integration layer than by driving them through a UI. Reach for E2E only for what genuinely requires the device/OS/UI layer: rendering, gestures, permissions, backgrounding, deep links, and cross-screen navigation.
- **Pre-PMF or prototype stage.** Before product-market fit, when the UI is expected to change weekly based on user feedback, a small manual smoke checklist plus strong crash reporting typically beats investing in E2E automation that will be rewritten before it pays back its authoring cost.

### Flake economics and release-train cadence

See `references/flake-management.md#flake-economics-real-device-vs-simulator` for why the same flake rate costs differently on real devices versus simulators (rerun latency, root-cause mix, and signal value all differ), and `references/release-and-rollout.md#release-train-cadence-and-testing-scope` for matching test scope to release cadence — including why a hotfix path is not optional once an app has real users, and how feature flags let you decouple "the build shipped safely" from "the feature is validated."

## Do / Avoid

### Do

- Build device matrix from analytics; keep PR gates emulator/simulator-first
- Track flake rate per test and device; quarantine and fix top offenders
- Use stable selectors (accessibility IDs, test tags) instead of localized text
- Include accessibility, locale, and upgrade-path coverage when the app depends on them
- Define pre-release gates and staged rollout with monitoring and rollback criteria
- Evaluate AI-native tools (Maestro MCP, Drizz, TestSprite) when selector maintenance is the top pain point
- Review AI-generated tests for correctness before promoting to CI gates

### Avoid

- Testing against live backends in CI
- Using localized text as test selectors
- Blocking all PRs on the full device matrix when smoke coverage is sufficient
- Treating device farms as a substitute for test design
- Using vision-based / non-deterministic tools as the sole PR gate (pair with deterministic native tests)
- Trusting autonomous test agents without human review of generated test logic

## Templates

- `assets/device-matrix.md` for OS and device coverage.
- `assets/mobile-test-plan.md` for test scope and automation.
- `assets/release-readiness-checklist.md` for release gates.

## Resources

- `references/framework-comparison.md` for choosing between XCUITest, Espresso/Compose, Appium 3 (released, W3C-only, Node 20+), Detox (New Architecture compatible), Maestro (docs.maestro.dev), Drizz, TestSprite, and Flutter testing (Patrol 4.0).
- `references/ai-native-testing.md` for AI-native mobile testing: VLM-based testing, MCP integration, self-healing, NL authoring, and decision framework.
- `references/flake-management.md` for flake control guidance.
- `references/device-farm-strategies.md` for cloud device farm selection, procurement questions, and cost optimization.
- `references/mobile-performance-testing.md` for startup, jank, memory, and battery testing.
- `references/cross-platform-test-patterns.md` for React Native, Flutter, and KMP testing patterns.
- `references/release-and-rollout.md` for TestFlight, Play pre-launch reports, staged rollout, and rollback planning.
- `references/localization-testing.md` for layered locale coverage and selector discipline.
- `references/accessibility-testing.md` for iOS accessibility audits and Android accessibility testing.
- `references/visual-regression-mobile.md` for golden image strategy, visual-diff tools (Percy, Applitools, Chromatic, Sauce Visual), native snapshot tooling (Paparazzi, Roborazzi, swift-snapshot-testing), pixel-tolerance vs perceptual diff, baseline rotation cadence, and CI artifact upload patterns.
- `data/sources.json` for curated documentation and device lab links.

## ASCII Flow

```text
Mobile QA request
  -> Define platforms, app type, release channel, and critical flows
  -> Build device matrix from analytics, OS support, risk, and cost
  -> Choose native, cross-platform, cloud-device, visual, accessibility, and perf layers
  -> Stabilize selectors, fixtures, permissions, network, locale, and reset paths
  -> Run targeted local/device-farm checks with artifacts
  -> Promote to release gates only with flake, rollout, and rollback evidence
```

## Navigation

- `## Workflow`, `## Outputs`, and `## Quality Checks` for the baseline sequence
- `## Expert Judgment` for the calls a checklist can't make: native-vs-cross-platform, when NOT to automate, flake economics, release-train cadence
- `## Templates` and `## Resources` for deeper materials
- `## Related Skills` for platform-specific and observability handoffs

## Related Skills

| Skill | Purpose |
|-------|---------|
| [qa-testing-ios](../qa-testing-ios/SKILL.md) | iOS depth: XCTest, Swift Testing, simctl |
| [qa-testing-android](../qa-testing-android/SKILL.md) | Android depth: Espresso, Compose Testing, UI Automator |
| [qa-testing-playwright](../qa-testing-playwright/SKILL.md) | Web and webview testing |
| [software-mobile](../software-mobile/SKILL.md) | Mobile architecture guidance |

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Use web search or web fetch to verify current external facts, versions, pricing, deadlines, regulations, or platform behavior before final answers.
- Prefer primary sources; report source links and dates for volatile information.
- If web access is unavailable, state the limitation and mark guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

