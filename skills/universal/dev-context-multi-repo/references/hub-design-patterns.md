# Hub Design Patterns

Recommended shape:
- one coordination repo
- one portable root `AGENTS.md`
- one thin `CLAUDE.md` compatibility layer when Claude-specific behavior matters
- one schema set
- generated profiles
- generated catalog pages
- graph outputs
- freshness and coverage reports

Best-practice organization:
- keep the root instruction file concise and task-routing focused
- put deep operating rules in linked docs or scoped rules
- add nested instruction files only when the nearest-directory override is genuinely needed
- keep platform-specific instruction files additive, not divergent
- derive human-readable catalog pages from structured profile data
- treat raw scans as transient inputs and normalized profiles as canonical generated outputs

Avoid:
- giant root instruction files
- manually curated duplicate summaries
- one-off profile formats per portfolio
- coupling the hub to one AI vendor

## Canonical Page Shape

<!-- Source: github.com/garrytan/gbrain@adb02b7826a010700efc968b18df8aaf17d8ffa1 (MIT), extracted 2026-04-13 -->

Catalog and concept pages should default to the **compiled-truth + timeline** two-zone layout. The top of the page is a regenerable synthesis of current state; the bottom is an append-only evidence log where every claim above the line can be traced to a dated source.

Reference: [assets/catalog-compiled-truth-template.md](../assets/catalog-compiled-truth-template.md) has a full example for a repo catalog page plus the discipline rules (above-line rewrites, below-line appends, strict `[Source: …]` citation format, resolved Open Threads moving into the Timeline rather than disappearing).

Use this shape because it answers two different questions cheaply at the same time: *"what is true now?"* reads the top, *"how did we get here?"* reads the bottom. A single append-only log fails the first question; a single rewriteable summary fails the second.
