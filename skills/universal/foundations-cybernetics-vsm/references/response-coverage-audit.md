# Response Coverage Audit

This artifact diagnoses observed control gaps; it is not a numerical proof of organizational viability. Start with a recurring failure signal, system boundary and recursion level, then map functions/channels rather than reporting-line titles.

## Fillable record

- Failure signal and consequence to prevent:
- System-in-focus / external environment / recursion level:
- S1 units and bounded autonomy:
- S2 coordination / S3 authority / S3* independent evidence path:
- S4 sensing and S3 interface / S5 conflict resolution:
- Observation window and evidence provenance:

| Outcome-relevant disturbance | Distinguishing signal | Effective response and authorized owner | Detection + response deadline | Shared dependencies / coupled failure | Replay evidence and outcome | Gap / next intervention |
|---|---|---|---|---|---|---|
| [class requiring distinct response] | [signal, freshness, false negatives] | [action, authority, resource feasibility] | [consequence deadline, measured latency] | [sensor/tool/person failure overlap] | [case/time, observed result; unknown if untested] | [smallest change, owner, acceptance] |

Do not score coverage by subtracting counts of labels, alerts, people or knobs. Under Ashby's finite-table assumptions and logarithmic measure, residual outcome variety is bounded **below** by disturbance minus regulator variety; the bound alone is not an intervention-performance guarantee. See [Ashby §11/6–11/7](https://ashby.info/Ashby-Introduction-to-Cybernetics.pdf).

## Completed synthetic diagnosis

Failure: shared-queue work is duplicated and novel executor failures wait too long for containment. Boundary: one agent service; S1 research/drafting executors; S2 queue claim protocol; S3 service operator; S3* replay reviewer; S4 failure-pattern review; S5 human authority for scope/constraint conflicts.

| Disturbance | Signal | Response / owner | Deadline | Coupling | Synthetic replay | Intervention |
|---|---|---|---|---|---|---|
| Duplicate claim | Two live claims for one work id | Reject second claim / S2 queue service | Before second external effect | Queue outage also hides claim state | Test claim collision: second executor rejected | Preserve atomic claim and effect idempotency |
| Novel executor failure | Unknown failure code and bounded diagnostic context | Pause affected work / authorized S3 on-call | 5 min containment window | Primary dashboard and executor share failed host | Initial replay: dashboard unavailable, no page; containment misses deadline | Independent heartbeat → bounded-context page; retest with dashboard down |
| Unsafe external action | Tool-boundary policy violation | Reject action / deterministic enforcement; notify appropriate authority | Before effect | Policy service timeout | Replay: fail-closed rejection, escalation received | Keep rejection; verify escalation receipt independently |
| Coupled queue + dashboard failure | Independent heartbeat + queue health probe | Stop new admissions / S3 operator | 2 min before backlog exhausts capacity | Shared DNS can defeat both probes | Not yet replayed: coverage UNKNOWN | Add independent route and coupled-failure drill |

Follow-up acceptance: replay the previously missed novel/coupled cases; record observed detection, receipt and authorized containment times. A working page without an effective authorized action remains a gap. Deploy interval is contextual evidence; consequence deadlines and disturbance dynamics determine whether response arrives in time. Review alert flood, acknowledgement fallback and whether punitive incentives suppress the bypass channel. This example is synthetic; replace it with provenance-bearing observations.
