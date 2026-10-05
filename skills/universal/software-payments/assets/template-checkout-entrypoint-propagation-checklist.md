# Template: Checkout Entrypoint Propagation Checklist

Use this when checkout API contract changes (status/error/payload).

## Contract Change

- Change summary: `________________________________________`
- Contract version/tag: `____________________________________`
- Owner: `_______________________________________________`

## Entrypoint Audit

| Surface | File/Component | Calls Checkout API | Handles Contract Status | Uses Shared Recovery UI | i18n Ready | Analytics Owner | Targeted Test |
|---|---|---|---|---|---|---|---|
| Subscription modal |  | [ ] | [ ] | [ ] | [ ] | client / server | [ ] |
| One-time purchase card |  | [ ] | [ ] | [ ] | [ ] | client / server | [ ] |
| Embedded paywall CTA |  | [ ] | [ ] | [ ] | [ ] | client / server | [ ] |
| Upsell CTA |  | [ ] | [ ] | [ ] | [ ] | client / server | [ ] |
| Other |  | [ ] | [ ] | [ ] | [ ] | client / server | [ ] |

## Telemetry Consistency

- [ ] Contract-failure KPI emitted by one layer only.
- [ ] If secondary diagnostic event exists, event name is distinct.
- [ ] Dedup key strategy documented.

## Release Decision

- [ ] Go
- [ ] No-go (missing migrated entrypoints)

Notes:
`_____________________________________________________________`
