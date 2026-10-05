# Primitive: Reinforcement Schedules

## Definition

A **reinforcement schedule** specifies the temporal or count-based pattern that connects a behavior to its reward. The schedule, not just the reward, determines how strongly and how durably the behavior is acquired and maintained. Skinner's four canonical schedules (Ferster & Skinner, 1957):

| Schedule | Reward Delivered | Behavioral Signature |
|---|---|---|
| **Fixed-Ratio (FR)** | After every Nth response | Burst of activity, pause after reward |
| **Variable-Ratio (VR)** | After an unpredictable number of responses (mean N) | High, steady response rate; **most resistant to extinction** |
| **Fixed-Interval (FI)** | After a fixed time has elapsed | Scalloped pattern: low activity early, ramp before deadline |
| **Variable-Interval (VI)** | After unpredictable time intervals (mean T) | Steady, moderate response rate |

Two empirical results that drive product design:
- **Partial-reinforcement extinction effect**: behavior reinforced intermittently is *more* resistant to extinction than behavior reinforced every time. Continuous reinforcement (CRF) trains fast but extinguishes fast; variable schedules train slower but persist.
- **Dopamine prediction error** (Schultz, 1997; Glimcher, 2011): the brain's reward signal encodes the *gap between expected and received reward*. Predictable rewards stop generating a dopamine response once the prediction stabilizes. Unpredictable rewards keep generating prediction error and remain motivationally potent — this is the mechanism behind the engagement power of variable-ratio schedules.

The variable-ratio schedule is the lever behind slot machines, social-media feeds, and loot boxes. **It is also the schedule most likely to cross from habit formation into compulsion.** Treat it as a regulated tool with explicit ethical bounds.

## When to Use

- Designing rewards, streaks, or recognition systems that need to maintain behavior past initial novelty.
- Diagnosing why an engagement system "worked at first" then collapsed (likely CRF — extinguishes fast once the reward becomes predictable).
- Choosing between time-gated and action-gated rewards (FI vs FR) for daily-cadence products.
- Auditing existing reward systems for unintended variable-ratio patterns that may be driving compulsive use.

## Misuse Boundary

**Ethical use**: Match the schedule to a behavior the user has endorsed, with a reward that reflects real progress toward the user's goal. Variable-interval schedules (mean-time-based) are generally lower-risk than variable-ratio (count-based with no upper bound).

**Manipulation**: Variable-ratio schedules attached to non-essential actions (refresh-to-discover, pull-to-refresh feed surfaces, gachapon mechanics, lootboxes) are the canonical compulsion-design pattern. Particular care is required when:
- The user reports inability to stop.
- The schedule is paired with sunk-cost mechanics (collections, streaks that reset to zero).
- Minors are in the population — UK PEGI / ASA / ICO Children's Code apply additional constraints.
- The reward is monetary or convertible to real-world value (UK Gambling Act 2005 implications).

**Required conditions**:
1. Default to **fixed schedules** (FR or FI) for habit formation. Use variable schedules only when there is a documented user-benefit reason and the system-level engagement metric is not the primary goal.
2. Variable schedules must have a **rate cap** — a maximum frequency at which the unpredictable reward can fire — and the cap must be transparent on request.
3. No variable-ratio reward attached to spending real money on a randomized outcome without the loot-box / probability disclosures required by jurisdiction (UK ASA, EU DSA, several US states).
4. Streaks and counters that reset to zero on a single miss are a sunk-cost manipulation — provide grace-day or pause mechanisms.
5. Children's Code (UK ICO): variable-ratio reward design directed at under-18 users requires data-protection impact assessment and is presumptively a high-risk pattern.

## Inputs

- The behavior being shaped.
- The available reward types (tangible, informational, social).
- The cadence at which the behavior can realistically occur.
- The population (adult / mixed / minor).
- The platform's regulatory exposure (UK, EU, sector-specific).

## Outputs

- A schedule specification: type (FR/VR/FI/VI), parameter (N or T), and rate cap.
- An extinction plan: how the schedule winds down or transitions if the user disengages from the underlying goal.
- An audit record of the ethical-bound check, especially for any variable-ratio component.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Reward system drives big launch then collapses in week 2 | Continuous reinforcement (CRF) — every action rewarded — extinguishes once the dopamine prediction stabilizes | Switch to fixed-ratio with N≥3, or fixed-interval daily, after the acquisition phase |
| Engagement is high but user satisfaction surveys decline | Variable-ratio schedule has produced compulsion without value — usage rises while reported well-being falls | Cap firing rate; add session-end interventions; remove the VR component if value is not measurable |
| Streak system increases stress and rage-quits | Fixed-ratio with reset-to-zero loss creates sunk-cost panic, especially after a missed day | Add grace days; show streak as best-of-week or rolling-7-day, not strict daily |
| Daily reward fades in motivational power after months | Fixed-interval prediction has stabilized; no prediction error, no dopamine response | Add a small variable-interval component (e.g. occasional surprise feature unlock) within capped bounds |
| Variable-ratio system was added without an ethical review and is now central to retention | Schedule was chosen for engagement metrics, not user goal | Document the harm-test failure; design a transition to a fixed schedule even if engagement drops short-term |

## Worked Example

**Scenario**: A productivity tool wants to reward users for completing daily tasks without engineering a slot-machine pattern.

Schedule choice:
- **Daily completion**: Fixed-interval (FI-1 day). The user gets a clear daily progress summary at end-of-day. Predictable, transparent, low compulsion risk.
- **Weekly milestone**: Fixed-ratio (FR-5 days complete in a week). Predictable, gives a clear goal, transitions cleanly to a habit.
- **Surprise component (optional)**: Variable-interval with a hard cap of one surprise per week (rate cap), where the surprise is non-monetary (a useful feature unlock, a relevant tip, a small visual flourish). VI is preferred over VR because the reward is time-bounded, not action-bounded — the user cannot grind for it.

What is **not** done:
- No infinite-scroll feed with VR rewards.
- No streak that resets to zero on a single miss.
- No randomized rewards tied to payment or to time-limited "boosts" the user can purchase.

**Ethical-bound check**: The system passes the harm test — the schedule is disclosed in the help text, the surprise rate is capped, and the user can disable surprises in settings.

## Sources

- Ferster, C. B. & Skinner, B. F. (1957). _Schedules of Reinforcement_. Appleton-Century-Crofts. — canonical taxonomy of reinforcement schedules and the partial-reinforcement extinction effect.
- Schultz, W., Dayan, P. & Montague, P. R. (1997). A neural substrate of prediction and reward. _Science_, 275(5306), 1593–1599. — dopamine as prediction-error signal.
- Glimcher, P. W. (2011). Understanding dopamine and reinforcement learning: The dopamine reward prediction error hypothesis. _PNAS_, 108 (Suppl. 3), 15647–15654. — modern synthesis of the prediction-error account.
- Eyal, N. (2014). _Hooked: How to Build Habit-Forming Products_. Portfolio. — applied product use of variable rewards (read critically alongside the misuse-boundary literature).
- Schüll, N. D. (2012). _Addiction by Design: Machine Gambling in Las Vegas_. Princeton University Press. — VR-schedule compulsion mechanics; the dark-pattern reference text.
- UK Information Commissioner's Office. _Age-Appropriate Design Code (Children's Code)_, Standard 13 ("Detrimental use of data") and Standard 14 ("Nudge techniques"). — regulatory boundary on engagement-design directed at minors.
