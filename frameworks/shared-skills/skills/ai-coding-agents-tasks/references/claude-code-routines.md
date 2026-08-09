# Claude Code Routines

## Table of Contents

- [When Routines Fit](#when-routines-fit)
- [The Three Trigger Types](#the-three-trigger-types)
- [Prompt Authoring Rules](#prompt-authoring-rules)
- [Limits and Caps](#limits-and-caps)
- [Creation Paths](#creation-paths)
- [Comparison With Adjacent Tools](#comparison-with-adjacent-tools)
- [Host-Side Design Implications](#host-side-design-implications)
- [See Also](#see-also)

Routines are Anthropic-cloud-hosted task configurations that run without a live session. A routine is a saved (prompt, repositories, connectors) tuple that activates via **schedule**, **API call**, or **GitHub event** — independently or combined on the same routine.

Routines sit between `/loop` (session-bound, local) and full CI infrastructure (GitHub Actions, n8n, cron). They are the only coding-agent task type that runs when the user's machine is off.

**Status:** volatile hosted automation surface, still in research preview as of 2026-07-11 (not GA — re-check before assuming a stable contract). Reviewed against `code.claude.com/docs/en/routines` and the Anthropic routines blog post on 2026-07-11; exact caps, headers, endpoint fields, and account/team semantics must be re-verified in the live Claude Code docs or UI before shipping an integration.

## When Routines Fit

| Use routines when | Use something else when |
|---|---|
| Work must run while laptop is off | Task is inherently interactive |
| Trigger is a schedule, a webhook, or a monitoring alert | You need a live pair-programming loop → use a normal session |
| Job requires Claude reasoning over code/issues/logs | Job is pure build/test/deploy → GitHub Actions |
| Output is a labelled issue, a draft PR, a Slack summary | You need strict timing (routines run "sometime in the window") |
| Connectors (Slack, Sentry, Linear, GitHub) already integrated | You need <1h cadence → minimum interval is 1 hour |

## The Three Trigger Types

### 1. Schedule

Cadence presets: hourly, daily, weekdays, weekly, plus **custom cron** (minimum 1-hour interval; sub-hourly expressions rejected). Timezone-aware; scheduled time is entered in local zone. Actual start can lag a few minutes behind the target — design for "sometime in the window," not exact-second precision.

Canonical use: nightly backlog grooming, morning release-note draft, weekly dependency audit, hourly backlog stale-check.

### 2. API (`/fire` endpoint)

Each routine exposes a dedicated endpoint. Bearer token is shown **exactly once at generation** — store it immediately.

```bash
POST https://api.anthropic.com/v1/claude_code/routines/{trigger_id}/fire

curl -X POST https://api.anthropic.com/v1/claude_code/routines/{trigger_id}/fire \
  -H "Authorization: Bearer {your_token}" \
  -H "anthropic-beta: {current_routine_beta_header}" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"text": "Production alert: error rate on /api/checkout exceeded 5% threshold. Alert ID: ALR-4821."}'
```

Response contains `claude_code_session_id` and `claude_code_session_url`. Log the URL — it opens the live run for inspection or manual continuation.

Three non-obvious facts:
- `text` is a **literal string**. JSON inside it is read as prose, not structured data. Write it as sentences.
- Each token is scoped to **one routine**. Rotate per-routine.
- The beta header can rotate. Do not hardcode a dated header in product code; store it as configuration with a visible last-verified date and fail closed when Anthropic rejects it.

Canonical use: alert → routine (Sentry posts stack trace as `text`, routine opens draft fix PR), deploy webhook → verification routine, external cron → routine.

### 3. GitHub Events

Supported: `pull_request` (opened, closed, assigned, labeled, synchronized, etc.) and `release` (created, published, edited, deleted).

Setup requires **both** steps (easy to stop at the first):
1. `/web-setup` in Claude Code → grants repository clone access
2. **Install the Claude GitHub App** on the target repo → enables webhook delivery

Filters (all conditions AND): Author, Title, Body, Base branch, Head branch, Labels, Is draft, Is merged, From fork.

**Regex gotcha:** `matches regex` tests the **entire** field. To match PR titles *containing* "hotfix", write `.*hotfix.*`. For substring intent, prefer `contains`.

**Branch permissions:** Claude pushes only to `claude/`-prefixed branches by default. To push elsewhere, enable "Allow unrestricted branch pushes" in routine settings. Commits appear under the routine owner's personal GitHub identity, not a bot account.

**Session model:** Each matching event starts a **fresh** session with no carryover from previous runs. Prompts must be self-contained per event.

## Prompt Authoring Rules

Routines run without approval prompts at every step. The prompt carries the full cognitive load.

| Rule | Why |
|---|---|
| Specify what "done" looks like | No human is there to notice a half-done run |
| Name specific connectors | Don't assume Claude knows which Slack workspace or Sentry project |
| Describe fallback when something unexpected happens | No one to re-prompt mid-run |
| State "do not do X" boundaries | No approval gate to catch scope creep |
| Self-contained per event (GitHub trigger) | No session state carries over |

**Bad:** "Check for issues."

**Good:** "Read all GitHub issues opened today in `{repo}`. For each: apply a label from [bug, feature, docs, question, needs-triage], assign based on CODEOWNERS for referenced files, post summary to `#dev-standup` with totals and breakdown. If zero issues, post `No new issues today.`"

## Limits and Caps

| Cap | Behaviour when hit |
|---|---|
| Daily run cap (per plan) | Rejected until window resets; metered-usage plans can continue on overage billing |
| GitHub per-routine hourly cap | Events **dropped**, not queued — gone until next window |
| Minimum schedule interval | 1 hour; sub-hourly cron rejected |

Published per-plan daily caps (verified 2026-07-11, `code.claude.com/docs/en/routines`): Pro 5/day, Max 15/day, Team and Enterprise 25/day. Live remaining count is at `claude.ai/code/routines` or `claude.ai/settings/usage` — caps can change without notice while the feature is in research preview, so treat the numbers above as a snapshot, not a contract.

**One-off runs are exempt.** A manually-fired one-off run (not on a recurring schedule) draws down normal session usage but does not count against the daily routine cap — model this as a separate counter from the recurring-schedule cap if you build quota-aware tooling on top of routines.

**Individual ownership only.** Routines belong to a personal `claude.ai` account during research preview. No team sharing, no transfer, no co-ownership. Teammates needing the same routine each set up a copy.

## Creation Paths

| Path | Supports |
|---|---|
| Web UI at `claude.ai/code/routines` → New Routine | All three trigger types (canonical) |
| CLI `/schedule` inside a session | Schedule trigger only; add API/GitHub in web UI afterward |
| Desktop app → New Task > New Remote Task | All three (distinct from local Desktop scheduled tasks) |

All three create the same underlying routine object.

## Comparison With Adjacent Tools

| Tool | Best for | Avoid when |
|---|---|---|
| **Routines** | AI reasoning on dev artefacts (diffs, issues, logs) while laptop is off | Strict sub-hourly timing; team-shared automation |
| GitHub Actions | Build/test/deploy pipelines, language-agnostic CI | Job requires code-aware reasoning |
| n8n / Zapier | Connecting 10+ SaaS tools without code | Job requires reading and modifying code |
| cron | Simple local scripts producing clean output | Job needs judgement or fresh context |
| `/loop` | Self-paced or recurring work **inside** a live session | Work must survive session end |

For most teams the answer is **Routines + Actions**: Actions run the pipeline, routines reason about what ran.

## Host-Side Design Implications

When modelling routines in a coding-agent runtime:

- Treat routine runs as a **remote task type** distinct from local shell and local agent tasks — they have a cloud-owned lifecycle, a session URL surface, and cannot be cancelled by closing the terminal.
- Trigger metadata (cron expression, event filter, API token ID) belongs in task state, not UI only.
- Each GitHub-event run produces a fresh session; link rather than merge transcripts when showing history.
- Cap behaviour is **drop, not queue** for GitHub events — surface this in UI so users tune filters instead of expecting replays.
- Beta-header rotation is a first-class migration concern; store the header version and verification date the routine was authored against so you can warn on upcoming rotation.

## See Also

- [`task-types-and-lifecycle.md`](task-types-and-lifecycle.md) — where routines fit in the task-family taxonomy
- [`../../ai-coding-agents-remote-runtime/SKILL.md`](../../ai-coding-agents-remote-runtime/SKILL.md) — routines as the canonical Anthropic-cloud remote runtime
- [`../../ai-coding-agents-sessions/SKILL.md`](../../ai-coding-agents-sessions/SKILL.md) — fresh-session-per-event session model
- [`../../ops-incident-response/SKILL.md`](../../ops-incident-response/SKILL.md) — alert → `/fire` integration pattern
