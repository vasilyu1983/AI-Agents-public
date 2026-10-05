# Native iOS App Foundation Skeleton

Use this reference when the user wants a maximum-flexibility native iOS skeleton that can start most new apps without Supabase, Vercel, or a custom backend by default.

## Table of Contents

- [Default Stack](#default-stack)
- [Module Layout](#module-layout)
- [Decision Matrix](#decision-matrix)
- [Extension Points](#extension-points)
- [Proof Gates](#proof-gates)
- [Anti-Patterns](#anti-patterns)

## Default Stack

Use this as the current default for a new Apple-native app (verify current toolchain versions at developer.apple.com/xcode):

| Layer | Default | Why |
|---|---|---|
| UI | SwiftUI | Standard new-screen default; UIKit only for mature API gaps |
| State | Observation with `@Observable`, `@State`, `@Bindable` | Native iOS 17+ state model |
| Actor isolation | Default Main Actor Isolation for app target | Reduces accidental off-main UI state mutation |
| Navigation | `NavigationStack` + typed route enum | Testable and reusable across feature modules |
| Local persistence | SwiftData first | Fastest product iteration for local structured data |
| Mature persistence | Core Data | Use when migrations, batch work, or existing stores dominate |
| iCloud sync | SwiftData/Core Data backed by CloudKit private database | Apple-account sync without a web backend |
| Local AI | `software-ios-ai-engine` facade | Keeps Foundation Models and retrieval optional |
| System exposure | App Intents | Siri, Spotlight, Shortcuts, widgets, controls, Apple Intelligence |
| Testing | Swift Testing + XCTest/XCUITest | Unit/integration vs UI/performance split |
| Release | Xcode Cloud/TestFlight proof gates | Matches App Store signing and capability behavior |

This skeleton is intentionally Apple-native. It is not a full replacement for server-owned admin jobs, cross-platform dashboards, shared web clients, or regulated backend audit trails.

## Module Layout

```text
App/
  AppMain.swift
  AppEnvironment.swift
  AppCoordinator.swift
  AppRoute.swift
DesignSystem/
  AppTheme.swift
  Components/
Features/
  Home/
  Onboarding/
  Settings/
Persistence/
  Models/
  SwiftDataStack.swift
  CoreDataCloudKitStack.swift
  CloudKitStatusStore.swift
  MigrationPlan.swift
AI/
  LocalAIEngine.swift
  FoundationModelsComposer.swift
  LocalRetrievalIndex.swift
  AIContracts.swift
Intents/
  AppIntentRegistry.swift
  AppEntities.swift
Search/
  LocalSearchIndex.swift
  SemanticSearchService.swift
Services/
  NetworkMonitor.swift
  EntitlementStore.swift
  NotificationRouter.swift
  DeepLinkRouter.swift
TestingSupport/
  Fixtures/
  LaunchArguments.swift
```

The skeleton should compile with the AI and CloudKit modules present but capability-gated. Unsupported devices or users with Apple Intelligence disabled must still run through deterministic local paths.

## Decision Matrix

| Requirement | Use | Avoid |
|---|---|---|
| Private user data across the user's Apple devices | SwiftData + CloudKit private database | Custom backend by default |
| Complex migration, batch import, app extensions, mature sync | Core Data + `NSPersistentCloudKitContainer` | Hand-rolled sync |
| User-to-user collaboration | Core Data CloudKit sharing or direct CloudKit sharing | SwiftData automatic private sync only |
| Public catalog readable by all users | Direct CloudKit public database | Treating private database as shared data |
| Server-owned writes, moderation, cron, admin console | Custom backend or BaaS | CloudKit-only skeleton |
| Local AI transformation/extraction/summarization | Foundation Models behind `LocalAIEngine` | Raw model text in the UI |
| Small local semantic search | Natural Language embeddings or local vector table | Server vector DB first |
| Large corpus or cross-platform vector search | `ai-vector-brain` upstream service | Forcing all vectors onto-device |

## Extension Points

- `AppEnvironment` owns dependency construction and test doubles.
- `AppCoordinator` owns navigation path, deep-link staging, and post-auth resume.
- `Persistence` exposes repositories or services; views do not reach directly into arbitrary model contexts.
- `AIContracts` defines typed input/output. Foundation Models, sentence bank, and retrieval stitch all return the same Swift type.
- `LocalRetrievalIndex` exposes top-k retrieval to both search UI and Foundation Models tools.
- `AppIntentRegistry` declares actions and entities once, then reuses them for Siri, Spotlight, Shortcuts, widgets, and controls.
- `EntitlementStore` is StoreKit-ready but starts as a no-op for free apps.

## Proof Gates

Before treating the skeleton as reusable:

1. `make build` or equivalent `xcodebuild` compile gate passes on a fresh clone.
2. `make test` runs Swift Testing/XCTest with an `.xcresult` artifact.
3. Fresh uninstall/install/launch smoke passes on a simulator.
4. At least one real-device smoke is documented for CloudKit, Apple Intelligence, StoreKit, APNs, camera, biometrics, or background work if those modules are enabled.
5. CloudKit schema compatibility is checked before production promotion.
6. App Intents compile and have stable identifiers; removing intents requires deprecation, not deletion.
7. Foundation Models path is gated by runtime availability and has a deterministic fallback.
8. Local retrieval has a small eval set with expected top-k evidence.
9. Privacy manifest and required-reason APIs are audited before archive.

## Anti-Patterns

- Building a BaaS-shaped skeleton when the stated constraint is Apple-native iCloud data.
- Making SwiftData models depend on server IDs or backend-only invariants before the app has a backend.
- Using CloudKit public database for private user data.
- Assuming SwiftData private sync supports collaboration without a separate sharing design.
- Parsing raw Foundation Models prose instead of using typed contracts.
- Treating App Intents as a late add-on; stable identifiers become user automation contracts.
- Shipping a local vector search with no corpus version, content hash, or eval cases.
