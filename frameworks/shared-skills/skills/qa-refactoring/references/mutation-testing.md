# Mutation Testing

Mutation testing measures the quality of your test suite by deliberately introducing small faults (mutants) into the source code and checking whether your tests detect them. A test suite that passes against broken code provides false confidence; mutation testing makes that gap visible.

## Contents

- [Core Concept](#core-concept)
- [Mutation Score](#mutation-score)
- [Tooling by Ecosystem](#tooling-by-ecosystem)
- [CI Integration and Thresholds](#ci-integration-and-thresholds)
- [Performance Budget](#performance-budget)
- [Interpreting Results](#interpreting-results)
- [Incremental Workflow](#incremental-workflow)
- [Common Pitfalls](#common-pitfalls)

---

## Core Concept

A **mutant** is a copy of the source code with a single small change applied by the tool (a mutation operator):

- Arithmetic operator replacement: `+` → `-`
- Conditional boundary shift: `>` → `>=`
- Boolean literal flip: `true` → `false`
- Statement deletion: remove a `return` or assignment
- Negated condition: `if (x)` → `if (!x)`

Each mutant is compiled and your test suite is executed against it.

- **Killed mutant**: at least one test fails — the tests detected the fault.
- **Survived mutant**: all tests pass — the tests did not detect the fault.
- **Timed-out mutant**: execution exceeded the timeout — treated as killed.
- **No-coverage mutant**: the mutant is on a line not executed by any test — trivially survived.

---

## Mutation Score

```
mutation score = killed mutants / total mutants × 100
```

Where "total mutants" excludes no-coverage mutants in most tools (coverage must exist before mutation score is meaningful).

A mutation score of 80 % means 20 % of the injected faults went undetected. The gap between line coverage and mutation score reveals tests that execute code without asserting meaningful outcomes.

---

## Tooling by Ecosystem

### JavaScript / TypeScript — Stryker

**Homepage:** https://stryker-mutator.io

```bash
npm install --save-dev @stryker-mutator/core @stryker-mutator/jest-runner
npx stryker run
```

Minimal `stryker.config.mjs`:

```js
export default {
  testRunner: 'jest',
  coverageAnalysis: 'perTest',   // enables incremental on changed files
  reporters: ['html', 'progress', 'dashboard'],
  thresholds: { high: 80, low: 60, break: 50 },
};
```

- `coverageAnalysis: 'perTest'` maps each test to the mutants it can kill, enabling selective re-runs on PRs.
- Stryker also supports Mocha, Vitest, Karma, and Jasmine runners.
- `.NET` support via `dotnet-stryker` (`dotnet tool install -g dotnet-stryker`). Latest: Stryker.NET 4.14 (May 2026), with Microsoft Testing Platform (MTP) support in preview.
- Official Stryker VS Code plugin released November 2025 — run mutation tests directly from the editor.

### Python — mutmut

**Homepage:** https://github.com/boxed/mutmut

```bash
pip install mutmut
mutmut run          # run all mutants
mutmut results      # show surviving mutants
mutmut show <id>    # diff of a specific surviving mutant
```

- Integrates with pytest by default.
- Cache stored in `.mutmut-cache`; re-runs are fast after the first pass.
- Export results: `mutmut junitxml > mutmut-results.xml` for CI artifact upload.

### Python — cosmic-ray

**Homepage:** https://github.com/sixty-north/cosmic-ray

```bash
pip install cosmic-ray
cosmic-ray init config.toml session.sqlite
cosmic-ray exec session.sqlite
cr-report session.sqlite
```

- Session-based: work is stored in SQLite, enabling resumable runs.
- Supports distributed execution (Celery workers) for large codebases.
- Preferred when you need fine-grained operator control or distributed runs.

### Java / Kotlin — PIT (Pitest)

**Homepage:** https://pitest.org

Maven plugin:

```xml
<plugin>
  <groupId>org.pitest</groupId>
  <artifactId>pitest-maven</artifactId>
  <version>1.19.1</version>
  <configuration>
    <targetClasses><param>com.example.*</param></targetClasses>
    <mutationThreshold>75</mutationThreshold>
    <coverageThreshold>80</coverageThreshold>
  </configuration>
</plugin>
```

```bash
mvn org.pitest:pitest-maven:mutationCoverage
```

- HTML report at `target/pit-reports/`.
- Kotlin support via `pitest-kotlin` plugin.
- Incremental mode (`withHistory`): stores previous run state, only re-mutates changed classes.

---

## CI Integration and Thresholds

### Recommended threshold bands

| Band | Mutation Score | Action |
|------|----------------|--------|
| High | ≥ 80 % | Green; no gate triggered |
| Low | 60–79 % | Warning; notify but do not block |
| Break | < 50 % | Fail the build |

These are defaults in Stryker; calibrate for your domain. Safety-critical paths (auth, payments, data migrations) warrant a break threshold of 70 % or higher.

### GitHub Actions example (Node.js)

```yaml
- name: Mutation tests (PR only)
  if: github.event_name == 'pull_request'
  run: npx stryker run --incremental --incrementalFile .stryker-incremental.json
- name: Upload Stryker report
  uses: actions/upload-artifact@v4
  with:
    name: stryker-report
    path: reports/mutation/
```

Run full mutation suites on a nightly schedule, not on every push — see Performance Budget below.

---

## Performance Budget

Mutation testing is inherently slow: N mutants × test suite duration. Typical ratios:

| Codebase size | Mutants | Full run time |
|---------------|---------|---------------|
| Small (< 5k LOC) | ~500 | 2–10 min |
| Medium (5–50k LOC) | ~5 000 | 30–90 min |
| Large (> 50k LOC) | ~50 000 | 4–12 hours |

**Rules:**

1. **PRs**: run incremental mutation only on lines changed in the diff (`--incremental` / `coverageAnalysis: 'perTest'` / PIT `withHistory`). Target: < 5 min gate time.
2. **Main / nightly**: run full mutation suite. Store the HTML report as a CI artifact.
3. **Never run full mutation on every push** to a shared branch — it blocks developers without proportional value.
4. Parallelize using test sharding or distributed runners (cosmic-ray + Celery, Stryker concurrency settings) when full runs exceed acceptable nightly windows.

---

## Interpreting Results

### Low mutation score (< 60 %)

Your tests pass for the wrong reasons. Common causes:

- Tests exercise code paths but assert only on side effects, not return values.
- Tests are written to pass the current implementation, not to specify behavior.
- Large blocks of code have no coverage at all (check no-coverage mutants first).

**Fix**: write behavior-specifying tests — given an input, assert the exact output. Do not assert on implementation details (internal calls, intermediate state).

### High survived count on a specific operator

| Surviving operator | Likely root cause |
|-------------------|-------------------|
| Conditional boundary (`>` vs `>=`) | Off-by-one tests missing |
| Boolean literal | Defensive defaults not tested |
| Statement deletion | Code path never called in tests |
| Return value | Return value not asserted |

### Equivalent mutants

Some surviving mutants are semantically equivalent to the original and cannot be killed by any test. Do not chase 100 % mutation score — flag these in your tool's ignore config and focus on meaningful gaps.

---

## Incremental Workflow

For teams adopting mutation testing on an existing codebase:

1. Run mutation on the module being actively refactored only. Do not gate the entire codebase.
2. Fix the most impactful survivors (high-traffic, high-risk code) first.
3. Raise thresholds incrementally: start at break = 40 %, raise 5 % per sprint until stable at 70–80 %.
4. Add full-codebase runs to the nightly pipeline before enforcing repo-wide thresholds.

---

## Mutation Score as the AI-Generated-Test Validator

By 2026 this is the converged-on use for mutation testing in AI-assisted codebases, and it
directly serves behavior-preserving refactors: when AI generates the characterization safety
net for a refactor, mutation testing verifies the net itself.

- **The failure mode it catches:** AI/agent-authored tests routinely reach high line coverage
  while passing trivially — hardcoded expected values, assertions on incidental output, oracles
  that describe *actual* behavior rather than *intended* behavior. Such tests pass before and
  after a behavior change, so they provide zero refactor-safety signal.
- **The gate:** line coverage measures execution; mutation score measures detection. For a
  refactor safety net, require the AI-generated characterization tests to clear a mutation-score
  threshold on the diff boundary before trusting them — not a coverage threshold.
- **Closed loop:** (1) AI drafts characterization tests targeted at the change boundary →
  (2) run mutation on the touched module → (3) any surviving mutant in refactor-critical code
  means the safety net has a hole; fix the test, not the threshold → (4) only then perform the
  refactor behind the verified net.
- **Do not** let an agent raise the score by weakening assertions to kill survivors — that is
  the test-healing anti-pattern inverted. Survivors are fixed by strengthening oracles.

---

## Common Pitfalls

| Pitfall | Effect | Remedy |
|---------|--------|--------|
| Running full mutation on every PR | Pipelines time out; developers bypass gate | Run incremental on PRs; full run nightly |
| Setting break threshold at 100 % | Equivalent mutants cause permanent failures | Cap break at 85 %; triage survivors before raising further |
| Ignoring no-coverage mutants | Score looks high but large gaps exist | Fix coverage first, then interpret mutation score |
| Mutation testing without unit tests | Nothing to kill mutants; score is 0 % | Write a characterization test baseline before enabling |
