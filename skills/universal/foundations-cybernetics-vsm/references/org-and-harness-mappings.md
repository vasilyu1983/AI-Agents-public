# Org and Harness Mappings

Read this when mapping the VSM onto a real agent harness, onto Team Topologies team types, or when someone asks how much human oversight an agent fleet needs. Every table here is a **practitioner heuristic**: Beer did not define these mappings. Use them to find the failure signal fast, then test it with the [response coverage audit](response-coverage-audit.md).

## Contents

- [Agent harness to VSM](#agent-harness-to-vsm)
- [Team Topologies to VSM](#team-topologies-to-vsm)
- [Evidence pack for effective human oversight](#evidence-pack-for-effective-human-oversight)
- [POSIWID check](#posiwid-check)
- [When not to prescribe S3*](#when-not-to-prescribe-s3)

## Agent Harness to VSM

| VSM function | Typical harness mechanism | Failure signal |
| --- | --- | --- |
| S1 operations | Subagents or worker agents with a bounded task and tool set | Workers wait on the orchestrator for every step |
| S2 coordination | Task board, claim locks, file ownership, shared scratch conventions | Two workers edit the same file or redo the same task |
| S3 control | Orchestrator budgets, turn caps, tool allow-lists, task allocation | Orchestrator re-does or re-reviews every worker result |
| S3* audit | Evals, sampled trace replay, spot-checks outside the normal report path | Only worker self-reports reach the orchestrator |
| S4 intelligence | Research or scout agent; model, API and regulation watch | Harness breaks on a model or API change nobody tracked |
| S5 identity | Human policy; `AGENTS.md`/`CLAUDE.md`; disallowed tools; constitutional rules | Conflicting instructions resolved ad hoc per run |
| Algedonic channel | Pre-tool-use blocking hooks, kill switch, direct page to a human | A destructive action is only noticed in the final summary |
| S3 saturation proxy | Orchestrator context-fill rate and queue of unreviewed results | Escalations pile up; the orchestrator summarises instead of deciding |

Overloaded-orchestrator fix order: add S2 (ownership, locks) so fewer conflicts reach S3; attenuate what reaches S3 (exception-only reports, structured summaries); move routine review to sampled S3*; only then add orchestrator capacity.

## Team Topologies to VSM

Team types and interaction modes are from Skelton & Pais, *Team Topologies* (IT Revolution, 2019). The VSM column is a heuristic crosswalk, not part of either source.

| Team Topologies element | VSM reading | What to check |
| --- | --- | --- |
| Stream-aligned team | S1 unit with its own environment | Can it ship without hand-offs? If not, S1 autonomy is missing |
| Platform team | S1 unit whose product amplifies other S1 units' variety | Are consumer request classes covered by self-service, or does every request queue on the platform team? |
| Enabling team | Temporary variety amplifier; often S4-adjacent (new capability) | Does it exit once capability transfers, or become a permanent dependency? |
| Complicated-subsystem team | S1 unit that attenuates specialist variety for others | Is the interface narrow enough that consumers do not need the specialism? |
| Interaction modes (collaboration, X-as-a-service, facilitation) | S2 coordination protocols | Is each team pair's mode explicit and time-boxed where it is collaboration? |
| Cognitive load | Variety a team must absorb | Split or attenuate when a team cannot recognise and respond to its request classes |

## Evidence Pack for Effective Human Oversight

"How many reviewers do we need for N agents?" has no count answer. Telukunta, Lilis & Baron (2026, arXiv:2608.10153, preprint, grade C) frame oversight as `V_human × G ≥ V_agents` and state that escalation SLA adherence, override drill outcomes and approval-gate quality must themselves be measured. Treat the inequality as framing; the evidence below is what shows oversight works:

| Evidence | What it shows | Where it comes from |
| --- | --- | --- |
| Coverage matrix | Each outcome-relevant agent behaviour class maps to a detecting signal and an authorised intervention | [response-coverage-audit.md](response-coverage-audit.md) |
| Escalation SLA adherence | Escalations reach an authorised human inside the consequence deadline, at peak load | Escalation logs |
| Override / kill-switch drill outcomes | Interventions actually stop or reverse the behaviour in time | Drill records |
| Approval-gate quality | Reviewers catch seeded or sampled defects, not only approve | Sampled review audits, seeded-defect tests |
| Triage and summarisation quality | Amplifiers (triage, summaries, tiering) do not drop the signal that mattered | Replay of missed incidents |

Staffing follows the evidence: add reviewers only where SLA adherence or gate quality fails after triage and tiering are in place.

## POSIWID Check

Beer: "the purpose of a system is what it does" (Beer 2002, *Kybernetes* 31(2), 209–219). Use it to test S5 claims:

1. Write down the stated purpose or identity (mission, `AGENTS.md` policy).
2. List what the system reliably produces, including side effects (what gets rewarded, what gets escalated, what gets shipped).
3. Where they differ, the observed behaviour is the operative purpose. Either change the mechanisms that produce it or restate the identity honestly. A values statement that never changes a decision is not S5.

## When Not to Prescribe S3*

Practitioner heuristic with no cited source; check it against your context. In a small team where everyone already sees the raw work (roughly a single team, no management layer), a formal sporadic-audit channel adds overhead and can read as distrust without adding information. Prefer shared raw artefacts (open dashboards, shared tickets, pair review). Introduce S3* when a reporting layer first sits between the people who decide and the work itself, or when an incident shows reports and reality diverged.
