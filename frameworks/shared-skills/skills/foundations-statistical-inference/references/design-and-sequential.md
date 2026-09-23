# Design, power, multiplicity, and sequential inference

## Planning precision

Choose an outcome, independent unit, baseline variability/rate, smallest meaningful effect or precision target, error criterion, allocation, and analysis before sample-size calculations. Account for clustering, attrition, and design changes. Power is a probability under a specified alternative and test; observed post-hoc power computed from the fitted effect adds little to the reported interval. Use scenario analyses when the baseline is uncertain.

Statistical and practical significance answer different questions. Equivalence requires a prespecified acceptable difference; failing to reject zero is not evidence of equivalence. Report absolute and relative changes with their baselines and uncertainty.

## Multiplicity

Define the family: endpoints, models, prompts, subgroups, repeated looks, or candidate selections. Family-wise error control such as Bonferroni controls any false rejection with valid component tests; it does not require independence. False-discovery-rate procedures control a different criterion and need the assumptions of the selected procedure. Report adjusted inference and the full explored family; choosing the best prompt and testing it on the same data produces selection bias.

Exploratory analyses remain useful when labeled. Use fresh held-out evaluation or selection-aware inference for confirmatory claims after selection.

## Sequential monitoring

Select a fixed horizon, prespecified group-sequential plan, or justified anytime-valid method. With data-dependent stopping, ordinary fixed-time p-values and confidence intervals generally lose their advertised guarantees. An e-process must satisfy its null-valid process requirements; a confidence sequence covers the parameter simultaneously across times under its assumptions. These methods do not eliminate dependence, selection, or model restrictions.

Record monitoring frequency, maximum budget, stopping boundaries, futility policy, adaptations, and what was actually followed. Do not silently relabel conventional p-values as anytime-valid or turn arbitrary rolling intervals into a confidence sequence.

Worked scenario: twenty independent null tests at level 0.05 have probability 1−0.95^20 ≈ 0.642 of at least one false rejection. Bonferroni tests each at 0.0025 to bound family-wise error by 0.05. The independence assumption is used only for the worked 0.642 calculation.

Counterexample: stopping an experiment the first time an ordinary p-value drops below 0.05 does not preserve a 5% false-positive claim.

Primary source: [Ramdas et al., game-theoretic statistics and safe anytime-valid inference](https://arxiv.org/abs/2210.01948). Its framework motivates method selection; it does not authorize an unspecified monitoring procedure.
