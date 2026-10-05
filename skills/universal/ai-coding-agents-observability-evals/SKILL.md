---
name: ai-coding-agents-observability-evals
description: "Designs coding-agent observability and evals. Use when measuring traces, replay, checkpoint lineage, quality trajectories, tool grading, regression, or cost."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-09-27
---

# AI Coding Agents Observability And Evals

Use this skill to design or review the feedback loop around a coding-agent runtime: traces, replayable transcripts, eval packs, regression gates, tool-call grading, latency and cost accounting, and production failure triage.

This skill covers how you operate a coding-agent product after the core runtime exists. It does not replace the runtime skills themselves.

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| What should the trace and telemetry model include? | [references/trace-and-telemetry-model.md](references/trace-and-telemetry-model.md) | Durable trace schema, session correlation, event stages, and replay boundaries |
| How should evals, regressions, and cost controls work? | [references/evals-regression-and-cost-ops.md](references/evals-regression-and-cost-ops.md) | Golden tasks, iterative self-extension packs, trajectory scorecards, and cost-aware release gates |
| How do I use the eval/trace substrate to improve the harness itself? | [references/harness-self-evolution.md](references/harness-self-evolution.md) | Closed-loop harness evolution: three observability pillars, falsifiable-contract edits, attribution |
| How does OpenAI Codex combine rollout replay, SQLite state, doctor reports, and telemetry? | [references/openai-codex-rollout-doctor-telemetry.md](references/openai-codex-rollout-doctor-telemetry.md) | Replay artifacts, rebuildable state indexes, redacted diagnostics, W3C traces, token metrics |
| How does Codex wire OTel exporters and what analytics events exist? | [references/openai-codex-otel-config.md](references/openai-codex-otel-config.md) | Schema lookup step, OTel vs proprietary analytics boundary, tracestate propagation and cardinality rules |

## When To Use

- Design tracing and replay for a coding-agent CLI
- Add regression evals for coding, review, or task-execution agents
- Evaluate whether a coding agent preserves correctness and structural quality while extending its own workspace across evolving specifications
- Grade tool calls, patch quality, verification behavior, or handoff quality
- Build latency, token, and cost accounting for agent sessions
- Review how incidents and bad runs should be debugged from stored traces

## Use Other Skills

| Need | Use Instead |
|------|-------------|
| Broader coding-agent architecture | [`../ai-coding-agents/SKILL.md`](../ai-coding-agents/SKILL.md) |
| Session persistence and transcript restore | [`../ai-coding-agents-state/SKILL.md`](../ai-coding-agents-state/SKILL.md) |
| Tool runtime design | [`../ai-coding-agents-runtime-core/SKILL.md`](../ai-coding-agents-runtime-core/SKILL.md) |
| Generic agent eval harnesses | [`../qa-agent-testing/SKILL.md`](../qa-agent-testing/SKILL.md) |
| Reliability and observability outside agent systems | [`../qa-observability/SKILL.md`](../qa-observability/SKILL.md) |

## Default Workflow

1. **Define the trace spine.** Session, turn, tool call, approval, worker, and verification events should share one correlation model.
2. **Store replay-safe artifacts.** Persist prompts, tool inputs, outputs, diffs, approvals, and synthesized summaries with enough structure to replay failures.
3. **Separate product telemetry from eval telemetry.** Production traces describe what happened; eval runs describe whether it was acceptable.
4. **Build golden task packs.** Keep a representative set of coding, review, debugging, multi-agent, and iterative self-extension tasks with stable scoring rubrics.
5. **Grade behavior, not just final output.** Score tool choice, verification discipline, retry loops, escalation quality, and cost efficiency.
6. **Keep telemetry cardinality under control.** Stable prompt IDs, opaque hashes, and bounded error categories belong in event payloads; high-cardinality strings do not belong in metrics dimensions.
7. **Attach release gates to deltas.** Compare candidate changes against a known baseline for quality, cost, latency, failure-mode drift, and—when work carries across checkpoints—trajectory slope and late-checkpoint regressions.
8. **Instrument incident triage.** A bad run should be trace-searchable by repo, user, session, tool, provider, worker, and error family.
9. **Review regressions continuously.** Add new real failures back into the eval corpus so the system hardens over time.

## Host Rules

