---
name: ai-coding-agents-observability-evals
description: "Designs coding-agent observability and evals. Use when measuring traces, replay, checkpoint lineage, quality trajectories, tool grading, regression, or cost."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-08-21
---

# AI Coding Agents Observability And Evals

Use this skill to design or review the feedback loop around a coding-agent runtime: traces, replayable transcripts, eval packs, regression gates, tool-call grading, latency and cost accounting, and production failure triage.

This skill covers how you operate a coding-agent product after the core runtime exists. It does not replace the runtime skills themselves.

## ASCII Flow

```text
agent session
  |
  v
trace events
  prompts + model turns + tool calls + permissions + file diffs + costs
  |
  v
replayable transcript
  stable IDs + redaction + source/runtime correlation
  |
  v
eval pack
  golden tasks + graders + regression gates + cost/latency budgets
  |
  v
release decision
  pass | investigate | rollback | update eval coverage
```

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| What should the trace and telemetry model include? | [`references/trace-and-telemetry-model.md`](references/trace-and-telemetry-model.md) | Durable trace schema, session correlation, event stages, and replay boundaries |
| How should evals, regressions, and cost controls work? | [`references/evals-regression-and-cost-ops.md`](references/evals-regression-and-cost-ops.md) | Golden tasks, iterative self-extension packs, trajectory scorecards, and cost-aware release gates |
| How do I use the eval/trace substrate to improve the harness itself? | [`references/harness-self-evolution.md`](references/harness-self-evolution.md) | Closed-loop harness evolution: three observability pillars, falsifiable-contract edits, attribution |
| How does OpenAI Codex combine rollout replay, SQLite state, doctor reports, and telemetry? | [`references/openai-codex-rollout-doctor-telemetry.md`](references/openai-codex-rollout-doctor-telemetry.md) | Replay artifacts, rebuildable state indexes, redacted diagnostics, W3C traces, token metrics |
| How does Codex wire OTel exporters and what analytics events exist? | [`references/openai-codex-otel-config.md`](references/openai-codex-otel-config.md) | OtelSettings TOML schema, exporter selection, W3C tracestate, contrast with proprietary analytics events |

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
| Session persistence and transcript restore | [`../ai-coding-agents-sessions/SKILL.md`](../ai-coding-agents-sessions/SKILL.md) |
| Tool runtime design | [`../ai-coding-agents-tools/SKILL.md`](../ai-coding-agents-tools/SKILL.md) |
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

- Keep one canonical trace ID across the entire session lifecycle.
- Preserve causal order for tool calls, approvals, worker messages, and verification passes.
- Keep event ordering monotonic within a session even when log sinks or transports are asynchronous.
- Store enough normalized state to debug a run without depending on transient UI rendering.
- Score traces at multiple layers: final answer, tool behavior, and workflow correctness.
- Preserve checkpoint and workspace lineage for iterative evals; a final snapshot cannot explain when extensibility was lost.
- Track token and cost usage per turn and per subsystem, not only per session total.
- Use eval results to block releases when quality or cost drift exceeds explicit thresholds.
- Hash or redact user-identifying plugin or extension data before it becomes telemetry dimensions.

## Scratch-Rebuild Coverage

- Coverage strength:
  strong for trace correlation, replay-safe storage, multi-layer grading, release-gate framing, and the need to trace recovery-class events
- Missing for faithful reproduction:
  low-cardinality telemetry discipline, reconnect and recovery event classes, approval-cancel telemetry, task-budget-versus-token-budget accounting, and incident-first trace queries need more explicit treatment
- Required additions:
  document trace events for reconnect, cancellation, fallback activation, recovery class, worker escalation, and plugin lifecycle changes, plus the eval rubric fields that map those events back to product quality without exploding metric cardinality

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
- A closed-loop **harness self-evolution** layer that turns the eval corpus into an optimizer signal (see [`references/harness-self-evolution.md`](references/harness-self-evolution.md)) — advanced, not MVP.

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

SlopCodeBench's Python experiments found that anti-slop and plan-first prompts improved initial structural quality, but did not halt the degradation slope or consistently improve correctness. Prompt-only controls are therefore insufficient: keep the trajectory pack as the control surface and treat prompt changes as candidates to evaluate. Use [`../qa-agent-testing/SKILL.md`](../qa-agent-testing/SKILL.md) for the detailed carried-workspace benchmark protocol and [`../software-clean-code-standard/SKILL.md`](../software-clean-code-standard/SKILL.md) for structural-erosion and verbosity definitions; this skill owns their telemetry and release-gate integration, not their formulas.

## OTel gen_ai Semantic Conventions

The OpenTelemetry GenAI spec (status: Development, unchanged since 2026-05) defines a standard schema for agent telemetry. Key attributes:

