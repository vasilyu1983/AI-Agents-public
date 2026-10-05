# Postmortem Facilitation

Blameless postmortems should improve the system, not perform hindsight theater.

## Named Standards

### Howie Post-Incident Guide (PagerDuty)

The Howie guide (https://howie-guide.pagerduty.com/) is the leading open standard for structured post-incident review. Key principles:

- **Narrative framing**: reconstruct "how we got here" — the sequence of decisions that made sense at the time — rather than hunting for a single error.
- **Structured interviews**: interview responders individually before the group debrief to surface private observations and reduce anchoring to the loudest voice in the room.
- **Near-miss inclusion**: treat near-misses (incidents that almost happened) as first-class postmortem subjects; they carry the same learning value with lower cost.
- **Human factors lens**: ask what conditions, pressures, and information each person was working under — not what they "should have" done in hindsight.

Use Howie as the facilitation standard when running postmortems on SEV1/SEV2 or any incident with organizational learning value. The generic blameless template below remains valid for lightweight SEV3 reviews.

## Facilitation Checklist

- Confirm scope, impact, and timeline before opinion-heavy discussion.
- Separate timeline facts from interpretation.
- Ask what made the action reasonable at the time.
- Capture contributing factors across tooling, process, communication, and design.
- End with owned actions, deadlines, and follow-up review dates.

## Avoid

- Hunting for a single root cause.
- Framing the postmortem as a personnel review.
- Closing the document without action owners.
