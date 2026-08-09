---
name: software-email-engineering
description: "Designs transactional email systems and send infrastructure. Use when implementing resets, receipts, deliverability controls, templates, or inbound email handling."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Transactional Email Engineering

Build reliable email systems that reach the inbox.

## Quick Reference

| Need | Recommended Options |
|---|---|
| Transactional ESP | Resend (modern DX), Postmark (deliverability), SendGrid (scale), AWS SES (cost) |
| Email templates | React Email (React components), MJML (responsive markup), Maizzle (Tailwind for email) |
| HTML email testing | Litmus (now part of Validity; pricing jumped sharply post-acquisition), Email on Acid, Parcel (free) |
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
4. Apply the relevant architecture, authentication, retry, rendering, and inbound-processing guidance.
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

**Separation of concerns**: Application code triggers an email event (user signed up, order placed, password reset requested). An email service receives the event, selects the template, populates data, and calls the ESP API. The ESP handles delivery, retries, and bounce processing. Never mix email construction logic into request handlers or domain logic.

**Never send email inline in request handlers.** Email delivery is I/O-bound and can fail. Sending inline blocks the response, and failures leave the user in an ambiguous state (did the action succeed but email failed, or did everything fail?). Always enqueue email sends as background jobs.

**Idempotency**: Deduplicate sends by event ID. If a background job retries after a transient failure, the email service should check whether the email for that event was already sent. Most ESPs provide message IDs and delivery status APIs for this. Without idempotency, users receive duplicate password reset emails or order confirmations.

**Queue with retry and DLQ**: Use a job queue (Sidekiq, BullMQ, Hangfire, Celery) with exponential backoff retries. After max retries, move to a dead letter queue for investigation. Alert on DLQ depth. Common failure modes: ESP rate limits, temporary network issues, invalid recipient addresses.

**Send abstraction**: Wrap the ESP client behind an interface. This enables provider switching without touching application code, simplifies testing (mock the interface), and centralizes retry/logging/metrics.

## Template Development

**React Email**: Write email templates as React components with TypeScript. Render to HTML string server-side with `render()`. Ships with pre-built components (`<Button>`, `<Section>`, `<Column>`) that produce email-safe HTML. Includes a local preview server for development. Best option when the team already uses React.

**MJML**: XML-based markup language that compiles to responsive, table-based HTML email. Handles the painful parts of email HTML (responsive columns, padding, Outlook conditionals) automatically. Framework-agnostic — works with any backend. Good middle ground between raw HTML and a full JS framework.

**Maizzle**: Tailwind CSS for email. Write emails with Tailwind utility classes, and Maizzle compiles them to inlined styles and email-safe HTML. Includes a development server with hot reload. Best for teams that already think in Tailwind.

**The core constraint**: Email HTML is stuck in approximately 2005. Tables for layout, inline styles for everything, limited CSS support. No flexbox, no grid, no modern CSS in Outlook. Every template framework exists to abstract over this pain. Always test the compiled output, not just the source.

## Deliverability Engineering

**SPF (Sender Policy Framework)**: A DNS TXT record that lists which IP addresses and services are authorized to send email from your domain. Without SPF, receiving servers may reject or spam-folder your emails.

**DKIM (DomainKeys Identified Mail)**: A cryptographic signature added to email headers. The sending server signs with a private key; receiving servers verify with a public key published in DNS. Proves the email was not tampered with in transit and was sent by an authorized sender.

**DMARC (Domain-based Message Authentication, Reporting, and Conformance)**: A DNS policy that tells receiving servers what to do when SPF and DKIM checks fail (none, quarantine, reject). Start with `p=none` to monitor, then tighten to `p=quarantine` or `p=reject` once authentication is solid. DMARC also provides aggregate reports on who is sending email from your domain.

