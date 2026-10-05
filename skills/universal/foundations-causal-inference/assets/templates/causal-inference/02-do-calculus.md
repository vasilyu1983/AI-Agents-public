# Primitive 2: Do-Calculus

## Definition

The **do-operator** do(X = x) represents a surgical intervention: fix X to value x and remove all incoming edges to X in the DAG. The distribution P(Y | do(X = x)) is the interventional distribution — what Y's distribution would be if we *forced* X to x, not merely observed X = x.

This distinction is fundamental:

- P(Y | X = x): probability of Y among units where X happened to be x (observational, includes selection)
- P(Y | do(X = x)): probability of Y if we externally set X to x (causal)

**Do-calculus** (Pearl 1995) is a complete set of three inference rules for transforming expressions containing do-operators into expressions over the observed distribution P. A causal effect is **identifiable** if do-calculus can reduce P(Y | do(X)) to a function of P alone.

The three rules (in terms of the mutilated graph G):

- **Rule 1** — insertion/deletion of observations
- **Rule 2** — action/observation exchange (when Z is "as good as" an intervention)
- **Rule 3** — deletion of actions (when do(Z) has no effect on Y given X)

## When to Use

Use do-calculus identifiability check before running any causal estimator on observational data:

1. You want to estimate a causal effect, not a conditional association.
2. You have a DAG.
3. You are not sure whether the effect is identifiable from observed data.

If the effect is not identifiable, no statistical method on that dataset will give a consistent causal estimate — more data and better models will not fix an identification failure.

## Inputs / Outputs

**Inputs**: a DAG; the target causal effect P(Y | do(X)); the set of observed variables.

**Outputs**: either (a) an expression for P(Y | do(X)) in terms of the observed distribution P — which specifies exactly what adjustment or formula to compute — or (b) a non-identifiability result.

## Worst Failure Modes

1. **Skipping the identifiability check**: running a regression or propensity model on non-identified causal effects produces confident but causally meaningless estimates.
2. **Conflating P(Y|X) with P(Y|do(X))**: the most common error in applied work. P(Y|X) can be arbitrarily far from P(Y|do(X)) when confounders are present.
3. **Using the adjustment formula with an invalid adjustment set**: not all conditioning sets satisfy the backdoor criterion. Using Z that contains a collider biases the estimate.
4. **Assuming identifiability because an instrument exists**: IV identifies LATE under its own assumptions; this is not equivalent to full identifiability of P(Y|do(X)) for all subpopulations.
5. **Treating front-door as always available**: the frontdoor criterion requires no unblocked backdoor paths to the mediator, which often fails in practice.

## Worked Example

**Setting**: Does smoking (X) cause lung cancer (Y)? There is an unobserved confounder U (genetic predisposition) that causes both X and Y. We observe tar deposits (M), which are caused by smoking.

**DAG**:

```text
U → X (Smoking)
U → Y (Cancer)
X → M (Tar) → Y (Cancer)
X → Y (Cancer) [possibly direct]
```

Suppose the only path from X to Y is through M (no direct edge X → Y). U is unobserved.

**Backdoor path**: X ← U → Y. Cannot be blocked because U is unobserved. Backdoor criterion fails.

**Frontdoor criterion**: M satisfies the frontdoor criterion:

1. M intercepts all directed paths from X to Y (X → M → Y).
2. No unblocked backdoor paths from X to M (U does not directly cause M).
3. All backdoor paths from M to Y are blocked by X (condition on X).

**Frontdoor formula**:
P(Y | do(X)) = Σ_m P(M = m | X) × Σ_{x'} P(Y | X = x', M = m) P(X = x')

This is computable from observational data even with the unobserved U.

**Numbers** (hypothetical):

- P(M = 1 | X = 1) = 0.9, P(M = 1 | X = 0) = 0.1
- P(Y = 1 | X = 1, M = 1) = 0.7, P(Y = 1 | X = 0, M = 1) = 0.5
- P(Y = 1 | X = 1, M = 0) = 0.3, P(Y = 1 | X = 0, M = 0) = 0.2
- P(X = 1) = 0.4

P(Y=1 | do(X=1)) ≈ 0.9 × (0.7×0.4 + 0.5×0.6) + 0.1 × (0.3×0.4 + 0.2×0.6) = 0.9×0.58 + 0.1×0.24 = 0.546

P(Y=1 | do(X=0)) ≈ 0.1×0.58 + 0.9×0.24 = 0.274

Causal effect of smoking: 0.546 − 0.274 = 0.272, even though U is never observed.

## Sources

1. Pearl, J. (1995). Causal Diagrams for Empirical Research. *Biometrika*, 82(4), 669–688.
2. Pearl, J. (2009). *Causality*. Cambridge University Press. Chapter 3.
3. Shpitser, I., & Pearl, J. (2006). Identification of Joint Interventional Distributions in Recursive Semi-Markovian Causal Models. *AAAI 2006*.
