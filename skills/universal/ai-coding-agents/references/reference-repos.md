# Reference Repos for Background Coding Agents

Load when building a background coding agent (trigger → sandbox → PR) or one of its layers, and you want open source code to read before you design. List compiled 2026-10-15; licence and archive notes are from that date.

## Contents

[How to use](#how-to-use-this-list) · [Decision matrix](#decision-matrix-what-to-take-from-each-repo) · [Harness](#1-harness-the-agent-loop) · [Complete copies](#2-complete-open-copies-of-a-background-agent) · [Block tooling](#3-blocks-agent-tooling-around-goose) · [Sandbox](#4-sandbox-and-devbox) · [Fleet](#5-changes-across-many-repos-fleet-layer) · [MCP gateway](#6-mcp-tool-gateway) · [Control plane](#7-control-plane) · [Review](#8-verification-and-review)

## How to use this list

- Read for patterns, copy only after a licence check. Before you reuse code, open the repo's `LICENSE` and its archive banner on the day you use it. Notes below go stale.
- Pick the layer first, then read one harness and one complete copy end to end before reading the building blocks. The published company systems put their effort in the sandbox and the deterministic gates around the agent loop, not in the loop itself.
- Clone shallow (`git clone --depth 1`) for reading; unshallow only to trace history.
- "Used by" notes repeat what the companies wrote in public engineering posts. Check the primary post before you quote one.

## Decision matrix: what to take from each repo

Load when you must decide adopt, fork, copy a pattern, or skip. Verdicts come from a read-only code review of shallow clones on 2026-10-15; nothing was built or run, so behaviour claims are from reading code. Re-check a claim at the commit you use.

**Default.** Adopt one agent loop unmodified and pinned, and build the environment around it: sandbox, egress, model gateway, budgets, PR identity, verifier. No company that published its background agent released that environment layer; it is the part you build. Fork a loop only when a control you must have cannot be met by its settings, hooks, a wrapper or a proxy, and someone is staffed to merge upstream releases for as long as the fork lives.

**Fork question.** goose is the usual fork candidate (Stripe forked it). Read before deciding: headless runs need Auto mode, which allows every tool; PreToolUse and Stop hooks fail open by default; the egress inspector only logs. A fork that fixes these must then track a fast-moving upstream. A closed CLI (Claude Code) cannot be forked at all; its Python Agent SDK is an MIT wrapper that starts the same CLI.

### Pick by scenario

| Scenario | Take | Why | Trap |
| --- | --- | --- | --- |
| Single locked container running a vendor CLI | Patterns from `claude-code-action`, `codex-action`; option names from `claude-agent-sdk-python` | Action restores agent config paths from the base branch and scrubs secrets from subprocess env; codex-action starts its key proxy in a separate step and drops sudo | claude-code-action trusts project settings by default |
| Swap or add an agent loop behind one interface | OpenCode unmodified; goose only with the fork question answered | OpenCode: MIT, server API with an event stream, permission rule engine, resumable sessions | Neither has a whole-run cost cap; OpenCode uses one shared password and in-process permissions |
| Sandbox, egress, secrets | gVisor as runtime; patterns from E2B `runtime` and microsandbox; secret scan from `docker/mcp-gateway` | Hostname-aware egress (SNI or Host check, pinned DNS, reject internal IPs) and placeholder secrets swapped outside the guest | gVisor has no domain filtering; a restored Firecracker snapshot repeats entropy and tokens; Modal and E2B defaults allow network |
| PR pipeline, review and trust | Patterns from `block/review`, Open SWE; Open-Inspect as counter-example | review drops findings without file and line and runs a disprove pass; Open SWE blocks the agent's own `gh pr create` and gates workflow-file pushes | Open-Inspect silently falls back to the App token and caches credentials in snapshots; pr-agent skips bot PRs by default |
| Codemods and legacy migration | ast-grep with tree-sitter; fixture style from `codemod`; flow from Slack's enzyme-to-rtl-codemod | ast-grep `kind` rules work where its PHP pattern syntax does not; codemod has fixture tests | No public PHP-to-React recipe catalog exists; Slack's tool passes on a substring "FAIL" check and only warns when tests disappear |
| Read a whole platform for patterns | Open-Inspect, Open SWE | Closest open copies of Ramp Inspect and of a PR-trust design | Open SWE production needs a licence key; Open-Inspect is single-tenant |

### Verdict per repo

Adopt = use as-is. Copy pattern = licence permits; rewrite in your own code. Ideas only = licence, archive state or maturity blocks copying. Skip = not useful for a background agent, or not examined.

| Verdict | Repos |
| --- | --- |
| Adopt | `google/gvisor`, `ast-grep/ast-grep`, `tree-sitter/tree-sitter` |
| Copy pattern | `anomalyco/opencode`, `openai/codex`, `anthropics/claude-agent-sdk-python`, `anthropics/claude-code-action`, `openai/codex-action`, `ColeMurray/background-agents`, `langchain-ai/open-swe`, `block/review`, `block/agent-skills` (blob and entropy scan in CI), `e2b-dev/runtime`, `superradcompany/microsandbox`, `docker/mcp-gateway`, `codemod/codemod`, `Skyscanner/turbolift`, Slack `enzyme-to-rtl-codemod` |
| Ideas only | `aaif-goose/goose` (fork question), `BerriAI/moyai`, `angristan/netclode` (no licence), `vercel-labs/open-agents`, `OpenHands/OpenHands`, `multica-ai/multica` (source-available), `proliferate-ai/proliferate` (AGPL), `terragon-labs/terragon-oss`, `block/agent-task-queue`, `block/builderbot`, `block/ai-rules`, `block/aittributor`, `modal-labs/modal-client`, `firecracker-microvm/firecracker`, `coder/coder` (AGPL plus enterprise), `devcontainers/spec`, `devcontainers/cli`, `IBM/mcp-context-forge`, `openrewrite/rewrite` (no PHP; some modules source-available), `lindell/multi-gitter`, `sourcegraph/src-cli`, `uber/piranha`, `The-PR-Agent/pr-agent`, `cloudflare/agents`, `temporalio/temporal` |
| Skip | `anthropics/claude-agent-sdk-typescript` (not open source), `Aider-AI/aider`, `e2b-dev/E2B` (SDK only), `daytonaio/daytona` (archived), `block/builderlab-cli`, `block/goose-plugins`, `block/goose2`, `block/flight-control`, `modelcontextprotocol/servers`, `stripe/ai`, Atlassian `rovo-dev-action` (runs with `--yolo`, no sandbox) |

Company product repos from Stripe, Ramp and Spotify (CLIs, product MCP servers, product plugins) were not examined in depth; none contains their background-agent system.

## 1. Harness (the agent loop)

| Repo | Note |
| --- | --- |
| [aaif-goose/goose](https://github.com/aaif-goose/goose) | Block's agent; Stripe's Minions forked it. Old `block/goose` URL redirects here. |
| [anomalyco/opencode](https://github.com/anomalyco/opencode) | Harness behind Ramp Inspect. Old `sst/opencode` URL redirects here. |
| [anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python) | SDK behind Spotify Honk. MIT. |
| [anthropics/claude-agent-sdk-typescript](https://github.com/anthropics/claude-agent-sdk-typescript) | Not open source ("All rights reserved"): read, do not copy. |
| [openai/codex](https://github.com/openai/codex) | |
| [Aider-AI/aider](https://github.com/Aider-AI/aider) | |

## 2. Complete open copies of a background agent

| Repo | Note |
| --- | --- |
| [ColeMurray/background-agents](https://github.com/ColeMurray/background-agents) | "Open-Inspect", modelled on Ramp Inspect. |
| [langchain-ai/open-swe](https://github.com/langchain-ai/open-swe) | Production deployments need a licence key. |
| [BerriAI/moyai](https://github.com/BerriAI/moyai) | |
| [angristan/netclode](https://github.com/angristan/netclode) | No licence: ideas only. |
| [vercel-labs/open-agents](https://github.com/vercel-labs/open-agents) | |
| [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands) | |
| [multica-ai/multica](https://github.com/multica-ai/multica) | Source-available, not open source. |
| [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) | CI trigger surface for Claude Code. |
| [openai/codex-action](https://github.com/openai/codex-action) | CI trigger surface for Codex. |
| [proliferate-ai/proliferate](https://github.com/proliferate-ai/proliferate) | AGPL-3.0; now a macOS IDE. |
| [terragon-labs/terragon-oss](https://github.com/terragon-labs/terragon-oss) | Shutdown snapshot: frozen. |

## 3. Block's agent tooling around goose

| Repo | Note |
| --- | --- |
| [block/review](https://github.com/block/review) | LLM code reviewer built on goose. |
| [block/agent-task-queue](https://github.com/block/agent-task-queue) | |
| [block/builderbot](https://github.com/block/builderbot) | |
| [block/builderlab-cli](https://github.com/block/builderlab-cli) | Default endpoint is Block's internal goose service; point it elsewhere. |
| [block/ai-rules](https://github.com/block/ai-rules) | |
| [block/agent-skills](https://github.com/block/agent-skills) | |
| [block/goose-plugins](https://github.com/block/goose-plugins) | |
| [block/goose2](https://github.com/block/goose2) | |
| [block/aittributor](https://github.com/block/aittributor) | |
| [block/flight-control](https://github.com/block/flight-control) | Archived. |

## 4. Sandbox and devbox

| Repo | Note |
| --- | --- |
| [modal-labs/modal-client](https://github.com/modal-labs/modal-client) | Ramp's sandbox vendor. Client only; the service is paid. |
| [e2b-dev/E2B](https://github.com/e2b-dev/E2B) | |
| [e2b-dev/runtime](https://github.com/e2b-dev/runtime) | |
| [superradcompany/microsandbox](https://github.com/superradcompany/microsandbox) | |
| [firecracker-microvm/firecracker](https://github.com/firecracker-microvm/firecracker) | microVM layer. |
| [google/gvisor](https://github.com/google/gvisor) | User-space kernel isolation. |
| [coder/coder](https://github.com/coder/coder) | AGPL-3.0. |
| [daytonaio/daytona](https://github.com/daytonaio/daytona) | Archived; development moved private. |
| [devcontainers/spec](https://github.com/devcontainers/spec) | Environment definition format. |
| [devcontainers/cli](https://github.com/devcontainers/cli) | |

## 5. Changes across many repos (fleet layer)

| Repo | Note |
| --- | --- |
| [openrewrite/rewrite](https://github.com/openrewrite/rewrite) | Spotify uses it. Some recipes need a commercial licence. |
| [Skyscanner/turbolift](https://github.com/Skyscanner/turbolift) | |
| [lindell/multi-gitter](https://github.com/lindell/multi-gitter) | |
| [sourcegraph/src-cli](https://github.com/sourcegraph/src-cli) | |
| [uber/piranha](https://github.com/uber/piranha) | Stale-flag cleanup. |
| [codemod/codemod](https://github.com/codemod/codemod) | |

## 6. MCP tool gateway

| Repo | Note |
| --- | --- |
| [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | Reference servers. |
| [docker/mcp-gateway](https://github.com/docker/mcp-gateway) | |
| [IBM/mcp-context-forge](https://github.com/IBM/mcp-context-forge) | |
| [stripe/ai](https://github.com/stripe/ai) | Stripe's customer-facing agent toolkit, not its internal tool gateway. |

## 7. Control plane

| Repo | Note |
| --- | --- |
| [cloudflare/agents](https://github.com/cloudflare/agents) | Ramp uses it. |
| [temporalio/temporal](https://github.com/temporalio/temporal) | Durable execution; Ramp's on-call agent uses it. |

## 8. Verification and review

| Repo | Note |
| --- | --- |
| [ast-grep/ast-grep](https://github.com/ast-grep/ast-grep) | Structural search and rewrite for deterministic gates. |
| [tree-sitter/tree-sitter](https://github.com/tree-sitter/tree-sitter) | |
| [The-PR-Agent/pr-agent](https://github.com/The-PR-Agent/pr-agent) | |
