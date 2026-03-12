# Cross-Platform Mobile Framework Comparison

Deep comparison of React Native, Flutter, Kotlin Multiplatform (KMP), and native development. Covers performance, developer experience, ecosystem maturity, app size, CI/CD complexity, migration paths, and team implications.

---

## Framework Overview (2026)

| Dimension | React Native | Flutter | KMP | Native (Swift + Kotlin) |
|-----------|-------------|---------|-----|------------------------|
| **Language** | TypeScript/JavaScript | Dart | Kotlin | Swift (iOS), Kotlin (Android) |
| **UI Rendering** | Native components via bridge/JSI | Custom rendering (Skia/Impeller) | Native UI per platform | Platform-native |
| **Code Sharing** | ~85-95% (UI + logic) | ~90-95% (UI + logic) | ~50-80% (logic only, unless Compose Multiplatform) | 0% |
| **First Release** | 2015 (Meta) | 2017 (Google) | 2020 stable (JetBrains) | Ongoing |
| **Managed Toolchain** | Expo (recommended for greenfield) | Flutter SDK | KMP Gradle plugin | Xcode + Android Studio |

---

## Comprehensive Comparison

### Performance

| Metric | React Native | Flutter | KMP | Native |
|--------|-------------|---------|-----|--------|
| **Cold start** | ~800-1200ms | ~600-1000ms | Native-equivalent | ~400-800ms |
| **Frame rate** | 55-60 FPS (New Architecture) | 58-60 FPS (Impeller) | 60 FPS (native UI) | 60 FPS |
| **Animation** | Good (Reanimated 3) | Excellent (Impeller) | Native-equivalent | Best |
| **JS/Dart overhead** | ~5-15ms bridge latency (JSI reduces this) | ~2-5ms Dart FFI | Zero (compiles to native) | Zero |
| **Heavy computation** | Offload to native modules or JSI | Isolates for parallel work | Kotlin/Native coroutines | GCD/Coroutines |
| **Memory footprint** | Higher (+30-50MB JS runtime) | Higher (+20-40MB Dart runtime) | Near-native | Baseline |

### Real-World Performance Data

```text
Benchmarks vary by app complexity. Typical production findings:

React Native (New Architecture + Hermes):
  - App launch: 0.8-1.2s (comparable to native for simple apps)
  - List scrolling: 58-60 FPS with FlashList
  - Memory: +30-50MB over native baseline

Flutter (Impeller on iOS):
  - App launch: 0.6-1.0s
  - List scrolling: 59-60 FPS
  - Memory: +20-40MB over native baseline

KMP (shared logic, native UI):
  - App launch: Native-equivalent
  - List scrolling: 60 FPS (native UI)
  - Memory: Near-native (+5-10MB for KMP runtime)

Native:
  - App launch: 0.4-0.8s (baseline)
  - List scrolling: 60 FPS (baseline)
  - Memory: Baseline
```

### Developer Experience

| Aspect | React Native | Flutter | KMP | Native |
|--------|-------------|---------|-----|--------|
| **Hot reload** | Fast Refresh (excellent) | Hot Reload (excellent) | No hot reload for native UI | SwiftUI Previews, Compose Preview |
| **Debugging** | Chrome DevTools, Flipper, React DevTools | Dart DevTools, Widget Inspector | Android Studio + Xcode | Platform-native debuggers |
| **IDE** | VS Code, WebStorm | VS Code, Android Studio, IntelliJ | Android Studio, IntelliJ | Xcode, Android Studio |
| **Type safety** | TypeScript (optional but standard) | Dart (sound null safety) | Kotlin (excellent) | Swift/Kotlin (excellent) |
| **Learning curve** | Low (JS/TS developers) | Medium (Dart is easy, widgets are new) | Medium (Kotlin, platform APIs) | High (two platforms, two languages) |
| **Community** | Very large, npm ecosystem | Large, growing | Growing, Kotlin ecosystem | Largest (platform-official) |

### Ecosystem and Plugin Availability

