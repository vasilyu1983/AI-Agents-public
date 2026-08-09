# Resend Cost Guide

Reference for controlling Resend email costs, spotting waste, and deciding when to upgrade or switch providers.

## Table of Contents

- [Plan Tiers](#plan-tiers)
- [When Free Tier Is Sufficient](#when-free-tier-is-sufficient)
- [When to Upgrade to Pro](#when-to-upgrade-to-pro)
- [Billing Model](#billing-model)
- [Cost Drivers](#cost-drivers)
- [Common Waste Patterns](#common-waste-patterns)
- [Optimization Tactics](#optimization-tactics)
- [Monitoring](#monitoring)
- [Alternatives](#alternatives)

## Plan Tiers

| Plan | Price | Daily Limit | Monthly Limit | Domains | Notes |
|------|-------|-------------|---------------|---------|-------|
| Free | $0 | 100 emails/day | 3,000/month | 1 | Single sender domain, basic analytics |
| Pro | $20/month | None | 50,000 included | Unlimited | Custom tracking domain, webhooks, dedicated IPs available |
| Enterprise | Custom | None | Negotiated | Unlimited | SLA, volume discounts, dedicated support |

## When Free Tier Is Sufficient

- Total transactional volume stays under 100 emails/day consistently.
- Single product with one sender domain.
- Early-stage product where email is limited to password resets, verification, and occasional notifications.
- No need for webhook integrations or advanced analytics.

## When to Upgrade to Pro

- Any day exceeds 100 sends (even once triggers queue delays or drops).
- Multiple products or brands requiring separate sender domains.
- Webhook delivery confirmation is needed for payment receipts or compliance audit trails.
- Volume is trending toward 2,000+/month and growing, meaning the free ceiling will be hit within a quarter.

## Billing Model

- Monthly subscription with a fixed email allocation per tier.
- Overage on Pro: billed per additional email beyond the 50,000 included. Check the current rate on the Resend pricing page; historically around $0.40 per additional 1,000 emails.
- Billing resets on the calendar month. Unused emails do not roll over.
- Bounced and rejected emails still count toward the monthly quota.

## Cost Drivers

| Driver | Impact | Control Lever |
|--------|--------|---------------|
| Email volume | Primary cost factor | Digests, suppression lists, send-only-when-needed logic |
| Number of domains | Forces Pro tier if >1 | Consolidate brands under one domain where possible |
| API calls | Indirect — each send = 1 API call | Batch API for bulk sends instead of individual calls |
| Bounce rate | Bounces count toward quota | List hygiene, verification before send |
| Webhook retries | Can multiply apparent volume on the receiving side | Acknowledge webhooks quickly, implement idempotent handlers |

## Common Waste Patterns

### Unnecessary transactional emails

Sending a separate email for every minor event (e.g., "your settings were saved," "you logged in from a new device") when users do not need or want them. Audit every email trigger and ask whether the user would notice if it stopped.

### No batching

Calling the Resend API once per recipient for bulk operations (onboarding cohorts, batch notifications). Each call is one email against the quota. Use the batch endpoint to send up to 100 emails in a single API call.

### Retry storms on failed webhooks

When the receiving server is slow or down, Resend retries webhook delivery automatically. If the receiver never acknowledges, retries pile up. This does not cost extra sends, but it can mask deliverability problems and waste engineering time debugging phantom failures. Fix: return 200 immediately, process asynchronously.

### Sending to dead addresses

Emails to invalid addresses bounce. Bounces count toward quota and hurt sender reputation. Maintain a suppression list and honor it on every send.

### Duplicate sends from race conditions

Multiple services or workers triggering the same transactional email (e.g., two webhook handlers both sending a receipt). Deduplicate with idempotency keys or a sent-email log.

## Optimization Tactics

### Batch API calls

Use the `/emails/batch` endpoint for any scenario where multiple emails go out at once. Reduces API overhead and is simpler to monitor.

### Implement email digests

Replace per-event emails with periodic digests. Example: instead of sending a notification for every comment, send a daily summary. This can reduce volume by 5-20x depending on the product.

### Use suppression lists

Maintain a suppression list of bounced, unsubscribed, and complaint addresses. Check the list before every send. Resend provides suppression list APIs — use them.

### Optimize templates to reduce rendering time

Complex templates with heavy inline CSS, large images, or conditional logic increase rendering time on Resend's side. Keep templates lean. Precompile where possible. This does not reduce quota usage but improves delivery speed and reduces API latency.

### Consolidate domains

Each additional sender domain requires Pro. If multiple domains are not adding deliverability or branding value, consolidate to one domain with subaddressing or reply-to routing.

### Gate sends with user preferences

Let users control notification frequency. Fewer unwanted emails means fewer sends, fewer unsubscribes, and fewer spam complaints.

## Monitoring

| Metric | Why It Matters | Action Threshold |
|--------|---------------|------------------|
| Daily/monthly send volume | Tracks burn against quota | >70% of monthly quota by mid-month |
| Bounce rate | Bounces waste quota and hurt reputation | >2% sustained |
| Suppression list size | Growing list = growing hygiene problem | Track month-over-month trend |
| Delivery rate | Confirms emails are reaching inboxes | <95% warrants investigation |
| Webhook success rate | Failed webhooks signal integration issues | <99% needs attention |
| API error rate | Failed API calls = emails not sent | Any sustained errors need immediate fix |

Set up alerts on send volume (daily and monthly) to catch unexpected spikes before hitting plan limits.

## Alternatives

| Provider | Free Tier | Paid Starting At | Best For |
|----------|-----------|------------------|----------|
| **SendGrid** | 100 emails/day (no monthly cap on free) | $19.95/month for 50K | Higher free daily limit with established ecosystem |
| **Postmark** | No free tier (trial credits only) | $15/month for 10K | Excellent deliverability, transactional-only focus |
| **AWS SES** | 62,000/month free (from EC2 only) | ~$0.10 per 1,000 emails | Cheapest at volume, requires more setup |
| **Mailgun** | 100 emails/day for first 3 months | $35/month for 50K | Flexible API, good for high-volume transactional |

**Decision framework:**

- Under 3,000 emails/month with simple needs: Resend Free or SendGrid Free.
- 3,000-50,000/month with good DX priority: Resend Pro.
- 50,000+/month and cost-sensitive: AWS SES (lowest per-email cost, higher setup effort).
- Deliverability is the top priority: Postmark.
- Already in AWS ecosystem: SES is the default unless DX matters more than cost.
