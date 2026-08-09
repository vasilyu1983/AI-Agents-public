# Opus 4.7 → 4.8 Memory Migration

Guidance for refreshing `AGENTS.md` / `CLAUDE.md` after the Claude Opus 4.7 (2026-04-16) and Opus 4.8 (2026-05-28) releases. Scope: changes that affect durable project memory. Prompt-time behavior changes (response length, thinking control) live in `ai-prompt-engineering` and `claude-api`.

Primary sources: [Best practices for using Claude Opus 4.7 with Claude Code](https://claude.com/blog/best-practices-for-using-claude-opus-4-7-with-claude-code) (2026-04-16); [What's new in Claude Opus 4.8](https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-8) (2026-05-28).

> **Superseded generation, checked 2026-07-11**: Opus 4.7/4.8 is no longer Anthropic's newest line. [Claude Fable 5 / Mythos 5](https://www.anthropic.com/news/claude-fable-5-mythos-5) shipped 2026-06-09 (global availability from 2026-07-01 after a brief export-control pause) and [Claude Sonnet 5](https://www.anthropic.com/news/claude-sonnet-5) shipped 2026-06-30, both superseding the 4.x line as Claude Code defaults. The migration mechanics below still apply almost unchanged — confirmed against [Prompting Claude Sonnet 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5) and [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5): effort still defaults to `high` (Sonnet 5, same as Opus 4.8; do not assume `xhigh`), and adaptive thinking is still the only thinking mode on Fable 5/Mythos 5 — `budget_tokens` remains dead. The one net-new memory implication: Fable 5's large default context window makes it *more* tempting to let a session balloon by appending tool output and history directly into context. Do not treat a bigger context window as license to skip external memory/retrieval — the progressive-disclosure and exception-file discipline in this skill applies more, not less, at this scale. Re-verify effort defaults and thinking-mode behavior against current docs before applying this checklist to a Fable 5 or Sonnet 5 session, since defaults have changed at every generation so far.

## Opus 4.8 Delta (shipped 2026-05-28, model id `claude-opus-4-8`)

The 4.7 memory moves below still apply — 4.8 builds on 4.7 and inherits its constraints. What changed for memory authors:

- **Effort default is now `high`, not `xhigh`.** On Opus 4.8 the [effort parameter](https://platform.claude.com/docs/en/build-with-claude/effort) defaults to `high` on all surfaces, **including Claude Code**. Do not write a memory line claiming `xhigh` is the default. If a task is reasoning-bound, set effort explicitly (`/effort high` is now the baseline; raise to `xhigh`/`max` only for the hardest work) rather than encoding it as a standing rule.
- **Mid-conversation system messages soften the "lock the prefix" rule.** 4.8 accepts `role: "system"` messages after a user turn ([mid-conversation system messages](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages)), so updated instructions can be appended **without** restating the full prompt or busting earlier prompt-cache hits. The session-prefix discipline (SKILL.md Workflow §12) still holds for *model and MCP-toolset* switches, which remain full re-reads; but you no longer need to treat every instruction refresh as a cache-buster.
- **Better compaction recovery + long-context handling.** 4.8 stays on task across compactions with fewer derailments and supports the 1M context window by default. Memory lines that existed only to re-anchor the agent after compaction (re-stating the goal, "remember you are working on X") are now mostly dead weight — delete them.
- **Better tool triggering.** 4.8 skips required tool calls less often than 4.7. Memory lines that nag the agent to "always run the tests" / "don't forget to use the linter" earn less; keep them only where the gate is genuinely non-obvious.
- **Lower prompt-cache minimum (1,024 tokens).** Smaller hot-memory files that were previously too short to cache now create cache entries — a mild argument *for* keeping `AGENTS.md` lean rather than padding it to hit a cache floor.
- **`budget_tokens` is still rejected (400 error).** Adaptive thinking remains the only thinking mode; the 4.7 advice to delete `budget_tokens` references is unchanged.

## What Changed on 2026-04-16

- **Tokenizer changed.** Token counts for the same prose differ from 4.6. Re-measure any line-of-sight token budgets that fed into memory-size decisions.
- **High reasoning effort is the default** in Claude Code (`xhigh` on 4.7; `high` on 4.8 — see the Opus 4.8 delta above). Either way, most memory instructions asking the agent to "think more" or "reason carefully" are redundant.
- **Adaptive thinking replaces `budget_tokens`.** The `budget_tokens` API parameter is no longer supported; the model decides its own thinking length. Delete any memory line that references or relies on `budget_tokens`.
- **Fewer subagents by default.** 4.7 is more conservative about spawning parallel workers. Workflows that previously worked implicitly now need explicit fan-out instructions.
- **Response length auto-calibrates.** Memory instructions like "be concise" or "keep responses short" now compete with 4.7's own calibration and usually lose.
- **Literal interpretation.** 4.7 takes instructions at face value. A sloppy `AGENTS.md` line that 4.6 silently generalized may now produce exactly what you wrote, not what you meant.

## Memory-Shaped Edits

These are the migration moves that belong in `AGENTS.md` / `CLAUDE.md`. Prompt-only moves are out of scope.

1. **Split strategic context from per-task intent.** Keep durable strategy in memory; write intent each turn. See SKILL.md §"Intent-First Memory".
2. **Delete progress scaffolding.** Lines like "summarize every 3 tool calls" or "announce your plan, then execute" no longer change behavior.
3. **Flip "Don't" lists to positive examples.** Replace negative rules with a short voice-of-good sample — "Like this: …" beats "Never do …".
4. **State fan-out explicitly.** If a workflow depends on parallel subagents, say so. 4.7 will not infer it.
5. **Delete `budget_tokens` references.** The parameter is gone; any memory line invoking it is dead weight or worse.
6. **Drop "be concise" / "keep it short".** Let 4.7 calibrate length.
7. **Tighten literal wording.** Re-read each rule and ask: *if the agent did exactly what this sentence says, would that be correct?* Rewrite ambiguous imperatives as success criteria.
8. **Re-measure budget.** After tokenizer change, your 150–200 instruction budget counts in tokens, not lines — recount if you were close to the ceiling.
9. **Cite the upgrade.** If you keep a rule that compensates for a pre-4.7 quirk, note the date and source so a future refresh can retire it.
10. **Regression-test before editing.** Run your top 3–5 prompts against the new model before touching memory. Often memory needs no change; you just learn which lines now do nothing.

## `budget_tokens` → Adaptive Thinking

Before (4.6):

```json
{ "thinking": { "type": "enabled", "budget_tokens": 8000 } }
```

After (4.7 and later): omit `budget_tokens` (it returns a 400 error on 4.7/4.8). The model sizes its own thinking via adaptive thinking. Claude Code defaults to a high reasoning effort (`xhigh` on 4.7, `high` on 4.8) — no memory line is needed to request it.

## Upgrade Checklist

Before keeping a line in memory after the 4.7 upgrade, ask:

- Is this still a **non-obvious mistake prevention**, or was it compensating for 4.6 guessing?
- Would a literal reading of this line produce the right behavior?
- If I deleted this line and re-ran my top prompt, would the output actually change?
- Does this rule describe **what good looks like** (keep) or **how to behave in a process** (consider deleting)?

If you cannot say yes to the first two or point to a concrete behavior change for the third, delete it.

## Related

- SKILL.md §"Intent-First Memory" — the split between strategic context and per-task intent.
- [../data/sources.json](../data/sources.json) — primary and secondary sources for this migration.
- `ai-prompt-engineering` / `claude-api` skills — prompt-time controls (thinking, caching, length).
