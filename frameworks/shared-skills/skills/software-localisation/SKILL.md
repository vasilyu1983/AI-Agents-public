---
name: software-localisation
description: "Implements production-grade i18n/l10n for React, Vue, Angular, and Next.js with ICU format and RTL support. Use when setting up or debugging localisation."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Software Localisation

Use this skill for production web-app i18n and l10n: library choice, message catalogs, ICU usage, locale routing, translation workflow, RTL, and release gates. The goal is not just translated strings. The goal is locale-safe product behavior.

## Quick Reference

| Need | Starting Direction |
|------|--------------------|
| React or general flexibility | `i18next` / `react-i18next` |
| ICU-first catalogs | `react-intl` / FormatJS |
| Vue | `vue-i18n` |
| Angular | `@angular/localize` |
| Next.js App Router | `next-intl` |
| smaller bundle bias | Lingui |
| stronger generated wrappers | `typesafe-i18n` only when deliberate |

## When to Use This Skill

- setting up or debugging i18n in React, Vue, Angular, or Next.js
- choosing libraries and catalog strategy
- implementing ICU pluralisation, formatting, and locale detection
- adding RTL support
- configuring extraction, translation workflow, or TMS integration
- fixing missing translations, mixed-language regressions, or bad locale fallback behavior

## Route Elsewhere

- general frontend architecture -> [software-frontend](../software-frontend/SKILL.md)
- international SEO and hreflang -> `marketing-seo`
- cross-cultural UX and market adaptation -> [software-ui-ux-design](../software-ui-ux-design/SKILL.md) or `marketing-geo-localization`
- general WCAG/ARIA compliance and European Accessibility Act (EAA) readiness -> [software-accessibility](../software-accessibility/SKILL.md); this skill only covers the i18n-specific slice (lang/dir propagation, script-aware line height, IME) in `references/accessibility-i18n.md`

## When Not to Use This Skill

- The product has one locale and no committed plan to add more — don't pre-build ICU catalogs, TMS integration, or locale routing "just in case." Ship plain strings and revisit when a second locale is real.
- The ask is "translate this text" with no code, catalog, or product surface involved — that's a translation task, not a localisation-engineering task; do it directly.
- The ask is about international SEO structure (hreflang, ccTLD vs subfolder) with no i18n implementation involved -> route to `marketing-seo` instead.

---

## Workflow

1. Confirm framework, locale count, route strategy, and translation workflow.
2. Choose the library and catalog model.
3. Define locale detection and persistence order.
4. Implement ICU or equivalent message formatting correctly.
5. Add extraction, review, and missing-key controls.
6. Add RTL and visual regression coverage where needed.
7. Block release on mixed-language or unsafe fallback behavior for indexable or customer-visible routes.

## ASCII Flow

```text
Localisation task
  -> Identify platform, source-of-truth catalog, and affected locales
  -> Choose key, ICU, formatting, and fallback strategy
  -> Patch durable source, not only generated output
  -> Check missing keys, plural rules, RTL, and text expansion
  -> Run generation or validation scripts
  -> Report locale coverage and residual translation risk
```

## Library Selection Rules

| Situation | Library | Why |
|---|---|---|
| React / TypeScript, general flexibility | `i18next` + `react-i18next` | Best selector API and plugin ecosystem |
| ICU-first catalogs, FormatJS tooling already in use | `react-intl` | Tightest ICU integration; FormatJS extract/compile pipeline |
| Next.js App Router | `next-intl` | Built for RSC + App Router; automatic locale routing |
| Vue | `vue-i18n` | Framework-native; best Vue tooling integration |
| Angular | `@angular/localize` | Build-time extraction and AOT compilation |
| Smaller bundle budget | Lingui | Smallest runtime; macro-based message extraction |
| Team explicitly wants generated type wrappers | `typesafe-i18n` | Full key-type safety; high maintenance model |

Do not choose by popularity alone. Choose by routing model, extraction needs, ICU expectations, and team maintenance habits.

### ICU MessageFormat 2 (MF2): Not Yet a Default Choice

MF2 is standardized at the syntax level in Unicode's LDML spec (stabilized through LDML 47-48), which makes it tempting to treat as "the new ICU." Do not migrate production catalogs to it as of mid-2026: ICU's own reference implementations are still draft/technology-preview status, and none of react-intl/FormatJS, i18next, vue-i18n, or Lingui has shipped a production MF2 migration path, and no mainstream TMS round-trips it. Keep using MessageFormat 1 / ICU syntax (documented in `references/icu-message-format.md`) and re-check adoption status before recommending a switch — this is a common "the spec is final, so it must be safe to use" misdiagnosis.

---

## Core Rules

### Encoding and content model

- use UTF-8 end to end
- never concatenate translatable strings
- use interpolation and ICU plural or select rules instead of ad hoc formatting

### Locale routing and fallback

- locale selection should prioritize user preference, then route or URL, then cookie, then headers, then default locale
- always define a fallback locale
- never silently fall back to English on indexable non-English routes
- metadata, breadcrumbs, JSON-LD, and visible copy must stay in the same locale

