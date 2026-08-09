# Cross-Platform Mobile Framework Comparison

Current comparison of React Native, Flutter, Kotlin Multiplatform (KMP), and native development for July 2026. This reference is intentionally qualitative: use it to choose a direction, then validate performance and release risk with platform tooling and current release notes.

---
## Table of Contents

- [Current Landscape](#current-landscape)
- [React Native](#react-native)
- [Flutter](#flutter)
- [Kotlin Multiplatform](#kotlin-multiplatform)
- [Native](#native)
- [Selection Table](#selection-table)
- [Practical Tradeoffs](#practical-tradeoffs)
- [UI Model](#ui-model)
- [Tooling And Release Flow](#tooling-and-release-flow)
- [Performance And Measurement](#performance-and-measurement)
- [Upgrade Risk](#upgrade-risk)
- [Current Defaults](#current-defaults)
- [When To Choose Each](#when-to-choose-each)
- [Choose React Native When](#choose-react-native-when)
- [Choose Flutter When](#choose-flutter-when)
- [Choose KMP When](#choose-kmp-when)
- [Choose Native When](#choose-native-when)
- [Migration Guidance](#migration-guidance)
- [Native To Shared](#native-to-shared)
- [Shared To Native](#shared-to-native)
- [Between Shared Frameworks](#between-shared-frameworks)
- [Verification Checklist](#verification-checklist)
- [Source Anchors](#source-anchors)


## Current Landscape

### React Native

- Best fit when the team is strongest in JavaScript or TypeScript and wants shared product velocity across iOS and Android.
- The New Architecture is no longer opt-in or a migration checkbox: current React Native and Expo releases removed the Legacy Architecture entirely, so the bridge-based renderer is not available even as a fallback. Treat "is every native module we depend on migrated" as the real gating question, not "should we adopt the New Architecture."
- Expo-managed apps are usually the fastest greenfield path unless you know early that you need bare-native customization or unsupported SDK work.

### Flutter

- Best fit when shared rendering, animation control, and consistent UI across platforms matter more than strict platform-native look and feel.
- Strong option for teams willing to standardize on Dart and a Flutter-first toolchain.
- Less ideal when a product depends heavily on first-party platform components or incremental adoption inside mature native apps.

### Kotlin Multiplatform

- Best fit when the team wants shared business logic, networking, and data layers while keeping native UI on iOS and Android.
- Compose Multiplatform for iOS is now stable, but shared UI is still a deliberate tradeoff rather than the default choice. Validate library support and native-feature surface area before choosing it.
- Strong brownfield option for existing native teams that want code sharing without a full UI rewrite.

### Native

- Best fit for products with heavy platform integration, demanding performance constraints, long-lived codebases, or highly differentiated platform UX.
- Highest delivery cost when two app teams must move in parallel, but lowest framework-induced ambiguity.

---

## Selection Table

| Constraint | React Native | Flutter | KMP | Native |
|-----------|--------------|---------|-----|--------|
| Fastest path for JS/TS team | Strong fit | Weak fit | Weak fit | Weak fit |
| Custom shared UI across both apps | Good | Strong fit | Partial fit | Weak fit |
| Shared logic with native UI | Possible, but not ideal | Possible, but framework-heavy | Strong fit | No sharing |
| Brownfield adoption into native apps | Moderate | Moderate | Strong fit | N/A |
| Platform fidelity and first-party UX | Good with tradeoffs | Medium | Strong fit | Strong fit |
| Native SDK / device API depth | Medium | Medium | Strong fit | Strong fit |
| Hiring from web ecosystem | Strong fit | Medium | Weak fit | Weak fit |
| Lowest framework risk | Medium | Medium | Medium | Strong fit |

---

## Practical Tradeoffs

### UI Model

- React Native shares UI and business logic, but still requires native knowledge around modules, build pipelines, and platform bugs.
- Flutter gives the most consistent cross-platform UI because it renders its own widgets, which is useful for design-heavy products and less useful when you want platform-native controls everywhere.
- KMP is the cleanest option when you want to share domain code but keep Apple and Android UI idiomatic.
- Native gives the best access to platform conventions, the latest system APIs, and lowest ambiguity during OS changes.

### Tooling And Release Flow

- React Native means JavaScript tooling plus native iOS/Android build systems. Expo reduces setup cost substantially for greenfield apps.
- Flutter centralizes more of the workflow into Flutter tooling, but iOS and Android release processes still matter.
- KMP adds shared-module complexity while preserving native build and release flows.
- Native keeps each platform fully conventional, which simplifies platform-specific debugging and release reviews.

### Performance And Measurement

- Do not use generic benchmark tables to choose a framework.
- Measure startup, scroll, memory, and background behavior on real devices using Instruments on Apple platforms and Macrobenchmark/Baseline Profiles on Android.
- Shared frameworks can perform well for many products, but performance risk rises with heavy lists, media processing, real-time graphics, or extensive bridge/native boundary traffic.

### Upgrade Risk

- React Native upgrade risk is mostly around native modules, the New Architecture boundary, and dependency churn.
- Flutter upgrade risk is mostly around plugin maturity and engine/toolchain changes.
- KMP upgrade risk is mostly around Kotlin, Gradle, iOS packaging, and any shared-UI dependencies.
- Native upgrade risk is mostly platform-driven rather than framework-driven.

---

## Current Defaults

| Area | React Native | Flutter | KMP | Native |
|------|--------------|---------|-----|--------|
| Navigation | Expo Router or React Navigation | GoRouter or auto_route | Native per platform | NavigationStack / Navigation Component |
| State | Zustand or Redux Toolkit | Riverpod or BLoC | ViewModel + StateFlow in shared/domain layers | `@Observable` on iOS, ViewModel + StateFlow on Android |
| Storage | MMKV, SQLite, secure storage | Isar, Hive, secure storage | SqlDelight / shared data layer | SwiftData/Core Data, Room/DataStore |
| Testing | Jest, React Native Testing Library, Detox/Maestro | flutter_test, integration_test, Maestro | kotlin.test plus native UI tests | Swift Testing/XCTest, JUnit/Compose Test/Macrobenchmark |
| OTA / patching | EAS Update when Expo is used | Validate current Flutter patching strategy before committing | Not a core value prop | Platform store delivery |

---

## When To Choose Each

### Choose React Native When

- The team is strongest in TypeScript and wants one shared app codebase.
- Speed to first release matters more than perfect platform fidelity.
- Expo-managed workflow is viable for the product.
- The app needs many standard SaaS/product flows rather than deep platform specialization.

### Choose Flutter When

- Product value depends on shared, highly controlled UI and animation behavior.
- The team is comfortable adopting Dart and Flutter-first tooling.
- Consistency across mobile surfaces matters more than native look-and-feel.

### Choose KMP When

- The team wants shared domain, networking, persistence, and business logic.
- Native UI quality is non-negotiable.
- Existing iOS and Android apps need a realistic incremental sharing path.

### Choose Native When

- The app is platform-heavy, regulated, media-intensive, or deeply dependent on the newest system APIs.
- Separate mobile specialists already exist.
- Long-term platform fidelity matters more than code sharing.

---

## Migration Guidance

### Native To Shared

- Native to React Native: good when a product team wants faster cross-platform delivery and can tolerate JavaScript plus native build complexity.
- Native to Flutter: strongest when the goal is a shared custom UI surface rather than incremental adoption.
- Native to KMP: safest incremental path when the immediate goal is shared business logic, not shared UI.

### Shared To Native

- React Native or Flutter to native usually means targeted rewrites around performance hotspots or platform-heavy domains.
- KMP to native is usually the least disruptive because UI is already native.

### Between Shared Frameworks

- React Native to Flutter or Flutter to React Native is typically a rewrite, not a migration.
- React Native to KMP can work if the end-state is shared logic plus native UI, but plan it as a gradual product architecture change, not a package swap.

---

## Verification Checklist

- Check the current React Native architecture and upgrading docs before recommending RN versions or migration effort.
- Check Expo changelog, Router, and screen-tracking docs before recommending managed workflow defaults.
- Check Flutter release notes and package maturity before recommending specific plugin-heavy integrations.
- Check Kotlin Multiplatform and Compose Multiplatform release notes before recommending shared UI on iOS.
- If performance is a deciding factor, require project-specific measurement rather than generic framework claims.

---

## Source Anchors

- React Native: official architecture and upgrading docs
- Expo: official changelog, Router, and screen-tracking docs
- Flutter: official docs and release notes
- Kotlin Multiplatform / Compose Multiplatform: official Android and JetBrains release guidance
- Apple / Android performance: Instruments, Baseline Profiles, Macrobenchmark