**Current mailbox-provider requirements**: Major inbox providers now treat authenticated sending posture as operational baseline, not optional polish, and enforcement has moved from "spam-fold it" to "reject it." Gmail escalated to outright SMTP rejections (5xx) for non-compliant bulk mail in November 2025 — this is no longer a quiet deliverability penalty, it is a hard bounce. Microsoft enforces an equivalent bar for Outlook.com/Hotmail/Live.com with an explicit `550 5.7.515` rejection code. Verify current Gmail and other provider rules for TLS in transit, aligned `From:`-domain authentication, PTR or reverse-DNS hygiene on sending IPs, complaint-rate limits, and one-click unsubscribe on bulk or lifecycle mail before final deliverability advice.

**Dedicated sending domain**: Use a subdomain like `mail.yourdomain.com` or `notifications.yourdomain.com` for transactional email. This isolates transactional reputation from marketing email reputation. If marketing email gets spam complaints, your password reset emails still reach the inbox.

**IP/domain warm-up**: New sending IPs and domains have no reputation. Start at 200–500 emails/day and roughly double each week over 3–4 weeks. Sudden high volume from a new IP triggers spam filters.

**Shared vs. dedicated IP — decide by volume and consistency, not ambition**: Most senders should default to the ESP's shared IP pool. A dedicated IP only pays off above roughly 50,000–100,000 sends/month sent consistently (a dedicated IP that goes quiet between sends loses reputation faster than a shared pool ever would). Below that volume, or with spiky/seasonal sending, a dedicated IP is a liability you warm up alone with no shared reputation to fall back on. Judgment call: recommend dedicated IPs for high-volume, steady, reputation-sensitive senders (financial, healthcare, high-ARPU transactional); recommend shared pools for everyone else, including most early-stage transactional workloads.

**Bounce and complaint rate thresholds**: Hard bounce rate must stay below 2%. Per Google's current published guidance, keep spam complaint rate below 0.10% as the working target; 0.3% or higher is the compliance-breaking threshold that triggers rejections and mitigation-ineligibility (Google restores mitigation eligibility only after 7 consecutive clean days). Remove hard bounces immediately and suppress complainers — treat 0.10% as the real ceiling, not 0.3%, since spam rate is a lagging indicator and by the time it crosses 0.3% the damage is already done.

**Separate transactional and marketing**: Use different sending domains, IPs, and ideally different ESPs for transactional vs. marketing email. Marketing email has inherently higher complaint rates that must not contaminate transactional deliverability.

**List hygiene has a sunset clock, not just a bounce trigger**: Suppress hard bounces immediately, but also sunset subscribers who show zero clicks (not opens — see Apple MPP below) for 6–12 months. A list that is never pruned drags down engagement-weighted inbox placement even when bounce and complaint rates look clean, because mailbox providers increasingly score sender reputation on engagement, not just complaints.

**Know when NOT to send — re-permission before resuming**: If a segment has been dormant for 6+ months, has unknown provenance (list import, stale opt-in, acquired company), or was collected under a consent regime that has since changed, do not resume normal sending into it. Run a low-volume re-permission campaign first ("Do you still want these emails?") and suppress everyone who doesn't respond. Resuming full-volume sends into a stale list is the single fastest way to blow up a warmed sending reputation — it looks identical to a spam blast from the receiving side.

**Opens are a dead metric for list health — measure clicks and conversions instead**: Apple Mail Privacy Protection now affects roughly 55–60% of tracked opens (Litmus Email Analytics, 2026), and Apple Mail/MPP combined account for a plurality of the email client market. An "open" no longer reliably means a human read the email. Use click-through rate, conversion rate, and reply rate as the primary engagement and list-health signals; treat open rate as a rough, client-mix-dependent proxy at best. See [references/deliverability.md](references/deliverability.md) for adaptation strategies.

### Deliverability Setup Checklist

