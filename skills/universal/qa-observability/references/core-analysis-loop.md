# The Core Analysis Loop

A hypothesis-free method for localising a production anomaly you cannot reproduce and have no theory about. Source: Charity Majors, Liz Fong-Jones, George Miranda, *Observability Engineering* (Early Release ch. 7; final ed. ch. 8), "The core analysis loop" and "Automating the brute force portion of the core analysis loop".

This is a **method**, not a product. Any backend that stores arbitrarily-wide structured events and can group by arbitrary dimensions at query time can run it. Honeycomb's BubbleUp is the implementation the book uses to illustrate it (see `tools-ebpf-apm.md` for that vendor entry); the loop itself is backend-agnostic.

## Table of Contents

- [When to reach for this instead of hypothesis-driven debugging](#when-to-reach-for-this-instead-of-hypothesis-driven-debugging)
- [The four-step loop](#the-four-step-loop)
- [Automating the brute-force portion](#automating-the-brute-force-portion)
- [Worked shape of the output](#worked-shape-of-the-output)
- [The hard prerequisite: wide structured events](#the-hard-prerequisite-wide-structured-events)
- [Operating notes and failure modes](#operating-notes-and-failure-modes)
- [Related](#related)

## When to reach for this instead of hypothesis-driven debugging

`qa-debugging` runs a **hypothesis-driven** workflow: Reproduce → Isolate → Instrument → fix → verify. That workflow assumes you can get the failure to happen again, and that you have at least a rough theory of where it lives.

The core analysis loop is the **complement** for the case where neither holds: a production anomaly that will not reproduce locally, in a system whose architecture you may not know, where the honest starting state is "something is slow and I have no idea why". The book frames the distinction as debugging *from known conditions* (you already know what to ask, so you jump to the right high-cardinality query) versus debugging *from first principles* (you assume nothing and let the data name the suspect).

Use hypothesis-driven debugging when you have a hypothesis. Use this loop when a hypothesis would be a guess — and note that the two chain naturally: the loop localises the anomaly to a component or condition, and hypothesis-driven debugging takes over from there.

## The four-step loop

Debugging from first principles begins when something tells you a thing is wrong — an alert, or something as ordinary as a customer complaint.

1. **Start with what prompted the investigation.** What did the customer or the alert actually tell you? Start there, not with a theory.
2. **Verify that what you know so far is true.** Is there a notable change in performance somewhere in this system? Data visualisations earn their place here: a change in behaviour shows up as a change in curve. If there is no visible change, the premise is wrong and the investigation restarts.
3. **Search for the dimensions that might drive that change.** Three moves, used in any order:
   - **Examine sample rows** from the area that shows the change — are there outliers in any column that hint at a cause?
   - **Slice those rows across dimensions**, looking for patterns — does any view highlight distinct behaviour along one or more dimensions?
   - **Filter to particular dimensions or values** within those rows to expose potential outliers more sharply.
4. **Ask whether you now know enough.** If yes, you are done. If not, **filter the view to isolate this area of performance as your next starting point, and return to step 3.**

The loop is deliberately mechanical. Its value is that it needs "no prior knowledge or wisdom about the system required" — it replaces the leap of familiar brilliance with a methodical, repeatable, verifiable process that a stranger to the codebase can execute.

## Automating the brute-force portion

Cycled by hand across every available dimension, the loop is correct but slow — the book calls the manual brute-force version potentially "an inordinate amount of time" and impractical to leave to human operators alone. The automation is a single well-defined computation:

1. **Isolate the anomalous region** — for example, a spike in request latency selected out of a heatmap.
2. **Compute the value distributions of *all* dimensions inside that region** (the anomaly).
3. **Compute the same distributions outside it** (the system baseline).
4. **Diff the two.**
5. **Sort by the size of the difference.**

What comes back is a ranked list of the ways in which the events you care about differ from everything else — "whether that be one deviation or dozens". No seeded intelligence about the application is needed, precisely because the method assumes nothing about it.

This is what to ask of a tool, and what to build if the tool does not have it: given a selected region and a baseline, rank every dimension by how differently it is distributed between the two.

## Worked shape of the output

The book's example (Honeycomb BubbleUp on a real incident) surfaces results for **63 interesting dimensions**, ranked by largest percentage difference. The top result is a field named `global.availability_zone` with a value of `us-east-1a`:

> only showing up in 17% of baseline events, but showing up in 98% of anomalous events

That single row localises the problem: slow events originate overwhelmingly from one availability zone. A second surfaced dimension narrowed it further to a particular VM instance type. Other dimensions surfaced too, but with less stark differences — which is itself the signal that they were probably not relevant.

The earlier, generic illustration in the same chapter has the same shape — a sorted list of dimensions and how often each appears inside the isolated area versus the baseline, e.g. an endpoint value present in 100% of requests in the isolated area but only 20% of the baseline.

Read the output as **correlation with a rank order**, not as a cause. In the book's case the strong `us-east-1a` signal turned out to be an underlying network issue with the cloud provider's entire availability zone — confirmed by contacting the provider and by independent customer reports from the same zone, not by the ranking alone.

## The hard prerequisite: wide structured events

This is the boundary condition, and it is not negotiable. The book states it directly:

> Note that the core analysis loop is something that can only be achieved using the baseline building blocks of observability, which is to say arbitrarily-wide structured events. You cannot achieve this with metrics -- they lack the broad context to let you slice and dice and dive up or down in the data.

Logs are only conditionally usable: the book allows them "unless you have correctly appended all the request id, trace id, and other headers, and then done a great deal of postprocessing to reconstruct them into events -- and then added the ability to aggregate them at read time and perform complex custom querying." In practice that is rebuilding an event store.

Practical consequences for instrumentation design:

- **Pre-aggregated metrics cannot run this loop.** Once a dimension is collapsed into a counter, the value that would have explained the anomaly is gone. This is the concrete cost of a low cardinality budget — see the cardinality note in `SKILL.md`.
- **One wide event per unit of work** (request, job, consumer message) beats many narrow ones. The dimensions you never thought to correlate are exactly the ones this loop finds.
- **Attributes you cannot group by are dead weight.** If the backend cannot `GROUP BY` a field at query time without pre-indexing, that field cannot participate in step 3.
- **Even the manual loop is unattainable without these building blocks** — automation is a speed improvement on top of a capability that the event model either gives you or does not.

## Operating notes and failure modes

- **Automated anomaly detection is not a substitute.** The same chapter argues that the hard part is choosing the box: too small and normal behaviour is flagged as anomalous, too large and anomalies are miscategorised as normal. In an environment where every deploy legitimately changes the performance curve, a human picks the region and the machine ranks the dimensions.
- **Correlation is where the loop stops.** It tells you which conditions accompany the anomaly. Confirming causation is a separate step, and often needs a second source (provider status, an independent report, a targeted experiment).
- **A flat ranking is information.** If no dimension separates anomaly from baseline, the anomalous region is probably drawn wrong, or the driving dimension is not instrumented at all.
- **Scope boundary:** this localises the anomaly to a component, condition, or population. It does not debug code logic — see the Expert Judgment note in `SKILL.md` on observability operating "on the order of systems, not on the order of functions", and switch to a debugger once you know where to look.

## Related

- `../../qa-debugging/references/production-debugging-patterns.md` — the hypothesis-driven counterpart, for reproducible failures
- `references/tools-ebpf-apm.md` — Honeycomb/BubbleUp as one vendor implementation of the automation
- `references/sampling-strategies.md` — what sampling does to the dimension distributions this loop diffs
- `references/log-aggregation-patterns.md` — structured event fields that make step 3 possible