### Translation workflow

- extract keys, do not hand-copy them
- keep namespace structure stable
- add translator context, glossary rules, and review gates
- hardcoded string detection and missing-key checks should run in CI

### RTL and accessibility

- use CSS logical properties
- set `dir="rtl"` where required
- test with real RTL content
- verify BiDi handling, icons, and screen-reader behavior across locales

---

## Production Gates

| Gate | Failure condition | Remediation |
|---|---|---|
| Mixed-language output | Any locale-routed page renders keys from a different locale | Missing-key CI check catches before merge |
| Missing-key bleed | Core UX or marketing route shows a key ID or raw fallback string | Extraction + catalog diff in CI pipeline |
| Machine translation on release path | MT output inserted without glossary, tone, or reviewer gate | Add human review step for all customer-visible locales |
| Locale switch drops state or breaks navigation | User changes locale and loses cart, form, or route state | Centralize locale state; separate from route/cookie |
| RTL launched without visual validation | Arabic/Hebrew/Farsi layout broken on launch | Require visual pass on one RTL locale before release |
| EU-market product ships accessible markup but only one language | Passes WCAG in English yet still fails the combined EAA + consumer-language bar in non-English EU markets | Review accessibility and localisation together for EU-facing surfaces; see `references/accessibility-i18n.md` |

## Known Traps

| Trap | Prevention |
|---|---|
| Keys drift between extraction, TMS, and runtime — fallback "works" but locale is broken | Run missing-key checks in CI; diff extraction output against TMS catalog before release |
| Visible strings translated, but validation messages / metadata / emails / JSON-LD left in English | Enumerate all locale surfaces (UI, email, SEO, legal) at project start; treat each as a separate test gate |
| String concatenation for grammar-sensitive or gendered copy | Use ICU `{count, plural, ...}` / `{gender, select, ...}`; never `"Hello " + name` |
| Only Latin-script locales tested | Require one long-string locale (de/ru) and one non-Latin (ja/ar) before "complete" |
| Locale persisted separately in route, cookie, and client state with no precedence rule | Define precedence order once: user preference > URL route > cookie > `Accept-Language` > default locale |
| Machine translation shipped without glossary or review | Require glossary, tone rules, and human review gate for all customer-visible content |
| Plural category count assumed from memory (e.g. "French is just one/other like English") | CLDR revises per-language category counts over time (French now has `one, many, other`); verify against the current CLDR plural rules chart, don't hardcode from a prior project |
| Translated content rendered as raw HTML (`v-html`, `dangerouslySetInnerHTML`, ICU HTML tags) with no CSP/Trusted Types | Real XSS advisories exist for this exact pattern in both vue-i18n (CVE-2025-53892) and Angular's i18n pipeline (CVE-2026-27970) — treat translation-file write access as privileged and pin patched library versions |

## Common Anti-Patterns

| Anti-pattern | Correct approach |
|---|---|
| English as silent fallback on locale-routed pages | Fail visibly in CI or preview when a key is missing in a non-default locale |
| Business logic encoded in translation keys | Keys represent UI text; business logic belongs in code |
| Translations split by developer convenience | Split by stable product domain and runtime loading boundary |
| CSS directional properties (`left`, `right`) patched per-view for RTL | Use CSS logical properties (`inline-start`, `inline-end`) from the start |
| Each product surface (marketing, support, product) runs separate locale logic | Centralize fallback, formatting, and detection in one shared locale layer |

## Ops Runbook

For large locale catalogs or mixed-language incidents:

- diff keys first
- translation pass second
- treat marketing and SEO locale gaps as release blockers
- chunk large locale files instead of reading them in one pass

Use [references/ops-runbook.md](references/ops-runbook.md) for the detailed triage procedure.

## Navigation

### Core references

- [references/framework-guides.md](references/framework-guides.md)
- [references/icu-message-format.md](references/icu-message-format.md)
- [references/translation-workflows.md](references/translation-workflows.md)
- [references/rtl-support.md](references/rtl-support.md)
- [references/locale-handling.md](references/locale-handling.md)
- [references/testing-i18n.md](references/testing-i18n.md)
- [references/accessibility-i18n.md](references/accessibility-i18n.md)
- [references/content-management-patterns.md](references/content-management-patterns.md)
- [references/ops-runbook.md](references/ops-runbook.md)

### Templates and data

- [assets/react-i18next-setup.md](assets/react-i18next-setup.md)
- [assets/vue-i18n-setup.md](assets/vue-i18n-setup.md)
- [assets/nextjs-i18n-setup.md](assets/nextjs-i18n-setup.md)
- [data/sources.json](data/sources.json)

### Maintenance

- `python3 scripts/check_urls.py`
- `python3 scripts/check_examples.py`

## Related Skills

- [software-frontend](../software-frontend/SKILL.md)
- `marketing-seo`
- [software-accessibility](../software-accessibility/SKILL.md)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify current library support, framework compatibility, and recommended tooling before final answers.
- Prefer official docs, package registries, and release notes for version-sensitive guidance.
- If web access is unavailable, mark version and maintenance guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

