# Mask: First-Principles

## Purpose

Strip away analogies, precedent, and "how we've always done it." Reason from physical or logical ground truth. Richard Feynman's problem-solving method, popularized in startup context by Elon Musk (though the method is centuries older).

## When To Apply

- Architecture decisions dominated by legacy patterns ("we use service pattern X because we always have")
- Cost decisions where the existing baseline is treated as a fixed constant
- Technology choices framed by "industry standard" rather than actual requirements
- Performance debates where assumptions about "impossible" or "too slow" are inherited from older tooling
- Pricing decisions anchored to competitor pricing without understanding the underlying cost structure
- Any decision where "that's just how it's done" is load-bearing in the argument

## Reasoning Rewrite

The mask replaces analogical reasoning with decomposition:

| Analogical reasoning | First-principles reasoning |
|---|---|
| "Everyone uses microservices at scale" | "What is our actual scaling bottleneck? Is it code complexity, team coordination, deploy frequency, or runtime load? Which of those does microservices actually address?" |
| "Our competitors charge $X" | "What is our actual cost to serve? What is the willingness-to-pay at each segment? Competitor pricing is one data point, not the answer." |
| "We can't do X in under Y milliseconds" | "Why can't we? What's the physical lower bound (speed of light, disk seek, network RTT)? What's the theoretical bound given our hardware? How much of the current latency is essential vs accidental?" |
| "Kubernetes is the standard for container orchestration" | "What are our actual requirements? Multi-tenancy? Auto-scaling? Self-healing? Which are we using today and how would we achieve each without Kubernetes?" |
| "We need a data warehouse" | "What questions do we need to answer? What's the data volume and query pattern? Would a simple read replica + SQL work for 80% of the questions?" |

The key move: **identify which assumptions are inherited vs actually required**, then test whether the inherited ones still apply in your specific situation.

## Launch Overlay

Append this to the perspective-agent brief for any agent you want to wear the First-Principles mask:

```text
MASK: First-Principles

In addition to your normal analysis, you must deconstruct the proposal to its
ground-truth assumptions. Do not let analogies or precedent do the work.

1. List every "everyone does it this way" or "it's standard to X" or "that's
   the industry norm" assumption in the proposal. Write each as an explicit
   claim.

2. For each claim, ask:
   - Why is this true? Trace back to the underlying physics, logic, or
     actual requirement.
   - Is the claim true in our specific situation, or only in the situation
     where the convention originated?
   - What would have to change for this claim to stop being true?

3. Identify the ESSENTIAL constraints vs the ACCIDENTAL conventions. Essential
   constraints are imposed by physics, logic, or hard business requirements
   (the user literally has to see a response within 200ms because of
   perception research). Accidental conventions are imposed by 'this is what
   our previous tool did' or 'this is what the first team chose in 2019.'

4. Propose what the decision would look like if you had to rebuild it today
   with no inherited assumptions.

Return your analysis in two parts:
1. Forward analysis (your normal stakeholder-role read)
2. First-principles analysis (inherited assumptions, essential vs accidental
   constraints, rebuild-from-scratch proposal)

The first-principles analysis often exposes that 3-4 inherited constraints no
longer apply, which changes the decision entirely.
```

## Worked Example

**Decision**: We need to add caching to speed up the dashboard. Should we use Redis?

**Forward analysis**: Redis is fast, well-understood, easy to deploy, etc.

**First-principles analysis**:

*Inherited assumption*: "Dashboards need caching to be fast."
- Why is this true? Because historically, dashboard queries scanned large tables and took 3-5 seconds.
- Is it true in our situation? Our data is 50GB in Postgres with proper indexes. A well-crafted query on this volume should return in <200ms without any caching layer.
- What would have to change? Either the data volume grows to where indexes don't save us, OR the query patterns are genuinely more complex than simple reads.

*Inherited assumption*: "Redis is the right cache."
- Why? Because Redis was designed for exactly this use case, and the industry norm is Redis for caching.
- Is it true in our situation? We have a single-node deployment with no HA requirement. Redis adds an operational surface (separate process, network hop, eviction policy, persistence decisions). A simple in-process LRU cache in the application layer would be zero operational cost.

*Rebuild from scratch*: Instead of "add Redis," the answer might be:
1. First, profile the actual slow queries and fix them with better indexes (most likely eliminates the need for caching at all)
2. If caching is still needed, use in-process LRU for <100MB of hot data
3. Only reach for Redis if you have multiple app servers that need shared cache coherence

The inherited conventions pushed toward Redis before anyone validated that caching was actually the right answer.

## Common Mistakes

- **Using it as an excuse to avoid industry practice**: "First principles says we shouldn't use Kubernetes" is a red flag if you don't understand what Kubernetes solves. The goal is to understand WHY conventions exist, then decide whether they apply — not to ignore them.
- **Over-applying it**: not every decision benefits from a rebuild-from-scratch analysis. Use it when inherited constraints are load-bearing and potentially outdated.
- **Confusing "first principles" with "contrarian"**: they are not the same. Sometimes the convention is right for good reasons and first-principles analysis confirms it.
- **Skipping step 4**: without proposing what you'd build from scratch, you have an assumption audit but no decision change.

## Evidence

- Richard Feynman, *Surely You're Joking, Mr. Feynman* (1985) — describes the method without naming it. His famous line: "I can live with doubt and uncertainty and not knowing. I think it's much more interesting to live not knowing than to have answers which might be wrong."
- Elon Musk's public discussions of battery cost analysis (2010s) — first-principles breakdown of battery materials proved batteries could be 10× cheaper than industry pricing suggested, because industry pricing reflected convention, not physics.
- Aristotle's *Posterior Analytics* — the original formulation of reasoning from first principles, 2300 years before Feynman.
