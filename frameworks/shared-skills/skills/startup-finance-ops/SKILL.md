---
name: startup-finance-ops
description: "Use when setting up or improving startup finance operations: bookkeeping workflow, billing/collections, cash runway and forecasting, monthly close, KPI packs (burn, burn multiple), finance controls, compliance awareness (entity/tax/VAT triggers), and fundraising finance readiness."
---

# Startup Finance Ops

Operational finance for survival: keep books clean enough to make decisions, protect cash, and avoid “unit economics but no runway” failure.

This is not accounting or tax advice. Use it to build a finance cadence and to work effectively with professionals.

## When to Use

- You need a basic finance operating system (solo founder or early team)
- Cash runway, burn, burn multiple, and forecasting for the next 13 weeks
- Billing and collections process (invoices, payment terms, follow-ups)
- Monthly close cadence and a minimal KPI pack
- Translating pricing/packaging into billing mechanics and cash impact
- Compliance awareness: entity setup, tax obligations, VAT/sales tax triggers
- Bookkeeping setup: accrual vs cash, reconciliation, chart of accounts
- Finance readiness for fundraising or audit prep

## When NOT to Use

- Detailed tax strategy or jurisdiction-specific filings -> [project-qtax](../project-qtax/) (UK only)
- Pricing and unit economics modeling -> [startup-business-models](../startup-business-models/)
- Full accounting or audit services (hire a professional)

---

## Quick Start (Inputs)

- Business model: subscription, usage-based, services, hybrid
- Billing method: card, invoice, ACH/wire; payment terms
- Current tooling: bank, invoicing, bookkeeping (or none)
- Revenue and expense structure: top 5 categories, major vendors, payroll/contractors
- Current runway and any upcoming commitments

---

## Workflow

1) Set up a minimal finance stack
- Bank account separation (business vs personal).
- Invoicing + payment collection workflow (even if manual).
- Bookkeeping tool/process (or outsourced).

2) Define a simple chart of accounts (CoA)
- Keep categories stable so month-over-month comparisons work.
- Separate COGS vs operating expenses.

3) Install billing and collections SOP
- Use `assets/billing-and-collections-sop.md`.
- Decide what “past due” means and what happens at 7/14/30 days.

4) Build a 13-week cash forecast (survival view)
- Use `assets/13-week-cash-forecast.md`.
- Update weekly with actuals and adjust decisions (hiring, spend, commitments).

5) Run a monthly close (lightweight)
- Use `assets/month-end-close-checklist.md`.
- Goal: numbers are directionally correct and consistent, not perfect.

6) Produce a minimal KPI pack
- Use `assets/finance-kpi-pack.md`.
- Tie decisions to cash: new spend must have a hypothesis and a stop rule.

---

## Unit Economics vs Cash (Critical)

Unit economics answers "is this a good business if it scales?"
Cash answers "do we survive long enough to find out?"

Common mismatch:
- Great gross margin but slow collections (AR) and high upfront costs
- Healthy LTV:CAC assumptions with no proof of payback time
- Usage-based revenue with variable compute costs that spike before pricing catches up

---

## Compliance Awareness (Not Tax Advice)

You are not an accountant. But you need to know enough to avoid expensive surprises and work effectively with professionals.

**Entity type -> tax obligations** (get jurisdiction-specific advice):

| Entity | Typical Tax Obligations | Watch For |
|--------|------------------------|-----------|
| Sole trader / sole prop | Personal income tax on all profit | Unlimited liability; no separation |
| LLC / LLP | Pass-through or elect corp tax | State/country variations; self-employment tax |
| Ltd (UK) / GmbH / SAS | Corporation tax + director obligations | Payroll for directors; annual filings |
| C-Corp (US) | Corporate tax + payroll | Double taxation; 83(b) elections for founders |

**VAT / sales tax triggers** (check before first revenue):
- Domestic revenue threshold (e.g., UK: GBP 90k; EU: varies by country; US: economic nexus by state)
- Cross-border digital services (EU: OSS/IOSS; US: state nexus rules)
- B2B reverse charge rules (know when you charge VAT vs buyer self-assesses)

**Payroll tax basics** (triggered when you hire):
- Contractor vs employee classification (misclassification = penalties)
- Employer tax obligations (NI, FICA, or equivalent)
- Equity/option tax events (exercise, vesting, sale)

**When to hire an accountant** (triggers, not timeline):
- First revenue or first employee (whichever comes first)
- Cross-border sales or customers in multiple tax jurisdictions
- Fundraising (investors expect clean books and a cap table)
- Annual filings deadline approaching with no process

**Red flags — stop and get professional help**:
- Mixing personal and business funds with no separation
- Revenue in multiple countries with no tax registration
- Equity grants with no tax advice to recipients
- Payroll without proper withholding setup

