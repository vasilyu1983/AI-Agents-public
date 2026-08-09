# Primitive: Cognitive Load & Working Memory

## Definition

Working memory is the limited-capacity system that holds and manipulates information during active task performance. Its capacity is the binding constraint on most real-time decisions, comprehension, and judgment under time pressure.

Capacity estimates:
- **Miller (1956)**: 7 ± 2 chunks, where a chunk is a meaningful unit (familiar pattern, learned grouping).
- **Cowan (2001, 2010)**: ~4 chunks for novel material under interference. The Cowan number is the operating constraint for unfamiliar content; Miller's wider bound applies when chunking is well-practiced.
- Working-memory load decays in seconds without rehearsal and is disrupted by interruption.

**Cognitive Load Theory** (Sweller, 1988; Sweller, van Merriënboer & Paas, 2019) decomposes load into three sources:

| Type | Source | Action |
|---|---|---|
| **Intrinsic** | Inherent complexity of the task | Cannot be reduced without changing the task; can be staged or pre-chunked |
| **Extraneous** | Imposed by how information is presented | Always reducible; the primary engineering target |
| **Germane** | Effort spent building mental schemas | Should be supported, not minimized |

Two additional empirical regularities:
- **Decision fatigue / ego depletion** — quality of judgment degrades over a sequence of decisions; later decisions revert to defaults or impulse (Vohs et al., 2008; the original ego-depletion claims have been heavily contested, but degradation across long decision sequences in field settings is robust).
- **Attention switching cost** — every context switch imposes a setup cost (Monsell, 2003); the cost compounds when switches are frequent and unpredictable.

## When to Use

- Designing forms, dashboards, error messages, configuration screens, alert lists, or any surface that imposes simultaneous information demands.
- Diagnosing why a feature has high abandonment mid-flow (typical signature: the screen exceeds 4 novel chunks, or the user is interrupted mid-decision).
- Onboarding flows, where the user has zero familiarity and operates entirely on the Cowan ~4 limit.
- High-stakes or time-pressured tasks (incident response, financial decisions, medical workflows) where working-memory failure has real consequences.
- Reducing notification, alert, or interruption noise that fragments user attention.

## Misuse Boundary

**Ethical use**: Reduce extraneous load so the user can devote working memory to their actual task. Expose intrinsic complexity progressively. Make important decisions in low-fatigue states.

**Manipulation**: Deliberately overloading working memory to suppress informed choice. Examples:
- Burying material terms in a wall of text or a long click-through flow that depletes attention before the consent point.
- Stacking sequential consent decisions so the critical one falls late in the chain when fatigue is highest.
- Multi-step cancellation flows that interrupt and re-prompt in order to exhaust the user.
- Dense default-laden forms designed to make the dishonest reading easier than the honest one.

**Required conditions**:
1. Material decisions (consent, payment, cancellation) must be presented at low cumulative cognitive load — typically near the start of a flow, with extraneous content stripped.
2. Forms and onboarding chunked to ≤4 novel items per screen unless the user has demonstrably acquired the chunking pattern.
3. Notifications and alerts ranked and rate-limited; not all signals deserve simultaneous attention.
4. UK regulatory context: ICO guidance on dark patterns explicitly cites cognitive overload as a route to invalid consent.

## Inputs

- The task's intrinsic complexity (irreducible vs reducible).
- The user's prior familiarity with the chunking patterns being used (novice vs expert).
- The total number of simultaneous information demands per screen / step.
- The interruption rate during the task.
- The position of critical decisions within the flow (early/low-fatigue vs late/high-fatigue).

## Outputs

- A revised flow with extraneous load stripped, intrinsic load staged, and germane load supported.
- A per-screen chunk count, ideally ≤4 for novel content.
- A notification / alert priority specification with rate limits.
- A position-of-decisions audit showing material decisions occur at low cumulative load.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| High abandonment on a specific screen | The screen exceeds working-memory capacity (often >7 visible decision points, or >4 novel ones) | Split into sequential screens; pre-fill defaults; chunk related fields visually |
| Power users are fast, novices abandon | Chunking patterns assume expertise the novice doesn't have | Provide novice-mode with explicit chunking; offer expert-mode toggle for repeat users |
| Error message says "fix the 7 problems below" and user gives up | Working-memory overload from simultaneous error display | Show errors progressively (one at a time) or grouped by section with completion signals |
| Notification stream is ignored | Rate of interruption exceeds attention-switching budget; ranking is flat | Apply priority tiers; rate-limit lower tiers; allow user to demote channels |
| Late-flow consent obtained but legal team flags it as invalid | Critical decision placed where cumulative load is highest | Move material decisions to position 1–2 of the flow, with isolated framing |
| Dashboard "shows everything" and is used by no one | Extraneous load is maximised; user cannot identify the relevant signal | Cut to ≤4–7 prioritised signals on the default view; everything else moves to drill-down |

## Worked Example

**Scenario**: A B2B settings page has 18 toggles on one screen and a 31% abandonment rate. The team wants to keep all features accessible but reduce abandonment.

Cognitive-load redesign:
- **Audit**: 18 toggles is well over the Cowan limit even for familiar users. ~6 toggles control everything most users care about (the 80% case).
- **Default view**: 6 priority toggles, each labelled with its outcome (not its mechanism). Extraneous detail removed from the surface; a "Show advanced" link reveals the remaining 12.
- **Grouping**: The 12 advanced toggles are split into 3 groups of 4 by function. Each group's group-level state (on / off / mixed) is shown collapsed.
- **Critical-decision position**: A "delete account" action that was previously buried at the bottom of the page is moved to its own confirmation flow with a separate, low-load screen — so the consent is given at low cumulative fatigue.
- **Measurement**: Abandonment rate, time-to-complete, and post-task satisfaction.

**Anti-pattern check**: The redesign does not hide functionality (all 18 toggles remain reachable). It removes extraneous load from the default surface. It does not exploit fatigue — material confirmations are isolated.

## Sources

- Miller, G. A. (1956). The magical number seven, plus or minus two: Some limits on our capacity for processing information. _Psychological Review_, 63(2), 81–97. — original chunk-capacity bound.
- Cowan, N. (2001). The magical number 4 in short-term memory. _Behavioral and Brain Sciences_, 24(1), 87–114. — revised lower bound for novel material under interference.
- Cowan, N. (2010). The magical mystery four: How is working memory capacity limited, and why? _Current Directions in Psychological Science_, 19(1), 51–57. — modern synthesis.
- Sweller, J. (1988). Cognitive load during problem solving: Effects on learning. _Cognitive Science_, 12(2), 257–285. — original cognitive load theory.
- Sweller, J., van Merriënboer, J. J. G. & Paas, F. (2019). Cognitive architecture and instructional design: 20 years later. _Educational Psychology Review_, 31, 261–292. — modern reformulation, intrinsic/extraneous/germane decomposition.
- Monsell, S. (2003). Task switching. _Trends in Cognitive Sciences_, 7(3), 134–140. — switching-cost evidence base.
- UK Information Commissioner's Office. _Guidance on harmful online design / deceptive design patterns_ (2024 update). — regulatory citation of cognitive overload as invalid-consent vector.
