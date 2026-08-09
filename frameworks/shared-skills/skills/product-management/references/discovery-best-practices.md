# Discovery Best Practices  
*Operational playbook for running continuous, high-quality product discovery.*

This file contains ONLY:
- Patterns  
- Checklists  
- Decision trees  
- Copy-ready workflows  
- No theory, no stories  

---
## Table of Contents

- [1.1 Opportunity Solution Tree (OST)](#11-opportunity-solution-tree-ost)
- [2. Discovery Cadence](#2-discovery-cadence)
- [2.1 Weekly Cadence (Continuous Discovery)](#21-weekly-cadence-continuous-discovery)
- [3. Customer Interview Patterns](#3-customer-interview-patterns)
- [3.1 The “Mom Test” Pattern (Past behavior only)](#31-the-“mom-test”-pattern-past-behavior-only)
- [3.2 Interview Structure Template](#32-interview-structure-template)
- [4. Assumption Mapping](#4-assumption-mapping)
- [4.1 Risk Categories](#41-risk-categories)
- [4.2 Assumption Grid Template](#42-assumption-grid-template)
- [5. Experiment Library](#5-experiment-library)
- [5.1 Value Tests](#51-value-tests)
- [5.2 Usability Tests](#52-usability-tests)
- [5.3 Feasibility Tests](#53-feasibility-tests)
- [5.4 Viability Tests](#54-viability-tests)
- [6. Experiment Test Card](#6-experiment-test-card)
- [7. Opportunity Prioritization](#7-opportunity-prioritization)
- [7.1 Problem Prioritization Checklist](#71-problem-prioritization-checklist)
- [7.2 Problem Scoring Matrix](#72-problem-scoring-matrix)
- [8. Insight Synthesis](#8-insight-synthesis)
- [8.1 Signal Strength Pattern](#81-signal-strength-pattern)
- [8.2 Insight Template](#82-insight-template)
- [9. Discovery → Delivery Handoff](#9-discovery-→-delivery-handoff)
- [10. Discovery Decision Tree](#10-discovery-decision-tree)
- [11. Continuous Discovery Operating Model](#11-continuous-discovery-operating-model)
- [12. Definition of Done (Discovery)](#12-definition-of-done-discovery)
- [13. Enterprise & Multi-Stakeholder Discovery](#13-enterprise--multi-stakeholder-discovery)
- [14. JTBD Switch Interview](#14-jtbd-switch-interview)
- [15. Voice-of-Customer at Scale (CAB & VoC)](#15-voice-of-customer-at-scale-cab--voc)
- [16. When You Cannot Talk to Users](#16-when-you-cannot-talk-to-users)
- [17. Discovery Theatre — Warning Signs](#17-discovery-theatre--warning-signs)


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

# 13. Enterprise & Multi-Stakeholder Discovery

## 13.1 Why Single-User Interviews Fail in B2B

In enterprise deals the person who feels the pain, the person who signs the contract, the person who uses the product daily, and the person who vetoes on technical grounds are four different humans with four different jobs-to-be-done. Interviewing only end users produces high-fidelity data on the wrong question.

## 13.2 Interview Focus by Role

| Role | Primary concern | What "value" means | Key questions to ask |
|---|---|---|---|
| **Champion** | Internal selling, political risk, career stake | "This makes me look good and is low-risk to sponsor" | What does success look like for your team in 6 months? Who else needs to say yes? What would cause this initiative to stall? |
| **Economic Buyer** | Budget authority, ROI narrative, board-level risk | "Return justifies the outlay; downside is bounded" | How does this map to a budget line? What is the cost of the status quo? What would make you pause the purchase? |
| **End User** | Daily workflow friction, learning curve, adoption | "This is less painful than what I do today" | Walk me through your current process step by step. Where do you lose the most time? What would you need to see to switch? |
| **Technical Evaluator** | Security, integration, compliance, operability | "This does not create a liability or an ops burden" | What security review does this need to pass? What systems must it integrate with? Who owns it after go-live? |

## 13.3 Multi-Stakeholder Synthesis Note

Map each finding to a role column. A deal or opportunity is real only when all four jobs are addressed. If evidence is missing for any role, that is a discovery gap — not a solved problem.

Synthesis template:

```
Opportunity: [problem statement]

Champion evidence:    [what you heard / confidence]
Econ Buyer evidence:  [what you heard / confidence]
End User evidence:    [what you heard / confidence]
Tech Eval evidence:   [what you heard / confidence]

Gap:  [which role is under-evidenced]
Next: [who to interview next]
```

---

# 14. JTBD Switch Interview

## 14.1 Purpose

Reconstructs the timeline of a real switch — from the moment a customer first felt dissatisfied to first use of the new solution. Reveals the real competitor (often "do nothing" or a spreadsheet) and the real job, which feature-comparison interviews miss entirely.

## 14.2 Forces of Progress Model

Four forces determine whether a switch happens:

```
                   SWITCH HAPPENS
                   when (Push + Pull) > (Anxiety + Habit)

Push    — dissatisfaction driving the customer away from the current situation
Pull    — attraction toward the new solution's promised outcome
Anxiety — fear of the new (cost, learning curve, lock-in, failure)
Habit   — comfort of the present ("good enough," sunk cost, inertia)
```

Discovery goal: surface all four forces, not just Pull. Most teams only ask about Pull and miss why deals stall.

## 14.3 Switch Timeline

Reconstruct in chronological order during the interview:

```
1. First thought     — "When did you first realize the current solution wasn't working?"
2. Passive looking   — "Did you start noticing alternatives? What triggered that?"
3. Active looking    — "What made you move from browsing to actually evaluating?"
4. Decision moment   — "What finally tipped you to buy / commit?"
5. First use         — "What happened the first time you used it? What surprised you?"
```

## 14.4 Example Switch-Interview Questions

1. "Tell me about the moment you first thought your current approach wasn't cutting it."
2. "What was the last straw — the event that made you start looking seriously?"
3. "What other options did you consider? Why did you rule each one out?"
4. "What almost stopped you from switching?"
5. "What were you most worried would go wrong after you committed?"
6. "What did you have to give up or stop doing to make this work?"
7. "Looking back, what was the real job you were hiring this to do?"

## 14.5 What This Finds That Feature Comparison Misses

- The real competing alternative (frequently a manual process, a spreadsheet, or doing nothing — not a named competitor)
- The emotional and social context of the switch decision
- Anxiety triggers that kill deals in the final stage
- The precise moment of progress — the struggling moment — where a new entrant can win

---

# 15. Voice-of-Customer at Scale (CAB & VoC)

## 15.1 Customer Advisory Board (CAB) Design Checklist

**Membership**
- [ ] 8–12 strategic accounts (not just largest — include fast-growing, early adopters, and at-risk)
- [ ] Mix of Champion, Economic Buyer, and senior End User roles across members
- [ ] Refresh 30% of seats annually to prevent groupthink

**Cadence**
- [ ] Quarterly sessions, 3–4 hours each
- [ ] Agenda published 3 weeks in advance
- [ ] Pre-read sent 1 week in advance

**Agenda discipline**
- [ ] Open with a company direction share (10 min max) — not a sales pitch
- [ ] Spend 60%+ of time in structured problem discussion, not product demos
- [ ] Assign a dedicated note-taker separate from the facilitator
- [ ] Close with explicit "what we heard" summary and follow-up commitment

**Failure modes to prevent**
- Avoid letting CAB become a feature-request queue — redirect to opportunity framing ("what problem would that solve?")
- Do not promise roadmap commitments in the session
- Do not fill seats only with friendly accounts — friendly bias produces false signal

## 15.2 Lightweight VoC Program

Continuous structured capture from existing operational feeds:

| Source | Signal type | Capture mechanism |
|---|---|---|
| Support tickets | Friction, broken workflows | Weekly tag review; map to OST opportunities |
| Sales call notes | Objections, competitor mentions | CRM field discipline; reviewed monthly |
| Customer success check-ins | Adoption gaps, expansion signals | Structured template; synthesized quarterly |
| NPS/CSAT verbatims | Sentiment, recurring themes | Monthly clustering by PM |

VoC output: tagged opportunity list maintained in OST. Each tag carries source, frequency count, and customer segment. Minimum threshold for OST entry: 3 independent sources for the same underlying problem.

---

# 16. When You Cannot Talk to Users

## 16.1 Decision Tree

```
Can you access real users directly?
├─ Yes → Run standard interview process (sections 3, 13, 14)
└─ No
   ↓
   Why not?
   ├─ Regulated industry / legal restriction → Proxy interviews + behavioral data (16.2a, 16.2b)
   ├─ Enterprise NDA / gated access → Proxy interviews + partner/SME interviews (16.2a, 16.2c)
   └─ No access at all yet → Analog research + behavioral data; plan smallest real-user test (16.2b, 16.2c)
```

## 16.2 Proxy Alternatives

**a. Proxy interviews — talk to those who talk to users daily**

| Proxy | What they provide | Discount for |
|---|---|---|
| Sales | Objections, competitive framing, buying process | Optimism bias; motivated to frame problems as solvable by your product |
| Customer success | Adoption patterns, churn signals, workarounds | Recency bias; hear from loudest or most at-risk accounts |
| Support | Friction points, error patterns, edge cases | Severity bias; hear only from users stuck enough to contact support |

Proxy evidence is weaker than direct user evidence. Label confidence accordingly:
- Direct interview → confidence: high
- Proxy interview → confidence: medium (note which proxy and sample size)

**b. Behavioral data analysis — revealed preference over stated preference**

- Usage logs: where do users drop off, skip steps, or repeat actions?
- Support ticket clustering: what error messages or task names appear most?
- Funnel analysis: where does adoption stall post-onboarding?
- Search / help center queries: what are users trying to figure out on their own?

Behavioral data shows what users do, not why. Combine with at least one proxy interview for context.

**c. Partner/SME interviews and analog research**

- Interview domain experts who have worked inside the target user's role
- Study analogous markets where the same workflow exists and user research is available
- Review published industry surveys, regulatory guidance, and professional association reports

## 16.3 Validation Gate

Proxy evidence is a temporary substitute. Before committing to build:

- [ ] State explicitly which evidence type was used and confidence level
- [ ] Identify the smallest real-user test that can validate the riskiest assumption once access opens (diary study, beta cohort, moderated session with one account)
- [ ] Set a calendar date to revisit with direct evidence — do not let proxy-based assumptions compound

---

# 17. Discovery Theatre — Warning Signs

Continuous discovery (Torres) is a cadence of activity, not a guarantee of learning. A team can run the weekly ritual — interviews scheduled, OST updated, experiments logged — and still be doing discovery theatre: motion without risk reduction. A checklist audit of "did we do the activities" will not catch this; only judgment about what the evidence actually changed will.

**Tells that discovery is theatre, not learning:**

- **Interviews confirm instead of test.** Every interview "validates" the existing solution. If nothing has been disconfirmed in the last 5-10 conversations, the questions are leading or the team is only hearing what it wants to hear (see the Mom Test pattern in section 3.1 — re-audit the actual questions asked, not just the fact that a call happened).
- **The OST has not changed shape in a quarter.** Same opportunities, same solutions, same experiments, just re-dated. A living opportunity tree prunes dead branches and adds new opportunities as evidence accumulates; a static tree is a slide, not a discovery artifact.
- **Experiments have no fail condition, or the fail condition is never invoked.** If every experiment "passes" or ends in "inconclusive, let's keep going," the test card was not actually falsifiable (see section 6 — Fail Condition is not optional).
- **Sample size and selection are never interrogated.** Five interviews with the friendliest accounts is not evidence of demand; it is evidence of goodwill. Ask who was *not* in the room and why.
- **Discovery output arrives after the build decision, as justification.** If discovery artifacts are produced to support a decision that leadership already made, discovery has been repurposed as internal marketing, not evidence-gathering — call this out explicitly rather than dressing up the decision retroactively.
- **The team can state what they did but not what they learned.** "We talked to 12 customers this month" is an activity count. "We learned that procurement, not the end user, kills 60% of our deals at the security-review stage" is a finding. If a debrief only produces the former, discovery is not converting into insight — audit against the Insight Template (section 8.2) and the Definition of Done (section 12).

**What to do about it**: Do not add more process. Pick the single riskiest current assumption, name the specific disconfirming evidence that would kill it, and run one test designed to find that evidence — not to confirm the plan already in motion.

---

**End of file.**
