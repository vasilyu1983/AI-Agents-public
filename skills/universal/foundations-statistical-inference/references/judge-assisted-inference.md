# Judge-assisted inference: PPI and PPI++

Use this reference when many items carry a cheap model label (an LLM judge or classifier) and a few carry a gold human label, and you need a valid interval for the gold-label quantity. Typical questions are "what is the true pass rate?" and "what is the true win rate?" The eval workflow (judge design, bias controls, rubric) belongs to [ai-evals](../../ai-evals/SKILL.md). This file owns only the estimator and its validity conditions.

## Decision rule

| Situation | Use |
|---|---|
| Only judge labels, no gold subset | No valid estimate of the gold quantity. Report the judge score as a judge score. |
| Gold subset only, judge ignored | Classical interval on the gold subset. Valid, but wide. |
| Random gold subset plus a large judge-labelled pool from the same distribution | PPI++ (power-tuned). It is never asymptotically worse than classical. |
| Gold subset chosen by hand, by disagreement, or by "hard cases" | Neither PPI nor the classical interval is valid for the population. Fix the sampling first. |

## Estimator (mean or pass rate)

Notation:

- n gold items, each with a human label Y_i and a judge label f_i.
- N unlabelled items, each with only a judge label f̃_j.

The estimators:

- **Classical:** θ̂ = mean(Y).
- **PPI (λ = 1):** θ̂ = mean(f̃) + [mean(Y) − mean(f)]. The bracket is the *rectifier*: the judge's measured bias on the gold set.
- **PPI++:** θ̂_λ = mean(Y) + λ·[mean(f̃) − mean(f)], with SE² = λ²·Var(f̃)/N + Var(Y − λf)/n.
  - For the mean, the variance-minimising value is λ* = Cov(Y, f) / ((1 + n/N)·Var(f)). Clip it to [0, 1].
  - This value is the mean-estimation case of the plug-in tuning in PPI++ §6, derived here with Hessian = 1.
  - λ = 0 recovers classical inference; λ = 1 recovers PPI.

A useless judge drives λ toward 0, which is the power-tuning guarantee. Original PPI with an inaccurate judge can be *wider* than classical inference. That was the motivation for PPI++ [PPI++2023].

## Worked example (re-derived with python3)

Inputs:

- N = 20,000 judge-graded responses with a judge pass rate of 0.78.
- n = 300 random items that also have human labels:

| | judge = 1 | judge = 0 |
|---|---|---|
| **human = 1** | 204 | 12 |
| **human = 0** | 24 | 60 |

This gives mean(Y) = 0.720, mean(f) = 0.760, Var(Y) = 0.2023, Var(f) = 0.1830, Cov(Y, f) = 0.1332 and corr = 0.69.

| Method | Estimate | SE | 95% CI |
|---|---|---|---|
| Judge only (N = 20,000) | 0.780 | 0.0029 | Invalid: the judge is biased +0.04 on gold |
| Classical (n = 300) | 0.720 | 0.0260 | [0.669, 0.771] |
| PPI (λ = 1) | 0.740 | 0.0201 | [0.701, 0.779] |
| PPI++ (λ̂ = 0.717) | 0.734 | 0.0189 | [0.697, 0.771] |

PPI++ is worth about 1.9× the gold labels here: it matches a classical interval with ~570 human labels. The judge-only interval is tight and wrong, which is the failure this method exists to prevent.

## Validity conditions

- **Random gold subset.** The gold items must be a uniformly random (or known-probability, then weighted) sample from the same pool as the unlabelled items.
- **Frozen judge.** The judge prompt, model and rubric must be fixed before the gold labels are seen. If the judge was tuned on the gold set, the rectifier is optimistic; use a fresh gold split or cross-fitting.
- **One judge run for both sets.** The same judge run and version must label both sets. Judge drift between the gold and unlabelled passes breaks the rectifier.
- **Independent units.** PPI's CLT intervals assume i.i.d. items. With several items per prompt family or conversation, resample whole clusters around the PPI estimator, or aggregate to the cluster first. This adaptation is a design choice here, not a theorem from the PPI papers. Check the clustering rules in [eval error bars](eval-error-bars.md).
- **Model comparisons.** For A-versus-B, apply PPI to the per-item *difference* on shared items. This keeps the pairing.

## When not to use it

- The gold labels themselves are unreliable, for example with low inter-annotator agreement. PPI corrects toward the gold labels, so it inherits their construct problems. See [measurement theory](../../foundations-measurement-theory/SKILL.md).
- Fewer than roughly 50–100 gold items. The CLT and the λ̂ plug-in are asymptotic, so treat the result as approximate and prefer an exact or bootstrap check. This is a rule of thumb, not from a cited source.
- The target is a per-item decision, not a population quantity. Use conformal methods instead: [conformal variants](conformal-variants.md).

## Tooling

- Package: `ppi-python` on PyPI, imported as `ppi_py`. Check the current release and signature in its docs before relying on the details below.
- Look up `ppi_mean_ci` in the installed version's API docs and confirm its signature, λ tuning and clipping behavior before choosing `lam`. For the estimator above, λ = 1 gives PPI and λ = 0 gives classical inference.
- Set the desired level explicitly: `alpha=0.05` requests 95% confidence. Do not infer the interval level from a package default.

Sources:

- [PPI2023] Angelopoulos, Bates, Fannjiang, Jordan, Zrnic, *Prediction-powered inference*, Science 382(6671):669–674 (2023), https://doi.org/10.1126/science.adi6000.
- [PPI++2023] Angelopoulos, Duchi, Zrnic, *PPI++: Efficient Prediction-Powered Inference*, https://arxiv.org/abs/2311.01453.
