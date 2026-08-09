# Domain Registrar Cost Guide

Reference for reducing domain registration and DNS costs, avoiding registrar upsells, and keeping a clean domain portfolio.

## Table of Contents

- [Provider Comparison](#provider-comparison)
- [Privacy Protection](#privacy-protection)
- [DNS Hosting](#dns-hosting)
- [Common Waste Patterns](#common-waste-patterns)
- [Transfer Savings](#transfer-savings)
- [Optimization Checklist](#optimization-checklist)
- [Monitoring](#monitoring)

## Provider Comparison

Prices are for a standard `.com` domain. Other TLDs vary significantly.

| Provider | Registration | Renewal | Transfer | Privacy | DNS | Notes |
|----------|-------------|---------|----------|---------|-----|-------|
| **Cloudflare** | ~$10 | ~$10 (at-cost) | ~$10 | Free | Free | At-cost pricing, no markup. No upsells. |
| **Porkbun** | ~$10 | ~$11 | ~$10 | Free | Free | Low prices, clean UI, no aggressive upsells. |
| **Namecheap** | ~$10 | ~$14 | ~$10 | Free (WhoisGuard) | Free (BasicDNS) | Renewal price higher than registration. |
| **GoDaddy** | ~$12 (promo ~$2 first year) | ~$22 | ~$12 | ~$10/year extra | Free (basic) | Aggressive upsells. Renewal price significantly higher than registration. |
| **Google Domains** | — | — | — | — | — | **Sunset in 2023.** Domains transferred to Squarespace. |

Key observations:

- Registration and renewal prices are almost always different. The registration price is a loss leader. Renewal is the real cost.
- GoDaddy's first-year promos are steep discounts that normalize to the highest renewal prices in this group.
- Cloudflare sells domains at wholesale (ICANN + registry cost), making it the cheapest for renewals.
- Google Domains no longer exists. Existing domains were migrated to Squarespace Domains.

## Privacy Protection

WHOIS privacy hides the registrant's name, email, and address from public WHOIS lookups.

| Provider | Privacy Cost | Notes |
|----------|-------------|-------|
| Cloudflare | Free | Enabled by default |
| Porkbun | Free | Enabled by default |
| Namecheap | Free | WhoisGuard included |
| GoDaddy | ~$10/year per domain | Charged as an add-on. Often pre-selected in cart. |
| Squarespace | Free | Inherited from Google Domains migration |

Paying for WHOIS privacy is unnecessary. Every major registrar except GoDaddy includes it for free. If currently paying for privacy at GoDaddy, this is an immediate savings opportunity by transferring out.

## DNS Hosting

DNS hosting is where name servers resolve queries for the domain. It does not need to be at the same provider as the registrar.

| Provider | Free DNS | Premium DNS | Notes |
|----------|----------|-------------|-------|
| Cloudflare | Yes (unlimited domains) | Enterprise tier | Industry-leading performance and DDoS protection on free tier |
| Porkbun | Yes | No premium tier | Adequate for most use cases |
| Namecheap | Yes (BasicDNS) | PremiumDNS ~$5/year | BasicDNS is fine for most domains |
| GoDaddy | Yes (basic) | Premium DNS ~$6/month | Premium DNS is rarely worth it |

Recommendation: Use Cloudflare for DNS regardless of where the domain is registered. Point nameservers to Cloudflare. Free tier includes Anycast, DDoS mitigation, and fast propagation.

## Common Waste Patterns

### Domains registered and never used

Domains bought for ideas that never materialized or projects that were abandoned. Each domain silently renews at the full renewal price annually.

**Fix:** Audit the full domain list quarterly. Set calendar reminders 30 days before each renewal. Cancel auto-renewal on any domain not actively serving traffic or protecting a brand.

### Privacy protection upsell

Paying $10/year per domain for WHOIS privacy at registrars that charge extra. On a portfolio of 10 domains at GoDaddy, that is $100/year for something Cloudflare and Namecheap provide for free.

**Fix:** Transfer to a registrar with free privacy.

### Premium DNS when standard DNS is fine

Paying for premium DNS at the registrar when the domain is a simple site or email-only setup. Premium DNS is only justified for high-traffic domains with strict uptime SLAs.

**Fix:** Cancel premium DNS. Use Cloudflare free DNS instead.

### Auto-renewal on domains no longer needed

Domains renew automatically by default. If a domain is no longer needed, it renews and charges appear on a credit card that may not be actively monitored.

**Fix:** Review auto-renewal status during each domain audit. Disable auto-renewal on any domain planned for retirement.

### Keeping DNS at an expensive registrar

Some registrars bundle DNS with domain management in a way that makes it feel mandatory. DNS can always be moved independently by updating nameservers.

**Fix:** Move DNS to Cloudflare (free). Keep the domain registered wherever it is if transfer is not worth the effort, but at minimum move DNS.

## Transfer Savings

Transferring a domain from GoDaddy to Cloudflare on a standard `.com`:

| Cost | GoDaddy | Cloudflare | Savings |
|------|---------|------------|---------|
| Annual renewal | ~$22 | ~$10 | ~$12/year |
| Privacy protection | ~$10/year | Free | ~$10/year |
| **Total per domain** | **~$32/year** | **~$10/year** | **~$22/year (69%)** |

On a portfolio of 5 domains: ~$110/year saved.
On a portfolio of 10 domains: ~$220/year saved.

Transfer process:

1. Unlock the domain at the current registrar.
2. Obtain the authorization/EPP code.
3. Initiate transfer at the new registrar (Cloudflare).
4. Approve the transfer via email confirmation.
5. Transfer completes in 5-7 days. The domain gains one year of registration at the new registrar's renewal price.

Constraints:

- Domains must be at least 60 days old to transfer.
- Some TLDs have specific transfer restrictions.
- Transfers extend registration by one year, so time transfers before the current renewal to avoid paying both.

## Optimization Checklist

1. **Audit all domains.** List every domain across all registrars. Include registration date, renewal date, renewal price, and current use status (active site, email only, parked, unused).
2. **Cancel unused domains.** Any domain not serving traffic, receiving email, or protecting a brand name should be dropped before its next renewal.
3. **Transfer domains to Cloudflare.** At-cost pricing, free privacy, free DNS. The transfer itself costs one year of renewal at Cloudflare's rate and extends registration by one year.
4. **Consolidate DNS to one provider.** Fewer DNS providers means fewer places to manage records, fewer credentials, and fewer bills. Cloudflare free tier handles this for unlimited domains.
5. **Set calendar reminders 30 days before each renewal date.** This gives time to decide whether to renew, transfer, or let the domain expire.
6. **Disable auto-renewal on domains planned for retirement.** Do this immediately after the decision is made, not 29 days before expiry.
7. **Remove paid privacy add-ons.** If any domains are paying for WHOIS privacy, transfer them to a registrar that includes it free or cancel the add-on if privacy is not critical.

## Monitoring

| Activity | Frequency | Action |
|----------|-----------|--------|
| Full domain audit | Annually (minimum) | Review every domain for active use, renewal cost, and registrar |
| Renewal date tracking | Ongoing | Calendar reminders 30 days before each renewal |
| Total portfolio cost | Annually | Sum all domain costs (registration + privacy + DNS) across all registrars |
| DNS provider review | Annually | Confirm all domains point to the intended DNS provider |
| Registrar consolidation check | Annually | Identify domains still at expensive registrars and evaluate transfer |

Track total annual domain portfolio cost as a single line item. For most startups and small teams, this should be under $100/year after optimization.
