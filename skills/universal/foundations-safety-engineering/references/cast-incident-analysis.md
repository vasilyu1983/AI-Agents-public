# CAST: incident analysis beyond root cause

Source: Leveson, *CAST Handbook: How to Learn More from Incidents and Accidents* (2019, 148 pp, MIT PSAS mirror). CAST stands for Causal Analysis based on System Theory. It uses the STAMP causality model: a loss happens because the safety control structure failed to enforce a safety constraint. A broken part or a bad actor is not the whole explanation.

The handbook calls CAST "an analysis method, not an investigation technique". Run it alongside the investigation, because it tells you which questions to ask.

## Why not "root cause"

The handbook lists common traps in accident analysis:

- **Root-cause seduction:** stopping at one convenient cause.
- **Hindsight bias:** "should have" judged with knowledge the people involved did not have at the time.
- **Superficial treatment of human error.**
- **A focus on blame.**
- **Chain-of-events models:** these usually stop at an operator close to the event.

CAST aims instead to:

- include all causal factors;
- reduce hindsight bias;
- take a systems view of human behaviour;
- explain "why" and "how", not "who".

## The five parts (iterative, not linear)

1. **Assemble basic information.**
   - Define the system boundary.
   - Name the loss and the hazardous state.
   - Derive the system-level safety constraints that were violated.
   - Describe the events without conclusions or blame.
   - Analyze the physical or technical loss: controls present, controls missing, and contextual factors.
   - Record open questions.
2. **Model the safety control structure** that existed for this hazard. Show who controlled what, through which actions, and with what feedback.
3. **Analyze each component in the loss,** starting at the bottom of the structure and working up. For every controller, human or automated, record:
   - its responsibilities related to the loss;
   - its contribution: actions taken, actions not taken, decisions;
   - flaws in its process or mental model;
   - the contextual factors that explain why the action made sense to it at the time.
4. **Identify flaws in the control structure as a whole.** Look for:
   - communication and coordination gaps;
   - a missing or unused safety information system;
   - safety culture;
   - changes and dynamics over time, including drift toward states of higher risk;
   - economic and environmental pressures.
5. **Create an improvement program.**
   - Write recommendations against the control structure, not against individuals.
   - The handbook's three requirements for follow-up: assign responsibility for implementing each recommendation, check that it was implemented, and set up feedback to test whether it worked.

At each step, generate questions. The analysis is done when every question is answered, or recorded as unanswerable.

## Applying it to software and AI-agent incidents

- An agent that took a harmful action is a controller with a flawed process model. Ask what context, tool output or instruction made the action look correct. "The model hallucinated" is a description, not an explanation.
- Include the humans who approved the action, the owner who set its permissions, and the team that shipped the prompt or tool change. The handbook expects flaws to appear at every level of the control structure, not only the lowest.
- Many recommendations is normal. Prioritize them; do not drop them. The handbook explicitly rejects cutting recommendations to keep the list short.
- Feed each confirmed flaw back into the forward STPA as a new loss scenario, and into the [traceability worksheet](../assets/templates/safety-traceability.md) as a constraint with a test.

## Safety-II lens

Pair CAST with a work-as-done question: how did this same workflow succeed on the days it did not fail? Adaptations that usually succeed can explain the day they did not (see [Safety-II, resilience and STAMP](safety-ii-and-stamp.md)).

**When not to use.** A fault with one cause, fully explained by a single defect and with no human or organizational controller involved, needs an ordinary postmortem. Use CAST when the incident involves several controllers, automation plus humans, repeated near-misses, or a "worked as designed" explanation.
