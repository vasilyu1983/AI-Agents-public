# Composition Recipes

Templates compose. The three folders ([`debate-methods/`](debate-methods/), [`decision-masks/`](decision-masks/), [`game-theory/`](../../skills/universal/foundations-game-theory/assets/templates/game-theory/)) each have their own "How to compose" hints, but most real decisions need a stack across folders. This doc maps common decision archetypes to a recommended stack.

These are starting points. Trim or extend based on cost budget and time pressure.

## Quick reference

| Decision archetype | Debate method | Decision mask(s) | Game-theory mechanisms |
|---|---|---|---|
| High-stakes irreversible (regulatory, board) | Courtroom (PROClaim) | Inversion on Defense | 13 (reasoning-tree audit), 11 (prediction market), 14 (credibility) |
| Multi-objective tradeoff (pricing × growth × compliance) | Polarity Management or Negotiation | Regret-Min on synthesis owner | 12 (ZOPA/BATNA), 9 (Pareto-Nash), 15 (generative social choice) |
| Series-A go/no-go | Pre-Mortem | Base-Rate Reset on optimist; Inversion on champion | 16 (meta-debate routing), 4 (Shapley post-run), 11 (prediction market) |
| Architecture RFC | Dialectical Inquiry | Second-Order on advocate; First Principles on critic | 13 (reasoning-tree audit), 4 (DAG-Shapley post-run), 7 (incentive-compatible synthesis) |
| Pricing change | Steel-Manning | Anchoring Reset on every member | 15 (generative social choice), 11 (prediction market) |
| Migration / cutover | Pre-Mortem + Devil's Advocate | Base-Rate Reset on champion; Inversion on owner | 13 (reasoning-tree audit), 5 (reputation gating), 6 (cooperation/defection) |
| Strategic uncertainty (market timing) | Scenario 2×2 | Second-Order; Base-Rate Reset | 11 (prediction market), 9 (Pareto-Nash) |
| Recurring high-frequency team optimization | (varies — measure first) | (none specific) | 10 (evolutionary search; ShinkaEvolve), 4 (DAG-Shapley), 5 (reputation gating) |
| Security or compliance review | Courtroom | Inversion on every member | 14 (credibility), 13 (reasoning-tree audit), 5 (reputation: adversarial tier) |
| Cross-domain ambiguous question | (varies after team selection) | (varies) | 3 (auction routing) → 16 (meta-debate routing) → main debate |

## Detailed recipes

### High-stakes irreversible (regulatory, board, large dollar)

**Goal**: Decision must survive after-the-fact scrutiny. Audit trail matters more than speed.

```
Team launch:
  debate.method = courtroom (PROClaim variant)
    Plaintiff: domain advocate (different specialization than Defense)
    Defense: domain skeptic (different specialization than Plaintiff)
    Court: orchestrator
    Critic: independent reviewer
    Judicial Panel: 3 heterogeneous judges
  masks:
    Defense agent wears Inversion (forces "what would guarantee failure?")
  game-theory:
    13 — synthesis is reasoning-tree audit, NOT majority vote
    11 — every claim carries a confidence stake, calibrated post-run
    14 — every claim carries cited evidence; per-claim credibility scored
    4 — Shapley scoring after the run for next-team-composition learning
```

**Why**: PROClaim's Progressive RAG + heterogeneous-judge structure is the most evidence-rich debate format. ACPO synthesis (mechanism 13) prevents confident-but-wrong consensus. Credibility scoring (14) catches single-claim failure modes that reputation gating (5) would miss. Inversion mask on Defense ensures the strongest case-against gets built rather than a token devil's advocate.

### Multi-objective tradeoff (pricing × growth × compliance, performance × maintainability × delivery)

**Goal**: No right answer. Buy-in from each stakeholder lens matters.

```
Team launch:
  debate.method = polarity-management OR negotiation-zopa-batna
    Polarity if the tradeoff is recurring and non-resolvable.
    Negotiation if the answer is a numeric compromise.
  masks:
    Synthesis owner wears Regret-Minimization
    Each stakeholder member wears their domain mask if applicable
  game-theory:
    12 — ZOPA/BATNA explicit per stakeholder
    9 — Pareto frontier mapped before picking a point
    15 — generative social choice for synthesis (maximin, not average)
```

