# Sharding Decision Framework

Use this file when someone is considering splitting a dataset across multiple database clusters — or has already decided to and needs to pick a partitioning key.

Primary source: Silvia Botros and Jeremy Tinley, *High Performance MySQL*, 4th ed. (O'Reilly, 2021), Ch. 11 "Scaling MySQL". The reasoning is MySQL-framed but engine-agnostic: the decision structure, the ER-diagram method, and the list of capabilities you give up apply to any relational store.

## Table of Contents

- [Sharding Is the Last Option, Not the First](#sharding-is-the-last-option-not-the-first)
- [Functional Partitioning vs Data Sharding](#functional-partitioning-vs-data-sharding)
- [Shard Only What Needs Sharding — With a Caveat](#shard-only-what-needs-sharding--with-a-caveat)
- [Choosing a Partitioning Key: The ER-Diagram Method](#choosing-a-partitioning-key-the-er-diagram-method)
- [Multiple Partitioning Keys](#multiple-partitioning-keys)
- [What You Give Up](#what-you-give-up)
- [Decision Checklist](#decision-checklist)

## Sharding Is the Last Option, Not the First

The book's ordering is explicit and worth preserving: **"If you cannot manage write traffic growth with optimized queries and queuing writes, then sharding is your next option."** Exhaust the cheaper levers first, in roughly this order.

**1. Query and schema optimization.** The ordinary work — index coverage, removing N+1 patterns, cutting write amplification from excess indexes. Cheapest, reversible, no architectural commitment.

**2. Read pools, if reads are the constraint.** An active/read-pool topology scales reads horizontally by directing writes to the source and reads to a pool of replicas. Two limits to know before you count on it. First, it does not scale forever: "At some point, the horizontal scaling will fall off due to the demand of replication on the source." Second, it costs you read-after-write consistency — "your application must have some tolerance for stale reads. You will never be able to guarantee that a write you complete on the source has already been replicated to a replica." Read pools do nothing for write load.

**3. Queuing, if writes are the constraint.** This is the step most teams skip, and it is where the highest-leverage saving usually is. Before sharding, "you should examine the write hotspots in your data and consider whether all the writes are truly required to persist to the database actively. Can some of them be placed into a queue and written to the database within an acceptable time frame?"

The worked example is a bulk-delete API: rather than executing deletes synchronously, return HTTP `202 Accepted`, enqueue the request (Kafka, SQS, or similar), and drain it "at the pace that doesn't lead to overloading the database directly with delete calls." The book is blunt about what this buys: **"The difference between the 200 and 202 response codes is all the engineering work of sharding this data to support a lot more parallel writes."** That is a product negotiation, not a technical one — "a common spot where negotiation with your product team is crucial for making the guarantees of the API plausible and achievable."

If you queue, instrument it: decide up front "the desired time frame within which these calls are expected to be fulfilled after being placed in queue," and monitor queue residency time. Rising residency "is going to be your metric for when this strategy has run its course and you really need to start splitting this data set."

**4. Sharding.** Only now. "Sharding means splitting your data into different, smaller database clusters so that you can execute more writes on more source hosts at the same time."

> **On row-count thresholds.** The book's 10-million-user and 500-million-user figures are illustrative hypotheticals in a worked blogging-service example, not thresholds. There is no row count at which sharding becomes correct. The trigger is write throughput that survives steps 1–3, not table size.

## Functional Partitioning vs Data Sharding

Two different things, often conflated.

**Functional partitioning** ("division of duties") means "dedicating different nodes to different tasks" — user records on one cluster, billing on another. Each cluster scales independently, and load spikes stay isolated: "A surge in user registrations might put a strain on the user cluster. With separate systems, your billing cluster is less loaded, allowing you to bill customers." Cheaper than data sharding and often sufficient. It buys a fixed, small multiple of capacity — you can only split along as many functional seams as the domain has.

**Data sharding** means splitting one logical dataset horizontally: "You shard the data by splitting it into smaller pieces, or shards, and storing them on different nodes." This is "the most common and successful approach for scaling today's very large MySQL applications" and the one that scales indefinitely — and costs the most.

Try functional partitioning first where a clean seam exists. It is a smaller change and does not force the cross-shard problems below.

## Shard Only What Needs Sharding — With a Caveat

The standard advice is to shard just the fast-growing tables: "Most applications shard only the data that needs sharding—typically, the parts of the data set that will grow very large." A small, mostly-cacheable table does not need splitting even in a large system.

The caveat is the part people get wrong:

> "Be wary when planning to 'only shard what needs sharding.' That concept needs to include not just the data that is growing rapidly but also the data that logically belongs with it and will regularly be queried at the same time. If you are sharding based on a `user_id` field but there is a set of other smaller tables that join on that same `user_id` in a majority of queries, it makes sense to shard all these tables together so that you can keep a majority of your application queries against one shard at a time and avoid cross database joins."

The unit of sharding is not "one big table." It is **the set of tables that queries touch together**, co-located by the same key. A small lookup table left unsharded turns every query that joins it into a cross-shard query — which is exactly what the design is trying to avoid. Identify the co-location set before you write any migration.

## Choosing a Partitioning Key: The ER-Diagram Method

"The most important challenge with sharding is finding and retrieving data." The partitioning key determines which rows land on which shard, and a good one answers both "Where should I store this data?" and "Where can I find the data I need to fetch?"

**The objective:** "make your most important and frequent queries touch as few shards as possible." Ideally one. "The worst case with sharded data sets is when you have no idea where the desired data is stored so that you need to scan every shard to find it."

**A worked negative example.** Partitioning on a hash of each table's own primary key — as MySQL's NDB Cluster does — is trivially simple to write and usually wrong for an application: "if you want user 3's blog posts, where can you find them? They are probably scattered evenly across all the shards because they're partitioned by the primary key, not by the user. Using a primary key hash makes it simple to know where to store the data, but it might make it harder to fetch it." It answers the first question and fails the second.

**The method.** Draw the entity-relationship graph and look for the connected subgraph reachable from each candidate key:

> "A good way to start is to diagram your data model with an entity-relationship diagram or an equivalent tool that shows all the entities and their relationships. Try to lay out the diagram so that the related entities are close together. You can often inspect such a diagram visually and find candidates for partitioning keys that you'd otherwise miss."

What you are looking for is a graph you can cut cleanly. The book contrasts two data models: the easily-sharded one "has many connected subgraphs consisting mostly of nodes with just one connection and you can 'cut' the connections between the subgraphs relatively easily," while the hard one has no such subgraphs. Reassuringly: "Most data models, luckily, look more like the lefthand diagram than the righthand one."

**The edges you cut are exactly what you lose.** Every relationship crossing a shard boundary becomes a query the application must resolve itself — the graph cut *is* the cost accounting. Which is why the diagram alone is not enough: "Don't just look at the diagram, though; consider your application's queries as well. Even if two entities are related in some way, if you seldom or never join on the relationship, you can break the relationship to implement the sharding." Weight each edge by how often real queries traverse it, then cut where the weight is lowest.

**A good key is usually an important entity's primary key**, because that entity becomes the unit of sharding: "if you partition your data by a user ID or a client ID, the unit of sharding is the user or client."

**Balance matters too.** Pick "something that lets you avoid cross-shard queries as much as possible but also makes shards small enough that you won't have problems with disproportionately large chunks of data. You want the shards to end up uniformly small, if possible, and if not, at least small enough that they're easy to balance by grouping different numbers of shards together." The book's illustration: for a US-only application splitting into 20 shards, do not shard by state — California is too large. County or telephone area code works, "because even though those won't be uniformly populated, there are enough of them that you can still choose 20 sets that will be roughly equally populated in total, and you can choose them with an affinity that helps avoid cross-shard queries." Many small buckets you can group beats few buckets sized by nature.

## Multiple Partitioning Keys

Some domains have two genuine access dimensions and no single key serves both. "you might need to shard your blogging application's data by both the user ID and the post ID because these are two common ways the application looks at the data... Sharding by user doesn't help you find comments for a post, and sharding by post doesn't help you find posts for a user. If you need both types of queries to touch only a single shard, you'll have to shard both ways."

That implies storing some data twice. It does **not** imply two full copies: "Just because you need multiple partitioning keys doesn't mean you'll need to design two completely redundant data stores." The book-club example stores full comments with the user data and only "a comment's headline and ID with the book data" — enough to render most book views from one store, with a fetch to the other store only when full comment text is needed. Duplicate the minimum that satisfies the common read path, and accept a second lookup for the rare one.

## What You Give Up

Budget for all of these before committing.

**Cross-shard joins and aggregations.** "Most sharded applications have at least some queries that need to aggregate or join data from multiple shards." A "most active users" listing must by definition touch every shard. "Making such queries work well is the most difficult part of implementing data sharding because what the application sees as a single query needs to be split up and executed in parallel as many queries, one per shard." Even with a good abstraction layer "such queries are so much slower and more expensive than in-shard queries that aggressive caching is usually necessary as well."

The health metric: **"You will know that the sharding scheme you chose was a good one if the cross-shard queries become outliers instead of norms."** If they are the norm, the partitioning key is wrong. (The exception is a design where that is intended — "Some applications use essentially random sharding where consistent data distribution is important or when there is no good partitioning key. A distributed search application is a good example. In this case, cross-shard queries and aggregation are the norm, not the exception.")

Mitigations: put cross-shard aggregation in application logic rather than pushing it into the data layer; use summary tables "built by traversing all the shards and storing the results redundantly on each shard," or consolidated onto a separate store if per-shard duplication is too wasteful. Non-sharded data often lives in a global node "with heavy caching to shield it from the load."

**Foreign keys across shards.** They simply do not work. "the normal solution is to check referential integrity as needed in the application or use foreign keys within a shard because internal consistency within a shard might be the most important thing." Integrity that the engine used to guarantee becomes application code you have to write and test.

**Cross-shard transactions.** "It's possible to use XA transactions, but this is uncommon in practice because of the overhead." Assume you do not get atomicity across shards, and design operations to be either single-shard or eventually consistent.

**Immediate consistency for cascading operations.** The accepted pattern is deferred cleanup: "if a user's book-club account expires, you don't have to remove it immediately. You can write a periodic job to remove the user's comments from the per-book shard, and you can build a checker script that runs periodically and makes sure the data is consistent across the shards." Two new pieces of infrastructure — the cleanup job and the consistency checker — that did not exist pre-sharding, and both need their own monitoring.

## Decision Checklist

Work top to bottom. Stop at the first row that resolves the pressure.

| Step | Question | If yes |
|---|---|---|
| 1 | Are slow or unindexed queries a material part of the load? | Fix those first — cheapest, reversible |
| 2 | Is the constraint read throughput rather than write throughput? | Read pool, if stale reads are tolerable |
| 3 | Can any writes tolerate deferred persistence? | Queue them; monitor queue residency time as the next trigger |
| 4 | Is there a clean functional seam between subsystems? | Functional partitioning before data sharding |
| 5 | Does the ER graph have a key whose connected subgraph covers most query paths? | That is your partitioning-key candidate |
| 6 | Are the shards it produces roughly balanced, or groupable into balanced sets? | Proceed; otherwise pick a finer-grained key |
| 7 | Have you enumerated the tables that must be co-located with the key? | Shard them together, not just the big table |
| 8 | Have you costed the cut edges — cross-shard joins, FK checks moved to app code, cleanup and checker jobs? | Budget them as build work, not follow-up |
