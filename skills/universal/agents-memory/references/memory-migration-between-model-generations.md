# Model-Upgrade Memory Migration

How to refresh `AGENTS.md` / `CLAUDE.md` when the team moves to a new model generation. This covers only changes to durable project memory. Prompt-time behavior (response length, thinking control, caching) belongs to `ai-prompt-engineering` and `claude-api`.

## Lookup Step First

Before editing memory, read the vendor's migration or prompting guide for the new model (for Claude: the "what's new" and prompting pages in the Claude platform docs; for Codex: the OpenAI model and Codex release notes). Extract answers to these questions. They drive which lines to delete or add:

| Question | Memory decision it feeds |
|----------|--------------------------|
| Did the default reasoning effort or thinking mode change? | Delete "think carefully" / "reason step by step" lines if the new default already covers them; never write the default itself into memory |
| Were any API parameters removed or renamed? | Delete memory lines and fragments that mention them |
| Does the model interpret instructions more literally than the last one? | Rewrite vague imperatives as success criteria (step 5 below) |
| Does it spawn subagents or call tools more or less readily? | Add or delete explicit fan-out and "always run X" lines |
| Does it calibrate response length or progress updates on its own? | Delete "be concise" and progress-scaffolding lines |
| Did the tokenizer change? | Recount token-based budgets that informed memory size |
| Does the vendor now recommend fewer, judgment-framed rules? | Collapse clusters of narrow prohibitions into one judgment statement |

Do not copy the answers into memory. They are facts about a model version, and they will be wrong after the next upgrade. Memory records the *behavior you want*, not the model's defaults.

## Memory-Shaped Edits

1. **Regression-test before editing.** Run your top 3–5 prompts against the new model before touching memory. Often memory needs no change; you just learn which lines now do nothing.
2. **Split strategic context from per-task intent.** Keep durable strategy in memory; write intent each turn. See [memory-discipline.md](memory-discipline.md).
3. **Delete compensations for old quirks.** A line that existed only to correct the previous model's habit (re-anchoring after compaction, nagging to run tools it now runs anyway, "be concise") is dead weight once the habit is gone. Delete it after the regression test confirms that.
4. **Flip "Don't" lists to positive examples.** Replace negative rules with a short sample of the good output: "Like this: …" beats "Never do …".
5. **Tighten literal wording.** Re-read each rule and ask: *if the agent did exactly what this sentence says, would that be correct?* Rewrite ambiguous imperatives as success criteria.
6. **State fan-out explicitly.** If a workflow depends on parallel subagents, say so; do not rely on a model's default appetite for spawning them.
7. **Re-check the budget.** Recount after the upgrade, especially if the tokenizer changed. The budget rule and its source live in [claude-md-instruction-budget.md](claude-md-instruction-budget.md).
8. **Mark compensating rules you keep.** If you keep a rule that works around a specific model's quirk, note the model and date next to it so a future refresh can retire it.

## Upgrade Checklist

Before keeping a line in memory after an upgrade, ask:

- Is this still a **non-obvious mistake prevention**, or was it compensating for the previous model's guessing?
- Would a literal reading of this line produce the right behavior?
- If I deleted this line and re-ran my top prompt, would the output actually change?
- Does this rule describe **what good looks like** (keep) or **how to behave in a process** (consider deleting)?

If you cannot say yes to the first two or point to a concrete behavior change for the third, delete it.

A larger context window is not a reason to skip external memory or retrieval. The progressive-disclosure and exception-file discipline in this skill matters more, not less, as sessions grow.

<details>
<summary>Old patterns</summary>

- **`budget_tokens` in thinking config.** Earlier Claude models took an explicit thinking-token budget; later generations replaced it with adaptive thinking and reject the parameter. Delete any memory line or fragment that sets or mentions it, and let the effort setting control depth.

</details>

## Related

- [memory-discipline.md](memory-discipline.md) — the split between strategic context and per-task intent.
- [../data/sources.json](../data/sources.json) — vendor sources for past migrations.
- `ai-prompt-engineering` / `claude-api` skills — prompt-time controls (thinking, caching, length).