**Why**: Multi-objective decisions die at synthesis when averaged. Maximin (15) forces the synthesis to either accommodate minority evidence or name the dissent honestly. Regret-Min mask on synthesis owner counters the "split the difference" instinct.

### Series-A or Series-B go/no-go (founder, board)

**Goal**: Decide whether to commit serious resources/dilution. Survivorship bias is acute.

```
Team launch:
  debate.method = pre-mortem
    Each agent imagines the outcome failed, works backward to causes.
  masks:
    The most optimistic member wears Base-Rate Reset
    The biggest champion wears Inversion
    Skeptics get no mask (don't compound skepticism)
  game-theory:
    16 — meta-debate routing for role assignment (capability-aware)
    11 — confidence staking on each predicted failure mode
    4 — Shapley scoring after the run; teams that systematically miss
        will show up in low-credibility members
    5 — reputation gating: track which members called past go/no-gos correctly
```

**Why**: Founder/board decisions are systematically biased toward optimism (champions self-select, skeptics filter out). Base-Rate Reset on the optimist counters survivorship bias; Inversion on the champion forces them to argue against their own thesis. Meta-debate routing (16) ensures the *right* agent argues each side, not the most senior one.

### Architecture RFC

**Goal**: Pick an architecture that survives 2-5 years. Multiple defensible options.

```
Team launch:
  debate.method = dialectical-inquiry (thesis / antithesis / synthesis)
  masks:
    Advocate of the proposed architecture wears Second-Order
    Critic wears First Principles
  game-theory:
    13 — reasoning-tree audit at synthesis
    4 — DAG-Shapley post-run (member workflow forms a clean DAG)
    7 — evidence-synthesis protocol (no incentive guarantee)
```

**Why**: Architecture decisions cascade — Second-Order mask on the advocate catches "this looks fine at first order but breaks downstream." First Principles on the critic prevents convention-bound critique. Reasoning-tree audit (13) at synthesis surfaces *where* the disagreement actually is, which is the load-bearing artifact for the RFC reviewer pool.

### Pricing change

**Goal**: Decide on a price move. Anchoring on existing or competitor prices is the dominant failure mode.

```
Team launch:
  debate.method = steel-manning
    Pricing-up advocate vs. pricing-down advocate, each argues the
    strongest version of the OPPOSING view.
  masks:
    EVERY member wears Anchoring Reset
  game-theory:
    15 — generative social choice for synthesis
    11 — confidence staking on willingness-to-pay estimates
```

**Why**: Pricing decisions are Exhibit A for anchoring. Reset on every member, then steel-man both sides to expose where the anchored framing is doing the work. Generative social choice (15) prevents synthesis defaulting to the existing-price status quo.

### Migration / cutover

**Goal**: Decide whether and when to ship a high-risk change.

```
Team launch:
  debate.method = pre-mortem + devils-advocate (composed)
    Pre-mortem first; then Devil's Advocate stress-tests the consensus
  masks:
    Migration champion wears Base-Rate Reset
    Migration owner wears Inversion
  game-theory:
    13 — reasoning-tree audit at synthesis
    5 — reputation gating: members with prior migration miscalls go to
        Probationary tier for THIS run only
    6 — explicit cooperation/defection tracking; "we tested it" without
        named test artifacts is a defection signal
```

**Why**: Migration teams are systematically over-confident — past migrations that "went fine" anchor the team on success. Base-Rate Reset surfaces what fraction of comparable migrations actually shipped without rollback. Pre-mortem maps failure modes; Devil's Advocate stress-tests the team's confidence in those mappings.

### Strategic uncertainty (market timing, category bet)

**Goal**: Decide enter / wait / monitor / avoid given large unknowns.

```
Team launch:
  debate.method = scenario-2x2
    Pick the two most uncertain variables; map four scenarios.
  masks:
    Each scenario gets one agent who wears Second-Order
    Optimistic-scenario agent additionally wears Base-Rate Reset
  game-theory:
    11 — every scenario carries a probability estimate (confidence stake)
    9 — Pareto frontier across scenarios on multiple objectives
```

**Why**: Scenario 2×2 forces the team to take each future seriously. Second-Order on each branch maps cascading effects. Probability stakes (11) prevent the team from secretly assuming one scenario is dominant — they have to commit numerically.

### Recurring high-frequency team optimization

**Goal**: A team runs frequently (daily / weekly) and you want to improve coordination rules.

