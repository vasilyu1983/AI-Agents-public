# Agentic AI Orchestration Template  

*Purpose: Design, operate, and evaluate multi-step, tool-using, agentic AI systems.*

Use this when building workflows where AI:

- Breaks down tasks  
- Uses tools/APIs  
- Collaborates across agents  
- Executes steps toward a goal  

---

# 1. Agentic System Overview

Fill this out first.

Goal:
User Segment:
Primary Task(s):
Constraints:
Success Definition:
Failure Modes:
Human Oversight Required (Yes/No):

---

# 2. Agent Definitions

Use one block per agent.

Agent Name:
Role / Responsibility:
Inputs:
Outputs:
Tools/APIs it can call:
Memory Access (None / Short-Term / Long-Term):
Constraints:
Success Criteria:
Failure Conditions:
Escalation Path:

---

# 3. Orchestration Pattern (Choose One)

## Pattern A — Planner → Executors

Use when tasks require decomposition.

Planner responsibilities:
• Break goal into subtasks
• Sequence subtasks
• Assign tasks to agents
• Validate intermediate outputs

Executors:
• Perform one subtask at a time
• Return structured output
• Report blockers or uncertainty

---

## Pattern B — Multi-Agent Collaboration

Use for complex or specialized domains.

Typical roles:

- Researcher → gathers info  
- Synthesizer → summarizes  
- Critic → validates, checks safety  
- Executor → takes action  

Collaboration Rules:
• Turn-taking or parallel
• Critic must approve before execution
• Researcher must cite sources
• Synthesizer must reduce ambiguity

---

## Pattern C — Guardrail Critic (Safety Layer)

Use when hallucination or compliance risk is high.

Critic responsibilities:
• Factuality check
• Policy & safety filter
• Bias/harm analysis
• Compliance with constraints
• Confidence scoring

Critic Output:
• Approve / Reject / Request More Info

---

# 4. Tool & API Access Template

Tool Name:
Purpose:
Input Format:
Output Format:
Rate Limits:
Safety Constraints:
Examples of Valid Calls:
Handling of Failures:

---

# 5. Memory & State Management

Choose one:

- **Stateless** (best for speed + reliability)  
- **Short-term memory** (store last X steps)  
- **Long-term memory** (vector store, logs)  

Template:
Memory Type:
What gets stored:
Retention:
Access rules:
Privacy constraints:

---

# 6. Execution Flow Template

This is the “source of truth” for orchestration.

Receive user request
Validate inputs
Planner generates task plan
Executors take tasks sequentially or in parallel
Critic validates each output if enabled
If failure → fallback / retry / escalate
Return final result with confidence score
Log to monitoring systems

---

# 7. Safety Guardrails Template

Input Validation:
• Allowed domains:
• Forbidden domains:
• PII handling:
Output Filters:
• Hallucination checks:
• Factuality grounding:
• Policy filters:
Action Safety:
• Restrictions on external tool use:
• Required human approval points:
Error Handling:
• Retries:
• Timeouts:
• Escalations:

---

# 8. Evaluation Metrics (Agentic-Specific)

Task Success Rate:
Average Steps per Task:
Unnecessary Step Rate:
Tool Use Success Rate:
Fallback Activation Rate:
Safety Violations:
Latency per Step:
Cost per Completion:
Human Override Rate:

Monitoring Frequency:  

- Daily for high-volume  
- Weekly for moderate volume  

---

# 9. Example (Editable)

Goal:
Automate weekly sales forecasting for revenue ops

Constraints:
Must be grounded in CRM data; zero hallucinations

Planner:
• Break forecasting into: data extraction → cleansing → model selection →
prediction → summary
• Assign subtasks to Researcher and Modeler

Agents:
Researcher:
Tools: CRM API, SQL connector
Output: cleaned dataset

Modeler:
Tools: forecasting model API
Output: predictions w/ confidence intervals

Critic:
Tasks: data integrity check, bias detection, grounding verification
Failure Mode: missing fields or abnormal variances

Executor:
Output: final forecast summary + recommended actions

Success Criteria:
• Forecast generated with <5% error
• End-to-end latency < 8s
• No hallucinated values

---

# 10. Orchestration Checklist

- [ ] Clear goal + constraints  
- [ ] Roles defined for each agent  
- [ ] Planner logic documented  
- [ ] Tools/APIs validated  
- [ ] Critic layer added where needed  
- [ ] Safety filters active  
- [ ] Memory strategy chosen  
- [ ] Monitoring metrics defined  
- [ ] Failures + escalations documented  
- [ ] Ready for prototype run  

---

# 11. Definition of Done (Agentic System)

An agentic system is **ready** when:

- [ ] Task plan executes end-to-end  
- [ ] Agents use tools reliably  
- [ ] Safety layer catches invalid outputs  
- [ ] Metrics exceed thresholds  
- [ ] Costs acceptable  
- [ ] Human oversight path validated  
- [ ] Logs + monitoring operational  
- [ ] Behavior is deterministic & repeatable  

---

**End of file.**
