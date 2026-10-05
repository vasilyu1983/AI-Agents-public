# Harness Self-Evolution (Closed Loop)

Static evals tell you *whether* a build regressed. A harness-evolution loop uses the same trace and eval substrate to *improve the harness itself* — automatically, with attribution. As of 2026 this is the frontier addition to coding-agent observability: the eval corpus stops being only a release gate and becomes the optimizer's reward signal.

Source: *Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses*, arXiv [2604.25850](https://arxiv.org/abs/2604.25850) (2026-04). Empirical claims below are from that paper and one cross-runtime reference design (*Building Effective AI Coding Agents for the Terminal*, arXiv [2603.05344](https://arxiv.org/abs/2603.05344)). Verify numbers and method names against the current papers before treating them as fixed fact.

## Why this belongs in the observability skill

The harness — tool wiring, middleware, memory, retry/verification scaffolding, *not* the system prompt — is now the dominant lever on coding-agent performance. Manual harness tuning fails for three reasons the rest of this skill already names elsewhere: heterogeneous edit surface, trajectory volume that buries signal, and edits whose effect is hard to attribute. Those are observability problems. Solve them and harness improvement becomes a closed loop on top of the trace + eval datasets you already built.

## The three observability pillars

A self-evolution loop needs three distinct observability surfaces. Missing any one collapses it back into trial-and-error:

- **Component observability** — every editable harness component has a file-level, revertible representation. The action space is explicit, not implicit in code. No component representation → the optimizer cannot reason about *what* it changed or roll it back.
- **Experience observability** — millions of raw trajectory tokens are distilled into a layered, drill-down evidence corpus an evolving agent can actually consume. This is the eval/trace store from this skill, re-shaped for an *agent* reader, not a human dashboard.
- **Decision observability** — every edit is paired with a self-declared prediction, later verified against the next round's task-level outcomes. This converts each edit into a falsifiable contract and is what makes effects attributable.

## The loop

```text
baseline harness + eval corpus
  -> agent proposes a harness edit (component observability: explicit, revertible)
  -> agent self-declares a prediction about its effect (decision observability)
  -> run eval pack; distill trajectories to evidence (experience observability)
  -> verify prediction against task-level outcomes
       prediction held    -> keep edit, fold into baseline
       prediction falsified -> revert; the failed contract is itself signal
  -> repeat
```

The falsifiable-contract step is the load-bearing one. An optimizer that edits without a pre-declared, verified prediction is doing benchmark-chasing, not attribution — and will overfit the corpus.

## Evidence

- Terminal-Bench 2 pass@1: **69.7% → 77.0%** over **ten** AHE iterations; surpasses the **human-designed Codex-CLI harness (71.9%)** and the ACE / TF-GRPO self-evolving baselines.
- Transfer: the frozen evolved harness reaches top aggregate success on **SWE-bench-verified using ~12% fewer tokens than the seed** harness, with no re-evolution.
- Cross-model-family: **+5.1 to +10.1 pp** on Terminal-Bench 2 across three other model families.
- Ablation: gains come from **tools, middleware, and long-term memory — not the system prompt.** Structural, not prose-level, transfer. This is why prompt-only "agent tuning" plateaus.

## Pattern / Anti-pattern / Recipe

- **Pattern:** treat the eval corpus as an optimizer reward signal, not only a release gate. Make every harness component file-level and revertible, require a pre-declared prediction per edit, and verify it against the next eval round before the edit is kept.
- **Anti-pattern:** "self-improving agent" that edits the system prompt in a loop with no component model and no pre-declared prediction. It overfits the benchmark, the gains do not transfer, and you cannot attribute or revert a regression.
- **Recipe:**
  1. Reuse the existing trace store (this skill's `trace-and-telemetry-model`) as the experience-observability source; add a distillation pass that produces an agent-readable evidence corpus, not a human dashboard.
  2. Represent each editable harness component as a tracked file with a revert path (component observability).
  3. Require every proposed edit to carry a written predicted effect on a named eval slice (decision observability).
  4. Gate keep/revert on the existing release-gate machinery — the prediction must clear the same baseline-delta thresholds used for human-authored changes.
  5. Keep the evolution loop and the production release gate as **separate datasets** (Core Invariant of this skill): the optimizer must never train on production telemetry directly.

## Boundary

This is an *optional, advanced* layer. The Minimal Viable Version of this skill (canonical trace ID, replay-safe storage, one golden pack, one release gate) ships without it. Add the loop only once the eval corpus is trustworthy and versioned — an evolution loop on a noisy corpus optimizes the noise.

---

*Thank you to arXiv for use of its open access interoperability.*