```
Pre-requisite:
  - Team has been running long enough to have a benchmark task set.
  - There is an objective quality metric (or proxy: review pass rate,
    issue-found rate, customer signal).

Optimization protocol:
  game-theory:
    10 — evolutionary coordination search (ShinkaEvolve recommended for
         sample efficiency unless you have AlphaEvolve-scale budget)
    4 — DAG-Shapley scoring per run feeds the fitness signal
    5 — reputation gating updates between runs based on Shapley + calibration
    11 — calibration tracking informs reputation tier promotions
```

**Why**: Hand-tuned coordination rules drift. Evolutionary search (10) tunes them automatically against the fitness signal. ShinkaEvolve is the right starting framework for coordination-rule evolution (sample-efficient); reserve AlphaEvolve for algorithm-discovery use cases.

### Security or compliance review

**Goal**: Surface vulnerabilities and gaps. False negatives are catastrophic; false positives are merely costly.

```
Team launch:
  debate.method = courtroom
    Plaintiff: feature/system advocate
    Defense: red-team specialist
    Court: lead
    Critic: independent compliance reviewer
    Judicial Panel: synthesis owner
  masks:
    EVERY member wears Inversion ("how would we guarantee a breach/violation?")
  game-theory:
    14 — every claim cites specific evidence (CWE ID, regulation paragraph,
         log line) with credibility scoring
    13 — reasoning-tree audit at synthesis
    5 — Defense agent operates at Adversarial tier (output verified by
        independent member before synthesis)
```

**Why**: Security and compliance share a structural property — the cost of false negatives is asymmetric. Inversion mask + Adversarial tier (5) + credibility scoring (14) layer three independent guardrails. Reasoning-tree audit (13) ensures minority "this is broken" findings aren't outvoted by majority "looks fine" assessments.

### Cross-domain ambiguous question (no clear team match)

**Goal**: A question spans 2+ teams or doesn't fit the static decision map.

```
Two-stage routing:

Stage 1 — Team selection:
  game-theory 3 (auction task routing)
  Candidate members bid relevance + key insight preview.
  Orchestrator picks the team composition.

Stage 2 — Role assignment within the team:
  game-theory 16 (meta-debate routing)
  Members produce role-tailored proposals.
  Peer review picks which member fills which role.

Stage 3 — Run the actual debate with the routed lineup.
  debate.method = (whatever the question warrants — courtroom,
    dialectical, scenario, etc.)
```

**Why**: Auction (3) picks *who's on the team*; meta-debate (16) picks *who plays which position*. Cross-domain questions need both — neither alone is sufficient.

## Composition principles

A few rules of thumb when composing your own stacks:

1. **Don't compound skepticism.** Inversion + Devil's Advocate + Pre-Mortem on the same agent collapses into "everything fails." Distribute skeptical frames across different members or phases.
2. **One synthesis discipline per run.** Reasoning-tree audit (13), generative social choice (15), and Pareto-Nash (9) are alternatives, not compositions. Pick one based on whether the decision has a right answer (13), needs buy-in (15), or is genuinely multi-objective (9).
3. **Mask cost is low; debate-method cost is medium; game-theory mechanism cost is high.** When in doubt, add a mask first. Reserve adding game-theory mechanisms for runs where the cost-to-quality lift is justified.
4. **Track calibration across runs.** Almost every recipe ends with mechanism 4 (Shapley) or 11 (calibration tracking) post-run. The portfolio improvement compounds across many runs even if any single run's gain from these is small.
5. **Latent Debate as a quality gate (optional).** Single-model interpretability technique ([2512.01909](https://arxiv.org/abs/2512.01909)) — high mid-layer disagreement signals correlate with higher hallucination risk. Use as a flag on individual member outputs, not as a debate method itself.

## Related

- [`debate-methods/README.md`](debate-methods/README.md) — methods catalog
- [`decision-masks/README.md`](decision-masks/README.md) — masks catalog
- [`game-theory/README.md`](../../skills/universal/foundations-game-theory/assets/templates/game-theory/README.md) — mechanisms catalog
- [`../../references/game-theory-agent-teams.md`](../../skills/universal/agents-subagents/references/game-theory-agent-teams.md) — cross-cutting design notes for game-theoretic team mechanisms
- [`../../references/team-selection-guide.md`](../../skills/universal/agents-subagents/references/team-selection-guide.md) — first-pass static routing before any composition recipe applies
