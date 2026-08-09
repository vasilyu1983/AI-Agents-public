# Primitive: Scale-Free Networks

**Sources**: Barabási & Albert (1999) Science; Clauset, Shalizi & Newman (2009) SIAM Review; Barabási (2016) Network Science §4.

## Definition

A **scale-free network** has a degree distribution that follows a power law:

P(k) ~ k^(−α)

where α is the scaling exponent, typically 2 < α < 3 for real networks. This fat-tailed distribution means a small number of nodes (hubs) have enormously more connections than the average.

**Barabási-Albert (BA) model** generates scale-free networks through two mechanisms:

1. **Growth**: the network grows by adding one node at a time
2. **Preferential attachment**: new nodes connect to existing nodes with probability proportional to their degree ("the rich get richer")

This produces α = 3 exactly. Empirical networks range from α ≈ 2.1 (Internet AS-level) to α ≈ 3.5 (co-authorship networks).

**Key properties of scale-free networks**:

- Ultra-small world: L ~ log(log n), shorter than random graphs of the same size
- Robust to random failure: random removal of nodes has little effect (most nodes have low degree)
- Fragile under targeted attack: removing the top hubs rapidly fragments the network
- Vanishing epidemic threshold: diseases or information spread to a finite fraction regardless of transmission rate (Pastor-Satorras & Vespignani 2001)

## When to Use

- Before designing resilience or immunisation strategies — hub targeting vs. random removal behave oppositely
- Before applying SIR models — vanishing threshold changes the epidemic forecast
- Characterising citation, social, or dependency networks for hub-based interventions
- Validating whether the "80/20" intuition holds in your specific network

## Inputs

- Degree sequence of the network
- Optional: full graph for goodness-of-fit cross-validation

## Outputs

- Estimated exponent α with 95% confidence interval
- Lower cutoff x_min (power law only valid above this degree)
- p-value from Kolmogorov-Smirnov test (p > 0.1 = plausible power law)
- Comparison against log-normal and exponential alternatives (likelihood ratio test)

## Failure Modes

1. **Visual inspection of log-log plots**: log-normal and power-law distributions look similar on log-log plots. Always use maximum-likelihood estimation + KS test (Clauset, Shalizi & Newman 2009).
2. **Reporting α without x_min**: a power law only holds above x_min; reporting α for the full degree range is incorrect.
3. **Not comparing alternative distributions**: a power law must beat log-normal and exponential by likelihood ratio; many claimed scale-free networks are better described as log-normal (Broido & Clauset 2019).
4. **Applying BA model to directed graphs without modification**: the standard BA model is undirected. For directed citation/web graphs, use directed preferential attachment variants.
5. **Treating "is this network scale-free?" as a settled, binary question**: it is not — this is a live, contested debate, not a closed one. Broido & Clauset (2019) applied a strict 5-tier statistical taxonomy to 927 real networks and found only ~4% met their "strongest" scale-free criterion (though 57% qualified under the weakest tier). Barabási publicly disputed the paper's methodology and thresholds; Holme (2019, Nat. Commun., published as a companion piece) reframes the same evidence to show that "is it scale-free" is highly sensitive to how strict a definition is chosen, and that scale-freeness is only cleanly defined in the infinite-size limit — any finite empirical network requires a judgment call on tolerance. **Practical implication**: do not report "this network is/isn't scale-free" as a fact from a single fitting run. Report the fitted α, x_min, goodness-of-fit, and which tier of scale-free-ness (if any) the network meets, and note that reasonable analysts disagree on how strict the bar should be. The Clauset-Shalizi-Newman (2009) test is necessary but does not resolve the definitional dispute — it only tells you whether a power law is a statistically defensible fit at all, not whether the network is "truly" scale-free in a way everyone would agree on.

## Worked Example

**npm dependency graph**: 4,200 packages, degree sequence extracted. MLE gives α̂ = 2.4, x_min = 10, p = 0.18 (plausible). Log-normal comparison: log-likelihood ratio R = 2.3, p = 0.03 → power law is significantly better. Conclusion: scale-free with hub concentration. The top 20 packages (0.5%) account for 35% of all dependencies. Targeted removal of these 20 packages disconnects 60% of the graph (percolation test), while random removal of 20 packages leaves the graph largely connected.

## Sources

- Barabási and Albert (1999). Emergence of Scaling in Random Networks. Science. [doi:10.1126/science.286.5439.509](https://doi.org/10.1126/science.286.5439.509)
- Clauset, Shalizi and Newman (2009). Power-law distributions in empirical data. SIAM Review. [doi:10.1137/070710111](https://doi.org/10.1137/070710111)
- Barabási (2016). Network Science. Cambridge. §4. [networksciencebook.com](https://networksciencebook.com/)
- Broido and Clauset (2019). Scale-free networks are rare. Nature Communications. [doi:10.1038/s41467-019-08746-5](https://doi.org/10.1038/s41467-019-08746-5)
- Holme (2019). Rare and everywhere: Perspectives on scale-free networks. Nature Communications 10:1016. [doi:10.1038/s41467-019-09038-8](https://doi.org/10.1038/s41467-019-09038-8) — Contested-debate counterpoint to Broido & Clauset; do not present the "rare" finding as a settled consensus.
- Pastor-Satorras and Vespignani (2001). Epidemic Spreading in Scale-Free Networks. Physical Review Letters. [doi:10.1103/PhysRevLett.86.3200](https://doi.org/10.1103/PhysRevLett.86.3200)

## Related

- [`06-percolation.md`](06-percolation.md) — targeted hub removal in scale-free networks triggers catastrophic percolation
- [`07-contagion-sir.md`](07-contagion-sir.md) — vanishing epidemic threshold on scale-free networks
- [`01-centrality-measures.md`](01-centrality-measures.md) — degree centrality identifies hubs for preferential-attachment claims
