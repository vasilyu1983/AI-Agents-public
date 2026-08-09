# Mechanism: Cooperation and Defection in Teams

## Domain Applications

- **Partnership incentive design**: model the partnership as iterated PD; align payoff structure so cooperation (delivering agreed value) dominates defection (cost-shifting, scope dumping) as a Nash strategy.
- **Platform ecosystem**: platform and developer face a cooperation game; platform's payoff structure determines whether developers invest in quality or extract value.
- **Compliance programs**: employees face PD between compliance cost and detection risk; payoff-scale testing identifies whether incentive structure supports cooperation.
- **Agent teams**: members face cooperation game; belief briefs + Shapley tracking make cooperation the dominant strategy by detecting free-riding.

## Prisoner's Dilemma in Agent Teams

Members face a cooperation game:

| | Other Members Invest Effort | Other Members Free-Ride |
|---|---|---|
| **You Invest Effort** | High-quality team output — best for all | You carry the team — your output quality drops due to overload |
| **You Free-Ride** | Others cover for you — you look good cheaply | Poor team output — worst for all |

## How "Defection" Manifests in Agent Teams

| Defection Behavior | How It Appears | Detection |
|-------------------|----------------|-----------|
| **Shallow analysis** | Generic statements without evidence | Check: does output reference specific data from context? |
| **Scope dumping** | Member punts hard questions to synthesis | Check: does member address the hard part of their brief? |
| **Echo-chambering** | Restating another member's point as own | Check: is contribution unique per Shapley assessment? |
| **Confidence inflation** | Stating high confidence without evidence | Check: evidence cited per claim ratio |

## Sustaining Cooperation

| Mechanism | How | Maps To |
|-----------|-----|---------|
| **Clear ownership** (already in your system) | Each member has distinct deliverable | Eliminates free-riding opportunity |
| **Belief briefs** (ECON pattern) | Members know what others will cover | Eliminates duplication incentive |
| **Shapley scoring** | Marginal contribution is measured | Makes free-riding detectable |
| **Reputation tiers** | Low contributors get more oversight next time | Creates long-term cooperation incentive |

## Measuring Defection Tendency Before You Need It (FAIRGAME)

The mitigations above react to defection observed in real runs. For high-stakes teams, you can also **measure defection tendency upfront** with FAIRGAME-style probes (Fair Assessment of Inter-agent Reasoning in Repeated Games, 2025–26):

| Probe | What it tests | Defect signal |
|---|---|---|
| **Payoff-scaled iterated Prisoner's Dilemma** (10–20 rounds) | Can the member sustain cooperation when defection has higher single-round payoff? | Switches to defection when cumulative score is behind, even after cooperative history |
| **Multi-agent Public Goods Game** (3+ members, dynamic payoff) | Does the member free-ride on others' contributions? | Member's contribution drops when group total is already high |
| **Asymmetric-information variant** | Does the member exploit private information rather than share it? | Withholds context that would help peers, then claims credit later |

**Operator rules:**

- Run probes **once per member, once per quarter**, not per task — these are profile tests, not gates.
- Use the **same model + same system prompt** the member runs in production. Probing a stripped-down variant doesn't transfer.
- A member with high defection tendency isn't disqualified — it's a **deployment constraint**: pair them with stricter Shapley scoring and lower trust tier in mechanism #5.

