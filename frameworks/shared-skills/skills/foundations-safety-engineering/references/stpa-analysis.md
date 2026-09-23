# STPA analysis

Method basis: Leveson and Thomas, STPA Handbook (2018), chapter 2. The analysis below applies its control-action categories; software examples are synthetic applications.

A loss is an unacceptable outcome for stakeholders. A hazard is a system condition that, in an adverse environment, can produce a loss. Define each before proposing mitigations.

Represent controllers, actions, controlled processes, and feedback. Examine what the controller believes about state, action completion, operating mode, and environmental conditions. A diagram shows possible communication; it does not show that feedback arrives accurately or that commands execute.

For each action assess:

| Category | Question |
|---|---|
| Omission | In what context does failing to provide the action lead to a hazard? |
| Provision | In what context does providing the action lead to a hazard? |
| Timing/order | When does early, late, or out-of-order provision become unsafe? |
| Duration | For continuous actions, when does persisting too long or stopping too soon become unsafe? |

Mark duration not applicable for a discrete command rather than inventing persistence. Examine related state transitions separately. A UCA names controller, action, unsafe category, context, and hazard. Derive a constraint that addresses that context; avoid vague “ensure safety” requirements.

Explore scenarios along the decision and execution paths: inaccurate feedback, mismatched process models, conflicting controllers, unreceived commands, unsafe actuator behavior, and missing coordination. Include scenarios where every component follows its local specification. Preserve these as scenario hypotheses until evidence establishes occurrence or control effectiveness.
