# Cost uncertainty method

Use this method when uncertain input ranges can change a budget or architecture decision. Use deterministic arithmetic when inputs are fixed. Use explicit low/base/high scenarios when probabilities or relative frequencies cannot be defended.

## Input contract

`scripts/cost_uncertainty.py` accepts one JSON object. See [the independent-input example](../assets/cost-uncertainty-example.json) and [the joint empirical example](../assets/cost-uncertainty-joint-example.json).

- Every input declares a unit, finite bounds, a supported distribution, provenance, and why that distribution is used. Supported distributions are `constant`, `uniform`, `triangular`, and weighted `empirical`.
- `provenance.kind` is `observed`, `contract`, `expert`, `scenario`, or `derived`; `source` and `as_of` are mandatory text. A label records provenance and does not prove the distribution is calibrated.
- Independent inputs are sampled independently. To preserve dependence seen in paired observations or scenarios, put two or more inputs in a `joint_empirical_group`; the runner resamples complete weighted rows. Separate inputs and separate joint groups remain mutually independent in the model.
- Each component is `coefficient * product(factors) / divisor`. Sum components for total cost. A signed coefficient can represent a credit or inflow. Keep units auditable; the runner validates numbers and names, not dimensional consistency.
- `budget` uses the strict event `modeled_cost > budget`. Quantiles must be unique and increasing. The seed makes a fixed input reproducible.

Example:

```bash
python3 scripts/cost_uncertainty.py \
  --input assets/cost-uncertainty-example.json \
  --output /tmp/cost-uncertainty.json \
  --sensitivity --morris-trajectories 40 --morris-levels 6
```

Run from this bundle's directory. The output separates the modeled cost distribution from Monte Carlo error. `mean_standard_error`, the binomial standard error and Wilson interval for budget exceedance, and approximate batch quantile standard errors describe finite-simulation noise. Batch quantile diagnostics can be unstable for sparse tails or small batches. None of these measures misspecified ranges, omitted inputs, stale prices, or wrong dependence. More draws reduce this numerical error at roughly the usual square-root rate; they do not repair the model.

## Morris screening

`--sensitivity` runs randomized Morris elementary-effects trajectories over the full normalized quantile ranges of independent `uniform` and `triangular` inputs. It reports:

- `mu_star`: mean absolute elementary effect, used for screening and ranking;
- `mu`: signed mean elementary effect;
- `sigma`: variation in elementary effects, which can arise from nonlinear response or interactions and does not distinguish them.

This is global screening across sampled input quantiles, not a local perturbation or Sobol variance decomposition. The command refuses joint empirical groups and independent empirical inputs because varying them one at a time would break their dependence or continuous-factor assumptions. For dependent inputs, compare whole joint scenarios or use a separately validated dependence-aware sensitivity method.

## Interpretation and stop rule

Before acting, compare simulation output with deterministic arithmetic and plausible scenario bounds. Inspect the echoed provenance and dependence assumptions. Increase draws only when simulation-error diagnostics could change the decision. Stop and return to simple scenarios if probability weights, dependence, units, or the cost formula cannot be defended.

The implementation follows the propagation sequence in JCGM 101: assign input distributions, draw input vectors, evaluate the model, and summarize the output distribution. Morris screening follows randomized one-factor-at-a-time trajectories and elementary effects. See [data/sources.json](../data/sources.json) for the primary sources and the dependent-input boundary.
