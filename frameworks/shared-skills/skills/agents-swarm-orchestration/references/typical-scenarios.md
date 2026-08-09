# Typical Scenarios

Maps common real jobs to a recommended orchestration shape. Read this when you know *what* you need to do but not *how* to dispatch it. Every row composes with the rest of this skill — the patterns are named in [../SKILL.md](../SKILL.md) §Named Patterns, the schemas in [output-contracts.md](output-contracts.md), the limits in [operational-guardrails.md](operational-guardrails.md).

The first question is always **"should this fan out at all?"** Most rows below are only correct *after* a single lead + one verifier has been ruled insufficient (Known Trap: swarm-before-checking).

## Table of Contents

- [How To Read A Scenario Row](#how-to-read-a-scenario-row)
- [Scenario Decision Table](#scenario-decision-table)
- [Deep Walkthrough 1 — Framework Migration / Large Refactor](#deep-walkthrough-1--framework-migration--large-refactor)
- [Deep Walkthrough 2 — Security / Compliance Sweep](#deep-walkthrough-2--security--compliance-sweep)
- [Deep Walkthrough 3 — Dependency-Chain Feature](#deep-walkthrough-3--dependency-chain-feature)
- [Cross-Platform Notes](#cross-platform-notes)
- [Anti-Scenarios — Do Not Swarm These](#anti-scenarios--do-not-swarm-these)

## How To Read A Scenario Row

Each scenario names: the **trigger**, the **surface + pattern** (from §Named Patterns), the **worker shape** (count + read/edit + model tier from §Model Guidance), the **wave structure**, and the **one trap** most likely to bite. Worker counts assume a shared branch; worktree isolation relaxes the read-only cap, never the edit-capable cap of 3.

## Scenario Decision Table

| # | Scenario | Trigger | Surface + pattern | Worker shape | Waves | Key trap |
|---|----------|---------|-------------------|--------------|-------|----------|
| 1 | **Framework migration / large refactor** | 10+ files, mechanical-ish, shared interface | Subagents, orchestrator-worker | ≤3 edit (balanced) + 1 read scout (fast); worktree isolation | Scout → freeze → edit waves of ≤3 → integration verify | Editing before the shared interface is frozen → merge thrash |
| 2 | **Cross-repo / portfolio audit** | Read-only inventory across many repos/dirs | Subagents, broad read fan-out | N read-only (fast/Haiku/Spark), N large | One wave; merge to one report | Workers re-reading the same broad context independently (cost smell) |
| 3 | **Test / flaky-test triage** | Failing or flaky suite, cause unknown | Subagents, read fan-out + 1 verifier | N read-only triage (fast) + 1 verifier (balanced) | Triage wave → verify the proposed cause | "Done" with no repro artifact — reject reports missing evidence |
| 4 | **PR / code-review board** | Diff needs multi-dimension review | Subagents or team, self-consistency / debate | 1 worker per dimension (security, perf, tests, style) read-only | Review wave → lead adversarially verifies each finding | Pipeline amplifies shared bias — baseline against one fresh reviewer (arXiv:2604.08963) |
| 5 | **Security / compliance sweep** | Auth, secrets, data-flow, policy | Subagents, orchestrator-worker + mandatory verifier | N read-only finders (balanced/strong) + 1 reviewer (strong) | Find → verify → human gate before any fix | Auto-merge on a high/critical task — must hit the human approval gate |
| 6 | **Dependency-chain feature** | schema → API → UI, real ordering | Subagents, dependency-aware waves | 1 edit worker per layer (balanced) | Strict waves; distilled dependency output between each | Forwarding raw upstream logs instead of a `contract_summary` |
| 7 | **Deep research / competitive intel** | Independent research streams | Subagents (isolated) or manager | N read-only research (balanced) + lead synthesizes | Stream wave → lead synthesis pass | Lead pastes raw transcripts into synthesis — distill first |
| 8 | **Multi-domain doc generation** | Write many files across domains | Subagents, large-scale write swarm | Up to 8–13 edit workers, exclusive dirs | Phased by dependency; verify file counts per phase | Context exhaustion mid-write — give exact read/write paths, not "all files" ([operational-guardrails.md](operational-guardrails.md) §Large-Scale Write) |
| 9 | **Evaluator-optimizer content loop** | Quality hard to verify deterministically | Generator + evaluator, capped retry | 1 generator + 1 evaluator (balanced) | Generate → evaluate → retry (max 2–3) → escalate | Unbounded retry loop — cap and pass only evaluator findings to retry |
| 10 | **CI / batch migration (non-interactive)** | Script-driven, no human in loop | Blueprint (deterministic + agentic) | Fan-out script + isolated `claude -p` / Codex workers | Wave 0 setup → agentic impl → deterministic verify → deliver | No script-level retry budget — auto-mode aborts with no human fallback ([noninteractive-and-blueprints.md](noninteractive-and-blueprints.md)) |
| 11 | **Scheduled / loop swarm** | Recurring unattended run | Any, wrapped in loop/schedule | Smallest viable; cheap tier; `flex`/background | Per tick; explicit stop condition | No owner / stop condition / success metric → operational debt |

## Deep Walkthrough 1 — Framework Migration / Large Refactor

**Job:** migrate 14 files from a deprecated API to its replacement. Mechanical per file, but they share a few helper signatures.

1. **Scout wave (1 read-only, fast model).** Map every call site, the shared helpers, and the exact import surface. Output → `reports/migration-map.json`, not the transcript.
2. **Freeze.** Lead decides the final helper signatures from the scout map and writes them to a frozen interface file. Nothing edit-capable launches until this exists (Operating Principle: freeze shared interfaces first).
3. **Edit waves of ≤3 (balanced model, worktree isolation).** Each worker owns an exclusive file set; `do_not_touch` lists the shared helper file (lead owns that). Brief uses the minimal worker template from §Dispatch Workflow, with `VERIFICATION: <per-file test + lint>`.
4. **Merge one at a time.** Lead validates `files_touched ⊆ owned_files`, runs the worker's verification, merges, then unblocks the next wave (§Lead Merge Contract).
5. **Integration verify.** After all waves, lead runs the full suite once. Partial-wave failure rolls back per the pre-declared rollback plan (Known Trap: no rollback plan).

**Why not one big wave:** edit-capable cap is 3 on a shared branch — super-linear merge cost above that. Worktree isolation lets read-only scouts go wide but does not lift the edit cap.

## Deep Walkthrough 2 — Security / Compliance Sweep

**Job:** find auth, secrets, and data-flow risks across a service before release. `risk_level: high`, often `critical`.

1. **Find wave (N read-only finders, balanced/strong model).** One finder per concern (authz, secret handling, PII flow, dependency CVEs). Each returns structured findings with a dated file:line citation; reject any finding without one (self-rejection clause: "reject the review if it contains zero inline line references").
2. **Adversarial verify (1 reviewer, strong model).** The reviewer's job is to *refute* each finding, not confirm it — default to refuted if uncertain. This counters bias amplification: a finder pipeline polarizes toward its own framing (arXiv:2604.08963), so the verifier must be an independent lens, not a second finder with a new title (Verifier Discipline: bad case = same prompt, different title).
3. **Human gate.** No fix merges automatically. Critical-risk side effects require human approval *before* execution (§Escalation Defaults). The lead presents confirmed findings; the human authorizes remediation scope.
4. **Remediation** (only after authorization) follows Walkthrough 1's edit-wave discipline.

**Why a verifier is mandatory here, optional elsewhere:** the cost of a false negative is a shipped vulnerability. This is the case where the verifier catches a *different class* of error than the finder — its independent value is the whole point.

## Deep Walkthrough 3 — Dependency-Chain Feature

**Job:** ship a feature that needs a DB schema change, then an API layer, then a UI — real ordering, not parallelizable.

1. **Wave 1 — schema (1 edit worker).** Owns `db/`. Returns a dependency output contract, not a log: `{ "artifacts": ["db/schema.sql"], "contract_summary": "added users.id UUID PK + sessions.user_id FK", "breaking_changes": [], "open_risks": [...] }` (§Dependency Output Contract).
2. **Wave 2 — API (1 edit worker).** Receives *only* the Wave 1 `contract_summary` as `read_only` input — never the schema worker's transcript. Owns `src/api/`. Emits its own contract for the UI.
3. **Wave 3 — UI (1 edit worker).** Consumes the API contract. Owns `src/ui/`.
4. **Integration verify** after the chain completes.

**Why strict waves, not fan-out:** each layer's contract is an input to the next. Launching them together means Wave 2 guesses at an interface Wave 1 hasn't frozen — exactly the conflict the wave structure exists to prevent. The savings from parallelism are zero when the dependency is real; the risk is not.

## Cross-Platform Notes

Every scenario maps to both runtimes; the dispatch primitive differs, the shape does not.

| Concern | Claude Code | Codex |
|---------|-------------|-------|
| Dispatch a wave | Spawn multiple subagents in one turn (explicit under Opus 4.7) | "Spawn one agent per item, wait for all, summarize each" (explicit activation) |
| Read-only scout | `Explore` built-in (Haiku) | `explorer` built-in, `sandbox_mode = "read-only"` |
| Edit worker isolation | `isolation: worktree` | `sandbox_mode = "workspace-write"` + controlled sandbox |
| Concurrency cap | No hard cap; depth always 1 | `max_threads: 6`, `max_depth: 1` (never raise depth) |
| Non-interactive (scenario 10) | `claude -p ... --output-format json` + `parallel` | Codex CLI batch + `spawn_agents_on_csv` (one worker per row) |
| Cheap loop tier (scenario 11) | `CLAUDE_CODE_SUBAGENT_MODEL` | `[profiles.cheap-loop]` + `service_tier = "flex"` |

Do not hardcode model IDs — verify against [platform-patterns.md](platform-patterns.md) and the live docs before dispatch.

## Anti-Scenarios — Do Not Swarm These

| Looks like a swarm job | Why it isn't | Do instead |
|------------------------|--------------|------------|
| "Fix this one bug" | Single context, no independent sub-tasks | Stay in the main thread; debug serially |
| "Refactor this module" where everything touches the same files | File-collision-prone; cap-3 doesn't help | One agent, sequential |
| "Make it work" (ambiguous) | Blocker is product ambiguity, not bandwidth | Resolve scope first; swarm can't fix unclear goals |
| "Add a verifier to every task" | Verifier with no distinct contract is pure cost | Add a verifier only when it catches a different error class |
| Reasoning-heavy single decision under fixed budget | Message-passing loses mutual information vs. one strong model on full context | One strong agent, full context (Tran & Kiela, arXiv:2604.02460 — scope limited to multi-hop reasoning) |

When in doubt, run one strong agent first and measure. Fan out only when a named, independent sub-task list exists and the coordination cost is below the parallelism gain.
