# Primitive: Context-Dependent Retrieval

## Definition

Memory retrieval is **cue-driven**. A learned association is most reliably retrieved when the cues present at retrieval match the cues present at encoding. The behavior or response is therefore **bound to the context** in which it was learned, not to the abstract goal alone.

Three converging empirical findings:
- **Encoding specificity principle** (Tulving & Thomson, 1973): retrieval depends on overlap between encoding context and retrieval context. A behavior is "remembered" — i.e., triggered automatically — to the extent its current context matches the original.
- **State-dependent and environment-dependent memory** (Godden & Baddeley, 1975; Smith & Vela, 2001): performance drops when the physical, sensory, or internal-state context shifts between encoding and retrieval, even when the underlying skill is intact.
- **Habit context-dependence** (Wood, Tam & Witt, 2005): when life circumstances change (move, new job, role change), even strong habits weaken because the contextual cues that triggered them are no longer present. This is a behavioral *opportunity* (good time to introduce new habits) and a *risk* (existing habits collapse).

Practical consequence: **a behavior that "the user knows how to do" is not the same as a behavior the user will perform.** Performance depends on the cue surface being present and stable.

## When to Use

- Migrations, redesigns, or platform shifts where existing user behavior could collapse because the cue context has changed.
- Designing for cross-device or cross-surface continuity (mobile / desktop / email / messaging) — each surface is a separate context unless the cue is replicated.
- Diagnosing why a feature with high adoption on one surface fails to transfer to another.
- Onboarding for users in **transition states** (new role, new tool, returning after dormancy) — cue overlap with prior usage will be minimal.
- Building reactivation flows for dormant users — the original context cues are weakened, so the reactivation cue must be re-anchored.

## Misuse Boundary

**Ethical use**: Replicate genuine task-relevant cues across contexts so users can perform behaviors they want to perform, regardless of where they are. Reactivation should target users with a real reason to return.

**Manipulation**: Engineering retrieval cues that have no relationship to user goals — pure-attention-capture push notifications, location-based prompts that don't serve the user's stated purpose, dark-patterned re-engagement aimed at users who have implicitly disengaged. Re-anchoring a dormant user back to the product is ethical only when the dormancy was non-rejection (cue collapse, not opt-out).

**Required conditions**:
1. Cross-surface cue replication serves a user-acknowledged behavior, not an engagement metric in isolation.
2. Users can identify and disable any artificial cue (notification, location prompt, calendar injection).
3. Re-engagement of dormant users distinguishes between "lost the cue" and "left the product." The latter must be respected.
4. UK GDPR + PECR: any contextual cue using personal data (location, behavior history) requires lawful basis and a genuine user benefit; legitimate-interest assertions for engagement-only purposes are weak.

## Inputs

- The contexts in which the behavior currently fires (which device, surface, time, preceding action).
- The contexts in which the behavior is desired but does not fire.
- The cues available in each context.
- The user's stated goal and whether the behavior serves it.

## Outputs

- A cue map: target behavior → contexts where it should fire → cues available in each context.
- A cue replication / migration plan for any change that disrupts existing cues.
- A reactivation strategy for dormant users that re-establishes the cue or replaces it with an honest substitute.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| App redesign caused a sharp drop in retention even though features are unchanged | Visual cues (icon position, layout, navigation entry) were the contextual triggers; they have changed, the habit has decayed | Stage UI changes; preserve the dominant cue (icon position, primary entry path) across at least one major release; instrument cue-conditional retention |
| Mobile feature has high usage; web version of the same feature is ignored | Behavior is bound to the mobile context only; no cross-context retrieval | Mirror the cue surface — equivalent entry point, similar visual prominence, parallel notification path |
| Push notifications drive opens but no engagement | Notification has become a context-free cue with no goal-relevance — extinction of the prediction | Replace generic prompts with cues tied to a specific user-relevant state; remove notifications that do not pass a goal-relevance test |
| Returning user (dormant 90+ days) churns immediately on reactivation | Reactivation re-exposes the user to old context cues but the underlying habit has decayed; the user is treated as returning rather than as new | Treat 90+ day dormant users as new-onboarding cohort; re-build cue→routine→reward rather than assuming retrieval |
| Power users break when the keyboard shortcut or click target moves by 8 pixels | Highly automated behavior is bound to fine-grained motor/visual cues | Treat motor-level cue shifts as breaking changes; deprecate with overlap, not replacement |

## Worked Example

**Scenario**: A workflow tool plans a major UI redesign. The team is worried about retention drop on a mature user base.

Context-dependent retrieval design:
- **Cue audit**: Identify the top three behaviors driving 80% of value (e.g., "create item," "review queue," "complete daily round-up"). For each, document the contextual cues currently triggering them — entry-point icon, navigation path, keyboard shortcut, notification timing.
- **Preserve**: Hold the strongest cue per behavior constant across the redesign (e.g., the icon position, the primary keyboard shortcut, the notification time-of-day). Change everything else.
- **Stage**: Roll out the redesign with the old surface available as a fallback for one full retention cycle (often 2–4 weeks). Measure cue-conditional retention by behavior, not just session count.
- **Detect collapse early**: Set an alert on cue-conditional completion rate per behavior. If a behavior's completion rate drops more than X% within Y days, the cue migration has failed and a partial rollback or cue restoration is required.
- **Reactivation cohort**: Users who lapse during the migration are routed through a re-anchoring flow, not a generic re-engagement flow.

**Anti-pattern check**: The team is not adding new cues to drive engagement; it is preserving the cues users already rely on. The reactivation cohort is offered a clear opt-out.

## Sources

- Tulving, E. & Thomson, D. M. (1973). Encoding specificity and retrieval processes in episodic memory. _Psychological Review_, 80(5), 352–373. — foundational paper on cue-dependence of retrieval.
- Godden, D. R. & Baddeley, A. D. (1975). Context-dependent memory in two natural environments: On land and underwater. _British Journal of Psychology_, 66(3), 325–331. — environment-dependent recall.
- Smith, S. M. & Vela, E. (2001). Environmental context-dependent memory: A review and meta-analysis. _Psychonomic Bulletin & Review_, 8(2), 203–220. — meta-analysis of context effects.
- Wood, W., Tam, L. & Witt, M. G. (2005). Changing circumstances, disrupting habits. _Journal of Personality and Social Psychology_, 88(6), 918–933. — habits collapse when context changes; transition states are habit-formation windows.
- Neal, D. T., Wood, W., Wu, M. & Kurlander, D. (2011). The pull of the past: When do habits persist despite conflict with motives? _Personality and Social Psychology Bulletin_, 37(11), 1428–1437. — context-cue dominance over motivation in habitual behavior.
