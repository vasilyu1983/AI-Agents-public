# Stale-Build Triage

Treat these as stale-build signals until proven otherwise:

- the simulator shows UI that does not exist in current source
- a script says build succeeded but the app still behaves like yesterday’s build
- screenshots from repeated runs do not reflect recent code edits
- sign-in appears to work but downstream screens behave like an older runtime

Default response:

1. locate the built `.app`
2. preserve logs, launch inputs, installed UUID/version, and relevant local-state evidence
3. replace/install the exact successful build artifact while retaining its data container where supported
4. launch it again
5. only then continue with feature debugging

If the fresh install fails, stop there and inspect bundle health.

## os.Logger vs print() for Simulator Log Capture

`print()` outputs to stdout, which is invisible to `simctl log stream`. For debugging decode errors, API responses, or any runtime diagnostics that need to be captured from the simulator console, use `os.Logger`:

```swift
import os

let logger = Logger(subsystem: "com.yourapp", category: "APIClient")

// In your decode error handler; redact private response content before logging:
if let decodingError = error as? DecodingError {
    switch decodingError {
    case .typeMismatch(let type, let ctx):
        logger.error("typeMismatch: expected \(String(describing: type)) at \(ctx.codingPath.map(\.stringValue).joined(separator: "."))")
    case .keyNotFound(let key, let ctx):
        logger.error("keyNotFound: \(key.stringValue) at \(ctx.codingPath.map(\.stringValue).joined(separator: "."))")
    case .valueNotFound(let type, let ctx):
        logger.error("valueNotFound: \(String(describing: type)) at \(ctx.codingPath.map(\.stringValue).joined(separator: "."))")
    case .dataCorrupted(let ctx):
        logger.error("dataCorrupted: \(ctx.debugDescription)")
    @unknown default:
        logger.error("unknown: \(String(describing: decodingError))")
    }
    // Log status/content type and a redacted diagnostic prefix separately.
    // Do not dump auth headers or response bodies containing private data.
}
```

Capture with subsystem filter:
```bash
xcrun simctl spawn "$SIMULATOR_UDID" log stream \
  --predicate 'subsystem == "com.yourapp" AND category == "APIClient"' \
  --level error
```

This is critical for diagnosing "The data couldn't be read because it isn't in the correct format" errors — the `DecodingError` path tells you exactly which field failed and why.

## After `xcodegen` regeneration: "file couldn't be opened" on a previously-green build

You edited `project.yml`, ran `./scripts/generate-xcodeproj.sh` (or `xcodegen`), and the next `xcodebuild` fails with `The file '<something>.plist' couldn't be opened` or `No such file` — pointing at a file that definitely exists on disk.

Compare the generated file path, case, target membership, build settings, and active project before blaming cached state. If paths are correct, rebuild into a separate project-specific DerivedData directory and compare with the failing build. A fresh build distinguishes incremental-state drift without deleting other projects' caches.

Only escalate to a verified project-only cache reset after that comparison implicates cached state. CI generation policy belongs to [software-ios-native](../../software-ios-native/SKILL.md); a regeneration is not itself proof that the cache is corrupt.

## Partial Build Failure + Stale Artifact Installation

When a build has errors in files unrelated to your changes, `xcodebuild` fails but may leave a valid `.app` bundle from a previous successful build in `DerivedData`. Running `simctl install` after a failed build will silently install this stale artifact.

**Gate on the actual build exit status**, not a grep result or a `.app` existing from a previous run. When filtering output, preserve the build status:

```bash
set -o pipefail
xcodebuild <project-and-destination-arguments> 2>&1 | tee build.log
# Proceed to install only when this pipeline exits successfully.
```

Use the exact artifact path from that successful build. A formatter or `tail` can exit 0 even when `xcodebuild` failed if pipeline failure handling is absent.

**Common scenario:** Pre-existing errors in files from concurrent work (e.g., missing types in files you didn't touch) cause build failure, but your files compiled fine individually. The app bundle in DerivedData is from a previous session and doesn't include your changes.
