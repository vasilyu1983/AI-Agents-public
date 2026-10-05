# iOS CI (GitHub Actions)

GitHub Actions specifics for iOS testing. Re-check runner-image availability before copying any pin.

Primary source:

- https://github.com/actions/runner-images

## Table of Contents

- [Why this matters](#why-this-matters)
- [Recommended Posture](#recommended-posture)
- [Runner Labels](#runner-labels)
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

## Runner Labels

Read the [runner-images inventory](https://github.com/actions/runner-images) and [hosted-runner reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners) before selecting a label. Check the label's architecture, installed Xcode versions, simulator runtimes, and announced removal dates. Larger and standard runners can have different architecture suffixes; do not infer arm64 or Intel from a marketing label. Set the tested label in `IOS_RUNNER_LABEL` and print the resolved image/Xcode in the job.

`macos-latest` changes its underlying image during staged rollouts. An explicit OS label still receives image updates, so verify installed destinations in each run.

If an iOS test job hangs after test discovery with 0 tests executed, use `-test-timeouts-enabled YES` with `-default-test-execution-time-allowance`/`-maximum-test-execution-time-allowance` so the job fails fast instead of hanging, and file or search `actions/runner-images` for the current status rather than assuming an upgrade fixes it.

## Example Workflow

Replace both action placeholders with reviewed commit SHAs from the owning action releases and set `IOS_RUNNER_LABEL` to the tested hosted label before using this example.

```yaml
name: iOS CI

on:
  pull_request:
  push:

jobs:
  test:
    runs-on: ${{ vars.IOS_RUNNER_LABEL }}
    steps:
      - uses: actions/checkout@<reviewed-commit-sha>

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
        uses: actions/upload-artifact@<reviewed-commit-sha>
        with:
          name: TestResults
          path: TestResults.xcresult
```

## What To Avoid

- Hardcoding `/Applications/Xcode_16.0.app` or `/Applications/Xcode_26.0.app` style paths in shared docs
- Assuming `macos-latest` is safe for reproducibility
- Assuming a specific iOS runtime is installed because it was present previously
- Copying stale device names without checking `-showdestinations`
- Assuming an Xcode upgrade fixes a runner hang without reproducing on the selected image

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

Use the [runner pricing docs](https://docs.github.com/en/billing/reference/actions-runner-pricing) and your measured billed duration to compare macOS runner cost with Xcode Cloud or a self-hosted Mac. Include idle capacity and maintenance costs in the latter comparison.

GitHub has repriced macOS runners before and may again. When the bill matters:

- keep PR-gate suites thin (see `## Principles` in `ios-ci-general.md`) — this is a cost lever, not just a flake lever.
- compare against Xcode Cloud's compute-hour pricing (see `ios-ci-general.md → CI Platform Choice`) before defaulting to GitHub-hosted macOS for high-volume release or nightly matrices.
- evaluate self-hosted macOS at sustained volume using measured utilization and maintenance overhead; compute the crossover instead of assuming a cheaper platform.
