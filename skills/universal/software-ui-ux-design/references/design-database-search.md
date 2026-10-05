# Design Database Search

Offline, searchable design-intelligence database: 80+ UI styles, 190+ color palettes, 70+ font pairings, 190+ product-type recommendations, severity-rated UX guidelines, chart-type guidance, and icon recommendations (count the CSV rows rather than trusting these figures after a re-sync). Queried via a stdlib-only Python BM25 search engine — no network, no dependencies.

Vendored from [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (MIT, © 2024 Next Level Builder). Data lives in `../data/*.csv`, queryable via the BM25 engine in `../scripts/`. The upstream per-framework stack CSVs, React performance rules, slide-deck data and corporate-identity data are deliberately not vendored: framework implementation rules belong to [software-frontend](../../software-frontend/SKILL.md) and [software-mobile](../../software-mobile/SKILL.md), deck design to [deck-narrative-and-visual-patterns.md](../../document-pptx/references/deck-narrative-and-visual-patterns.md), and identity packs to corporate-identity-pack.md.

## Table of Contents

- [When to Use](#when-to-use)
- [Step 1: Generate a Design System](#step-1-generate-a-design-system)
- [Step 2: Persist as Master + Page Overrides](#step-2-persist-as-master--page-overrides)
- [Step 3: Domain Deep-Dives](#step-3-domain-deep-dives)
- [Query Strategy](#query-strategy)
- [Troubleshooting Map](#troubleshooting-map)
- [Scripts and Data Files](#scripts-and-data-files)

## When to Use

| Task | Entry Point |
|------|------------|
| New project, page, or product surface | `--design-system` first, then domain searches |
| Choose style, palette, or font pairing | `--design-system`, or `--domain style|color|typography` |
| New component (modal, pricing card, chart) | `--domain style` + `--domain ux` |
| UX review / fix a UI bug | `--domain ux "<symptom keywords>"` |
| Framework-specific implementation rules | [software-frontend](../../software-frontend/SKILL.md) or [software-mobile](../../software-mobile/SKILL.md), not this database |

All commands run from the skill root:

```bash
python3 scripts/search.py "<query>" [options]
```

## Step 1: Generate a Design System

Always start a new surface with `--design-system`. It searches product, style, color, landing, and typography domains in parallel, applies decision rules from `ui-reasoning.csv`, and returns a complete recommendation — pattern, style, palette, typography, effects, plus anti-patterns to avoid.

```bash
python3 scripts/search.py "fintech saas dashboard" --design-system -p "Acme Pay"
python3 scripts/search.py "beauty spa wellness" --design-system -f markdown   # markdown output for docs
```

## Step 2: Persist as Master + Page Overrides

Add `--persist` to write the design system to disk for cross-session retrieval:

```bash
python3 scripts/search.py "<query>" --design-system --persist -p "Project" [--page "dashboard"]
```

This creates `design-system/MASTER.md` (global source of truth) and optionally `design-system/pages/<page>.md` (page-specific deviations). Retrieval rule when building a page: read MASTER.md, check `pages/<page>.md`; if the page file exists its rules override Master.

This is the same master-plus-overrides pattern used for repo memory hierarchies: one global contract, narrow scoped exceptions, never a blended copy.

Add `--format designmd` to also emit [DESIGN.md](https://github.com/google-labs-code/design.md) (Apache-2.0) — a portable YAML-front-matter + markdown format kept at the project root. Do not assume an agent loads it automatically; reference it from the agent's instruction file (for example CLAUDE.md or AGENTS.md) and check each tool's docs for what it reads. Combine with `--persist` to write `DESIGN.md` at `--output-dir` (default: cwd) alongside the usual `design-system/MASTER.md`; without `--persist` it prints to stdout. Fields the CSV database can't populate (spacing scale, corner-radius tokens, full typography scale) are declared under the spec's `omitted` front-matter key rather than invented.

```bash
python3 scripts/search.py "<query>" --design-system --format designmd
python3 scripts/search.py "<query>" --design-system --format designmd --persist -p "Project"
```

## Step 3: Domain Deep-Dives

```bash
python3 scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

| Domain | Use For | Example Keywords |
|--------|---------|------------------|
| `product` | product-type recommendations | saas, e-commerce, portfolio, healthcare, fintech |
| `style` | UI styles, effects, AI prompt keywords | glassmorphism, minimalism, brutalism, dark mode |
| `color` | shadcn-style semantic palettes by product type | saas, ecommerce, healthcare, beauty |
| `typography` | curated font pairings with CSS/Tailwind config | elegant, playful, professional, modern |
| `google-fonts` | individual Google Fonts lookup (1900+ fonts) | sans serif, variable, japanese, popular |
| `landing` | page section order, CTA placement, conversion strategy | hero, social-proof, pricing, testimonial |
| `chart` | chart type selection with a11y grades and library picks | trend, comparison, funnel, real-time |
| `ux` | severity-rated do/don't guidelines with code examples | animation, accessibility, z-index, loading |
| `icons` | icon recommendations with import code | navigation, settings, commerce |
| `web` | app-interface rules (iOS/Android/RN) | touch targets, safe areas, Dynamic Type |

## Query Strategy

- Combine product + industry + tone + density: `"entertainment social vibrant content-dense"`, not `"app"`.
- If results miss, re-query with synonyms: `"playful neon"` → `"vibrant dark"` → `"content-first minimal"`.
- `--design-system` first for the full recommendation, then `--domain` to deep-dive any single dimension.
- Hand implementation planning to the framework skill ([software-frontend](../../software-frontend/SKILL.md), [software-mobile](../../software-mobile/SKILL.md)); this database stops at design decisions.
- BM25 ignores words of ≤2 characters; prefer specific multi-word queries over single generic terms.

## Troubleshooting Map

| Problem | Query |
|---------|-------|
| Can't decide style/color | re-run `--design-system` with different keyword mix |
| Dark mode contrast issues | `--domain ux "dark mode contrast"` |
| Animations feel unnatural | `--domain ux "easing spring duration"` |
| Form UX is poor | `--domain ux "validation error focus"` |
| Navigation feels confusing | `--domain ux "navigation hierarchy back"` |
| Layout breaks on small screens | `--domain ux "mobile breakpoint responsive"` |
| Performance / jank | `--domain ux "virtualize main-thread debounce"`; React/Next.js rendering and bundle issues go to [performance-optimization.md](../../software-frontend/references/performance-optimization.md) |

Before delivery, run `--domain ux "animation accessibility z-index loading"` as a final validation pass and review [ui-quality-priority-rules.md](ui-quality-priority-rules.md) priorities 1–3.

## Scripts and Data Files

Offline design-database search engine (stdlib-only Python, vendored from [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), MIT)

> **Upstream trust note:** that repo's star count is far out of proportion to its watchers, contributors, and age — a star-inflation signature. This says nothing about the vendored content, which was taken on merit and is unaffected. It does mean: never cite its star count as social proof, and re-diff before pulling any upstream update.

- `../scripts/search.py` — CLI: `--design-system`, `--domain <domain>`, `--persist`, `--format designmd` (exports the generated design system as a spec-conformant `DESIGN.md` — Google Labs' Apache-2.0 portable design-context format; coding agents do not load it automatically (Claude Code reads CLAUDE.md/AGENTS.md and `.claude/rules/`), so reference it from the agent's instruction file)
- `../scripts/core.py` — BM25 engine and CSV domain config
- `../scripts/contrast_check.py` — WCAG contrast calculator (single pair, stdin batch, or tokens×surfaces cross product); the only accepted source for contrast numbers in a spec
- `../scripts/design_system.py` — design-system generation and Master + page-overrides persistence
- `../data/*.csv` — style, color, typography, Google Fonts, product, landing, chart, UX-guideline, app-interface, icon, motion and UI-reasoning databases
