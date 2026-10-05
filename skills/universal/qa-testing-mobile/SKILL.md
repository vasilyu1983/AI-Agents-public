---
name: qa-testing-mobile
description: "Plans mobile QA automation for iOS and Android apps. Use when planning automation frameworks, device matrix, flake control, or CI/CD release gates."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# QA Testing (Mobile)

Design and execute reliable, cost-aware mobile testing across iOS and Android (native + cross-platform).

## Quick Reference

Start with the [workflow](#workflow); use [Expert Judgment](#expert-judgment) for framework and automation tradeoffs, and [Resources](#resources) for depth.

## Quick Start

- Fill [assets/mobile-test-plan.md](assets/mobile-test-plan.md) to define risk, layers, and gates.
- Fill [assets/device-matrix.md](assets/device-matrix.md) from analytics to pick Tier 1/2/3 coverage.
- Use [references/framework-comparison.md](references/framework-comparison.md) to choose automation frameworks.
- Use `references/release-and-rollout.md` to define beta, pre-release, staged rollout, and rollback checks.
- Use [references/accessibility-testing.md](references/accessibility-testing.md) to add iOS and Android accessibility coverage.
- Use [references/flake-management.md](references/flake-management.md) to set a flake budget, reruns, and quarantine rules.

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
- Run CI against isolated test backends and seeded accounts so tests cannot mutate production data.
- Include accessibility, locale/timezone, and upgrade-path coverage when the app depends on them.
- Prefer stable selectors (accessibility IDs/test tags), not localized text. For vision-based tools, use specific visible labels.
- When using AI-native tools, review auto-generated tests for correctness before trusting as gates. Pair vision-based or nondeterministic checks with deterministic tests; they must not be the sole PR gate.
- If a visual report references a missing temporary screenshot path, re-capture the current screen or inspect the UI hierarchy. Do not dismiss the report just because the temp file expired.
- Treat vendor pricing, device availability, and store-policy details as live facts: verify with official docs before finalizing.
- When platform-specific known traps matter, verify the current bug behavior against primary sources and encode the regression in the platform-specific suite rather than relying on cross-platform smoke coverage.
- Add a fresh-clone CI gate (build/archive from a clean `git clone` with no dev-side regenerators) and, for iOS, require Archive-green, not just Build-green; details in [references/release-and-rollout.md](references/release-and-rollout.md) and [qa-testing-ios ios-ci-general.md](../qa-testing-ios/references/ios-ci-general.md) ("Build action ≠ Archive action").
- Gate release branches on current store policy (Play target API, App Store SDK minimum) and on Android vitals bad-behaviour thresholds as rollout halt criteria; see [references/release-and-rollout.md](references/release-and-rollout.md#store-policy-and-vitals-gates).

## Distribution-Channel Validation

- Mobile release readiness should include the real distribution path, not only local or CI compile success.
- For iOS, archive/signing, TestFlight readiness, and any production-only behaviors such as APNs or StoreKit should be validated on the channel that matches production behavior.
- For Android, include Play-track or equivalent store/device-lab evidence where store-side behavior matters.
- For every gate, record `built`, `installed`, `launched`, `journey-verified`, `channel-verified`, or `monitored-rollout` with source/build identity, platform, OS/device, locale, backend, channel, artifacts, and observation window.
- Do not collapse simulator, device-lab, beta-channel, and production evidence into one pass. A later stage inherits earlier evidence only for the exact same build and configuration.
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

- **Team shape drives more than app shape.** A team with one shared engineering org and no dedicated iOS/Android specialists gets more leverage from Detox/Patrol/Maestro (one suite, one skill set) even at some flake/maintenance cost. A team with separate iOS and Android pods with deep native expertise can favor XCUITest + Espresso run in parallel. Compare measured flake rate, execution time, and maintenance effort on representative journeys before deciding whether duplicated platform tests cost less than a shared abstraction.
- **Maintenance cost compounds; authoring cost does not.** Cross-platform frameworks (Appium especially) look cheaper on day one (one test written, two platforms covered) but the total cost of ownership is dominated by flake triage and selector maintenance over the suite's life, not initial authoring time. Before committing to a shared cross-platform E2E layer for a native (non-RN/Flutter) app, compare maintenance over the expected suite lifetime with the pilot's authoring cost.
- **The app's own architecture usually settles it.** If the app is already React Native or Flutter, fighting the framework's own native test tool (Detox / Patrol) in favor of Appium "for consistency" is rarely worth it — you inherit Appium's flake and lose the tighter JS-bridge or widget-tree synchronization the native-to-the-framework tool gives you for free.
- **Re-evaluate at scale inflection points, not on a fixed schedule.** The right trigger to revisit this decision is a change in team structure (specialist pods forming or dissolving) or a doubling of suite size (maintenance cost scales differently than authoring cost), not a calendar date.

### When NOT to automate mobile E2E

Automating everything is not free, and the default bias in this skill toward automation should be overridden when:

- **The screen or flow changes faster than the test can stabilize.** A screen mid-redesign, an A/B-tested onboarding flow with multiple live variants, or a pre-PMF feature likely to be cut within a quarter is a poor automation target — the maintenance cost is paid before the test ever earns its keep. Cover these with manual exploratory testing and defer automation until the UI stabilizes.
- **The flow is low-traffic and low-blast-radius.** An internal admin tool, a rarely used settings sub-screen, or a low-traffic flow with limited consequences may not justify a dedicated E2E test. Include severity and data-loss risk; crash reporting alone does not catch silent failures. Reserve E2E automation for flows on the critical path (auth, checkout, core value prop) identified in `## Inputs to Gather`.
- **The team cannot commit to fixing flakes.** A UI test suite nobody triages degrades into noise that gets ignored, then bypassed, then actively distrusted — at that point it provides *negative* value (false confidence) versus no suite at all. If there is no owner and no flake SLA, do not add more E2E coverage; fix the existing suite's trust first.
- **A cheaper layer already covers the risk.** Business logic, validation rules, and API contracts are almost always better (faster, more deterministic, cheaper to maintain) covered at the unit/integration layer than by driving them through a UI. Reach for E2E only for what genuinely requires the device/OS/UI layer: rendering, gestures, permissions, backgrounding, deep links, and cross-screen navigation.
- **Pre-PMF or prototype stage.** Before product-market fit, when the UI is expected to change weekly based on user feedback, a small manual smoke checklist plus strong crash reporting typically beats investing in E2E automation that will be rewritten before it pays back its authoring cost.

### Flake economics and release-train cadence

See `references/flake-management.md#flake-economics-real-device-vs-simulator` for why the same flake rate costs differently on real devices versus simulators (rerun latency, root-cause mix, and signal value all differ), and `references/release-and-rollout.md#release-train-cadence-and-testing-scope` for matching test scope to release cadence — including why a hotfix path is not optional once an app has real users, and how feature flags let you decouple "the build shipped safely" from "the feature is validated."

## Templates

- `assets/device-matrix.md` for OS and device coverage.
- `assets/mobile-test-plan.md` for test scope and automation.
- [assets/release-readiness-checklist.md](assets/release-readiness-checklist.md) for release gates.

## Resources

- `references/framework-comparison.md` for choosing between XCUITest, Espresso/Compose, Appium 3 (W3C-only; check npm `engines` for the supported Node range and run CI on a maintained Node LTS line), Detox (New Architecture compatible), Maestro (docs.maestro.dev), Drizz, TestSprite, and Flutter testing (Patrol).
- [references/ai-native-testing.md](references/ai-native-testing.md) for AI-native mobile testing: VLM-based testing, MCP integration, self-healing, NL authoring, and decision framework.
- `references/flake-management.md` for flake control guidance.
- [references/device-farm-strategies.md](references/device-farm-strategies.md) for cloud device farm selection, procurement questions, and cost optimization.
- [references/mobile-performance-testing.md](references/mobile-performance-testing.md) for startup, jank, memory, and battery testing.
- [references/cross-platform-test-patterns.md](references/cross-platform-test-patterns.md) for React Native, Flutter, and KMP testing patterns.
- `references/release-and-rollout.md` for TestFlight, Play pre-launch reports, staged rollout, and rollback planning.
- `references/localization-testing.md` for layered locale coverage and selector discipline.
- `references/accessibility-testing.md` for cross-platform accessibility release-gate questions and pointers to qa-testing-accessibility for iOS/Android audit APIs.
- [references/visual-regression-mobile.md](references/visual-regression-mobile.md) for golden image strategy, visual-diff tools (Percy, Applitools, Chromatic, Sauce Visual), pointers to native snapshot tooling in qa-testing-android / qa-testing-ios, pixel-tolerance vs perceptual diff, baseline rotation cadence, and CI artifact upload patterns.
- [references/test-layers-and-suite-anti-patterns.md](references/test-layers-and-suite-anti-patterns.md) for the unit/integration/E2E cost profile, deep-link and offline test entry points, and suite-level anti-patterns.
- `data/sources.json` for curated documentation and device lab links.

## Navigation

Use [Templates](#templates) for plan outputs and [Resources](#resources) for issue-specific depth; platform command details route through [Related Skills](#related-skills).

## Related Skills

| Skill | Purpose |
|-------|---------|
| [qa-testing-ios](../qa-testing-ios/SKILL.md) | iOS depth: XCTest, Swift Testing, simctl |
| [qa-testing-android](../qa-testing-android/SKILL.md) | Android depth: Espresso, Compose Testing, UI Automator |
| [qa-testing-playwright](../qa-testing-playwright/SKILL.md) | Web and webview testing |
| [software-mobile](../software-mobile/SKILL.md) | Mobile architecture guidance |

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
