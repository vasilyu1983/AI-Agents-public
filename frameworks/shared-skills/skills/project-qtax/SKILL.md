---
name: project-qtax
description: UK taxation expert for HMRC, MTD, Self-Assessment, income tax, NI contributions, and tax software design. Advises on tax regulations, calculations, user flows, trends, and compliance. Uses web search for current rates and HMRC updates. (project)
metadata:
  globs: |
    **/*.md
    **/tax/**
    **/hmrc/**
    **/declaration/**
---

# UK Taxation Expert

Expert advisor for UK taxation, HMRC compliance, Making Tax Digital (MTD), and Self-Assessment. Provides tax calculations, regulatory guidance, and advice on tax software design patterns.

## When to Use This Skill

| Trigger | Action |
|---------|--------|
| "Calculate tax for..." | Run tax calculation with breakdown |
| "What's the tax on..." | Explain tax treatment + calculation |
| "HMRC MTD integration" | Reference MTD API guidance |
| "Self-Assessment deadline" | Provide filing deadlines |
| "Tax allowance for..." | Explain allowance + eligibility |
| "Tax software UX" | Advise on filing flow design |
| "NI contributions" | Calculate Class 2/4 NI |
| "Property income tax" | Explain rental income taxation |
| "Dividend tax" | Explain dividend allowance + rates |
| "Capital gains" | Explain CGT calculations |

Do NOT use for:

- Non-UK tax jurisdictions → refer to local tax authority
- Corporation Tax (CT600) → separate HMRC service
- VAT returns → separate HMRC MTD service
- Payroll/RTI → employer obligations, not self-assessment
- Regulated financial advice → refer to qualified accountant/IFA

---

**Role**: You are a UK taxation expert with deep knowledge of:

- **Self-Assessment**: Full SA100/SA102/SA103/SA105/SA108 form knowledge
- **HMRC MTD**: Making Tax Digital APIs, GovTalk XML, submission protocols
- **Income Tax**: Bands, rates, allowances, reliefs for all income types
- **National Insurance**: Class 2/4 for self-employed, thresholds, calculations
- **Tax Software Design**: UX patterns for tax filing applications

**Approach**: Provide accurate calculations with explanations. Always cite current tax year rates. Use web search for volatile data. Include disclaimers for complex scenarios requiring professional advice.

---

## Quick Reference: Tax Rates 2025/26

### Income Tax Bands (England, Wales, NI)

| Band | Taxable Income | Rate |
|------|----------------|------|
| Personal Allowance | Up to £12,570 | 0% |
| Basic Rate | £12,571 - £50,270 | 20% |
| Higher Rate | £50,271 - £125,140 | 40% |
| Additional Rate | Over £125,140 | 45% |

**Note**: Personal Allowance reduces by £1 for every £2 earned over £100,000 (fully tapered at £125,140).

### Scottish Tax Bands 2025/26

| Band | Taxable Income | Rate |
|------|----------------|------|
| Personal Allowance | Up to £12,570 | 0% |
| Starter Rate | £12,571 - £15,397 | 19% |
| Basic Rate | £15,398 - £27,491 | 20% |
| Intermediate Rate | £27,492 - £43,662 | 21% |
| Higher Rate | £43,663 - £75,000 | 42% |
| Advanced Rate | £75,001 - £125,140 | 45% |
| Top Rate | Over £125,140 | 48% |

*Source: [mygov.scot](https://www.mygov.scot/scottish-income-tax/current-income-tax-rates)*

### Dividend Tax Rates 2025/26

| Band | Rate |
|------|------|
| Dividend Allowance | £500 tax-free |
| Basic Rate | 8.75% |
| Higher Rate | 33.75% |
| Additional Rate | 39.35% |

### Capital Gains Tax 2025/26

| Asset Type | Basic Rate | Higher Rate |
|------------|------------|-------------|
| Residential Property | 18% | 24% |
| Other Assets | 10% | 20% |
| Annual Exemption | £3,000 | - |

*IMPORTANT: Always use WebSearch to verify current rates — they change annually in April.*

---

## Quick Reference: Key Deadlines 2025/26

| Event | Deadline |
|-------|----------|
| Tax Year Ends | 5 April 2026 |
| Register for Self-Assessment | 5 October 2026 |
| Paper Return Deadline | 31 October 2026 |
| Online Return Deadline | 31 January 2027 |
| Pay Tax Owed | 31 January 2027 |
| 1st Payment on Account | 31 January 2027 |
| 2nd Payment on Account | 31 July 2027 |

**Penalties**:

- Late filing: £100 immediate + daily penalties after 3 months
- Late payment: 5% of tax owed + interest

---

## Quick Reference: Common Allowances

| Allowance | Amount | Notes |
|-----------|--------|-------|
| Personal Allowance | £12,570 | Reduces over £100k income |
| Trading Allowance | £1,000 | For small self-employment income |
| Property Allowance | £1,000 | For small rental income |
| Savings Allowance (Basic) | £1,000 | £500 for higher rate, £0 for additional |
| Dividend Allowance | £500 | Down from £1,000 in 2023/24 |
| Marriage Allowance | £1,260 | Transfer to spouse if non-taxpayer |
| Blind Person's Allowance | £3,070 | Additional allowance |
| Capital Gains Exemption | £3,000 | Down from £6,000 in 2023/24 |

---

## Decision Tree: Request Routing

```text
User Request
    │
    ├─ Tax calculation?
    │   ├─ Income tax? → [references/tax-rates-allowances.md]
    │   ├─ NI contributions? → [references/ni-contributions.md]
    │   ├─ Dividend tax? → [references/tax-rates-allowances.md]
    │   ├─ Capital gains? → [references/tax-rates-allowances.md]
    │   └─ Full scenario? → [references/tax-scenarios.md]
    │
    ├─ Self-Assessment process?
    │   ├─ How to file? → [references/self-assessment-guide.md]
    │   ├─ Which forms? → [references/self-assessment-guide.md]
    │   ├─ Deadlines? → Quick Reference above
    │   └─ Payment options? → [references/self-assessment-guide.md]
    │
    ├─ HMRC/MTD integration?
    │   ├─ API endpoints? → [references/hmrc-mtd-integration.md]
    │   ├─ Authentication? → [references/hmrc-mtd-integration.md]
    │   ├─ Submission format? → [references/hmrc-mtd-integration.md]
    │   └─ Error handling? → [references/hmrc-mtd-integration.md]
    │
    ├─ Tax software design?
    │   ├─ User flows? → [references/tax-software-ux.md]
    │   ├─ Section patterns? → [references/tax-software-ux.md]
    │   ├─ UX decisions? → [references/tax-software-ux.md]
    │   └─ Form design? → [references/tax-software-ux.md]
    │
    ├─ Specific scenarios?
    │   ├─ Company director? → [references/tax-scenarios.md]
    │   ├─ Freelancer? → [references/tax-scenarios.md]
    │   ├─ Landlord? → [references/tax-scenarios.md]
    │   └─ Multiple income? → [references/tax-scenarios.md]
    │
    └─ Audit/Review?
        ├─ Tax calculation check? → [assets/tax-calculation-review.md]
        └─ User flow review? → [assets/user-flow-audit.md]
```

---

## Tax Filing Software: Common Patterns

### 7 Standard Tax Sections (SA Return)

| Section | SA Form | Description |
|---------|---------|-------------|
| Employment | SA102 | PAYE income, benefits, expenses |
| Self-Employment | SA103 | Sole trader income and expenses |
| Dividends | SA100 | UK dividend income |
| Bank Interest | SA100 | Savings and interest income |
| Property Income | SA105 | Rental income |
| Capital Gains | SA108 | Asset disposals |
| Tax Payments | SA100 | Payments on account made |

### Common Filing Patterns

| Pattern | Prevalence | Sections Used |
|---------|------------|---------------|
| Company Director | 30% | Employment + Dividends |
| Employee Only | 25% | Employment |
| Landlord | 15% | Property (+ Employment) |
| Freelancer | 10% | Self-Employment |
| Investor | 10% | Dividends + Interest + CGT |
| Mixed | 10% | Multiple sections |

### User Personas

1. **Sole Traders/Freelancers**: Self-employment income, expense tracking, Class 4 NI
2. **Company Directors**: PAYE salary + dividends, tax-efficient extraction
3. **Landlords**: Property income, mortgage interest relief, capital allowances
4. **Employees with Side Income**: PAYE + additional income requiring SA

---

## Tax Calculation Formulas

### Income Tax Calculation

```text
1. Total Income = Employment + Self-Employment + Dividends + Interest + Property + Other
2. Allowable Deductions = Pension contributions + Gift Aid + Allowable expenses
3. Taxable Income = Total Income - Personal Allowance - Deductions
4. Income Tax = Sum of (Income in each band × Rate for that band)
5. Tax Due = Income Tax - Tax Already Paid (PAYE) - Tax Credits
```

### National Insurance (Self-Employed)

```text
Class 2 NI (2025/26):
- £3.50/week (voluntary for most self-employed since April 2024)
- Automatic NI credits if profits > Small Profits Threshold (£6,845)
- Voluntary payment only needed if profits < £6,845 and want NI credits
- Annual (if paying voluntarily): £182.00 (52 × £3.50)

Class 4 NI (2025/26):
- 0% on profits up to £12,570
- 6% on profits £12,571 - £50,270
- 2% on profits over £50,270
```

### Dividend Tax Calculation

```text
1. Total Dividends received
2. Subtract Dividend Allowance (£500)
3. Add remaining dividends to other income
4. Tax at marginal rate:
   - Basic rate band: 8.75%
   - Higher rate band: 33.75%
   - Additional rate band: 39.35%
```

**See**: [references/tax-scenarios.md](references/tax-scenarios.md) for worked examples

---

## Web Search Protocol

**IMPORTANT**: For any question about current rates, HMRC updates, or market conditions, you MUST use WebSearch.

### Required Searches

1. Search: `"UK income tax rates 2025/26 HMRC"`
2. Search: `"HMRC self-assessment deadline 2026"`
3. Search: `"Making Tax Digital updates 2025 2026"`
4. Search: `"UK National Insurance rates self-employed 2025/26"`
5. Search: `"HMRC MTD API changes 2026"`

### When to Search

- Tax rates or thresholds (change annually)
- HMRC policy announcements
- MTD compliance requirements
- Filing deadline changes
- New reliefs or allowances
- Budget/Autumn Statement changes

### What to Report

After searching, provide:

- **Current official data** with source (gov.uk preferred)
- **Comparison to skill baseline** (if rates have changed)
- **Effective dates** for any changes
- **Impact on filing software** if relevant

---

## HMRC MTD Integration Summary

### API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/individuals/self-assessment` | SA return submission |
| `/individuals/calculations` | Tax calculation |
| `/individuals/reliefs` | Claim reliefs |
| `/individuals/income-received` | Report income |

### Authentication

- OAuth 2.0 with Government Gateway credentials
- Separate user and application credentials
- Token refresh required every 4 hours

### Submission Flow

1. Create calculation → Get calculation ID
2. Submit return → Get submission ID
3. Poll status → Accepted/Rejected
4. Handle errors → Resubmit if needed

**See**: [references/hmrc-mtd-integration.md](references/hmrc-mtd-integration.md) for full details

---

## MTD ITSA Mandation Timeline

| From | Income Threshold | Requirement |
|------|------------------|-------------|
| April 2026 | £50,000+ | Mandatory quarterly reporting |
| April 2027 | £30,000+ | Mandatory quarterly reporting |
| April 2028 | £20,000+ | Mandatory quarterly reporting |

### Quarterly Update Deadlines

| Quarter End | Deadline |
|-------------|----------|
| 5 July (or 30 June) | 7 August |
| 5 October (or 30 September) | 7 November |
| 5 January (or 31 December) | 7 February |
| 5 April (or 31 March) | 7 May |

### Penalty Points System

- Each missed quarterly update = 1 penalty point
- **£200 fine** when reaching 4 points
- Points expire after 12 months of compliance
- **Soft landing**: First cohort (April 2026) won't receive points for first 4 missed updates

### Exemptions

- Taxpayers subject to power of attorney (permanent)
- Trusts, estates, non-resident companies (until April 2029)
- Digitally excluded (age, disability, no internet)
- Partnerships (date TBD)

---

## Upcoming Changes (April 2026)

| Change | Current (2025/26) | From 6 April 2026 |
|--------|-------------------|-------------------|
| Dividend Tax (Basic) | 8.75% | 10.75% |
| Dividend Tax (Higher) | 33.75% | 35.75% |
| Dividend Tax (Additional) | 39.35% | 39.35% (unchanged) |
| MTD ITSA (£50k+) | Voluntary | Mandatory |

*Source: Autumn Budget 2025 (November 2025)*

---

## Navigation

**Resources**

- [references/tax-rates-allowances.md](references/tax-rates-allowances.md) — Complete rate tables, allowances, thresholds
- [references/self-assessment-guide.md](references/self-assessment-guide.md) — Filing process, forms, deadlines
- [references/hmrc-mtd-integration.md](references/hmrc-mtd-integration.md) — MTD API reference for developers
- [references/tax-software-ux.md](references/tax-software-ux.md) — Tax software UX patterns and design
- [references/tax-scenarios.md](references/tax-scenarios.md) — Common scenarios with calculations
- [references/ni-contributions.md](references/ni-contributions.md) — Class 2/4 NI for self-employed

**Templates**

- [assets/tax-calculation-review.md](assets/tax-calculation-review.md) — Calculation audit checklist
- [assets/user-flow-audit.md](assets/user-flow-audit.md) — UX review framework

---

## Authoritative Sources

**Official HMRC**

- **Self-Assessment**: gov.uk/self-assessment-tax-returns
- **MTD API**: developer.service.hmrc.gov.uk
- **Tax Manuals**: gov.uk/hmrc-internal-manuals
- **Tax Rates**: gov.uk/income-tax-rates
- **NI Rates**: gov.uk/national-insurance-rates-letters

**Professional Bodies**

- **ICAEW**: icaew.com — Chartered Accountants guidance
- **ACCA**: accaglobal.com — Professional standards
- **ATT**: att.org.uk — Tax Technicians resources
- **CIOT**: tax.org.uk — Chartered Institute of Taxation

**Industry**

- **AccountingWEB**: accountingweb.co.uk — News and updates
- **TaxJournal**: taxjournal.com — Technical analysis
- **Taxation**: taxation.co.uk — Professional publication

---

## Key Disclaimers

**This skill provides information and calculation assistance only.**

- **NOT** regulated tax advice (for binding decisions, consult a qualified accountant)
- **NOT** legal advice (for disputes, consult a tax solicitor)
- **NOT** financial advice (for investments, consult an IFA)

**Always recommend professional advice for**:

- Complex tax situations (£100k+ income, international elements)
- Tax investigations or disputes with HMRC
- Business structures and incorporation decisions
- Inheritance tax planning
- R&D tax credits and other specialist reliefs

**Rate Verification**: Tax rates change annually. Always verify current rates via WebSearch or gov.uk before relying on calculations.
