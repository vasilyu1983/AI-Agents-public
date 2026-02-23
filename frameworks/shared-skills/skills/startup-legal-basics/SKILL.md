---
name: startup-legal-basics
description: "Use when setting up startup legal basics: incorporation/entity choices, founder IP assignment, contractor agreements, basic B2B contracting, privacy fundamentals, and legal readiness for selling/fundraising (not legal advice)."
---

# Startup Legal Basics

Foundational legal checklists for early-stage startups. This is not legal advice; use it to prepare and to work efficiently with qualified counsel.

## When to Use

- Choosing an entity setup and getting incorporation done
- Ensuring founders and contractors assign IP correctly
- Building a sane contracting process (MSA/SOW, DPA, basic procurement flow)
- Privacy basics: data mapping, roles (controller/processor), and policy scope
- Legal readiness for first customers and light fundraising prep

## When NOT to Use

- Jurisdiction-specific legal advice or interpretation of laws
- Complex regulated domains (health, finance, children’s privacy) without counsel
- Deep security compliance programs (SOC 2/ISO) -> [qa-observability](../qa-observability/) (technical controls) + dedicated compliance work

---

## Quick Start (Inputs)

- Primary jurisdiction(s): founder location, customer location(s)
- Entity goal: bootstrapped, VC-backed, or uncertain
- Product type: SaaS, marketplace, services, hybrid
- Data: what personal data is collected, and what third parties receive it
- Selling motion: self-serve terms vs negotiated B2B contracts

---

## Workflow

1) Entity and ownership setup
- Decide: LLC vs C-Corp (or local equivalent) based on funding expectations and tax/legal advice.
- Ensure founders have signed equity and IP documents early.

2) IP assignment and contractor hygiene
- Founders: assign IP to the company; confirm prior employer/IP constraints.
- Contractors: use written agreements with IP assignment + confidentiality.

3) Contracting basics for selling
- Decide your default contract stack: click-through terms vs MSA/SOW.
- Add a simple “contract intake” flow to avoid random obligations.

4) Privacy fundamentals (minimum viable)
- Create a data map (what you collect, why, where it goes, retention).
- Decide your roles: controller/processor where relevant.
- Ensure your policies match reality (do not claim controls you do not have).

5) Fundraising readiness (light)
- Keep a basic corporate record set (cap table, key agreements, IP assignments).
- Avoid “side agreements” that complicate diligence later.

---

## Resources

| Resource | Purpose |
|----------|---------|
| [entity-and-ownership-basics.md](references/entity-and-ownership-basics.md) | Entity decisions, founder docs checklist |
| [contracting-basics.md](references/contracting-basics.md) | Contract intake, common clauses, red flags |
| [privacy-basics.md](references/privacy-basics.md) | Data map, privacy roles, policy scope |
| [ip-protection-guide.md](references/ip-protection-guide.md) | IP types, assignment, open source licensing, trademark and patent strategy |
| [employment-law-basics.md](references/employment-law-basics.md) | Worker classification, employment docs, non-competes, international hiring |
| [terms-of-service-guide.md](references/terms-of-service-guide.md) | TOS drafting, SLA design, DPA requirements, cookie consent, enforceability |
| [equity-agreements-guide.md](references/equity-agreements-guide.md) | Founder equity splits, vesting schedules, 83(b) elections, advisor agreements |

## Templates

| Template | Purpose |
|----------|---------|
| [incorporation-checklist.md](assets/incorporation-checklist.md) | Incorporation and founder docs checklist |
| [ip-assignment-checklist.md](assets/ip-assignment-checklist.md) | Founder/contractor IP assignment checklist |
| [contract-intake-checklist.md](assets/contract-intake-checklist.md) | Intake questions and review flow |
| [data-map-template.md](assets/data-map-template.md) | Data map starter |

## Data

| File | Purpose |
|------|---------|
| [sources.json](data/sources.json) | Legal readiness references |

---

## Common Mistakes

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| Verbal equity promises | Legal disputes, cap table chaos | Written agreements only |
| Missing 83(b) election | 6-figure tax liability on illiquid stock | File within 30 days, calendar immediately |
| No contractor IP assignment | Company doesn't own code/content | Agreement signed before work starts |
| Policy/practice mismatch | Regulatory liability, failed audits | Data map validates privacy policy claims |
| Side deals with advisors | Due diligence failure, cap table mess | Everything documented in cap table |
| Unlimited liability accepted | Existential risk from customer contract | Cap at 12-24mo fees paid |
| Cookie banner doesn't block | GDPR violation | Test that cookies actually wait for consent |
| No DPA with vendors | GDPR violation when processing EU data | DPA with every vendor handling PII |

---

## What Good Looks Like

- Every contributor who writes code/content has signed a valid IP assignment to the company.
- You have a repeatable contract intake process and a default position on key terms.
- You know what data you collect and can explain it consistently across product, contracts, and policies.
- Your cap table is clean and matches all signed agreements.
- You can respond to a GDPR rights request within 30 days.
