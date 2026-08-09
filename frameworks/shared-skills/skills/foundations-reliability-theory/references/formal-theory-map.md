# Reliability Theory Formal Theory Map

Use this map when a task needs the math behind availability, failure modeling, redundancy, SLOs, or launch risk.

## Theory Spine

| Construct | What It Formalizes | Operational Test |
|-----------|--------------------|------------------|
| Reliability R(t) | Probability a non-repairable item survives to time t | Is the mission time and failure definition explicit? |
| Survival / CDF | Relationship between survival and cumulative failure | Are censored observations handled correctly? |
| Hazard h(t) | Instantaneous failure rate conditional on survival | Is failure rate constant, increasing, or decreasing? |
| Repairability | Whether the system can return to service after failure | Are MTTR and maintenance policies part of the model? |
| Availability A | Fraction/probability of time in usable service | Does the calculation include detection and restore time? |
| Series system | Any component failure fails the system | Are component reliabilities multiplied, not averaged? |
| Parallel system | Redundant paths can tolerate some failures | Are independence and switchover coverage valid? |
| Fault tree | Top event decomposed into Boolean causes | Are common-cause and dependency events represented? |
| Weibull model | Flexible lifetime distribution with shape beta and scale eta | Are sample size, censoring, and confidence intervals adequate? |

## Primitive Dependency Map

| Primitive | Depends On | Boundary |
|-----------|------------|----------|
| MTBF/MTTR | Stable failure and repair definitions | MTBF is not an uptime guarantee |
| Availability | Repairable-system assumptions | A = MTBF / (MTBF + MTTR) assumes steady-state exponential behavior |
| Hazard functions | Lifetime data and censoring model | Constant hazard is only one special case |
| Bathtub curve | Lifecycle phases | Diagnose with data; do not assume phase |
| FTA | Boolean structure and independence assumptions | Common causes break simple gate math |
| FMEA | Enumerated modes and scoring scale | RPN is ordinal, not a precise risk value |
| Redundancy math | Independence, coverage, repair policy | Redundancy can reduce reliability if failover is weak |
| Error budgets | Stable SLI/SLO definitions | Budget math is only as valid as the measurement |
| Allocation | System target and subsystem topology | Targets must match architecture and ownership |

## Evidence Standards

- Availability claim: state observation window, good/bad event definition, MTBF, MTTR, and topology.
- Redundancy claim: state independence, common-cause factor, coverage probability, and failover test evidence.
- Weibull claim: state sample size, censoring, beta/eta confidence intervals, and goodness-of-fit.
- FMEA claim: list high-severity modes separately from RPN rank.
- Fault-tree claim: show top event, gates, basic events, and common-cause assumptions.
- SLO claim: define SLI, threshold, window, burn-rate alert, and excluded events.

## Reliability Arithmetic Reminders

- Series reliability: R_system = product(R_i).
- Parallel reliability for independent components: R_system = 1 - product(1 - R_i).
- Steady-state availability for exponential repairable system: A = MTBF / (MTBF + MTTR).
- Downtime budget: allowed bad time = (1 - SLO) * window.
- Weibull hazard: beta < 1 decreasing, beta = 1 constant, beta > 1 increasing.

## Source Anchors

- Lewis, O'Connor/Kleyner, Birolini: reliability math, system composition, FTA/FMEA, allocation.
- Weibull: lifetime distribution and shape interpretation.
- IEC 60812: FMEA/FMECA process.
- IEC 61025 and NRC/NASA fault-tree handbooks: FTA structure and gates.
- Google SRE books: SLOs, error budgets, burn-rate alerting.
- NIST Engineering Statistics Handbook: reliability statistics and lifetime distributions.
