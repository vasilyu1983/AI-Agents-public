# Test Impact Analysis

## Table of Contents

- [Concept](#concept)
- [Safety Contract](#safety-contract)
- [Tool Landscape](#tool-landscape)
- [Jest: findRelatedTests](#jest-findrelatedtests)
- [Launchable](#launchable)
- [Datadog Test Visibility](#datadog-test-visibility)
- [BuildPulse (Flake Trending)](#buildpulse-flake-trending)
- [NCrunch for .NET](#ncrunch-for-net)
- [CI Integration Patterns](#ci-integration-patterns)
- [TIA Anti-Patterns](#tia-anti-patterns)
- [Related Resources](#related-resources)

Test Impact Analysis (TIA) reduces CI cycle time by running only the tests that could be affected by a given code change. Instead of executing the full suite on every PR, TIA builds a change-to-test dependency map and selects the minimal subset likely to catch regressions in the changed code.

---

## Concept

The core idea: if a change touches `src/payment/charge.ts`, only tests that directly or transitively depend on `payment/charge.ts` need to run for that PR. Tests that cover unrelated modules are skipped.

```text
Code change
    │
    ▼
Dependency graph lookup
    │
    ▼
Affected test set  ──► Run (fast feedback)
    │
Unaffected tests   ──► Skip (or defer to scheduled full run)
```

The dependency graph is built from one or more signals:

- **Static analysis** – parse imports/requires; build a module dependency tree.
- **Dynamic instrumentation** – instrument the test runner to record which source files are loaded during each test execution; store the mapping for future runs.
- **Git diff** – identify changed files; join against the stored mapping.

---

## Safety Contract

TIA MUST NEVER reduce coverage below the established baseline. Violating this contract makes TIA worse than running the full suite.

Rules:

1. **Full suite on merge to `main`** – TIA applies only to PR / feature-branch runs. The mainline always runs everything.
2. **Full suite on scheduled cadence** – Run the complete suite on a nightly or pre-release schedule to catch cross-cutting regressions the impact map missed.
3. **Fallback on graph staleness** – If the dependency map has not been updated within a configurable window (e.g., 7 days since last full run), fall back to the full suite.
4. **Fallback on structural changes** – Dependency graph invalidators (package.json changes, tsconfig.json changes, build system changes, file renames) trigger a full run.
5. **Coverage baseline check** – After each full run, assert that aggregated line/branch coverage has not decreased below the stored baseline. Block merge if it has.

```yaml
# Example CI gate: enforce safety contract
tia_safety:
  full_run_triggers:
    - paths: ["package.json", "package-lock.json", "tsconfig*.json", "jest.config.*"]
    - schedule: "0 2 * * *"   # nightly full run
    - branches: ["main", "release/*"]
  coverage_baseline:
    enforce: true
    metric: lines
    minimum_delta: 0          # coverage must not decrease
```

---

## Tool Landscape

| Tool | Languages | Signal source | Hosted / Self-hosted |
|------|-----------|--------------|----------------------|
| **Launchable** | Java, Python, Go, Ruby, JS/TS, .NET | ML model on historical results | Hosted SaaS |
| **Datadog Test Optimization** | JS/TS, Python, Java, Ruby, Go, .NET | Dynamic instrumentation + APM | Hosted (Datadog) |
| **BuildPulse** | Any (JUnit XML) | Flake trending from test reports | Hosted SaaS |
| **jest --findRelatedTests** | JavaScript / TypeScript | Static import graph | CLI (built-in) |
| **NCrunch** | .NET (C#, VB.NET) | Continuous in-IDE instrumentation | Local / CI |
| **Bazel** | Polyglot | Hermetic build graph | Self-hosted |
| **Nx affected** | JS/TS monorepos | Module dependency graph | CLI (built-in) |

Note: Datadog's product is currently marketed as "Test Optimization" (not "Test Visibility" — both names appear in documentation). Verify current product name at https://docs.datadoghq.com/tests/ before configuring.

---

## Jest: findRelatedTests

Jest's built-in flag performs static import graph traversal to find tests related to changed source files. No external service required.

```bash
# Run only tests affected by changed files (from git diff)
git diff --name-only HEAD~1 HEAD | \
  grep -E '\.(ts|tsx|js|jsx)$' | \
  xargs npx jest --findRelatedTests --passWithNoTests
```

### GitHub Actions integration

```yaml
- name: Run affected tests
  run: |
    CHANGED=$(git diff --name-only ${{ github.event.before }} ${{ github.sha }} \
      | grep -E '\.(ts|tsx|js|jsx)$' || true)
    if [ -z "$CHANGED" ]; then
      echo "No JS/TS changes — skipping jest"
    else
      echo "$CHANGED" | xargs npx jest --findRelatedTests --passWithNoTests --ci
    fi
```

**Limitations**: only traces static imports; dynamic `require()` calls and barrel re-exports can cause missed tests. Combine with a full nightly run per the safety contract.

---

## Launchable

Launchable applies an ML model trained on your historical test results and code-change patterns to rank and subset tests. It predicts which tests are most likely to fail for a given change set.

### How it works

1. **Record** – Launchable CLI instruments your CI to upload test results and git metadata after each run.
2. **Train** – The model learns which tests fail when specific files change.
3. **Subset** – On each PR, the CLI returns the predicted high-value subset; the runner executes that subset.
4. **Always record** – Full runs (nightly, merge to main) continue to feed the model.

### CLI integration (Java/Maven example)

```bash
# Record build results
launchable record build --name "$BUILD_ID" --source .

# Request a subset (target: 20 minutes of the most impactful tests)
launchable subset --target 20% --build "$BUILD_ID" maven > launchable-subset.txt

# Run the subset
mvn test -Dsurefire.includesFile=launchable-subset.txt

# Record results
launchable record tests --build "$BUILD_ID" maven target/surefire-reports/
```

Launchable guarantees a configurable confidence level (e.g., 95% confidence the subset catches any failure the full suite would catch). The safety contract is enforced by Launchable's own model confidence threshold.

---

## Datadog Test Visibility

Datadog Test Visibility (part of CI Visibility) instruments test frameworks at runtime to record per-test traces, durations, and outcomes. It powers:

- **Flaky test detection** – automatic identification of non-deterministic tests across branches.
- **Test impact analysis** – correlates code changes with historically failing tests using the stored trace data.
- **Early flake detection** – new tests are run multiple times on first appearance to establish a stability baseline before they can block CI.

### Setup (JavaScript / Vitest)

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import { DatadogCIPlugin } from 'dd-trace/ci/vitest';

export default defineConfig({
  plugins: [DatadogCIPlugin()],
  test: { reporters: ['verbose'] },
});
```

```bash
# Required env vars
export DD_API_KEY=<api-key>
export DD_ENV=ci
export DD_SERVICE=my-service
npx vitest run
```

### Key metrics surfaced

| Metric | Use |
|--------|-----|
| Flakiness rate per test | Prioritise deflake work |
| Mean duration trend | Detect slowdowns before they block CI |
| Branch vs mainline failure divergence | Catch regressions introduced on a branch |
| TIA skip ratio | Measure CI time saved |

---

## BuildPulse (Flake Trending)

BuildPulse ingests JUnit XML test reports from any CI system and provides flake trending, ownership attribution, and quarantine recommendations. It does not perform TIA itself but is the recommended complement for flake visibility when using TIA tools that do not have built-in flake detection.

### Integration (GitHub Actions)

```yaml
- name: Upload test results to BuildPulse
  if: always()
  uses: buildpulse/buildpulse-action@v0
  with:
    account: ${{ secrets.BUILDPULSE_ACCOUNT_ID }}
    repository: ${{ secrets.BUILDPULSE_REPOSITORY_ID }}
    path: test-results/**/*.xml
    key: ${{ secrets.BUILDPULSE_ACCESS_KEY_ID }}
    secret: ${{ secrets.BUILDPULSE_SECRET_ACCESS_KEY }}
```

### What BuildPulse surfaces

- **Flakiness score per test** – percentage of runs that produced an inconsistent result.
- **Trend chart** – flakiness rate over time to distinguish stable, improving, and worsening tests.
- **Owner attribution** – maps flaky tests to the last committer on that test file.
- **Quarantine recommendations** – flags tests with flakiness > configurable threshold as quarantine candidates.

Pair BuildPulse trending data with MTTR-Flake SLO tracking (see [production-testing-and-shift-right.md](./production-testing-and-shift-right.md)) for a complete flake lifecycle picture.

---

## NCrunch for .NET

NCrunch is a continuous test runner for Visual Studio and Rider that instruments .NET tests at the bytecode level and runs them automatically as you type. It provides the tightest possible feedback loop: sub-second test execution for changed code paths.

### How it implements TIA

NCrunch maintains a runtime instrumentation map linking each line of source code to the tests that executed it. When a file changes, only the mapped tests re-run — in the background, in parallel, without a manual trigger.

### CI mode

NCrunch can export its coverage and impact data for use in CI pipelines:

```xml
<!-- ncrunch.project settings for CI export -->
<NCrunchProjectSettings>
  <CoverageExportFormat>opencover</CoverageExportFormat>
  <CoverageExportPath>coverage/ncrunch.xml</CoverageExportPath>
</NCrunchProjectSettings>
```

In CI, NCrunch's coverage output feeds into SonarQube or the Datadog Test Visibility .NET agent for dashboard aggregation.

**Limitation**: NCrunch is a local-first IDE tool. For CI-only .NET TIA, prefer [dotnet-coverage](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-coverage) with a custom impact mapping script, or Datadog Test Visibility for .NET.

---

## CI Integration Patterns

### Pattern 1: Static graph (fast, no service dependency)

```text
git diff → jest --findRelatedTests (or nx affected)
  ├── affected test set → run immediately
  └── unaffected → skip

Nightly: full suite → update coverage baseline
```

### Pattern 2: ML-assisted (highest skip ratio)

```text
PR: Launchable subset → run predicted high-value tests
    ├── results → uploaded to Launchable for model training
    └── gate: Launchable confidence ≥ 95%

Merge to main: full suite always runs
Nightly: full suite → coverage baseline check
```

### Pattern 3: Instrumented visibility + manual TIA

```text
All runs: Datadog Test Visibility instruments every run
  → flake detection, duration trends, failure attribution

PR: developer checks flake dashboard; quarantines known flaky tests
    ├── CI skips quarantined tests (with expiry enforcement)
    └── Full suite on nightly schedule

BuildPulse: receives JUnit XML from all runs → flake trending dashboard
```

---

## TIA and Merge Queues

Merge queues (GitHub, GitLab, Trunk, Aviator) serialize PR merges through a shared CI pipeline to prevent the "works on my branch" class of regression. TIA interacts with merge queues in two ways that require explicit handling.

### The amplification problem

A test that fails 5% of the time on a single isolated PR run will fail on roughly every other merge queue cycle if the queue processes 10–15 PRs per hour. The merge queue amplifies flake debt from a nuisance into a pipeline-stopping event.

### How TIA helps and where it breaks

TIA reduces queue cycle time by running only the tests affected by the batch. This reduces total flake exposure because fewer tests run. However:

- If the TIA dependency map is stale, unrelated tests may be skipped, allowing regressions to pass.
- Merge queues typically batch multiple PRs; the impact set is the union of all changes in the batch. Ensure TIA tools support batch-level impact computation, not just single-PR impact.
- GitHub merge queue requires branch protection rules that reference specific status checks. Map TIA-scoped check names consistently or use a wrapper check that always reports.

### Integration pattern for GitHub merge queue + Nx affected

```yaml
# .github/workflows/ci.yml
on:
  merge_group:
    types: [checks_requested]
  pull_request:

jobs:
  test-affected:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Compute affected projects
        id: affected
        run: |
          BASE=${{ github.event.merge_group.base_sha || github.event.pull_request.base.sha }}
          AFFECTED=$(npx nx show projects --affected --base=$BASE --head=HEAD --type=lib,app)
          echo "projects=$AFFECTED" >> $GITHUB_OUTPUT

      - name: Run tests for affected projects
        run: npx nx run-many --target=test --projects=${{ steps.affected.outputs.projects }} --parallel=4

  # Required check placeholder — always runs, always passes if test-affected passes
  required-tests:
    needs: test-affected
    runs-on: ubuntu-latest
    if: always()
    steps:
      - run: |
          if [ "${{ needs.test-affected.result }}" != "success" ]; then
            echo "Tests failed"; exit 1
          fi
```

### Quarantine in merge queue context

Most queue tools (Aviator, Trunk, Mergify) support automatic quarantine: a quarantined test runs and logs output but its failure does not eject the PR from the queue. This should be paired with:

- An MTTR-Flake SLO so quarantined tests do not accumulate indefinitely.
- Quarantine expiry (maximum 5 business days for standard; 2 for critical-path).
- Never quarantine a test that gates security, auth, or payment correctness.

---

## TIA Anti-Patterns

| Anti-Pattern | Risk | Mitigation |
|-------------|------|------------|
| TIA on mainline / merge commits | Regressions hidden from the baseline run | TIA for PRs only; full suite always runs on main |
| Stale dependency graph | Map diverges from code; wrong tests skipped | Invalidate on structural file changes; max 7-day TTL |
| No nightly full run | Coverage silently erodes | Enforce nightly via cron; fail pipeline on coverage delta |
| TIA without flake visibility | Flaky tests pollute the impact signal | Pair with BuildPulse or Datadog Test Visibility |
| Trusting 100% TIA skip | Even ML models miss cross-cutting changes | Enforce safety contract (see above) regardless of tool confidence |

---

## Related Resources

- [production-testing-and-shift-right.md](./production-testing-and-shift-right.md) -- MTTR-Flake SLO and shift-right context
- [quality-metrics-dashboard.md](./quality-metrics-dashboard.md) -- flake rate metrics and dashboards
- [operational-playbook.md](./operational-playbook.md) -- CI/CD pipeline quality gates
- [Launchable Docs](https://www.launchableinc.com/docs)
- [Datadog Test Visibility](https://docs.datadoghq.com/tests/)
- [BuildPulse](https://buildpulse.io/)
- [Jest --findRelatedTests](https://jestjs.io/docs/cli#--findrelatedtests-spaceseparatedlistofsourcefiles)
- [NCrunch](https://www.ncrunch.net/)
