# Memory Discipline

## Table of Contents

- [Intent-First Memory](#intent-first-memory)
- [Exception-File Test](#exception-file-test)
- [Promoting Notes Into Instruction Files](#promoting-notes-into-instruction-files)
- [Instruction Budget](#instruction-budget)
- [Measuring Whether Memory Is Working](#measuring-whether-memory-is-working)
- [Feedback Loops](#feedback-loops)

## Intent-First Memory

Each recent model generation has taken instructions more literally and generalized less from vague wording. This raises the payoff of clear intent in durable memory and lowers the payoff of "how to behave" prose.

Split what goes into CLAUDE.md / AGENTS.md along two axes:

| Layer | Lives in | Example |
|-------|----------|---------|
| Strategic context (durable) | CLAUDE.md / AGENTS.md | What we're building, who it's for, what good looks like, what's off-limits, exact commands |
| Per-task intent (variable) | Each prompt turn | "Refactor getUser to use the new DI container; keep behavior identical" |

You still write per-task intent every turn. The win from memory is that you stop retyping the strategic context on top of it. If a line would appear in >80% of per-task prompts, lift it into memory.

Write intent as success criteria, not imperative steps. Declarative goals let the model loop toward them; imperative micromanagement burns turns and costs tokens.

See [memory-migration-between-model-generations.md](memory-migration-between-model-generations.md) for the model-upgrade migration checklist.

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

## Promoting Notes Into Instruction Files

Auto-memory (`MEMORY.md` and its topic files, Codex memories), agent-written notes, and learned lessons are machine-local and unreviewed. `AGENTS.md`, `CLAUDE.md`, and rules files are shared, always loaded, and paid for every session. Promotion moves a note across that line, so gate it.

Promote a note only when all five hold:

1. **Repeated.** The mistake recurred, or the note was needed, in more than one session or task.
2. **Verified.** It was re-checked against the current code, config, or docs: the command runs, the path exists. Being remembered is not verification.
3. **Stable.** It changes more slowly than the file is reviewed, so it holds no live state such as versions, counts, ticket status, or who is working on what.
4. **Scoped.** It applies to everyone working in that directory. Put it in the nearest scoped file (a nested `AGENTS.md` or a path-scoped rule), not the root.
5. **Non-standard.** It passes the exception-file test above: a practice the agent would not infer, never a repository overview. Context files are reported not to raise task success in general while adding inference cost, and overviews did not help (arXiv 2602.11988, abstract).

Keep it as a note when it is machine-specific (local paths, auth, tooling), personal preference, or in-flight project state. Delete it when it contradicts the current code (the code wins), when a doc, skill, or linter already covers it, or when it no longer re-verifies. A hard constraint becomes a hook or tool setting, not a line, because instruction files are context, not enforcement.

**Review.** The agent proposes the promotion as a diff; it never writes into a shared instruction file on its own. Whoever reviews instruction-file changes (CODEOWNERS, or the file's owner) approves it like code.

**Test.** Pick a held-out task the note should fix, one not used to write the note, and run it with and without the new line. Promote only if behaviour changes the intended way and a guard task the agent already passes still passes. Then give the section a working-if line (below). The baseline and guard-set method is in [ai-evals learned and procedural memory](../../ai-evals/references/retrieval-and-memory-eval.md#6-learned-and-procedural-memory).

After promoting, delete the source note or replace it with a pointer, so the fact keeps one home.

## Instruction Budget

Memory file size matters beyond token cost: adherence degrades as always-loaded instructions pile up, so every line consumes instruction budget, not just context tokens. The ceiling, its source, and how firmly to trust it are in [claude-md-instruction-budget.md](claude-md-instruction-budget.md) (the single owner of that figure).

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

Explicit verification instructions are among the highest-leverage lines in project memory: an agent that can check its own work through a tight feedback loop catches its own mistakes before handing off. (A "2–3x" gain is often quoted for this; no primary source for it is known — do not cite it as data.)

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
