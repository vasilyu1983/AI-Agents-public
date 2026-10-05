# Source Currency: Stale, Dead, and Changed Sources

Research sources change status: sites shut down, blogs move, APIs add keys or rate limits, and freemium tools reprice. This file teaches how to recognize each failure and what to do about it. It holds no status table, prices, or limits. For the current record of a source, read `data/sources.json`, then confirm anything the scan depends on at the operator's own page on the day you use it.

## Contents

- [Lookup Rule](#lookup-rule)
- [Anti-Pattern Catalog](#anti-pattern-catalog)

---

## Lookup Rule

Before a source carries weight in a scan:

1. Open the operator's own page (docs, terms of use, pricing, or status page), not an aggregator or a remembered figure.
2. Confirm the source is live and still publishes at the URL you plan to use.
3. Note any key requirement, rate limit, or plan cap that affects the scan, and pace requests to it.
4. Record the check date next to any figure you cite in the report.
5. If the operator page cannot be reached, say so in the report and treat the fact as unverified.

---

## Anti-Pattern Catalog

### AP-1: Counting a Retired Source as a Live Signal

**Smell:** A workflow checks a retired site (for example Papers with Code) for "code available" badges or leaderboard entries and treats the result as current.

**Why it fools you:** A retired site's data is frozen at shutdown. Implementations may have been deleted, forked, or superseded since, and a redirect can make the site look alive.

**Counter-recipe:**
1. Search GitHub directly for the paper title or arXiv ID.
2. Use `research-git` to inspect candidate implementations for recent activity, open issues, and dependency freshness.
3. Treat the frozen data as a historical baseline only; confirm current results at the conference proceedings or the paper's own repository.

---

### AP-2: Treating an Archive as Current

**Smell:** A scan counts a publication on indefinite hiatus (for example Distill) as an active source.

**Why it fools you:** An archive inflates the source count without adding recent signal.

**Counter-recipe:**
1. Use the archive for foundational explanations that remain canonical.
2. For current material, use sources that still publish.
3. Mark archive findings with their real `window` and do not grade them as recently validated.

---

### AP-3: Citing a Moved Blog at Its Old URL

**Smell:** A sources file or query points at an author's old blog host after the author moved.

**Why it fools you:** The old URL may still serve cached content, so the scan looks complete while missing every post since the move.

**Counter-recipe:**
1. Check the author's current home page or profile for the live blog URL before scanning.
2. Update `data/sources.json` to the live URL.
3. Search both the old and new locations when the move date is unclear.

---

### AP-4: Treating a Research API as Unlimited

**Smell:** A script bursts requests at OpenAlex, Semantic Scholar, or arXiv with no pacing, or assumes no key is ever needed.

**Why it fools you:** These APIs set key rules and rate limits that change over time. Some degrade quietly (partial or empty pages) before they fail hard, so a script can look successful while returning a fraction of the results.

**Counter-recipe:**
1. Look up each API's current key requirement and rate limit on its operator page before a large scan.
2. Pace requests to the strictest limit in the scan.
3. On HTTP 429, back off exponentially and cap the wait.
4. Log result counts per query and flag an unexpected zero, so a throttled empty page is not read as "no papers".

---

### AP-5: Paying for a Citation-Graph Tool When a Free API Suffices

**Smell:** A workflow uses a paid or capped visual citation-graph tool as the default for bulk citation traversal.

**Why it fools you:** The citation edges these tools draw are usually available from the OpenAlex and Semantic Scholar APIs. The paid interface is worth it only when the visual layout is the bottleneck, which is rare in automated scanning.

**Counter-recipe:**
1. Use the OpenAlex or Semantic Scholar citation endpoints for bulk traversal.
2. Reserve visual graph tools for manual exploration of an unfamiliar subfield.
3. Check the tool's current plan limits at its own page before building a workflow on it.

---

### AP-6: Citing Commercial-Tool Pricing as a Durable Fact

**Smell:** A scan report, idea card, or `data/sources.json` entry states a price or free-tier cap for a research tool without a check date.

**Why it fools you:** Freemium research tools reprice on a SaaS cadence, and third-party pricing aggregators often disagree with each other and with the vendor.

**Counter-recipe:**
1. Never state a tool price without the date you checked it and the page you checked.
2. Prefer the vendor's own pricing page over aggregators; if the vendor page blocks an automated fetch, say so and corroborate across two or more independent sources before citing a figure.
3. In reports, write "verify current pricing before acting" rather than presenting a cached figure as current.
