# Assumption Test Template  

*Purpose: Validate the riskiest parts of an idea before investing in delivery.*

Use this template to design structured, measurable tests for value, usability, feasibility, and viability.

---

# 1. Assumption Categories

**Value Risk** – Do customers care? Will they use it?  
**Usability Risk** – Can they figure it out on first try?  
**Feasibility Risk** – Can we build it? Does tech support it?  
**Viability Risk** – Should we build it? Legal, cost, ops constraints.

---

# 2. Assumption Mapping Template

Idea / Hypothesis:
User Segment:
Opportunity (Problem):

Assumptions:

Value:
Usability:
Feasibility:
Viability:
Riskiest Assumption:
Why it’s riskiest:
Evidence we have:
Evidence missing:

---

# 3. Test Card Template

Test Name:

Purpose:
Assumption Type: Value / Usability / Feasibility / Viability

Hypothesis:
We believe that…

Test Method:
(Choose one: concierge / fake door / prototype / usability task / tech spike / pricing test / legal review / shadow mode)

Procedure:
Step 1:
Step 2:
Step 3:

Success Criteria:
Fail Condition:

Sample Size:
Segment:
Duration:

Owner:
Status:
Next Steps:

---

# 4. Experiment Types (Operational)

### **Value Tests**

- Fake door  
- Landing page with CTA  
- Pre-selling / pre-pay  
- Pitch test  
- Concierge / manual fulfillment  
- Price sensitivity test  

### **Usability Tests**

- Prototype task walkthrough  
- Think-aloud usability test  
- Unmoderated task completion  
- Success score (completion %)  

### **Feasibility Tests**

- Tech spike  
- Latency benchmark  
- Integration stub  
- Load test  

### **Viability Tests**

- Legal/privacy review  
- Cost modeling  
- Brand review  
- Operational capacity review  

---

# 5. Prioritizing Tests

Run assumptions in this order:

1. **Value** – If they don’t care, nothing else matters  
2. **Usability** – If they can’t use it, it won’t succeed  
3. **Feasibility** – Validate core tech constraints  
4. **Viability** – Ensure compliance + business fit  

Checklist:

- [ ] One test per assumption  
- [ ] Batch small tests first  
- [ ] Parallelize where possible  

---

# 6. Example (Editable)

Idea: Guided Setup for New Users
Segment: SMB admins
Opportunity: “New users get stuck on first configuration.”

Assumptions:

Value: They want guidance (high risk)
Usability: They can follow steps
Feasibility: Can be built using existing UI components
Viability: No legal concerns
Riskiest = Value

Test Name: Fake Door CTA
Method: Value
Hypothesis:
We believe 20%+ of new users will click "Start Guided Setup".

Procedure:

Add CTA to onboarding screen
Track clicks for 7 days
Show “Coming soon” modal
Success Criteria: ≥20% click
Fail Condition: <10% click
Owner: PM
Next Step:
If pass → usability test
If fail → revisit opportunity

---

# 7. Test Design Checklist

- [ ] Test isolates ONE assumption  
- [ ] Has measurable success criteria  
- [ ] Has clear fail condition  
- [ ] Sample size defined  
- [ ] Time-bound  
- [ ] No coding unless required  
- [ ] Covers highest-risk assumption first  
- [ ] Results tied back to Opportunity Solution Tree  

---

# 8. Definition of Done (Assumption Testing)

A test is **complete** when:

- [ ] One assumption validated or invalidated  
- [ ] Clear evidence collected  
- [ ] Decision recorded (pivot / persevere / redesign)  
- [ ] OST updated  
- [ ] Next test queued  

---

**End of file.**
