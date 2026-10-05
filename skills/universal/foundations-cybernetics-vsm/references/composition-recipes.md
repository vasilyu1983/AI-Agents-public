# Composition Recipes

Read this when a diagnosis needs several primitives in sequence. Each recipe lists the stack, the checks, and the output. Ashby checks in every recipe are coverage checks (disturbance class → distinguishing signal → authorised effective response → deadline), never count subtraction; see [response-coverage-audit.md](response-coverage-audit.md).

## Contents

- [Agent-Team Topology Audit](#agent-team-topology-audit)
- [Organisational Design for a Startup](#organisational-design-for-a-startup)
- [Incident Escalation as Algedonic Channel](#incident-escalation-as-algedonic-channel)
- [Scaling a Platform Team](#scaling-a-platform-team)

## Agent-Team Topology Audit

**Goal:** find where an agent hierarchy will fail.

1. S1 (#3): list worker agents with scope and autonomy level. Map harness parts to VSM with [org-and-harness-mappings.md](org-and-harness-mappings.md#agent-harness-to-vsm).
2. S2 (#4): any shared resource (files, tools, rate limits) without an explicit coordination protocol is a thrashing risk.
3. S3 (#5): the orchestrator sets bounded resource and operational policy inside S5; it does not micro-execute.
4. Ashby (#2): for each outcome-relevant disturbance class, verify the orchestrator can detect the distinction and select an effective response under real timing, authority and resource limits. Conant–Ashby: the regulator's model must represent the distinctions needed to choose a response.
5. Variety engineering (#10): if the orchestrator is overwhelmed, attenuate (summaries, exception routing) before adding capacity.
6. Algedonic (#11): critical failures bypass normal reporting to a human or S5.

**Output:** viability gap table; disturbance-to-observation-to-response mapping with uncovered distinctions; missing interfaces; one structural change per gap. Counts of alerts, agents, labels or dashboard states are not proof of requisite variety.

**Human oversight of a fleet:** Telukunta et al. (2026, arXiv:2608.10153, preprint) frame it as `V_human × G ≥ V_agents`. Do not operationalise the terms as raw counts or use the inequality as a deployment proof. Use the [oversight evidence pack](org-and-harness-mappings.md#evidence-pack-for-effective-human-oversight).

## Organisational Design for a Startup

**Goal:** a lightweight structure that scales without command bottlenecks.

1. Recursion (#9): name the two or three levels actually needed (company → product area → squad).
2. S1 (#3): autonomous squad boundaries with clear scope.
3. S3* (#6): a ground-truth mechanism for founders as layers appear (see [when not to prescribe S3*](org-and-harness-mappings.md#when-not-to-prescribe-s3)).
4. S4 (#7): who scans the environment and translates it into strategy.
5. S5 (#8): a one-page identity document; test it with the [POSIWID check](org-and-harness-mappings.md#posiwid-check).
6. Feedback (#1): at least one balancing loop per key variable (burn, retention, lead time).

**Check:** each of S1–S5 is present and named; each material disturbance has a sensing and response path at the right level. Set S3* and S4→S5 rhythms from risk and change rate, then test them.

**Worked example:** four product squads (S1), shared-roadmap coordination (S2), resource policy and audit (S3/S3*), market scanning (S4), mission constraints (S5). Material disturbances: a cross-squad dependency conflict, a production incident, a market change. If the market signal reaches S4 but no path can change portfolio allocation, that distinction lacks an effective response; add the S4→S5 decision path or delegate bounded authority. Counting surfaces or levers does not establish the gap.

**Output:** role-to-system map; disturbance-response coverage table; missing systems; one structural change per gap.

## Incident Escalation as Algedonic Channel

**Goal:** production crises reach decision authority fast, bypassing ticket queues.

1. Algedonic (#11): define the trigger as deviation from the service's own baseline, sized from the consequence deadline. Error-budget burn-rate alerting is one sourced pattern; see [reliability-theory error budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md).
2. S5 (#8): who holds authority to close the incident or accept risk.
3. Feedback (#1): the triggered loop is alert → diagnosis → mitigation/rollback → verified recovery.
4. S3* (#6): the post-incident review compares what S3 saw (dashboards, alerts) with the real failure timeline.
5. Variety engineering (#10): only deviation-from-normal reaches on-call.

**Checks:** compare detection-plus-response latency with the consequence deadline and how fast the disturbance evolves. Frequent deploys against a slow response are an investigation signal, not an automatic violation. Any resource shared by two or more S1 units (queue, database, gateway) without an S2 protocol is a high-severity gap. Test the trigger at a risk-based interval and after channel or authority changes.

**Output:** loop diagram (type, goal variable, latency, active/missing); latency-vs-deadline table; shared resources lacking S2 protocols; one structural change per gap.

## Scaling a Platform Team

**Goal:** stop the platform team becoming the bottleneck for its consumers.

1. Ashby (#2): map consumer request classes to signals and effective platform responses. Use the [Team Topologies crosswalk](org-and-harness-mappings.md#team-topologies-to-vsm).
2. Variety engineering (#10): amplify supply (self-service APIs, docs, inner source); attenuate demand (standard interfaces, request templates).
3. S2 (#4): coordination between consuming teams so their requests do not conflict.
4. S3 (#5): platform-wide policy; platform sub-teams are S1 units with autonomy inside it.
5. Feedback (#1): lead time and consumer outcomes as balancing-loop goal variables. Diagnose stagnant lead time before assigning it to S2 or S3.

**Output:** request-class-to-response coverage table; self-service expansion plan; S3 policy boundary; missing coordination protocols.
