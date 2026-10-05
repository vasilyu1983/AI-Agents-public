# Feedback Outcome Contract

## FeedbackOutcome (backend)

- `id`
- `entity_id`
- `entity_type`
- `source_type`
- `source_id`
- `outcome_type`
- `status`
- `impact_score`
- `details`
- `measured_at`
- `owner_scope`

## InlineReactionFeedback (client → backend)

Lightweight per-response feedback that ties user reactions to specific context bundles:

- `context_bundle_id` — ties reaction to the exact context assembly that produced the response
- `reaction` — semantic reaction (e.g., `resonated` / `neutral` / `off`)
- `surface` — which surface the feedback came from (ask, dashboard, email, etc.)
- `timestamp` — when the reaction was captured

### Client-side UX patterns

- **Tie feedback to the bundle, not the answer.** The `context_bundle_id` is the correlation key. This lets the backend update memory confidence and surface ranking, not just track satisfaction.
- **Reaction taxonomy:** Use 2-3 options, not 5-star scales. `resonated / off` (binary) or `resonated / neutral / off` (ternary) works. More options cause decision fatigue and reduce capture rate.
- **Optimistic UI:** Mark feedback as sent immediately on tap. Submit async. Never block the UI or show errors for feedback submission — it's best-effort.
- **One-shot per response:** Once feedback is sent for a bundle ID, replace the buttons with a "Thanks" confirmation. Never show buttons again for that bundle.
- **Feedback fatigue:** Don't show feedback on every surface. Start with the highest-value surface (chat/ask responses). Expand to dashboard guidance only after validating the pattern.

### Backend processing

- Feedback updates memory confidence scores, not operational truth.
- A `resonated` reaction on a response that used specific memories should increase those memories' confidence.
- An `off` reaction should decrease confidence and potentially flag the memory for review.
- Aggregate reaction rates per surface inform context assembly ranking — surfaces where users consistently react `off` need assembly tuning.

## Rules

- Outcomes update derived memory, never operational truth directly.
- Keep action execution and measured impact as separate fields.
- Require owner scope on every feedback record.
- Inline reactions are a subset of feedback — they have lower fidelity but higher capture rate than structured corrections.
