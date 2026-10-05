---
name: ai-evals
description: "Designs trustworthy LLM, agent, responsible-AI, and multimodal evaluations. Use when measuring quality, fairness, privacy, grounding, safety, or judge reliability."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.8"
last_validated: 2026-08-24
---

# AI Evaluation and Fine-Tuning Methodology Skill

Use this skill to calibrate graders, derive release gates, and compare evaluation
or adaptation methods. Domain skills own what to measure; this skill owns the
measurement controls. Training loss is telemetry; held-out behavior determines
whether an adaptation improved the system.

## Quick Reference

| Task | Read or Run | Outcome |
|------|-------------|---------|
| Build a (question, ideal-answer) set and tune it | `references/dataset-construction.md` | Sourcing, ideal-answer authoring, run→compare→tune loop, robustness slice by perturbing memorized cases |
| Compose an eval dataset | `references/eval-dataset-design.md` | Task distribution, difficulty, sampling, annotation, versioning, contamination, bias audits, golden vs dynamic sets |
| Stop a judge from rating its own output high | `references/llm-judge-bias.md` | Self-preference, position, length, verbosity controls |
| Pick / wire an eval framework | `references/framework-integration.md` | inspect-ai, lighteval, Ragas, DeepEval, promptfoo, Braintrust integration snippets + when to use each |
| Choose metrics and a pass threshold defensibly | `references/threshold-derivation.md` | Metric set by use case with direction and action-if-fails; derive thresholds from a labeled set; inter-rater agreement; gate design |
| Stop flaky runs reading as regressions | `references/flake-and-reproducibility.md` | pass@k vs pass^k, seeds, temperature, quarantine, contamination/leakage, system-benchmark hazards (hardware lottery, thermal/background load, unreported CIs) |
| Decide if "A beats B" is real, size the set | `references/eval-statistics.md` | Bootstrap CIs, McNemar, power/MDE sizing, FDR, variance reduction |
| Get maximum from an LLM | `references/llm-optimization-technique-map.md` | Technique ladder across prompts, data, RAG/tools, test-time compute, SFT, preference/RFT, PEFT, distillation; measured case where a confidence scorer scored below no scorer |
| Decide whether and how to fine-tune | `references/fine-tuning-eval-loop.md` | Prompt/RAG/tool baseline, SFT vs preference/RFT vs PEFT, split hygiene, promotion gates |
| Evaluate on live/production traffic | `references/online-production-eval.md` | Offline-online correlation, A/B+guardrails, shadow/canary, drift, regression replay, HITL |
| Turn user behavior into eval and preference data | `references/conversational-feedback-signals.md` | Implicit NL signals, action signals, edit→preference pairs, collection timing, feedback biases |
| Evaluate refusals, jailbreaks, harm | `references/safety-redteam-eval.md` | Over/under-refusal, ASR per attack family, injection, harm rubrics, robustness |
| Evaluate responsible or multimodal AI | `references/responsible-multimodal-evaluation.md` | Intersectional fairness, privacy/memorization/poisoning, oversight/appeals, provenance, grounding, diffusion, multimodal attacks, latency/cost |
| Go beyond one judge | `references/advanced-judging.md` | Juries, fine-tuned judges, CoT/probability scoring, calibration (kappa/ECE), agentic reward, human-vs-judge routing |
| Evaluate a retrieval, KB, or memory system | `references/retrieval-and-memory-eval.md` | Independent held-out set, slice floors, Wilson CIs, confident-wrong rate, per-stage tests, change-triggered regression gate, state-maintenance acceptance tests, cross-tenant canaries, learned-memory baselines, vendor benchmark claims |
| Measure whether memory skills improve an agent | [memory-skills-ablation](references/memory-skills-ablation.md) | Validate paired skills-on/off outcomes, complete safety slices, configuration parity and measured telemetry; export descriptive paired results |
| Measure hallucination | `references/hallucination-eval.md` | Taxonomy, claim-level scoring, abstention next to hallucination rate, reference-free triage |

## Scope Boundaries (Use These Skills for Depth)

