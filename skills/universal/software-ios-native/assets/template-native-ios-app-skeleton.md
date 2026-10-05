# Native iOS App Skeleton Template

Use this as the starting checklist for a reusable SwiftUI app foundation.

## File Layout

```text
App/
  AppMain.swift
  AppEnvironment.swift
  AppCoordinator.swift
  AppRoute.swift
DesignSystem/
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
  AIContracts.swift
  LocalAIEngine.swift
  FoundationModelsComposer.swift
  LocalRetrievalIndex.swift
Intents/
  AppIntentRegistry.swift
  AppEntities.swift
Services/
  NetworkMonitor.swift
  EntitlementStore.swift
  NotificationRouter.swift
  DeepLinkRouter.swift
TestingSupport/
```

## Defaults

- SwiftUI for new screens.
- Observation for UI-facing state.
- `@MainActor` app services unless they genuinely coordinate background work.
- SwiftData + CloudKit private sync for user-owned structured data.
- Core Data + CloudKit for mature migration or sharing needs.
- App Intents from the first feature that has a stable user action.
- `LocalAIEngine` facade even when the first implementation is deterministic.
- Foundation Models and local vector retrieval behind capability gates.

## Required Gates

- Fresh clone build.
- Fresh uninstall/install/launch.
- Swift Testing or XCTest lower-layer tests.
- XCUITest smoke for onboarding/settings/home.
- Privacy manifest review.
- Archive/signing check before TestFlight.
- Real-device checks for CloudKit, Apple Intelligence, StoreKit, APNs, biometrics, camera, and background work when enabled.
