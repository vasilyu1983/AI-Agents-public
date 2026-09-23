# Graph decision and validation worksheet

Use before graph rankings, blast-radius or diffusion commitments. This worksheet owns graph semantics and inference assumptions; it does not add general simulation infrastructure.

## Intake and deliverable

Record target population, observation window, node inclusion, relation/edge direction, weights, timestamps, collection/sampling, missingness and decision. Deliver the chosen construction, baseline, ranking/partition/reachability results, sensitivity table and permitted interpretation. Compare plausible missing-edge/node and projection scenarios; scenario ranges are not statistical confidence intervals unless the sampling model supports them.

## Directed operational impact

For dependent→dependency edges reverse traversal to find exposed dependents. Specify required/optional edges, runtime/version conditions and fallbacks before calling exposure an outage. Example A→B and C→B: removing B exposes A,C; removing A does not expose B,C. A community partition cannot substitute for this traversal.

## Diffusion and cohort costs

Separate SIR/SIS, threshold adoption and referral branching. For iid transmissibility T on a locally tree-like uncorrelated configuration network use B=T(⟨k²⟩−⟨k⟩)/⟨k⟩. Degree3 gives B=.8 at T=.4 and B=1.2 at T=.6. Finite seeds can die out above threshold. Calibrate contacts and transmission, compare temporal/static models, choose simulation precision, and separate Monte Carlo uncertainty from model and sampled-graph uncertainty.

In iid subcritical referral branching, expected total cohort including one seed is 1/(1−R). Seed cost C and per-descendant incentive I give CAC=C(1−R)+IR. With C=5,R=.6,I=0, total cohort=2.5 and CAC=2; with I=1, CAC=2.6. Duplicates, finite populations and changing conversion break this formula.

## Review cases

- Two disconnected triangles: useful descriptive components despite only six nodes; inference still requires a null comparison.
- A→B@5 and B→C@3: static reachability exists but time-respecting reachability does not.
- Community parameters: γ controls resolution; ε controls convergence. Scan γ and seeds, evaluate downstream utility and degree-preserving nulls where appropriate.
- Report known graph construction limitations rather than ranking sampled hubs as universally important.

Primary derivation: [Newman SIR/percolation](https://arxiv.org/html/cond-mat/0205009v1). Use the bundled sources for temporal paths, community inference and power-law tests.