- [ ] SPF TXT record published on sending domain; ends in `~all` or `-all` (never `+all`)
- [ ] DKIM key ≥ 2048-bit generated and CNAME/TXT record published
- [ ] DMARC TXT record at `_dmarc.<domain>` with `rua=` reporting address
- [ ] DMARC policy starts at `p=none`; tighten to `p=quarantine` after two clean weeks, then `p=reject`
- [ ] Transactional email uses a subdomain isolated from marketing (`mail.example.com`, not `example.com`)
- [ ] `List-Unsubscribe` and `List-Unsubscribe-Post: List-Unsubscribe=One-Click` headers on all bulk/lifecycle mail
- [ ] Bounce and complaint ESP webhooks connected to a suppression handler
- [ ] Google Postmaster Tools domain verified and monitored
- [ ] Warm-up plan documented (start date, daily volume ramp, success criteria)

## Email Rendering Quirks

**Outlook's rendering engine is mid-transition — test both, don't assume either.** Classic Outlook for Windows (desktop) uses the Word HTML rendering engine: no flexbox, no grid, heavily restricted CSS, and MSO conditional comments (`<!--[if mso]>`) needed for fixes. The "New Outlook for Windows" replaces Word with a Chromium/WebView2-based engine with full modern HTML/CSS support and no longer needs MSO hacks. Microsoft made New Outlook the default in April 2026, began blocking new classic-Outlook installs in June 2026, and ends support for Word-rendering desktop versions in October 2026 — but enterprise fleets lag OS/app rollouts for years, so classic Outlook (Word engine) remains the most likely client to break a layout and still needs explicit testing well past the "official" cutover. Verify current rollout status before assuming Word-engine testing is no longer required for a given recipient base.

**Gmail strips `<style>` blocks** in certain contexts (embedded/clipped emails, non-Google Workspace accounts). Always inline critical styles. Use a CSS inliner (juice, Maizzle built-in, MJML built-in) as the last build step.

**Dark mode**: Support `prefers-color-scheme: dark` where available (Apple Mail, some Outlook versions). Provide explicit background colors on all elements — email clients that auto-invert colors will produce unexpected results on transparent backgrounds. Test both light and dark rendering.

**Images**: Assume images are blocked by default. Always include descriptive `alt` text. Do not use images for critical information (CTAs, key text). Specify `width` and `height` attributes to prevent layout collapse when images are blocked.

**Max width**: 600px is the safe standard for email body width. Some modern clients support wider, but 600px renders correctly everywhere including mobile.

**Font support**: Web fonts work in Apple Mail and some Thunderbird versions, but nowhere else. Always declare system font fallbacks. Stick to web-safe fonts (Arial, Georgia, Verdana) for maximum compatibility.

## Inbound Email Processing

**Webhook-based architecture**: The ESP receives incoming email on a designated address (e.g., `reply+token@inbound.yourdomain.com`), parses it, and POSTs structured data to your webhook endpoint. You process the parsed content in your application.

**Parsed data**: From address, to address (use unique tokens for routing), subject line, body (both plain text and HTML), attachments (usually as URLs or base64). Most ESPs also extract headers, CC/BCC, and threading references.

**Common use cases**: Reply-by-email (GitHub-style comment replies), email-to-ticket (support systems), document ingestion (forward invoices to an OCR pipeline), email-based approval workflows.

**Security considerations**: Verify webhook signatures to confirm the POST came from your ESP. Sanitize HTML body content before storing or displaying (XSS risk). Scan attachments for malware. Rate-limit inbound processing to prevent abuse. Use unique, unguessable tokens in the to-address to prevent spoofing.

**MX record setup**: Point an MX record for your inbound subdomain to the ESP's inbound servers. For example, `inbound.yourdomain.com MX → inbound.postmarkapp.com`.

## Context-Aware Transactional Email

Standard transactional emails send the same copy to everyone. Context-aware emails capture the trigger context at event time and use it to personalize the email content, improving conversion and relevance.

**The pattern**:

1. **Capture context at the trigger point.** When a user starts checkout, save the feature or surface that triggered it (`source_key: "checkout_resume"`, `source_key: "feature_gate"`, etc.) alongside the event timestamp.
2. **Map context to copy variants.** Build a lookup from source identifiers to specific headline, value proposition, and urgency copy. Each variant should speak directly to the feature the user was trying to access.
3. **Fall back to generic.** When no source is available (direct URL, old events, missing data), use a generic but still compelling template. The fallback must be production-quality, not a placeholder.

