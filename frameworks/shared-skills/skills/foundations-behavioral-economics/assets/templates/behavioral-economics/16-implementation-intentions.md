# Primitive: Implementation Intentions & Habit Stacking

## Definition

An **implementation intention** is a self-authored if-then plan of the form **"When situation X arises, I will perform response Y."** It commits the actor in advance to a specific behavior in response to a specific cue, transferring control of the behavior from goal pursuit (slow, effortful, motivation-dependent) to cue-driven retrieval (fast, automatic, motivation-independent). Gollwitzer (1999, 2014).

Empirical findings:
- Implementation intentions roughly **double or triple** the rate of goal completion across health, academic, and workplace domains (Gollwitzer & Sheeran, 2006, meta-analysis: d ≈ 0.65 across 94 studies).
- The effect operates by linking a mental representation of the cue (X) to a mental representation of the response (Y), so when X occurs, Y is automatically retrieved and initiated.
- The plan must be **specific** (concrete cue, concrete response). Vague intentions ("I will exercise more") have no effect; specific if-then formulations ("When I sit down at my desk on Monday, I will open the planning view") have large effects.

**Habit stacking** (Clear, 2018, drawing on Lally et al., 2010) is a popularised form of the same principle: anchor a new behavior to an existing well-established behavior. The pre-existing routine supplies the cue.

| Comparison | Defaults (#4) | Implementation Intentions (#16) |
|---|---|---|
| Authorship | Set by designer | Authored by the user |
| Trigger | "Do nothing" path | A specific situational cue |
| Mechanism | Inertia toward pre-set | Pre-committed cue→response binding |
| Best for | Static configuration | Recurring behaviors that need to fire on a cue |

## When to Use

- New-behavior adoption where the user has stated a goal but does not yet have a cue (most onboarding for habit-forming products).
- Goal-pursuit features (savings, study, exercise, focus, recurring task completion).
- Bridging the early "motivation" phase before a habit has formed (see #12 habit loop) — the implementation intention provides the artificial cue that scaffolds the real habit.
- Migration / transition states where users need to re-anchor a behavior to a new context (see #15).
- Internal-tooling rollouts where a behavior must fit into an existing work routine (standup, weekly review, on-call rotation).

## Misuse Boundary

**Ethical use**: Help the user create plans that serve goals the user has stated. The user authors the if-then, or selects from options that match a goal they've articulated. The plan can be edited or revoked by the user.

**Manipulation**: Pre-filling implementation intentions for the user's "future self" without true consent — committing them to behavior they did not endorse. Using if-then framing to lock users into recurring engagement with no edit path. Generating plans whose response behavior serves the platform's metrics rather than the user's stated goal.

**Required conditions**:
1. The goal that the implementation intention serves is explicitly stated by the user, not assumed.
2. The user can edit, snooze, or remove the plan at any time.
3. Recommended cues are stable and observable (existing routines, calendar events, scheduled times) — not engineered cues whose only purpose is engagement.
4. The system does not silently expand an implementation intention into adjacent behaviors the user did not author.
5. UK regulatory context: any "commitment" framing must remain genuinely revocable; framing that relies on guilt or perceived loss of investment moves into reactance / dark-pattern territory.

## Inputs

- A specific user-stated goal.
- An existing stable cue available to the user (time, location, preceding action, calendar event).
- The desired response behavior, specified concretely.
- Optional: a fallback ("If I miss the cue, I will...") to absorb single-instance failures without extinguishing the plan.

## Outputs

- A specific if-then plan, authored by or co-authored with the user.
- An instrumented cue and response so cue-conditional completion can be measured.
- An edit / opt-out path the user can find within one tap.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Plan is set up and never fires | Cue is too vague ("when I have time") or is not observable | Re-specify the cue: a clock time, a calendar event, an action the user already does daily |
| Plan fires but user doesn't perform the response | Response is too effortful for the cue moment, or requires a separate context shift | Match response effort to cue context (a 30-second action for a passing cue; a 5-minute action only for a deliberate-attention cue) |
| Goal is achieved early; plan continues to fire and becomes friction | No exit condition was set | Add a review/expiry built into the plan ("review after 4 weeks"); the plan should be designed to retire itself or convert to a habit |
| User abandons after one missed instance | Single-failure → "I'm bad at this" → plan revoked | Build in a fallback ("If I miss it, I will pick it up at next week's review") and a no-blame restart |
| Pre-filled plans drive low completion | The user did not author the plan; mental representation is not bound | Make plan creation a deliberate user step; offer templates as starting points, not finished products |

## Worked Example

**Scenario**: A finance app wants users to review their spending weekly. Generic reminders have a 12% completion rate.

Implementation-intentions design:
- **Goal capture**: At onboarding, the user states whether weekly review is a goal. If not, the feature is not pushed.
- **Plan authoring**: The user is offered a template — "When [day] at [time], I will open the weekly review." Defaults: Sunday evening or Monday morning. The user adjusts day/time. The user can additionally select a cue anchor (calendar event, end of an existing routine).
- **Plan structure**: The plan is stored as a calendar event with the action embedded as a deep link. The cue fires through the user's existing calendar surface, not a new notification stream.
- **Fallback**: "If I miss the review, I will do it the next time I open the app." This single line typically prevents abandonment after a missed week.
- **Exit / review**: After 4 weeks, the user is asked whether the review is now a habit, should continue with the plan, or should be removed.
- **Measurement**: Cue-conditional completion (of users with the plan, % who completed the review within 24h of the cue), week-over-week. Compare against the no-plan control cohort.

**Anti-pattern check**: The user authored the plan. The cue rides on the user's existing calendar — no new engagement channel was manufactured. The plan retires itself if not useful.

## Sources

- Gollwitzer, P. M. (1999). Implementation intentions: Strong effects of simple plans. _American Psychologist_, 54(7), 493–503. — original formulation.
- Gollwitzer, P. M. & Sheeran, P. (2006). Implementation intentions and goal achievement: A meta-analysis of effects and processes. _Advances in Experimental Social Psychology_, 38, 69–119. — meta-analysis: d ≈ 0.65 across 94 studies.
- Gollwitzer, P. M. (2014). Weakness of the will: Is a quick fix possible? _Motivation and Emotion_, 38, 305–322. — modern review and limits.
- Lally, P., van Jaarsveld, C. H. M., Potts, H. W. W. & Wardle, J. (2010). How are habits formed: Modelling habit formation in the real world. _European Journal of Social Psychology_, 40(6), 998–1009. — anchoring new behaviors to existing routines (the empirical basis for habit stacking).
- Adriaanse, M. A., Vinkers, C. D. W., De Ridder, D. T. D., Hox, J. J. & De Wit, J. B. F. (2011). Do implementation intentions help to eat a healthy diet? A systematic review and meta-analysis of the empirical evidence. _Appetite_, 56(1), 183–193. — domain-specific meta-evidence.
