# Primitive 6: Difference-in-Differences

## Definition

**Difference-in-Differences (DiD)** compares the change in outcomes over time in a treated group to the change in outcomes over time in a control group. The double difference removes time-invariant confounders and common time trends:

τ_DiD = (Ȳ_{T,post} − Ȳ_{T,pre}) − (Ȳ_{C,post} − Ȳ_{C,pre})

This identifies the **Average Treatment Effect on the Treated (ATT)** under the **parallel trends assumption**: absent treatment, the treated group would have evolved over time in parallel with the control group. Also state no anticipation, consistency, no relevant spillovers (or an explicit interference estimand), and stable composition/selection for the target population; these do not follow from a pretrend test.

**Two-way fixed effects (TWFE)** regression implementation:
Y_{it} = α_i + λ_t + τ D_{it} + ε_{it}

where α_i are unit fixed effects, λ_t are time fixed effects, and D_{it} is the treatment indicator.

**Staggered DiD**: units adopt treatment at different times. Canonical TWFE is biased under heterogeneous treatment effects across cohorts (Goodman-Bacon 2021 decomposition). Use one of the heterogeneity-robust estimators:
- Callaway & Sant'Anna (2021): cohort-specific ATTs, then aggregate; doubly robust.
- Sun & Abraham (2021): interaction-weighted estimator; decomposes TWFE by cohort.
- Borusyak, Jaravel & Spiess (2024, *RES*): imputation estimator; requires no always-treated units.
- Gardner (2022): two-stage DiD; intuitive, extends to event studies.
- For continuous or multi-valued treatment doses, use de Chaisemartin, D'Haultfœuille & Vazquez-Bare (2024, *AEA P&P*) or the 2025 extension to treatments continuously distributed at every period — not the Roth et al. (2023) synthesis paper, which surveys the discrete-treatment estimators above rather than proposing a continuous-treatment estimator itself.
- When parallel trends is uncertain rather than clearly violated or clearly satisfied: Rambachan & Roth (2023, *RES*) HonestDiD produces confidence intervals valid under bounded violations, instead of a binary pre-trend pass/fail.

## When to Use

- Pre/post data available for treated and control units.
- A plausible comparison group exists (similar pre-trends).
- Treatment is not universal — some units are never treated or treated later.
- Event timing is known and exogenous.

Common applications: policy evaluation, feature rollouts, regulatory changes, marketing interventions applied to geographic markets.

## Inputs / Outputs

**Inputs**: panel or repeated cross-section data; treatment timing; outcome Y; unit and time identifiers; pre-treatment periods for trend diagnostics; prespecified target ATT, comparison group and identifying assumptions.

**Outputs**: ATT estimate; uncertainty reflecting assignment and error dependence (e.g., city clusters for city assignment), with few-cluster limitations and justified small-sample methods; pretrend diagnostics with uncertainty and design-compatible bounded-trend sensitivity; post-treatment dynamic effects (event-study post-period).

## Worst Failure Modes

1. **Parallel trends violation**: if treated and control groups were on different pre-trends, the DiD estimate captures the trend difference, not the treatment effect. Plot pretrends with uncertainty; non-significance is not proof (low power), and selecting analyses after passing a pretest can distort estimates/coverage. Prespecify plausible departures and sensitivity bounds. Synthetic control (#7) imposes different donor-pool/counterfactual assumptions and is not an automatic cure.
2. **Anticipation effects**: if treated units change behavior *before* the official treatment date (in anticipation), the pre-period is contaminated. Redefine the treatment date or use leads in the event study.
3. **Staggered DiD with TWFE and heterogeneous effects**: TWFE uses early adopters as controls for late adopters in some periods, producing a weighted average with negative weights. This can flip signs. Use Callaway-Sant'Anna.
4. **Spillovers to control group**: if the treatment spills over to control units (e.g., a marketing campaign in one city attracts customers from a neighboring city in the control), the control group is contaminated. Use a "donut" control buffer or geographic controls.
5. **Choosing controls to match pre-trends post-hoc**: selecting control groups that happen to match pre-trends by searching data invalidates inference. Pre-register the control group selection criterion.

## Worked Example

**Setting**: A retailer rolls out a loyalty program in 5 pilot cities (treated). 10 similar cities are not yet enrolled (control). Monthly revenue data available for 6 months pre- and 3 months post-rollout.

**Data summary**:
- Treated cities: pre-period avg revenue = 100K/month, post-period avg = 118K/month → change = +18K
- Control cities: pre-period avg revenue = 102K/month, post-period avg = 107K/month → change = +5K

**DiD estimate**: τ = 18K − 5K = 13K/month (common time trend = +5K; treatment effect = 13K over that)

**Trend diagnostics:** Illustrative pre-period coefficients are near zero, but six months may have low power to detect economically relevant departures. Report intervals and a prespecified bounded-trend sensitivity analysis; do not approve the design from six non-significant tests.

**Illustrative regression point estimate:** Y_{it} = α_i + λ_t + 13.1 D_{it} + ε_{it}. Assignment is by city; inference must address dependence and the small number of treated cities. A conventional clustered s.e. alone does not justify a precise p-value; report an appropriate small-cluster analysis and its assumptions.

**Interpretation**: the observed double difference is ~13K per city/month. Interpret it as the pilot ATT only if parallel trends, no anticipation/spillovers and composition assumptions are defensible; report sensitivity and uncertainty before a causal claim.

## Sources

1. Angrist, J. D., & Pischke, J.-S. (2009). *Mostly Harmless Econometrics*. Princeton University Press. Chapter 5.
2. Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-Differences with Multiple Time Periods. *Journal of Econometrics*, 225(2), 200–230.
3. Roth, J., Sant'Anna, P. H. C., Bilinski, A., & Poe, J. (2023). What's Trending in Difference-in-Differences? A Synthesis of the Recent Econometrics Literature. *Journal of Econometrics*, 235(2), 2218–2244.
4. Goodman-Bacon, A. (2021). Difference-in-Differences with Variation in Treatment Timing. *Journal of Econometrics*, 225(2), 254–277.
5. de Chaisemartin, C., D'Haultfœuille, X., & Vazquez-Bare, G. (2024). Difference-in-Differences Estimators with Continuous Treatments and No Stayers. *AEA Papers and Proceedings*, 114, 597–601.
6. Rambachan, A., & Roth, J. (2023). A More Credible Approach to Parallel Trends. *Review of Economic Studies*, 90(5), 2555–2591. doi:10.1093/restud/rhad018

7. Roth, J. (2022). Pretest with Caution: Event-Study Estimates after Testing for Parallel Trends. *American Economic Review: Insights*, 4(3), 305–322. https://www.aeaweb.org/content/file?id=15847