- **Domain metrics for retrieval** (nDCG/MRR/recall, faithfulness) -> [ai-rag](../ai-rag/SKILL.md)
- **Agent harness: tool/trace grading, refusal/red-team packs, regression suites, CI status model** -> [qa-agent-testing](../qa-agent-testing/SKILL.md)
- **Coding-agent golden tasks, trace replay, cost ops** -> [ai-coding-agents-observability-evals](../ai-coding-agents-observability-evals/SKILL.md)
- **Running benchmark harnesses on Hub models** -> use the `huggingface-skills:` plugin (external)
- **Prompt CI/CD and structured output contracts** -> [ai-prompt-engineering](../ai-prompt-engineering/SKILL.md)
- **Model selection** -> [ai-architecture-advisor](../ai-architecture-advisor/SKILL.md);
  **serving and quantization** -> [ai-llm-inference](../ai-llm-inference/SKILL.md);
  **API cost economics** -> [ops-cost-optimization](../ops-cost-optimization/SKILL.md)

## Workflow

1. **Transform the vague ask into a verifiable goal.** "Is it good?" is not
   gradeable. Ask: which case would fail first if the requirement reverted?
2. **Build the dataset before the grader.** Source real questions, author ideal
   answers from the system's allowed context, and plan the run→compare→tune loop
   — see `references/dataset-construction.md`. No dataset, no eval.
3. **Pick the cheapest grader that works.** Deterministic check > LLM judge >
   human. Reserve the LLM judge for what code cannot decide (Rule 5: use the
   model only for judgment calls).
4. **If using an LLM judge, control its bias** before trusting any number — see
   `references/llm-judge-bias.md`. Judge bias can confound quality with surface features. When one judge isn't enough (high stakes, weak
   agreement, open-ended), escalate to juries / fine-tuned judges / calibrated
   scoring — see `references/advanced-judging.md`.
5. **Control flake and leakage** with repeated trials (pass^k for reliability
   gates, pass@k only for capability), low judge temperature, seed
   pinning, and held-out testsets — see `references/flake-and-reproducibility.md`.
6. **Derive thresholds from a labeled calibration set**, not intuition or copied
   targets — see `references/threshold-derivation.md`. **Size the gating set and
   judge "A beats B" with statistics** (bootstrap CIs, McNemar, power/MDE, FDR) —
  see `references/eval-statistics.md`. For frozen paired results, run
  `python3 scripts/analyze_paired_results.py results.csv --estimand unit_mean`;
  declare whether units or clusters define the target population first. A population-level superiority claim needs design-compatible uncertainty;
  exact fixed-suite differences remain descriptive evidence.
7. **Only fine-tune after the baseline has earned it.** Compare prompt/RAG/tool
   fixes first, then choose SFT for imitation/style/format/tool-call behavior,
   preference/RFT for rubric-scored reasoning or tradeoffs, and PEFT/LoRA/QLoRA
   when adapting an open model under compute or deployment constraints — see
   `references/fine-tuning-eval-loop.md`. Training loss is telemetry; held-out
   behavior is the verdict.
8. **Apply the full optimization ladder, not one pet method.** For maximum LLM
   performance, evaluate cheap prompt/context/tool fixes, then inference-time
   methods (self-consistency, best-of-N, rerank/verify/refine), then data/SFT,
   preference/RFT/RLVR, PEFT, and distillation as the evidence warrants — see
   `references/llm-optimization-technique-map.md`. Each technique gets its own
   failure mode and gate.
9. **Gate loudly.** A gate that passes while silently skipping cases is a
   failure dressed as success (Rule 12: fail loud). Report skipped/quarantined
   cases in the gate output.
10. **Extend past the offline gate where the system warrants it.** Add
   safety/red-team evaluation (refusal precision/recall, jailbreak ASR,
   injection, harm rubrics) — see `references/safety-redteam-eval.md` — and, once
   in production, online evaluation (offline-online correlation, A/B with
   guardrails, drift, regression replay) — see `references/online-production-eval.md`.
   The offline gate is a filter; production is the verdict.

## Core Principles

- **The judge is a model with failure modes.** Treat its scores as one
  calibrated input, never as ground truth.
- **Judge independence needs evidence.** Prefer a different judge model and
  calibrate against human labels and planted failures. A different family reduces
  one self-preference risk; it does not establish an unbiased grader.
- **Behavior, not plausibility.** Rubrics that reward "looks good" reward length
  and confidence. Pin rubrics to verifiable behavior.
- **No threshold without a labeled set.** A copied target (">95%") is a guess
  until validated on your own distribution.
- **No fine-tune without a baseline and a holdout.** A tuned model that beats no
  prompt/RAG/tool baseline, or only wins on the training/dev set, has not earned
  release.
