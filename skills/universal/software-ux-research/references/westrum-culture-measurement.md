# Westrum Culture Measurement — A Validated Instrument for Team Information Flow

Marschak–Radner team theory tells you what an information structure *should* be. It does not tell you what your team's actual information structure *is*. This file adds the measurement side: a sociological typology of how information flows through organizations, and the seven validated survey items that turn it from a vibe into a number.

Source: Nicole Forsgren, Jez Humble, Gene Kim, *Accelerate: The Science of Lean Software and DevOps* (IT Revolution, 2018), Chapter 3 (typology, Table 3.1, printed p. 65) and Chapter 13 (psychometrics, printed pp. 191–192). The typology itself is Ron Westrum's (Westrum 2004/2014), not the *Accelerate* authors'.

## Table of Contents

- [Bridge: Why This Sits Next to Team Theory](#bridge-why-this-sits-next-to-team-theory)
- [Westrum's Three-Culture Typology](#westrums-three-culture-typology)
- [The Seven Validated Survey Items](#the-seven-validated-survey-items)
- [Scoring](#scoring)
- [Causal Direction: Act Your Way to a Better Culture](#causal-direction-act-your-way-to-a-better-culture)
- [Provenance and Limits](#provenance-and-limits)
- [How to Use This With the Primitives](#how-to-use-this-with-the-primitives)

---

## Bridge: Why This Sits Next to Team Theory

`foundations-team-theory` is built on the Marschak/Radner mathematics of team decision problems: agents sharing a payoff, partitioned observations, an information structure chosen by the designer, and person-by-person optimality as the solvable weakening of global optimality. Those primitives are *normative* — they say what a well-designed information structure looks like, and they price communication against the loss it removes.

Westrum's typology is the *empirical* counterpart. Team theory assumes an information structure is whatever the designer wired; Westrum's observation is that organizational culture determines what information actually flows through the wire — whether messengers are shot, whether responsibilities are shirked, whether bridging across boundaries happens at all. A team-theoretic design that assumes honest, timely observation-sharing between agents is describing a *generative* culture whether or not it says so. In a pathological one, the same wiring diagram delivers distorted or withheld observations, and the person-by-person optimum you solved for is solving the wrong problem.

The seven items below are what make that check runnable. They give you a measured estimate of whether your assumed information structure is the one you actually have — the difference between designing communication rules and knowing whether they are being used.

Westrum's own framing supports the link: he holds that "the organizational culture predicts the way information flows through an organization," and gives three characteristics of good information (Ch. 3, printed p. 65):

1. It provides answers to the questions that the receiver needs answered.
2. It is timely.
3. It is presented in such a way that it can be effectively used by the receiver.

Those are, near enough, the properties team theory quietly assumes every observation has.

---

## Westrum's Three-Culture Typology

Westrum developed the typology in 1988 while researching human factors in system safety — accidents in highly complex, risky technological domains such as aviation and healthcare. The three types are described in *Accelerate* Ch. 3 (printed p. 64) as:

- **Pathological (power-oriented) organizations** are characterized by large amounts of fear and threat. People often hoard information or withhold it for political reasons, or distort it to make themselves look better.
- **Bureaucratic (rule-oriented) organizations** protect departments. Those in the department want to maintain their "turf," insist on their own rules, and generally do things by the book — their book.
- **Generative (performance-oriented) organizations** focus on the mission. How do we accomplish our goal? Everything is subordinated to good performance, to doing what we are supposed to do.

Table 3.1, *Westrum's Typology of Organizational Culture* (printed p. 65), reproduced:

| Pathological (Power-Oriented) | Bureaucratic (Rule-Oriented) | Generative (Performance-Oriented) |
|---|---|---|
| Low cooperation | Modest cooperation | High cooperation |
| Messengers "shot" | Messengers neglected | Messengers trained |
| Responsibilities shirked | Narrow responsibilities | Risks are shared |
| Bridging discouraged | Bridging tolerated | Bridging encouraged |
| Failure leads to scapegoating | Failure leads to justice | Failure leads to inquiry |
| Novelty crushed | Novelty leads to problems | Novelty implemented |

The types are not bins but "points on a scale . . . a 'Westrum continuum'" (Westrum 2014, quoted at printed p. 66) — which is exactly why Likert-type items work as the measurement form.

Two caveats the authors themselves raise (printed pp. 69–70): bureaucracy is not necessarily bad — quoting Mark Schwartz, the goal of bureaucracy is to "ensure fairness by applying rules to administrative behavior" — and Westrum's rule-oriented culture is "perhaps best thought of as one where following the rules is considered more important than achieving the mission." Sector is not destiny: the authors report working with US Federal Government teams they "would have no issue describing as generative, as well as startups that are clearly pathological."

---

## The Seven Validated Survey Items

Quoted verbatim from Ch. 13, printed pp. 191–192. The stem is shared; each line is one item.

> On my team . . .
>
> - Information is actively sought.
> - Messengers are not punished when they deliver news of failures or other bad news.
> - Responsibilities are shared.
> - Cross-functional collaboration is encouraged and rewarded.
> - Failure causes inquiry.
> - New ideas are welcomed.
> - Failures are treated primarily as opportunities to improve the system.

Response scale, verbatim: "Using a scale from '1 = Strongly disagree' to '7 = Strongly agree,' teams can quickly and easily measure their organizational culture."

Two design decisions worth carrying over into any instrument you write:

- **Team, not organization.** The authors flag this as "a departure from Westrum's original framework — because organizations can be very large and can have pockets of different organizational cultures. In addition, people can answer more accurately for their team than for their organization."
- **Items, not questions.** The book's own footnote: these "aren't actually questions; instead, they are statements." Statements must be worded strongly enough that a respondent can strongly agree *or* strongly disagree.

The book reports these items "have been tested and found to be statistically valid and reliable" via discriminant validity, convergent validity, and reliability (internal consistency) tests, and states "you can use these questions in your surveys too." Reassess periodically: constructs that pass today can drift, "especially if you suspect a change in the system or environment."

---

## Scoring

From printed p. 68: "take the numerical value (1-7) corresponding to the answer to each question and calculate the mean across all questions. Then you can perform statistical analysis on the responses as a whole."

That mean is the construct score. Do not analyze single items in isolation — the validity work applies to the seven-item construct, not to any one statement pulled out of it. For the general form of that rule, see [`software-ux-research/references/survey-design-guide.md`](survey-design-guide.md#construct-validity-measuring-what-cannot-be-measured-directly).

---

## Causal Direction: Act Your Way to a Better Culture

The book argues you change culture by changing behavior, not by changing minds first. It grounds this in John Shook's account of the Fremont, California plant that seeded US Lean manufacturing (printed p. 74):

> "what my . . . experience taught me that was so powerful was that the way to change culture is not to first change how people think, but instead to start by changing how people behave—what they do" (Shook 2010).

And states the consequence directly (printed p. 75):

> "You can act your way to a better culture by implementing these practices in technology organizations, just as you can in manufacturing."

The practices named are Lean management and continuous delivery. Note the direction of the design claim carefully: the authors describe this as an **inferential predictive** research design (Ch. 12), in which theory-driven hypotheses are stated and then tested — "Whenever we talk about impacting or driving results in this book, our research design utilized this third type of analysis." They explicitly exclude causal analysis: "Predictive, causal, and mechanistic analysis . . . were not included in our research, because we did not have the data necessary for this kind of work," and causal analysis "generally requires randomized studies." So: hypothesized and supported as a directional prediction, in the authors' own words — not established as causation.

Applied to a team-theoretic design, this reads as: do not try to negotiate a better information structure by exhortation. Change the practice that forces the information to move (a shared queue, a blameless review, a cross-team on-call rotation), then re-measure the seven items and see whether the culture followed.

---

## Provenance and Limits

Carry these whenever you cite the instrument or any *Accelerate* magnitude:

- **Association, not causation.** Except where the authors' own inferential-predictive design claims a direction (quoted above), findings in this book are *associated with*, not *causes of*, the outcomes. Correlations reported are Pearson correlations at the exploratory stage; the book is explicit that "correlation is only the exploratory stage."
- **2016-era survey population.** The distribution figures are a snapshot of that respondent pool, not a stable industry constant. Footnote 1 to Ch. 3, verbatim: "In 2016, 31% of respondents were classified as pathological, 48% bureaucratic, and 21% generative." Do not present these as current figures.
- **Self-reported perceptual data.** This is a survey instrument. It measures the lived experience of the people who answered — which the authors argue is the right way to measure culture ("culture is the lived experiences of those working on a team"), but it is not system telemetry and does not become so by being averaged.
- **Sample, not census.** The research is primary and quantitative but drawn from a self-selected respondent pool across four annual collections; the book itself notes that "descriptive findings are only as good as the underlying research design and data collection methods."
- **Retired tiers.** The book's high/medium/low performer thresholds came from a cluster analysis of that same era's data and are not current benchmarks. Use the seven culture items; do not resurrect the performance tiers as present-day fact.

---

## How to Use This With the Primitives

| Primitive | What the seven items add |
|---|---|
| #2 Information structure | Measures whether observations actually reach the agents your design assumes they reach ("Information is actively sought") |
| #4 Value of communication | A low score on bridging or shared responsibility means your communication channel's realized value is below its theoretical value — the channel exists but is not used |
| #7 Information cost | Fear is an unpriced cost on the channel; "Messengers are not punished . . ." is the item that detects it |
| #8 Organizational forms | Bureaucratic scores predict departmental optimization over global payoff — the common-task condition weakening in practice |
| #10 Common-task condition | "Failures are treated primarily as opportunities to improve the system" is a direct probe of whether the shared payoff is genuinely shared |

Full primitive definitions: [`primitives-overview.md`](../../foundations-team-theory/references/primitives-overview.md).
