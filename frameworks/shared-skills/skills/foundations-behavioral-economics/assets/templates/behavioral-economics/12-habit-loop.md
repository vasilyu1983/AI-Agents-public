# Primitive: Habit Loop (Cue → Routine → Reward)

## Definition

A habit is a learned association in which a stable contextual **cue** automatically triggers a **routine** (behavior) that has historically produced a **reward**. With repetition, control of the routine shifts from the goal-directed prefrontal system to the stimulus-response system (dorsolateral striatum / basal ganglia). The behavior becomes context-driven and largely insensitive to the current value of the outcome.

Two-system model (Wood & Rünger, 2016; Hardwick et al., 2019; Robbins & Costa, 2017):
- **Goal-directed system** — slow, prefrontal, evaluates outcomes; sensitive to reward devaluation. Drives early performance of a new behavior.
- **Stimulus-response (habit) system** — fast, striatal, triggered by cues; largely insensitive to current reward value. Takes over after repeated cue-routine-reward pairing in stable contexts.

Practical implications:
- Behaviors that depend on motivation, reminders, or willpower are still goal-directed — they collapse under cognitive load, stress, or context change.
- Behaviors that fire automatically on a stable cue persist even when motivation is absent. **Retention at scale is a habit-system outcome, not a motivation-system outcome.**
- Habit formation is **context-bound**: change the cue (new device, new role, removed icon, layout change) and the habit weakens or extinguishes.

The "21 days" claim is folk-myth. Median time-to-automaticity in field studies is ~66 days for daily behaviors, with a wide range (Lally et al., 2010).

## When to Use

- Any product or workflow whose value depends on **recurring user action** — daily check-in, weekly review, recurring task completion, repeat purchase, repeat session.
- Designing onboarding when first-week activation must convert to durable usage.
- Diagnosing why retention curves drop sharply after week 2–4 (the period when motivation fades but habit has not yet formed).
- Internal tooling and B2B workflows where adoption depends on getting the behavior into a stable cue (calendar event, Slack notification, standup).
- Migrations where an established habit is at risk because the cue is changing (new UI, replaced tool, role change).

## Misuse Boundary

**Ethical use**: Build habits around behavior the user has stated they want to perform. Make the cue legible, the reward honest, and the exit easy. The user should be able to recognize the habit when asked and abandon it without friction.

**Manipulation**: Engineering habits the user did not endorse — slot-machine notification patterns, doomscroll loops, compulsive-checking designs. The fingerprint of dark-pattern habit design: the user reports trying to stop and being unable to, and the habit is structurally hard to extinguish (cue is everywhere, reward is variable, exit is buried). See also primitive #13 (reinforcement schedules) — variable-ratio schedules are the specific lever that crosses this line.

**Required conditions**:
1. The user has a stated goal that the habit serves.
2. The cue is observable and legible — the user can identify what triggered the behavior.
3. The reward is real and matches the user's goal, not a substitute reward (a streak counter that has no relationship to the user's actual outcome is a fake reward).
4. The user can disable the cue (notification, reminder, icon) and the habit then decays naturally.
5. UK context: ASA CAP Code and CMA guidance on engagement design require that habit-forming features cannot be presented as user-benefit when their actual purpose is operator engagement metrics.

## Inputs

- Stable contextual cue available to the user (time of day, location, preceding action, system event, notification).
- A routine that produces a real outcome the user wants.
- A reward delivered in close temporal proximity to the routine.
- A repetition cadence the user can sustain (daily and weekly cadences form habits faster than weekly-only or sparse cadences).

## Outputs

- A specified cue → routine → reward triple, instrumented so cue exposure and routine completion can be measured.
- An expected time-to-automaticity range (typically 4–12 weeks for daily behaviors).
- A retention metric tied to the habit (cue-conditional completion rate, not just session count).

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Strong week-1 engagement, sharp dropoff at week 2–4 | Goal-directed system carried the behavior; cue is unstable or absent | Identify a stable cue and bind the routine to it before motivation fades |
| Users complete the routine but the habit collapses on a context change | Habit was bound to a fragile cue (specific screen position, specific notification copy) | Bind to durable cues (time of day, calendar event, an action the user already does daily) |
| Streak/reward exists but doesn't drive durable behavior | Reward is decoupled from the user's actual outcome — counter inflation, not real progress | Make the reward observable in the user's life, not just in the product |
| Habit doesn't generalize across devices or surfaces | Context-bound encoding; cue exists on one surface only | Replicate the cue across surfaces (mobile + desktop + email) so context shifts don't extinguish the habit |
| Power users want to disable the loop and can't | The exit path is hidden — habit design has crossed into dark-pattern territory | Make notification/reminder controls one tap away; honor the disable signal |

## Worked Example

**Scenario**: A B2B project-management tool has 70% week-1 activation but 22% week-4 retention. Diagnosis: users complete onboarding (goal-directed), but no habit forms.

Habit-loop application:
- **Cue**: Daily 9:00 AM standup calendar event (existing user routine, not a new artifact).
- **Routine**: Open the tool's "Today" view. The view is generated automatically and ready by 8:55 AM.
- **Reward**: A 30-second visible-progress signal — yesterday's checked-off items, today's three priorities pre-staged. The reward must be the user's own outcome being clear, not gamification.
- **Cadence**: Daily Mon–Fri.
- **Measurement**: Cue-conditional completion rate (of users with the calendar integration enabled, % who open the Today view by 9:30 AM). Track by week-of-tenure to detect when the cue-routine binding stabilizes.

**Anti-pattern check**: Don't add a streak counter on the Today view — that's a substitute reward (#13 misuse). The reward is the user seeing their own work-state clearly.

## Sources

- Wood, W. & Rünger, D. (2016). Psychology of habit. _Annual Review of Psychology_, 67, 289–314. — modern review of habit psychology.
- Lally, P., van Jaarsveld, C. H. M., Potts, H. W. W. & Wardle, J. (2010). How are habits formed: Modelling habit formation in the real world. _European Journal of Social Psychology_, 40(6), 998–1009. — field measurement of time-to-automaticity (median ~66 days).
- Hardwick, R. M., Forrence, A. D., Krakauer, J. W. & Haith, A. M. (2019). Time-dependent competition between goal-directed and habitual response preparation. _Nature Human Behaviour_, 3, 1252–1262. — competition between the two systems under time pressure.
- Robbins, T. W. & Costa, R. M. (2017). Habits. _Current Biology_, 27(22), R1200–R1206. — neural circuitry: dorsolateral striatum and the habit system.
- Wood, W., Mazar, A. & Neal, D. T. (2022). Habits and goals in human behavior: Separate but interacting systems. _Perspectives on Psychological Science_, 17(2), 590–605. — recent synthesis of dual-system habit theory.
