# Coding Agent Usage Tracking

Practical guide to measuring actual token usage and costs from Claude Code and OpenAI Codex CLI sessions using the ccusage tool family.

**Freshness anchor:** April 2026 — covers ccusage (Claude Code), @ccusage/codex (Codex CLI), @ccusage/mcp. Verify CLI options with `--help` before recommending; both tools evolve rapidly.

---

## Table Of Contents

- [Why Track CLI Agent Usage](#why-track-cli-agent-usage)
- [Data Sources](#data-sources)
- [Raw Log Formats](#raw-log-formats)
- [DIY Parsing Without ccusage](#diy-parsing-without-ccusage)
- [ccusage For Claude Code](#ccusage-for-claude-code)
- [ccusage Codex For OpenAI Codex CLI](#ccusage-codex-for-openai-codex-cli)
- [Common Options](#common-options)
- [JSON Export And Dashboard Integration](#json-export-and-dashboard-integration)
- [Unified Cost View](#unified-cost-view)
- [MCP Integration](#mcp-integration)
- [Cost Alerting Patterns](#cost-alerting-patterns)
- [Anti-Patterns](#anti-patterns)
- [Related References](#related-references)
- [Primary Sources](#primary-sources)

---

## Why Track CLI Agent Usage

[`agent-economics.md`](agent-economics.md) provides the ROI framework for projecting agent costs. This guide complements it with actual measurement.

| Concern | Projection (agent-economics) | Measurement (this guide) |
|---------|------------------------------|--------------------------|
| "Will this agent pay for itself?" | ROI formula, break-even volume | Actual monthly spend vs value created |
| "Which model costs most?" | Per-model pricing tables | Per-model token breakdown from real sessions |
| "Are we within budget?" | Monthly cost projections | Daily/weekly spend alerts from CLI data |
| "Should we kill this agent?" | Kill signals and thresholds | Actual cost trend to validate kill decision |

Use cases:

- Individual developer cost awareness
- Team budget enforcement and allocation
- ROI validation against projected costs from agent-economics framework
- Audit trail for enterprise compliance

---

## Data Sources

Both tools read local JSONL logs. No API calls, no credentials, no data leaves the machine.

| CLI Tool | Log Location | Override | Format |
|----------|-------------|----------|--------|
| Claude Code | `~/.config/claude/projects/` (v1.0.30+), legacy `~/.claude/projects/` | — | JSONL per conversation |
| OpenAI Codex | `~/.codex/sessions/` | `CODEX_HOME` env var | JSONL per session |

Logs accumulate automatically — no opt-in required.

---

## Raw Log Formats

Understanding the raw JSONL structure lets you query data directly, build custom analysis, or debug ccusage output.

### Claude Code JSONL Schema

Each file at `~/.claude/projects/{project-hash}/{session-uuid}.jsonl` contains one JSON object per line. Assistant messages carry token usage:

```json
{
  "type": "assistant",
  "sessionId": "session-uuid",
  "timestamp": "2026-04-07T14:23:01.000Z",
  "message": {
    "model": "claude-sonnet-4-6",
    "id": "msg_abc123",
    "usage": {
      "input_tokens": 3500,
      "output_tokens": 420,
      "cache_creation_input_tokens": 14492,
      "cache_read_input_tokens": 13359
    }
  },
  "costUSD": 0.05,
  "requestId": "req_xyz789"
}
```

**Token fields** (in `message.usage`):

| Field | Meaning |
|-------|---------|
| `input_tokens` | Standard prompt tokens |
| `output_tokens` | Generated response tokens |
| `cache_creation_input_tokens` | Tokens written to cache (optional) |
| `cache_read_input_tokens` | Tokens read from cache — cheaper rate (optional) |

**Other useful fields:**
- `message.model` — exact model name (e.g., `claude-opus-4-7`, `claude-opus-4-6`, `claude-sonnet-4-6`)
- `costUSD` — pre-calculated cost (may be 0; ccusage recalculates from tokens when using `--mode calculate`)
- `timestamp` — ISO 8601, used for date grouping
- `sessionId` — groups messages into conversations

**Additional data sources on disk:**
- `~/.claude/stats-cache.json` — pre-aggregated daily/model stats (messageCount, tokensByModel, modelUsage with per-model totals)
- `~/.claude/usage-data/session-meta/{session-uuid}.json` — per-session summaries with tool_counts, languages, git activity

### Codex CLI JSONL Schema

Each file at `~/.codex/sessions/YYYY/MM/DD/rollout-{timestamp}-{uuid}.jsonl` contains timestamped events. Token data is in `event_msg` entries with `token_count` type:

```json
{
  "timestamp": "2026-04-07T14:30:45.433Z",
  "type": "event_msg",
  "payload": {
    "type": "token_count",
    "info": {
      "total_token_usage": {
        "input_tokens": 622719,
        "cached_input_tokens": 575104,
        "output_tokens": 9682,
        "reasoning_output_tokens": 3918,
        "total_tokens": 632401
      },
      "last_token_usage": {
        "input_tokens": 61358,
        "cached_input_tokens": 61056,
        "output_tokens": 371,
        "reasoning_output_tokens": 173,
        "total_tokens": 61729
      }
    }
  }
}
```

**Key difference from Claude Code:** Codex logs **cumulative** totals (`total_token_usage`) plus the **last turn** delta (`last_token_usage`). ccusage computes per-turn deltas by subtracting previous cumulative values.

**Token fields** (in `payload.info.total_token_usage` or `last_token_usage`):

| Field | Meaning |
|-------|---------|
| `input_tokens` | Standard prompt tokens |
| `cached_input_tokens` | Tokens served from cache — cheaper rate |
| `output_tokens` | Generated tokens (includes reasoning) |
| `reasoning_output_tokens` | Reasoning tokens — informational, not separately billed |
| `total_tokens` | Sum of input + output |

For cost accounting, sum **only** `last_token_usage` per request. `total_token_usage`
is cumulative within an epoch and summing it across events duplicates tokens. If
`last_token_usage` is absent, reconstruct a delta from consecutive totals; a
decrease starts a new epoch (for example after context compaction or model
change). Never add `reasoning_output_tokens` again: it is already within
`output_tokens`.

`scripts/codex-usage.py traces` emits bounded accounting rows only (session ID,
timestamp, counters, model, source and pricing provenance), never prompt or tool
content. Cost is fail-closed as `unpriced` unless the exact model ID, standard
service tier, standard context-pricing class and every applicable cache rate are
known. A total-delta reconstruction is marked `estimated`; `last_token_usage`
with all of those conditions is `exact`. A model ID alone cannot distinguish
GPT-5.6 Sol standard from Fast or long-context billing.

**Model name** comes from `turn_context` entries (separate JSONL lines with `type: "turn_context"`):

```json
{
  "type": "turn_context",
  "payload": {
    "model": "gpt-5.4",
    "effort": "xhigh"
  }
}
```

**Other Codex data sources:**
- `~/.codex/session_index.jsonl` — quick lookup with session ID, thread name, timestamp
- `~/.codex/history.jsonl` — global session history
- `~/.codex/state_5.sqlite` — `threads` table has aggregated tokens_used per session

---

## DIY Parsing Without ccusage

### Claude Code — Daily Token Totals (jq)

```bash
# Sum tokens per model across all sessions for today
find ~/.claude/projects -name '*.jsonl' -newer /tmp/today_marker | \
  xargs cat | \
  jq -r 'select(.message.usage != null) |
    "\(.message.model // "unknown"),\(.message.usage.input_tokens),\(.message.usage.output_tokens),\(.message.usage.cache_creation_input_tokens // 0),\(.message.usage.cache_read_input_tokens // 0)"' | \
  awk -F, '{m[$1]+=$2; o[$1]+=$3; cc[$1]+=$4; cr[$1]+=$5}
    END {for (k in m) printf "%s: input=%d output=%d cache_create=%d cache_read=%d\n", k, m[k], o[k], cc[k], cr[k]}'
```

### Claude Code — Quick Session Summary (Python)

```python
import json, glob, os
from collections import defaultdict

totals = defaultdict(lambda: {"input": 0, "output": 0, "cache_read": 0, "cache_create": 0})

for path in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")):
    for line in open(path):
        try:
            rec = json.loads(line)
            usage = rec.get("message", {}).get("usage")
            if not usage:
                continue
            model = rec.get("message", {}).get("model", "unknown")
            totals[model]["input"] += usage.get("input_tokens", 0)
            totals[model]["output"] += usage.get("output_tokens", 0)
            totals[model]["cache_read"] += usage.get("cache_read_input_tokens", 0)
            totals[model]["cache_create"] += usage.get("cache_creation_input_tokens", 0)
        except json.JSONDecodeError:
            continue

for model, t in sorted(totals.items()):
    print(f"{model}: in={t['input']:,} out={t['output']:,} "
          f"cache_read={t['cache_read']:,} cache_create={t['cache_create']:,}")
```

### Claude Code — Use stats-cache.json (fastest)

```bash
# Pre-aggregated daily stats — no JSONL parsing needed
# dailyActivity is an array of {date, messageCount, sessionCount, toolCallCount}
jq '.dailyActivity | sort_by(.date) | .[-7:][] |
  "\(.date): messages=\(.messageCount) sessions=\(.sessionCount) tools=\(.toolCallCount)"' \
  ~/.claude/stats-cache.json

# Per-model all-time totals
jq '.modelUsage | to_entries[] |
  "\(.key): input=\(.value.inputTokens) output=\(.value.outputTokens) cache_read=\(.value.cacheReadInputTokens)"' \
  ~/.claude/stats-cache.json
```

### Codex — Extract Token Deltas (jq)

```bash
# Get per-turn token usage from a single session
jq -r 'select(.type == "event_msg" and .payload.type == "token_count") |
  .payload.info.last_token_usage |
  "\(.input_tokens),\(.cached_input_tokens),\(.output_tokens),\(.reasoning_output_tokens)"' \
  ~/.codex/sessions/2026/04/07/rollout-*.jsonl
```

### Codex — Daily Totals Across Sessions (Python)

Note: Codex JSONL entries can have null `last_token_usage` — always fall back to `total_token_usage` and guard against non-dict values.

```python
import json, glob, os
from collections import defaultdict

daily = defaultdict(lambda: {"input": 0, "output": 0, "cached": 0, "reasoning": 0})

for path in glob.glob(os.path.expanduser("~/.codex/sessions/*/*/*/**.jsonl")):
    for line in open(path):
        try:
            rec = json.loads(line)
            if not isinstance(rec, dict) or rec.get("type") != "event_msg":
                continue
            payload = rec.get("payload")
            if not isinstance(payload, dict) or payload.get("type") != "token_count":
                continue
            info = payload.get("info")
            if not isinstance(info, dict):
                continue
            usage = info.get("last_token_usage")
            if not isinstance(usage, dict):
                usage = info.get("total_token_usage")
            if not isinstance(usage, dict):
                continue
            date = rec.get("timestamp", "")[:10]
            if not date:
                continue
            daily[date]["input"] += usage.get("input_tokens", 0) or 0
            daily[date]["output"] += usage.get("output_tokens", 0) or 0
            daily[date]["cached"] += usage.get("cached_input_tokens", 0) or 0
            daily[date]["reasoning"] += usage.get("reasoning_output_tokens", 0) or 0
        except Exception:
            continue

for date in sorted(daily):
    t = daily[date]
    print(f"{date}: in={t['input']:,} out={t['output']:,} "
          f"cached={t['cached']:,} reasoning={t['reasoning']:,}")
```

### Standalone Scripts

For a full CLI experience without ccusage, use the scripts in this skill:

```bash
# Claude Code
python scripts/claude-usage.py daily                          # daily activity from stats-cache
python scripts/claude-usage.py monthly --since 2026-01-01     # monthly from JSONL
python scripts/claude-usage.py sessions --last 10             # recent sessions
python scripts/claude-usage.py models                         # per-model all-time totals
python scripts/claude-usage.py daily --json                   # JSON output

# Codex
python scripts/codex-usage.py daily                           # daily token/cost report
python scripts/codex-usage.py monthly                         # monthly aggregated
python scripts/codex-usage.py sessions --last 5               # recent sessions
python scripts/codex-usage.py models                          # per-model breakdown
python scripts/codex-usage.py daily --since 2026-04-01 --json # filtered JSON
```

Both scripts are stdlib-only Python (no pip install), support `--since`/`--until`/`--json`/`--last` flags, and include approximate cost estimates.

Scripts: [`../scripts/claude-usage.py`](../scripts/claude-usage.py), [`../scripts/codex-usage.py`](../scripts/codex-usage.py)

### How ccusage Adds Value Over DIY

| What ccusage handles | DIY effort |
|---------------------|-----------|
| Deduplication by message+request ID hash | You must track seen IDs yourself |
| LiteLLM pricing lookup and caching | You must maintain a pricing table |
| Delta calculation from Codex cumulative totals | You must track previous totals per session |
| Responsive terminal tables | Raw numbers only |
| Date/timezone grouping with locale formatting | Manual date parsing |
| Model alias resolution (e.g., `gpt-5-codex` → `gpt-5`) | You must maintain alias map |

**Recommendation:** Use DIY for quick one-off queries or custom analysis. Use ccusage for recurring reporting and cost monitoring.

---

## ccusage For Claude Code

### Installation

```bash
# Run without global install (recommended)
npx ccusage daily
bunx ccusage daily

# Global install
npm install -g ccusage
```

### Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `daily` | Usage grouped by calendar date | `ccusage daily` |
| `weekly` | Usage grouped by week | `ccusage weekly` |
| `monthly` | Monthly aggregated report | `ccusage monthly` |
| `sessions` | Per-conversation detail | `ccusage sessions` |
| `blocks` | 5-hour billing window tracking | `ccusage blocks` |

### Key Options (ccusage-specific)

| Option | Purpose |
|--------|---------|
| `--breakdown`, `-b` | Show per-model cost breakdown |
| `--instances`, `-i` | Group daily results by project |
| `--project NAME`, `-p` | Filter to a specific project |
| `--start-of-week mon\|sun` | Week boundary for `weekly` command |
| `--active`, `-a` | Show current active block (`blocks`) |
| `--live` | Live monitoring mode (`blocks`) |
| `--mode auto\|calculate\|display` | Cost calculation method |

### Output

Each report shows per-model rows with: input tokens, cached input tokens, output tokens, reasoning output tokens, total tokens, and calculated cost in USD.

---

## ccusage Codex For OpenAI Codex CLI

**Status:** Experimental beta. Expect breaking changes.

### Installation

```bash
# Run without global install (recommended — always use @latest)
npx @ccusage/codex@latest daily
bunx @ccusage/codex@latest daily

# Shell alias (recommended)
alias ccusage-codex='npx @ccusage/codex@latest'
```

### Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `daily` | Usage grouped by calendar date | `ccusage-codex daily` |
| `monthly` | Monthly aggregated report | `ccusage-codex monthly` |
| `sessions` | Per-session detail | `ccusage-codex sessions` |

Note: `weekly` and `blocks` are not available in @ccusage/codex. Check `--help` for current command list.

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `CODEX_HOME` | Override root directory (default: `~/.codex`) |
| `LOG_LEVEL` | Verbosity: 0 (silent) through 5 (trace) |

### Limitations

- No data before September 6, 2025 (when Codex CLI started emitting token events)
- Some early September 2025 sessions without model metadata are skipped
- Falls back to `gpt-5` model name when metadata is missing

---

## Common Options

Shared across both `ccusage` and `@ccusage/codex`:

| Option | Purpose | Example |
|--------|---------|---------|
| `--json`, `-j` | Machine-readable JSON output | `ccusage daily --json` |
| `--since DATE` | Filter from date (YYYY-MM-DD or YYYYMMDD) | `--since 2026-04-01` |
| `--until DATE` | Filter to date (inclusive) | `--until 2026-04-07` |
| `--timezone ZONE`, `-z` | Timezone for date grouping | `-z America/New_York` |
| `--locale LOCALE`, `-l` | Date formatting locale | `-l en-US` |
| `--offline`, `-O` | Use cached pricing (no network) | `--offline` |
| `--config PATH` | Custom config file path | `--config ./my-config.json` |

### Configuration File Precedence

1. Command-line arguments (highest)
2. Custom config file (`--config`)
3. Local project config (`.ccusage/ccusage.json` or `.ccusage/codex.json`)
4. User config (`~/.config/claude/ccusage.json`)
5. Built-in defaults (lowest)

---

## JSON Export And Dashboard Integration

Both tools support `--json` for programmatic output.

```bash
# Export daily Claude Code spend to file
ccusage daily --json --since 2026-04-01 > claude-code-april.json

# Extract just dates and costs with jq
ccusage daily --json | jq '.daily[] | {date, costUSD}'

# Export Codex monthly spend
npx @ccusage/codex@latest monthly --json > codex-monthly.json
```

### JSON Structure (daily example)

```json
{
  "daily": [
    {
      "date": "2026-04-07",
      "inputTokens": 125000,
      "cachedInputTokens": 40000,
      "outputTokens": 30000,
      "reasoningOutputTokens": 5000,
      "totalTokens": 155000,
      "costUSD": 1.23,
      "models": {
        "claude-sonnet-4-6": { "inputTokens": 125000, "outputTokens": 30000, "..." : "..." }
      }
    }
  ],
  "totals": { "inputTokens": 125000, "costUSD": 1.23, "..." : "..." }
}
```

Pipe JSON into Metabase, Grafana, or a spreadsheet for team dashboards.

---

## Unified Cost View

### Shell Aliases

```bash
# Today's spend across both tools
alias ai-spend-today='echo "=== Claude Code ===" && ccusage daily --since $(date +%Y-%m-%d) && echo "=== Codex ===" && npx @ccusage/codex@latest daily --since $(date +%Y-%m-%d)'

# Monthly summary
alias ai-spend-month='echo "=== Claude Code ===" && ccusage monthly && echo "=== Codex ===" && npx @ccusage/codex@latest monthly'

# JSON combined export
alias ai-spend-json='echo "{\"claude_code\":" && ccusage daily --json && echo ",\"codex\":" && npx @ccusage/codex@latest daily --json && echo "}"'
```

### Cross-Tool Command Comparison

| Dimension | ccusage (Claude Code) | @ccusage/codex (Codex) |
|-----------|----------------------|------------------------|
| Today's spend | `ccusage daily --since $(date +%Y-%m-%d)` | `npx @ccusage/codex@latest daily --since $(date +%Y-%m-%d)` |
| This month | `ccusage monthly` | `npx @ccusage/codex@latest monthly` |
| Session drill-down | `ccusage sessions` | `npx @ccusage/codex@latest sessions` |
| JSON for scripts | `ccusage daily --json` | `npx @ccusage/codex@latest daily --json` |
| Per-model breakdown | `ccusage daily -b` | Built into default output |

---

## MCP Integration

`@ccusage/mcp` exposes usage data as MCP tools so agents can query their own cost data.

### Use Cases

- Agent self-monitoring: check remaining budget before proceeding
- Cost-aware agent loops: degrade to cheaper model when budget is low
- Automated cost reports via agent tools

### Setup

Add to your MCP configuration (`.mcp.json` or `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "ccusage": {
      "command": "npx",
      "args": ["@ccusage/mcp@latest"]
    }
  }
}
```

For MCP server configuration details, see [`../../agents-mcp/SKILL.md`](../../agents-mcp/SKILL.md).

---

## Cost Alerting Patterns

### Simple Threshold Script

```bash
#!/bin/bash
# check-ai-spend.sh — alert when daily spend exceeds budget
DAILY_BUDGET=5.00
SPEND=$(ccusage daily --since "$(date +%Y-%m-%d)" --json | jq '.totals.costUSD // 0')

if (( $(echo "$SPEND > $DAILY_BUDGET" | bc -l) )); then
  echo "ALERT: Daily Claude Code spend \$$SPEND exceeds budget \$$DAILY_BUDGET"
  # Add: slack webhook, email, or desktop notification
fi
```

### Cron-Based Monitoring

```cron
# Check Claude Code spend every 4 hours
0 */4 * * * /path/to/check-ai-spend.sh >> /var/log/ai-spend.log 2>&1
```

### Team-Level Patterns

- Aggregate individual developer JSON exports into a shared dashboard
- Set per-developer daily or weekly budgets with threshold scripts
- Weekly automated cost report via cron and Slack webhook
- Compare actual spend against [`agent-economics.md`](agent-economics.md) ROI projections

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|--------------|-------------|-----------------|
| Never checking usage | Surprise bills, no ROI data | Run `ccusage monthly` at minimum |
| Checking only totals | Cannot optimize per-model costs | Use `--breakdown` or `--json` for per-model data |
| Manual JSONL parsing for recurring reports | Fragile; format changes break scripts | Use ccusage `--json` for stable output; reserve DIY for one-off analysis |
| Ignoring cached input tokens | Overestimates actual cost | ccusage already accounts for cached pricing |
| Tracking one tool but not the other | Incomplete cost picture | Track both Claude Code and Codex |
| Hardcoding pricing in scripts | Prices change frequently | Let ccusage fetch from LiteLLM or use `--offline` cache |

---

## Related References

- [Agent Economics & ROI Framework](agent-economics.md) — ROI projections and cost decision framework
- [Evaluation & Observability](evaluation-and-observability.md) — Production telemetry with OpenTelemetry
- [Code & SWE Agents](code-swe-agents.md) — Coding agent operating patterns
- [`dev-ai-coding-metrics`](../../dev-ai-coding-metrics/SKILL.md) — Pilot metrics, adoption, and ROI scorecards
- [`agents-mcp`](../../agents-mcp/SKILL.md) — MCP server setup for @ccusage/mcp

## Primary Sources

- ccusage (Claude Code): [github.com/ryoppippi/ccusage](https://github.com/ryoppippi/ccusage)
- @ccusage/codex (Codex CLI): [npmjs.com/package/@ccusage/codex](https://www.npmjs.com/package/@ccusage/codex)
- @ccusage/mcp (MCP server): [npmjs.com/package/@ccusage/mcp](https://www.npmjs.com/package/@ccusage/mcp)
- Documentation: [ccusage.com](https://ccusage.com/)