| Category | React Native | Flutter | KMP | Native |
|----------|-------------|---------|-----|--------|
| **Camera** | react-native-camera, Expo Camera | camera package | Native per platform | AVFoundation, CameraX |
| **Maps** | react-native-maps | google_maps_flutter | Native per platform | MapKit, Google Maps SDK |
| **Push** | react-native-firebase, Expo Notifications | firebase_messaging | Native per platform | APNs SDK, FCM SDK |
| **Auth/Biometrics** | Expo LocalAuthentication | local_auth | Native per platform | AuthenticationServices, BiometricPrompt |
| **Payments** | RevenueCat, Stripe RN | RevenueCat, Stripe Flutter | RevenueCat, native SDKs | StoreKit 2, Google Play Billing |
| **Storage** | AsyncStorage, WatermelonDB, MMKV | sqflite, Hive, Isar | SqlDelight (shared) | Core Data/SwiftData, Room |
| **Navigation** | React Navigation, Expo Router | GoRouter, auto_route | Native per platform | NavigationStack, Navigation Component |
| **Plugin gap risk** | Low (large ecosystem) | Medium (growing) | Low (uses native directly) | None |

### App Size Comparison

| Framework | Minimal App | Medium App | Notes |
|-----------|------------|------------|-------|
| React Native | ~8-15 MB | ~25-50 MB | Hermes reduces JS bundle size |
| Flutter | ~12-20 MB | ~30-60 MB | Skia/Impeller engine adds baseline |
| KMP | ~5-10 MB | ~20-40 MB | Shared logic adds ~2-5 MB |
| Native (iOS) | ~3-8 MB | ~15-35 MB | Baseline |
| Native (Android) | ~3-8 MB | ~15-35 MB | Baseline |

### CI/CD Complexity

| Aspect | React Native | Flutter | KMP | Native |
|--------|-------------|---------|-----|--------|
| **Build system** | Metro + Xcode + Gradle | Flutter SDK + Xcode + Gradle | Gradle + Xcode | Xcode / Gradle |
| **Build time** | 5-15 min (both platforms) | 5-15 min (both platforms) | 5-10 min per platform | 3-8 min per platform |
| **CI runners** | macOS (for iOS) + Linux (Android) | macOS (for iOS) + Linux (Android) | macOS (for iOS) + Linux (Android) | macOS (iOS) + Linux (Android) |
| **OTA updates** | EAS Update (Expo), CodePush | Shorebird (emerging) | Not applicable | Not applicable |
| **Dependency resolution** | npm + CocoaPods/SPM + Gradle | pub + CocoaPods + Gradle | Gradle + SPM/CocoaPods | SPM/CocoaPods + Gradle |
| **CI config complexity** | High (3 package managers) | Medium (2 build systems) | Medium (2 build systems) | Low (1 per platform) |

---

## State Management Comparison

| Approach | React Native | Flutter | KMP | Native |
|----------|-------------|---------|-----|--------|
| **Recommended default** | Zustand or Redux Toolkit | Riverpod or BLoC | ViewModel + StateFlow | @Observable (iOS), ViewModel + StateFlow (Android) |
| **Simple apps** | Context + useState | setState + InheritedWidget | — | @State (iOS), Compose State (Android) |
| **Complex apps** | Redux Toolkit + RTK Query | Riverpod + Freezed | Shared ViewModel with KMP-ViewModel | TCA (iOS), MVI (Android) |
| **Server state** | React Query / RTK Query | Riverpod AsyncValue | Ktor + Flow | URLSession + async/await, Retrofit + Flow |
| **Persistence** | MMKV, AsyncStorage | SharedPreferences, Hive | Settings (multiplatform) | UserDefaults, DataStore |

---

## Testing Framework Comparison

| Layer | React Native | Flutter | KMP | Native (iOS) | Native (Android) |
|-------|-------------|---------|-----|-------------|-----------------|
| **Unit** | Jest | flutter_test | kotlin.test | Swift Testing / XCTest | JUnit |
| **Widget/Component** | React Native Testing Library | flutter_test (widget test) | — | ViewInspector | Compose Test |
| **Integration** | Detox | integration_test | — | XCUITest | Espresso |
| **E2E** | Maestro, Detox | integration_test, Maestro | — | Maestro | Maestro |
| **Snapshot** | jest (snapshots) | golden tests | — | swift-snapshot-testing | Paparazzi, Roborazzi |