For deeper entity comparisons and jurisdiction checklists, see `references/compliance-awareness.md`.

---

## Bookkeeping Fundamentals

**Accrual vs cash basis** — choose early, stay consistent:
- Cash basis: record when money moves. Simpler. Fine for early-stage, most small businesses.
- Accrual basis: record when earned/incurred. Required for GAAP/IFRS, needed for fundraising at Series A+.
- Switch trigger: when investors or auditors require accrual, or annual revenue exceeds local threshold.

**Reconciliation cadence**:
- Weekly: bank account reconciliation (15 min — catch errors early)
- Monthly: credit cards, payroll, subscriptions, AR/AP
- Quarterly: review chart of accounts, clean up miscategorized transactions

**Common founder bookkeeping mistakes**:

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| No separate business bank account | Audit nightmare; pierces LLC veil | Open a business account before first transaction |
| Categorizing everything as "general expense" | Useless P&L; bad tax deductions | Use 10-15 categories max, be consistent |
| Ignoring accounts receivable aging | Cash surprises; bad forecasting | Track AR weekly with follow-up SOP |
| No receipt/invoice storage | Failed audits; lost deductions | Use a tool (Dext, Hubdoc) or a folder per month |
| Delaying bookkeeping until tax time | Months of catch-up; errors compound | Close books monthly, even if rough |

**Finance readiness checklist** (fundraising / audit / hiring finance): see `assets/finance-readiness-checklist.md`.

---

## Anti-Patterns (What NOT to Do)

| Anti-Pattern | Why It Fails | Better Approach |
|--------------|--------------|-----------------|
| Forecasting uncommitted pipeline as revenue | Overstates cash position; surprises when deals slip | Only count signed contracts or card-on-file |
| Single-scenario forecasting | Blind to downside risk | Always maintain base/optimistic/pessimistic |
| Monthly-only cash review | Too slow to catch problems | Weekly 13-week forecast update |
| Ignoring AR timing | Invoice sent ≠ cash received | Track days-to-collection separately |
| "We'll fundraise before we run out" | Markets change; diligence takes longer | Start fundraising at 6-9 months runway |
| Gross margin confusion | Excluding variable costs inflates margins | Include all COGS (compute, payments, support) |
| No tax registration before first invoice | Penalties, back-taxes, lost deductions | Register entity and tax IDs before revenue |
| Skipping VAT registration past threshold | Retroactive VAT liability on past sales | Monitor revenue against domestic threshold monthly |
| Founder salary = "I'll just take what's left" | No payroll tax compliance; messy books | Set a modest salary, run proper payroll |

---

## Resources

| Resource | Purpose |
|----------|---------|
| [bookkeeping-stack.md](references/bookkeeping-stack.md) | Minimal tooling and roles |
| [cash-and-saas-metrics.md](references/cash-and-saas-metrics.md) | Runway, burn, burn multiple, and KPI definitions |
| [pricing-to-billing.md](references/pricing-to-billing.md) | Turning pricing into invoices, terms, and cash impact |
| [compliance-awareness.md](references/compliance-awareness.md) | Entity comparison, jurisdiction checklist, when-to-hire decision tree |
| [financial-modeling-basics.md](references/financial-modeling-basics.md) | 3-statement model, revenue/expense modeling, scenario analysis, model hygiene |
| [fundraising-finance-readiness.md](references/fundraising-finance-readiness.md) | Finance diligence prep, data room, GAAP readiness, accrual conversion |
| [ar-collections-management.md](references/ar-collections-management.md) | AR aging, collections workflow, DSO benchmarks, dunning sequences |
| [budget-planning-allocation.md](references/budget-planning-allocation.md) | Budget frameworks, stage benchmarks, scenario budgeting, governance |

## Templates

| Template | Purpose |
|----------|---------|
| [billing-and-collections-sop.md](assets/billing-and-collections-sop.md) | Billing, follow-ups, escalation |
| [13-week-cash-forecast.md](assets/13-week-cash-forecast.md) | Weekly cash forecast |
| [month-end-close-checklist.md](assets/month-end-close-checklist.md) | Close cadence |
| [finance-kpi-pack.md](assets/finance-kpi-pack.md) | Minimal KPI pack |
| [finance-readiness-checklist.md](assets/finance-readiness-checklist.md) | Fundraising / audit / hire-finance readiness |

## Data

| File | Purpose |
|------|---------|
| [sources.json](data/sources.json) | Finance ops references |

---

## What Good Looks Like

- You can answer “how many weeks of runway” from a single sheet that is updated weekly.
- Every invoice has an owner and a follow-up schedule; AR is not a surprise.
- You review burn and burn multiple monthly and make decisions (cut, pause, double down).