**Where this applies**:

- **Checkout-resume / cart-abandonment emails**: "You were exploring [feature name] — pick up where you left off" usually converts better than a generic "Complete your purchase."
- **Drip sequences**: Knowing which paywall the user hit lets drip emails reinforce the specific value they already expressed interest in.
- **Upgrade nudges**: When a free user hits a gated feature, the follow-up email can reference that exact feature instead of listing everything.

**Implementation notes**:

- Store the trigger context in the user's profile or a lightweight events table, not just in the email job payload. Drip crons that run hours or days later need access to it.
- Keep the context-to-copy mapping in one place (a function or config object) so new features get email copy as they're added to the paywall.
- Test the fallback path explicitly — it handles more traffic than you expect.

## Common Anti-Patterns

| Anti-Pattern | Reason |
|---|---|
| Sending email synchronously in request handlers | Blocks the response, creates partial-failure ambiguity, and provides no retry on ESP failures. Always use background jobs. |
| No retry for failed sends | Transient ESP errors and network blips are normal. Without retry, emails silently disappear. Use exponential backoff with a dead letter queue. |
| Sharing sending domain between transactional and marketing | Marketing complaint rates damage transactional deliverability. Separate domains, separate IPs, ideally separate ESPs. |
| Not setting up DKIM/DMARC | Emails land in spam or get rejected entirely. Required for Google/Yahoo bulk-sender compliance since February 2024. |
| DMARC `p=none` indefinitely | `p=none` is monitoring-only and provides zero spoofing protection. Your domain can be freely impersonated for phishing attacks against your users. Use `p=none` only long enough to audit all sending sources, then progress to `p=quarantine` and `p=reject`. |
| RFC 8058 one-click unsubscribe implicit, not explicit | Including `List-Unsubscribe` with an HTTPS URL is not sufficient. The `List-Unsubscribe-Post: List-Unsubscribe=One-Click` header must be present explicitly. Without it, Gmail does not treat the URL as one-click capable and the sender fails the bulk-sender requirement. |
| Using div-based layout in email HTML | Breaks in Outlook and many older clients. Use table-based layout or a framework (MJML, React Email) that generates tables automatically. |
| Not testing in real email clients | The gap between browser preview and actual email client rendering is enormous. Test in Outlook (desktop), Gmail (web), Apple Mail, and at least one mobile client. |
| Hardcoding email content instead of using templates | String concatenation for email bodies is unmaintainable, error-prone, and makes localization impossible. Use a template system from day one. |
| Ignoring bounce and complaint feedback | Continuing to send to addresses that hard-bounce or mark you as spam destroys sender reputation. Process ESP webhooks for bounces and complaints, and suppress those addresses immediately. |

## Known Traps

- **Tracking links and open pixels without deciding the privacy and consent posture first** — the implementation may be easy, but the compliance and user-trust cost is not.
- **Putting transactional and lifecycle-trigger logic in separate systems with no source-of-truth event contract** — users receive duplicate, contradictory, or out-of-order email.
- **Reply-by-email flows without strict token routing and replay protection** — spoofed or mis-threaded inbound messages land on the wrong record.
- **Template previews treated as rendering proof** — Outlook desktop, Gmail clipping, dark-mode inversion, and mobile clients still need real verification.
- **Domain alignment assumed because SPF passes** — DMARC alignment and DKIM signing need explicit verification on the actual sending domain.

## Scenarios

Recipes keyed to common implementation moments. Each lists the shortest path using patterns above.

### S1 — Transactional password reset with idempotency by event_id

1. Generate a stable `event_id` (e.g., `reset:{user_id}:{token_hash}`) at the trigger point.
2. Before enqueuing, check whether an email for this `event_id` was already sent and delivered.
3. Enqueue the send job with `event_id` as the idempotency key; store send status in a `email_events` table.
4. In the job, call the ESP API and record the response `message_id` alongside `event_id`.
5. On retry, re-check the `email_events` table; skip the ESP call if already delivered.
6. Alert on DLQ entries; failed password resets block users.

