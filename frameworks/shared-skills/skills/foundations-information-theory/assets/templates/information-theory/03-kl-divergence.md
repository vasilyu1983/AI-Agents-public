# Primitive 3: KL Divergence

## Definition

**Kullback-Leibler (KL) divergence** from distribution Q to distribution P:

```
D_KL(P ‖ Q) = Σ_{x} p(x) log [ p(x) / q(x) ]      [discrete]
D_KL(P ‖ Q) = ∫ f_P(x) log [ f_P(x) / f_Q(x) ] dx  [continuous]
```

Properties:
- D_KL(P‖Q) ≥ 0 always (Gibbs inequality / non-negativity)
- D_KL(P‖Q) = 0 iff P = Q almost everywhere
- **Asymmetric**: D_KL(P‖Q) ≠ D_KL(Q‖P) in general
- **Undefined** when Q(x) = 0 and P(x) > 0 (forward KL is infinite; reverse KL avoids this)
- Not a metric (violates triangle inequality and symmetry)

**Reverse KL**: D_KL(Q‖P) — penalizes Q for assigning mass where P assigns none.

**Jensen-Shannon (JS) divergence** (symmetric, bounded):

```
JSD(P‖Q) = ½ D_KL(P‖M) + ½ D_KL(Q‖M)   where M = ½(P+Q)
JSD ∈ [0, log 2] (base-2) or [0, 1] (base-e after normalizing)
sqrt(JSD) is a proper metric
```

**Relation to cross-entropy**:  H(P,Q) = H(P) + D_KL(P‖Q)

**Forward vs. reverse KL behavior**:
- Forward D_KL(P‖Q): **mean-seeking** — Q must cover all modes of P; penalizes missed mass heavily
- Reverse D_KL(Q‖P): **mode-seeking** — Q collapses to a mode of P; penalizes extra mass less

---

## When to Use

- **RLHF / policy regularization**: D_KL(π‖π_ref) penalizes the policy for diverging from the reference. Forward KL typically used; direction must match the optimization objective.
- **Variational inference (VAE, diffusion)**: ELBO = E[log p(x|z)] − D_KL(q(z|x)‖p(z)); reverse KL between approximate and prior posterior.
- **Hypothesis testing**: Chernoff-Stein lemma: error exponents in binary hypothesis tests are D_KL(P₁‖P₀).
- **Distribution shift monitoring**: D_KL(P_current‖P_reference) tracks how far a live distribution has drifted from baseline.
- **Symmetric comparison**: Use JSD when neither direction is more natural; use JSD's square root as a true distance.

---

## Inputs

| Input | Type | Description |
|-------|------|-------------|
| P | Distribution (numerator) | True or target distribution |
| Q | Distribution (denominator) | Approximate or reference distribution |
| Support alignment | Boolean check | Q must have support ⊇ support of P for forward KL to be finite |

---

## Outputs

| Output | Type | Range | Interpretation |
|--------|------|-------|----------------|
| D_KL(P‖Q) | Non-negative real | [0, ∞) | Extra bits needed to encode P using Q's code |
| D_KL(Q‖P) | Non-negative real | [0, ∞) | Extra bits needed to encode Q using P's code |
| JSD(P‖Q) | Non-negative real | [0, log 2] | Symmetric divergence; sqrt is a proper metric |

---

## Failure Modes

1. **Asymmetry trap**: Using D_KL as a symmetric "distance." D_KL(P‖Q) and D_KL(Q‖P) can differ dramatically, especially when one distribution has narrow support. Always specify direction explicitly; use JSD for symmetric needs.
2. **Zero-probability singularity**: If Q(x)=0 for any x where P(x)>0, forward D_KL(P‖Q)=∞. Mitigation: add-ε smoothing (Laplace), or switch to reverse KL, or use JSD (which uses the mixture M and is always finite for any P,Q with finite support).
3. **KL ≠ perceptual distance**: High KL does not imply perceptually large difference. For natural images or language, Wasserstein/Earth-Mover distance is often more aligned with perceptual similarity.
4. **Mixing forward and reverse in the same system**: RLHF typically minimizes D_KL(π‖π_ref) (forward, penalizing deviation); VAE minimizes D_KL(q‖p) (reverse, mode-seeking). Swapping direction silently changes optimization behavior.
5. **Numerical underflow in log-space**: For very small p(x) or q(x), compute KL in log-space: Σ exp(log_p) · (log_p − log_q). Never divide raw probability values and then take log.

---

## Worked Example

**RLHF KL penalty direction**

A language model π is fine-tuned from π_ref. The RLHF objective:

```
maximize E[r(x)] − β · D_KL(π ‖ π_ref)
```

Using forward D_KL(π‖π_ref): penalizes π for assigning mass to tokens π_ref would assign near-zero probability. This discourages mode collapse away from the reference distribution.

Swapping to D_KL(π_ref‖π): the gradient signal would instead penalize π_ref for assigning mass to tokens π misses — which is not the intent; π_ref is fixed during fine-tuning.

**Distribution shift detection**

Reference distribution P_ref (week 1 production traffic) vs. current P (week 6):

```
D_KL(P_current ‖ P_ref) = 0.03 bits   → minimal drift
JSD(P_current, P_ref) = 0.01           → symmetric view confirms low shift
```

After a model update:

```
D_KL(P_current ‖ P_ref) = 1.4 bits    → significant drift; alert triggered
JSD = 0.42                              → confirms both directions affected
```

---

## Sources

- Cover, T. M. & Thomas, J. A. (2006). *Elements of Information Theory*, 2nd ed., Ch. 2. Wiley.
- Kullback, S. & Leibler, R. A. (1951). On information and sufficiency. *Annals of Mathematical Statistics*, 22(1), 79–86.
- MacKay, D. J. C. (2003). *Information Theory, Inference, and Learning Algorithms*, Ch. 2. Cambridge.
- Lin, J. (1991). Divergence measures based on the Shannon entropy. *IEEE Transactions on Information Theory*, 37(1), 145–151. (JS divergence.)
- Stiennon, N. et al. (2020). Learning to summarize with human feedback. *NeurIPS 2020*. (RLHF KL penalty application.)
