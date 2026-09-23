# Measurement primitives

## Physical quantities and latent constructs

Physical measurement starts with a specified measurand, unit, measurement model, operating conditions, and reference. Record corrections and an uncertainty budget; traceability requires a documented calibration chain and uncertainties. Calibration is not adjustment. These terms follow JCGM 200:2012; uncertainty treatment follows JCGM 100:2008.

Psychometric measurement starts with an explicit construct and interpretation. Evidence may address content, response processes, internal structure, relationships with other variables, and consequences relevant to the proposed use. The 2014 Testing Standards treat validity as support for score interpretation and use, rather than an inherent permanent property of an instrument.

## Operationalization

Write `target -> observable -> instrument -> scoring rule -> decision`. Enumerate omitted target facets and nuisance influences. A benchmark pass rate can be affected by task sampling, scaffolding, scorer errors, tool access, or contamination. Claims about a bare model need controls that separate these influences.

## Reliability and error

Choose replication to match use: inter-rater agreement for coding, repeated occasions for stable traits, task sampling for benchmarks, or repeat sensor readings for precision. Correlation is not agreement: adding 10 to every repeated score preserves perfect correlation while changing absolute scores. Confidence intervals and subgroup precision matter when decisions depend on individual cutoffs.

Classical `X = T + E` is a model with assumptions, not a guarantee that an observed score reveals truth. Alpha summarizes item covariance under a scoring model; redundant items can raise it while narrowing content. State the model and purpose before choosing alpha, omega, agreement statistics, or generalizability analysis. Do not treat any coefficient as a universal pass/fail criterion.

## Scale and permissible operations

Categorical labels permit classification; ordered labels permit rank comparisons. Equal-interval and ratio interpretations require additional justification. For an interval scale, a change of origin preserves differences but changes ratios: 20 degrees Celsius is not twice 10 degrees Celsius in thermodynamic temperature. Positive affine transformations preserve interval relations; ratio scales also require a meaningful zero. A questionnaire sum does not acquire equal units merely because arithmetic is possible.

## Calibration

For a sensor, document references, range, environmental conditions, corrections, and uncertainty. For a probability forecast, compare predictions with observed frequencies using held-out data and uncertainty; calibration need not imply discrimination. For a rating rubric, document anchor meaning and rater training. Never call these three operations interchangeable.

## Counterexample

A five-item survey repeats nearly identical questions about whether a user likes a logo. High internal consistency would not justify calling it a measure of trust in the company's handling of data. Missing content and criterion evidence leave that interpretation insufficient even if responses are stable.