### S2 — Domain warm-up + DMARC alignment for a new sending domain

1. Create a dedicated sending subdomain (e.g., `mail.example.com`); publish SPF and DKIM DNS records.
2. Set DMARC to `p=none; rua=mailto:reports@example.com` to collect aggregate reports without blocking mail.
3. Start sending at 200–500 emails per day; ramp by roughly 2× each week over 3–4 weeks.
4. Monitor bounce rate (<2%) and spam complaint rate (<0.1%) in the ESP dashboard daily.
5. Review DMARC aggregate reports weekly; verify `dkim=pass` and `spf=pass` alignment on outbound.
6. Tighten DMARC to `p=quarantine` then `p=reject` only after two consecutive clean weeks.

### S3 — Bounce and complaint suppression list integration

1. Subscribe to ESP bounce and complaint webhooks; route both to a single handler.
2. On hard bounce, mark the address as `suppressed: true` in your user or contact table immediately.
3. On spam complaint, suppress the address and log the complaint source for sender reputation tracking.
4. Gate every outbound send against the suppression table before handing off to the ESP.
5. Expose a suppression-check helper so all email code paths use one gate, not per-feature checks.
6. Alert when daily hard-bounce count exceeds threshold; do not wait for ESP-level warnings.

### S4 — RFC 8058 one-click unsubscribe wiring

1. Add `List-Unsubscribe` and `List-Unsubscribe-Post` headers to every bulk or lifecycle email sent.
2. Expose a POST endpoint (e.g., `/email/unsubscribe`) that accepts the `List-Unsubscribe=One-Click` form body.
3. On POST, mark the recipient as unsubscribed in your suppression table without requiring further confirmation.
4. Return HTTP 200 immediately; the mail client does not wait for a redirect or UI response.
5. Verify compliance: Gmail and Yahoo require one-click unsubscribe for senders sending >5k/day.
6. Test by sending to a seed mailbox; inspect headers with a raw-message viewer before production rollout.

### S5 — React Email template + locale switching

1. Define each template as a React component accepting a typed `props` object, including `locale: string`.
2. Pass locale-specific copy via a `t(key, locale)` helper; keep translation keys in JSON files per locale.
3. Render to HTML string server-side: `await render(<ResetEmail {...props} />)`.
4. Store the rendered HTML string in the outbox or pass it directly to the ESP send call.
5. Run the preview server (`email dev`) and verify each locale variant in the browser before shipping.
6. Add a snapshot test per locale to catch rendering regressions on template changes.

## Navigation

### References
- [references/deliverability.md](references/deliverability.md) — Yahoo/Google bulk-sender requirements, DMARC progression, BIMI/VMC, Microsoft 365 requirements, Apple MPP, Postmaster Tools
- [Skill Sources](data/sources.json): curated primary sources for email engineering guidance.

### Related Skills

- [software-backend](../software-backend/SKILL.md) — Backend service architecture, background jobs, and queue patterns
- `marketing-email-automation` — Marketing campaigns, drip sequences, and ESP workflow automation
- [software-frontend](../software-frontend/SKILL.md) — Frontend implementation (email preference UIs, unsubscribe pages)
- [software-security-appsec](../software-security-appsec/SKILL.md) — Security considerations for inbound email processing and webhook verification

## Freshness Protocol

Email providers, template frameworks, and deliverability standards evolve. Verify current information before recommending specific tools or configurations.

### Trigger Conditions

- "Which transactional email provider should I use?"
- "Is Resend/Postmark/SendGrid still recommended?"
- "What's the current best practice for DMARC?"
- "What do Gmail sender requirements require today?"
- "Should I use React Email or MJML?"
- "What are current email client rendering limitations?"

### How to Freshness-Check

1. Start from [data/sources.json](data/sources.json) for official documentation links.
2. Run a targeted web search for the specific provider or standard.
3. Prefer official docs and provider changelogs over blog posts for feature, webhook, retention, and pricing claims.

### What to Report

