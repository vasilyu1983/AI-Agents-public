# How-to-Apply Recipes

For each method shape, a playbook for going from "I read the paper" to "the idea is in my codebase or design".

## Table of Contents

- [Recipe Format](#recipe-format)
- [Recipes per Method Shape](#recipes-per-method-shape)
- [Validation-Before-Adoption Checklist](#validation-before-adoption-checklist)
- [Kill Criteria Patterns](#kill-criteria-patterns)

## Recipe Format

Each recipe has:
- **Goal**: what success looks like
- **Prerequisites**: what you need before starting
- **Steps**: concrete sequence
- **First measurement**: the earliest signal that tells you "keep going" or "stop"
- **Common pitfalls**: stuff that wastes a week if you don't know it

## Recipes per Method Shape

### `prompting-pattern`

**Goal:** Run the new pattern against your existing eval set and beat your current baseline by ≥X%.

**Prerequisites:**
- A frozen eval set with at least 50 items.
- A current-baseline metric you trust.
- Access to a model the pattern was demonstrated on (or a justified substitute).

**Steps:**
1. Implement the prompt template literally as the paper describes. Don't "improve" it on first pass.
2. Run on a sample of 20 eval items. Inspect outputs by hand.
3. Compare to your current prompt on the same 20 items.
4. If signal is positive on the sample, run the full eval.
5. If positive on the full eval, ablate: remove parts of the prompt to find the active ingredient.
6. Lock in the minimal viable version, not the paper's full version.

**First measurement:** After step 3, look at the 20 samples. If you can't see a qualitative difference, the metric difference (if any) is probably noise.

**Common pitfalls:**
- Adopting the full prompt template when only one phrase mattered.
- Forgetting to control for prompt length (longer prompts can win for unrelated reasons).
- Using a different model than the paper without justifying the swap.

### `architecture-tweak`

**Goal:** Implement a small, isolated version of the tweak and measure on a controlled training run.

**Prerequisites:**
- A reference implementation you trust (PyTorch / JAX / etc.).
- Compute budget for at least one A/B controlled run.
- A frozen eval suite that can detect the size of the claimed improvement.

**Steps:**
1. Start from your current architecture; isolate the smallest possible change.
2. If the paper provides reference code, port the tweak only — not the full pipeline.
3. Run a smoke test (1k steps) to confirm the model trains and loss decreases.
4. Run a controlled comparison (same data, same optimizer, same seed schedule) for the smallest scale that can detect the claimed effect.
5. Measure on your eval suite, not just the paper's.

**First measurement:** After step 3, the smoke test must train without instabilities. If loss spikes or NaNs appear, debugging will eat the rest of the lift estimate.

**Common pitfalls:**
- Porting too much of the paper's pipeline (changing N things at once means you can't isolate the tweak's contribution).
- Using a much smaller scale than the paper and concluding "doesn't work" — many architecture tweaks need scale to manifest.
- Skipping the seed-variance check — gains within seed-variance are noise.

### `training-recipe`

**Goal:** Run the training recipe on your data and measure quality + cost vs. your current recipe.

**Prerequisites:**
- A reproducible training pipeline.
- Compute budget for at least 2 controlled runs.
- A meaningful eval signal that doesn't reward training-set memorization.

**Steps:**
1. Start with the recipe applied at small scale (e.g., 1B params if paper uses 70B).
2. Hold data fixed; swap only the recipe.
3. Track loss curves, eval scores, and total compute side-by-side.
4. If quality matches at small scale, scale up only if compute budget justifies.
5. If quality drops at small scale, the recipe may need scale — try one tier larger before discarding.

**First measurement:** After step 1, the loss curve shape should match the paper's (within reason). If shape is qualitatively different, something in the implementation is wrong.

**Common pitfalls:**
- Comparing total quality without controlling for total compute.
- Skipping the "does it work at small scale at all?" check before committing budget.
- Ignoring data-quality interactions (some recipes only help on noisy data).

### `evaluation-method`

**Goal:** Run the new eval against models you've already evaluated and compare its rankings.

**Prerequisites:**
- A set of models with known relative quality.
- Implementation of the eval (or willingness to build it).

**Steps:**
1. Implement the eval on a small set (e.g., 3 models you know rankings for).
2. If the new eval ranks them consistently with what you know, the eval is at least sensible.
3. Run on a wider model set; check correlation with existing evals.
4. Identify cases where the new eval disagrees with existing evals — these are the eval's actual contribution.
5. Decide whether to add the eval to your suite, replace an existing eval, or use it for a specific dimension.

**First measurement:** After step 1, sanity check. If the new eval ranks a known weaker model higher, the eval is broken or measuring something orthogonal.

**Common pitfalls:**
- Treating the new eval as ground truth without correlation analysis.
- Using LLM-as-judge evals without checking judge model bias.
- Not testing on adversarial inputs designed to fool the eval.

### `data-construction-recipe`

**Goal:** Generate a small dataset using the recipe and check quality before scaling.

**Prerequisites:**
- A clear definition of "good" for the target dataset.
- A way to evaluate generated data (manual review or downstream eval).

**Steps:**
1. Generate 100 examples with the recipe.
2. Manually review for quality, diversity, and failure modes.
3. If quality is acceptable, scale to a downstream-eval-relevant size.
4. Train on the generated data and measure downstream effect.

**First measurement:** After step 2, if you wouldn't keep these 100 examples, scaling won't fix the problem.

**Common pitfalls:**
- Generating millions of low-quality examples and assuming volume compensates.
- Skipping the manual review and trusting the recipe's filtering.
- Not measuring distributional drift from your existing training data.

### `inference-time-method`

**Goal:** Apply the method at inference, measure quality + latency + cost vs. baseline.

**Prerequisites:**
- A baseline inference setup with measured latency and quality.
- A small sample set to A/B on.

**Steps:**
1. Implement the method on top of your existing inference path.
2. Run on 20 samples, compare quality, latency, cost.
3. If positive, run on full eval; track cost-per-improvement-point.
4. Decide where to enable: always-on, opportunistic, or only on hard inputs.

**First measurement:** After step 2, latency cost and cost-per-call. If method is 5× slower for 2% improvement, it's a niche tool, not always-on.

**Common pitfalls:**
- Reporting quality gain without latency/cost.
- Ignoring per-input variance — some inputs benefit more than others.
- Not implementing the obvious fallback (skip the method on inputs where the baseline is already confident).

### `system-design-pattern`

**Goal:** Apply the pattern to one component, measure end-to-end effect.

**Prerequisites:**
- A clear scope: which component is changing.
- An end-to-end metric that captures the system's purpose.

**Steps:**
1. Sketch the design change on paper. Identify what stays the same.
2. Implement in a flag-gated branch.
3. Run end-to-end on a representative workload.
4. Measure end-to-end metric, not just component metric.
5. Roll out behind a flag with rollback ready.

**First measurement:** After step 3, the end-to-end metric. Component-level wins that don't show up end-to-end aren't wins.

**Common pitfalls:**
- Optimizing the component's metric while degrading another component.
- Not flag-gating; rollback becomes painful.
- Ignoring operational complexity costs (more components = more failure modes).

### `theoretical-bound`

**Goal:** Use the bound to inform design decisions; verify the bound's assumptions match your situation.

**Prerequisites:**
- Understanding of the assumptions the bound rests on.

**Steps:**
1. Identify the assumption set (e.g., bounded model class, specific loss, i.i.d. data).
2. Check whether your situation satisfies them.
3. If assumptions hold, use the bound to set design constraints (e.g., "no method in this class can do better than X").
4. If assumptions break, the bound informs but doesn't constrain.

**First measurement:** Step 2. If assumptions fail, don't waste time on the bound.

**Common pitfalls:**
- Treating the bound as universal when it's conditional.
- Skipping the assumption check; theoretical results that look strong often have load-bearing assumptions.

### `negative-result`

**Goal:** Avoid wasting time on methods the negative result rules out.

**Prerequisites:** Understanding the scope of the negative claim.

**Steps:**
1. Identify what the negative result actually claims (and the scope).
2. Cross-check against your planned approach.
3. If your approach falls in scope, drop it. If it falls outside scope, proceed but log the rationale.
4. If it falls in scope but you have reason to think the negative result missed a case, that's a research project, not adoption.

**First measurement:** Step 1. Many "negative results" are scoped narrowly; the headline often overstates the scope.

**Common pitfalls:**
- Discarding a method based on a negative result that doesn't apply to your case.
- Believing a negative result blindly without checking the methodology that produced it.

## Validation-Before-Adoption Checklist

Before any idea moves from `validate` to `adopted`:

- [ ] Reproduced on a smoke-test scale (or shown impractical)
- [ ] Measured against your eval, not just the paper's
- [ ] Cost / latency / compute trade-off measured
- [ ] Failure modes identified
- [ ] Rollback path defined
- [ ] Owner identified

## Kill Criteria Patterns

When to stop pursuing an idea:

- **Smoke test fails or shows no signal** after recipe-prescribed steps.
- **Cost / quality ratio is worse than current** by a margin you wouldn't accept on a vendor pitch.
- **Required scale or data is unavailable** and the idea doesn't degrade gracefully.
- **A trap fires that you missed earlier** (especially Trap 11 or 12).
- **Time spent exceeds 2× the lift estimate** without convergent signal — switch off, write up the negative finding, move on.
