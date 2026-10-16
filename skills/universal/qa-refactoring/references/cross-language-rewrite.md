# Cross-Language and Cross-Framework Rewrite

Same-language refactoring proves behavior with in-process tests. A rewrite into another language or framework cannot: the old tests do not run on the new code. Typical cases: PHP to Next.js, COBOL batch to Java, VB6 or .NET Framework to modern .NET, Python 2 to 3, AngularJS or jQuery screens to React, a Rails or Django monolith to services. This reference owns what changes: an oracle that sits outside both stacks, the semantic hazards of the language pair, effects that leave the process, and the loop that scales translation. Seams, characterization and the agent loop stay in [strangler-fig-migration.md](strangler-fig-migration.md), [characterization-testing.md](characterization-testing.md) and [brownfield-agent-loop.md](brownfield-agent-loop.md).

## Contents

- [When to use](#when-to-use)
- [Black-box parity oracle](#black-box-parity-oracle)
- [Semantic hazards of the language pair](#semantic-hazards-of-the-language-pair)
- [Side-effect inventory and capture sink](#side-effect-inventory-and-capture-sink)
- [Spec extraction](#spec-extraction)
- [Auth and session](#auth-and-session)
- [URLs and SEO](#urls-and-seo)
- [Security parity](#security-parity)
- [Routing seam](#routing-seam)
- [Translation at scale](#translation-at-scale)
- [Data](#data)
- [Code-graph fallback for unsupported languages](#code-graph-fallback-for-unsupported-languages)

## When to use

Use this when the old tests cannot run against the new code and the legacy system keeps serving traffic or jobs. The end-state choice (modernize in place, new frontend over the legacy backend, or full rewrite in slices) is made in [migration-modernization-guide.md](../../software-architecture-design/references/migration-modernization-guide.md); decide there first.

Stop and choose modernize-in-place when the goal is only a supported runtime and typed code: a runtime upgrade plus static analysis with a baseline file and automated upgrade rules (for example PHPStan and Rector for PHP, OpenRewrite for Java) keeps one language, so the ordinary refactor loop applies and none of the rest of this file does.

## Black-box parity oracle

The oracle drives only the system's observable interface, so the same suite runs unchanged against both stacks. Pick the interface the users or callers actually touch:

| Legacy shape | Oracle input | Oracle compares |
|---|---|---|
| Web app or API | HTTP request | Status, headers that matter, body, DB-state diff |
| UI screens (frontend rewrite) | Browser actions | Accessibility tree or DOM text, screenshots with a set tolerance, network calls made |
| Batch or CLI job | Input files, arguments, schedule | Output files byte for byte or after listed normalisation, exit code, DB-state diff |
| Message consumer | Consumed messages | Produced messages and their order, DB-state diff |
| Library | Public API calls | Return values, raised errors, observable state |

Every row also compares captured outbound effects (see the sink below).

- **One target variable.** The suite takes a target (base URL, binary, queue, package) and a database connection per run. The same files run against legacy and against the new stack; a second copy of the suite is a defect.
- **Normalisation rules are written down and reviewed.** Typical rules: generated IDs, timestamps the request itself creates, CSRF tokens, cookie values, header or field order. Each rule is a named entry with an owner. Normalising a field away hides drift in that field, so a new rule needs the same review as a changed assertion.
- **Pin nondeterminism.** Fix the clock, random seed, locale and timezone on both stacks and in the database session before capture. An unpinned oracle flakes, and the loop then "fixes" the flake by weakening an assertion.
- **Corpus.** Build it from production traffic, job inputs or logs with PII scrubbed before they leave production, then add hand-picked edge cases the logs never show (empty and oversized input, repeated submits, unicode, missing optional fields, expired sessions, month-end and leap-day runs).
- **Prove the oracle can fail.** Before migration of a slice: it passes against legacy and it fails against the unmigrated new stack. On top of that, seed one deliberate difference in the new stack and confirm the matching case goes red. An oracle never seen failing is not yet an oracle.
- **The test writer is not the implementer.** A separate agent or person writes the parity tests from the spec and the legacy behavior; the implementer cannot edit them. Hash the suite each iteration as in the brownfield loop.

Record parity as a per-slice result: cases run, cases passing on legacy, cases failing on the unmigrated stack, normalisation rules in force.

## Semantic hazards of the language pair

Agents translating line by line keep the syntax and change the meaning. Before the first slice, write the hazard list for the specific pair by walking these categories against both languages' documentation, then pin one parity case per hazard with inputs chosen to hit the difference.

| Category | Question to answer for the pair |
|---|---|
| Comparison and coercion | Does `==`, string-to-number or truthiness behave the same? |
| Null and empty | Which of null, empty string, zero, empty collection are distinct, falsy, or equal? |
| Numbers | Integer width and overflow, decimal versus binary float, division of integers |
| Rounding and formatting | Rounding mode (half-up, half-even, half-away-from-zero), number and currency formatting |
| Text | Encoding, byte versus character length, case mapping, collation and sort of accented text |
| Dates and time | Default timezone, zone-less database types, DST, month arithmetic |
| Collections | Ordering guarantees of maps and sets, key coercion, sort stability, comparator contract |
| Errors | Exceptions versus error values, suppressed warnings, partial failure mid-loop |
| State lifetime | Per-request versus per-process state, globals, static caches, thread or event-loop sharing |
| Load and init order | Code that runs on include, import or class load |
| Dynamic dispatch | Magic methods, reflection, string-built calls that a search for the name misses |
| Database dialect | Implicit casts, truncation, empty string versus NULL, zero dates, charset limits |

### Worked example: PHP to TypeScript

| Hazard | PHP behavior | What to pin |
|---|---|---|
| Loose comparison | `==` juggles types; a numeric string equals a number | Cases around `"0"`, `"abc"`, `null`, `0`, `"1e3"` compared with `==` |
| Falsiness | `null`, `""`, `"0"`, `0`, `[]` are falsy; `"0.0"` and `"false"` are truthy; JS differs on `"0"` and `[]` | Every `if ($x)` and `empty()` on user input |
| Integer range | Integers overflow to float; JS `Number` loses exactness above the safe-integer limit | IDs and money at and above that limit; use `BigInt` or strings where needed |
| Rounding | `round()` rounds half away from zero; `Math.round` rounds half toward positive infinity | Negative `.5` values and prices |
| Float formatting | `number_format`, `printf` and implicit float-to-string differ from JS `toFixed` and `toString` | Every formatted money or percentage output |
| Dates and zones | `date_default_timezone_set`, `DateTime` and MySQL `DATETIME` (no zone) differ from JS `Date` | Values near midnight, DST changes, month ends |
| Locale and encoding | `setlocale`, `mb_*` versus byte functions, legacy charsets | Multibyte text, case mapping, sort order of accented strings |
| Arrays | An ordered hash map; numeric-string keys become integers; JS objects order integer keys first | Key order in output and JSON, `"1"` versus `1` keys; use `Map` or arrays when order is semantic |
| Sorting | Older PHP sorts are unstable; comparison callbacks that return booleans instead of negative/zero/positive integers misorder silently | Ties in sorted lists, every custom comparison callback |
| Magic methods | `__get`, `__call`, `__toString` hide logic behind property access | Each class that defines them; find call sites by behavior, not by name |
| Shared state | `$GLOBALS` and `static` live for one request in PHP; a Node process serves many requests | Two interleaved requests that touch module-level state |
| Include order | `include`/`require` run code at load time | Pages whose output depends on which file loaded first |
| Error suppression | `@` hides warnings; warnings and notices become values (`false`, `null`) | Failing file, DB or array-index calls on bad input |
| MySQL non-strict mode | Implicit casts, silent truncation, zero dates | Over-length and invalid values on every write path |
| Character set | `utf8mb3` cannot store four-byte characters | Emoji round trip in each text column |

### First hazards for other common pairs

Starting points, not complete lists; walk the category table for each.

- **COBOL to Java or C#:** packed decimal (COMP-3) and fixed-point rounding versus `BigDecimal`/`decimal` scale; EBCDIC to Unicode and sort order; `REDEFINES` record layouts; implicit truncation on `MOVE`; JCL step order and condition codes as control flow.
- **Python 2 to 3:** `str` versus `bytes`; `/` on integers; `round()` changes to half-even; dict ordering assumptions; `map`/`filter` returning iterators.
- **VB6 or .NET Framework to modern .NET:** `On Error Resume Next`; array lower bounds (`Option Base`); default culture in parsing and formatting; `Variant` coercion; removed framework APIs replaced with near equivalents.
- **Java to Kotlin or Go:** nullability at the boundary; checked exceptions versus error values; integer overflow behavior; collection immutability.
- **AngularJS or jQuery to React:** two-way binding and digest-cycle timing; event order and delegated handlers; DOM-mutating plugins; global state on `window`; form submit and validation order.
- **Oracle to PostgreSQL (data layer):** empty string is NULL in Oracle; `NUMBER` precision; date types carrying time; implicit conversions in comparisons.

## Side-effect inventory and capture sink

A rewrite passes its interface tests and still breaks the business through effects nobody sees. Inventory them before the first slice:

- scheduled work: system crontab, the framework scheduler, JCL or enterprise schedulers;
- outbound: email, HTTP clients, webhooks, queue publishes, file drops to partners;
- local: file writes and uploads, cookies and headers, session writes, shutdown or finalizer hooks;
- routing: web-server rewrites and gateway rules that change which code runs.

For each stack, search the language's own calls for these (for PHP: `mail()`, `curl_*`, `header()`, `session_*`, `register_shutdown_function`, `.htaccess`). Each entry names its owner, trigger, target and whether a repeat is harmless. In shadow or dual-run mode every outbound effect of the new stack goes to a capture sink (a fake SMTP server, a recording HTTP stub, a scratch queue or directory), never to real recipients. The oracle compares captured effects with legacy's, and the cutover checklist confirms the real sender is switched exactly once.

## Spec extraction

Write a spec per route, screen, job or module before the oracle freezes. Every statement carries provenance: `file:line`, the SQL, or a log sample. Mark anything the code cannot tell you ("not derivable from code": business intent, who consumes an endpoint or file, why a rule exists) and send those items to a subject-matter expert. The expert reviews the spec before the oracle freezes; a frozen oracle built on a wrong spec makes the wrong behavior permanent.

Keep known legacy bugs in a separate list. Preserve them in the rewrite unless the spec owner decides otherwise, so a fix never hides inside a "parity" change.

## Auth and session

For a web system split across two stacks, pick one session authority before the first route moves.

- The legacy system stays the issuer at first. The new stack validates through a session endpoint the legacy app exposes, not by reading the legacy session store's serialization format.
- Test across both stacks: cookie domain and path, CSRF token flow, logout, and expiry, in both directions (log in on legacy then open a new route, and the reverse).
- Before moving identity to an identity provider, check password-hash compatibility against the current library documentation of the new stack; do not assume the legacy algorithm verifies.
- Extract auth last unless the session bridge is already proven.

## URLs and SEO

For public web pages, build the URL inventory from access logs plus the rewrite rules, so URLs that only exist through rewrites appear. Per URL, write a golden test for status code, redirect target, canonical tag, trailing-slash behavior and query-string handling. Compare legacy and new; any deliberate change is a listed redirect, not a side effect.

## Security parity

- A per-entry-point matrix of "auth required" and role, checked against both stacks.
- A CSRF rejection test on every state-changing route.
- XSS golden payloads in every field that renders whenever the templating or UI framework changes; they catch raw HTML injection.
- Grep the new data layer for raw SQL strings and review each one; the legacy bug class returns through them.

## Routing seam

The seam is where a request, job or message is sent to legacy or new. Default: put it outside both applications, so it holds no business logic and rollback is a configuration change.

| Legacy shape | Default seam | Alternative and its cost |
|---|---|---|
| Web app or API | Reverse proxy or API gateway in front of both | Framework-level rewrites in the new app (for example Next.js fallback rewrites to the legacy origin) when the frontend team owns the edge: rollback needs a deploy, and the new app becomes a single point of failure for legacy traffic |
| UI screens | Route-level split in the shell or proxy | Micro-frontend host embedding old and new screens: shared global state and styles leak between them |
| Batch job | Scheduler entry per job, switched one job at a time | Both jobs run with one writing to a scratch target until parity holds |
| Message consumer | Topic or consumer-group routing | Duplicate consumption with an idempotency key on the new side |

Framework rewrite and middleware features change between releases; read the current documentation of the framework before writing seam config.

## Translation at scale

The order matters, and each step is a gate for the next.

1. Build and prove the judge first: the oracle above, shown to fail.
2. Write a translation rulebook (how each legacy construct maps, including the pair's hazard list) and a gap inventory (constructs with no rule yet).
3. Stress-test the rulebook on one sample slice and refine it from what breaks.
4. Fan out per slice, each with its own task, gate command and file ownership.
5. Fix failures at the rule level: change the rulebook and re-run the affected slices, not each file by hand.
6. Expect regressions after merge. Keep the rollback path from the seam alive until the post-merge period is clean.

This follows the vendor's own report: Anthropic, "How Anthropic runs large-scale code migrations with Claude Code", 2026-07-16, https://claude.com/blog/ai-code-migration. It is a vendor result, not an independent measurement.

Why the judge cannot be the translating model: in "Articulate but Wrong" (arXiv 2605.21537, 2026-05-20), semantic-trap snippets drifted in 39.7% of attempts against 7.0% for controls, and in 31.7% (83/262) of drift cases the producing model endorsed its own output. That corpus is Python 2 to 3, so read it as direction for other pairs, not as their rate.

## Data

Before a read cutover:

- per-table row counts and checksums over all rows, not samples;
- timestamps compared after timezone normalisation, never skipped;
- charset and collation check on every text column;
- one writer per table at any time;
- outbox or change data capture for synchronisation, not bare dual writes (see [strangler-fig-migration.md](strangler-fig-migration.md#dual-write-strategies)).

Name the reverse-sync method (how writes made on the new stack reach the legacy database while rollback is still possible) before any write cutover. Without it, rollback loses data.

## Code-graph fallback for unsupported languages

[dev-context-code-graph](../../dev-context-code-graph/SKILL.md) produces no symbols for languages its parsers do not cover, and many legacy languages are among them (its Supported Scope lists which). For those, seam choice and blast radius from the graph are empty. Build a substitute:

1. Entry-point table: the framework's route dump, web-server rewrites plus front controllers, scheduler and JCL definitions, queue subscriptions.
2. Dependency graph: from grep over the language's include, import, copybook or autoload mechanism.
3. Table-to-file map: from SQL strings, stored-procedure calls and ORM models.

Treat the result as a lower bound. Dynamic includes, string-built calls and string-built SQL hide edges; grep the name as a string before trusting an "unused" verdict.
