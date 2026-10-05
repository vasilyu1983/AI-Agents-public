# scripts/

Utility scripts for the `qa-testing-ios` skill.

---

## xcresult_to_junit.py

Converts an `.xcresult` bundle produced by `xcodebuild` into a JUnit XML file
that CI systems (GitHub Actions, Bitrise, Jenkins, CircleCI) can ingest for
test-result publishing and trend tracking.

**Requirements:**
- Python 3.9+ (stdlib only — no third-party dependencies)
- Xcode 16+ (`xcresulttool get test-results {tests,summary}` subcommands; test fixtures captured from Xcode 27.0)

### Usage

```bash
python3 scripts/xcresult_to_junit.py <bundle.xcresult> [--output junit.xml]
# or, from already-saved xcresulttool JSON (e.g. for testing):
python3 scripts/xcresult_to_junit.py --tests-json tests.json [--summary-json summary.json] [--output junit.xml]
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `<bundle.xcresult>` | One of this or `--tests-json` | — | Path to the `.xcresult` bundle; the script runs both `get test-results tests` and `get test-results summary` against it |
| `--tests-json <path>` | One of this or `<bundle.xcresult>` | — | Saved output of `xcresulttool get test-results tests` |
| `--summary-json <path>` | No | — | Saved output of `xcresulttool get test-results summary`, used as a cross-check |
| `--output <path>` | No | `junit.xml` | Output file path |

**Exit codes:**

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Usage error, `xcrun` not found, or input path missing |
| 2 | `xcresulttool` returned a non-zero exit code |
| 3 | Unexpected JSON structure, or no `Test Case` nodes found |
| 4 | The JUnit counts disagree with the `get test-results summary` counts (only when a summary is available) |

**Examples:**

```bash
# Basic conversion (also cross-checks against the summary)
python3 xcresult_to_junit.py TestResults.xcresult

# Custom output path
python3 xcresult_to_junit.py TestResults.xcresult --output reports/junit.xml

# Show help
python3 xcresult_to_junit.py --help
```

### How it works

1. Runs `xcrun xcresulttool get test-results tests --path <bundle> --format json` (and `get test-results summary` for the cross-check).
2. Walks the test node tree and treats each `Test Case` node as one test — never a leaf detail node. A failed `Test Case` carries child nodes (`Failure Message`, `Runtime Warning`, `Expected Failure`, `Arguments`) that are never counted as separate tests.
3. Groups test cases under their `Test Suite` (or bundle) ancestor.
4. Emits a standard JUnit XML document:
   - `<testsuites>` — top-level container with aggregate counts
   - `<testsuite>` — one element per discovered test suite
   - `<testcase>` — one element per test, with `<failure>` for failed tests (message text pulled from the `Failure Message` children), `<error>` for a result the script does not recognise, and `<skipped>` for skipped tests. A Swift Testing `withKnownIssue` expected failure is recorded as a pass with the known-issue text in `<system-out>`.
5. If `--summary-json` (or the bundle path, which fetches it automatically) is available, compares the parsed failure/error/test counts against the summary and exits 4 on a mismatch — so a converter regression fails the CI step instead of silently reporting green.

Regression tests, including a fixture where 3 of 11 tests fail, live in `scripts/tests/`: `python3 -m unittest discover -s scripts/tests`.

---

## CI Integration

### GitHub Actions

Add a step after `xcodebuild test` to convert and publish results:

```yaml
jobs:
  test:
    runs-on: macos-26        # verify current label/Xcode version against actions/runner-images; Xcode 16+ required

    steps:
      - uses: actions/checkout@v4

      - name: Run tests
        run: |
          xcodebuild test \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=<simulator-name>,OS=latest' \
            -resultBundlePath TestResults.xcresult \
            | xcpretty || true

      - name: Convert xcresult to JUnit XML
        if: always()
        run: |
          python3 skills/universal/qa-testing-ios/scripts/xcresult_to_junit.py \
            TestResults.xcresult \
            --output reports/junit.xml

      - name: Publish test results
        if: always()
        uses: mikepenz/action-junit-report@v4
        with:
          report_paths: reports/junit.xml
          check_name: iOS Test Results

      - name: Upload xcresult artifact
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: TestResults.xcresult
          path: TestResults.xcresult
```

**Notes:**
- Use `if: always()` on the conversion and publish steps so results are
  uploaded even when tests fail.
- `mikepenz/action-junit-report` (or `EnricoMi/publish-unit-test-result-action`)
  renders per-test pass/fail status in the PR check summary.
- Pair with `actions/upload-artifact` to retain the raw `.xcresult` bundle
  for local triage with Xcode.

### Bitrise

Add a **Script** step after the **Xcode Test for iOS** step:

```yaml
- script@1:
    title: Convert xcresult to JUnit XML
    is_always_run: true
    inputs:
      - content: |
          #!/usr/bin/env bash
          set -euo pipefail

          XCRESULT="${BITRISE_XCRESULT_PATH}"
          OUTPUT="${BITRISE_DEPLOY_DIR}/junit.xml"

          python3 "$BITRISE_SOURCE_DIR/scripts/xcresult_to_junit.py" \
            "$XCRESULT" \
            --output "$OUTPUT"

          echo "JUnit XML: $OUTPUT"

- deploy-to-bitrise-io@2:
    inputs:
      - deploy_path: "$BITRISE_DEPLOY_DIR/junit.xml"
```

Then add the **Test Reports** step (or the built-in JUnit reporter) to parse
`$BITRISE_DEPLOY_DIR/junit.xml` and surface results in the Bitrise build UI.

**Notes:**
- `BITRISE_XCRESULT_PATH` is set automatically by the **Xcode Test for iOS**
  step when `-resultBundlePath` is configured.
- `is_always_run: true` ensures the conversion runs even on test failure.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `xcresulttool not found` | Xcode CLI tools not active | Run `xcode-select --install` or `sudo xcode-select -s /Applications/Xcode.app` |
| `xcresulttool exited with code 64` | Unsupported subcommand | Confirm Xcode 16+ is selected (`xcode-select -p`) |
| `unexpected xcresulttool JSON structure` | Bundle from Xcode < 16 | Re-run tests with Xcode 16+ selected |
| Empty `junit.xml` (no test cases) | All tests skipped or plan empty | Check test plan configuration and `xcodebuild` destination |
