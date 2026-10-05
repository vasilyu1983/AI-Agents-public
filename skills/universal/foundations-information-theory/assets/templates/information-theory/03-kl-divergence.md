# Primitive 3: KL and JS Divergence

## Definition

D_KL(P‖Q) = Σ p(x) log[p(x)/q(x)], with P the numerator and Q the denominator (reference).
- ≥ 0, and 0 iff P = Q almost everywhere. Asymmetric; not a metric.
- **Direction:** D_KL(P‖Q) is large where Q puts little mass where P has mass. Outcomes with p(x) = 0 contribute nothing, so mass that only Q produces is invisible to it. It is infinite when q(x) = 0 and p(x) > 0.
- When optimizing Q against fixed P: D_KL(P‖Q) is mass-covering (mean-seeking); D_KL(Q‖P) is mode-seeking and penalizes Q for putting mass where P has none.
- Cross-entropy decomposition: see [04-cross-entropy.md](04-cross-entropy.md).

Jensen–Shannon: JSD(P,Q) = ½ D_KL(P‖M) + ½ D_KL(Q‖M), M = ½(P+Q). Unnormalized maximum is 1 bit (base 2) or ln(2) nats (base e); dividing nats by ln 2 normalizes to [0,1]. √JSD is a metric.

## Traps

1. **Unstated direction.** Always write both arguments. "Does the new version still cover what the old one did?" is D_KL(P_old‖P_new). "Does the new version put mass where the old one never did?" is D_KL(P_new‖P_old).
2. **Support failure.** A zero in the denominator where the numerator has mass makes KL infinite. Reversing the arguments asks a different question and can also be infinite. Smoothing changes the answer; report ε.
3. **Mixture does not rescue KL.** JSD is finite because each term is measured against M, which covers both supports. That does not make KL(P‖Q) or KL(Q‖P) finite.
4. **Fixed drift thresholds.** KL and JSD values depend on binning, support, sample size and base. There is no universal alert level; calibrate against a no-change baseline (bootstrap or historical windows) and the cost of a false alarm.
5. **KL is not perceptual distance**; Wasserstein may track perceived change better.
6. **Numerics:** compute in log space, Σ exp(log p)(log p − log q).

## Known answers

- P = (1, 0), Q = (0, 1): KL(P‖Q) = infinite (the numerator's outcome has zero denominator mass), KL(Q‖P) = infinite, JSD = 1 bit, the maximum.
- RLHF objective maximize E[r] − β D_KL(π‖π_ref) penalizes the policy for mass on tokens the reference finds unlikely; it does not require covering every reference mode. Swapping to D_KL(π_ref‖π) would penalize missing reference mass instead.

## Sources

Cover & Thomas (2006) Ch. 2; Kullback & Leibler (1951); Lin (1991). Not in sources.json: Stiennon, N. et al. (2020), Learning to summarize with human feedback, *NeurIPS 2020*. Full references: [`../../../data/sources.json`](../../../data/sources.json).
