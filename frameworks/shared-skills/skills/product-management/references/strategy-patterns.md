# Strategy Patterns  

*Operational guide for building, evaluating, and executing product strategy.*

This file contains ONLY:

- Patterns  
- Templates  
- Checklists  
- Decision trees  
- Zero theory or stories  

---

# 1. Strategy Kernel (Core Pattern)

Use this structure for ANY product strategy.

## 1.1 Structure

Diagnosis:
• What’s the real problem?
• What’s blocking progress?
• What evidence supports this?

Guiding Policy:
• Your approach to the problem
• The constraints you embrace
• The areas you choose NOT to pursue

Actions:
• Concrete moves (bets) aligned to guiding policy
• Focused, non-overlapping, high-leverage

## 1.2 Checklist

- [ ] Diagnosis is specific, evidence-backed  
- [ ] Guiding policy narrows focus  
- [ ] Actions are mutually reinforcing  
- [ ] No “wishful thinking” (vague goals ≠ strategy)  
- [ ] Can explain it in < 90 seconds  

---

# 2. Product Strategy Structure (Operational)

## 2.1 Strategy Template

Product Vision (3–5 years)
Diagnosis (the core challenge)
Strategic Focus Areas (2–4 themes)
Bets (concrete actions)
Outcomes (metrics tied to each focus area)
Guardrails (what we will NOT do)

---

# 3. Strategy Focus Areas (Patterns)

Each focus area must be a **problem space**, not a feature category.

### Common patterns

- **Acquisition acceleration**  
  - Problems: awareness, activation friction  
  - Metrics: signups, activation rate  
- **Retention lift**  
  - Problems: churn drivers, weak engagement  
  - Metrics: retention %, time-to-value  
- **Scalable foundation**  
  - Problems: reliability, performance, quality  
  - Metrics: uptime, latency, incident reduction  
- **Revenue expansion**  
  - Problems: low ARPU, unused value, upgrade friction  
  - Metrics: ARPU, expansion revenue  

---

# 4. Strategic Bet Patterns

Bets = concrete actions that express your strategy.  
They MUST be hypotheses, not commitments.

### Bet Starter Templates

- “We believe we can improve **[metric]** by solving **[problem]** for **[segment]** through **[approach]**.”  
- “If we validate **[assumption]**, we will invest in **[direction]**.”  
- “We will prioritize **[problem]** over **[other problem]** because **[reason]**.”  

### Bet Types

- **Acquisition bets**: new surfaces, channel experiments  
- **Activation bets**: onboarding redesign, guided flows  
- **Retention bets**: habit loops, key action reinforcement  
- **Monetization bets**: packaging, pricing tests  
- **Platform bets**: API/SDK, reliability upgrades  
- **Expansion bets**: adjacent use cases  

---

# 5. Competitive Mapping Patterns

## 5.1 Competitive Alternatives Table

Competitor (or Alternative) | Strengths | Weaknesses | Why Customers Choose It | Why They Switch

## 5.2 Differentiation Pattern

Your differentiation MUST come from:

- [ ] Attributes users care deeply about  
- [ ] Attributes competitors underperform on  
- [ ] Attributes consistent with your vision & constraints  

### Differentiation Types

- Speed / simplicity  
- Intelligence (AI-powered)  
- Integration / extensibility  
- Trust / compliance  
- Vertical depth  

---

# 6. Strategy Prioritization

## 6.1 Strategic Alignment Test

A focus area or bet qualifies ONLY if:

- [ ] It moves a top-level metric  
- [ ] It strengthens your differentiation  
- [ ] It supports your guiding policy  
- [ ] It eliminates a major risk  

If “No” to any → remove or reframe.

---

## 6.2 Portfolio Balance Pattern

Ensure your bets form a balanced portfolio:

- **50% near-term** (Now/Next)  
- **30% medium-term** (Next/Later)  
- **20% long-term** (frontier bets)  

---

# 7. OKR Pattern Library (Strategy-Aligned)

Use OKRs ONLY to express outcomes of strategic focus.

## 7.1 OKR Structure

Objective:
A qualitative, time-bound expression of strategic intent.

Key Results:
2–4 measurable outcomes linked to this objective.

### Examples (fill-in patterns)

**Acquisition**

- O: Increase qualified signups  
  - KR: +X% signup → activation  
  - KR: +X% quality score from new channels  

**Retention**

- O: Strengthen weekly engagement  
  - KR: Weekly active users +X%  
  - KR: Time-to-value -X days  

**Revenue**

- O: Expand paid adoption  
  - KR: ARPU +X%  
  - KR: Upgrade conversion +X%  

**Platform**

- O: Improve reliability  
  - KR: Latency -X%  
  - KR: Incidents -X%  

---

# 8. Strategy Decision Trees

## 8.1 Do you have a strategy?

Do you have a clear diagnosis?
├─ No → Conduct discovery → Identify root problem
└─ Yes
↓
Do you have a guiding policy?
├─ No → Choose focus & constraints
└─ Yes
↓
Do actions reinforce each other?
├─ No → Reduce/realign bets
└─ Yes → Strategy is ready

---

## 8.2 Should we add a new strategic bet?

Does it fit the vision?
├─ No → Reject
└─ Yes
↓
Does it solve a top-3 problem?
├─ No → Deprioritize
└─ Yes
↓
Can we test it in ≤ 6 weeks?
├─ No → Split or redesign
└─ Yes → Add as a bet

---

# 9. Product Explainability (2026 Pattern)

Products are now evaluated by AI systems (search, recommendations, comparison engines) before reaching human buyers. Product explainability is how clearly a product communicates its purpose, value, behavior, and limits to both people and AI systems.

## 9.1 Why This Matters

- AI-mediated discovery is replacing traditional search
- Comparison engines parse product metadata before showing to users
- LLM-powered assistants recommend products based on structured data
- Poor explainability = invisible to AI = invisible to customers

## 9.2 Explainability Checklist

**For AI Systems**

- [ ] Clear value proposition in structured format (JSON-LD, Open Graph)
- [ ] Feature documentation accessible to AI parsing
- [ ] Pricing transparency for comparison engines
- [ ] Use case definitions for AI-mediated recommendations
- [ ] FAQ content answering common comparison questions

**For Humans**

- [ ] Product behavior is predictable and documented
- [ ] Limitations are stated upfront
- [ ] Pricing model is understandable without sales call
- [ ] "What happens when..." edge cases are covered

## 9.3 Explainability Audit Template

```text
Product: [Name]
Value Prop (1 sentence):
Primary Use Cases (3-5):
Key Differentiators (2-3):
Limitations/Non-Goals:
Pricing Model Summary:
Structured Data Present: [ ] JSON-LD [ ] Open Graph [ ] Schema.org
```

---

# 10. Anti-Patterns

- AVOID: Strategy as a list of projects  
- AVOID: “Be better at everything” goals  
- AVOID: Copying competitor features  
- AVOID: No constraint definition  
- AVOID: More than 4 focus areas  
- AVOID: Bets written as commitments  
- AVOID: Strategy with no metrics  

---

# 10. Definition of Done (Strategy)

A strategy is **ready** when:

- [ ] You have a validated diagnosis  
- [ ] You have 2–4 focus areas  
- [ ] Each focus area has measurable outcomes  
- [ ] You have a small set of strategic bets  
- [ ] Bets map to outcomes  
- [ ] There are explicit non-goals  
- [ ] Alignment achieved with leadership & teams  

---

**End of file.**