---

## Cost of Ownership

### Year-1 Development Cost Comparison (Illustrative)

```text
Assumptions: Medium-complexity app, 3 major features, both platforms

Native (separate teams):
  2 iOS devs + 2 Android devs = 4 developers
  Timeline: 6 months
  Total: ~4 x 6 = 24 person-months

React Native:
  2 RN devs + 0.5 native specialist (consulting) = 2.5 developers
  Timeline: 5 months
  Total: ~2.5 x 5 = 12.5 person-months

Flutter:
  2 Flutter devs + 0.5 native specialist = 2.5 developers
  Timeline: 5 months
  Total: ~2.5 x 5 = 12.5 person-months

KMP (shared logic, native UI):
  1 KMP dev + 1 iOS dev + 1 Android dev = 3 developers
  Timeline: 5.5 months
  Total: ~3 x 5.5 = 16.5 person-months

Note: These are rough estimates. Actual costs vary significantly
by team experience, app complexity, and native feature requirements.
```

### Long-Term Maintenance Cost Factors

| Factor | React Native | Flutter | KMP | Native |
|--------|-------------|---------|-----|--------|
| **Framework upgrades** | Major version upgrades can be painful (RN → New Architecture) | Generally smooth | Relatively stable | Xcode/Android Studio updates |
| **OS update compatibility** | Lag of days-weeks for new OS features | Lag of days-weeks | Immediate (native UI) | Immediate |
| **Bug surface area** | Framework + bridge + native | Framework + engine + native | Shared logic + native UI | Platform only |
| **Dependency maintenance** | npm: frequent updates, breaking changes | pub: moderate frequency | Gradle: mature ecosystem | SPM/CocoaPods: mature |

---

## Real-World Framework Adoption

### Notable Apps by Framework (as of 2026)

| Framework | Apps | Notes |
|-----------|------|-------|
| **React Native** | Instagram, Facebook, Shopify, Discord, Bloomberg, Coinbase | Largest enterprise adoption |
| **Flutter** | Google Pay, BMW, eBay Motors, Alibaba (Xianyu), Nubank | Growing enterprise adoption |
| **KMP** | Netflix, Cash App, VMware, Philips, McDonald's | Shared logic, native UI |
| **Native** | Most banking apps, Apple apps, Google apps | Default for high-stakes apps |

---

## Decision Framework

### Weighted Criteria Matrix

Score each criterion 1-5 for your project, then multiply by weight.

| Criterion | Weight | React Native | Flutter | KMP | Native |
|-----------|--------|-------------|---------|-----|--------|
| Time to market | varies | 5 | 5 | 3 | 2 |
| Performance requirements | varies | 3 | 4 | 5 | 5 |
| Platform fidelity | varies | 4 | 3 | 5 | 5 |
| Code sharing % | varies | 5 | 5 | 3 | 1 |
| Team JS/TS experience | varies | 5 | 1 | 2 | 1 |
| Team Kotlin experience | varies | 2 | 1 | 5 | 3 |
| Team Dart experience | varies | 1 | 5 | 1 | 1 |
| Long-term maintenance | varies | 3 | 3 | 4 | 5 |
| Plugin/SDK availability | varies | 4 | 3 | 5 | 5 |
| Hiring availability | varies | 5 | 3 | 3 | 4 |

### When to Choose Each

```text
Choose React Native when:
  ✓ Team has JavaScript/TypeScript expertise
  ✓ Rapid prototyping or MVP is the priority
  ✓ Web developers transitioning to mobile
  ✓ OTA updates are valuable (Expo EAS Update)
  ✓ Large npm ecosystem overlap with web app
  ✓ Hiring from web developer pool

Choose Flutter when:
  ✓ Custom, pixel-perfect UI across both platforms
  ✓ Heavy animation and custom rendering
  ✓ Team is willing to learn Dart
  ✓ Consistent look and feel matters more than platform fidelity
  ✓ Greenfield project with no existing codebase
  ✓ Desktop/web targets from same codebase

Choose KMP when:
  ✓ Team has Kotlin expertise
  ✓ Native UI experience is non-negotiable
  ✓ Sharing business logic (not UI) is the goal
  ✓ Existing native apps that need shared logic
  ✓ Performance-critical domains (finance, media)
  ✓ Gradual adoption into existing native codebase

Choose Native when:
  ✓ Maximum performance and platform integration
  ✓ Heavy use of platform-specific APIs (AR, ML, health)
  ✓ Separate iOS and Android teams already exist
  ✓ App Store review sensitivity (Apple prefers native)
  ✓ Long-lived product with decade+ maintenance horizon
  ✓ Budget supports two codebases
```

