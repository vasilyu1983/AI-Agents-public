# Design Database Search

Offline, searchable design-intelligence database: 80+ UI styles, 160 color palettes, 70+ font pairings, 160 product-type recommendations, severity-rated UX guidelines, chart-type guidance, icon recommendations, and stack-specific implementation rules for 16 frameworks. Queried via a stdlib-only Python BM25 search engine — no network, no dependencies.

Vendored from [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (MIT, © 2024 Next Level Builder). Data lives in `../data/*.csv` and `../data/stacks/*.csv`, both queryable via the BM25 engine in `../scripts/`. `../data/slides/*.csv` (slide/deck design data) and `../data/cip/*.csv` (corporate identity pack data) are also vendored from the same upstream repo but from its sibling `design-system` and `design` skills respectively — read these CSVs directly, since `scripts/core.py`'s domain config does not yet enumerate them and `scripts/search.py` cannot query them.

## Table of Contents

- [When to Use](#when-to-use)
- [Step 1: Generate a Design System](#step-1-generate-a-design-system)
- [Step 2: Persist as Master + Page Overrides](#step-2-persist-as-master--page-overrides)
- [Step 3: Domain Deep-Dives](#step-3-domain-deep-dives)
- [Step 4: Stack-Specific Guidelines](#step-4-stack-specific-guidelines)
- [Query Strategy](#query-strategy)
- [Troubleshooting Map](#troubleshooting-map)

## When to Use

| Task | Entry Point |
|------|------------|
| New project, page, or product surface | `--design-system` first, then domain searches |
| Choose style, palette, or font pairing | `--design-system`, or `--domain style|color|typography` |
| New component (modal, pricing card, chart) | `--domain style` + `--domain ux` |
| UX review / fix a UI bug | `--domain ux "<symptom keywords>"` |
| Framework-specific implementation rules | `--stack <name>` |

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
| `react` | React/Next.js performance rules | rerender, memo, bundle, suspense, waterfall |
| `web` | app-interface rules (iOS/Android/RN) | touch targets, safe areas, Dynamic Type |

## Step 4: Stack-Specific Guidelines

```bash
python3 scripts/search.py "<keyword>" --stack <stack>
```

Available stacks: `react`, `nextjs`, `vue`, `nuxtjs`, `nuxt-ui`, `svelte`, `astro`, `angular`, `swiftui`, `react-native`, `flutter`, `jetpack-compose`, `html-tailwind`, `shadcn`, `threejs`, `laravel`. Each returns severity-rated do/don't rows with good/bad code examples and docs URLs.

## Query Strategy

- Combine product + industry + tone + density: `"entertainment social vibrant content-dense"`, not `"app"`.
- If results miss, re-query with synonyms: `"playful neon"` → `"vibrant dark"` → `"content-first minimal"`.
- `--design-system` first for the full recommendation, then `--domain` to deep-dive any single dimension.
- Always finish implementation planning with one `--stack` query for the target framework.
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
| Performance / jank | `--domain ux "virtualize main-thread debounce"` or `--domain react` |

Before delivery, run `--domain ux "animation accessibility z-index loading"` as a final validation pass and review [ui-quality-priority-rules.md](ui-quality-priority-rules.md) priorities 1–3.
