---
description: Behavioral-economics decision rules for agent teams: blind first round, both frames in synthesis, justified defaults, base rates before probabilities, and mandatory dissent. Defensive hardening only.
last_verified: 2026-09-24
status: stable
---

# Behavioral Economics Applied to Multi-Agent Teams

> **Gate before invoking:** Check [`foundations-behavioral-economics` § When to Apply](../../foundations-behavioral-economics/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.

Anchoring, framing, defaults, social proof, discounting and choice architecture are explained in the [foundation's templates](../../foundations-behavioral-economics/assets/templates/behavioral-economics/). LLM members inherit these biases from their training text, and a team amplifies them because members defer to each other and to the orchestrator. This file is for hardening the team against its own bias, never for designing biased outputs aimed at users.

## Decision rules

1. **Blind first round.** Every member commits a position from the brief alone before reading any peer. Cross-reading starts only after all positions are logged. Sequential dispatch lets the first voice set the frame.
2. **State the verdict in both frames.** Synthesis writes a gain frame and a loss frame. If the verdict changes between them, don't commit; send it to debate.
3. **Justify the default explicitly.** The synthesis owner names which option is the status quo and labels the recommendation as "default, because …" or "active change, because …". Continuity is not a reason. A probability claim (failure, attack, churn rate) must state its base rate before the case-specific update.
4. **Mandatory dissent, and at most four options.** If no member dissents on the lead candidate, the owner assigns a devil's advocate for one round and answers the counter-case before committing. Agreement is not evidence of quality. Present three verdict options (primary, alternative, hold), not a binary and not a long unranked list. A deferral of cost beyond about 90 days needs a stated trade: effort now vs. effort later vs. value gained.

## Worked recipe — pre-synthesis bias sweep

```text
Synthesis owner, before committing:
1. Anchoring   did the first member's frame go unchallenged?        yes → re-frame
2. Frames      does the verdict flip between gain and loss frame?   yes → debate
3. Default     status quo chosen because it is familiar?            yes → justify or drop
4. Base rate   any probability claim without a prior?               yes → add prior
5. Deferral    any "fix later" without the now/later trade?          yes → state it
Any uncertain answer → one devil's-advocate round, then commit.

Output:  primary      <action> + rationale
         alternative  <second-best> + when it would beat primary
         hold         <wait posture> + unblocking signal + deadline
```

Manifest wiring, using fields the shipped `agents/teams/*/team.yaml` files already carry:

```yaml
coordination: { mode: belief-driven, blind_first_round: true, belief_brief: true }
debate:
  mandatory_dissent: true
  decision_masks: [anchoring-mask, base-rate-mask, inversion]   # agents/templates/decision-masks/
synthesis: { bias_audit_required: true, frame_symmetry: true, npv_check_for_deferrals: true }
verdict_options: [primary, alternative, hold]
```

## Related

- [debate-quickstart.md](debate-quickstart.md): devil's advocate and steel-manning methods.
- [decision-theory-applied.md](decision-theory-applied.md): the `hold` option and its deadline.
- [mast-failure-taxonomy.md](mast-failure-taxonomy.md): overlapping failure surface from a different lens.
