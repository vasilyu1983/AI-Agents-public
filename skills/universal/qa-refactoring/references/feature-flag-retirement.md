# Feature Flag Retirement

A step-by-step recipe for safely removing a feature flag after its rollout is complete. Leaving dead flags in the codebase adds cognitive load, creates stale branching, and risks accidental re-activation. Retire each flag within one release cycle of reaching 100 % rollout.

## Contents

- [When a Flag Is Ready to Retire](#when-a-flag-is-ready-to-retire)
- [Step-by-Step Recipe](#step-by-step-recipe)
- [Post-Mortem the Rollout](#post-mortem-the-rollout)
- [Common Pitfalls](#common-pitfalls)

---

## When a Flag Is Ready to Retire

A flag is a retirement candidate when all of the following are true:

- It has been at 100 % enabled (or 100 % disabled) for at least one full release cycle.
- No rollback has been triggered in that period.
- Monitoring shows no anomalies attributable to the flagged feature.
- The product owner or feature owner confirms permanent direction.

Automate candidate detection: query your flag management system (LaunchDarkly, Unleash, custom config) for flags with `percentage = 100` and `age > 30 days`.

---

## Step-by-Step Recipe

### 1. Identify All References

Find every call site before touching any code.

```bash
# Grep for the flag key across the codebase (exclude archives and build artifacts)
rg "MY_FEATURE_FLAG" --type-list   # verify file types
rg "MY_FEATURE_FLAG" -g '!**/node_modules/**' -g '!**/.archive/**' -l

# AST-level search for typed flag enums (TypeScript example)
npx ts-morph-grep "FeatureFlag.MY_FEATURE_FLAG"

# For Java: use your IDE's "Find Usages" or
grep -rn "MY_FEATURE_FLAG" src/ --include="*.java"
```

Produce a checklist:

- Source files (application code, configuration)
- Test files (unit, integration, E2E)
- Infrastructure-as-code (env vars, Terraform, Helm values)
- Analytics and monitoring dashboards
- Documentation and runbooks

### 2. Mark the Dead Branch

Before deleting anything, confirm which branch is "dead" (the branch that will never execute again):

- Flag was enabled → the `else` / `false` branch is dead.
- Flag was disabled → the `if` / `true` branch is dead.

Open a PR that adds a comment marking dead code. This creates a reviewable checkpoint and catches disagreements about direction before deletion begins.

### 3. Remove the Dead Branch First

Delete the dead code path and its tests. Keep the flag guard in place for now.

```diff
- if (featureEnabled(FeatureFlag.MY_FEATURE_FLAG)) {
-   return newImplementation(input);
- } else {
-   return legacyImplementation(input);   // dead branch
- }
+ if (featureEnabled(FeatureFlag.MY_FEATURE_FLAG)) {
+   return newImplementation(input);
+ }
```

Run full CI. Confirm no test covers the removed branch (a surviving test means the branch was not truly dead — stop and investigate).

### 4. Delete the Flag Guard

With the dead branch gone, remove the flag check itself, making the surviving code unconditional.

```diff
- if (featureEnabled(FeatureFlag.MY_FEATURE_FLAG)) {
-   return newImplementation(input);
- }
+ return newImplementation(input);
```

Run full CI again. The behavior is unchanged — only the conditional and flag lookup are removed.

### 5. Delete the Flag Definition Last

Only after the guard is gone, remove:

- The flag constant / enum value.
- The default value in configuration files.
- The flag registration call in your feature-flag SDK initializer.
- The flag entry in your flag management system (LaunchDarkly dashboard, Unleash DB, etc.).

Deleting the definition before removing all call sites causes compile errors or silent `false` fallback — always clean call sites first.

### 6. Update Analytics and Dashboards

Feature flags often gate instrumented events or dashboard segments. After removal:

- Remove or archive dashboard panels that segment by the flag.
- Update alert conditions that reference the flag state.
- Remove any A/B experiment tracking that used the flag as a variant key.
- Notify the data/analytics team so they do not query a non-existent dimension.

### 7. Remove from Tests

Clean up test scaffolding:

- Delete test helpers that override the flag value.
- Delete test cases that test the dead branch.
- Remove `FeatureFlag.MY_FEATURE_FLAG` from any test fixture or factory.

Leaving dead test helpers signals to future developers that the flag is still meaningful.

---

## Post-Mortem the Rollout

After retirement, run a lightweight post-mortem (15–30 min, async is fine):

| Question | Purpose |
|----------|---------|
| Did the flag enable safe rollback? Was rollback used? | Validate flag necessity |
| How long did the flag live from creation to retirement? | Identify if flags are being retired promptly |
| Were there any incidents linked to the flag state? | Feed back into flag hygiene policy |
| Was the retirement PR larger or smaller than expected? | Surface scope creep or missed call sites |

Store the summary in your team's decision log or post-mortem system. Patterns across multiple flag retirements reveal systemic issues (flags living too long, missed dashboard cleanup, etc.).

---

## Common Pitfalls

| Pitfall | Effect | Remedy |
|---------|--------|--------|
| Deleting the flag definition before removing call sites | Runtime `false` fallback silently activates dead branch | Always remove call sites first, definition last |
| Skipping the analytics/dashboard step | Stale segments cause misleading metrics | Add analytics to the retirement checklist |
| Retiring a flag before 100 % rollout confirmation | Removes the rollback path while risk is still live | Gate retirement on explicit product sign-off |
| Large retirement PRs that mix flag removal with unrelated refactors | Hard to review; blame history polluted | One PR per flag; no unrelated changes |