- **Current landscape**: what is stable and widely used now
- **Emerging trends**: what is gaining traction (and why)
- **Deprecated/declining**: what is falling out of favor (and why)
- **Recommendation**: default choice + 1-2 alternatives, with trade-offs

## Regulatory Traps

- **Gmail/Yahoo bulk sender requirements (effective Feb 2024; enforcement hardened November 2025 — verify current thresholds)**: senders exceeding 5,000 messages/day to Gmail or Yahoo addresses must have SPF and DKIM aligned on the same `From:` domain, a DMARC policy of at least `p=none` (Google's own guidance: "your DMARC enforcement policy can be set to none" satisfies the floor — `p=quarantine`/`p=reject` are not mandatory but are the correct target posture), and one-click List-Unsubscribe (RFC 8058) with `List-Unsubscribe-Post` header on all commercial/promotional mail. Since November 2025, Gmail rejects non-compliant bulk mail outright at the SMTP level (5xx) rather than spam-foldering it.
- **DMARC trajectory — treat `p=none` as a compliance floor, not a destination**: `p=none` satisfies today's minimum for Google and Microsoft, but provides zero anti-spoofing protection, and both providers signal that stricter alignment requirements are likely to tighten over time. Architect authentication to reach `p=reject` on a real timeline regardless of the current floor.
- **One-click unsubscribe (RFC 8058)**: the `List-Unsubscribe-Post` header must be present alongside the mailto/URL `List-Unsubscribe` header; clicking unsubscribe must remove the recipient within two business days; failure to honour this triggers deliverability penalties, not just user annoyance.
- **Complaint rate threshold — 0.3% sustained kills delivery**: Google Postmaster Tools and Yahoo report complaint rates; Google's published guidance is to keep spam rate below 0.10% and treat 0.3%+ as the hard compliance-breaking threshold (mitigation eligibility only returns after 7 consecutive clean days); track Postmaster Tools data actively, not reactively.
- **Microsoft (Outlook.com / Hotmail / Live.com) enforcement — announced April 2025, enforced from May 5, 2025**: senders over 5,000/day to consumer Outlook.com addresses must meet SPF/DKIM/DMARC at a minimum of `p=none` aligned to SPF or DKIM (preferably both), plus List-Unsubscribe. Non-compliant mail is rejected outright with SMTP code `550 5.7.515`, not spam-foldered — Microsoft changed its original junk-folder plan to hard rejection before rollout completed. Verify current enforcement status; this is understood to be fully active through 2026.
- **DKIM key length**: 1024-bit DKIM keys are treated as insufficient by modern validators — use 2048-bit minimum; some providers auto-generate 1024-bit keys on older plans, verify.
- **Subdomain isolation matters more now**: shared sending domains or subdomains that carry mixed transactional + marketing traffic are harder to remediate if complaint rates spike; separate domains with separate DMARC records are the correct posture.
- **SPF `+all` is fatal**: any SPF record ending in `+all` passes all senders and DMARC alignment fails; verify SPF ends in `~all` or `-all`.
- **ARC (Authenticated Received Chain)**: for forwarding scenarios (mailing lists, ticketing relays), ARC headers preserve the original authentication chain; important for B2B mail that passes through forwarding infrastructure.
- **DMARC adoption is wide but enforcement is thin**: roughly half of internet domains publish a DMARC record, but only a low-single-digit percentage of all domains enforce `p=reject` — do not assume a partner or third-party sender is actually protected just because a DMARC record exists; check the policy tag (verify current adoption figures, they move quickly).

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Use web search/web fetch to verify current external facts, versions, pricing, deadlines, regulations, or platform behavior before final answers.
- Verify current webhook security, HTTPS requirements, inbound parsing behavior, metadata retention, and provider sandbox or quota defaults before final recommendations.
- Verify current mailbox-provider sender requirements before advising on DMARC posture, unsubscribe flows, bulk-mail behavior, or complaint-rate thresholds.
- Prefer primary sources; report source links and dates for volatile information.
- If web access is unavailable, state the limitation and mark guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

