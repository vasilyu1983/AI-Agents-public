# Native Deep-Research Agents

Reference for the major native deep-research agents. These are dedicated products or modes where the model autonomously plans queries, browses sources, and synthesizes a report — as opposed to a custom agentic pipeline you build yourself. Last updated: 2026-07-11.

**Fact-check requirement**: verify current feature availability, context windows, pricing, and output limits against official provider docs before recommending for production use. Capabilities in this space change monthly. **Check two pages, not one**: a provider's feature guide (e.g. "how to use deep research") and its deprecations/sunset page are maintained independently and can disagree — see the OpenAI entry below for a live example where the guide still recommended a model days before its documented shutdown.

**RL-training note**: as of 2026, the leading research agents (OpenAI Deep Research, Gemini Deep Research, Perplexity Deep Research) are increasingly post-trained with reinforcement learning on tool-use and search trajectories, optimizing for multi-step planning, source selection, and synthesis quality rather than single-pass generation. This RL post-training is described generically by all three vendors; specific method names (e.g., named RL algorithms or dataset names) have not been publicly disclosed as of May 2026 — verify at each vendor's research blog before citing a specific method.

## Table of Contents

- [Comparison Table](#comparison-table)
- [ChatGPT Deep Research (OpenAI)](#chatgpt-deep-research-openai)
- [Gemini Deep Research (Google DeepMind)](#gemini-deep-research-google-deepmind)
- [Perplexity Deep Research](#perplexity-deep-research)
- [xAI Grok DeepSearch](#xai-grok-deepsearch)
- [Claude with Web Search (Anthropic)](#claude-with-web-search-anthropic)
- [Long-Horizon Memory: Anthropic Memory Tool](#long-horizon-memory-anthropic-memory-tool)
- [Selection Criteria Summary](#selection-criteria-summary)
- [URL-Health and Citation-Verification Recipe](#url-health-and-citation-verification-recipe)
- [S2S / Session-State Trap (Agentic Research Loops)](#s2s--session-state-trap-agentic-research-loops)

---

## Comparison Table

| Dimension | ChatGPT Deep Research (OpenAI) | Gemini Deep Research (Google) | Perplexity Deep Research | Claude with Web Search (Anthropic) |
|-----------|-------------------------------|------------------------------|-------------------------|-------------------------------------|
| **API surface** | Responses API; model IDs: `o3-deep-research` (depth) / `o4-mini-deep-research` (speed/cost) — **sunset 2026-07-23, replacement `gpt-5.5-pro`** [verified: developers.openai.com/api/docs/deprecations, 2026-07-11; the parallel guide at developers.openai.com/api/docs/guides/deep-research still recommended these model IDs as current on the same date — guide and deprecations page disagree, trust the deprecations page] | Interactions API (`POST /v1beta/interactions`); model IDs: `deep-research-preview-04-2026` / `deep-research-max-preview-04-2026` [verified: ai.google.dev, 2026-07-11] | Chat completions API; model ID: `sonar-deep-research` [verified: docs.perplexity.ai/api-reference/chat-completions-post] | Messages API; tool type: `web_search_20260318` (adds response-inclusion control) / `web_search_20260209` (dynamic filtering) / `web_search_20250305` (basic) — all GA, no beta header [verified: platform.claude.com/docs/en/docs/agents-and-tools/tool-use/web-search-tool, 2026-07-11] |
| **Search-grounding mechanism** | Autonomous multi-step web search; exact index and ranking undisclosed | Google Search + URL Context tool by default; MCP servers and File Search also supported | Iterative query refinement over real-time web index | Explicit tool calls; Claude decides when to search; dynamic filtering (code execution) post-processes results to reduce noise |
| **Citation fidelity** | Inline citations in report; citations can point to pages that no longer contain the cited text — P9 hostile-source detection required | Inline citations in structured report; some citations may link to Google search result pages rather than direct sources | Paragraph-level inline citations; citation laundering risk on SEO-heavy topics (P9 required) | Sentence-level citations with `cited_text` (up to 150 chars); `url` and `title` per citation; full tool-call trace auditable |
| **Long-horizon memory** | No persistent cross-session memory; each report is self-contained | No persistent cross-session memory | No persistent cross-session memory | Via the Anthropic **memory tool** (`memory_20250818`): a client-side tool writing to a client-controlled persistent directory (path application-defined; `/memories` by convention). Cross-session persistence is app-implemented, not a turnkey platform feature. (See below.) |

---

## ChatGPT Deep Research (OpenAI)

> **Sunset notice (verify before building anything new)**: OpenAI's deprecations page [`developers.openai.com/api/docs/deprecations`, verified 2026-07-11] lists `o3-deep-research` (snapshot `o3-deep-research-2025-06-26`) and `o4-mini-deep-research` (snapshot `o4-mini-deep-research-2025-06-26`) as shut down **2026-07-23**, with `gpt-5.5-pro` as the recommended replacement — announced 2026-04-22. As of the same date, the feature guide at `developers.openai.com/api/docs/guides/deep-research` still described these model IDs as the current, recommended way to call Deep Research via the Responses API, with no visible deprecation banner. **Do not trust the feature guide alone** — check the deprecations page directly, and re-verify the replacement model's deep-research capability (tool access, source count, report structure) before porting a pipeline, since `gpt-5.5-pro` is a general reasoning model, not a purpose-built deep-research variant like its predecessors.

**Product status**: available in ChatGPT Pro, Team, Enterprise, and Education plans. Also accessible via the Responses API (model IDs above, until sunset).

**o3 vs o4-mini tradeoff**: use `o3-deep-research` when synthesis depth and source diversity are critical; use `o4-mini-deep-research` when turnaround time and cost matter and the research question is moderately scoped. Both are optimized for browsing and data analysis (RL-post-trained on search trajectories).

**How it works**: OpenAI's Deep Research mode launches an autonomous research agent that plans a sequence of web searches, browses and reads source pages, and produces a long-form structured report with inline citations. The planning and searching phases can take 5–30 minutes for complex questions. Web search is always on for these models and cannot be disabled — a single query typically triggers 10–30 searches. The agent is RL-post-trained for multi-step tool use; specific training methods are not publicly disclosed.

**Pricing** (approximate — verify at OpenAI's current pricing page before budgeting): token pricing is roughly $10/M input and $40/M output tokens on `o3-deep-research`. Per-query cost is commonly cited around $1.50–$8.00 for `o3-deep-research` and $0.40–$2.50 for `o4-mini-deep-research`, but independent benchmarking (Artificial Analysis, mid-2026) reported real-world averages running well above the low end of that range on complex multi-source queries — treat published per-query figures as a floor, not a ceiling, and pilot on representative queries before committing to a budget. The Batch API cuts these costs roughly in half.

**MCP connector (Feb 10, 2026)**: ChatGPT Deep Research gained MCP connector support and trusted-domain restriction in the ChatGPT product (UI, not API). Enables connecting to internal tools and data sources during research; trusted-domain restriction improves auditability by limiting browsing to approved domains. Verify current MCP connector availability at `help.openai.com` before relying on it in production workflows.

**Strengths**:
- Strongest source diversity of the five agents — actively follows multiple parallel query branches.
- Long synthesis reports with section headers, sub-questions, and inline citations.
- Relatively strong multi-step reasoning; handles conflicting sources by flagging disagreements.
- Can be prompted to restrict sources to specific domains or date ranges.

**Limitations**:
- Model IDs on an announced sunset path (see notice above) — confirm current model availability before any new integration work.
- Opaque search log — you cannot inspect the exact URLs browsed or query sequence used.
- Hallucination risk on niche topics; citations can point to pages that no longer contain the cited text (apply URL-health recipe below).
- Non-deterministic — repeating the same question produces a different report.
- Slow for time-sensitive tasks (5–30 min per report).
- No direct API control over source selection strategy.
- Cost is convex in query complexity — vague or multi-part questions can spike spend well past the advertised per-query range.

**When to choose**: open-ended competitive surveys, technical background research, market overviews where speed is not critical and some opacity in the search path is acceptable.

**When to avoid**: auditable deliverables, regulated outputs, source-controlled research, tasks with a hard per-query cost ceiling, or when you need repeatable results.

---

## Gemini Deep Research (Google DeepMind)

**Product status (May 2026)**: available in Gemini Advanced (Google One AI Premium) and some Workspace tiers. Also accessible via the Gemini API (Interactions API, preview status) with pay-as-you-go pricing.

**API model IDs** [verified: `ai.google.dev/gemini-api/docs/deep-research`, fetched 2026-05-17]:
- `deep-research-preview-04-2026` — speed-optimized
- `deep-research-max-preview-04-2026` — maximum comprehensiveness

**API endpoint**: `POST https://generativelanguage.googleapis.com/v1beta/interactions`

**Typical resource use**: ~80–160 search queries per task; 250k–900k input tokens (50–70% cached); 60k–80k output tokens; max research duration 60 minutes.

**How it works**: Gemini presents a structured research plan to the user before executing (`agent_config: collaborative_planning`), which can be revised before the search phase begins. It then uses Google Search and the URL Context tool to browse sources and produces a long-form report. Supports async execution (`background=true`) and streaming.

**Strengths**:
- Explicit plan step before execution — user can review and revise the query strategy.
- Strong structured report format (clear headers, numbered sections).
- Deep Google index access for current news, filings, and product documentation.
- Interruptible at the plan step — closer to a supervised workflow than a fire-and-forget mode.
- MCP server support and multimodal inputs (images, PDFs).

**Limitations**:
- Synthesis depth typically thinner than ChatGPT Deep Research on complex multi-faceted questions.
- Citation quality varies; some citations link to Google search result pages rather than direct sources.
- Preview status — model IDs include date suffix and will change; verify before production use.

**When to choose**: structured report output, tasks where reviewing the query plan before execution is valuable, current news and regulatory research where Google index freshness matters.

**When to avoid**: deep technical synthesis requiring many source types, highly niche domains with sparse Google index coverage.

---

## Perplexity Deep Research

**Product status**: available in Perplexity Pro. Accessible via the Perplexity API (Chat Completions endpoint).

**API model ID** [verified: `docs.perplexity.ai/api-reference/chat-completions-post`, fetched 2026-05-17]: `sonar-deep-research`

**Cost note** [verified: `docs.perplexity.ai/guides/pricing`, 2026-07-11]: `sonar-deep-research` triggers 20–30+ searches per query. Pricing is multi-component and metered per token type: $2/M input tokens, $8/M output tokens, $2/M citation tokens, $3/M reasoning tokens, plus $5 per 1,000 search queries. **Whether there is an additional flat per-request fee on top of this is inconsistently reported across secondary sources as of this writing** — treat any specific per-1,000-request figure as unverified until you confirm it on the live pricing page for your account tier. Reasoning tokens dominate cost on complex questions: a documented medium-complexity example totaled roughly $1.19 (mostly reasoning-token cost), and typical full queries commonly range from $0.30 to $1.30+ depending on reasoning depth and search count — noticeably higher than simple sonar/sonar-pro calls. Verify current pricing at `docs.perplexity.ai/guides/pricing` before production budget planning.

Other Perplexity sonar API model IDs (same source): `sonar`, `sonar-pro`, `sonar-reasoning-pro`.

**How it works**: Perplexity Deep Research performs iterative query refinement before synthesizing. It typically completes in 2–5 minutes. It shows inline citations after each paragraph and links directly to the sources it used. The underlying model is RL-post-trained for search trajectories; specific training methods are not publicly disclosed.

**Strengths**:
- Fastest turnaround of the four agents for moderate-complexity questions.
- Inline citations shown at the paragraph level, making it easier to spot unsupported claims.
- Good at current events and fast-moving topics (strong real-time web index).
- API access available via chat completions — can be integrated into custom pipelines.

**Limitations**:
- Citation laundering risk on SEO-heavy topics — Perplexity's index includes many aggregator and AI-generated content sites; apply P9 hostile-source detection and URL-health recipe below.
- Shorter synthesis than ChatGPT DR for complex multi-part questions.
- Less strong at handling contradictory sources — tends to average rather than flag disagreements.
- No support for restricting sources to specific domains via the product UI (API allows more control).

**When to choose**: current event monitoring, competitive quick-scans, tasks where inline citations and speed are the priority.

**When to avoid**: high-stakes vendor comparisons (P9 hostile-source detection is harder to enforce), deep primary-source research, regulated outputs.

---

## xAI Grok DeepSearch

**Product status**: DeepSearch is available as a mode in the Grok product (grok.com) and — as of this update — as documented server-side tools in the xAI API [verified: `docs.x.ai/developers/tools/overview`, `docs.x.ai/developers/tools/web-search`, `docs.x.ai/developers/tools/x-search`, 2026-07-11]. This is a change from earlier status: xAI previously had no documented API path for DeepSearch-equivalent behavior.

**API surface**: `web_search` and `x_search` are server-side tools managed by xAI that execute automatically when enabled on a chat completion request (demonstrated with `grok-4.5` in the current docs — confirm current flagship model ID before use, xAI ships new Grok versions frequently). `x_search` additionally supports keyword search, semantic search, user search, and thread fetch over X/Twitter, with optional image/video understanding. Citations return automatically as source URLs when a tool is invoked. Pricing is metered by token usage plus a per-tool-invocation charge — check the current xAI pricing page for rates.

**What is still missing**: a dedicated report-generating deep-research *model* or endpoint with the autonomous multi-step planning and long-form synthesis of `o3-deep-research`, Gemini Deep Research, or `sonar-deep-research`. `web_search`/`x_search` are search tools you compose into your own agentic loop (P2), not a one-call deep-research product.

**Recommendation**: Grok's API is now a legitimate option for a custom pipeline (P1–P4) that needs X/Twitter as a first-class source alongside the open web — no other agent in this comparison indexes X natively. It is not yet a substitute for the one-call native deep-research products in this table.

**When to choose**: custom pipelines where X/Twitter discourse (breaking news, sentiment, crypto, trend research) is a required source; ad-hoc product-UI research on grok.com.

**When to avoid**: workflows expecting a single-call, fully autonomous long-form research report — build that yourself with P2 + P4 on top of these tools, or use one of the four dedicated deep-research products above.

---

## Claude with Web Search (Anthropic)

**Product status**: web search is available via the Anthropic Messages API (GA — no beta header required). There is no dedicated "Deep Research" mode — deep-research behavior requires explicit prompting and a P2 plan-then-execute loop.

**API tool versions** [verified: `platform.claude.com/docs/en/docs/agents-and-tools/tool-use/web-search-tool`, fetched 2026-07-11]:
- `web_search_20260318` — current version; adds **response-inclusion control** (`response_inclusion: "excluded"` drops raw search-result blocks already consumed by code execution from the response, cutting output-token cost on agentic workflows that don't need to echo raw search content back to the client).
- `web_search_20260209` — adds **dynamic filtering** (Claude writes and executes code to post-process search results before they enter context, reducing noise and token consumption). Still available; superseded by `20260318` for new integrations.
- `web_search_20250305` — basic web search, no dynamic filtering or response-inclusion control. Still available.

**Dynamic filtering model support**: Claude Fable 5, Claude Opus 4.8, Claude Mythos 5, Claude Mythos Preview, Claude Opus 4.7, Claude Opus 4.6, Claude Sonnet 5, Claude Sonnet 4.6. Requires code execution tool access (provisioned automatically when dynamic filtering runs). Note the current Claude model tier: **Mythos-class** (Fable 5, Mythos 5, Mythos Preview) now sits above Opus-class in capability — Fable 5 and Mythos 5 reached general availability 2026-06-09, were briefly restricted to US-persons-only under export controls (2026-06-12 to 2026-06-30), and are now globally available again. Claude Sonnet 5 (GA 2026-06-30) replaces Sonnet 4.6 as the default free/pro model and is the current recommended default for cost-sensitive research pipelines that don't need Mythos-class reasoning depth.

**Citation format**: each cited sentence includes `url`, `title`, and `cited_text` (up to 150 characters). Citation fields do not count toward token usage.

**Pricing**: $10 per 1,000 web searches, plus standard token costs for search-generated content.

**How it works**: Claude treats web search as a tool call within a normal conversation or agent session. The search steps, URLs browsed, and intermediate reasoning are visible in the conversation trace. With dynamic filtering, Claude post-processes query results via code execution before reasoning, improving accuracy on technical documentation, literature review, and citation verification tasks.

**Strengths**:
- Full tool-call trace — every search query and URL is visible and auditable.
- Best at structured output shapes (JSON, YAML, typed contracts) because the user controls the synthesis format.
- Strongest at following explicit research plans (P2) — responds well to structured system prompts with stop criteria and evidence tiers.
- Can be combined with the verifier subagent pattern (P4) by running a second Claude call on the ledger.
- Dynamic filtering (with `web_search_20260209` + code execution) materially reduces irrelevant content in context for technical research.
- Long-horizon multi-session memory via the Anthropic memory tool (see below).

**Limitations**:
- No dedicated deep-research mode — comparable depth to ChatGPT Deep Research requires explicit multi-turn prompting with a plan.
- Slower and more expensive than the other agents for the same depth of research when done through the API.
- Web search tool availability may vary by region and plan; dynamic filtering requires code execution tool to be enabled.

**When to choose**: auditable research pipelines, custom agentic workflows where you need source control and structured output, integration into Claude Code or production systems, long-horizon multi-session research (with app-implemented persistent memory via the Anthropic memory tool).

**When to avoid**: ad-hoc open-ended research where you want a single-click report.

---

## Long-Horizon Memory: Anthropic Memory Tool

For multi-session research tasks — literature reviews spanning days, regulatory monitoring, competitive intelligence updated weekly — session-state loss is the primary failure mode. The Anthropic **memory tool** (`memory_20250818`) addresses this at the application layer.

**How it works**: the memory tool is a **client-side tool** that reads and writes to a **client-controlled persistent directory** (conventionally named `/memories`, but the path is application-defined — not a platform-mandated mount). Cross-session persistence is implemented by the application, not provided as a turnkey platform guarantee. Confirmed [`platform.claude.com/docs/en/docs/agents-and-tools/tool-use/memory-tool`, verified 2026-07-11]: the memory tool is **generally available on the Messages API with no beta header required**, and is available on all Claude 4 and later models. It supports just-in-time context retrieval (Claude reads memory files back on demand rather than front-loading them) and is eligible for Zero Data Retention where configured. It pairs with server-side compaction and client-side context editing for long-running agent sessions — see the canonical docs for the combined pattern.

> **Canonical docs**: `platform.claude.com/docs/en/docs/agents-and-tools/tool-use/memory-tool` is the current, confirmed doc tree as of 2026-07-11. `/mnt/memory/` is an unofficial community convention from earlier Claude Code harnesses, **not** the official Anthropic API shape.

> **"Dreaming" / "Auto Dream"**: an optional Claude Code and community memory-consolidation pattern — **not** a documented Anthropic platform capability. Do not rely on it as a platform guarantee.

**Application to research workflows**:

1. After each searcher iteration, append new ledger rows to your configured persistent directory (e.g. `<app-dir>/source-ledger.jsonl`).
2. Write the current `ResearchPlan` checkpoint to your persistent directory (e.g. `<app-dir>/research-plan.json`).
3. On session resume, reload from these files — do not reconstruct from conversation context.
4. If using Claude Code with community memory-consolidation hooks, offline note compression between sessions is possible — but treat this as an optional pattern, not a platform feature.

This replaces the S2S session-state persistence pattern (disk writes after each subagent) with a durable store that survives context resets. Path layout and persistence guarantee are determined by your application, not the Anthropic platform.

---

## Selection Criteria Summary

| Question | Recommendation |
|----------|----------------|
| Need the deepest synthesis, don't care about auditability | ChatGPT Deep Research (`o3-deep-research`) — **confirm it hasn't sunset; see notice above** |
| Need depth with lower cost | ChatGPT Deep Research (`o4-mini-deep-research`) — same sunset caveat |
| Want to see and approve the query plan before execution | Gemini Deep Research |
| Need fast results with inline citations for current events | Perplexity Deep Research (`sonar-deep-research`) — note multi-component pricing |
| Need auditable traces, structured output, or API integration | Claude with web search (`web_search_20260318`, GA) |
| Need long-horizon multi-session research memory | Claude with the Anthropic memory tool (`memory_20250818`; GA, client-controlled persistent directory, path app-defined; cross-session persistence is app-implemented) |
| Need X/Twitter-indexed content via a documented API | Grok DeepSearch (`web_search` / `x_search` tools, `docs.x.ai`) — compose your own loop; no one-call report mode |
| Need repeatable, source-controlled research | None — use a custom pipeline (P2 + P4 + P1) |
| Output will be cited in a product, report, or regulatory filing | None — use a custom pipeline |

---

## URL-Health and Citation-Verification Recipe

Research output — from any native agent — must not silently carry dead, redirected, or content-mismatched URLs into the final synthesis. Apply this recipe before finalizing any research artifact.

**Step 1 — Collect all cited URLs from the synthesis and ledger.**
Extract every URL referenced in the draft synthesis and in the `SourceLedger`. Deduplicate.

**Step 2 — Dereference each URL.**
For each URL:
- Issue an HTTP HEAD request (fall back to GET if HEAD returns 405).
- Record: final URL after redirects, HTTP status code, redirect chain length.

**Step 3 — Flag by status.**
- `200` and final URL matches ledger URL → PASS.
- `200` but final URL differs from ledger URL (redirect) → FLAG as `url_redirected`; update ledger entry with final URL; re-verify content match.
- `404`, `410`, `5xx`, or timeout → FLAG as `url_dead`; mark ledger entry `confidence: none`; do not include in synthesis without explicit `[DEAD LINK]` annotation.
- `403` / `401` → FLAG as `url_gated`; note that content could not be verified; downgrade to secondary evidence tier.

**Step 4 — Content match check.**
For PASS and redirected URLs, fetch a snippet and verify the `supporting_quote` from the ledger entry still appears on the current page. If the quote is absent: FLAG as `content_changed`; downgrade entry to `confidence: low`.

**Step 5 — Quarantine or annotate.**
- Dead / gated links: remove from synthesis or annotate `[UNVERIFIED — source unavailable as of {date}]`.
- Redirected links: update ledger URL field; re-run content match.
- Changed-content links: re-read the current page; decide if the claim is still supported.

**Step 6 — Automation.**
Use `scripts/citation_verifier.py --input claims.jsonl` for batch verification. The script checks JSONL of `{claim, source_url, supporting_quote}` and reports status per claim. For URL-health specifically, integrate HTTP status checking before the supporting-quote step.

**Trigger**: run this recipe after the verifier subagent (P4) pass and before emitting the final `SynthesisArtifact`.

---

## S2S / Session-State Trap (Agentic Research Loops)

When using Claude with web search in a multi-turn agentic loop, session-state loss on model switch or context reset causes the agent to lose its search position.

**Without the memory tool**: persist the `ResearchPlan` and `SourceLedger` to disk after each iteration; resume the loop by reloading from disk, not from conversation context.

**With the Anthropic memory tool**: write to your configured persistent directory using the `memory_20250818` client-side tool — the directory survives context resets because it is application-managed storage, not session memory. Offline note consolidation ("Dreaming") is an optional Claude Code / community pattern, not a documented platform guarantee.

See P1 (source-ledger-as-contract) and the Known Traps table in SKILL.md.