This shifts the cooperation problem from "detect defection in the trace" (hard, after-the-fact) to "predict defection from member identity" (cheaper, structural). Pair with reputation gating (#5) and Shapley scoring (#4) for the full loop.

Source: Game-Theoretic Lens on LLM-MAS, arXiv 2601.15047 §"FAIRGAME framework" — [arxiv.org/abs/2601.15047](https://arxiv.org/abs/2601.15047). Note: this is a measurement methodology, not a runtime mechanism — its output feeds the trust tier in mechanism #5.

## SPNE Free-Riding Fix (MAC-SPGG)

FAIRGAME probes measure defection tendency; MAC-SPGG eliminates it structurally by redesigning the public-goods reward so effortful contribution is the unique Subgame Perfect Nash Equilibrium at every decision node.

**When to use**: standard FAIRGAME probing shows high free-rider risk, or the team is an LLM ensemble where symmetric payoffs create classic free-rider equilibria.

**Recipe**: Convert the parallel public-goods game into a Sequential Public Goods Game — agents move in sequence, each observing predecessors' outputs. Reward structure is calibrated so effortful contribution dominates at every node (not just in expectation), making defection non-credible even for the last mover.

**RL training recipe**: MAC-SPGG [NeurIPS 2025 + AAMAS 2026] provides the reinforcement-learning training loop: instantiate the sequential game, define effortful contribution as the reward signal, train until SPNE emerges. Reported to outperform single-agent baselines, CoT prompting, and standard cooperative methods across reasoning, math, code generation, and NLP.

**Boundary condition**: sequential observation creates a latency chain — each agent must wait for its predecessor. Do not apply in hard-latency-bound pipelines where parallel emission is required. Also assumes agents with stable utility under the reward signal; verify SPNE proof assumptions hold for the specific ensemble.

Source: arXiv 2508.02076, NeurIPS 2025 + AAMAS 2026.

**Learning-in-games note**: INPO (ICLR 2025 Oral, arXiv 2407.00617) frames RLHF itself as a symmetric two-player zero-sum game and applies online mirror descent (no-regret self-play) to converge to a Nash policy without explicit win-rate estimation — bridging classic learning-in-games theory (#6, #10, #11) with LLM alignment.

## Correcting the Tit-for-Tat Myth (Axelrod, 1980–81)

The composition recipe above and the "tit-for-tat sufficient" shorthand in `SKILL.md` trace back to Robert Axelrod's iterated-Prisoner's-Dilemma tournaments. The commonly repeated version of this story is looser than what actually happened:

- **What happened**: Anatol Rapoport's Tit-for-Tat (start cooperative, then mirror the opponent's last move) won both of Axelrod's round-robin tournaments (200-round pairings, summed scores across all entrants) against a field of far more complex submitted strategies. Axelrod and Hamilton then used this to argue reciprocity can sustain cooperation among purely self-interested players without central enforcement (Axelrod & Hamilton, *Science*, 1981).
- **What did *not* happen**: Tit-for-Tat was not proven to be a universally optimal or dominant strategy, and it does not win every environment. It performs poorly under noisy/error-prone execution (a single misread move can trigger a costly retaliation spiral — "generous" or "contrite" Tit-for-Tat variants were later developed specifically to fix this), and it can be beaten by coordinated strategy pools (in a widely cited 2004 rerun, a team from Southampton entered multiple strategies that recognized each other via opening move sequences and let some members deliberately lose to boost others — closer to a designed coalition than to a single "best" strategy). Tit-for-Tat's tournament win is also a two-tournament, specific-payoff, perfect-monitoring result — it is evidence for reciprocity as *a* robust mechanism, not a proof that it is *the* equilibrium.
- **Applied implication for this mechanism**: treat "tit-for-tat sufficient" (SKILL.md composition recipe) as an operationally cheap default under perfect, low-noise monitoring of counterpart behavior — not as a game-theoretic guarantee. Under noisy monitoring (you can only infer a partner's "effort" from a lagging or partial signal), use a more forgiving variant or fall back to reputation gating (#5) and explicit evidence collection rather than strict reciprocity.

Source: Axelrod & Hamilton, "The Evolution of Cooperation," *Science* 211(4489):1390-1396, 1981. [doi.org/10.1126/science.7466396](https://www.science.org/doi/10.1126/science.7466396)

## Related

- [`01-econ-belief-driven.md`](01-econ-belief-driven.md) — belief briefs eliminate duplication incentive
- [`04-shapley-contribution.md`](04-shapley-contribution.md) — makes free-riding measurable
- [`05-reputation-gating.md`](05-reputation-gating.md) — creates long-term cooperation incentive
- [`17-online-shapley-prompt-evolution.md`](17-online-shapley-prompt-evolution.md) — auto-mutate underperforming members' prompts based on Shapley signal
