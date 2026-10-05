# Implementation Pitfalls and Scenarios

Anti-patterns, known traps, and implementation recipes for transactional email. Authentication record syntax and the DMARCbis (RFC 9989) progression live in [deliverability.md](deliverability.md#2-dmarc-progression-strategy); the architecture rules and setup checklist stay in [../SKILL.md](../SKILL.md).

## Contents

- [Common Anti-Patterns](#common-anti-patterns)
- [Known Traps](#known-traps)
- [Scenarios](#scenarios)
  - [S1 — Transactional password reset with idempotency by event_id](#s1--transactional-password-reset-with-idempotency-by-event_id)
  - [S2 — Authentication and DMARC alignment for a new sending domain](#s2--authentication-and-dmarc-alignment-for-a-new-sending-domain)
  - [S3 — Bounce and complaint suppression list integration](#s3--bounce-and-complaint-suppression-list-integration)
  - [S4 — RFC 8058 one-click unsubscribe wiring](#s4--rfc-8058-one-click-unsubscribe-wiring)
  - [S5 — React Email template + locale switching](#s5--react-email-template--locale-switching)

## Common Anti-Patterns

| Anti-Pattern | Reason |
|---|---|
| Sending email synchronously in request handlers | Blocks the response, creates partial-failure ambiguity, and provides no retry on ESP failures. Always use background jobs. |
| No retry for failed sends | Transient ESP errors and network blips are normal. Without retry, emails silently disappear. Use exponential backoff with a dead letter queue. |
| Sharing sending domain between transactional and marketing | Marketing complaint rates damage transactional deliverability. Separate domains, separate IPs, ideally separate ESPs. |
| Not setting up DKIM/DMARC | Emails land in spam or get rejected entirely. Required for Google/Yahoo bulk-sender compliance since February 2024. |
| DMARC `p=none` indefinitely | `p=none` is monitoring-only and provides zero spoofing protection. Your domain can be freely impersonated for phishing attacks against your users. Use `p=none` only long enough to audit all sending sources, then progress to `p=quarantine` and, for domains whose users do not post to mailing lists, `p=reject` (RFC 9989). |
| RFC 8058 one-click unsubscribe implicit, not explicit | Including `List-Unsubscribe` with an HTTPS URL is not sufficient. The `List-Unsubscribe-Post: List-Unsubscribe=One-Click` header must be present explicitly. Without it, Gmail does not treat the URL as one-click capable and the sender fails the bulk-sender requirement. |
| Using div-based layout in email HTML | Breaks in Outlook and many older clients. Use table-based layout or a framework (MJML, React Email) that generates tables automatically. |
| Not testing in real email clients | The gap between browser preview and actual email client rendering is enormous. Test in Outlook (desktop), Gmail (web), Apple Mail, and at least one mobile client. |
| Hardcoding email content instead of using templates | String concatenation for email bodies is unmaintainable, error-prone, and makes localization impossible. Use a template system from day one. |
| Ignoring bounce and complaint feedback | Continuing to send to addresses that hard-bounce or mark you as spam destroys sender reputation. Process ESP webhooks for bounces and complaints, and suppress those addresses immediately. |

## Known Traps

- **Campaign-practice traps** (tracking pixels or links added before the consent posture is decided, warm-up cadence) are owned by marketing-email-automation: deliverability.md.
- **Putting transactional and lifecycle-trigger logic in separate systems with no source-of-truth event contract** — users receive duplicate, contradictory, or out-of-order email.
- **Reply-by-email flows without strict token routing and replay protection** — spoofed or mis-threaded inbound messages land on the wrong record.
- **Template previews treated as rendering proof** — Outlook desktop, Gmail clipping, dark-mode inversion, and mobile clients still need real verification.
- **Domain alignment assumed because SPF passes** — DMARC alignment and DKIM signing need explicit verification on the actual sending domain.

## Scenarios

Recipes keyed to common implementation moments. Each lists the shortest path using the patterns in [../SKILL.md](../SKILL.md).

### S1 — Transactional password reset with idempotency by event_id

1. Generate a stable business `event_id`; commit the reset event and an outbox row atomically, with a unique constraint on purpose/recipient/event.
2. Freeze the template/locale payload, claim the row with a lease, and recheck suppression before sending.
3. Send with the stable provider idempotency key; persist provider acceptance and message ID without waiting for delivery.
4. Retry ambiguous outcomes only within the provider's documented deduplication semantics; reconcile or quarantine unknown outcomes beyond that window. An accepted message must not be resent just because delivery is unconfirmed.
5. Deduplicate signed webhook events durably and apply event-time/sequence precedence; duplicate or late events cannot clear suppression.
6. Test the crash-after-acceptance and two-worker races with stubs; alert on unresolved sends and DLQ entries.

### S2 — Authentication and DMARC alignment for a new sending domain

1. Create a dedicated sending subdomain (e.g., `mail.example.com`); publish SPF and DKIM DNS records.
2. Set DMARC to `p=none; rua=mailto:reports@example.com` to collect aggregate reports without blocking mail.
3. Ramp volume and monitor bounce/complaint rates per marketing-email-automation's warm-up ramp.
4. Review DMARC aggregate reports weekly; verify `dkim=pass` and `spf=pass` alignment on outbound.
5. Tighten DMARC to `p=quarantine` (optionally `t=y` first) after at least a month of clean reports, then to `p=reject` after an equally long quarantine period; a transactional-only subdomain can end at `p=reject`, while a domain whose users post to mailing lists should stay at `p=quarantine` (RFC 9989).

### S3 — Bounce and complaint suppression list integration

1. Subscribe to ESP bounce and complaint webhooks; route both to a single handler.
2. On hard bounce, mark the address as `suppressed: true` in your user or contact table immediately.
3. On spam complaint, suppress the address and log the complaint source for sender reputation tracking.
4. Gate every outbound send against the suppression table before handing off to the ESP.
5. Expose a suppression-check helper so all email code paths use one gate, not per-feature checks.
6. Alert when daily hard-bounce count exceeds threshold; do not wait for ESP-level warnings.

### S4 — RFC 8058 one-click unsubscribe wiring

1. Add RFC 8058 headers to marketing/subscribed mail where provider rules require them; ensure DKIM covers both headers.
2. Expose a POST endpoint (e.g., `/email/unsubscribe`) that accepts the `List-Unsubscribe=One-Click` form body.
3. On POST, mark the recipient as unsubscribed in your suppression table without requiring further confirmation.
4. Return HTTP 200 immediately; the mail client does not wait for a redirect or UI response.
5. Verify scope and timing through the marketing-owned provider rules; do not apply a Gmail numeric volume boundary to Yahoo.
6. Test by sending to a seed mailbox; inspect headers with a raw-message viewer before production rollout.

### S5 — React Email template + locale switching

1. Define each template as a React component accepting a typed `props` object, including `locale: string`.
2. Pass locale-specific copy via a `t(key, locale)` helper; keep translation keys in JSON files per locale.
3. For the installed toolchain, check the [render API](https://react.email/docs/utilities/render); import components/render from `react-email` and await `render(<ResetEmail {...props} />)`.
4. Store the rendered HTML string in the outbox or pass it directly to the ESP send call.
5. Run the preview server (`email dev`) and verify each locale variant in the browser before shipping.
6. Add a snapshot test per locale to catch rendering regressions on template changes.
