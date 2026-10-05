---
description: Agent-team applied layer for game-theory mechanisms. The 22 canonical mechanism playbooks live in foundations-game-theory, with the shared-payoff aggregation ones in foundations-team-theory; this file keeps the default team stack, when to switch on the others, and the team.yaml wiring.
last_verified: 2026-09-24
status: stable
---

# Game Theory — Agent-Team Applied Recipe Layer

> **Gate before invoking:** Check [`foundations-game-theory` § When to Apply](../../foundations-game-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.

All 22 mechanisms (belief-driven coordination, debate, auctions, Shapley, reputation, BMV, RCS, conformal act/escalate, attested delegation, coalition routing and the rest) have one canonical playbook each. Incentive mechanisms live in the [game-theory templates](../../foundations-game-theory/assets/templates/game-theory/); the shared-payoff aggregation mechanisms (belief-driven coordination, debate, courtroom, prediction market, reasoning-tree audit, meta-debate routing, BMV, RCS, conformal act/escalate) moved to the [team-theory templates](../../foundations-team-theory/assets/templates/team-theory/). The foundation's mechanism map and selection checklist sit in its [SKILL.md](../../foundations-game-theory/SKILL.md). This file keeps only the team-level choices.

## Decision rules

1. **Default stack for every team.** Give each member a belief brief naming its lane and what peers cover, so members don't all produce the same analysis ([01](../../foundations-team-theory/assets/templates/team-theory/01-econ-belief-driven.md)). Make dissent a required synthesis section ([07](../../foundations-game-theory/assets/templates/game-theory/07-mechanism-design-synthesis.md)). Synthesize by reasoning-tree audit, not majority vote ([13](../../foundations-team-theory/assets/templates/team-theory/13-reasoning-tree-audit.md)): members share training biases, so correlated errors pass a vote.
2. **Debate on trigger only.** Run debate when named conditions fire (a finding conflicts with another member's recommendation, confidence is split), never on agreement ([02](../../foundations-team-theory/assets/templates/team-theory/02-adversarial-debate.md)). For a genuine continuous trade-off, use negotiation instead of debate ([12](../../foundations-game-theory/assets/templates/game-theory/12-negotiation-zopa-batna.md)).
3. **Consensus is not permission to act on high-stakes or irreversible work.** Use conformal act/escalate: a single-answer set acts, a multi-answer set escalates ([20](../../foundations-team-theory/assets/templates/team-theory/20-conformal-social-choice.md)). For best-of-N selection, use BMV for discrete answers and RCS for open-ended ones ([18](../../foundations-team-theory/assets/templates/team-theory/18-beyond-majority-voting.md), [19](../../foundations-team-theory/assets/templates/team-theory/19-radial-consensus-score.md)).
4. **Scale mechanisms with team size and trust.** At 6+ members or with separable workstreams, route through coalitions with local leads instead of a flat panel ([22](../../foundations-team-theory/assets/templates/team-theory/22-coalition-formation-routing.md)). When a delegate can self-claim capability, require an attested contract before auction or reputation routing ([21](../../foundations-game-theory/assets/templates/game-theory/21-attested-delegation-contracts.md)). After each run, record a Shapley-style contribution note to find free-riders and to rotate composition ([04](../../foundations-team-theory/assets/templates/team-theory/04-shapley-contribution.md)).

## Worked recipe — launch prompt and manifest

```text
Goal: <decision/review/diagnosis>      Context: <required inputs>
Belief briefs:
  member-1: focus on X. Expect member-2 to cover Y. Don't duplicate.
  member-2: focus on Y. Challenge member-1 if <condition>.
  member-3: focus on Z. Flag gaps neither 1 nor 2 would catch.
Debate: only when <trigger conditions>
Synthesis: reasoning-tree audit, dissent section required
Each finding: confidence (high/medium/low) + evidence; "insufficient evidence" is a valid output
After synthesis: contribution note per member
```

```yaml
coordination: { mode: belief-driven, belief_brief: true }
debate: { enabled: true, triggers: [<conditions>] }
synthesis: { protocol: reasoning-tree, dissent_required: true, confidence_calibration: true }
trust: { default_tier: standard }
```

These fields appear in the shipped `agents/teams/*/team.yaml` files. Act/escalate, attested delegation and coalitions have no manifest field yet; state them in the launch prompt.

## Related

- [decision-theory-applied.md](decision-theory-applied.md): which aggregation rule to use.
- [behavioral-economics-applied.md](behavioral-economics-applied.md): mandatory dissent and blind first rounds.
- [debate-quickstart.md](debate-quickstart.md): debate formats.
