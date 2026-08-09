# iOS CI (GitHub Actions)

GitHub Actions specifics for iOS testing. Re-check runner-image availability before copying any pin.

Primary source:

- https://github.com/actions/runner-images

## Table of Contents

- [Why this matters](#why-this-matters)
- [Recommended Posture](#recommended-posture)
- [Runner Labels](#runner-labels-as-of-july-2026)
- [Example Workflow](#example-workflow)
- [What To Avoid](#what-to-avoid)
- [Drift Checks](#drift-checks)
- [Optional Extras](#optional-extras)
- [When To Escalate To Self-Hosted macOS](#when-to-escalate-to-self-hosted-macos)
- [Cost Notes](#cost-notes)

## Why this matters

- GitHub-hosted macOS images change weekly
- `macos-latest` migrates over time
- simulator runtimes can disappear from a runner image even when the OS label stays the same

## Recommended Posture

- Prefer explicit OS labels over `macos-latest` for stability.
- Verify the available Xcode version on the runner before selecting it.
- Verify destinations before the test run.
- Upload `xcresult` even on cancelled or failed jobs.

## Runner Labels (as of July 2026)

- `macos-26`: GA since February 26, 2026 ([GitHub changelog](https://github.blog/changelog/2026-02-26-macos-26-is-now-generally-available-for-github-hosted-runners/)). Ships Xcode 26 as the base Xcode. Runs natively on Apple Silicon (arm64). Use for new projects targeting iOS 26 SDK.
- `macos-latest` migration: GitHub began rolling `macos-latest` from `macos-15` to `macos-26` starting June 15, 2026, over several weeks. By July 2026, `macos-latest` should already resolve to `macos-26` in most workflows — re-verify with `xcodebuild -version` in the job rather than assuming, since staged rollouts do not land on every account the same day.
- `macos-15`: Still available under explicit label. Carries Xcode 16 series. Use when you need Xcode 16 stability while incrementally adopting Xcode 26, or when `macos-latest` drifted out from under you mid-migration and you need a pinned fallback.
- `macos-26-large` / `macos-26-intel` / `macos-26-xlarge`: Intel (x64) variants of the macOS 26 image family.

Known issue: Xcode 26.0.1 on `macos-26-xlarge` runners had a bug where iOS test jobs hang indefinitely after test discovery with 0 tests executed. Upgrade to Xcode 26.0.1+ patch or a newer minor; confirm the job exits before relying on these runners.

## Example Workflow

```yaml
name: iOS CI

on:
  pull_request:
  push:

jobs:
  test:
    runs-on: macos-26
    steps:
      - uses: actions/checkout@v4

      - name: Print Xcode version
        run: xcodebuild -version

      - name: Print available destinations
        run: xcodebuild -workspace MyApp.xcworkspace -scheme MyApp -showdestinations

      - name: Resolve packages
        run: xcodebuild -resolvePackageDependencies -workspace MyApp.xcworkspace -scheme MyApp

      - name: Run tests
        run: |
          set -euo pipefail
          xcodebuild test \
            -workspace MyApp.xcworkspace \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=<simulator-name>,OS=latest' \
            -resultBundlePath TestResults.xcresult

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: TestResults
          path: TestResults.xcresult
```

## What To Avoid

- Hardcoding `/Applications/Xcode_16.0.app` or `/Applications/Xcode_26.0.app` style paths in shared docs
- Assuming `macos-latest` is safe for reproducibility
- Assuming a specific iOS runtime is installed because it was present previously
- Copying stale device names without checking `-showdestinations`
- Using `macos-26` with Xcode 26.0.1 without verifying the test hang bug is not affecting your runner (check runner-images issue tracker before pinning)

## Drift Checks

When a workflow breaks unexpectedly, inspect:

- runner image release notes and announcements
- the `Set up job` log for the image version
- `xcodebuild -version`
- `xcodebuild -showdestinations`
- `xcrun simctl list devices available`

## Optional Extras

Cache decisions should be conservative:

- Swift package resolution cache can help
- DerivedData caching can help, but only if cache invalidation is understood
- do not add cache layers until the baseline job is stable and measurable

## When To Escalate To Self-Hosted macOS

- you need fixed simulator runtimes across long periods
- you need a nonstandard Xcode matrix
- runner-image drift is hurting reliability more than hosted convenience helps

## Cost Notes

macOS runners are the most expensive line item on most iOS repos' CI bill. As of the January 1, 2026 GitHub Actions repricing ([runner pricing docs](https://docs.github.com/en/billing/reference/actions-runner-pricing)), standard macOS (3-4 core) runners bill at roughly $0.062/minute overage, versus ~$0.006/minute for Linux x86 — and macOS minutes still consume the monthly included-minutes pool at a 10x multiplier. A 15-minute smoke run costs the same included-minutes budget as 150 Linux minutes.

Re-verify current rates before budgeting — GitHub has repriced macOS runners before and may again. When the bill matters:

- keep PR-gate suites thin (see `## Principles` in `ios-ci-general.md`) — this is a cost lever, not just a flake lever.
- compare against Xcode Cloud's compute-hour pricing (see `ios-ci-general.md → CI Platform Choice`) before defaulting to GitHub-hosted macOS for high-volume release or nightly matrices.
- self-hosted macOS (Mac minis, cloud Mac providers) amortizes better than pay-per-minute once volume is high and stable; re-evaluate the crossover point periodically rather than assuming hosted is always cheaper at small scale.
