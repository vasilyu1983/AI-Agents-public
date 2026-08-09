# Memory Discipline

## Table of Contents

- [Intent-First Memory (Opus 4.7+)](#intent-first-memory-opus-47)
- [Exception-File Test](#exception-file-test)
- [Instruction Budget](#instruction-budget)
- [Measuring Whether Memory Is Working](#measuring-whether-memory-is-working)
- [Feedback Loops](#feedback-loops)

## Intent-First Memory (Opus 4.7+)

Opus 4.7 (shipped 2026-04-16) takes instructions literally and no longer silently generalizes. This raises the payoff of clear intent in durable memory and lowers the payoff of "how to behave" prose.

Split what goes into CLAUDE.md / AGENTS.md along two axes:

| Layer | Lives in | Example |
|-------|----------|---------|
| Strategic context (durable) | CLAUDE.md / AGENTS.md | What we're building, who it's for, what good looks like, what's off-limits, exact commands |
| Per-task intent (variable) | Each prompt turn | "Refactor getUser to use the new DI container; keep behavior identical" |

You still write per-task intent every turn. The win from memory is that you stop retyping the strategic context on top of it. If a line would appear in >80% of per-task prompts, lift it into memory.

Write intent as success criteria, not imperative steps. Declarative goals let 4.7 loop toward them; imperative micromanagement burns turns and costs tokens.

See [opus-4-7-memory-migration.md](opus-4-7-memory-migration.md) for the full migration checklist (tokenizer change, adaptive thinking, fan-out defaults, `budget_tokens` break).

## Exception-File Test

Before adding a new line to `AGENTS.md` or `CLAUDE.md`, ask:

1. Is this fact hard to infer from the repo?
2. Does it matter on most sessions rather than only occasionally?
3. Would the agent make the same mistake again without it?

If the answer is not "yes" to all three, the content usually belongs somewhere else:

- docs for broad explanation
- searchable notes for history
- skills for repeatable procedures
- tool config for runtime behavior

## Instruction Budget

Memory file size matters beyond token cost. Research across 2,500+ repositories shows that agent compliance drops after approximately 150–200 discrete instructions. Every line in always-loaded memory consumes instruction budget — not just context tokens.

Implications:

- Generic advice ("write clean code", "follow best practices") wastes instruction budget without creating behavior change.
- Rules already enforced by linters, formatters, or type systems do not belong in project memory.
- Each line should pass the exception-file test (hard to infer, needed most sessions, prevents repeated mistakes).
- Ruthless pruning matters more than comprehensive coverage.

## Measuring Whether Memory Is Working

Pruning is useful only if you can tell which lines earn their budget. Close any behavioral-rules file (e.g. `.claude/rules/coding-behavior.md` — canonical source at [`coding-behavior.md`](coding-behavior.md) — or a scoped section of `AGENTS.md`) with an explicit "working-if" line stating the observable signals that tell you the rules are paying for their token cost. Example:

> **These rules are working if:** fewer unnecessary changes appear in diffs, fewer rewrites happen because of overcomplication, and clarifying questions come *before* implementation rather than after mistakes.

Review the signal every few weeks. If the diff quality hasn't changed, the rule is cosmetic — delete it. If one signal has improved but another hasn't, the corresponding rule may need sharpening or replacement. Without a working-if line, the only way to discover a rule isn't working is to keep failing at the task it was meant to prevent. (Pattern refined from [forrestchang/andrej-karpathy-skills@fb8fdb0](https://github.com/forrestchang/andrej-karpathy-skills), MIT.)

## Feedback Loops

Explicit verification instructions are the single highest-impact practice for agent efficiency. Agents perform 2–3x better when they can verify their own work through tight feedback loops.

Add verification steps to `AGENTS.md` so the agent runs checks after changes rather than handing off unchecked work:

```markdown
## Verification

After code changes, run:
1. `npm test` — confirm no regressions
2. `npm run lint` — confirm style compliance
3. `npm run typecheck` — confirm type safety

After prompt or config edits, run:
1. `wc -c <edited-file>` — confirm within character cap
2. `rg "{{[^}]+}}" <edited-dir>` — confirm no unresolved placeholders
```

The pattern extends to UI work (Playwright MCP for visual verification), API work (curl or httpie for endpoint checks), and infrastructure (plan/apply dry runs).
