# OpenAI Internal Practice (Codex)

Moved from the hub SKILL.md.

Source: [*How OpenAI uses Codex*](https://cdn.openai.com/pdf/6a2631dc-783e-479b-b1a4-af0cfbd38630/how-openai-uses-codex.pdf), 2025 — internal-usage report across Security, Product, Frontend, API, Infrastructure, and Performance Engineering teams. These patterns are validated by daily use inside OpenAI; cite this source rather than restating as your own observations.

### Optional two-stage Ask → Code flow

- **Use when:** the user requests a plan, unresolved architecture or scope choices need review, or the active runtime requires planning before execution. Ask/Code labels are runtime-specific; other runtimes can use the same decision boundary without those modes.
- **Otherwise:** for a clear, authorized change, inspect the relevant context, implement, inspect the result, and fix failures from affected checks before handoff. A multi-file edit alone does not require another approval step.
- **Completion:** finish the authorized workflow; pause only for a decision or action outside its authority. Respect an explicit plan-only request and any active runtime mode.

### Environment-as-prompt (compoundable)

- **Pattern:** treat the agent's runtime environment — startup script, env vars, internet access — as part of the persistent prompt. Iterate on env config every time a build error appears and ask whether the env should have prevented it.
- **Why:** env improvements compound. A startup script that installs the right toolchain once removes a category of errors from every future task in the repo.
- **Anti-pattern:** treating env failures as one-off prompt fixes. The agent re-discovers the same gap on every new task.
- **Recipe:** maintain a single `setup.sh` (or equivalent) that the agent runs at session start; add to it when a class of build error recurs.

### Prompt-as-GitHub-Issue

- **Pattern:** structure prompts the way you would write a PR description or issue — file paths, component names, diffs, doc snippets, and "implement this the same way it's done in [module X]" anchors.
- **Why:** the model already responds well to PR/issue-shaped text from training distribution; this is free signal that doesn't require new tooling.
- **Anti-pattern:** chat-shaped prompts ("can you change the auth flow?") that omit the repo coordinates the agent needs to act precisely.

### Task queue as lightweight backlog

- **Pattern:** fire off tangential ideas, partial work, or incidental fixes as separate Codex tasks rather than holding them in human working memory. The queue *is* the backlog; no obligation to produce a full PR per task.
- **Why:** captures drive-by fixes without forcing context switches; staging area mirrors the engineer's working set.
- **Where this lives in the library:** see [`../../ai-coding-agents-state/SKILL.md`](../../ai-coding-agents-state/SKILL.md) for the task-runtime detail and the sizing heuristic (~1 hour of human work / a few hundred LOC).

### Best-of-N as a generation primitive

- **Pattern:** generate N parallel solutions for a single task and either pick the best or combine parts of multiple outputs.
- **Why:** for ambiguous or open-ended tasks, the cheapest quality-improving move is variance, not better prompting.
- **Anti-pattern:** running Best-of-N on tasks with one obviously correct shape (mechanical refactors, type fixes). Wasted compute; pick prompt engineering instead.
- **Vendor scope:** Codex-specific feature surface. The equivalent on other runtimes is parallel subagent dispatch — see [`../agents-swarm-orchestration/SKILL.md`](../../agents-swarm-orchestration/SKILL.md).
