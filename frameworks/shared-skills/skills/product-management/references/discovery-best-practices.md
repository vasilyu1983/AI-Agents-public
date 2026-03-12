# Discovery Best Practices  
*Operational playbook for running continuous, high-quality product discovery.*

This file contains ONLY:
- Patterns  
- Checklists  
- Decision trees  
- Copy-ready workflows  
- No theory, no stories  

---

# 1. Core Patterns

## 1.1 Opportunity Solution Tree (OST)

**Structure**
Outcome (metric you’re trying to move)

↳ Opportunities (customer problems / needs)
↳ Solutions (ideas, experiments)
↳ Experiments (tests to validate assumptions)


**Checklist**
- [ ] Outcome is measurable  
- [ ] Opportunities are phrased as problems, not features  
- [ ] Solutions are hypotheses, not commitments  
- [ ] Experiments have clear pass/fail criteria  
- [ ] Each branch ties directly to the outcome  

---

# 2. Discovery Cadence

## 2.1 Weekly Cadence (Continuous Discovery)

**Every week**
- [ ] 1–2 customer conversations  
- [ ] Update OST with new opportunities  
- [ ] Prioritize assumptions (value / usability / feasibility / viability)  
- [ ] Run at least 1 experiment  
- [ ] Synthesize insights into signals (strong / medium / weak)  

**Every month**
- [ ] Refresh outcome metrics  
- [ ] Retire invalidated branches  
- [ ] Add new opportunities discovered through interviews  

---

# 3. Customer Interview Patterns

## 3.1 The “Mom Test” Pattern (Past behavior only)

**Good Questions**
- “Tell me about the last time you…”
- “Walk me through how you solved that…”
- “What tools did you use?”
- “What happened right before / after?”
- “How much did that cost you (time, money, frustration)?”

**Avoid**
- “Would you use this?”  
- “Do you like this idea?”  
- “How much would you pay?”  

## 3.2 Interview Structure Template
Warm-Up (1 min)
Trigger: “Tell me about the last time you…”
Deep Dive: “Walk me through that step by step.”
Probing:
Alternatives tried?
Workarounds?
Impact of problem?
Closing:
Commitment test
Ask for artifacts (screenshots, exports)
Ask for people to talk to next

---

# 4. Assumption Mapping

## 4.1 Risk Categories
- **Value** – Will they care?  
- **Usability** – Can they use it?  
- **Feasibility** – Can we build it?  
- **Viability** – Should we build it? (legal, cost, brand)

## 4.2 Assumption Grid Template
                | Low Evidence | High Evidence
--------------------|--------------|--------------
High Risk | Prioritize | Monitor
Low Risk | Later | Ignore for now


---

# 5. Experiment Library

## 5.1 Value Tests
- **Smoke test** (landing page + CTA)  
- **Fake door** (“notify me”)  
- **Pitch test** (sell before building)  
- **Concierge test** (manual fulfillment)  
- **Prototype test** (narrated walk-through)

## 5.2 Usability Tests
- **Unmoderated usability**  
- **Think-aloud walkthrough**  
- **Task completion scoring**  

## 5.3 Feasibility Tests
- **Tech spike**  
- **API integration stub**  
- **Latency benchmark**  

## 5.4 Viability Tests
- **Legal review**  
- **Finance model check**  
- **Operational capacity test**  

---

# 6. Experiment Test Card

Hypothesis:
We believe that…

Assumption:
Value / Usability / Feasibility / Viability

Test:
Describe action to validate

Evidence:
What success looks like (numeric or binary)

Fail Condition:
What invalidates the hypothesis

Next Step:
What we’ll do if the test passes or fails


---

# 7. Opportunity Prioritization

## 7.1 Problem Prioritization Checklist
- [ ] Frequency of problem  
- [ ] Severity / cost of problem  
- [ ] Existing alternatives  
- [ ] Strategic alignment  
- [ ] Segment importance (who cares most?)  
- [ ] Evidence strength  

## 7.2 Problem Scoring Matrix
Score each 1–5:

Frequency
Impact
Evidence strength
Strategic alignment

Total Score = Sum (higher = better opportunity)

---

# 8. Insight Synthesis

## 8.1 Signal Strength Pattern
- **Strong signal**  
  - Multiple customers  
  - Same context  
  - High severity  
  - Existing workaround costs real effort  
- **Medium signal**  
  - Some evidence but inconsistent  
- **Weak signal**  
  - Isolated anecdote  

## 8.2 Insight Template
Pattern observed:
Evidence:
Impact on customer:
Opportunity wording:
Next test:


---

# 9. Discovery → Delivery Handoff

**Checklist**
- [ ] Validated solution (experiments pass)  
- [ ] Artifacts (screenshots, workflows, data)  
- [ ] User stories / jobs  
- [ ] Updated OST  
- [ ] Measurable outcome defined  
- [ ] Engineering feasibility checked  
- [ ] Risks documented  

---

# 10. Discovery Decision Tree

Do we understand the problem?
├─ No → Run interviews + map opportunities
└─ Yes
↓
Do we have high-risk assumptions?
├─ Yes → Run tests → update OST
└─ No
↓
Do we have evidence solution works?
├─ No → Run value/usability/feasibility tests
└─ Yes
↓
Ready for delivery


---

# 11. Continuous Discovery Operating Model

**Weekly Inputs**
- Customer conversations  
- Product analytics  
- Experiment results  

**Weekly Outputs**
- Updated OST  
- Prioritized assumptions  
- Validated learnings  
- Prepared next experiments  

---

# 12. Definition of Done (Discovery)

- [ ] We know **who** has the problem  
- [ ] We know **how often** and **how painful**  
- [ ] We’ve seen the problem in real behavior  
- [ ] We’ve validated the **key assumptions**  
- [ ] We’ve identified the **riskiest part first**  
- [ ] We’ve run **minimum 1 value + 1 usability test**  
- [ ] We have **clear evidence** the solution is worth building  

---

**End of file.**