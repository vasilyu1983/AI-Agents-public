# On-Call Practices

Operational defaults for healthy on-call rotations and escalation.

## Rotation Rules

- Keep primary and secondary coverage explicit.
- Limit consecutive high-severity weeks where possible.
- Hand over unresolved risks in writing at shift change.
- Review noisy alerts weekly and either tune or retire them.

## Escalation Rules

- Page secondary support when impact is still unclear after the first triage window.
- Escalate to leadership only for confirmed SEV1 impact, data-loss risk, or external communications risk.
- Escalate to security immediately when compromise or abuse is plausible.

## Fatigue Controls

- Track pages per engineer and after-hours distribution.
- Use post-incident reviews to remove repeat toil.
- Treat pager noise as reliability debt, not personal weakness.
