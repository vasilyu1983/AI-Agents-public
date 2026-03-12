# A3 Debrief Template  

*Purpose: Quickly and systematically analyze issues, decisions, or failures to improve future execution.*

Use after:

- Incidents  
- Failed experiments  
- Missed deadlines  
- Project pivots  
- Launches  

Fits on one page.  

---

# 1. A3 Template (Copy/Paste)

Title:

Date:
Owner:
Team:

Background
• What happened?
• Why are we analyzing this?
Current Situation
• Facts only (no opinions)
• Impact on customers / team / business
Goal / Expected Outcome
• What we intended to happen
• Target metrics if relevant
Root Cause Analysis
• Primary root cause:
• Contributing factors:
• Evidence:
Countermeasures
• What actions will prevent recurrence?
• Owners + deadlines
Follow-Up Plan
• What to inspect?
• How often?
• Success indicators
Lessons Learned
• What did we learn?
• What will we do differently next time?

---

# 2. Root Cause Patterns

Use these patterns to identify root causes quickly.

## Pattern A — “5 Whys”

Why did this happen?
Why did that happen?
Why did that happen?
Why did that happen?
Root cause:

## Pattern B — Categorize by Type

- **People:** Misaligned expectations, unclear roles  
- **Process:** Missing steps, unclear handoff  
- **Tools:** Bugs, lack of instrumentation  
- **Communication:** No shared understanding  
- **Assumptions:** Invalidated or untested  

## Pattern C — Evidence Check

A valid root cause MUST have:

- [ ] Evidence  
- [ ] Clear link to the outcome  
- [ ] Something the team can influence  

---

# 3. Countermeasure Template

Action:
Owner:
Deadline:
Expected Impact:
Dependencies:
Risks:
Success Criteria:

---

# 4. Example (Editable)

Title: Onboarding Drop-Off Incident

Date: April 2
Owner: PM – Activation
Team: Growth + Design

Background
Activation dropped from 32% → 20% after onboarding change.
Current Situation
• Step 2 error rate increased 3x
• Affected 40% of new users
• Support tickets increased by 18%
Goal
Keep activation stable while shipping redesign.
Root Cause Analysis
Primary Root Cause:
• API response delay causing form timeout
Evidence:
• Logs show 1.8s → 8.4s latency spike
• Engineering confirmed regression
Contributing Factors:
• Missing alert for API latency
• No fallback message in UI
Countermeasures
• Fix API regression (Owner: Backend Lead, Due: Apr 3)
• Add API latency alert (Owner: SRE, Due: Apr 4)
• Add UI fallback state (Owner: Design, Due: Apr 7)
Follow-Up Plan
• Monitor latency daily for 2 weeks
• Track activation trend weekly
• Review after 30 days
Lessons Learned
• Instrumentation required before rollout
• Must test onboarding end-to-end with production data

---

# 5. Debrief Facilitation Script

Use this structure in team debrief meetings:

“Let’s start with what we intended to happen.”
“Here’s what actually happened.”
“Let’s identify the primary root cause — evidence only.”
“Which countermeasures will prevent this next time?”
“Who owns what, and by when?”
“Let’s agree on how we’ll follow up.”

---

# 6. Quality Checklist

- [ ] Fits on a single page  
- [ ] Uses facts, not opinions  
- [ ] Contains a single clear root cause  
- [ ] Countermeasures address root cause  
- [ ] Owners + dates assigned  
- [ ] Follow-up clearly defined  
- [ ] Lessons captured for future cycles  

---

# 7. Definition of Done (A3 Debrief)

An A3 is **complete** when:

- [ ] Team agrees on root cause  
- [ ] Countermeasures prevent recurrence  
- [ ] Follow-up plan is scheduled  
- [ ] Insights feed back into roadmap or process  

---

**End of file.**
