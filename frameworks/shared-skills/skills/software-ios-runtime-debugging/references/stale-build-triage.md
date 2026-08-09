# Stale-Build Triage

Treat these as stale-build signals until proven otherwise:

- the simulator shows UI that does not exist in current source
- a script says build succeeded but the app still behaves like yesterday’s build
- screenshots from repeated runs do not reflect recent code edits
- sign-in appears to work but downstream screens behave like an older runtime

Default response:

1. locate the built `.app`
2. uninstall the installed app
3. install the fresh bundle
4. launch it again
5. only then continue with feature debugging

If the fresh install fails, stop there and inspect bundle health.

## os.Logger vs print() for Simulator Log Capture

`print()` outputs to stdout, which is invisible to `simctl log stream`. For debugging decode errors, API responses, or any runtime diagnostics that need to be captured from the simulator console, use `os.Logger`:

```swift
import os

let logger = Logger(subsystem: "com.yourapp", category: "APIClient")

// In your decode error handler:
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
    if let raw = String(data: data.prefix(2000), encoding: .utf8) {
        logger.error("raw response: \(raw)")
    }
}
```

Capture with subsystem filter:
```bash
xcrun simctl spawn "iPhone 17 Pro" log stream \
  --predicate 'subsystem == "com.yourapp" AND category == "APIClient"' \
  --level error
```

This is critical for diagnosing "The data couldn't be read because it isn't in the correct format" errors — the `DecodingError` path tells you exactly which field failed and why.

## After `xcodegen` regeneration: "file couldn't be opened" on a previously-green build

You edited `project.yml`, ran `./scripts/generate-xcodeproj.sh` (or `xcodegen`), and the next `xcodebuild` fails with `The file '<something>.plist' couldn't be opened` or `No such file` — pointing at a file that definitely exists on disk.

`xcodegen` reshuffles file-reference UUIDs in `project.pbxproj` on every regeneration. DerivedData's incremental build manifest is keyed by those UUIDs, so after a regen the cached build state points at stale paths. `xcodebuild clean` does **not** clear that cache — it only wipes the last build products, not the DerivedData manifest.

Fix: delete DerivedData for this project entirely, then rebuild:

```bash
rm -rf ~/Library/Developer/Xcode/DerivedData/<ProjectName>-*
xcodebuild -scheme <Scheme> build
```

Prevention: after any `xcodegen` run that changes file membership (new target, renamed resource, added locale), delete DerivedData as a reflex — it is faster than guessing which caches are stale. On CI, do not run `xcodegen` at all; commit the regenerated `.xcodeproj` and let CI build against it directly.

## Partial Build Failure + Stale Artifact Installation

When a build has errors in files unrelated to your changes, `xcodebuild` fails but may leave a valid `.app` bundle from a previous successful build in `DerivedData`. Running `simctl install` after a failed build will silently install this stale artifact.

**Detection heuristic:** If you see behavior that doesn't match your latest code changes, check whether the build actually succeeded:

```bash
# Check the build result — don't just grep for YOUR errors
xcodebuild ... 2>&1 | tail -3
# Look for "BUILD SUCCEEDED" vs "BUILD FAILED"
```

**Prevention:** Only install after confirming build success:
```bash
xcodebuild ... && xcrun simctl install ...
# The && ensures install only runs on success
```

**Common scenario:** Pre-existing errors in files from concurrent work (e.g., missing types in files you didn't touch) cause build failure, but your files compiled fine individually. The app bundle in DerivedData is from a previous session and doesn't include your changes.
