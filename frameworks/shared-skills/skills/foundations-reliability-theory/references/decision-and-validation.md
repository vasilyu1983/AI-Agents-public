# Reliability estimate and evidence worksheet

## Intake and output

Name the service event/SLI, observation window, mission time, repairability, uptime/downtime definitions, failure exposure, censoring mechanism, topology and common causes. Deliver point estimate, uncertainty method, dependence assumptions, high-severity modes, mitigations, verification and unknowns. Reliability analysis supports evidence; it does not certify safety or compliance.

## Means and sparse evidence

For alternating renewal cycles with finite mean uptime U and downtime D, long-run availability=E[U]/(E[U]+E[D]); exponentials are not required. Mean uptime100h and downtime samples1,9h give 100/105≈.952381. Report downtime tails separately.

With n independent Bernoulli trials all successful, a one-sided 95% exact lower success bound is .05^(1/n). Ten successes give≈.741, not proof of .995. About598 successes are necessary to reach .995 under that model; independent representative fault contexts must still be justified. With zero failures over exposure T under a homogeneous Poisson failure model, the one-sided95% upper rate is −ln(.05)/T. Zero events do not establish perfect reliability; model assumptions matter.

## Lifetime data and censored fitting

Use δ_i=1 for failures,0 for independent noninformative right censoring. Likelihood=∏f(t_i)^δ_i R(t_i)^(1−δ_i). For a two-parameter Weibull with d=Σδ_i>0:

d/β+Σδ_i ln(t_i)−d Σt_i^βln(t_i)/Σt_i^β=0; η=(Σt_i^β/d)^(1/β).

The bundled NIST fixture contains ten failures and ten survivors at500h. Validate fits against the published example rather than inventing a fitting dataset. Report parameter/quantile confidence and goodness-of-fit; maintenance choices require consequence/cost context, not β or B10 alone.

## Dependence and failover

Mixture cR_parallel+(1−c)R_single lies between its inputs. At R_single=.9,R_parallel=.99,c=.5 it is .945. A separately modeled independent controller with survival q=.9, whose failure disables the system, gives .8505: the extra failure mechanism causes harm, not mixture coverage alone.

FTA top event AB∨AC for independent A=.1,B=.2,C=.3 has probability .1(.2+.3−.2×.3)=.044. Cut sets overlap through A; treating them independent gives the wrong .0494. Use Boolean/inclusion-exclusion/BDD calculation.

Agent chains: P(all succeed)=∏P(step_i succeeds | prior successes). Marginal products need independence. Estimate conditional/handoff outcomes and end-to-end success with uncertainty; pass^k horizon is distinct from evaluation sample size. Absorbing Markov models require state sufficiency and validated transitions.

Keep FMEA/FTA here. Hand off unsafe interactions between functioning components to foundations-safety-engineering for control structure, unsafe actions and constraints.

Primary references: [NIST censor likelihood](https://www.itl.nist.gov/div898/handbook/apr/section4/apr412.htm), [NIST censored Weibull example](https://www.itl.nist.gov/div898/handbook/apr/section4/apr413.htm), [MIT safety handbooks](https://psas.scripts.mit.edu/home/books-and-handbooks/).
