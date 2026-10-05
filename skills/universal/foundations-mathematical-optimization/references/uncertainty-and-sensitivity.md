# Uncertainty and sensitivity

Choose uncertainty semantics from the decision, not convenience. These are modeling choices requiring application evidence; this bundle supplies no universal guarantee for real demand.

- Deterministic sensitivity: perturb an uncertain coefficient or constraint, resolve, and find decision switches. Include joint perturbations where correlations matter. A local derivative is not an unlimited-range prediction.
- Robust optimization: define an uncertainty set and require feasibility across it. Report set construction, correlations, and conservatism; the guarantee extends only to that set, not arbitrary future conditions.
- Stochastic optimization: specify a distribution or weighted scenarios and separate here-and-now choices from recourse after observations. Include nonanticipativity so the model does not use future information. A sample optimum is not automatically an optimum for the population distribution.
- Chance constraints: define the violation probability and whose randomness it covers. Finite sampled feasibility alone does not establish a population probability bound.

Validate a chosen allocation on held-out or stress scenarios; report data provenance, independent sampling unit, and dependence/drift limitations. Distribution estimation and interval inference belong in statistical inference; utility under uncertainty belongs in decision theory.

Primary references: [Stanford robust optimization lectures](https://web.stanford.edu/class/ee364b/lectures/robust_slides.pdf), uncertainty-set definitions and chance constraints; [MIT stochastic programming lecture](https://ocw.mit.edu/courses/6-079-introduction-to-convex-optimization-fall-2009/5e4810dabbe02645b52fc082cd18ee74_MIT6_079F09_lec13.pdf), sample-average approximation and out-of-sample validation. The examples below are hand-derived modeling examples.

## Worked sensitivity and uncertainty example

One divisible product earns value 3 per unit, with capacity 2: maximizing `3x` subject to `0 <= x <= 2` gives value 6. Raising capacity to 2.5 gives 7.5. If an additional market cap `x <= 2` applies, adding production capacity provides no gain. The multiplier is therefore tied to the complete model and perturbation regime.

A here-and-now order `q` must not exceed uncertain capacity, known only to lie in `[8,12]`. Robust feasibility requires `q <= 8`. Choosing `q=10` using mean capacity is infeasible at capacity 8. If overruns are allowed at a stated cost, that is a different recourse/stochastic model, not the same robust guarantee. If capacity is later observed before ordering, the timing creates a different decision again.
