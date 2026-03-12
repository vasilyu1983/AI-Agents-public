# Roadmap Patterns  

*Operational guide for outcome-based and theme-based product roadmaps.*

This file contains ONLY:

- Structures
- Patterns
- Decision frameworks
- Checklists
- Copy-ready templates

---

# 1. Roadmap Structures

## 1.1 Outcome-Based Roadmap (Primary Pattern)

**Format**
Time Horizon: Now (0–3 mo) / Next (3–9 mo) / Later (9–18 mo)

For each horizon:
• Outcome (metric to improve)
• Themes (problem spaces)
• Example Bets (hypothesis-level, NOT commitments)

**Checklist**

- [ ] Roadmap expresses outcomes, not features  
- [ ] Themes map directly to outcomes  
- [ ] Each bet is a hypothesis, not a deliverable  
- [ ] No dates on features  
- [ ] Each theme has an owner  

---

## 1.2 Theme-Based Roadmap

**Structure**
Theme (Problem Space):
• Problem Statement
• Outcome Metric
• Key Risks
• Example Opportunities
• Example Tests / Experiments

**When to use**

- Large product surface area  
- Multiple teams working in parallel  
- Uncertainty is high  

---

## 1.3 Now / Next / Later Pattern

Use when:

- Priorities shift often  
- Need to avoid feature commitments  
- Stakeholders want time framing without deadlines  

Definitions:

- **Now** = Being worked on  
- **Next** = Preparatory work / discovery  
- **Later** = Strategy-aligned, but not staffed  

---

# 2. Prioritization Patterns

## 2.1 The 3 Filters (minimal, effective)

Use before anything goes on the roadmap:

**Filter 1: Strategic Fit**

- [ ] Aligns with product vision  
- [ ] Supports annual/company-level objectives  

**Filter 2: Value**

- [ ] Moves a meaningful metric  
- [ ] Clear problem + evidence  

**Filter 3: Feasibility**

- [ ] Tech/design can validate within roadmap horizon  

Only items passing **ALL 3** may appear.

---

## 2.2 RICE (Operational Adaptation)

Reach: # users/events per period
Impact: 1 (massive) / 0.75 / 0.5 / 0.25 (minimal)
Confidence: %
Effort: # person-weeks
Score = (Reach × Impact × Confidence) / Effort

Use for:

- Comparing initiatives inside a theme  
- Not for comparing across multiple products  

---

## 2.3 Problem Scoring Matrix

Use to prioritize **themes** rather than features:

Score each 1–5:
• Business value
• Customer value
• Evidence strength
• Effort (reverse score)
• Strategic alignment

---

## 2.4 Opportunity Scoring

Use when prioritizing based on customer-perceived value gaps.

**Method**

Survey customers to rank features/problems 1–10 on two dimensions:
1. **Importance**: How important is this to you?
2. **Satisfaction**: How satisfied are you with current solution?

**Formula**

```text
Opportunity Score = Importance + (Importance - Satisfaction)
```

High importance + low satisfaction = biggest opportunity.

**Template**

| Feature/Problem | Importance (1-10) | Satisfaction (1-10) | Opportunity Score |
|-----------------|-------------------|---------------------|-------------------|
| [Feature A]     | 9                 | 3                   | 15                |
| [Feature B]     | 7                 | 6                   | 8                 |
| [Feature C]     | 8                 | 4                   | 12                |

**When to Use**

- Comparing features within same product area
- Validating roadmap priorities with customer data
- Identifying low-hanging fruit improvements

**Checklist**

- [ ] Sample size >= 30 customers per segment
- [ ] Questions phrased consistently
- [ ] Respondents represent target segment
- [ ] Results compared across customer segments
- [ ] High-opportunity items mapped to roadmap themes

## 2.5 ICE Scoring (Lightweight Alternative)

Use for quick prioritization when reach data unavailable.

```text
Impact (1-10): How much will this move the metric?
Confidence (1-10): How sure are we about impact?
Ease (1-10): How easy is it to implement?

ICE Score = Impact × Confidence × Ease
```

**When to Use**

- Early-stage products without usage data
- Fast prioritization in discovery
- Growth experiments

---

# 3. Standing Roadmap Reviews

## 3.1 Monthly Review (Operative)

Agenda:

- [ ] Update outcome metrics  
- [ ] Review experiment results  
- [ ] Move items between Now/Next/Later  
- [ ] Remove invalidated items  
- [ ] Confirm upcoming discovery priorities  

---

## 3.2 Quarterly Refresh (Strategic)

Checklist:

- [ ] Align roadmap to annual company objectives  
- [ ] Reassess outcomes with leadership  
- [ ] Reprioritize themes  
- [ ] Add/remove bets based on evidence  
- [ ] Communicate changes (stakeholders + teams)  

---

# 4. Roadmap Communication Patterns

## 4.1 Stakeholder Alignment Deck (5 slides)

1. **Vision** – Where we’re headed  
2. **Strategy** – Focus areas / bets  
3. **Current Outcomes** – Metric progress  
4. **Roadmap** – Now / Next / Later  
5. **Risks & Requests** – What support is needed  

---

## 4.2 Script for “Outcome Roadmap Walkthrough”

Re-anchor on vision
State primary outcomes (metrics)
Describe themes (problem areas)
Walk through Now → Next → Later
Emphasize bets, not commitments
Ask for alignment: “Is anything missing or misaligned?”

---

## 4.3 Handling Feature Requests (Pattern)

When stakeholders say: “We need feature X.”

Response pattern:
Clarify problem: “What outcome are you trying to achieve?”
Map to theme/outcome on roadmap
If aligned → add as a potential bet
If misaligned → explain with strategy & outcomes
Offer a discovery slot for deeper evaluation

---

# 5. Decision Trees

## 5.1 Should This Go on the Roadmap?

Is it tied to a measurable outcome?
├── No → Exclude
└── Yes
↓
Is it a problem space (theme)?
├── Yes → Add under theme
└── No
↓
Is it a high-confidence initiative?
├── No → Put in “Next” for discovery
└── Yes → Put in “Now” or “Next” depending on staffing

---

## 5.2 Time Horizon Assignment

Now:

Validated idea
Clear metric
Team staffed
Next:

High potential
In discovery
Risk/assumption heavy
Later:

Strategically valuable
Unvalidated
Not yet staffed

---

# 6. Anti-Patterns (Do Not Use)

- AVOID: Roadmap as a list of features  
- AVOID: Dates tied to feature delivery  
- AVOID: “Nice to haves” written as commitments  
- AVOID: 20+ items competing for attention  
- AVOID: Promising deliverables before discovery is done  
- AVOID: Mixing discovery and delivery tasks on roadmap  

---

# 7. Definition of Done (Roadmap)

A roadmap is **ready to share** when:

- [ ] Expressed as **outcomes + themes**, not features  
- [ ] Includes **Now / Next / Later** with clear definitions  
- [ ] All themes tie to the product strategy  
- [ ] All bets are hypotheses (non-committal)  
- [ ] Outcomes include measurable metrics  
- [ ] Stakeholders aligned on objectives  
- [ ] Risks & dependencies are documented  
- [ ] Updated within the last 30 days  

---

**End of file.**
