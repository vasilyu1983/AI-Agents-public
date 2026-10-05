# Practical Causal Design Contract

## Target-trial emulation

Before estimation write eligibility, treatment strategies, assignment procedure, time zero, follow-up, outcome, causal contrast and analysis plan. Align eligibility, assignment and follow-up start to avoid immortal-time bias. State whether the target is intention-to-treat, per-protocol, ATT or another estimand. An observational emulation still needs exchangeability, positivity and consistency; reproducing trial vocabulary does not randomize treatment.

## Selection, measurement and missingness

Add observation/selection nodes and measurement timing to the design graph. Separate missing outcomes, censoring, missing covariates and noisy exposure/outcome measurement. Complete-case analysis, inverse-probability censoring weights and imputation require different assumptions; none universally repairs MNAR selection. Record missingness by treatment/time/subgroup and sensitivity to plausible nonrandom missingness. See foundations-measurement-theory for construct/instrument validity and foundations-statistical-inference for uncertainty methods.

## Longitudinal treatment

When a time-varying confounder is affected by prior treatment and predicts later treatment/outcome, ordinary adjustment can block causal effects or introduce bias. Consider longitudinal g-formula, marginal structural models with treatment/censoring weights, or structural nested models under sequential exchangeability, positivity and consistency. Check weight tails and effective independent sample size at each time; specify sustained regimes rather than treating all historical exposure as a single baseline variable.

## Policy value and transport

CATE is a conditional average, not an identified individual counterfactual effect. Evaluate targeting policy value on held-out/cross-fitted data with overlap for the actions it recommends, resource constraints and uncertainty; subgroup discovery on training data does not validate launch impact. Under interference, name the exposure mapping and target intervention saturation. Cluster/switchback designs do not automatically identify a global launch effect without design-specific assumptions.

Transportability needs a named target population, measured effect modifiers, selection assumptions and target support. Do not transfer a local IV/RDD effect or trimmed-sample ATE to all users by relabeling it.

## Completion artifact

Deliver trial/design table, diagram, estimand/population including exclusions, identification assumptions, data/missingness audit, estimator/uncertainty contract, design-compatible sensitivity and decision limitations. On unidentified effects, inadequate overlap or implausible measurement validity, report an association or an inconclusive result rather than a causal point estimate.

Known-answer controls: pure NDE plus total NIE reconstructs TE with interaction; binary IV without no-defiers does not yield the standard complier claim; a dollar mean difference alone cannot yield an E-value; donor-placebo inference is not matched-design Rosenbaum sensitivity. The checked RR helper remains `scripts/evalue.py`; it does not implement these broader estimators.

Primary reference: Hernan and Robins, [Causal Inference: What If](https://www.hsph.harvard.edu/miguel-hernan/causal-inference-book/), target trials, longitudinal g-methods, selection and transport assumptions.
