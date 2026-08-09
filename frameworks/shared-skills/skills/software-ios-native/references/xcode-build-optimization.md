# Xcode Build Optimization

Methodology for measuring, analyzing, and improving Xcode build times. Wall-clock build time is the primary metric.

Primary docs:

- https://developer.apple.com/documentation/xcode/improving-the-speed-of-incremental-builds
- https://developer.apple.com/videos/play/wwdc2022/110364/

## Table of Contents

- [Principles](#principles)
- [Benchmarking](#benchmarking)
- [Compilation Analysis](#compilation-analysis)
- [Project-Level Analysis](#project-level-analysis)
- [SPM Dependency Analysis](#spm-dependency-analysis)
- [Common Wins](#common-wins)
- [Diagnostic Flags](#diagnostic-flags)
- [Workflow](#workflow)

## Principles

1. **Wall-clock time is the primary metric.** Cumulative task time is diagnostic only — it measures total CPU work, not what the developer waits for.
2. **Benchmark before optimizing.** Never change build settings based on assumptions about what's slow.
3. **Never modify project settings without approval.** Recommend first, execute only after review.
4. **Re-benchmark after every change.** Verify the improvement is real and no regression was introduced.
5. **Best-practice settings are never revert candidates.** Even if they don't measurably improve build time, correctness settings stay.

## Benchmarking

### Build Types to Measure

| Build Type | What It Measures | Command |
|---|---|---|
| **Clean build** | Full compilation cost | `xcodebuild clean build` |
| **Cached clean build** | Compilation caching effectiveness (Xcode 16+) | Auto-detected when `COMPILATION_CACHE_ENABLE_CACHING = YES` |
| **Zero-change build** | Overhead floor (indexing, script phases, planning) | Build immediately after a successful build |
| **Incremental build** | Impact of a typical edit | Build after touching a specific file |

### Methodology

- Run **3 iterations** of each build type
- Report **medians and spread** (max - min)
- If spread exceeds **20% of median**, results are unreliable — investigate environment noise (Spotlight indexing, other processes, thermal throttling)
- Record hardware, Xcode version, macOS version, and any relevant environment state

### Timing Commands

```bash
# Clean build with timing
time xcodebuild -workspace MyApp.xcworkspace -scheme MyApp \
    -destination 'generic/platform=iOS' \
    clean build 2>&1 | tail -5

# Zero-change build
time xcodebuild -workspace MyApp.xcworkspace -scheme MyApp \
    -destination 'generic/platform=iOS' \
    build 2>&1 | tail -5
```

## Compilation Analysis

### Build Timing Summary

After a build, inspect the Build Timing Summary in Xcode's build log or extract it:

Focus areas:
- **CompileSwiftSources** — total Swift compilation time per target
- **SwiftEmitModule** — module emission time (can be 60s+ for large modules)
- **Planning Swift module** — dependency analysis time (30s+ possible for complex graphs)
- **Linking** — often fast but can be slow with many frameworks

### Ranking by Impact

Rank hotspots by **expected wall-clock impact**, not cumulative time. A 10-second task on the critical path matters more than a 30-second task that runs in parallel with something longer.

### Expression Type Checking

The most common Swift-specific compilation bottleneck is complex type inference. Use diagnostic flags to find slow expressions:

```bash
# Add to Other Swift Flags in build settings
-warn-long-expression-type-checking=100  # Warn if type checking takes >100ms
-warn-long-function-bodies=100           # Warn if function body takes >100ms
```

Common patterns that cause slow type checking:
- Missing explicit type annotations on complex expressions
- Long chains of operator overloads
- Complex closures without parameter type annotations
- `AnyObject` protocol constraints
- Large bridging headers
- Missing `final` on classes (prevents devirtualization)
- Monolithic computed properties in view bodies

## Project-Level Analysis

### Build Settings Audit

Check these settings against best practices:

| Setting | Best Practice | Why |
|---|---|---|
| `SWIFT_COMPILATION_MODE` | `wholemodule` for Release, `incremental` for Debug | Whole module is slower but produces better optimized code |
| `DEBUG_INFORMATION_FORMAT` | `dwarf` for Debug (not `dwarf-with-dsym`) | dSYM generation adds significant time in Debug |
| `COMPILATION_CACHE_ENABLE_CACHING` | `YES` (Xcode 16+) | Caches compilation results across builds |
| `BUILD_LIBRARY_FOR_DISTRIBUTION` | `NO` unless shipping a binary framework | Forces module stability, slower compilation |
| `ENABLE_PREVIEWS` | Only in schemes that use previews | Preview support adds compilation overhead |

### Scheme and Target Analysis

- Check target dependencies for unnecessary links
- Check scheme build order — are targets building serially that could be parallel?
- Inspect run script phases — are any running on every build when they could be cached?
- Check for `DEFINES_MODULE = YES` on targets that don't need it

### Run Script Phases

Script phases are a common source of zero-change build overhead:

- Add input/output file lists so Xcode can skip unchanged scripts
- Gate debug-only scripts with `if [ "$CONFIGURATION" = "Debug" ]`
- Move linters and formatters to pre-commit hooks instead of build phases
- Check for scripts that touch timestamps (causes cascade rebuilds)
- Check `ExtractAppIntentsMetadata` phase — can add significant time on projects with App Intents
- Check asset catalog compilation time — large catalogs with many image sets can slow builds
- Flag CocoaPods if still present — evaluate migration to SPM for affected dependencies

### Task Backtraces (Xcode 16.4+)

Task Backtraces show the dependency chain for any build task. Use them to identify why a task waited:

```
Build > Show Build Timeline > right-click task > Show Task Backtrace
```

## SPM Dependency Analysis

### What to Check

| Issue | Symptom | Fix |
|---|---|---|
| Unused dependencies | Packages in graph that no target imports | Remove from `Package.swift` |
| Circular dependencies | Build errors or excessive recompilation | Restructure module boundaries |
| Oversized modules (200+ files) | Long `CompileSwiftSources` time | Split into focused modules |
| Umbrella `@_exported import` | Changes cascade across all importers | Remove re-exports; import directly |
| Swift macro packages | Rebuild on every clean build (`swift-syntax` universal builds) | Pin versions, accept the cost, or evaluate alternatives |
| Multi-platform `Package.swift` | Builds for platforms you don't need | Use platform-specific conditions |
| SPM plugin overhead | Plugins run as build tools on every build | Evaluate if the plugin is worth the cost; move to pre-commit |
| Checkout cost | Large repos or many dependencies slow resolution | Pin versions, use binary dependencies where available |
| Configuration drift | Different targets use different Swift settings | Align optimization level, concurrency settings across targets |
| Test target dependencies | Test targets pulling in unnecessary production modules | Minimize test target dependencies; use protocol-based test doubles |

### Verification

Before recommending dependency removal, confirm the package is actually in the dependency graph:

```bash
# Check if a package is referenced in the project
grep -r "PackageName" MyApp.xcodeproj/project.pbxproj
```

### Modular SDK Migration Caveat

Splitting a monolithic target into modular SPM packages increases the number of build tasks. This can improve incremental build times but may worsen clean build times. **Benchmark before recommending.**

## Common Wins

Ranked by typical wall-clock impact:

1. **Skip debug-only run scripts** — gate with configuration check
2. **Add input/output file lists to scripts** — prevents re-running unchanged scripts
3. **Remove serial bottlenecks** — parallelize independent targets
4. **Enable compilation caching** (Xcode 16+) — `COMPILATION_CACHE_ENABLE_CACHING = YES`
5. **Fix stale project structure** — remove dead targets, unused frameworks, orphan file references
6. **Add explicit types to complex expressions** — reduces type checker time
7. **Split oversized targets** — enables parallel compilation
8. **Remove unused SPM dependencies** — reduces graph resolution and checkout time
9. **Mark classes as `final`** — enables devirtualization, reduces compile time
10. **Move linters to pre-commit** — removes per-build overhead

## Diagnostic Flags

| Flag | Purpose | Where to Add |
|---|---|---|
| `-warn-long-expression-type-checking=N` | Warn if expression type-check > N ms | Other Swift Flags |
| `-warn-long-function-bodies=N` | Warn if function body compile > N ms | Other Swift Flags |
| `-debug-time-compilation` | Print per-file compilation time | Other Swift Flags |
| `-debug-time-function-bodies` | Print per-function compilation time | Other Swift Flags |
| `-driver-time-compilation` | Print driver-level timing | Other Swift Flags |
| `-stats-output-dir /path` | Write compilation statistics to directory | Other Swift Flags |

## Regression Evaluation

After applying an optimization:

1. Re-benchmark all build types (clean, cached, zero-change, incremental)
2. Compare medians against baseline
3. If a change causes regression in any build type, evaluate the tradeoff:
   - Compilation caching may slow clean builds but speed up cached builds — net positive
   - Module splitting may increase task count but enable parallelism — benchmark both
4. **Best-practice settings are never revert candidates**, even if they don't measurably improve build time:
   - `DEBUG_INFORMATION_FORMAT = dwarf` (Debug)
   - `SWIFT_COMPILATION_MODE = incremental` (Debug)
   - `GCC_OPTIMIZATION_LEVEL = -Onone` (Debug)
   - `COMPILATION_CACHE_ENABLE_CACHING = YES`
   - `ENABLE_TESTABILITY = YES` (Debug)
   - `SWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG` (Debug)
5. For all other settings, revert if the regression exceeds the improvement in the target build type

## Workflow

1. **Benchmark** the current state (clean, cached, zero-change, incremental)
2. **Analyze** the Build Timing Summary and critical path
3. **Identify** the top 3 wall-clock bottlenecks
4. **Recommend** changes with expected impact language:
   - "Should reduce clean build time by approximately 15-20 seconds"
   - "Expected to eliminate the zero-change rebuild overhead from script phase X"
   - "May improve incremental builds; benchmark to confirm"
5. **Get approval** before modifying project settings
6. **Apply** one change at a time
7. **Re-benchmark** after each change to verify
8. **Report** results with before/after medians, spread, and confidence notes
