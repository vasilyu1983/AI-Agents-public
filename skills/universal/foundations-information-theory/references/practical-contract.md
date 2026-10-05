# Finite Distribution Measurement Contract

## Define the measurement

State outcomes/random variables, empirical sampling frame, joint/conditional distributions, discrete versus continuous treatment, log base, estimator, support, sample size and uncertainty/null baseline. Token counts, embedding spread and document similarity are proxies unless this distributional contract exists. Conditional task information I(task;candidate|selected) is the exact target for marginal information; pairwise subtraction is only a heuristic.

## Runnable known answers

`python3 scripts/discrete_information.py` prints the self-contained known-answer suite. The module provides entropy, joint-table MI, KL, JS, simplified bit-based Fano bound and bits-per-byte from total bit NLL. It validates finite probability masses summing to one; it is not an empirical estimator or corpus scorer. KL support failure is reported as infinity in Python; CLI output uses an explicit support result instead of nonfinite JSON. Run `python3 scripts/test_discrete_information.py`.

Controls: fair coin entropy=1 bit; deterministic entropy=0; independent fair binary variables MI=0; identical fair variables MI=1; disjoint point masses JS=1 bit and forward KL infinite. H(Y)=1 may coexist with H(Y|X)=0, so marginal label entropy is not irreducible classification loss.

BPB = total negative log2 sequence probability / bytes under a shared text encoding/corpus/context convention. Mean token entropy divided by corpus bytes is dimensionally wrong. Fano uses finite label alphabets and conditional entropy; a nonpositive simplified floor is inconclusive, not evidence that the features suffice.

## Estimator choice and guardrails

For finite discrete tables, plug-in entropy/MI has finite-sample bias and support sensitivity; use sample-size/support diagnostics, held-out or permutation baselines and uncertainty appropriate to independent sampling units. Jiao-Venkat-Han-Weissman estimators address discrete functional estimation; NSB and Miller-Madow have their own regimes, not interchangeable universal corrections. Continuous kNN/neural MI needs estimator-specific consistency and bias checks; a confidence interval cannot validate a misspecified estimator. InfoNCE saturation is not a universal bound on NWJ.

Data processing: for T <- X -> Y (T is computed from X without additional Y information), I(T;Y) <= I(X;Y); deterministic invertible transformations preserve MI where defined. This does not imply that longer texts contain more relevant bits or that quantizing agent summaries guarantees task utility.

A source-code bit bound concerns exact reconstruction under its source model; rate-distortion additionally fixes a distortion measure. Do not convert Gaussian MSE bounds into ROUGE-loss or natural-language token guarantees. Semantic entropy detects sampling instability, not stable false beliefs; validate thresholds on representative grounded factuality labels. Neural MI/RL entropy results are setup-specific empirical evidence, not universal production laws.

## Completion

Deliver the measurement contract, value/units and support checks, estimation uncertainty, decision relevance and an explicit heuristic/theorem distinction. If probabilities or sampling variables are undefined, label the score a proxy and evaluate its task performance rather than reporting invented bits.
