---
name: software-localisation
description: "Implements production-grade i18n/l10n for React, Vue, Angular, and Next.js with ICU format and RTL support. Use when setting up or debugging localisation."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# Software Localisation

Use this skill for production web-app i18n and l10n: library choice, message catalogs, ICU usage, locale routing, translation workflow, RTL, and release gates. The goal is not just translated strings. The goal is locale-safe product behavior.

## When to Use This Skill

- setting up or debugging i18n in React, Vue, Angular, or Next.js
- choosing libraries and catalog strategy
- implementing ICU pluralisation, formatting, and locale detection
- adding RTL support
- configuring extraction, translation workflow, or TMS integration
- fixing missing translations, mixed-language regressions, or bad locale fallback behavior
- delivering backend-generated prose (AI summaries, narratives) to localized web or native clients

## Route Elsewhere

- general frontend architecture -> [software-frontend](../software-frontend/SKILL.md)
- international SEO and hreflang -> `marketing-seo`
- cross-cultural UX and market adaptation -> [software-ui-ux-design](../software-ui-ux-design/SKILL.md) or `marketing-geo-localization`
- general WCAG/ARIA compliance and European Accessibility Act (EAA) readiness -> [software-accessibility](../software-accessibility/SKILL.md); this skill only covers the i18n-specific slice (lang/dir propagation, script-aware line height, IME) in `references/accessibility-i18n.md`

## When Not to Use This Skill

- The product has one locale and no committed plan to add more — don't pre-build ICU catalogs, TMS integration, or locale routing "just in case." Ship plain strings and revisit when a second locale is real.
- The ask is "translate this text" with no code, catalog, or product surface involved — that's a translation task, not a localisation-engineering task; do it directly.
- The ask is about international SEO structure (hreflang, ccTLD vs subfolder) with no i18n implementation involved -> route to `marketing-seo` instead.

### Native Mobile Boundary

This skill owns strings, plurals, catalogs, and the translation pipeline for native apps as well as web, including backend-generated prose and catalog key/value parity: see [references/backend-generated-content-i18n.md](references/backend-generated-content-i18n.md). Framework setup here is web-first; the platform APIs belong to [software-ios-native](../software-ios-native/SKILL.md), [software-android-native](../software-android-native/SKILL.md), or [software-mobile](../software-mobile/SKILL.md). Anchors to check there:

- iOS: String Catalogs (`Localizable.xcstrings`); plurals via the editor's "Vary by Plural", which adds each language's CLDR plural forms.
- Android: per-app language preference (Android 13 / API 33+) via `AppCompatDelegate.setApplicationLocales(LocaleListCompat.forLanguageTags(...))` (backward-compatible) or `LocaleManager`; declare locales with `android:localeConfig`, or `androidResources { generateLocaleConfig = true }` (AGP 8.1+).

---

## Workflow

