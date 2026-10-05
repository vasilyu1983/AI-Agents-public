---
name: software-email-engineering
description: "Designs transactional email systems and send infrastructure. Use when implementing resets, receipts, deliverability controls, templates, or inbound email handling."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# Transactional Email Engineering

## Quick Reference

| Need | Recommended Options |
|---|---|
| Transactional ESP | Resend (modern DX), Postmark (deliverability), SendGrid (scale), AWS SES (cost) |
| Email templates | React Email (React components), MJML (responsive markup), Maizzle (Tailwind for email) |
| HTML email testing | Litmus, Email on Acid, Parcel — check provider capabilities and pricing |
| Deliverability setup | SPF, DKIM, DMARC, dedicated sending domain |
| Inbound email | SendGrid Inbound Parse, Postmark Inbound, AWS SES receiving |
| Email queue | Background job + idempotent send, dead letter queue for failures |
| Template preview | React Email preview server, Maizzle dev server |
| Tracking | Open tracking (pixel), click tracking (link wrapping), unsubscribe handling |

## When to Use This Skill

- Choosing a transactional email provider for an application
- Building email sending infrastructure (queues, retries, idempotency)
- Developing HTML email templates that render across clients
- Setting up SPF, DKIM, and DMARC for a sending domain
- Implementing inbound email processing (reply-by-email, email-to-ticket)
- Debugging deliverability issues (bounces, spam folder placement, authentication failures)

## When NOT to Use This Skill

- **Marketing email campaigns and automation** → `marketing-email-automation`
- **Email deliverability for marketing (list hygiene, segmentation)** → `marketing-email-automation`
- **Backend API design and service architecture** → [software-backend](../software-backend/SKILL.md)
- **Background job infrastructure (generic)** → [software-backend](../software-backend/SKILL.md)
- **Push notifications and mobile messaging** → [software-mobile](../software-mobile/SKILL.md)
- **Real-time in-app notifications** → [software-realtime](../software-realtime/SKILL.md)

## Workflow

