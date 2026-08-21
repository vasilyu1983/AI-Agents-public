# research-scout — Learnings

## Patterns That Work

- [2026-08-12] Before adjudicating a tension between a new rule and an established framework, read that framework's own scope statement: C4's FAQ self-scopes to static structure and prescribes supplements, settling by primary source.
- [2026-05-30] If both ideas already have same-day per-claim-graded evidence, the right mode is PACKAGE (Steps 3/5c/6), not a fresh SEARCH. Prove no source was invented in packaging via comm -23 (packaged URLs subset of source-doc URLs).
- [2026-05-30] The two-plus source-family corroboration gate earned its keep; it correctly capped a strong single-channel founder-revenue claim (Cupidly 4,967/mo from one X post) at validate not promote.
- [2026-05-17] Skill-uplift: give workers a parent-verified fact packet + verify-or-hedge mandate for non-packet dates; they then hedge volatile facts instead of asserting them, closing gaps without propagating over-claims.
- [2026-05-17] May-2026 closed-loop skill-memory consensus = hook auto-capture + scheduled dreaming-style consolidation + eval-gated promotion, reviewing hard cases only; port the shape, treat vendor 'Nx' and RL controllers as traps.
- [2026-05-17] Marketing-skill audits fail on SOTA currency not build maturity (~2-week platform-churn half-life); dual-axis scoring (build rank vs SOTA currency) revealed worst-built = most-stale skill, invisible under one score.
- [2026-05-17] [2026-05-17] Verify-or-hedge must apply to the parent's 'verified-facts packet' too: a worker's mandated WebFetch caught a wrong packet fact (Anthropic /mnt/memory/+Dreaming) before it propagated skill-wide.
- [2026-05-17] [2026-05-17] Multi-skill maturity audits need a parent verification+synthesis pass: cross-cutting model-launch facts (Opus 4.7 tokenizer change) hit many skills but belong to no single one, so blind per-skill workers miss them.
- [2026-05-17] Coding-agent-runtime skill-maturity audits: corroborate completeness against arXiv harness papers (OpenDev 2603.05344, AHE 2604.25850), not only community runtime posts — AHE exposes the harness-self-evolution gap static eval skills miss.
- [2026-05-17] For skill-uplift scans, give each per-skill worker its existing sources.json as a do-not-re-pitch baseline and treat cross-worker corroboration (same arXiv ID from two blind workers) as the top promote signal.
- [2026-05-17] A blind worker's REFUSAL to cite a parent-supplied anchor benchmark is itself a verification signal — treat it as a contradiction flag. Parent anchor "AI SDR 42x ROI / 24.7 mtgs/mo" was vendor-inflated (Landbase/Qualified marketing); the GTM worker conspicuously declined to adopt it, and an independent check (Pavilion GTM Benchmarks 2026) put the real figure at ~8:1 ROI with hybrid pods beating AI-only. Re-verify any parent-packet fact a worker pointedly won't repeat.
- [2026-05-17] Foundations-skill maturity audits: scan workers near-universally recommend "seed N learnings entries" to 'activate' an empty learnings loop as a P0/P1 — applying this fabricates field-use evidence that never happened (fail-loud violation). Parent must inject a standing override into every uplift worker (fix scaffold only, never invent entries); 14/15 workers proposed seeding, override held in all 14.
## Mistakes to Avoid

- [2026-08-17] Vendored CSVs can carry deliberate local edits (ui-ux-design colors.csv WCAG notes vs upstream ui-ux-pro-max): upstream sync must be row-level merge, never overwrite.
- [2026-08-17] Anonymous raw.githubusercontent.com 429s fast on multi-file drift checks; fetch via gh api -H 'Accept: application/vnd.github.raw' instead.
- [2026-08-12] Ranking skills by diagram-term density needs a homonym filter first: 'C4' matched the Colossal Clean Crawled Corpus in 4 AI skills but the C4 architecture model in only 2 — raw 'rg -c' ranked the dataset skills above the real consumers.
- [2026-07-11] A 4-week-old sweep still had wrong facts (OpenAlex mandate date, Elicit's repriced tiers, ResearchRabbit's acquisition year); verify dates against primary announcements, never cite tool pricing without a re-verification date.
- [2026-05-30] Tag manufactured demand before grading virality; revenue driven by a paid ad or quiz-funnel (Coursiv) is ad-spend not product-market pull and must not score as organic virality.
- [2026-05-29] iOS-opportunity scans must check incumbent M&A, not just complaint density: ranked 'AI photo-calorie' as a fresh wedge, but MyFitnessPal had already acquired Cal AI (Mar 2026) — the killer feature was already consolidated.
- [2026-05-17] Shared skills can ship operator-supplied real PII (a project-scoped skill shipped real org names/emails/org-chart in data/*.json); gitignore the real file, commit only synthetic *.example.json templates.
- [2026-05-17] 'git rm --cached' only durably untracks a file if a matching .gitignore rule exists first; otherwise the next 'git add -A' re-tracks it.
- [2026-05-17] Under a concurrent multi-agent 'git add -A' sweep, commit only via path-scoped 'git add <paths> && git commit -m MSG -- <paths>'; a bare add entangles unrelated sweep edits or gets staged changes reverted.
- [2026-05-17] Link-integrity probes must resolve paths relative to the containing file: a basename regex flagged valid cross-skill links (../other-skill/references/*) as dead by checking the local references/ dir.
- [2026-05-17] sources.json health probes must be schema-agnostic: a flat sources[] key lookup reports domain-keyed schemas (keys like kubernetes/iac/cicd) as 'empty', producing a false no-provenance finding. Parse all dict values, not one key.
- [2026-05-17] Worker over-claims run both ways: one called a real current URL 'fabricated' (React 19.2); another asserted an unverified mandate (Android API-36). Parent must verify pessimistic data-integrity claims too, not just optimistic versions.
- [2026-05-17] Standards-body audits: workers cite RETIRED spec pages as current (SLSA v1.0 'Retired' quoted as live; actual v1.2). Parent must re-fetch the spec's version banner and rewrite to the current-version URL.
- [2026-05-17] Scan workers over-claim version/compat facts; re-verify every load-bearing version or contradiction claim against primary sources and write the accurate partial form, never the worker's blanket claim.
## Domain Knowledge

- [2026-08-17] 'UI UX Max Pro' users mention = nextlevelbuilder/ui-ux-pro-max-skill; try name permutations before reporting a source link missing.
- [2026-06-11] May 2026 EU Digital Omnibus postponed AI Act Annex III high-risk deployer obligations from 2026-08-02 to 2027-12-02 (provisional, formal adoption ~mid-2026); any skill citing the August 2026 date is stale.
- [2026-05-30] Award and editorial signals (Apple Design Awards) prove distribution via near-zero-CAC featuring but not ROI; grade them on a separate axis from revenue and never conflate the two.
- [2026-05-17] zsh does not word-split unquoted $VAR (unlike bash); multi-path git commands must list paths literally or use an array, or git sees one giant pathspec.
## Open Questions

## Consolidated Principles

- [2026-08-08] Cross-domain sources may promote individual mechanisms while the combined product hypothesis stays at validate; component evidence does not establish event order, durable retention, or revenue.