- Triage a bad run on a user's machine by running the agent CLI's own doctor or diagnostic command first (Codex's `doctor` subcommand is one example), before reading traces. It surfaces install, update-target, auth, config, sandbox-helper, and MCP faults that traces do not show. Ask for its redacted machine-readable report (`codex doctor --json`), not screenshots or the `--summary` view. Report schema: [Doctor Reports](references/openai-codex-rollout-doctor-telemetry.md#doctor-reports).
- Keep one canonical trace ID across the entire session lifecycle.
- Preserve causal order for tool calls, approvals, worker messages, and verification passes.
- Keep event ordering monotonic within a session even when log sinks or transports are asynchronous.
- Store enough normalized state to debug a run without depending on transient UI rendering.
- Score traces at multiple layers: final answer, tool behavior, and workflow correctness.
- Preserve checkpoint and workspace lineage for iterative evals; a final snapshot cannot explain when extensibility was lost.
- Track token and cost usage per turn and per subsystem, not only per session total.
- Use eval results to block releases when quality or cost drift exceeds explicit thresholds.
- Hash or redact user-identifying plugin or extension data before it becomes telemetry dimensions.
- Isolate the grader from the agent: a coding agent can edit tests, `conftest.py`, or CI config and turn a gate green. Hash test and grader paths before and after each eval task, grade from a clean checkout of those paths, and emit a `harness_tamper` trace event that auto-fails the task on any change.

## Recovery And Budget Evidence

Emit recovery events as typed state transitions rather than free-form errors. The minimum set is `reconnect_started|succeeded|failed`, `control_cancelled`, `fallback_activated`, `worker_escalated`, and `plugin_loaded|reloaded|disabled`. Each event carries stable session/turn/worker/plugin IDs, attempt number, bounded reason class, prior and next state, and duration. Keep raw payloads and detailed provider errors in redacted traces; metrics receive only the bounded event and reason classes.

Track task budget, context/input tokens, output tokens, reasoning tokens when exposed, tool calls, wall time, and external spend as separate fields. A task may exhaust one while retaining the others, and some runtimes enforce only a subset. Record `limit_source`, `limit_value`, `observed_value`, and terminal outcome so a recovered run is distinguishable from a failure or user cancellation. Evals should grade recovery correctness, duplicate-side-effect avoidance, cancellation latency, and whether the final status matches the trace.

## Build Order

1. Define the canonical trace and correlation model.
2. Persist replay-safe prompts, tool IO, approvals, and diffs.
3. Add event sequencing, redaction, and low-cardinality telemetry rules.
4. Add per-turn and per-subsystem usage accounting.
5. Add production search and incident-debug views over traces.
6. Build eval corpora and scoring rubrics from real tasks.
7. Attach release gates to baseline deltas in quality, cost, and failure drift.

## Core Invariants

- Every meaningful runtime action must be trace-correlated.
- Production telemetry and eval telemetry are different datasets with different purposes.
- Replay must not depend on ephemeral UI state.
- Cost accounting must explain which subsystem and provider consumed budget.
- Real failures should feed the eval corpus over time.
- Metrics dimensions must stay low-cardinality even when trace events carry richer detail.

- Evals should reflect the real failure profile of your agent. Do not ship only synthetic tasks or happy-path benchmarks.

## Failure Modes

- Trace fragments that cannot be joined across tool calls, approvals, or workers.
- Incident debugging blocked because only rendered output was stored.
- Eval suites scoring final answers while missing workflow regressions.
- Cost spikes that cannot be attributed to provider, tool, or worker class.
- Release gates based on synthetic tasks that miss real production failures.
- Green tests at a final checkpoint masking steadily worsening extension robustness or structural quality.
- Metrics or dashboards becoming unusable because free-form strings were emitted as dimensions.

## Minimal Viable Version

- One canonical trace ID and turn correlation model.
- One replay-safe storage shape for prompts, tool calls, outputs, and approvals.
- One searchable incident view over stored traces.
- One golden-task eval pack with stable rubrics.
- One carried-workspace trajectory with per-checkpoint correctness, quality, cost, and duration when the product performs repeated repository edits.
- One low-cardinality telemetry policy for event fields versus metrics dimensions.
- One explicit threshold for blocking regressions in quality or cost.

## What Strong Implementations Add

- Recovery-specific trace events for reconnect, fallback, cancellation, and continuation.
- Per-subsystem cost and latency slices.
- Twin-column telemetry patterns with redacted or hashed identifiers where needed.
- Eval grading for verification discipline, escalation quality, and retry behavior.
- Continuous ingestion of real production failures into regression packs.
- Rollout gates that compare candidate builds to known-good baselines.
- Iterative self-extension packs that compare candidate and baseline trajectories, including degradation slope and late-checkpoint behavior rather than only final scores.
- A closed-loop **harness self-evolution** layer that turns the eval corpus into an optimizer signal (see [references/harness-self-evolution.md](references/harness-self-evolution.md)) — advanced, not MVP.

## Known Traps

- Logging only user-visible messages and losing the tool, permission, retry, and fallback evidence needed to explain failures.
- Designing replay as a transcript export instead of a structured artifact set that can reconstruct routing, tool calls, and decision boundaries.
- Aggregating eval, runtime, and cost signals into one scoreboard and making regressions impossible to attribute.
- Tagging telemetry with raw prompts, provider payloads, or user data that should have been redacted or hashed before export.
- Shipping evaluation suites that reward benchmark gains while ignoring recoverability, debuggability, and operational failure modes.
- Treating an anti-slop or plan-first prompt as a durable quality control without measuring what happens after repeated extensions.

## Common Anti-Patterns

- Logging only the final answer and calling it observability.
- Treating replay as a transcript screenshot rather than structured artifacts.
- Mixing production telemetry and eval metrics into one undifferentiated score.
- Measuring only session-total cost with no attribution.
- Emitting raw provider, plugin, or prompt text into metrics tags.
- Shipping on benchmark wins while ignoring incident-debuggability.

## Iterative Self-Extension Trajectories

Single-shot correctness and green tests do not prove extension robustness. Add a versioned iterative pack when the agent is expected to revisit the same codebase: each checkpoint supplies an evolved external specification and the agent continues from its own prior workspace. Record fresh checkpoint context separately from the carried code so the eval measures the consequences of earlier design choices rather than conversation recall.

For every checkpoint, persist lineage plus the outcome vector: `trajectory_id`, `checkpoint_id`, `parent_checkpoint_id`, `spec_version`, workspace identity and content hash, strict/isolated/core/regression results, erosion, verbosity, cost, and duration. Compare candidate and baseline trajectories on both level and slope. A release review should surface worsening structural-quality slope or a late-checkpoint correctness regression even when the final aggregate score is green. Derive product-specific gates from a representative baseline and repeated runs; SlopCodeBench does not establish universal thresholds.

One long-horizon preprint reports that explicit quality-guidance prompts reduced initial verbosity and erosion but did not change the degradation rate; effects on correctness are unsourced — verify. Prompt-only controls are therefore insufficient: keep the trajectory pack as the control surface and treat prompt changes as candidates to evaluate. Use [`../qa-agent-testing/SKILL.md`](../qa-agent-testing/SKILL.md) for the detailed carried-workspace benchmark protocol and [`../software-clean-code-standard/SKILL.md`](../software-clean-code-standard/SKILL.md) for structural-erosion and verbosity definitions; this skill owns their telemetry and release-gate integration, not their formulas.

## OTel gen_ai Semantic Conventions

The OpenTelemetry GenAI semantic conventions define a standard schema for agent telemetry. Before linking or pinning dashboards, resolve the conventions' current location and stability status from the OpenTelemetry project itself. Key attributes:

- `gen_ai.operation.name` — operation identifier on the root span (e.g., `invoke_agent`, `create_agent`, `execute_tool`)
- `gen_ai.agent.name`, `gen_ai.agent.id`, `gen_ai.agent.version` — agent identity
- `gen_ai.tool.name` / `gen_ai.tool.call.id` — child spans for tool invocations
- `gen_ai.conversation.id` — cross-turn conversation correlation

**Location caveat (verify before citing a URL):** the gen_ai conventions have been relocated within the OpenTelemetry project before, and old spec pages can render "moved" notices while the attribute names stay valid; at last check the `opentelemetry.io` gen-ai spec page itself pointed to a separate `open-telemetry/semantic-conventions-genai` repository. Treat any bookmarked gen-ai spec URL as unstable; re-resolve it from the OpenTelemetry project before you cite it in a runbook or dashboard link.

**Experimental status caveat:** while the conventions are experimental, most SDKs emit them only behind an opt-in such as `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental`; check the SDK's docs for the current flag. Expect attribute churn until the conventions are declared stable. Design instrumentation against the attribute names, but gate production dashboards and alerting thresholds on a version-pinned snapshot, not "whatever the SDK emits today," so an upstream rename doesn't silently blank a panel.

**Contrast with Codex proprietary crate:** Codex ships a bespoke `codex-rs/otel` crate (OtelSettings TOML, OtelExporter variants, W3C tracestate propagation) that predates the gen_ai semconv. The proprietary crate maps to the same conceptual slots but uses different attribute names and has no gen_ai.tool.call.id equivalent. When building cross-runtime dashboards, normalize to gen_ai semconv attributes and treat the Codex-proprietary shape as a source adapter.

**Cache-hit telemetry:** provider-side prompt caching can move cost and latency sharply without any quality change, and API choice and prompt layout affect hit rates. Track cache hits (and cache writes, where billed) as their own cost dimension, separate from inference cost. Do not fold cache hits into generic token-usage metrics; they have different cost multipliers and different debugging value. Look up the provider's current caching and pricing docs before estimating the savings of an API migration.

## Eval-Pack Identity And Artifact Validation

Two pre-release patterns that hold across agent runtimes:

### Named, versioned eval pack

- **Pattern:** give the eval corpus a product name, a semantic version, and a published rubric. "Did it pass `<pack> v2.1`?" is a more actionable release gate than "did the eval suite pass?"
- **Anti-pattern:** an eval suite that silently changes its task set between releases, so pass-rate deltas are not comparable.
- **Recipe:** publish the pack as a versioned artifact, cite the pack version in release notes, and record a pack-version field in eval telemetry so historical pass rates stay interpretable after the pack evolves.

### Static validation for declarative agent artifacts

- **Pattern:** every declarative artifact an agent reads (MCP manifests, plugin manifests, workflow/recipe files, eval task definitions, skill frontmatter) gets a static validator for schema conformance, undeclared-extension use, and policy violations. Run it in CI, at package, at install, and at runtime load; each layer catches different drift.
- **Anti-pattern:** validating only at runtime, so invalid artifacts reach the user as a cryptic crash instead of a pre-ship error.
- **Recipe:** add a `validate` command to the CLI that runs all static gates (schema conformance, dependency reachability, policy compliance, extension allowlist intersection) and wire it into CI and the activation path.

## Harness Self-Evolution (Frontier)

Static evals tell you *whether* a build regressed. A harness-evolution loop goes further: the same trace + eval substrate becomes the reward signal for automatically improving the **harness** (tool wiring, middleware, memory, retry/verification scaffolding — not the system prompt). One preprint reports observability-driven harness evolution beating a human-designed harness on Terminal-Bench 2 and transferring frozen to SWE-bench-verified at lower token cost (single-paper preprint result; see [references/harness-self-evolution.md](references/harness-self-evolution.md)). Public-benchmark gains are not a release signal for your product: public coding benchmarks can be exploited, saturated, or retired, so gate on your own versioned pack.

This needs three distinct observability surfaces — **component** (every editable harness part is file-level and revertible), **experience** (trajectories distilled into an agent-readable evidence corpus, not a human dashboard), and **decision** (every edit carries a pre-declared prediction verified against the next eval round). The decision pillar — falsifiable contracts per edit — is what separates attributable evolution from benchmark-chasing that overfits the corpus.

Keep this strictly separate from the production release gate (Core Invariant: optimizer never trains on production telemetry), and add it only once the eval corpus is versioned and trustworthy. Full method, the loop, evidence, and the Pattern/Anti-pattern/Recipe are in [references/harness-self-evolution.md](references/harness-self-evolution.md).

## Expert Judgment: Where Non-Experts Get This Wrong

These are the calls a strong operator makes differently from a team that just wired up a tracer and a pass/fail suite.

- **A pass-rate delta on a small pack is not a release gate until it is tested as paired data.** A 30-task golden pack moving from 26/30 to 24/30 (87%→80%) looks like a regression but cannot be resolved at that size. Both builds run the same tasks, so compare them per task: count discordant pairs (b = tasks the baseline passed and the candidate failed, c = the reverse) and apply an exact McNemar / sign test on b vs c. If the 2-point drop is 3 new failures and 1 new pass, exact two-sided p ≈ 0.63; with 30 tasks, even 5 new failures and no new passes gives p ≈ 0.06, and it takes 6-to-0 to clear 0.05. Do not gate by comparing each build's own Wilson or Clopper-Pearson lower bound: at equal n that bound is monotone in the pass count, so the rule collapses to "never lose one task" (point-estimate gating in disguise). Pre-declare the minimum detectable effect and alpha, size the pack from them, and treat a non-significant result on an underpowered pack as "unresolved", not "no regression". When you repeat runs per task to cut agent noise, aggregate to a per-task pass rate first and test the per-task differences (paired bootstrap or sign test); do not pool repeated runs as independent pairs. Use pass^k (the task passes on all k runs) when the claim is reliability rather than average quality. Method and power sizing: [`../ai-evals/references/eval-statistics.md`](../ai-evals/references/eval-statistics.md).
- **"Replay" means two different measurements; label which one ran.** A replay that stubs tools with recorded outputs isolates the agent change; a replay that re-executes tools live usually mixes environment drift (dependency, network, repo state) into the delta. Tag every eval run `replay:recorded` or `replay:live`, and compare candidate vs baseline only within one mode; check the trace model for which tool outputs are actually captured before trusting recorded mode.
- **Uniform trace sampling throws away the signal you built observability for.** At scale, capturing every session at full fidelity is a cost problem, so teams sample — but uniform sampling keeps the 99% of boring successful runs and drops exactly the failed, escalated, or cancelled sessions that justify the whole pipeline. Sample on outcome, not on request count: capture 100% of failures, escalations, cancellations, and verifier rejections; sample successes at whatever rate the budget allows. This is tail-based sampling keyed on business outcome, not on span duration.
- **`contains`/`excludes` substring checks in a golden task are gameable, and agents will find the gap.** An agent optimized against a static eval pack (by you, by harness self-evolution, or by the model provider's own RL) can learn to satisfy the literal check without satisfying the intent — e.g., adding a docstring containing the word "handles error" without handling the error. Treat any eval pack that has been used as an optimization target for more than a few cycles as partially compromised: rotate a subset of golden tasks, add mutated/adversarial variants, and keep at least one grading path (compiles, tests pass, schema-valid) that is not a substring match.
- **Full-fidelity traces of proprietary source code are a data-residency liability, not just an engineering convenience.** Storing complete file diffs and raw prompts (which routinely embed customer source, secrets in comments, or internal API names) in a central trace store creates an enterprise trust problem the moment a customer asks "where does our code go and who can read it." Decide early whether traces containing file content live in customer-controlled storage/region, get truncated to diff hunks plus hashes, or get a separate, shorter retention window than metadata-only telemetry — retrofitting this after a large customer's security review is far more expensive than designing it in.

## Navigation

### References

- [references/trace-and-telemetry-model.md](references/trace-and-telemetry-model.md) — Trace schema, replay boundaries, and production telemetry
- [references/evals-regression-and-cost-ops.md](references/evals-regression-and-cost-ops.md) — Eval packs, scorecards, release gates, and cost operations
- [references/harness-self-evolution.md](references/harness-self-evolution.md) — Closed-loop harness evolution: three observability pillars, falsifiable-contract edits, evidence and recipe
- [references/openai-codex-rollout-doctor-telemetry.md](references/openai-codex-rollout-doctor-telemetry.md) — OpenAI Codex rollout replay, SQLite mirror, doctor report schema, trace propagation, and metrics
- [references/openai-codex-otel-config.md](references/openai-codex-otel-config.md) — schema lookup step, OTel vs analytics boundary, propagation and cardinality rules
- [references/recovery-trace-events.md](references/recovery-trace-events.md) — Recovery-event taxonomy and trace requirements for interrupted or resumed agent work

### Templates

- [assets/templates/golden-task.schema.json](assets/templates/golden-task.schema.json) — JSON Schema for one golden-task regression-eval entry
### Data

- [`data/sources.json`](data/sources.json) — Primary docs and implementation references for coding-agent observability and evals

### Related Skills

- [`../ai-evals/SKILL.md`](../ai-evals/SKILL.md) - Judge-bias taxonomy, pairwise/flake control, and threshold derivation for the golden-task graders here
- [`../ai-coding-agents/SKILL.md`](../ai-coding-agents/SKILL.md)
- [`../ai-coding-agents-state/SKILL.md`](../ai-coding-agents-state/SKILL.md)
- [`../ai-coding-agents-runtime-core/SKILL.md`](../ai-coding-agents-runtime-core/SKILL.md)
- [`../qa-agent-testing/SKILL.md`](../qa-agent-testing/SKILL.md)

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
