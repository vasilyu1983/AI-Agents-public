# Sampling and estimation

## Establish the inference target

Define the estimand before selecting the statistic: population mean, proportion, paired difference, quantile, conditional association, or prediction. State denominator and units. A convenience sample estimates its sampled population unless a defensible transport/weighting model supports a wider target. Report nonresponse and missingness; an unobserved outcome is not zero.

Identify the unit supporting independence: repeated tasks within a user, time blocks, sites, and shared datasets introduce dependence. Use a design-compatible cluster, paired, longitudinal, or hierarchical analysis rather than pretending every row is independent. Very few clusters can make asymptotic cluster-robust intervals unreliable.

## Match the uncertainty to the claim

| Claim | Suitable approach and conditions |
|---|---|
| Mean of independent observations | Standard-error/t interval when distributional or asymptotic conditions are credible; inspect skew and influential observations |
| Proportion | Binomial interval for independent Bernoulli trials; use Wilson or an exact method rather than a boundary-degenerate Wald interval |
| Paired difference | Analyze within-pair differences; do not discard the dependence |
| Quantile or complex estimator | Method-specific interval or design-respecting resampling; preserve clusters/time dependence and account for estimator instability |
| Model parameter | Likelihood or posterior inference with explicit model assumptions, identifiability, and diagnostics |
| Future outcome | Predictive distribution or prediction interval including outcome variability, not only parameter uncertainty |

Do not prescribe one bootstrap for every estimator. The data-generating design and the estimator determine whether resampling is appropriate. This reference intentionally contains no generic bootstrap implementation.

## Bayesian inference

Specify likelihood, prior, and posterior target. Use prior predictive checks to expose implausible scales, posterior predictive checks for model misfit, and sensitivity to plausible alternative priors. Report computational diagnostics for approximate inference; a posterior draw count is not the effective sample size. Bayesian intervals are conditional on the modeling choices; poorly chosen likelihoods can give precise but wrong answers.

## Worked example and counterexample

Under an illustrative independent, approximately normal sample model, n=100, mean=10, sample SD=2 gives SE=0.2. A 95% t interval is approximately 10 ± 1.984×0.2, or [9.603, 10.397]. This is uncertainty about the population mean, not a range containing 95% of individual observations.

Counterexample: 100 outputs from one prompt/user are not evidence of 100 independent users. Report that effective replication is unknown and use a repeated-unit model or obtain independent units before a population claim.

Primary interpretation reference: [ASA statement](https://www.amstat.org/asa/files/pdfs/P-ValueStatement.pdf). No fixed statistical threshold substitutes for scientific or decision context.
