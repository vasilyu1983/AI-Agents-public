# Debugging Methodologies

Which method to use, when to switch, and the traps in each. The scientific method itself
(observe, hypothesize, predict, test) is assumed knowledge; the value here is the selection
rules and the failure modes.

## Contents

- [Method Selection](#method-selection)
- [Bisection: Code, Config, and Input](#bisection-code-config-and-input)
- [Environment and Config Diffs](#environment-and-config-diffs)
- [OODA During Active Impact](#ooda-during-active-impact)
- [Agent-Driven Root-Cause Analysis](#agent-driven-root-cause-analysis)
- [Recurring Bug Class: Time and Timezones](#recurring-bug-class-time-and-timezones)

---

## Method Selection

| Situation | Default method | Switch when |
|-----------|----------------|-------------|
| Known-good and known-bad versions exist | `git bisect run` with an automated check | The check is flaky: repeat it per step (below) or capture instead |
| Works in one environment, fails in another | Environment/config diff, then test each difference alone | Diff is empty: suspect data volume, concurrency, or dependency versions not in config |
| Failing input is large (file, payload, test case) | Input minimization (delta debugging: halve the input, keep the half that still fails) | Failure depends on the combination, not a subset: minimize pairwise |
| Deterministic crash with a stack trace | Read from the first frame in your code; inspect the inputs that reached it | The first frame is fine and state was already corrupt: find where it became corrupt (watchpoint, rr reverse-continue) |
| Intermittent, timing-dependent | Capture once (rr, core dump, tail-sampled trace), analyze offline | Never "re-run until it fails" past 2-3 attempts |
| Production-only, no repro | Observability-first: metrics to find where, traces to find which hop, logs by trace ID for why, profiles for where time went | No hypothesis at all: `../../qa-observability/references/core-analysis-loop.md` |
| Active user impact | OODA loop, mitigation first | Once mitigated, return to the full method for root cause |
| No theory after 2-3 disconfirmed hypotheses | Stop guessing; add instrumentation that answers one specific question | See SKILL.md Expert Judgment |

Hypothesis discipline that separates good debugging from trial-and-error:

- Write the **prediction** before running the test: "if H is true, X will show Y." A test
  without a prediction cannot disconfirm anything.
- Prefer the **cheapest test that splits the remaining hypotheses**, not the test for the most
  likely one. One test that rules out half the list beats three that each rule out one.
- Change one variable at a time; when you cannot (a restart changes many), treat the result as
  weak evidence.

## Bisection: Code, Config, and Input

- `git bisect run <script>`: exit 0 = good, 1-124 or 126-127 = bad, **125 = skip** (use it for
  commits that do not build or where the test cannot run). A script that exits non-zero for
  build failures marks them as bad and sends the bisect to the wrong commit.
- **Flaky check under bisect:** a single pass at one step can be luck. Loop the check inside the
  script (N runs, bad if any fail) with N chosen from the measured failure rate. At a 1-in-10
  failure rate, one clean run proves little.
- Merge-heavy history: `git bisect start --first-parent` isolates which merged PR introduced the
  bug before descending into its commits.
- Bisect config and flags the same way: toggle half the differing keys at once, not one by one.
- If the bisect lands on an innocuous commit (formatting, a dependency lockfile bump), the real
  cause is often environmental or a latent bug that commit merely exposed. Report it as "first
  commit where the failure is observable," not "the commit that caused it."

## Environment and Config Diffs

- Diff the *effective* configuration (what the process actually loaded), not the files in the
  repo: env vars injected by the platform, secrets, flag service values, defaults that differ by
  library version.
- `scripts/config_diff.py file_a file_b` handles .env, JSON, and YAML, flattens nested keys so
  reordering does not show as change, and redacts secret-looking values unless `--show-secrets`.
  It exits 1 when files differ and 2 when a file cannot be parsed. Never read a parse failure as
  "no differences."
- Beyond config: dependency versions (lockfile vs installed), OS and base image, CPU
  architecture, data volume and shape, locale and timezone, feature flag cohorts, and clock.

## OODA During Active Impact

Use when an incident needs action faster than writing formal hypotheses allows.

- **Observe** the freshest signal: error rate, latency, a trace ID.
- **Orient**: classify what changed (code, config, data, infrastructure, external dependency).
- **Decide** on the single most reversible action: rollback, flag off, shed load, or targeted
  instrumentation.
- **Act**, then observe again to confirm the effect before the next action.

Keep each loop short (minutes). Once impact is mitigated, switch back to hypothesis-driven root
cause analysis; OODA finds a lever, not a cause.

## Agent-Driven Root-Cause Analysis

When an agent or LLM helps drive RCA from logs, recordings, or a diff:

1. Collect evidence before forming hypotheses: recording, logs with IDs, the diff, error context.
2. Rank hypotheses from that evidence, not from training priors alone.
3. For each top hypothesis, name the artifact location that would confirm or refute it.
4. Inspect that location, then state the finding with the evidence cited.

**A finding must trace to a specific artifact location**: replay event, log line plus
correlation ID, stack frame, or record. Anything not traceable is a hypothesis and must be
labelled as one, along with the evidence that would confirm it. An LLM matching a stack trace to
a familiar pattern ("this is a connection-pool race, add a lock") without inspecting the
evidence is a silent failure presented as a result. Derive the fix and regression test from the
verified cause, not from the hypothesis.

## Recurring Bug Class: Time and Timezones

| Symptom | Likely cause | Check |
|---------|--------------|-------|
| Wrong display time for some users | Client not converting from UTC, or user timezone not stored | Browser vs server timezone; profile timezone field |
| Off by one day near midnight | Date-only comparison or truncation in the wrong zone | Where the value is truncated to a date, and in which zone |
| Scheduled job fires at the wrong hour | Host or container `TZ` differs from what the scheduler assumes | `TZ` env, system timezone, scheduler timezone setting |
| Bugs twice a year | DST transition: nonexistent or repeated local times | Calculations that add "one day" as 24 hours across a transition |
| Database times shifted by the server offset | Column type without timezone, or session timezone differs | Column type; the database session's timezone setting |

Test fixtures should pin the clock and the timezone and include both DST transitions and a
non-whole-hour offset zone.