- `gen_ai.operation.name` — operation identifier on the root span (e.g., `invoke_agent`, `create_agent`, `execute_tool`)
- `gen_ai.agent.name`, `gen_ai.agent.id`, `gen_ai.agent.version` — agent identity
- `gen_ai.tool.name` / `gen_ai.tool.call.id` — child spans for tool invocations
- `gen_ai.conversation.id` — cross-turn conversation correlation

**Repo-split caveat (verify before citing a URL):** as of mid-2026 these conventions moved out of the main `open-telemetry/semantic-conventions` repo into a dedicated `open-telemetry/semantic-conventions-genai` repo. The old `opentelemetry.io/docs/specs/semconv/gen-ai/*` pages now render "moved" notices, and the attribute registry marks the gen_ai.* entries as deprecated-in-place (relocated, not removed — the names above are still current). Treat any bookmarked gen-ai-spans URL as unstable; re-resolve from the dedicated repo before you cite it in a runbook or dashboard link.

**Experimental status caveat:** These conventions require `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` to activate in most SDK implementations. A repo split this late in the spec's life is itself a signal — expect further attribute churn through at least end of 2026. Design instrumentation against the attribute names, but gate production dashboards and alerting thresholds on a version-pinned snapshot, not "whatever the SDK emits today," so an upstream rename doesn't silently blank a panel.

**Contrast with Codex proprietary crate:** Codex ships a bespoke `codex-rs/otel` crate (OtelSettings TOML, OtelExporter variants, W3C tracestate propagation) that predates the gen_ai semconv. The proprietary crate maps to the same conceptual slots but uses different attribute names and has no gen_ai.tool.call.id equivalent. When building cross-runtime dashboards, normalize to gen_ai semconv attributes and treat the Codex-proprietary shape as a source adapter.

**Responses API cache-hit telemetry:** The OpenAI Responses API achieves 40-80% better cache utilization than Chat Completions in agentic workloads (per OpenAI migration guidance). Cache-hit events are a distinct cost-accounting concern and should be tracked as a separate telemetry dimension from inference cost. Do not aggregate cache hits into generic token-usage metrics; they have different cost multipliers and different debugging value.

## Cross-Platform Patterns (Goose)

Goose is now maintained under AAIF (Linux Foundation; founding contributors Block, Anthropic, OpenAI; transferred April 7, 2026). Repository: `aaif-goose/goose`.

Goose's `evals/` structure (including `open-model-gym/`) plus the `recipe-scanner/` static validator suggest two additions to how this skill frames evals and pre-release gates.

### Named eval harness with versioned model×task matrix

Goose's `open-model-gym/` is an explicit, versioned eval pack targeting open-weight models across a fixed workflow matrix. This is stronger than "we have some regression tests" — it is a named, referenceable benchmark with a stable identity.

- **Pattern:** give your eval corpus a product name, a semantic version, and a published rubric. "Did it pass `open-model-gym v2.1`?" is a more actionable release gate than "did the eval suite pass?"
- **Anti-pattern:** an eval suite that silently changes its task set between releases, so pass-rate deltas are not comparable.
- **Recipe:** publish the eval pack as a versioned artifact. Release notes cite the pack version. Add a pack-version field to eval telemetry so historical pass rates stay interpretable after the pack evolves.

### Static analysis for agent definitions (recipe-scanner)

Goose's `recipe-scanner/` is cargo-deny for YAML workflows — it catches schema violations, undeclared-extension usage, and policy-violating configurations before a recipe is allowed to ship or run. This generalizes beyond recipes to any YAML/JSON artifact your agent consumes: MCP manifests, plugin manifests, eval task definitions, skill frontmatter.

- **Pattern:** every declarative artifact an agent reads should have a static validator. Validation runs in CI, at package, at install, and at runtime-load. Each layer catches different drift.
- **Anti-pattern:** validating only at runtime. Invalid artifacts then reach the user as a cryptic crash instead of a pre-ship error.
- **Recipe:** add a `validate` command to your CLI that runs all static gates: schema conformance, dependency reachability, policy compliance, extension allowlist intersection. Wire it into CI and into the activation path.

## Harness Self-Evolution (Frontier)

Static evals tell you *whether* a build regressed. As of 2026, best-in-class implementations also close the loop: the same trace + eval substrate becomes the reward signal for automatically improving the **harness** (tool wiring, middleware, memory, retry/verification scaffolding — not the system prompt). Observability-driven harness evolution beats human-designed harnesses on Terminal-Bench 2 and transfers frozen to SWE-bench-verified at lower token cost.

This needs three distinct observability surfaces — **component** (every editable harness part is file-level and revertible), **experience** (trajectories distilled into an agent-readable evidence corpus, not a human dashboard), and **decision** (every edit carries a pre-declared prediction verified against the next eval round). The decision pillar — falsifiable contracts per edit — is what separates attributable evolution from benchmark-chasing that overfits the corpus.

