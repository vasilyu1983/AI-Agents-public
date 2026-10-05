---
name: software-ios-native
description: "Guides native iOS with Swift, SwiftUI, UIKit interop, concurrency, and persistence. Use when building or reviewing iPhone/iPad apps after establishing runtime truth."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Native iOS Development

Use this skill for native iOS work only. It is the default shared-skill entrypoint for SwiftUI-first iOS 17+ apps, bounded rewrites from older codebases, and agent-assisted workflows in Xcode, Codex, and Claude Code.

## Quick Reference

| Task | Default Picks | Notes |
|------|---------------|-------|
| **State & UI** | | |
| New UI screens | SwiftUI | UIKit interop only where Apple APIs require it |
| Observable state (iOS 17+) | `@Observable` + main actor isolation | Replaces ObservableObject/Published |
| Async work | `async`/`await`, structured concurrency | Detached tasks only when intentionally breaking inheritance |
| Unit/integration tests | Swift Testing | Preferred over XCTest for new tests |
| UI automation tests | XCTest / XCUITest | Keep using for UI and performance tests |
| **State machine discipline** | | |
| Submit guard | `guard state == .idle else { return }` | Prevents double-tap duplicate submissions in `@Observable` stores |
| Transient completion | One-shot UI effect or explicit acknowledgement | Do not reset durable state on an arbitrary timer; store and cancel any delayed task |
| Minimal state enums | Remove states that can't happen anymore | Dead enum cases produce dead error handling and mislead future readers |
| **Networking & resilience** | | |
| Network reachability | `@Observable` singleton + `NWPathMonitor` | Publish `isConnected`; disable submit buttons when offline; start monitor in screen `.onAppear` |
| **Agent tooling & build** | | |
| Agent tooling (in Xcode) | Xcode native assistant | Verify the live stable/beta Xcode and Swift versions, and Xcode's macOS host requirement (matters for CI runner images), at developer.apple.com/news/releases before citing one; check Apple's Upcoming Requirements page for the upload-SDK floor and minimum deployment target before submission — do not build release submissions against a beta SDK |
| Agent tooling (outside Xcode) | XcodeBuildMCP if callable | Otherwise fall back immediately to Apple CLI |
| CLI fallback | `xcodebuild`, `simctl`, `xcresulttool` | Default path when MCP is unavailable or blocked |
| Build / install / stale-app failures | `software-ios-runtime-debugging` | Use before UI or feature diagnosis |
| XcodeGen projects | `scripts/generate-xcodeproj.sh` | Must regenerate after adding new Swift files |
| **Local-dev launcher pair** | `scripts/run-local-ios-dev.sh` + `scripts/stop-local-ios-dev.sh` | Two defensive guards (grep env + generated plist for `localhost:`); persist simulator UDID; never `pkill -f Simulator`. See [quick-reference-extended.md#agent-tooling--build](references/quick-reference-extended.md#agent-tooling--build) |
| `.pbxproj`-managed projects | Add new files to target membership | Do not assume on-disk Swift files are auto-discovered |
| **Generated files / CI landmines** | Commit generated outputs or regenerate in CI hook | `git add -f` for gitignored-folder tracked files; Xcode Cloud `ci_post_clone.sh` for env shims. See [quick-reference-extended.md](references/quick-reference-extended.md#agent-tooling--build) |
| **TARGETED_DEVICE_FAMILY → "1"** | Requires fresh archive + ASC build attachment | Changing `project.yml` alone is insufficient; value is baked into binary. |
| **Canvas, immersive screens, sheets, l10n hygiene** | See [quick-reference-extended.md](references/quick-reference-extended.md#canvas-immersive-screens--l10n-hygiene) | Canvas start state and gestures, persistent sheets, viz state ownership, grid sizing, sheet swapping, l10n plain-enum call rule (catalog parity and regeneration live in software-localisation) |
| **StoreKit & billing** | | |
| StoreKit 2 subscriptions | `@Observable` StoreKitManager + TransactionSyncService | `transaction.finish()` only after backend sync confirms |
| Paywall presentation | `.sheet(isPresented:)` from any locked screen | Don't navigate to Settings; present modal directly |
| Product pricing display | `product.displayPrice` from StoreKit | Never hardcode prices; Apple handles locale formatting |
| Promotional offers (rewards) | Server-signed `.promotionalOffer()` in `Product.purchase(options:)` | Bridges Stripe credit gaps for Apple-billed users; user must redeem |
| **Paid Apps Agreement (#1 invisible blocker)** | Verify Active at appstoreconnect.apple.com/business | Silent empty `Product.products(for:)` results; check before subscription-level diagnosis. Full decision table + timeline in [app-store-connect-checklist.md Phase 5](../software-mobile/references/app-store-connect-checklist.md). See [quick-reference-extended.md](references/quick-reference-extended.md#storekit--billing) |
| **ASC `Missing Metadata`** | Fill all required fields: prices, localization, review screenshot | Products exist but fields incomplete. Workflow in [app-store-connect-checklist.md](../software-mobile/references/app-store-connect-checklist.md). See [quick-reference-extended.md](references/quick-reference-extended.md#storekit--billing) |
| **Review screenshot** | sRGB 8-bit RGB PNG 72 DPI, 1284 × 2778 | ASC rejects Display P3 / 16-bit device screenshots; use Pillow profile conversion. See [quick-reference-extended.md](references/quick-reference-extended.md#storekit--billing) |
| **Accounting currency (backend-denominated)** | `NumberFormatter` + explicit `currencyCode` + `locale = .current` | Never `String(format: "£%.2f", …)`; details in [quick-reference-extended.md](references/quick-reference-extended.md#storekit--billing) |
| Year/ID display | `Text(verbatim:)` | Suppress locale number formatting (2026 not 2,026) |
| **Locale-aware time formatting; strings and backend locale** | `"jm"` date skeleton via `DateFormatter`; strings, plurals and the backend translation pipeline live in [software-localisation](../software-localisation/SKILL.md) | Platform rows in [quick-reference-extended.md](references/quick-reference-extended.md#l10n--backend-locale) |
| **Auth & push** | | |
| Sign in with Apple | `ASAuthorizationController` + `CheckedContinuation` | Guideline 4.8 requires an equivalent privacy-preserving login (limits data to name/email, allows a private relay email, no ad tracking without consent) if a 3rd-party social login is offered — Sign in with Apple is the usual way to satisfy it, not the only one; check current exemptions |
| OTP code input | Hidden `TextField` + `.textContentType(.oneTimeCode)` | Better than magic links for native; iOS auto-fills from notifications |
| Non-`@MainActor` delegates | Match the SDK requirement; hop to `@MainActor` for UI state | `MainActor.assumeIsolated` checks isolation; use it only when the callback contract guarantees that executor. |
| Push notification categories | Register `UNNotificationCategory` in `didFinishLaunchingWithOptions` | Must be set before any notification arrives; match `aps.category` from backend |
| Badge count (iOS 16+) | `try? await UNUserNotificationCenter.current().setBadgeCount(0)` | `applicationIconBadgeNumber` is deprecated; `setBadgeCount` is `async throws` |
| Push delegate isolation | Inspect the imported SDK requirement and callback contract | Hop UI mutations to `@MainActor`; do not infer a universal delegate fix from a private crash symbol. See [swiftui-observation-concurrency.md](references/swiftui-observation-concurrency.md#nonisolated-async-delegate-methods--nested-mainactorrun) and [quick-reference-extended.md](references/quick-reference-extended.md#auth--push--detailed-rows) |
| `Task { }` isolation | Inherits the actor context where its closure is formed; annotate explicitly across nonisolated callbacks | `Task.detached` breaks actor inheritance. See [swiftui-observation-concurrency.md](references/swiftui-observation-concurrency.md#task---inherits-its-actor-context) |
| `actor` vs `@MainActor final class` | Choose the isolation owner by the work and shared state | A main-actor caller resumes on the main actor after `await`; keep CPU-heavy work off it. See [swiftui-observation-concurrency.md](references/swiftui-observation-concurrency.md#actor--mainactor-final-class-refactoring-guidance) |
| `@Sendable async` closure awaited from `@MainActor` | Return results to the isolated caller; isolate the body if it needs UI state | `@Sendable` is a transfer-safety constraint, not an executor choice; caller isolation survives `await`. See [swiftui-observation-concurrency.md](references/swiftui-observation-concurrency.md#sendable-async-closure-isolation-footgun) |
| `SCNView` in `UIViewRepresentable` | Create initial scene once; update changed inputs | A no-op `updateUIView` is correct only for immutable inputs. See [swiftui-observation-concurrency.md](references/swiftui-observation-concurrency.md#scnview-reassignment-in-updateuiview-anti-pattern) |
| Push action routing | Check `response.actionIdentifier` in `didReceive` | `UNNotificationDefaultActionIdentifier` = tap; custom IDs = action buttons; dismiss = no route |
| Push-open ownership, preferences, entitlements, APNs proof, export gate, backend routing, QA loop | See full rows in [quick-reference-extended.md](references/quick-reference-extended.md#auth--push--detailed-rows) | Inspect final exported app/profile: push-enabled TestFlight/App Store exports require `production`; backend: per-device `push_environment` column authoritative |
| Swift Concurrency crash triage | Symptom-first triage runbook | Private SwiftUI symbol crash → start at [swift-concurrency-crash-triage.md](../software-ios-runtime-debugging/references/swift-concurrency-crash-triage.md); ladder: console → MTC → TSan → lldb `bt` |
| **SwiftUI API modernization** | | |
| Deprecated API review | [references/swiftui-deprecated-api.md](references/swiftui-deprecated-api.md) | Systematic deprecated→modern mapping |
| SwiftUI performance audit | [references/swiftui-performance.md](references/swiftui-performance.md) | View splitting, lazy stacks, modifier efficiency |
| Modern Swift idioms | [references/modern-swift-patterns.md](references/modern-swift-patterns.md) | Foundation modernization, date/string/collection patterns |
| **Concurrency (constructive)** | | |
| Writing correct concurrency | [references/swift-concurrency-patterns.md](references/swift-concurrency-patterns.md) | Structured concurrency, async streams, bridging, migration |
| Concurrency compiler errors | [references/swift-concurrency-diagnostics.md](references/swift-concurrency-diagnostics.md) | Error→fix mapping for Swift 6 diagnostics |
| **Persistence** | | |
| SwiftData modeling | [references/swiftdata-core.md](references/swiftdata-core.md) | Core rules, predicates, CloudKit, indexing, class inheritance |
| Core Data persistence | [references/core-data-persistence.md](references/core-data-persistence.md) | Stack setup, contexts, object IDs, batch ops, migrations, CloudKit |
| Reusable app skeleton | [references/native-ios-app-foundation-skeleton.md](references/native-ios-app-foundation-skeleton.md) | SwiftUI shell, Observation state, persistence, CloudKit, App Intents, local AI hooks, release gates |
| iCloud database app | [references/icloud-cloudkit-app-skeleton.md](references/icloud-cloudkit-app-skeleton.md) | SwiftData/Core Data/CloudKit choice, private/public/shared scopes, no-server limits |
| **Stacks & monetization** | | |
| Pick a starter stack to monetize/engage | [references/starter-stacks-and-monetization.md](references/starter-stacks-and-monetization.md) | CloudKit→Cloudflare→RevenueCat→Supabase graduation ladder; on-device AI as free tier; webhook idempotency traps |
| Run iOS dev as a conveyor / app factory | [references/ios-app-conveyor.md](references/ios-app-conveyor.md) | 4 pillars: default stack per class, shared SPM, Fastlane+Match CI, agent build loop; 2026 stack survey |
| **Build performance** | | |
| Xcode build optimization | [references/xcode-build-optimization.md](references/xcode-build-optimization.md) | Benchmarking, diagnostic flags, SPM analysis, common wins |
| **Swift 6.2+ / Xcode 26+ additions** | See [quick-reference-extended.md](references/quick-reference-extended.md#swift-62--xcode-26-additions) | Default MainActor isolation, iOS 26 `withAnimation` regression, stale `SubscriptionStatus.all`, `AnyView`/`@ObservedObject`/`NavigationView`/`.id(UUID())` modernization, Combine lifecycle, coordinator navigation |

Rule: `rules/ios/money.md` loads this invariant when Claude edits a matching file.

## When to Use This Skill

SwiftUI-first iOS 17+ screens, app skeletons, UIKit bounded rewrites, agent-assisted Xcode/Codex/Claude Code workflows, Swift Concurrency, SwiftData/Core Data persistence, Xcode build optimization, privacy manifests, release gates, and native iOS code review.

## Defaults

- UI: SwiftUI-first; UIKit interop only where Apple APIs require it.
- State: `@Observable` + main actor isolation (iOS 17+).
- New projects: `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor` (Xcode 26+); `nonisolated`/`@concurrent` only when breaking out.
- Async: structured concurrency + `async`/`await`; detached tasks only when intentionally breaking inheritance.
- Tests: Swift Testing for unit/integration; XCTest/XCUITest for UI automation.
- Release gates: privacy manifests, required-reason APIs, SDK compliance, accessibility, real-device verification — non-optional. Verify minimum Xcode version at developer.apple.com/news/releases each release cycle.

## Version Currency (check every session)

- **Current stable vs beta:** read Apple's Developer Releases page (developer.apple.com/news/releases) for the current GA iOS/Xcode and the beta point releases, and swift.org/blog for the current Swift release, before naming any version. APIs from a GA release are shippable behind `#available` checks; an Xcode beta is never used for App Store submissions. Check the Xcode release notes for the minimum macOS host version.
- **Submission gates:** App Store Connect enforces two separate floors — the build SDK (which Xcode you compile with) and the minimum deployment target. Read Apple's Upcoming Requirements page before each submission; a build-SDK floor does not change your deployment target.
- Point releases drift fast; treat any specific point-release number in this skill as an example, not a current fact.

## Expert Judgment Calls

- **SwiftUI vs UIKit:** default to SwiftUI. Reach for UIKit interop only for a named capability gap (e.g., precise text-kit control, certain camera/AR compositions, legacy `UICollectionView` compositional layouts not yet matched in SwiftUI) — not because a contributor is more comfortable in UIKit. Re-evaluate the gap list each Xcode cycle; SwiftUI closes gaps yearly and yesterday's justified UIKit escape hatch is often removable.
- **Strict concurrency adoption:** recent Xcode new-project templates can set `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor` and enable Approachable Concurrency without turning on Swift 6 language mode — check `SWIFT_VERSION` and the isolation settings in the generated project rather than trusting a remembered default. Treat "Swift 6 language mode", "Approachable Concurrency" (changes runtime behavior: existing `nonisolated async` functions can now run on the caller's actor), and "default MainActor isolation" as three separate switches with separate migration cost, not one bundle. For a new project it is reasonable to turn all three on, since there is no legacy code to fight. For an existing pre-Swift-6 codebase, do not flip strict concurrency in one PR: enable it module-by-module or file-by-file, starting from leaf types with no dependents, and budget real calendar time — the Swift Forums "explosion of isolation violations" reports are the normal experience, not a sign something is wrong. Never bulk-silence with `@preconcurrency` as a substitute for doing the migration.
- **Dependency management:** Swift Package Manager is the default for every new dependency and for new projects outright. Only keep CocoaPods where an existing project already depends on it and the migration cost (Pods with no SPM manifest, deeply nested transitive Pod dependencies) currently exceeds the maintenance tax of running two package managers. Don't introduce a new CocoaPods dependency into an SPM-only project to save a day of integration work — it reintroduces the exact tooling fragmentation SPM removed.
- **Modularization threshold:** don't split into SPM modules pre-emptively. Splitting pays off once a target exceeds roughly 150-200 files, once independent teams need to build/test in isolation, or once agent-driven workflows need a bounded package to avoid loading the whole app graph for one feature. Below that, module boundaries add build-graph and API-surface overhead without a compiler-enforced win. See [xcode-build-optimization.md → SPM Dependency Analysis](references/xcode-build-optimization.md#spm-dependency-analysis) for the build-time tradeoffs either way.
- **TestFlight and phased release discipline:** never promote straight from internal build to a 100% production release. Run at least one external TestFlight wave sized to catch device/OS-version variance, then use phased release (7-day ramp) for production so a bad build caps its blast radius before full rollout. Treat a skipped phased release as a release-risk finding worth calling out, not a minor process nit.

## ASCII Flow

```text
iOS native task
  -> Confirm app shape: SwiftUI, UIKit interop, service, or release gate
  -> Prove Xcode, simulator/device, build, install, and launch reality
  -> Choose architecture: Observation, concurrency, persistence, navigation
  -> For reusable skeletons, add iCloud data, App Intents, local AI/retrieval hooks, and release gates
  -> Implement bounded slice with tests and privacy/accessibility checks
  -> Check Swift, StoreKit, signing, privacy, and App Store traps
  -> Build, run, inspect logs/screenshots, and report proof
```

## Runtime Truth And Prompting

Proof-first: verify tool reality (Xcode assistant → XcodeBuildMCP → Apple CLI), prove build+launch before UI diagnosis, require bounded slices with explicit proof artifacts. Load [references/runtime-proof-and-prompts.md](references/runtime-proof-and-prompts.md) for agent defaults, proof rules, execution loop, and prompt shape.

## Rewrite Workflow

1. Lock the baseline:
   existing app behavior, minimum OS, device classes, external integrations, and non-goals.
2. Choose the target defaults:
   SwiftUI-first, iOS 17+, Observation, Swift Concurrency, Swift Testing, XCTest/XCUITest.
3. Slice the rewrite into bounded vertical features:
   app shell, auth/session, core navigation, feature flows, integrations, release surfaces.
   XcodeGen: run `scripts/generate-xcodeproj.sh` after adding new files. `.pbxproj` projects: register new files in target membership explicitly.
4. For each slice, require evidence:
   build success, run success, targeted tests, parity notes, and known gaps.
5. Keep release-only concerns visible throughout: privacy manifests, entitlement changes, required-reason APIs, push, store metadata.
   Push QA: sign off `sandbox` (device) and `production` (TestFlight) paths separately; validate cold-start tap, warm resume, and normal reopen.
6. End every batch with a handoff: changed behavior, validation performed, residual risk, next slice.
7. When a backend change eliminates an error class, immediately remove the now-impossible error types, decoders, and UI states from the iOS client.

## Specialized Patterns

Load [references/ui-and-integration-patterns.md](references/ui-and-integration-patterns.md) for Canvas/gesture/immersive surfaces, auth/onboarding/Supabase integration gotchas, and StoreKit 2 billing + server-notification rules.

## Release Signing And Distribution

Xcode can re-sign an archive during distribution. Validate the exported App Store/TestFlight app and its provisioning profile; push-enabled exports require `aps-environment = production`, and release exports must not enable debugging. Use the Organizer distribution method for TestFlight/App Store. Full gate list (archive inspection, generated `Info.plist`, encryption prompt) in [references/ios-release-and-compliance.md](references/ios-release-and-compliance.md#release-signing-and-distribution).

## Known iOS Traps

Full trap table in [references/ios-traps-and-scenarios.md](references/ios-traps-and-scenarios.md). Top traps by crash frequency and silent-failure risk:

| Trap | Symptom | Fix |
|---|---|---|
| `_performBlockAfterCATransactionCommitSynchronizes:` | UIKit main-thread assertion | Capture the backtrace and isolate the actual UI call; the private symbol does not identify one cause. |
| UN delegate touching UI state | Isolation diagnostic or notification-tap failure | Match the SDK requirement, transfer a Sendable payload, then hop UI work to `@MainActor`. |
| `Task { }` created in a nonisolated callback then mutating `@Observable` | Off-actor UI mutation; the closure inherits the nonisolated creation context | Hop explicitly with `Task { @MainActor [weak self] in … }`; a task created inside a main-actor-isolated method already inherits that actor |
| Actor call awaited from `@MainActor` | Caller resumes on its own actor; shared state may change while suspended | Re-check request identity/state after `await`; do not replace an actor to repair a supposed executor loss. |
| `@Sendable async` closure touching UI state | Closure body may lack required actor isolation | Add `@MainActor` only when its body needs UI state; the caller still resumes on its actor. |
| `SCNView` updates | Rebuilding scenes can reset interaction state or perform unnecessary work | Create initial objects once; apply changed inputs incrementally in `updateUIView`. |
| iOS 26 `withAnimation` in `@MainActor` methods | Animations fail to start or skip starting state | Hoist `withAnimation` out of `@MainActor` body |
| Xcode 26 `SubscriptionStatus.all` stale | StoreKit 2 shows wrong tier post-upgrade | Query `Product.SubscriptionInfo.Status` directly |
| Locale-change handler missing store reset | Language change has no visible effect | `reset()` every prose-caching store + `URLCache.shared.removeAllCachedResponses()` |
| Stored profile locale wins over `?locale=` param | iOS user sees English despite picker showing Russian | Server priority must be `?locale=` > `Accept-Language` > stored profile |

Web-search `_performBlockAfterCATransactionCommitSynchronizes:` before code review (private symbol). `dataCorrupted` + `<!DOCTYPE html>` = API routing/auth bug, not push crash. Never bulk-silence Swift 6 errors with `@preconcurrency`. Detailed recipes in [swift-concurrency-crash-triage.md](../software-ios-runtime-debugging/references/swift-concurrency-crash-triage.md).

## When NOT to Use This Skill

Use a different skill when:

- **Cross-platform or platform-choice decisions** → [software-mobile](../software-mobile/SKILL.md)
- **iOS build/install/launch failures, stale installs, simulator drift, XcodeGen issues** → [software-ios-runtime-debugging](../software-ios-runtime-debugging/SKILL.md)
- **iOS test execution, simulator flake control, `xcresult` triage** → [qa-testing-ios](../qa-testing-ios/SKILL.md)
- **Web UI or browser app implementation** → [software-frontend](../software-frontend/SKILL.md)
- **General architecture without iOS-specific constraints** → [software-architecture-design](../software-architecture-design/SKILL.md)
- **iOS visual design, HIG layout/typography, dark mode design, dashboard patterns** → [software-ios-design](../software-ios-design/SKILL.md)

## Scenarios

S1 StoreKit 2 entitlement reconciliation · S2 APNs sandbox vs production proof · S3 Swift 6.2 concurrency migration · S4 `withAnimation` Xcode 26 regression · S5 privacy manifest pre-submission audit. Step-by-step recipes in [references/ios-traps-and-scenarios.md](references/ios-traps-and-scenarios.md#scenarios).

## Navigation

### References

| Resource | Purpose |
|----------|---------|
| [references/quick-reference-extended.md](references/quick-reference-extended.md) | Verbose Quick Reference rows moved from SKILL.md: local-dev launcher, CI landmines, StoreKit/ASC, l10n, push |
| [references/ios-traps-and-scenarios.md](references/ios-traps-and-scenarios.md) | Full Known iOS Traps table and Scenarios S1–S5 recipes |
| [references/ios-rewrite-playbook.md](references/ios-rewrite-playbook.md) | Rewrite slicing, acceptance criteria, and evidence rules |
| [references/agentic-ios-tooling.md](references/agentic-ios-tooling.md) | Xcode's native coding agent, XcodeBuildMCP, and CLI fallback selection rules |
| [references/xcodebuildmcp-workflows.md](references/xcodebuildmcp-workflows.md) | Verified XcodeBuildMCP install, config, and workflow loops |
| [references/codex-claude-ios-workflows.md](references/codex-claude-ios-workflows.md) | Repo memory, approval boundaries, and prompt patterns |
| [references/runtime-proof-and-prompts.md](references/runtime-proof-and-prompts.md) | Proof-first runtime execution, token discipline, and prompt shape |
| [references/ui-and-integration-patterns.md](references/ui-and-integration-patterns.md) | Canvas, immersive UI, backend integration, and StoreKit 2 patterns |
| [references/swiftui-observation-concurrency.md](references/swiftui-observation-concurrency.md) | Verified app-layer defaults for SwiftUI, Observation, and concurrency |
| [references/swiftui-deprecated-api.md](references/swiftui-deprecated-api.md) | Deprecated→modern SwiftUI API mapping |
| [references/swiftui-performance.md](references/swiftui-performance.md) | View splitting, lazy stacks, modifier efficiency, and rendering patterns |
| [references/swift-concurrency-patterns.md](references/swift-concurrency-patterns.md) | Structured concurrency, async streams, bridging, and migration tables |
| [references/swift-concurrency-diagnostics.md](references/swift-concurrency-diagnostics.md) | Swift concurrency compiler error→fix mapping |
| [references/networking-and-data-loading.md](references/networking-and-data-loading.md), [references/swiftui-composition-patterns.md](references/swiftui-composition-patterns.md) | API client, request coalescing, pagination, image cache, MetricKit; ViewModifier, PreferenceKey, property wrappers, result builders |
| [references/swiftdata-core.md](references/swiftdata-core.md) | SwiftData modeling, predicates, CloudKit, indexing, and class inheritance |
| [references/core-data-persistence.md](references/core-data-persistence.md) | Core Data stack ownership, context rules, migrations, and CloudKit constraints |
| [references/native-ios-app-foundation-skeleton.md](references/native-ios-app-foundation-skeleton.md) | Reusable SwiftUI app foundation: modules, defaults, extension points, proof gates |
| [references/icloud-cloudkit-app-skeleton.md](references/icloud-cloudkit-app-skeleton.md) | iCloud/CloudKit data-layer: schema, database scopes, no-server boundaries |
| [references/modern-swift-patterns.md](references/modern-swift-patterns.md) | Modern Swift idioms, Foundation API, and coding style |
| [references/xcode-build-optimization.md](references/xcode-build-optimization.md) | Build benchmarking, compilation diagnostics, and optimization workflow |
| [references/ios-release-and-compliance.md](references/ios-release-and-compliance.md) | Privacy, SDK compliance, and release-gate checks |
| [data/sources.json](data/sources.json) | Primary sources and current external references |

### Templates

| Template | Purpose |
|----------|---------|
| [assets/template-ios-rewrite-brief.md](assets/template-ios-rewrite-brief.md) | Rewrite scope and constraint brief |
| [assets/template-native-ios-app-skeleton.md](assets/template-native-ios-app-skeleton.md) | Copyable native iOS app foundation layout and module checklist |
| [assets/template-ios-cloudkit-persistence-stack.md](assets/template-ios-cloudkit-persistence-stack.md) | SwiftData/Core Data/CloudKit stack starter with schema and sync gates |
| [assets/template-ios-makefile-and-proof-loop.md](assets/template-ios-makefile-and-proof-loop.md) | Agent-friendly Makefile targets and build/test/archive proof loop |
| [assets/template-ios-feature-request.md](assets/template-ios-feature-request.md) | Feature-level Codex / Claude Code request format |
| [assets/template-ios-proof-checklist.md](assets/template-ios-proof-checklist.md) | Source-backed proof and validation checklist |
| [assets/template-ios-agent-handoff.md](assets/template-ios-agent-handoff.md) | Post-change handoff with evidence and residual risk |
| [assets/scaffolds/app-class-blueprints.md](assets/scaffolds/app-class-blueprints.md) | Pick app class (CRUD/notes, AI wrapper, content/feed, utility-IAP) → tier, scaffolds, monetization, cost |
| [assets/scaffolds/entitlement-and-paywall.md](assets/scaffolds/entitlement-and-paywall.md) | Copy-paste StoreKit 2 `EntitlementStore` + `PaywallGate` (single source of truth) |
| [assets/scaffolds/push-and-engagement.md](assets/scaffolds/push-and-engagement.md) | Copy-paste `PushManager` with deferred opt-in + `Reachability` |
| [assets/scaffolds/cloudflare-worker-backend.md](assets/scaffolds/cloudflare-worker-backend.md) | Worker scaffold: subscription webhook (idempotent, re-fetch), AI proxy, push |

### Related Skills

| Skill | Purpose |
|-------|---------|
| [software-mobile](../software-mobile/SKILL.md) | Platform choice and cross-platform tradeoffs |
| [software-ios-runtime-debugging](../software-ios-runtime-debugging/SKILL.md) | Build/install/launch proof, stale-build triage, and simulator/package debugging |
| [qa-testing-ios](../qa-testing-ios/SKILL.md) | iOS test execution, `xcresult`, and simulator stability |
| [agents-memory](../agents-memory/SKILL.md) | Shared `AGENTS.md` / `CLAUDE.md` memory strategy |
| [dev-context-engineering](../dev-context-engineering/SKILL.md) | Cross-tool context design for Codex and Claude Code |
| [software-performance](../software-performance/SKILL.md) | Performance measurement and regression gates |
| [software-ios-design](../software-ios-design/SKILL.md) | iOS design patterns, HIG compliance, dark mode, dashboard layout |

## Freshness Lookups

Freshness-check before final answers on Xcode/SwiftUI/Swift Testing changes, XcodeBuildMCP setup, iOS privacy manifests, App Store requirements, or any "is X still the default?" question. Start from [data/sources.json](data/sources.json), then Apple Developer docs and WWDC sessions. Prefer Apple docs/release notes for Xcode/SwiftUI/privacy/store; official Anthropic/OpenAI docs for Codex/Claude Code; XcodeBuildMCP repo for tool names and config.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both. After: append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md`.
