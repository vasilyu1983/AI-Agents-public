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

Stryker's definition: `score = detected / valid`, where `valid = detected + undetected` and `undetected = survived + no-coverage`. **No-coverage mutants count against the score by default** — they are not excluded. A separate "score based on covered code only" metric exists if you want coverage-gap and detection-gap reported apart, but the default score already penalizes missing coverage (stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/; other tools may define the denominator differently — check before assuming parity).

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
- `.NET` support via `dotnet-stryker` (`dotnet tool install -g dotnet-stryker`). Check github.com/stryker-mutator/stryker-net/releases for the current version and for Microsoft Testing Platform (MTP) per-test coverage support before relying on it.
- A Stryker VS Code plugin exists; check its marketplace page for which runners (StrykerJS, Stryker.NET) it currently covers.

### Python — mutmut

**Homepage:** https://github.com/boxed/mutmut

```bash
pip install mutmut
mutmut run          # run all mutants
mutmut results      # show surviving mutants
mutmut show <id>    # diff of a specific surviving mutant
```

- Integrates with pytest by default.
- mutmut 3 stores mutant data in a `mutants/` directory (not `.mutmut-cache`, which was the mutmut 2.x layout).
- `mutmut browse` opens an interactive TUI over surviving mutants; `mutmut export-cicd-stats` emits CI-consumable stats (mutmut 3 README, github.com/boxed/mutmut). Check the current export command name before scripting against it — CLI subcommands have moved across mutmut 2→3.

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
  <version><!-- current release from github.com/hcoles/pitest/releases --></version>
  <!-- pitest-maven and pitest core release together; keep them in lockstep -->
  <!-- Kotlin: check whether the standalone pitest-kotlin plugin is maintained or superseded by Arcmutate before relying on it. -->
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
- Kotlin support: check whether `pitest-kotlin` is still maintained or superseded by Arcmutate before depending on it.
- Incremental mode (`withHistory`): stores previous run state, only re-mutates changed classes.

---

## CI Integration and Thresholds

### Recommended threshold bands

Stryker's default bands (check the current Stryker config docs): `high` and `low` are thresholds, and `break` defaults to `null` (no build failure) unless you set it explicitly. There is no built-in "gap" band — a score at or above `low` and below `high` is the warning zone, and a score below `low` is danger; `break` only fails the build if you configure it.

| Band | Mutation Score | Action |
|------|----------------|--------|
| High | ≥ 80 % (your `high`) | Green; no gate triggered |
| Warning | `low` to `high` (e.g. 60–79 %) | Notify but do not block |
| Danger | below `low` | Visible warning; still does not fail the build unless `break` is set |
| Break | below your configured `break` value | Fail the build — this is opt-in, not a Stryker default |

Calibrate `low`/`high`/`break` for your domain. Safety-critical paths (auth, payments, data migrations) warrant setting `break` at 70 % or higher; most teams should not leave `break` unset in CI, since an unset `break` means mutation score can never fail the pipeline.

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

Mutation testing is inherently slow: run time ≈ mutants × mean time of the tests that cover each mutant ÷ parallel workers. Mutant count grows roughly with the amount of code in scope. Estimate from a dry run on one module, then calibrate against your first full run.

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
| Setting break threshold at 100 % | Equivalent mutants cause permanent failures | Keep `break` a few points below your realistic ceiling (a team-specific choice, not a vendor default) and triage survivors before raising further |
| Assuming no-coverage mutants are excluded from the score | Score looks higher than it is; the default Stryker score already counts them against you | Fix coverage first — no-coverage mutants count as undetected by default, not as excluded |
| Mutation testing without unit tests | Nothing to kill mutants; score is 0 % | Write a characterization test baseline before enabling |
