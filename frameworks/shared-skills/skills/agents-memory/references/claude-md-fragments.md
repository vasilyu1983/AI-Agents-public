# CLAUDE.md / AGENTS.md Paste-Ready Fragments

Reusable blocks for the highest-leverage project-memory sections. Each fragment carries a cache-protection or context-budget rationale — the *why* is what makes the block worth keeping in hot memory.

Sources: Paweł Huryn, ["Claude Code's Limits Are Generous. The Problem Is Your Harness."](https://x.com/PawelHuryn/status/2048170309396926577) (Apr 25, 2026); Thariq, ["Lessons from Building Claude Code"](https://x.com/trq212/status/2024574133011673516) and ["Session Management & 1M Context"](https://x.com/trq212/status/2044548257058328723); [Claude Code – Model configuration](https://code.claude.com/docs/en/model-config); [Codex – Subagents](https://developers.openai.com/codex/subagents).

## Table of Contents

- [Choosing A Variant](#choosing-a-variant)
- [When To Use Any Of These](#when-to-use-any-of-these)
- [1. Task Delegation Block](#1-task-delegation-block)
- [2. Preferred Tools Block](#2-preferred-tools-block)
- [3. Session Model & Effort](#3-session-model--effort)
- [4. Lean-Loading Hygiene](#4-lean-loading-hygiene-compact-rule-not-a-fragment)
- [What Not To Put In Project Memory](#what-not-to-put-in-project-memory)
- [Validation](#validation)

## Choosing A Variant

Each high-leverage block ships in three forms. Pick one per repo:

- **Neutral** — when `AGENTS.md` and `CLAUDE.md` are the same file (symlink) and both runtimes share the policy. Default choice.
- **Claude-specific** — when only Claude Code uses this repo, or when the repo's `CLAUDE.md` diverges from `AGENTS.md`.
- **Codex-specific** — when only Codex uses this repo, or when adding a Codex-only section under a `**Codex:**` heading inside a shared file.

Ship the neutral form unless a runtime has actually picked the wrong tool/model and the other handled it fine. Reactive, not preemptive.

## When To Use Any Of These

Add a fragment only after the *exception-file test*: the rule is hard to infer from the repo, matters most sessions, and prevents a repeated mistake. Do not paste fragments wholesale.

## 1. Task Delegation Block

**Why this belongs in CLAUDE.md / AGENTS.md.** Opus 4.7 does not fan out to subagents by default; Codex inherits parent reasoning unless told otherwise. Without an explicit delegation rule, the parent thread reads bulk content into its own context, blowing both cache and budget. A delegation block tells the agent *when* to delegate — the parent reasons; subagents do the work. Concrete model/effort values live in `.claude/agents/*.md` and `.codex/agents/*.toml`, not here.

### 1a. Neutral (shared AGENTS.md ↔ CLAUDE.md)

```markdown
## Task Delegation

Spawn subagents to isolate context, parallelize independent work, or offload bulk mechanical tasks. The parent should reason and route — not read.

Delegate to a **cheap subagent** (low effort, small model):
- Bulk mechanical work, no judgment (renames, format conversions, repetitive edits across N files).

Delegate to a **mid-tier subagent** (default effort, mid model):
- Scoped research, code exploration, in-scope synthesis (read N files, return a summary).

Keep on the **parent**:
- Planning, tradeoffs, multi-system reasoning, work that needs in-flight context.

Trigger fan-out when:
- The task touches 3+ independent files or paths.
- The work is read-heavy and the output is a summary, not a diff.
- Two or more steps have no shared state and can run in parallel.

Concrete model and effort values live in subagent definition files, not here.
```

### 1b. Claude Code

```markdown
## Task Delegation (Claude Code)

- **Haiku subagent**: bulk mechanical work, no judgment. Pair with `effort: low` in the subagent's frontmatter.
- **Sonnet subagent**: scoped research, code exploration, in-scope synthesis. Default `effort: medium`.
- **Opus on parent**: planning, tradeoffs, multi-system reasoning. Default `effort: medium` on this repo (raise to `high` for hard debugging via `/effort high`).

Trigger fan-out when the task touches 3+ independent files, is read-heavy with summary output, or has parallelizable steps with no shared state.

`CLAUDE_CODE_SUBAGENT_MODEL` sets the default model for any subagent without an explicit `model:` field.
```

### 1c. Codex

```markdown
## Task Delegation (Codex)

- **Cheap subagent** (`model_reasoning_effort = "low"`): bulk mechanical work, renames, format conversions.
- **Mid subagent** (`model_reasoning_effort = "medium"`): scoped research, summarization. Matches the parent's default on this repo.
- **Parent stays at `"medium"`** for planning. Raise to `"high"` only when debugging race conditions or cross-system tradeoffs — and finish that task before lowering again.

Subagent files live in `.codex/agents/*.toml` and inherit parent values when omitted. Define model and effort there, not here.
```

**Adapt by**: trimming to the tiers the repo actually uses; adding a project-specific "always delegate X" line if a recurring task fits (e.g. "log triage → mid-tier subagent").

## 2. Preferred Tools Block

**Why this belongs in CLAUDE.md / AGENTS.md.** Default tools are often the most expensive ones. The `Read` tool loads PDFs as images; screenshots and Chrome scraping push huge token payloads; un-tagged file references force grep-based search. A Preferred Tools block standardizes the cheap path so the agent does not have to re-derive it each session.

This block is largely runtime-agnostic — both Claude Code and Codex benefit from the same routing. Use the neutral form unless a runtime-specific MCP makes one path materially cheaper.

### 2a. Neutral (recommended)

```markdown
## Preferred Tools

### Data Fetching

- **Built-in fetch tool** (Claude `WebFetch`, Codex `web` / equivalent): free, text-only, works on public pages that don't block bots.
- **agent-browser CLI** (`npm i -g agent-browser && agent-browser install`): free, local Rust CLI + Chrome via CDP. Use for dynamic pages or auth walls. Prefer `snapshot` for AI-friendly DOM state and element refs for interaction.
- **Notice recurring fetch patterns and propose wrapping them as dedicated tools.** When the same fetch/parse logic comes up more than once, suggest a named wrapper and add it to `## Dedicated Tools` below.

### PDF Files

Use `pdftotext`, **not** the file-read tool. Reading a PDF directly loads it as an image (expensive). Read the PDF directly only when the user explicitly asks to analyze embedded images.

### Library Docs

Use the `context7` MCP for library/framework/SDK documentation. Avoid generic web search — context7 returns version-current API references and is far cheaper per token.

### Large Codebases

Prefer a code-graph index over raw file reads when one exists. Tag known files with explicit paths instead of relying on grep. See the `dev-context-code-graph` skill for graph generation.

## Dedicated Tools

<!-- List project-specific tools here. For each, link to its skill or script file. Keep entries short: name, when to use, where the implementation lives. -->
```

### 2b. Runtime-specific note (only when tools genuinely diverge)

```markdown
**Claude Code only:**
- For PDFs, never the `Read` tool — use `pdftotext` via Bash.

**Codex only:**
- (add only if a Codex-specific tool routing materially differs)
```

**Adapt by**: deleting sections the project doesn't need (e.g. drop the PDF block if the repo never handles PDFs); pinning specific versions if reproducibility matters; adding `## Dedicated Tools` entries as recurring patterns get extracted.

## 3. Session Model & Effort

**Why this belongs in CLAUDE.md / AGENTS.md.** Switching models mid-session invalidates the cached prefix and forces a full re-read. The session model must be picked at start and locked. A routing rule documents the default so the agent doesn't switch partway through and silently blow the cache. Effort is documented here so the parent knows when raising it is justified.

### 3a. Neutral

```markdown
## Session Model & Effort

- **Default**: medium reasoning effort on the parent. Sufficient for most CRUD, refactors, scoped tests, and scoped research.
- **Raise to high effort**: complex debugging, cross-system tradeoffs, architectural choices. Drop back when the hard part is done.
- **Drop to low effort**: trivial CRUD, renames, format-only changes — usually better expressed as a delegated subagent (see `## Task Delegation`).

**Do not switch models mid-session.** Switching invalidates the cached prefix and forces a full re-read. If the session needs a different model, finish the current task, clear the session, and start fresh.

Same rule for tools: do not add or remove MCP servers mid-session. Lock the toolset at start.
```

### 3b. Claude Code

```markdown
## Session Model & Effort (Claude Code)

- **Default model**: Opus 4.7 on the parent (set in user settings); subagents default to the model in `CLAUDE_CODE_SUBAGENT_MODEL` (set in `settings.json`, not here).
- **Default effort**: `medium`. Raise with `/effort high` for hard debugging or architectural work; reset with `/effort medium` after.
- **Reserve `xhigh` and `max`** for tasks where reasoning depth is the bottleneck. They burn tokens fast.
- **Do not `/model` mid-session.** Switching invalidates the cached prefix. Finish the task, `/clear`, restart.
- **Lock the MCP set at start.** Adding or removing servers mid-session has the same cache cost.
```

### 3c. Codex

```markdown
## Session Model & Effort (Codex)

- **Default model**: set in `~/.codex/config.toml` (`model = "..."`). Subagents inherit unless they declare their own.
- **Default `model_reasoning_effort = "medium"`** on the parent. Sufficient for most work.
- **Raise to `"high"`** for race-condition debugging, cross-system tradeoffs, or planning that touches 3+ services. Lower back when the hard part is done.
- **Drop to `"low"`** only via a delegated subagent — keeping the parent at low silently degrades planning quality.
- **Do not change `model` mid-session.** Codex re-reads context on model swap.
```

**Adapt by**: changing the default if the team's economics favor a different baseline; pinning a specific model version when reproducibility matters.

## 4. Lean-Loading Hygiene (compact rule, not a fragment)

This is a one-liner that belongs in the project memory's discipline section, not as a separate block:

```markdown
- Disable unused MCP servers, tools, skills, and plugins for the project. Move long rules out of CLAUDE.md / AGENTS.md and into skills loaded on demand. Hot memory is the always-loaded prefix — every line costs cache budget.
```

## What Not To Put In Project Memory

These belong in `settings.json` / `~/.codex/config.toml`, **not** AGENTS.md / CLAUDE.md:

- Environment variables (`CLAUDE_CODE_DISABLE_1M_CONTEXT`, `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`, `CLAUDE_CODE_SUBAGENT_MODEL`, Codex `model_reasoning_effort` defaults).
- Base URL / API key routing (OpenRouter, custom proxies).
- Concrete `model:` / `effort:` values for subagents — those live in subagent files (`.claude/agents/*.md`, `.codex/agents/*.toml`).

These belong in skills, not project memory:

- Multi-step playbooks ("how to triage a Sentry alert").
- Reusable workflows that fire on cadence.
- Tool-specific procedures with their own references and assets.

## Validation

After adding a fragment, check:

- The block prevents a *specific repeated mistake* — name it in a comment if non-obvious.
- If `AGENTS.md` is symlinked to `CLAUDE.md`, you used the **neutral** variant (or split with explicit `**Claude Code:**` / `**Codex:**` subheadings inside one block).
- Total file length stays under the instruction budget (~150–200 discrete rules; see `memory-discipline.md`).
- Nothing in the fragment duplicates information the agent can infer from the repo (`package.json`, file tree, README).
