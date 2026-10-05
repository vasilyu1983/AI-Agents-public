# Context Hygiene — Runtime Failure Modes And Strategies

## Table of Contents

- [Two complementary verb sets](#two-complementary-verb-sets)
- [Context failure modes (F1–F5)](#context-failure-modes-f1f5)
- [Context rot](#context-rot)
- [Context mutation economics](#context-mutation-economics)
- [Compaction verification](#compaction-verification)
- [Mode collapse](#mode-collapse)
- [Tool-result pressure](#tool-result-pressure)
- [Sub-agent isolation recipe (P11)](#sub-agent-isolation-recipe-p11)
- [Just-in-time vs upfront context](#just-in-time-vs-upfront-context)
- [Assembly-layer hygiene checklist](#assembly-layer-hygiene-checklist)
- [Related references](#related-references)

**Purpose.** The skill's pattern catalog (`patterns-catalog.md`) covers *where knowledge lives*. This reference covers *what happens inside the context window at runtime*. Both axes must hold for a mature context layer.

Pair with `anti-patterns-catalog.md` for the A19–A26 entries these failures map to, and with `context-assembly.md` for the bundle-construction mechanics.

## Two complementary verb sets

The skill already names **storage-layer lifecycle verbs** — `remember / recall / forget / improve`. Context hygiene adds **assembly-layer runtime verbs**. The four verbs `write / select / compress / isolate` come from LangChain's context-engineering post (2025); this skill adds `order` and `format` because mature designs need both. Treat the six-verb set as the superset. (Breunig's 2025 posts are the source for the failure modes F1–F4 below, not for the verbs.)

| Verb | What it does | Where it lives in the skill |
|------|--------------|-----------------------------|
| **write** | Persist something outside the window (scratchpad, episode log, memory store) so the window can forget it | Feedback Layer, Memory Layer |
| **select** | Pull only what the current step needs from the layers below (just-in-time, not prompt stuffing) | Context Assembly Layer |
| **compress** | Summarize, truncate, or re-project to fit the budget without losing load-bearing detail | Context Assembly Layer §Context Compression |
| **isolate** | Give a bounded task its own context window (sub-agent) and return a compact summary | Pattern P11 |
| **order** | Place stable content first and volatile content last so identical inputs produce identical prompts and the KV cache stays warm | Context Assembly Layer §KV-cache-friendly layout |
| **format** | Project tool results, memories, and retrieval hits into the shape the model uses best — typed fields over raw blobs, summaries over dumps | Context Assembly Layer §Tool-result projection |

Storage verbs operate on the durable layer. Runtime verbs operate on the window. A design that nails storage but ignores runtime produces a well-organized knowledge store that still poisons the model on turn three.

**`order` in practice.** Position matters because attention is non-uniform across the window: middle-of-context content gets less attention than start or end ("lost in the middle"). The cheap, durable fix is a deterministic layout — tool definitions → system prompt → persistent memory block → retrieved evidence → conversation history → current turn — applied identically every turn. Identical prefixes also let the provider's prompt cache hit, cutting both latency and token cost. The ordering and cache-invalidation rules are owned by [ai-prompt-engineering → Cache-Aware Prompt Layout](../../ai-prompt-engineering/SKILL.md#cache-aware-prompt-layout).

**`format` in practice.** Models reason better over typed projections than raw payloads. A 5K-token JSON tool result becomes a 12-field summary keyed to what the agent will actually use. A retrieved doc becomes `{title, source, snippet, evidence_id}` rather than the full chunk. The format verb is what turns A18 (raw embeddings injected without reranking) and A24 (no tool-result compaction) into solved problems.

<!-- Source: https://www.langchain.com/blog/context-engineering-for-agents (LangChain, 2025; origin of write / select / compress / isolate) -->
<!-- Source: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (Anthropic, 2025-09) -->

## Context failure modes (F1–F5)

Long context windows do not produce better answers by themselves. F1–F4 are Drew Breunig's 2025 taxonomy of *how* long contexts degrade (poisoning, distraction, clash, confusion); F5 (proactive interference) comes from the memory-interference literature cited below. This F1–F5 list is the skill's one failure-mode checklist: every surface bundle is checked against all five before shipping. Context collapse of a stored playbook (A35) is a storage-side failure tracked in the anti-pattern sweep, not an F mode.

### F1 — Context Poisoning

- **Definition.** A hallucinated or wrong fact enters the context and is referenced on subsequent turns as if true, compounding the error.
- **Detection signals.** Multi-turn traces show the model citing a fact the source of truth does not contain. Agent "goals" sections acquire statements no user or tool ever provided. Memory confidence does not decay for unreinforced facts.
- **Mitigation.**
  - Validate extracted facts at `remember()` time against the operational layer (P1) before writing.
  - Treat long-horizon agent memory as an adversarial surface: every stored item carries `source_episode_id` (A13 blocked) and confidence (A14 blocked).
  - On contradiction, the ingest-time category (attribution / temporal / stale) determines the cleanup path, not a silent overwrite.
  - For long-running agents (P3), snapshot the core block periodically and diff against the operational layer to catch drift.
- **Maps to.** A19 context poisoning, A13 provenance, A14 confidence model.

### F2 — Context Distraction

- **Definition.** The context grows large enough that the model over-focuses on stored history and under-attends to its training-time knowledge or the current task.
- **Detection signals.** Repeated actions from history rather than novel synthesis. Pokemon-playing Gemini agent observation: >100K tokens of history caused repetition over planning. For tool-using agents, repeated tool calls that neither succeed nor advance the task.
- **Mitigation.**
  - Cap per-surface token budgets explicitly (see `context-assembly.md` §Token Budget Management).
  - Compact conversation history above a threshold: keep the last N turns verbatim, summarize the rest. Preserve episode IDs in the summary so provenance survives.
  - For long-horizon tasks, **isolate** into a sub-agent (P11) rather than letting the parent window grow indefinitely.
  - Periodically reset the agent to a known-good base and replay only the minimal working state.
- **Maps to.** A20 context distraction, P11 sub-agent isolation.

### F3 — Context Clash

- **Definition.** Information or tool descriptions in the context disagree — e.g., two memories giving different values for the same fact, a tool whose description contradicts the system prompt, an MCP server with instructions that collide with the app's guardrails.
- **Detection signals.** Model oscillates between behaviors on similar inputs. Responses blend two contradictory sources without flagging the clash. New MCP tool integrations cause regressions in unrelated tasks.
- **Mitigation.**
  - Ingest-time contradiction detection (A4 blocked) with categories attribution / temporal / stale.
  - Tool allowlists per surface — never let every tool be available on every surface. A tool that is never needed on a given surface is a clash risk, not a capability win.
  - For MCP: vet tool descriptions on registration, re-vet on version bump, and route untrusted MCP servers through a namespace with its own prompt-injection perimeter.
  - Order context deterministically so identical inputs produce identical prompts (KV-cache-friendly layout, below).
- **Maps to.** A21 context clash, A4 query-time contradiction detection.

### F4 — Context Confusion

- **Definition.** Too many tools or too many irrelevant facts crowd the bundle. The model picks the wrong tool, cites the wrong fact, or fails to act because nothing in context is clearly relevant.
- **Detection signals.** Small-model benchmarks show failure past ~30 tools (Llama-3.1-8B fails at 46 tools, succeeds at 19). Similar failures appear in larger models with irrelevant facts stuffed into memory slices.
- **Mitigation.**
  - Select only what the current step needs. Just-in-time retrieval over prompt-stuffing (A5 blocked).
  - Per-surface tool allowlists tuned to the surface's actual jobs. The dashboard surface does not need the "send email" tool.
  - Retrieval rerankers before injection, not after (A18 blocked).
  - Memory slices filtered by `memory_type` + recency, not by "give me everything for this user."
- **Maps to.** A22 context confusion, A5 prompt stuffing, A18 raw embeddings.

### F5 — Proactive Interference

- **Definition.** Accumulating semantically-similar key/value pairs in the memory store suppress recall of the *current* value. Each prior association for a slot (e.g., past values of "user's city" or "current project name") competes at retrieval time, degrading accuracy for the now-correct entry.
- **Detection signals.** Retrieval accuracy on recently-updated facts degrades as session count grows even though context-window size is unchanged. The model answers with a stale value it has no in-window reason to prefer. Prompt-engineering mitigations (e.g., explicit "use the most recent" instructions) reduce but do not eliminate the effect.
- **Key finding.** Degradation follows a roughly log-linear trajectory as stale associations accumulate; the authors locate the bottleneck beyond mere context access, and prompt-level workarounds reduce but do not remove it (arXiv 2506.08184, "Unable to Forget", June 2025, grade C preprint; corroborated as the motivating problem in SleepGate arXiv 2603.14517).
- **Mitigation.**
  - Use version-tagged or namespaced KV slots for any fact that updates over time — each new value supersedes the prior slot rather than adding a sibling entry.
  - Tie to the operational-truth separation pattern (P1): mutable facts belong behind tools or SQL, not as repeated memory rows with the same semantic key.
  - Apply P14 sleep-time consolidation to prune stale associations; the consolidation job should tombstone prior-version rows rather than coexisting with them.
- **Maps to.** A19 context poisoning (stale-value variant), A31 sleep-time pollution, P1 operational truth, P14 sleep-time consolidation.

<!-- Source: arXiv 2506.08184 "Unable to Forget" (June 2025, preprint, grade C) -->

<!-- Source: https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html (Breunig, 2025-06) -->
<!-- Source: https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html (Breunig, 2025-06) -->

Thank you to arXiv for use of its open access interoperability.

## Context rot

Beyond F1–F5, there is a continuous degradation pattern:

- **What it is.** As the number of tokens in the window grows, attention quality decreases because every token attends to every other token (n² relationship). The model's attention budget is finite; long contexts dilute it.
- **Practical effect.** Instruction-following degrades first, factual recall degrades next, multi-step reasoning last.
- **Threshold is model-specific — measure it.** Where rot becomes noticeable depends on the model and the task, and it sits well below the advertised window. Measure it for the production model with the `context_rot` suite (`builds/evals/suites/context_rot/`) and set the compaction trigger below the measured knee. Treat that zone as where compaction, subagent dispatch, or a fresh session should already have fired — not where you start considering them. Consequence for system design: the model is at its least intelligent point *exactly when* auto-compaction must run, which is why steered/proactive compaction (hinting at the next task) produces better summaries than unsteered auto-compaction.
- **Defenses.**
  1. **KV-cache-friendly layout.** Put stable content first and volatile content last; the ordering and invalidation rules live in [ai-prompt-engineering → Cache-Aware Prompt Layout](../../ai-prompt-engineering/SKILL.md#cache-aware-prompt-layout).
  2. **Compaction triggers.** Set a hard threshold (e.g., 80% of budget) at which conversation history is summarized. Keep the summary below a ceiling and keep the last few turns verbatim. Decide *when* with [Context mutation economics](#context-mutation-economics) and verify the result with [Compaction verification](#compaction-verification).
  3. **Just-in-time selection.** Do not load memory, retrieval, or graph traversal into the prompt unless the current step needs it. Progressive disclosure (`context-assembly.md` §Context Compression).
  4. **Sub-agent isolation (P11).** For any sub-task that would double the parent's context, spawn a sub-agent instead.

<!-- Source: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (Anthropic, 2025-09) -->

## Context mutation economics

Clearing tool results, compacting history, or editing any earlier block changes the prompt prefix. Every token after the edit point must be written to the provider cache again at the cache-write price instead of being read at the cache-read price. The saving is that the cleared tokens are no longer read on each remaining turn.

**Rule.** Clear or compact mid-session only when

```text
cleared_tokens × read_price × remaining_turns  >  rewritten_suffix_tokens × (write_price − read_price)
```

Otherwise keep the tokens and mutate at the next task boundary, where the suffix is short or the cache is being rebuilt anyway. Prices here are symbolic multiples of the base input price P; look up the real read and write multipliers for the production model before using the rule.

**Worked example** (read = 0.1P, write = 1.25P). Clearing 40k tokens that sit before a 60k-token suffix:

- One-time rewrite premium: 60,000 × (1.25 − 0.1) P = 69,000 P.
- Saving per remaining turn: 40,000 × 0.1 P = 4,000 P.
- Break-even: 69,000 / 4,000 = **17.25 remaining turns**.
- With 10 turns left, clearing saves 40,000 P and costs 69,000 P, so keep. With 20 turns left, it saves 80,000 P against 69,000 P, so clear.

**Edge cases.**
- If the cache will expire before the next turn anyway (idle gap longer than the TTL), the rewrite happens regardless, so the premium is zero and clearing wins.
- The rule prices only tokens. Clear sooner when the tokens themselves cause harm (F1–F5, context rot), and record that reason.
- Mutating near the end of the prefix is cheap because the rewritten suffix is small; prefer appending corrections over editing early blocks.
- Some providers tie replayed reasoning (thinking) blocks to an unedited conversation: editing the system prompt, tools or earlier messages can invalidate them or make the request fail. Check the provider's docs before editing mid-conversation on a reasoning model; appending stays safe.

## Compaction verification

Summaries silently drop low-salience constraints, which is the F1 poisoning and F5 interference path. Verify every compaction; do not trust it.

1. **Pin a must-survive set before summarizing:** open tasks and todo IDs, user-stated constraints, entity IDs, and decisions with their provenance IDs (episode, message, or decision IDs).
2. **Compact**, carrying durable IDs in each summary line (P20 anchored summarization).
3. **Run a recall probe** against the compacted context: one question per pinned item ("What constraint did the user set on X?", "Which decision superseded D-12, and why?"). Match answers against the pinned value, not against a model judgment.
4. **Fail the compaction if any pinned item is lost.** Keep the pre-compaction transcript, retry with the missing items passed as explicit keep-instructions, or fall back to keeping the last N turns verbatim. Log the lost item and the probe result.

## Mode collapse

Context rot's quieter sibling. Where context rot degrades the *substrate* (attention quality drops as tokens grow), mode collapse degrades the *output distribution* (the model produces increasingly narrow, repetitive, or stylistically homogeneous responses).

- **What it is.** Output diversity collapses across turns or across sessions. The model converges on one phrasing, one structure, or one recommendation regardless of input nuance. Often a downstream effect of alignment training, but the context layer can amplify or mask it.
- **Why the context layer matters.** A poorly designed memory layer that re-injects the model's own prior outputs as "facts" creates a feedback loop: the model's patterns become the user's "preferences" become the model's next prompt. Within a session this looks like F1 (poisoning); across sessions it looks like the agent only ever saying the same thing.
- **Detection signals.**
  - Same-format response across structurally different inputs.
  - User corrections that get acknowledged then silently re-violated next turn.
  - Memory store accumulates near-duplicate "preferences" extracted from the model's own past suggestions.
  - Eval suite shows decreasing variance on open-ended prompts over time.
- **Mitigation.**
  - Distinguish *user-stated* preferences from *model-inferred* ones at storage time. Confidence (A14) and provenance (A13) make this trivial; without them, mode collapse is invisible.
  - Never extract "memories" from the assistant's own outputs unless the user explicitly confirmed them.
  - Decay unreinforced inferred preferences faster than user-stated ones.
  - Periodically sample and review the stored memory layer for self-similarity (an inspection-surface job — see `inspection-and-review-surfaces.md`).
- **Maps to.** A13 provenance, A14 confidence, A19 poisoning at session scope.

<!-- Source: https://blog.logrocket.com/llm-context-problem-strategies-2026/ (LogRocket, 2026) — names rot + collapse as the two 2026 challenges -->

## Tool-result pressure

Tool outputs are the most common driver of context bloat in agent loops:

- **Problem.** An agent calls a tool, gets a 5K-token result, acts on it, then keeps the full result in context for the next N turns even though it only needed one field.
- **Recipe (tool-result compaction).**
  1. After the agent acts on the tool result, replace the full result with a short model-written summary (or a structured projection of the fields that were actually used).
  2. Keep a pointer to the full result in the episode log so it can be re-fetched if needed.
  3. For streaming or high-volume tools (logs, search results), cap the result size at the tool boundary — do not let the tool return arbitrarily large payloads into the window.
  4. Tag tool results with their origin for injection defense (see `security-threat-model.md`) — never treat tool output as a trusted instruction source.
- **Maps to.** A24 no tool-result compaction, and the `write` runtime verb.

<!-- Source: https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools (Anthropic) -->

## Sub-agent isolation recipe (P11)

When to split:

- Sub-task is bounded and has a well-defined output (report, summary, search synthesis).
- Sub-task would need significant context (docs, tools, history) that the parent does not need after the sub-task returns.
- Parallelism is available — multiple searches, multiple file analyses.

Handoff contract:

- **Input to the sub-agent.** Minimal brief: task statement, acceptance criteria, tool allowlist, output schema, token budget.
- **Output from the sub-agent.** Compact summary that fits the parent's budget. Include citations or episode IDs so the parent can re-fetch detail if it needs to.
- **What does not cross the boundary.** The sub-agent's full conversation history, its scratch reasoning, its intermediate tool results. The parent sees only the returned summary.

Anti-pattern: using a sub-agent as a black box without a defined output schema. The returned summary becomes a new source of context clash (F3) or poisoning (F1) in the parent.

<!-- Source: Anthropic multi-agent research architecture, 90.2% over single-agent Opus 4 on Anthropic's internal research eval (Opus 4 lead + Sonnet 4 subagents), at ~15x chat tokens. -->

## Just-in-time vs upfront context

Two approaches to giving the model what it needs:

- **Upfront (prompt-stuffing).** Load everything at turn start. Simple to implement; poisons quickly as the app grows. A5 anti-pattern.
- **Just-in-time.** Start with a lean bundle; let the model request more via tools (search, memory lookup, graph traversal) when the current step needs it. Requires tool discipline and good retrieval latency but scales to long-horizon tasks.

The default is just-in-time for anything that is not always relevant. Guardrails, actor identity, and the current task stay upfront; memory, retrieval, and relationship context are fetched on demand.

## Assembly-layer hygiene checklist

Before shipping a per-surface bundle:

- [ ] Token budget set and enforced (hard cap, not a soft target).
- [ ] Content order is KV-cache-friendly (stable → volatile).
- [ ] Tools in the bundle are allowlisted for this surface.
- [ ] Memory slices filter by `memory_type` + recency + `owner_scope`.
- [ ] Retrieval results carry evidence IDs and are reranked before injection.
- [ ] Tool-result compaction runs between turns.
- [ ] Compaction threshold for conversation history defined and tested; mid-session clears pass the mutation-economics rule; every compaction passes the must-survive recall probe.
- [ ] All five failure modes (F1–F5) have a documented defense for this surface.
- [ ] Long-horizon sub-tasks use P11 sub-agents, not parent context.
- [ ] Provenance, confidence, and owner_scope survive the compression step.

Every item that fails lands the design in the "NOT BLOCKED" column of the anti-pattern sweep and requires a written justification.

## Related references

- `context-assembly.md` — bundle construction mechanics and token-budget policy
- `anti-patterns-catalog.md` — A19–A26 catalog entries for the failures above
- `patterns-catalog.md` — P11 sub-agent isolation
- `security-threat-model.md` — injection/poisoning threat model (context can be *adversarial* as well as bloated)
- `evals-and-operations.md` — observability spans for measuring hygiene in production
