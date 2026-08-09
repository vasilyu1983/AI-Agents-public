---
description: Formal theory map for information-theory foundations. Use to distinguish theorem-level guarantees from applied heuristics.
last_verified: 2026-05-02
status: stable
---

# Information Theory Formal Theory Map

## Purpose

Use this map when an applied information-theory recommendation needs theorem assumptions, estimator caveats, or a boundary between asymptotic guarantees and production heuristics.

## Theory Areas

| Area | Formal Objects | What It Supports | Boundary |
|---|---|---|---|
| Probability and measure | Random variables, distributions, sigma-algebras, Radon-Nikodym derivatives | Entropy, KL, MI, cross-entropy | Continuous entropy is not invariant under coordinate transforms |
| Source coding | Entropy rate, prefix codes, Kraft inequality, AEP | Lossless compression, typical sets, redundancy audits | Shannon limits are asymptotic unless finite-blocklength analysis is added |
| Channel coding | Mutual information, capacity, noisy channel theorem | Throughput ceilings and error bounds | Capacity does not say a finite implementation reaches the bound |
| Rate-distortion | Distortion measure, test channel, R(D) | Lossy compression, summarization budgets, token pruning | Result depends entirely on the distortion function |
| Divergence geometry | KL, JS, f-divergences, Bregman divergences | Training losses, variational objectives, distribution comparison | Most divergences are not metrics |
| MDL and stochastic complexity | Two-part codes, normalized maximum likelihood, regret | Model selection and overfit control | Code length depends on model class and coding convention |
| Information bottleneck | Sufficient statistics, IB Lagrangian, variational bounds | Representation compression | DNN compression interpretations remain contested |
| IT Generalization Bounds (CMI / PAC-Bayes) | Conditional mutual information I(W;Z_i \| S), PAC-Bayes posterior, algorithmic stability, SGD trajectory | Generalization error certificates for trained models; tighter bounds via loss-landscape flatness | CMI bounds require conditioning on full training trajectory, not just final weights; often vacuous for large DNNs without flatness augmentation (Peng et al. ICLR 2025 addresses this) | 
| Estimation theory | Plug-in estimators, bias correction, concentration, bootstrap | Entropy/MI estimates from finite data | High-dimensional estimates can be dominated by estimator bias; InfoNCE-family estimators are bounded above by log(K) (negative batch size) — use f-DIME or CMI-based protocols in high-MI regimes |

## Applied Primitive Coverage

| Primitive | Formal Backbone | Must Check Before Use |
|---|---|---|
| Shannon entropy | Discrete entropy, differential entropy, entropy rate | Discrete vs continuous source; log base; stationarity |
| Mutual information | KL between joint and product marginals | Estimator bias, sample size, dimensionality |
| KL divergence | Absolute continuity of P relative to Q | Support mismatch; direction of comparison |
| Cross-entropy | Expected code length under model Q for data P | Tokenizer/vocabulary dependence |
| Channel capacity | Max mutual information over input distributions | Channel model, noise law, finite blocklength |
| Rate-distortion | Optimization over conditional reconstructions | Distortion function and acceptable loss |
| MDL | Model code plus data code | Model family and coding scheme |
| Information bottleneck | Compression-prediction tradeoff | Estimator and representation assumptions |
| Fano's inequality | Lower bounds from conditional entropy | Label space size and residual uncertainty |
| Typical sets / AEP | Law of large numbers for information density | Ergodicity/stationarity and block length |
| Redundancy/compression | Entropy gap and universal coding regret | Source correlations and code family |

## Production Rule

Do not present information-theoretic values as absolute product metrics without the measurement contract: variable definition, sampling frame, estimator, units, uncertainty interval, and invariance caveat.
