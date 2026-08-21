# Reliability Theory Patterns, Scenarios, and Traps

Use this reference before accepting availability math, redundancy claims, FMEA priorities, Weibull fits, or SLO release policies.

## Core Patterns

| Pattern | Use When | Watch For |
|---------|----------|-----------|
| Failure definition first | Anyone reports MTBF, uptime, or incident rate | Different teams may count failures differently |
| Topology composition | Multiple components form a service | Series vs. parallel math and hidden dependencies |
| Common-cause audit | Redundancy is proposed | Same region, code, operator, power, vendor, or config |
| Coverage modeling | Standby/failover is part of reliability | Failover may fail or be too slow |
| Severity override | FMEA ranks by RPN | Catastrophic low-frequency modes must still be reviewed |
| Censoring-aware fit | Lifetime data has devices still alive | Naive averages bias reliability estimates |

## Scenarios

### Service SLO From Architecture

1. Define the SLI and "good event" precisely.
2. Compute availability for each required component.
3. Compose series dependencies multiplicatively.
4. Model redundant paths with common-cause correction.
5. Compare architecture-derived availability to observed incident data.
6. Set burn-rate alerts on multiple windows.

### Redundancy Proposal Review

1. Identify whether the topology is active-active, active-standby, or k-of-n.
2. Check shared failure domains.
3. Model failover coverage probability.
4. Test switchover under realistic load and dependency failure.
5. Reject "more replicas = more nines" unless common-cause and coverage are quantified.

### Launch FMEA

1. Enumerate failure modes bottom-up.
2. Score severity, occurrence, and detection consistently.
3. Pull out all high-severity items before sorting by RPN.
4. Build a fault tree for top events and single points of failure.
5. Re-score residual risk after mitigations.

### Weibull Maintenance Planning

1. Separate complete failures from right-censored observations.
2. Fit Weibull with confidence intervals.
3. Interpret beta only if sample size supports it.
4. Use B10 or chosen percentile for maintenance planning, not just mean life.
5. Refit after design, process, or operating-environment changes.

## Anti-Patterns

| Anti-Pattern | Why It Fails | Corrective Move |
|--------------|--------------|-----------------|
| MTBF as guarantee | MTBF is an expectation under assumptions, not a promise that the next failure is far away | Report distribution, observation window, and uncertainty |
| Adding nines | Availability percentages do not add | Compose through topology and downtime budgets |
| Parallel independence assumption | Shared dependencies cause correlated failure | Model common-cause factor and failure domains |
| FMEA RPN absolutism | RPN scales are ordinal and can hide catastrophic modes | Review high severity separately |
| Weibull from tiny sample | Shape and scale estimates are unstable | Report uncertainty or wait for more data |
| Error budget as permission to break | Budget is a control mechanism, not an excuse | Tie burn to release gates and incident response |
| Redundancy without exercise | Untested failover may not work when needed | Run scheduled failover tests and include failures in MTTR |

## Known Traps

- Observation-window trap: recent uptime can look perfect while long-tail failures remain unmeasured.
- Repair-time trap: MTTR often excludes detection, decision, rollback, and verification time.
- Independence trap: identical software builds fail together.
- Allocation trap: subsystem targets are assigned uniformly despite unequal topology criticality.
- SLO drift trap: changing SLI definitions invalidates historical error budget comparisons.
- MIL-HDBK trap: handbook tables may be conservative or stale for modern components.
- Config-propagation trap: a configuration or control-plane update reaches every replica, so replication multiplies its blast radius instead of dividing it. No parallel-path formula models this; enumerate it as a basic event in the fault tree. Both the AWS DynamoDB DNS-automation failure (19–20 Oct 2025) and the Cloudflare Bot Management feature-file failure (18 Nov 2025) took this shape — in each case the components stayed healthy and the propagated artefact was the fault.
- Backlog-tail trap: MTTR measured to root-cause fix understates recovery. After the Oct 2025 DynamoDB event the service itself recovered in under three hours while dependent services drained backlogs for most of the following day. Measure MTTR to dependent-service recovery, not to the fix.
- Remembered-failure-mode trap: redundancy encodes the last failure you experienced. us-east-1 has failed in three structurally different ways since 2021; designs hardened against one mode were still taken out by the next. Ask which mode your redundancy assumes.
- Single-run success rate as reliability metric for agent systems — trap: a single pass/fail ignores consistency variance across repeated runs, sensitivity to semantically equivalent task variants, and failure-type-specific fault tolerance. Fix: use pass^k across ≥10 runs; measure perturbation degradation at ε=0.1–0.3; inject fault types (timeout, rate limit, schema drift) at controlled intensity and measure per-type impact. (ReliabilityBench, Gupta 2026, arXiv:2601.06112.)

## Compact Review Sequence

1. Define failure and repair events.
2. Identify repairable vs. non-repairable model.
3. Draw system topology.
4. Compose reliability/availability through topology.
5. Check common-cause and coverage assumptions.
6. Review high-severity failure modes independently of RPN.
7. Validate lifetime distribution and censoring.
8. Convert SLO to error budget and burn-rate alerts.
9. State uncertainty and what data would change the decision.