Keep this strictly separate from the production release gate (Core Invariant: optimizer never trains on production telemetry), and add it only once the eval corpus is versioned and trustworthy. Full method, the loop, evidence, and the Pattern/Anti-pattern/Recipe are in [`references/harness-self-evolution.md`](references/harness-self-evolution.md).

## Expert Judgment: Where Non-Experts Get This Wrong

These are the calls a strong operator makes differently from a team that just wired up a tracer and a pass/fail suite.

- **A pass-rate number without a confidence interval is not a release gate, it's a coin flip.** A 30-task golden pack moving from 26/30 to 24/30 (87%→80%) looks like a regression but is well within noise for that sample size. Compute a Wilson or Clopper-Pearson interval per task family and require the candidate's lower bound to clear the baseline's, not just the point estimate. Teams that skip this either ship real regressions ("it was only a 3-point dip, could be noise" — and it wasn't) or block good releases on sampling variance. Grow the pack before you trust single-run deltas; below roughly 50 tasks per family, run each task N≥3 times and gate on the mean.
- **Uniform trace sampling throws away the signal you built observability for.** At scale, capturing every session at full fidelity is a cost problem, so teams sample — but uniform sampling keeps the 99% of boring successful runs and drops exactly the failed, escalated, or cancelled sessions that justify the whole pipeline. Sample on outcome, not on request count: capture 100% of failures, escalations, cancellations, and verifier rejections; sample successes at whatever rate the budget allows. This is tail-based sampling keyed on business outcome, not on span duration.
- **`contains`/`excludes` substring checks in a golden task are gameable, and agents will find the gap.** An agent optimized against a static eval pack (by you, by harness self-evolution, or by the model provider's own RL) can learn to satisfy the literal check without satisfying the intent — e.g., adding a docstring containing the word "handles error" without handling the error. Treat any eval pack that has been used as an optimization target for more than a few cycles as partially compromised: rotate a subset of golden tasks, add mutated/adversarial variants, and keep at least one grading path (compiles, tests pass, schema-valid) that is not a substring match.
- **Full-fidelity traces of proprietary source code are a data-residency liability, not just an engineering convenience.** Storing complete file diffs and raw prompts (which routinely embed customer source, secrets in comments, or internal API names) in a central trace store creates an enterprise trust problem the moment a customer asks "where does our code go and who can read it." Decide early whether traces containing file content live in customer-controlled storage/region, get truncated to diff hunks plus hashes, or get a separate, shorter retention window than metadata-only telemetry — retrofitting this after a large customer's security review is far more expensive than designing it in.

## Navigation

### References

- [`references/trace-and-telemetry-model.md`](references/trace-and-telemetry-model.md) — Trace schema, replay boundaries, and production telemetry
- [`references/evals-regression-and-cost-ops.md`](references/evals-regression-and-cost-ops.md) — Eval packs, scorecards, release gates, and cost operations
- [`references/harness-self-evolution.md`](references/harness-self-evolution.md) — Closed-loop harness evolution: three observability pillars, falsifiable-contract edits, evidence and recipe
- [`references/openai-codex-rollout-doctor-telemetry.md`](references/openai-codex-rollout-doctor-telemetry.md) — OpenAI Codex rollout replay, SQLite mirror, doctor report schema, trace propagation, and metrics
- [`references/openai-codex-otel-config.md`](references/openai-codex-otel-config.md) — OtelSettings TOML schema, OtelExporter variants, W3C tracestate members, analytics event contrast
- [`references/recovery-trace-events.md`](references/recovery-trace-events.md) — Recovery-event taxonomy and trace requirements for interrupted or resumed agent work

### Data

- [`data/sources.json`](data/sources.json) — Primary docs and implementation references for coding-agent observability and evals

### Related Skills

- [`../ai-evals/SKILL.md`](../ai-evals/SKILL.md) - Judge-bias taxonomy, pairwise/flake control, and threshold derivation for the golden-task graders here
- [`../ai-coding-agents/SKILL.md`](../ai-coding-agents/SKILL.md)
- [`../ai-coding-agents-sessions/SKILL.md`](../ai-coding-agents-sessions/SKILL.md)
- [`../ai-coding-agents-tools/SKILL.md`](../ai-coding-agents-tools/SKILL.md)
- [`../qa-agent-testing/SKILL.md`](../qa-agent-testing/SKILL.md)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Trace shapes, event names, and replay payloads are product-specific. Preserve the architecture, but verify the target runtime before copying field names directly.
- Evals should reflect the real failure profile of your agent. Do not ship only synthetic tasks or happy-path benchmarks.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