- **No "maximum performance" without a technique ladder.** The best result often
  comes from composition: cleaner data + stronger retrieval/tool contracts +
  calibrated judge + small test-time search + selective post-training. Test the
  cheapest credible lift before moving weights.
- **Optimize behavior, not hidden knowledge.** Fine-tune for stable formatting,
  domain style, tool-use patterns, rubric-following, or compact specialized
  behavior. Use retrieval/context for facts that change or must be cited.
- **Locate variability before changing the gate.** Regrade frozen outputs to
  separate judge instability from system unreliability; keep real stochastic
  failures in the reliability denominator.
- **Held-out or it's contaminated.** If tuning ever saw the eval cases, the
  scores are inflated.
- **Check that the proxy still tracks the outcome.** Tuning to a metric can
  weaken its relationship with user outcomes. Re-anchor it against fresh human
  labels or production evidence when the model, grader, or traffic changes.
- **Match uncertainty to the claim.** Population-level pass rates, win rates,
  and judge-human agreement need design-compatible uncertainty. Exact counts
  over a fixed deterministic suite describe that suite and need their
  denominator and limits; do not invent sampling intervals for them. See
  `references/eval-statistics.md`.

- Eval framework APIs (inspect-ai, lighteval, Ragas, DeepEval, promptfoo,
  Braintrust) change across releases. Verify current API and version against
  official docs before recommending a specific call or flag.
- Optimization-method papers from arXiv are often preprint-only and
  benchmark-sensitive. Treat unreplicated methods as `validate`, not `promote`,
  until they beat a strong local baseline with cost/latency/safety gates.
- Judge-bias findings (position, length, self-preference) are well-replicated,
  but their magnitudes (and for length, the direction) are judge- and
  prompt-dependent — re-measure on your own setup; do not quote a fixed number as universal.
- Fine-tuned-judge models (Prometheus, JudgeLM, and successors) and jailbreak
  attack/defense results move fast — verify the current model, license, and
  benchmark-agreement claims before recommending a specific judge or asserting a
  model is robust to a given attack family.
- Indirect prompt injection is a leading agentic attack class; treat any
  "the agent is safe against injection" claim as requiring fresh adaptive testing.
- Statistics methods (bootstrap, McNemar, FDR, power/MDE) are stable, but verify
  the exact API (scipy/statsmodels) before copying a call.

## Release Decision Gate

### Select foundations only when they change the eval decision

- If a proxy score is being interpreted as quality, trust, fairness, or another
  construct, or compared across populations or grader versions, use
  [measurement theory](../foundations-measurement-theory/SKILL.md). Return the
  construct, observed proxy, interpretation evidence, comparability limits,
  and missing validation. Skip this audit for a routine execution of an already
  documented instrument with unchanged interpretation and population.
- If uncertainty, dependent repeats/clusters, multiple comparisons, or repeated
  stopping can change a conclusion, use
  [statistical inference](../foundations-statistical-inference/SKILL.md). Return
  the estimand, independent unit, interval method and assumptions, and the
  multiplicity/stopping rule. Skip inference for reporting exact outcomes of a
  fixed deterministic fixture suite without a population claim; report its
  denominator and scope instead. Neither foundation substitutes for this skill's
  dataset, grader controls, or release decision.

Write the release rule before scoring: required tasks and slices, minimum acceptable effect, uncertainty method, regression budget, and handling for grader errors or missing results. A candidate passes only when every blocking slice is present and the predeclared decision rule clears. Learned, model, heuristic, and human graders must pass planted-good and planted-bad controls that detect calibration drift; deterministic exact-match, schema, executable-test, and invariant graders instead need versioned implementations with relevant positive and negative fixtures. Missing denominators, stale fingerprints, failed grader controls, or an unavailable judge produce `inconclusive`, never an implicit pass. For memory-skill effectiveness, use the [paired ablation procedure](references/memory-skills-ablation.md); public development fixtures validate the harness, while an independently frozen set is required for a held-out claim. Keep measured results separate from the release recommendation.

## Known Traps

- Grading an agent with the same model that produced the output (self-preference)
- Comparing two candidates in fixed order and trusting the winner (position bias)
- Copying a `>95%` threshold from a blog without validating it on your data
- One judge call per request with no cheap deterministic pre-filter (cost blowup)
- Quarantining genuine stochastic system failures until the gate becomes green
- Generating a synthetic testset from the same docs used to tune the system
- Reporting a builder-written eval as held-out for a retrieval/KB/memory system, or
  letting the eval fall back silently when the index is stale (see
  `references/retrieval-and-memory-eval.md`)
