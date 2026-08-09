# Monthly Cost Review Checklist

Use this checklist at the start of each billing cycle to review the previous month's infrastructure spend.

---

## 1. Collect Bills

- [ ] Download or screenshot billing summary for each paid service
- [ ] Record total spend per service in cost tracking sheet
- [ ] Calculate month-over-month change for each service
- [ ] Flag any service with > 20% month-over-month increase

## 2. Review Top Spenders

For the top 3 services by cost:

- [ ] Identify the top cost driver within each service
- [ ] Check if usage-based charges are trending up, stable, or down
- [ ] Compare current usage to plan limits — are you near overage?
- [ ] Check for anomalies: unexpected spikes, new charges, or unfamiliar line items

## 3. Subscription Audit

- [ ] List all active subscriptions with their renewal dates
- [ ] Check for services not used in the past 30 days — cancel or downgrade
- [ ] Check for unused seats or add-ons — remove them
- [ ] Verify no duplicate services (two analytics tools, two email providers, etc.)

## 4. Free Tier Check

- [ ] For each paid service, check if usage has dropped below the free tier threshold
- [ ] If yes, evaluate downgrading to free tier

## 5. Quick Wins

- [ ] Remove unused preview deployments and branches (Vercel, Netlify)
- [ ] Clean up unused storage (Supabase, R2, S3)
- [ ] Check for stale Codespaces or CI artifacts
- [ ] Review auto-renewal settings on domains — disable for domains to drop

## 6. Record and Plan

- [ ] Update cost tracking sheet with this month's data
- [ ] Note any optimization actions to take this month
- [ ] Set calendar reminder for mid-cycle usage check
- [ ] If quarterly review is due, schedule the deep review

---

## Monthly Summary Template

```
Month: [YYYY-MM]
Total Infrastructure Spend: $[amount]
Month-over-Month Change: [+/-]$[amount] ([+/-]X%)

Top 3 Services:
1. [Service] — $[amount] ([main cost driver])
2. [Service] — $[amount] ([main cost driver])
3. [Service] — $[amount] ([main cost driver])

Actions Taken:
- [action 1]
- [action 2]

Actions Planned:
- [action 1]
- [action 2]
```