1. Confirm the email job: provider choice, sending infrastructure, template work, deliverability, or inbound handling.
2. Route lifecycle-marketing, generic backend, or mobile-notification work to the adjacent skill when email engineering is not the main problem.
3. Choose the provider and template approach from the decision tree.
4. Apply the [send-pipeline correctness](#send-pipeline-correctness), authentication, rendering, and inbound-processing guidance. For Cloudflare sending/routing, load `cloudflare-email-service` if installed in the runtime; otherwise use the [official Email Service docs](https://developers.cloudflare.com/email-service/) before implementing bindings or APIs.
5. Verify current provider capabilities, limits, and policies through the navigation references before final advice.

## ASCII Flow

```text
Email engineering task
  -> Classify transactional, lifecycle, marketing, or operational email
  -> Define consent, suppression, template, and sending boundary
  -> Configure auth: SPF, DKIM, DMARC, bounce, and complaint handling
  -> Implement queueing, idempotency, provider limits, and observability
  -> Verify deliverability and legal/provider requirements
  -> Test rendering, links, unsubscribe, and failure paths
```

## Decision Tree

```text
Which email provider?
├── Modern DX, React Email integration, startup?
│   └── YES → Resend
├── Maximum deliverability, transactional focus?
│   └── YES → Postmark
├── High volume, need marketing + transactional on one platform?
│   └── YES → SendGrid
├── Cost-sensitive, AWS already in stack?
│   └── YES → AWS SES (requires more self-managed infrastructure)
├── Enterprise, existing Mailgun contract?
│   └── YES → Mailgun
└── Need both send and receive?
    └── YES → Postmark or SendGrid (both have inbound parsing)

Which template framework?
├── Team uses React?
│   └── YES → React Email (components, type safety, preview server)
├── Need responsive email without a JS framework?
│   └── YES → MJML (compiles to table-based HTML)
├── Team uses Tailwind CSS?
│   └── YES → Maizzle (Tailwind for email, compiles to inlined styles)
└── Simple transactional emails only?
    └── YES → ESP built-in templates or plain HTML with inline styles
```

## Email Architecture

**Recipient state and idempotency gate.**

Model recipient delivery state separately from campaign or job state. Key each send by message purpose, recipient, and business event, and suppress duplicates across retries. Keep suppression history append-only and enforcement fail-closed: never clear complaint or legal suppression automatically; allow unsubscribe reversal only with auditable fresh consent where lawful, and replace a hard-bounced address only after correction and reverification. A provider “accepted” response means queued for delivery, not delivered: reconcile later events and retain the provider message ID for traceability.

**Separation of concerns**: Application code triggers an email event (user signed up, order placed, password reset requested). An email service receives the event, selects the template, populates data, and calls the ESP API. The ESP handles delivery, retries, and bounce processing. Never mix email construction logic into request handlers or domain logic.

**Never send email inline in request handlers.** Email delivery is I/O-bound and can fail. Sending inline blocks the response, and failures leave the user in an ambiguous state (did the action succeed but email failed, or did everything fail?). Always enqueue email sends as background jobs.

**Queue with retry and DLQ**: Use a job queue (Sidekiq, BullMQ, Hangfire, Celery) with exponential backoff retries. After max retries, move to a dead letter queue for investigation. Alert on DLQ depth. Common failure modes: ESP rate limits, temporary network issues, invalid recipient addresses.

**Send abstraction**: Wrap the ESP client behind an interface. This enables provider switching without touching application code, simplifies testing (mock the interface), and centralizes retry/logging/metrics.

### Send-Pipeline Correctness

1. Commit the business event and an outbox row in the same database transaction. Put a unique constraint on `(purpose, recipient, business_event)`; a pre-send lookup alone races concurrent workers. Store the template/locale version and immutable payload needed for retries.
2. Claim rows with a lease or database lock, recheck suppression, then send with the same provider idempotency key and payload on every retry. Read the provider's [idempotency semantics and retention](https://resend.com/docs/dashboard/emails/idempotency-keys) before choosing the retry horizon. An application key or provider message ID alone cannot prevent a duplicate after an ambiguous network timeout; reconcile the outcome, and quarantine unresolved sends when the provider's deduplication window has expired.
3. Persist provider acceptance and message ID separately from delivery. Retry transient failures with bounded backoff; permanent failures go to suppression or investigation. Never resend merely because a delivery webhook has not arrived.
4. Verify webhook signatures on the raw request body, then durably insert each event with a unique provider event ID before acknowledging. Process duplicate events idempotently. Keep the event log and reduce state using provider event time/sequence and documented precedence: arrival order can differ from event order. A late delivery event must not clear a later complaint, unsubscribe, or hard-bounce suppression.
5. Test worker races, crashes before/after provider acceptance, expired idempotency windows, repeated webhooks, and reversed event order with stubs before live sending.

## Template Development

**React Email**: Write email templates as React components with TypeScript. Render to HTML server-side with `await render()`. Read the [official changelog](https://react.email/docs/changelog) and [render documentation](https://react.email/docs/utilities/render) for the installed major: components and rendering utilities are unified in `react-email`, so avoid copying older split-package imports. Ships with pre-built components (`<Button>`, `<Section>`, `<Column>`) that produce email-safe HTML. Includes a local preview server for development. Best option when the team already uses React.

**MJML**: XML-based markup language that compiles to responsive, table-based HTML email. Handles the painful parts of email HTML (responsive columns, padding, Outlook conditionals) automatically. Framework-agnostic. For the installed major, check the [Node API](https://documentation.mjml.io/#inside-node-js): await compilation, use strict validation to block malformed templates, and enable includes only within explicit template roots. Check [release notes](https://github.com/mjmlio/mjml/releases) before upgrading.

**Maizzle**: Tailwind CSS for email. Write emails with Tailwind utility classes, and Maizzle compiles them to inlined styles and email-safe HTML. Includes a development server with hot reload. Best for teams that already think in Tailwind.

**Rendering constraint:** Use table-based layout and inline critical styles when classic Outlook is in the recipient mix. Check feature support against the target clients and test compiled output; browser previews do not prove inbox rendering.

## Deliverability Engineering

**SPF, DKIM, and DMARC**: publish all three for every sending domain and align them with the visible `From:` domain; start DMARC at `p=none` to collect aggregate reports before tightening. Record syntax, key rotation, and the progression plan are in [references/deliverability.md](references/deliverability.md). DMARCbis (RFC 9989) obsoletes RFC 7489: the `pct`, `rf`, and `ri` tags are removed, `t=y` (test mode: the published policy is applied one level down) replaces the `pct` ramp, `np=` (from RFC 9091) sets policy for non-existent subdomains, and domains whose users may post to mailing lists SHOULD NOT publish `p=reject`. See [references/deliverability.md](references/deliverability.md#2-dmarc-progression-strategy).

**Mailbox-provider rules:** Before configuring authentication, complaint alerts, or unsubscribe headers, load the marketing-owned sender-requirements reference and follow its official provider links for current thresholds and enforcement. The implementation detail remains here: SPF authenticates the envelope sender, DKIM the signing domain; DMARC passes when at least one passing identity aligns with the visible `From:` domain under the configured strict/relaxed mode. Passing both authentication mechanisms does not mean both must align. A subdomain can align in relaxed mode.

**Transport security:** For inbound domains or a self-managed MTA, use the [MTA-STS and TLS-RPT deployment steps](references/deliverability.md#9-transport-security-mta-sts-and-tls-rpt). An outbound-only ESP domain cannot secure recipients by publishing an inbound MTA-STS policy; verify that the sending provider honors recipients' policies.

**Dedicated sending domain**: Use a subdomain like `mail.yourdomain.com` or `notifications.yourdomain.com` for transactional email. This isolates transactional reputation from marketing email reputation. If marketing email gets spam complaints, your password reset emails still reach the inbox.

**IP/domain warm-up**: New sending IPs and domains have no reputation, and sudden high volume from a new sender triggers spam filters. The ramp cadence and pause rules are a sending-practice decision owned by marketing-email-automation.

**Shared vs. dedicated IP:** Default to the ESP's shared pool for low or irregular volume. Consider dedicated IPs only with steady traffic, a staffed warm-up plan, and a provider-supported volume profile; read the ESP's eligibility and cost before recommending one. No universal monthly threshold guarantees better delivery.

**Bounce and complaint controls:** Suppress hard-bounced addresses and complainers promptly. Configure alert thresholds from the current provider rules linked above, including the provider's metric denominator and recovery conditions; do not transplant one provider's threshold to another.

**Separate transactional and marketing**: Use different sending domains, IPs, and ideally different ESPs for transactional vs. marketing email. Marketing email has inherently higher complaint rates that must not contaminate transactional deliverability.

**List hygiene, sunset policy, re-permission, and open-rate measurement are program decisions** owned by `marketing-email-automation` (see its `references/deliverability.md` and `references/re-engagement-winback.md`). The engineering rule that stays here: never infer consent, engagement, or re-engagement from open-pixel events — Apple Mail Privacy Protection can prefetch pixels without a human opening the message, so the suppression and consent code paths must key on clicks, replies, or explicit actions.

### Deliverability Setup Checklist

- [ ] SPF TXT record published on sending domain; ends in `~all` or `-all` (never `+all`)
- [ ] RSA DKIM key ≥ 2048-bit recommended and CNAME/TXT record published; verify provider requirements (RFC 8301 permits 1024-bit RSA)
- [ ] DMARC TXT record at `_dmarc.<domain>` with `rua=` reporting address
- [ ] DMARC policy starts at `p=none` (RFC 9989 suggests at least a month of reports), then `p=quarantine` (optionally with `t=y` first), then `p=reject` only for domains whose users do not post to mailing lists (e.g., transactional-only subdomains); add `np=reject` to block non-existent-subdomain spoofing; do not use `pct` (removed in RFC 9989)
- [ ] Transactional email uses a subdomain isolated from marketing (`mail.example.com`, not `example.com`)
- [ ] RFC 8058 headers and body unsubscribe link on marketing/subscribed mail where required; classify purely transactional messages separately
- [ ] Bounce and complaint ESP webhooks connected to a suppression handler
- [ ] Google Postmaster Tools domain verified and monitored
- [ ] Warm-up plan documented (start date, daily volume ramp, success criteria)

## Email Rendering Quirks

**Outlook's rendering engine is mid-transition — test both, don't assume either.** Classic Outlook for Windows (desktop) uses the Word HTML rendering engine: no flexbox, no grid, heavily restricted CSS, and MSO conditional comments (`<!--[if mso]>`) needed for fixes. The "New Outlook for Windows" replaces Word with a Chromium/WebView2-based engine with different HTML/CSS support; classic MSO fixes may not apply. Microsoft has already pushed back the enterprise rollout once (Message Center MC949965) — check the Microsoft 365 Message Center and roadmap for the current opt-out and cutover phases rather than trusting a remembered date. Enterprise fleets lag app rollouts for years anyway, so classic Outlook (Word engine) remains the most likely client to break a layout and needs explicit testing until your own recipient client data shows it is gone. Verify current rollout status before assuming Word-engine testing is no longer required for a given recipient base.

**Gmail strips `<style>` blocks** in certain contexts (embedded/clipped emails, non-Google Workspace accounts). Always inline critical styles. Use a CSS inliner (juice, Maizzle built-in, MJML built-in) as the last build step.

**Dark mode**: Support `prefers-color-scheme: dark` where available (Apple Mail, some Outlook versions). Provide explicit background colors on all elements — email clients that auto-invert colors will produce unexpected results on transparent backgrounds. Test both light and dark rendering.

**Images**: Assume images are blocked by default. Always include descriptive `alt` text. Do not use images for critical information (CTAs, key text). Specify `width` and `height` attributes to prevent layout collapse when images are blocked.

**Max width**: 600px is a conventional desktop design width, not a universal rendering guarantee. Use a fluid mobile layout and test recipient clients.

**Font support**: Web-font support varies by client; check the [support matrix](https://www.caniemail.com/search/?s=font-face) for the recipient mix. Always declare system font fallbacks. Stick to web-safe fonts (Arial, Georgia, Verdana) for maximum compatibility.

## Inbound Email Processing

**Webhook-based architecture**: The ESP receives incoming email on a designated address (e.g., `reply+token@inbound.yourdomain.com`), parses it, and POSTs structured data to your webhook endpoint. You process the parsed content in your application.

**Parsed data**: From address, to address (use unique tokens for routing), subject line, body (both plain text and HTML), attachments (usually as URLs or base64). Most ESPs also extract headers, CC/BCC, and threading references.

**Common use cases**: Reply-by-email (GitHub-style comment replies), email-to-ticket (support systems), document ingestion (forward invoices to an OCR pipeline), email-based approval workflows.

**Security considerations**: Verify webhook signatures to confirm the POST came from your ESP. Sanitize HTML body content before storing or displaying (XSS risk). Scan attachments for malware. Rate-limit inbound processing to prevent abuse. Use unique, unguessable tokens in the to-address to prevent spoofing.

**MX record setup**: Point an MX record for your inbound subdomain to the ESP's inbound servers. For example, `inbound.yourdomain.com MX → inbound.postmarkapp.com`.

## Trigger Context for Lifecycle Email

Context-aware copy for checkout-resume, drip, and upgrade-nudge email is lifecycle marketing — see marketing-email-automation/references/automation-workflows.md. The engineering constraint: persist the trigger context (e.g., a `source_key`) in the user profile or an events table at trigger time, not only in the email job payload, because delayed jobs run hours or days later.

## Common Anti-Patterns and Known Traps

The recurring failures: sending inline in request handlers, no retry or DLQ, one sending domain for transactional and marketing, missing DKIM/DMARC or `p=none` left indefinitely, `List-Unsubscribe` without the explicit `List-Unsubscribe-Post: List-Unsubscribe=One-Click` header, div-based layout, browser previews treated as client rendering proof, hardcoded content, ignored bounce/complaint feedback, transactional and lifecycle triggers with no shared event contract, reply-by-email without strict token routing and replay protection, and DMARC alignment assumed because SPF passes. Reasons and fixes: [references/pitfalls-and-scenarios.md](references/pitfalls-and-scenarios.md). Campaign-practice traps (tracking before consent, warm-up cadence) live in marketing-email-automation.

## Scenarios

Recipes S1-S5 (password reset idempotent by `event_id`, new-domain authentication with DMARC alignment and RFC 9989 progression, bounce/complaint suppression gate, RFC 8058 one-click unsubscribe endpoint, React Email with locale switching): [references/pitfalls-and-scenarios.md](references/pitfalls-and-scenarios.md#scenarios).

## Navigation

### References
- [references/deliverability.md](references/deliverability.md) — Provider-requirements pointer, DMARCbis (RFC 9989) progression, RSA/Ed25519 signing, transport security, BIMI/VMC, diagnostics
- [references/pitfalls-and-scenarios.md](references/pitfalls-and-scenarios.md) — Anti-pattern table, known traps, and implementation scenarios S1-S5
- [Skill Sources](data/sources.json): curated primary sources for email engineering guidance.
- [scripts/check_email_auth.py](scripts/check_email_auth.py) — DNS check for SPF, DKIM, DMARC (`t=`, `np=`, staged next-policy advice), and BIMI; pass `--all-sources-aligned` only after aggregate reports show it.

### Related Skills

- [software-backend](../software-backend/SKILL.md) — Backend service architecture, background jobs, and queue patterns
- `marketing-email-automation` — Marketing campaigns, drip sequences, and ESP workflow automation
- [software-frontend](../software-frontend/SKILL.md) — Frontend implementation (email preference UIs, unsubscribe pages)
- [software-security-appsec](../software-security-appsec/SKILL.md) — Security considerations for inbound email processing and webhook verification

Before selecting an ESP, template toolchain, certificate, or operational limit, follow the relevant official link in [data/sources.json](data/sources.json) and record the capability, policy, or price used in the decision.

## Authentication Traps

- **RSA key length:** RFC 8301 requires at least 1024-bit RSA and recommends at least 2048-bit; do not describe all 1024-bit keys as invalid. Keep an RSA signature when adding Ed25519 until the target receiver/ESP support is verified; use separate selectors ([details](references/deliverability.md#1-yahoo-and-google-bulk-sender-requirements)).
- **SPF `+all`:** Authorizes every sender. It weakens authentication but does not inherently break DMARC alignment; remove it even when the domain aligns.
- **Forwarding:** SPF can fail after forwarding. Verify surviving aligned DKIM and the recipient's ARC policy; an ARC header alone does not guarantee acceptance.
- **DMARC presence:** Inspect the policy and actual-message alignment. DNS presence alone does not prove signatures, delivery, or spoofing protection.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