- Reporting "all passed" when some cases were skipped or errored (silent success)
- Claiming "A beats B" from a point estimate with no confidence interval or test
- Gating a small regression on a set far too small to detect it (no power check)
- Tuning safety to block harm without a benign set, so the model over-refuses
- Trusting a seed for reproducibility through a hosted API that isn't deterministic
- Fine-tuning because the prompt is messy, the retrieval is broken, or the tool
  contract is ambiguous
- Declaring the fine-tune better from training loss, validation loss, or one
  cherry-picked demo instead of a paired held-out eval with CIs
- Letting the training set, grader calibration set, and release gate share cases
- Training a judge or reward model on labels produced only by the same model
  family it will later grade

## Navigation

Resources:

- [references/dataset-construction.md](references/dataset-construction.md) - Sourcing questions, authoring ideal answers, run→compare→tune loop
- [references/eval-dataset-design.md](references/eval-dataset-design.md) - Dataset composition: distribution, difficulty, sampling, annotation, versioning, contamination, bias, golden vs dynamic
- [references/llm-judge-bias.md](references/llm-judge-bias.md) - Judge bias taxonomy and controls
- [references/framework-integration.md](references/framework-integration.md) - Framework selection and integration snippets
- [references/threshold-derivation.md](references/threshold-derivation.md) - Metric set by use case, deriving thresholds and gates from labeled data
- [references/flake-and-reproducibility.md](references/flake-and-reproducibility.md) - Flake, seeds, contamination, leakage, system-benchmark hazards
- [references/eval-statistics.md](references/eval-statistics.md) - Paired cluster bootstrap workflow and analyzer, McNemar, power/MDE, FDR, variance reduction
- [references/llm-optimization-technique-map.md](references/llm-optimization-technique-map.md) - Maximum-performance technique ladder and eval gates
- [references/fine-tuning-eval-loop.md](references/fine-tuning-eval-loop.md) - Eval-first fine-tuning decisions, SFT/preference/RFT/PEFT selection, split hygiene, promotion gates
- [references/online-production-eval.md](references/online-production-eval.md) - Offline-online correlation, A/B+guardrails, drift, replay, HITL
- [references/conversational-feedback-signals.md](references/conversational-feedback-signals.md) - Implicit/action user-feedback taxonomy, edit→preference pairs, collection timing, feedback biases
- [references/safety-redteam-eval.md](references/safety-redteam-eval.md) - Refusal precision/recall, jailbreak/injection, harm rubrics, robustness
- [references/advanced-judging.md](references/advanced-judging.md) - Juries, fine-tuned judges, scoring methods, calibration, human-vs-judge routing, agentic reward
- [references/retrieval-and-memory-eval.md](references/retrieval-and-memory-eval.md) - Independent held-out sets, slice floors, per-stage pipeline tests, change-triggered regression gate, exact-state scoring
- [references/hallucination-eval.md](references/hallucination-eval.md) - Hallucination taxonomy, claim-level metrics, abstention, judge prompt, reference-free triage
- [references/responsible-multimodal-evaluation.md](references/responsible-multimodal-evaluation.md) - Responsible-AI measurement and multimodal grounding, diffusion, safety/red-team, latency, and cost gates
- [scripts/prompt_eval_runner.py](scripts/prompt_eval_runner.py) - Offline regression check of pre-collected outputs in a JSONL suite against `expected_substrings` and/or `expected_schema`. A record with no assertions fails; malformed assertion fields, non-JSON numeric constants, and duplicate case IDs exit 2. It calls no model API and measures nothing statistical; compare two variants with `scripts/analyze_paired_results.py`.
- [data/sources.json](data/sources.json) - Sources to verify against

Related skills:

- [ai-llm](../ai-llm/SKILL.md), [ai-rag](../ai-rag/SKILL.md), [ai-coding-agents-observability-evals](../ai-coding-agents-observability-evals/SKILL.md), [qa-agent-testing](../qa-agent-testing/SKILL.md)

## Learnings Loop

Consult `learnings.consolidated.md` for relevant prior decisions or pitfalls;
open `learnings.md` only when their history is needed. Skip both when unrelated
to the task. After applying it, append one dated bullet to
`learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py` if you
hit a pattern, mistake, or surprising fact. Do not modify `SKILL.md` itself.
