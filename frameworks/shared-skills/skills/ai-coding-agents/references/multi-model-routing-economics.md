# Multi-Model Routing Economics

Operational data for routing coding work between cheap workhorse models and premium reasoning models. Numbers and commands below are quoted **verbatim from a frozen 2026-04-28 working-day post** comparing Kimi K2.6 against Claude Opus 4.6/4.7 and GPT-5.2.

Source: @eng_khairallah1, 2026-04-28 — <https://x.com/eng_khairallah1/status/2049055333054857612>

> **Time-decaying data — read the reality-checks.** Model scores, prices, and context windows move in weeks. The **durable content of this file is the 85/15 routing *pattern* and the CLI/MCP operational surfaces, not the constants.** The quoted tables are preserved unaltered for attribution integrity; dated "May 2026 reality-check" callouts sit beside the stale ones. **Re-fetch live numbers from primary sources at use time** before using any figure to pick a model.
>
> Last reviewed against primary sources: **2026-05-17**.

Operational data only — no endorsement of any specific provider.

## Table of Contents

- [85/15 Routing Split](#8515-routing-split)
- [SWE-Bench Verified Numbers](#swe-bench-verified-numbers)
- [Per-Mtok Pricing](#per-mtok-pricing)
- [Context Window Tradeoff](#context-window-tradeoff)
- [Step Reduction and Planning Mode](#step-reduction-and-planning-mode)
- [Kimi CLI Operational Commands](#kimi-cli-operational-commands)
- [MCP Config Transfer](#mcp-config-transfer)
- [IDE Integration Surfaces](#ide-integration-surfaces)
- [Agent Swarm Capacity](#agent-swarm-capacity)
- [License](#license)

## 85/15 Routing Split

Practical split observed in mixed coding workloads:

- **~85%** of tasks: cheap workhorse handles end-to-end (refactors, tests, scaffolding, doc edits, scripted multi-file changes).
- **~15%** of tasks: route to premium reasoning model (architectural decisions, hard debugging, novel algorithm design, security-sensitive review).

The routing decision is per-task, not per-session — a session typically calls both models. Author reports ~85% reduction in weekly API spend after adopting the split.

## SWE-Bench Verified Numbers

| Model | SWE-Bench Verified |
|---|---|
| Claude Opus 4.6 | 80.8 |
| Kimi K2.6 | 80.2 |
| GPT-5.2 | 80.0 |

Spread is <1 point — capability is not the routing axis at this tier; cost and context are. (Note: the same article cites pricing against **Opus 4.7**; benchmark column above is what the author reported for the comparison.)

> **May 2026 reality-check (verified 2026-05-17).** The ~80% cluster above is **no longer the frontier — it is now the workhorse tier.** SWE-Bench Verified standings (self-reported leaderboard, [llm-stats.com](https://llm-stats.com/benchmarks/swe-bench-verified)): Claude **Opus 4.7 = 87.6%** (GA, released 2026-04-16, 1M ctx) opened a ~7-point gap over the Opus 4.6 / Kimi K2.6 / GPT-5.2 cluster (≈80.0–80.8%); a non-GA **Claude Mythos Preview** tops the board at **93.9%** (preview, not generally available — do not route production to it). Vendor-reported **GPT-5.5 ≈88.7%** (OpenAI, 2026-04) is not yet on the independent board. **Re-read for the routing pattern, not the 80% numbers**: the conclusion "capability is not the routing axis *at the workhorse tier*" still holds; the premium tier the 15% routes to has itself moved up a generation.

## Per-Mtok Pricing

| Model | Input ($/Mtok) | Output ($/Mtok) | Relative |
|---|---|---|---|
| Kimi K2.6 | 0.80 | 3.60 | baseline |
| Claude Opus 4.7 | 5.00 | 25.00 | ~7× more expensive |
| GLM-5.1 | — | — | Kimi is ~50% cheaper |

Drives the workhorse choice in the 85/15 split.

> **May 2026 reality-check (verified 2026-05-17).** Premium-tier pricing in the quoted table still holds: **Claude Opus 4.7 = $5.00 in / $25.00 out** per Mtok ([Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)) — rate unchanged, but Opus 4.7 ships a new tokenizer that can emit **~35% more tokens** for the same input, raising *effective* cost. Workhorse-tier figure has drifted: **Kimi K2.6 official API ≈ $0.60 in / $2.50 out** (third-party routers higher: OpenRouter ≈ $0.73/$3.49). New premium reference point: **GPT-5.5 ≈ $5.00 in / $30.00 out** (OpenAI, 2026-04). The ~7× premium-vs-workhorse ratio that drives the 85/15 economics still holds; the absolute numbers do not — re-fetch before costing a workload.

## Context Window Tradeoff

- Kimi K2.6: **262K tokens**.
- Claude Opus 4.7: up to **1M tokens**.

Long-codebase work that doesn't fit in 262K must either chunk or route to the 1M model. Most single-file or single-feature work fits comfortably in 262K.

## Step Reduction and Planning Mode

- K2.6 reports a **35% reduction in agent steps** vs K2.5 on the same tasks — fewer tool calls per completed task lowers wall-clock and per-task cost together.
- The model uses an explicit **thinking/planning mode**: it architects the structure first, then executes file by file referencing earlier decisions. Reduces hallucinated imports and contradictory files in multi-file refactors (author tested across 12-file refactor with no cross-file breakage).

## Kimi CLI Operational Commands

Install (Python **3.10+** required):

```bash
pip install kimi-code
kimi
```

Auth and session control:

```text
/login           # auth
/sessions        # list sessions
--continue       # resume previous session
/compact         # summarize history, free context, status bar shows usage
--yolo           # skip confirmation prompts (dangerous on unfamiliar codebases)
Ctrl-X           # toggle shell mode (run shell without leaving agent)
kimi acp         # launch in ACP mode for IDE integration
```

## MCP Config Transfer

Reuse an existing MCP config from another CLI:

```bash
kimi --mcp-config-file your-existing-config.json
```

Add servers individually:

```bash
kimi mcp add --transport http context7 https://mcp.context7.com/mcp
kimi mcp list
kimi mcp test context7
```

The `--transport http` flag and per-server URL form are the operational surface — match it when bringing servers across CLIs.

## IDE Integration Surfaces

- **VS Code**: extension on the marketplace.
- **Zed**: native support.
- **Cursor and JetBrains**: integrate via ACP (`kimi acp`).

If you already run Claude Code in VS Code/Zed/Cursor, the surface area for switching the workhorse is editor-level, not workflow-level.

## Agent Swarm Capacity

Up to **100 parallel sub-agents** per swarm. Currently runs through the **web interface only — CLI support announced as in progress at time of writing**. Capacity ceiling matters when planning fan-out workloads — most patterns stay well below 10, but bulk processing (e.g., per-document analysis across hundreds of files) can scale further.

## License

Kimi K2.6 model weights are released under **Apache 2.0**, full weights on Hugging Face. Affects whether self-hosted routing is viable for licensing-sensitive workloads.
