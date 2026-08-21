# Typical Scenarios

End-to-end walkthroughs for the situations that bring people to this skill. Each follows the same shape: **Situation → Which layer → What to write → How to verify.** Runtime-specific steps are marked **[Claude Code]** or **[Codex]**; unmarked steps apply to both.

## Table of Contents

1. [Instructions are being ignored](#1-instructions-are-being-ignored)
2. [Team handoff — trusting a mature memory file](#2-team-handoff--trusting-a-mature-memory-file)
3. [Migrating repeated prompt preambles into memory](#3-migrating-repeated-prompt-preambles-into-memory)
4. [Recovering from memory bloat](#4-recovering-from-memory-bloat)
5. [Codex-only project setup](#5-codex-only-project-setup)
6. [Multi-repo portfolio drift — remediation](#6-multi-repo-portfolio-drift--remediation)
7. [Headless / CI agent runs](#7-headless--ci-agent-runs)

---

## 1. Instructions are being ignored

**Situation**: A rule is written in `CLAUDE.md` / `AGENTS.md` but the agent keeps violating it.

**Diagnose in this order** (cheapest first — stop at the first hit):

1. **Is the file even loaded?**
   - **[Claude Code]** Run `/memory` — it lists every loaded `CLAUDE.md`, rule file, and memory file. If the file is absent, check cwd (loading is cwd-upward), `claudeMdExcludes` in local settings, and that you are in the right repo root.
   - **[Codex]** Run `codex --show-context` (or `/init` to confirm discovery). Symlinked/remote workspaces historically missed `AGENTS.md`; confirm the right file resolved.
2. **Is the rule past the instruction ceiling?** Compliance falls off after ~150–200 discrete instructions across *all* loaded tiers combined. Count with `wc -l` across every loaded file. If you are over budget, the rule is not being "ignored" — it is being out-competed. Prune lower-value lines.
3. **Is a higher-priority tier contradicting it?** Order: user/project explicit instructions > scoped rules > the rest. A global `~/.claude/CLAUDE.md` line or a more recent rule can override the one you are watching. Grep all tiers for the conflicting topic and resolve to one statement.
4. **Is it a literal-interpretation miss?** Opus 4.7+ takes lines at face value. "Keep functions small" does nothing; "functions over 40 lines must be split" is enforceable. Rewrite vague imperatives as success criteria.
5. **Is it a hard requirement masquerading as a suggestion?** Memory *suggests*; it cannot *guarantee*. If the rule must hold every time (no secrets committed, tests must pass), move it to a hook or CI gate. See [structure-patterns.md](structure-patterns.md) "Hooks vs Project Memory" and the `agents-hooks` skill.

**Verify the fix**: re-run the exact prompt that triggered the violation. If behavior changes, the diagnosis was right. If not, you stopped too early — continue down the list.

---

## 2. Team handoff — trusting a mature memory file

**Situation**: You inherit a repo whose `AGENTS.md` / `CLAUDE.md` is large and old. Can you trust it?

**Which layer**: read-only audit before you edit anything.

**What to do**:

1. Run the audit gate: `bash scripts/audit_repo.sh <repo>` — surfaces stale paths, wrong-layer content, scaffold-tense, and platitudes. Treat HIGH findings as "do not trust until checked."
2. Run `bash scripts/lint_claude_memory.sh <repo>` for size/symlink/secrets/import hygiene.
3. For every rule, ask the exception-file test: *would the agent infer this from the code/README anyway?* Inferable lines are noise that survived; flag them.
4. Distinguish **reactive** rules (added after a real mistake — keep) from **pre-emptive** ones (added "just in case" — suspect). Reactive rules usually carry a "why/example" note; pre-emptive ones rarely do.
5. Cross-check volatile claims (model versions, CLI flags, version pins) against current docs — see SKILL.md "Fact-Checking".

**Verify**: the file is trustworthy when `audit_repo.sh` shows no HIGH findings *and* every remaining rule answers "what mistake does this prevent?". Anything that fails both is a candidate for deletion, not preservation.

---

## 3. Migrating repeated prompt preambles into memory

**Situation**: You paste the same context ("we use pnpm not npm", "always run `make check` before pushing") into most prompts.

**Which layer**: durable, shared → `AGENTS.md`. Machine-local recall that evolves → auto-memory (**[Claude Code]** auto-memory dir; **[Codex]** the `memories` layer).

**What to write**:

1. **Identify**: list the lines you repeat. The threshold — if a line would appear in >80% of your prompts on this repo, it belongs in memory; below that, keep it per-prompt intent.
2. **Classify**: strategic/durable context → memory; per-task intent ("now refactor the auth module") stays in the prompt. Do not lift intent into memory.
3. **Extract** one line at a time into `AGENTS.md`, phrased as a success criterion or exact command, not a vibe.
4. **Verify behavior is unchanged**: run a representative prompt *without* the preamble. If the agent now does the right thing from memory alone, the extraction worked.
5. **Prune the prompt**: delete the lifted lines from your prompt template so they are not double-counted against the instruction budget.

**Verify**: the preamble is gone from your prompts and the top 3 workflows still behave correctly. If a workflow regresses, the line was intent (return it to the prompt), not durable context.

---

## 4. Recovering from memory bloat

**Situation**: `CLAUDE.md` / `AGENTS.md` has grown to 300–500+ lines over months and the agent's adherence is getting *worse*.

**Why it gets worse, not better**: past the ~150–200 instruction ceiling, adding rules dilutes all of them. Bloat is negative-yield.

**What to do** (prune without breaking behavior):

1. **Snapshot first.** Copy the current file to a dated archive *outside* the agent-write path before cutting. Never prune the only copy.
2. **Sort by yield.** For each line ask: (a) is it inferable from code/README? (b) does it answer "what mistake does this prevent?" (c) has it caught a real mistake? Lines failing (a)/(b) go first.
3. **Cut categories that earn nothing on current models**: personality lines ("act like a senior engineer", "think step by step"), progress scaffolding ("summarize every N steps"), "be concise" / length nags, and post-compaction re-anchoring — see [opus-4-7-memory-migration.md](opus-4-7-memory-migration.md).
4. **Demote, don't delete, real detail.** Long procedures → `docs/`. Path-specific rules → **[Claude Code]** `.claude/rules/*.md` with `paths:` frontmatter / **[Codex]** nested `AGENTS.md`. Reusable workflows → a skill.
5. **Target**: hot memory back under ~100–150 usable lines across all loaded tiers.

**Verify**: `wc -l` confirms the cut; then re-run your top 3–5 prompts. If none regressed, the removed lines were dead weight — which is the common case.

---

## 5. Codex-only project setup

**Situation**: A repo (or a teammate) uses Codex with no Claude Code in the loop. The default "symlink `CLAUDE.md` → `AGENTS.md`" pattern does not apply.

**Which layer**:

- **Shared, committed** → `AGENTS.md` at repo root (run `codex` `/init` to scaffold). Nested `AGENTS.md` in packages that need local context.
- **Personal behavioral instructions, cross-repo** → `~/.codex/AGENTS.md`.
- **Higher-precedence directory guidance** → `AGENTS.override.md`; it may be developer-local or checked in.
- **Operational config** (model, reasoning effort, sandbox/approval, MCP servers, multi-agent limits) → `config.toml`, **not** `AGENTS.md`. See [loading-and-layers.md](loading-and-layers.md) for the split.
- **Accumulated recall** → the Codex `memories` layer (opt-in; off by default) — keep must-always rules in `AGENTS.md`, not here.

**What to write**: the same essentials checklist as Claude Code (layout, exact build/test/lint commands, conventions, prohibitions, verification). Skip Claude-only mechanisms (`.claude/rules/`, `claudeMdExcludes`, hooks) — they do nothing in Codex.

**Verify**: `codex --show-context` shows the expected `AGENTS.md` resolved; a fresh session follows a repo-specific rule with no prompt reminder.

---

## 6. Multi-repo portfolio drift — remediation

**Situation**: Several repos started from a shared `AGENTS.md` baseline that has silently forked. Detection found divergence; now reconcile it.

**Which layer**: cross-repo alignment, then per-repo commit.

**What to do**:

1. **Detect**: `bash scripts/compare_blocks.sh <repo1> <repo2> ...` classifies shared H2 sections as IDENTICAL / ALIGNMENT-CANDIDATE / REVIEW / DIVERGENT by line overlap.
2. **Triage by class**: IDENTICAL → leave. ALIGNMENT-CANDIDATE → these *should* match but drifted; pick the canonical version (usually the most recent or most-tested). REVIEW/DIVERGENT → intentional per-repo difference; leave but document *why* so the next audit does not "fix" it.
3. **Reconcile**: edit each lagging repo's section to the canonical text in its own commit (keep paired `AGENTS.md`/`CLAUDE.md` changes together). Do not introduce a third variant.
4. **Re-run** `compare_blocks.sh` to confirm the candidates are now IDENTICAL.

**Verify**: the alignment-candidate set is empty (or every remaining divergence has a one-line rationale). Run `audit_portfolio.sh` to confirm no repo regressed to a HIGH finding.

---

## 7. Headless / CI agent runs

**Situation**: An agent runs non-interactively (GitHub Actions, a cron job, a remote queue) with no human to answer clarifying questions.

**Which layer**: `AGENTS.md` carries more weight here — there is no interactive turn to supply intent, so durable memory *is* the contract.

**What to write / check**:

1. **No interactive escapes.** Remove any rule that says "ask the user before X" as the only safeguard — in headless mode there is nobody to ask. Convert those to a hard default or a CI gate.
2. **Exact, non-interactive commands.** Flags that prompt (`-i`, interactive rebases, `git add -i`) will hang. Document the non-interactive equivalents.
3. **Verification must be machine-checkable.** "Confirm it looks right" is useless headless; specify the command whose exit code decides pass/fail.
4. **Auto-memory may differ.** **[Claude Code]** machine-local auto-memory and **[Codex]** the `memories` layer may be absent or disabled in CI (Codex memories are off by default and may be unset on a fresh runner). Do not rely on accumulated recall existing — put anything load-bearing in committed `AGENTS.md`.
5. **Interactively-authenticated MCP servers may be missing.** Tools that need a browser login can be absent in headless runs; gate on their presence rather than assuming them.

**Verify**: dry-run the exact CI invocation locally with no TTY (e.g. pipe from `/dev/null`); confirm it completes without waiting on input and that every verification step returns a real exit code.
