# Opportunity Assessment Scorecard (Core, Non-AI)

Purpose: evaluate and prioritize customer problems before committing to solutions.

## Inputs

- Problem evidence (interviews, tickets, logs, revenue/churn drivers)
- Target segment(s) and current alternatives/workarounds
- Constraints (time, budget, compliance, dependencies)

## Outputs

- Scored opportunity with an explicit decision: Proceed / Explore / Park / Discard
- Next steps: the smallest learning plan to de-risk value, usability, feasibility, viability

## Core

# 1. Opportunity Assessment Template (Copy/Paste)

## 1. Problem Summary

Problem Statement:
User Segment:
Context (when problem occurs):
Frequency:
Severity:
Impact (time, money, emotion):
Evidence (quotes, data):

## 2. Current Workarounds / Alternatives

Workarounds users rely on:
Why these are insufficient:
Competitor solutions:
Why customers switch away:

## 3. Market & Customer Signals

% of target customers experiencing this (estimate + method):

Common patterns:
Who cares most (segment scoring):
Urgency level:

## 4. Strategic Fit

Alignment with product vision:
Alignment with company goals:
Dependencies:
Risks:

## 5. Metrics Impacted

List metrics this opportunity affects.

Primary metric:
Secondary metrics:
Guardrail metrics:

## 6. Opportunity Size (Rough)

TAM (lightweight estimate):
Affected user volume:
Time/cost savings per user:
Value creation potential:

## 7. Assumptions & Risks

Value Risks:
Usability Risks:
Feasibility Risks:
Viability Risks:

## 8. Recommended Next Steps

Proceed / Explore / Discard / Park

Immediate actions:
Experiments to run:
Stakeholders to align:

---

# 2. Opportunity Scoring Pattern

Score each on a 1–5 scale:

### **Impact**

1 = small nuisance  
5 = critical business outcome  

### **Frequency**

1 = rare  
5 = daily  

### **Evidence Strength**

1 = anecdotal / unverified  
3 = consistent qualitative evidence (multiple users)  
5 = triangulated evidence (qual + quant + observed behavior)  

### **Strategic Alignment**

1 = low  
5 = directly supports vision  

**Total Opportunity Score = Impact + Frequency + Evidence + Alignment**  
(Max 20)

---

# 3. “Who Cares Most?” Segmentation Score

For each segment, score 1–5:

- Pain severity  
- Pain frequency  
- Workaround cost  
- Segment strategic value  
- Budget / willingness  

**Segment Score = Sum (max 25)**  
Choose segment with highest score.

---

# 4. Decision Tree: Is This Opportunity Worth Pursuing?

Do many users experience this problem?
├─ No → Low priority
└─ Yes
↓
Is the pain severe and costly?
├─ No → Keep on radar
└─ Yes
↓
Is there strong evidence (interviews + data)?
├─ No → Run more discovery
└─ Yes
↓
Does solving it align with product strategy?
├─ No → Discard/Park
└─ Yes → Prioritize

---

# 5. Example (Editable)

1. Problem Summary

Problem: “Ops managers spend 3–5 hours weekly reconciling shipment data.”
Segment: Mid-size logistics companies
Frequency: Weekly
Severity: 4/5
Impact: Delays cause missed SLAs and penalties
Evidence: 6 interviews, analytics logs confirm manual exports

2. Alternatives

Workarounds: Spreadsheets, macros, manual calls
Competitors: TMS upgrades (expensive), BI tools (not automated)

3. Market Signals

Affected customers: 200+ accounts
Urgency: High during peak season

4. Strategic Fit

Aligns with vision to automate data operations

5. Metrics

Primary: Time-to-value
Secondary: Activation rate
Guardrail: Support tickets

6. Opportunity Size

~5 hours saved per week per user
High operational cost avoided

7. Risks

Value: Do they trust automation?
Usability: Will they understand automated changes?
Feasibility: API limits?
Viability: Pricing impact?

8. Next Steps

Proceed: HIGH PRIORITY
Experiments:

Fake door for “Auto-Reconcile”
Prototype guided reconciliation workflow

---

# 6. Opportunity Assessment Checklist

- [ ] Real user problem (not idea-driven)  
- [ ] Evidence from interviews + data  
- [ ] Financial impact considered  
- [ ] Clear segment that cares most  
- [ ] Workarounds documented  
- [ ] Strong strategic alignment  
- [ ] Metrics identified  
- [ ] Risks mapped  
- [ ] Next steps defined  

---

# 7. Definition of Done (Opportunity Assessment)

An opportunity is **ready** when:

- [ ] Problem is validated  
- [ ] Segment selected with scoring  
- [ ] Impact + frequency quantified  
- [ ] Alternatives known  
- [ ] Strategy fit confirmed  
- [ ] Score assigned  
- [ ] Decision made (Proceed / Explore / Discard / Park)  

---

## Decision Rules

- Proceed only if: evidence strength >= 3 (default; use 4-5 for high-cost bets) AND "who cares most" segment is explicit AND success metric is measurable.
- Explore if: evidence is mixed OR willingness-to-pay is unknown OR alternatives are poorly understood.
- Park if: strategic alignment is low but the problem is real.
- Discard if: problem is not severe, not frequent, or better solved by process/policy than product.

## Risks

- Bias: building for loud minorities or biased samples
- Misattribution: confusing correlation with causation in metrics
- Compliance/privacy: collecting or storing customer data without a clear purpose/retention plan
- Roadmap theater: scoring without changing decisions

## Optional: AI / Automation

Use only if allowed by policy and data handling rules.

- Synthesis: cluster interview notes and summarize themes; keep source links and spot-check quotes.
- Drafting: generate a first-pass assessment from raw notes; humans own scoring and decisions.
- Consistency: check for missing metrics definitions, fuzzy scope, or unsupported claims.

**End of file.**
