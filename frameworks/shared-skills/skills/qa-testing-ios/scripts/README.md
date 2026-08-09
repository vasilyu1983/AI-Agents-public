# scripts/

Utility scripts for the `qa-testing-ios` skill.

---

## xcresult_to_junit.py

Converts an `.xcresult` bundle produced by `xcodebuild` into a JUnit XML file
that CI systems (GitHub Actions, Bitrise, Jenkins, CircleCI) can ingest for
test-result publishing and trend tracking.

**Requirements:**
- Python 3.9+ (stdlib only — no third-party dependencies)
- Xcode 16+ (`xcresulttool get test-results tests` subcommand)

### Usage

```bash
python3 scripts/xcresult_to_junit.py <bundle.xcresult> [--output junit.xml]
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `<bundle.xcresult>` | Yes | — | Path to the `.xcresult` bundle |
| `--output <path>` | No | `junit.xml` | Output file path |

**Exit codes:**

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Usage error, `xcresulttool` not found, or bundle path missing |
| 2 | `xcresulttool` returned a non-zero exit code |
| 3 | Unexpected JSON structure from `xcresulttool` |

**Examples:**

```bash
# Basic conversion
python3 xcresult_to_junit.py TestResults.xcresult

# Custom output path
python3 xcresult_to_junit.py TestResults.xcresult --output reports/junit.xml

# Show help
python3 xcresult_to_junit.py --help
```

### How it works

1. Runs `xcresulttool get test-results tests --path <bundle> --format json`.
2. Walks the test node tree recursively to collect leaf (individual) test cases.
3. Groups test cases by suite name.
4. Emits a standard JUnit XML document:
   - `<testsuites>` — top-level container with aggregate counts
   - `<testsuite>` — one element per discovered test suite
   - `<testcase>` — one element per test, with `<failure>` for failed tests,
     `<error>` for errored tests, and `<skipped>` for skipped/expected-failure tests.

---

## CI Integration

### GitHub Actions

Add a step after `xcodebuild test` to convert and publish results:

```yaml
jobs:
  test:
    runs-on: macos-15        # or macos-14; Xcode 16+ required

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
          python3 frameworks/shared-skills/skills/qa-testing-ios/scripts/xcresult_to_junit.py \
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