1. Confirm framework, locale count, route strategy, and translation workflow.
2. Choose the library and catalog model.
3. Define explicit-route resolution separately from first-entry locale negotiation and persistence.
4. Implement ICU or equivalent message formatting correctly.
5. Add extraction, missing-key, and stale-translation controls ([missing key detection](references/translation-workflows.md#missing-key-detection)); for LLM/MT drafts, enforce the ICU-AST, glossary, quality-estimation, and reviewer gates in [references/translation-workflows.md](references/translation-workflows.md#ai-powered-translation).
6. Add RTL and visual regression coverage where needed; see [references/testing-i18n.md](references/testing-i18n.md) for pseudo-localisation, RTL automation, and pluralisation edge-case test patterns.
7. Block release on mixed-language or unsafe fallback behavior for indexable or customer-visible routes.

## Quick Reference

| Situation | Library | Why |
|---|---|---|
| React / TypeScript, general flexibility | `i18next` + `react-i18next` | Selector typing when enabled; plugin integration |
| ICU-first catalogs, FormatJS tooling already in use | `react-intl` | ICU catalogs with FormatJS extract/compile |
| Next.js App Router | `next-intl` | Built for RSC + App Router; configured locale routing |
| Vue | `vue-i18n` | Framework-native; Vue tooling integration |
| Angular | `@angular/localize` | Build-time extraction and AOT compilation |
| Smaller bundle budget | Lingui | Macro extraction; measure the shipped bundle |
| Team explicitly wants generated type wrappers | `typesafe-i18n` | Full key-type safety; high maintenance model |

Do not choose by popularity alone. Choose by routing model, extraction needs, ICU expectations, and team maintenance habits. For setup steps per framework, see [references/framework-guides.md](references/framework-guides.md).

### ICU MessageFormat 2 (MF2): Not Yet a Default Choice

MF2 is standardized at the syntax level in Unicode's LDML spec (Stable since CLDR/LDML 47, March 2025), which makes it tempting to treat as "the new ICU." Do not migrate production catalogs to it until the toolchain catches up: check whether ICU's own implementations have left draft/technology-preview status, whether your library (react-intl/FormatJS, i18next, vue-i18n, Lingui) ships a production MF2 path, and whether your TMS round-trips it. Keep using MessageFormat 1 / ICU syntax (documented in `references/icu-message-format.md`) and re-check adoption status before recommending a switch — this is a common "the spec is final, so it must be safe to use" misdiagnosis.

---

## Core Rules

### Encoding and content model

- use UTF-8 end to end
- never concatenate translatable strings
- use interpolation and ICU plural or select rules instead of ad hoc formatting

### Locale routing and fallback

- an explicit locale in a valid URL or deep link wins for that request; preserve it through navigation and canonical metadata (see [references/locale-handling.md](references/locale-handling.md) for date/number/currency detection specifics)
- when no explicit locale is present, negotiate from authenticated preference, persisted choice, supported `Accept-Language`, then default locale
- a stored preference may redirect an unlocalized entry route, but must not silently rewrite a shared explicit-locale URL
- always define a fallback locale
- never silently fall back to English on indexable non-English routes
- metadata, breadcrumbs, JSON-LD, and visible copy must stay in the same locale

### Translation workflow

- extract keys, do not hand-copy them
- keep namespace structure stable
- add translator context, glossary rules, and review gates; see [references/translation-workflows.md](references/translation-workflows.md) for extraction/TMS/CI pipeline patterns and [references/content-management-patterns.md](references/content-management-patterns.md) for TM, glossary, and cost-at-scale patterns
- hardcoded string detection and missing-key checks should run in CI

### RTL and accessibility

- use CSS logical properties
- set `dir="rtl"` where required
- test with real RTL content; see [references/rtl-support.md](references/rtl-support.md) for Arabic/Hebrew/Farsi-specific patterns
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
| Localized accessibility regression | Locale changes break language/direction markup, script rendering, or text input | Test the i18n accessibility slice in `references/accessibility-i18n.md`; route legal applicability to the accessibility owner |

## Known Traps

| Trap | Prevention |
|---|---|
| Keys drift between extraction, TMS, and runtime — fallback "works" but locale is broken | Run missing-key checks in CI; diff extraction output against TMS catalog before release |
| Visible strings translated, but validation messages / metadata / emails / JSON-LD left in English | Enumerate all locale surfaces (UI, email, SEO, legal) at project start; treat each as a separate test gate |
| String concatenation for grammar-sensitive or gendered copy | Use ICU `{count, plural, ...}` / `{gender, select, ...}` (or the library's own plural syntax, e.g. vue-i18n pipe plurals); never `"Hello " + name` |
| Only Latin-script locales tested | Require one long-string locale (de/ru) and one non-Latin (ja/ar) before "complete" |
| Locale persisted separately in route, cookie, and client state with no precedence rule | Separate resolution rules: explicit URL/deep-link locale for the request; otherwise authenticated preference > persisted choice > supported `Accept-Language` > default |
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
- [references/backend-generated-content-i18n.md](references/backend-generated-content-i18n.md) — backend-generated prose for localized clients (generate-in-locale vs translate-after-cache), locale contract, native catalog parity

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

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