---

## Migration Paths

### From Native to Cross-Platform

| Path | Strategy | Risk | Timeline |
|------|----------|------|----------|
| Native → React Native | Brownfield: embed RN views in native app | Medium | 3-6 months |
| Native → Flutter | Add-to-app: embed Flutter modules | Medium | 3-6 months |
| Native → KMP | Extract shared logic to KMP module | Low | 2-4 months |
| Native → KMP + Compose Multiplatform | Shared logic + shared UI | High | 6-12 months |

### From Cross-Platform to Native

| Path | Strategy | Risk | Timeline |
|------|----------|------|----------|
| React Native → Native | Rewrite screen by screen | Medium-High | 6-12 months |
| Flutter → Native | Full rewrite (no incremental path) | High | 6-12 months |
| KMP → Native | Remove shared module, duplicate logic | Low | 2-4 months |

### Between Cross-Platform Frameworks

| Path | Feasibility | Notes |
|------|------------|-------|
| React Native → Flutter | Full rewrite | Different language, paradigm |
| Flutter → React Native | Full rewrite | Different language, paradigm |
| React Native → KMP | Extract logic to Kotlin, keep or replace UI | Moderate effort |
| KMP → React Native | Rewrite shared logic in TypeScript | Moderate effort |

---

## Team Skill Requirements and Hiring

### Minimum Team Composition

| Framework | Minimum Team | Ideal Team | Hiring Pool Size |
|-----------|-------------|------------|-----------------|
| React Native | 2 RN developers | 2 RN + 1 iOS native + 1 Android native | Very large (web devs) |
| Flutter | 2 Flutter developers | 3 Flutter + 1 native specialist | Growing |
| KMP | 1 Kotlin + 1 iOS + 1 Android | 2 Kotlin + 1 iOS + 1 Android | Medium |
| Native | 2 iOS + 2 Android | 3 iOS + 3 Android | Large (per platform) |

### Ramp-Up Time for New Hires

| Background | React Native | Flutter | KMP | Native |
|-----------|-------------|---------|-----|--------|
| Web developer (JS/TS) | 2-4 weeks | 6-8 weeks | 8-12 weeks | 12-16 weeks |
| iOS developer (Swift) | 4-6 weeks | 6-8 weeks | 4-6 weeks | 0 |
| Android developer (Kotlin) | 4-6 weeks | 6-8 weeks | 2-4 weeks | 0 |
| Flutter developer (Dart) | 4-6 weeks | 0 | 8-12 weeks | 12-16 weeks |

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Choosing framework based on hype | Mismatch with team skills and requirements | Use weighted decision matrix |
| Assuming 100% code sharing | Native modules always needed for some features | Budget 10-20% platform-specific code |
| Ignoring native developer needs | Cross-platform teams still need native expertise | Hire at least one native specialist per platform |
| Starting migration without brownfield plan | Big-bang rewrite fails | Adopt incrementally (embed, module-by-module) |
| Benchmarking with toy apps | Real performance differs from Hello World | Benchmark with production-representative features |
| Ignoring CI/CD complexity | Build pipeline becomes bottleneck | Evaluate CI/CD cost and complexity early |

---

## Cross-References

- [mobile-testing-patterns.md](mobile-testing-patterns.md) — Testing strategies per platform and framework
- [offline-first-architecture.md](offline-first-architecture.md) — Local database strategies per platform
- [ios-best-practices.md](ios-best-practices.md) — iOS-specific architecture and patterns
- [android-best-practices.md](android-best-practices.md) — Android-specific architecture and patterns
- [operational-playbook.md](operational-playbook.md) — Mobile architecture patterns and decision tables
