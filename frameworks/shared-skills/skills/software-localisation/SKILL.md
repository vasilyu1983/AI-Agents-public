---
name: software-localisation
description: Production-grade i18n/l10n patterns for React, Vue, Angular, Next.js, and Node.js. Covers library selection (i18next/react-i18next, FormatJS/react-intl, next-intl, vue-i18n, @angular/localize, Lingui, typesafe-i18n), ICU message format, RTL support, locale routing/detection, TMS integration, string extraction, and CI/CD translation workflows. Use when setting up or debugging localisation in a codebase.
---

# Software Localisation - Quick Reference

Production patterns for internationalisation (i18n) and localisation (l10n) in modern web applications. Covers library selection, translation management, ICU message format, RTL support, and CI/CD workflows.

**Snapshot (2026-02)**: i18next 25.x, react-i18next 16.x, react-intl 8.x, vue-i18n 11.x, next-intl 4.x, @angular/localize 21.x. Always verify current versions in the target repo (see Currency Check Protocol).

**Authoritative References**:
- [i18next Documentation](https://www.i18next.com/)
- [FormatJS/react-intl](https://formatjs.github.io/)
- [ICU Message Format](https://unicode-org.github.io/icu/userguide/format_parse/messages/)
- [MDN Intl API](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl)

## Quick Reference

| Task | Tool/Library | Command | When to Use |
|------|--------------|---------|-------------|
| React i18n | react-i18next | `npm i i18next react-i18next` | Most React apps, flexibility |
| React i18n (ICU) | react-intl (FormatJS) | `npm i react-intl` | ICU-first message catalog + tooling |
| Vue i18n | vue-i18n | `npm i vue-i18n` | Vue 3 apps |
| Angular i18n | @angular/localize | `ng add @angular/localize` | Angular apps |
| Next.js i18n | next-intl | `npm i next-intl` | Next.js App Router |
| Minimal bundle | LinguiJS | `npm i @lingui/core @lingui/react` | Bundle size critical |
| Type-safe | typesafe-i18n | `npm i typesafe-i18n` | TypeScript-first projects |
| String extraction | i18next-parser | `npx i18next-parser` | Extract keys from code |
| ICU linting | @formatjs/cli | `npx formatjs extract` | Validate ICU messages |

## Decision Tree: Library Selection

```text
Project requirements:
    │
    ├─ React/Next.js project?
    │   ├─ ICU-first message catalogs + FormatJS tooling?
    │   │   └─ react-intl (FormatJS)
    │   │
    │   ├─ Flexibility, plugins, lazy loading?
    │   │   └─ react-i18next
    │   │
    │   ├─ Bundle size critical?
    │   │   └─ LinguiJS (ICU syntax)
    │   │
    │   └─ TypeScript-first, compile-time safety?
    │       └─ typesafe-i18n
    │
    ├─ Vue/Nuxt project?
    │   └─ vue-i18n (Composition API)
    │
    ├─ Angular project?
    │   ├─ Built-in solution preferred?
    │   │   └─ @angular/localize (first-party, AOT support)
    │   │
    │   └─ Need i18next ecosystem?
    │       └─ angular-i18next (wrapper)
    │
    └─ Framework-agnostic / Node.js?
        └─ i18next core (works everywhere)
```

## Library Comparison

| Library | ICU Support | Lazy Loading | TypeScript | Best For |
|---------|-------------|--------------|------------|----------|
| react-i18next | Plugin/optional | Native | Good | Flexible, popular React choice |
| react-intl | Native | Manual | Good | ICU-first catalogs + tooling |
| LinguiJS | Native | Native | Excellent | Bundle-conscious apps |
| typesafe-i18n | Limited | Manual | Excellent | Compile-time key safety |
| vue-i18n | Native | Native | Good | Vue 3 apps |
| @angular/localize | Native | AOT | Native | Angular apps |

## Core Concepts

### Character Encoding (Critical)

**Always use UTF-8** across your entire stack to prevent text corruption:

```text
PASS Required: UTF-8 everywhere
- Database: utf8mb4 (MySQL) or UTF-8 (PostgreSQL)
- HTML: <meta charset="UTF-8">
- HTTP headers: Content-Type: text/html; charset=utf-8
- File encoding: Save all source files as UTF-8
- API responses: JSON with UTF-8 encoding
```

UTF-8 supports all Unicode characters including emojis, mathematical symbols, and all language scripts. Inconsistent encoding causes: corrupted characters (�), failed searches for accented names, and rejected international input.

### Translation Key Patterns

```typescript
// Flat keys (simple)
"welcome": "Welcome to our app"
"user.greeting": "Hello, {name}"

// Nested keys (organised)
{
  "user": {
    "greeting": "Hello, {name}",
    "profile": {
      "title": "Your Profile"
    }
  }
}

// Namespace separation (scalable)
// common.json, auth.json, dashboard.json
```

### ICU Message Format Essentials

```text
// Simple interpolation
"Hello, {name}!"

// Pluralisation
"{count, plural, one {# item} other {# items}}"

// Select (gender, category)
"{gender, select, male {He} female {She} other {They}} liked your post"

// Number formatting
"Price: {price, number, currency}"

// Date formatting
"Posted: {date, date, medium}"
```

### Locale Detection Strategy

```text
Priority order:
1. User preference (stored in profile/localStorage)
2. URL parameter or path (/en/about, ?lang=de)
3. Cookie (NEXT_LOCALE, i18next)
4. Accept-Language header
5. Default locale fallback
```

## Locale Quality Gates (SEO/AEO-Safe)

Use these gates for locale-routed, indexable pages (for example `/vi/*`, `/de/*`):

- Do not ship mixed-language content on a single locale route.
- Do not silently fall back to English for indexable page content.
- Keep metadata, breadcrumbs, and JSON-LD in the same locale as visible content.
- Prefer explicit missing-key handling in CI over runtime fallback in production SEO pages.
- If fallback is unavoidable, use locale-safe neutral copy and track missing keys.

### Missing Translation Decision Rule

- Marketing/SEO pages: block publish or replace with locale-safe copy; never inject English fragments.
- Product UI (non-indexed surfaces): fallback is acceptable with telemetry and follow-up fix.

## EN/RU Mixed-Language Regression Protocol

Use this when users report locale mixing (for example RU screens showing EN fragments).

### 1) Key-Parity Diff (Base vs Target Locale)

Compare key sets between source and target locale files; treat missing keys as release blockers on user-facing pages.

```bash
jq -r 'paths(scalars) | join(".")' app/src/messages/en/*.json | sort -u > /tmp/en.keys
jq -r 'paths(scalars) | join(".")' app/src/messages/ru/*.json | sort -u > /tmp/ru.keys
comm -23 /tmp/en.keys /tmp/ru.keys   # present in EN, missing in RU
```

### 2) Hardcoded-String Sweep in UI

Search for user-visible literals in components/pages that should use i18n keys.

```bash
rg -n '>[A-Za-z][^<]{2,}<' app/src -g '*.tsx'
rg -n '"[A-Za-z][^"]{2,}"' app/src -g '*.tsx' -g '*.ts'
```

### 3) Route-Level Locale Smoke Check

For target locale routes, verify rendered text is consistently localized and no fallback EN fragments appear in critical UI regions.

### 4) Engine Text Audit

Ensure computed/engine-driven messages (not just static labels) pass through translation mapping instead of returning raw EN strings.

### 5) CI Gate

Add a lightweight gate that fails when:
- required target-locale keys are missing,
- newly added UI literals bypass the i18n layer,
- locale-routed smoke pages include mixed-language sentinel terms.

### Runtime Constraint Note

If an agent runtime has no external translation connector, do not block on auto-translation tools. Enforce key completeness + placeholder strategy, then backfill approved translations in a separate tracked pass.

## Engine Output i18n (`_i18n` Metadata Pattern)

Server-generated engine content (astrology calculations, ML outputs, computed reports) needs localisation without making the engine locale-aware.

### Pattern

- Engine attaches `_i18n: { key: "transits.neptune_trine.description", params: { planet: "Neptune" } }` alongside the English string
- Client resolves: `_i18n ? t(_i18n.key, _i18n.params) : englishFallback`
- Backward-compatible: old cached responses without `_i18n` gracefully degrade to English
- Server caches once; every locale resolves on the client
- Use `t.has(key)` before `t(key)` for graceful fallback

| Pattern | Status | Why |
|---------|--------|-----|
| `{ text: "Neptune trine Jupiter", _i18n: { key: "transits.neptune_trine", params: { p1: "Neptune", p2: "Jupiter" } } }` | PASS | Client resolves per locale; server caches once |
| `{ text_en: "...", text_ru: "...", text_de: "..." }` | FAIL | Server bloat, cache per locale |
| `t(meaning.theme)` | FAIL | Using raw engine output as translation key |
| `t.has('meanings.4.theme') ? t('meanings.4.theme') : meaning.theme` | PASS | Graceful fallback when key missing |

## Locale Key Design Anti-Patterns

### "1 Field, N Slots"

Using one locale key for multiple distinct UI purposes. Each UI slot (badge, card title, modal description, affirmation) needs its own semantically distinct key, even if the English text happens to be similar.

| Pattern | Status | Why |
|---------|--------|-----|
| `meanings.4.advice` used for karmic debt, life path, birthday guidance, and advanced cycles (same text 6x) | FAIL | Coupling breaks when any slot needs a different translation |
| `meanings.4.advice`, `karmicDebt.4.lifeLesson`, `lifePath.4.affirmation`, `birthday.4.guidance` | PASS | Distinct keys per slot — independent translation |

### Short vs. Long Variants

Plan for both from the start.

| Pattern | Status | Why |
|---------|--------|-----|
| `nodeGrowth` (full: "North Node — growth and new beginnings") + `nodeGrowthShort` (badge: "Growth") | PASS | Each UI context gets appropriate length |
| Single `nodeGrowth` key that's too long for badge UI, requires substring hacks | FAIL | Substring breaks in non-English locales |

### Static Key Maps over String Transforms

When API output format doesn't match locale key naming, use a hardcoded map instead of string manipulation.

```typescript
// PASS: Explicit map — handles all edge cases
const PHASE_TO_KEY: Record<string, string> = {
  "New Moon": "new", "Waxing Crescent": "waxingCrescent",
  "First Quarter": "firstQuarter", "Full Moon": "full"
};

// FAIL: String transform — breaks on "New Moon" → "newMoon" vs actual key "new"
const key = phaseName.replace(/\s+/g, '').replace(/^./, c => c.toLowerCase());
```

## Machine Translation Quality Gates

Short, domain-specific terms trip up automated MT. Known examples:

| Locale | Expected | MT Output | Term |
|--------|----------|-----------|------|
| Arabic | `أرض` (earth as element) | `أذن` (ear) | "earth" |
| Japanese | `火` (fire as element) | `樅` (fir tree) | "fire" |
| Hindi | `भू` (earth) | `कान` (ear) | "earth" |

### Rules

1. Maintain a curated dictionary of domain terms (zodiac signs, elements, planetary names, astronomical terms) per locale
2. Never auto-translate terms shorter than 3 words without dictionary lookup
3. Post-MT audit: grep for known bad translations (compile a blocklist per locale)
4. For new locales, translate domain terms first, then use them as glossary constraints for MT

## Locale Propagation Protocol

Every commit adding EN keys MUST propagate to all target locales. This is the #1 recurring i18n bug — hit in 4+ independent sessions.

### Steps

1. **Before commit**: diff EN locale files against target locales for missing keys
2. **Script-based propagation**: inject missing keys from EN into all other locales with EN fallback values
3. **CI gate**: fail builds when target locale files have fewer keys than EN (configurable threshold)
4. **Pre-commit hook** (optional): auto-run propagation script on staged locale files

### Quick Key-Parity Check

```bash
jq -r 'paths(scalars) | join(".")' messages/en/*.json | sort -u > /tmp/en.keys
for locale in ar de es fr hi it ja ko pt-BR ru tr vi zh; do
  jq -r 'paths(scalars) | join(".")' messages/$locale/*.json | sort -u > /tmp/$locale.keys
  echo "=== $locale missing ==="
  comm -23 /tmp/en.keys /tmp/$locale.keys | head -20
done
```

### Batch Translation Approach

Find all gaps first (diff-based), then translate systematically file-by-file. One-at-a-time discovery is 5x slower than batching:

1. Run key-parity check across all locales to produce the full gap list
2. Group missing keys by namespace/file
3. Translate one file at a time for each locale, using existing translations as glossary context
4. Verify parity after the batch completes

## Duplicate JSON Key Detection

Large hand-edited JSON locale files can have duplicate keys. Per JSON spec, last-writer-wins — keys are silently dropped.

### CI Check

```bash
# Detect duplicate keys in JSON locale files
node -e "
const fs = require('fs');
const file = process.argv[1];
const text = fs.readFileSync(file, 'utf8');
const keys = [];
JSON.parse(text, (key, value) => { if (key) keys.push(key); return value; });
const dupes = keys.filter((k, i) => keys.indexOf(k) !== i);
if (dupes.length) { console.error('DUPLICATE KEYS in', file, ':', [...new Set(dupes)]); process.exit(1); }
" "$FILE"
```

Run this on every locale file in CI to catch silent key collisions before they reach production.

## Navigation

### Resources (Deep Dives)

- [references/framework-guides.md](references/framework-guides.md) - React, Vue, Angular, Next.js implementation
- [references/icu-message-format.md](references/icu-message-format.md) - Pluralisation, select, formatting
- [references/translation-workflows.md](references/translation-workflows.md) - TMS, CI/CD, string extraction
- [references/rtl-support.md](references/rtl-support.md) - Right-to-left language support
- [references/locale-handling.md](references/locale-handling.md) - Dates, numbers, currencies
- [references/testing-i18n.md](references/testing-i18n.md) - Pseudo-localisation, visual regression, plural testing, missing translation CI detection
- [references/accessibility-i18n.md](references/accessibility-i18n.md) - Screen readers across languages, ARIA in multilingual contexts, BiDi accessibility, IME
- [references/content-management-patterns.md](references/content-management-patterns.md) - Translation memory, glossaries, context for translators, MTPE workflows, cost optimisation

### Templates (Production Starters)

- [assets/react-i18next-setup.md](assets/react-i18next-setup.md) - React + i18next complete setup
- [assets/vue-i18n-setup.md](assets/vue-i18n-setup.md) - Vue 3 + vue-i18n setup
- [assets/nextjs-i18n-setup.md](assets/nextjs-i18n-setup.md) - Next.js App Router i18n

### Data

- [data/sources.json](data/sources.json) - 60+ curated external references

### Related Skills

- [../software-frontend/SKILL.md](../software-frontend/SKILL.md) - Frontend architecture patterns (React, Vue, Angular, Next.js)
- [../marketing-seo-complete/SKILL.md](../marketing-seo-complete/SKILL.md) - Hreflang, international SEO

## Common Patterns

### Namespace Organisation

```text
locales/
├── en/
│   ├── common.json      # Shared: buttons, errors, nav
│   ├── auth.json        # Login, register, password
│   ├── dashboard.json   # Dashboard-specific
│   └── validation.json  # Form validation messages
├── de/
│   └── ... (same structure)
└── ar/
    └── ... (same structure)
```

### Lazy Loading (Performance)

```typescript
// i18next: Load namespaces on demand
i18n.loadNamespaces('dashboard').then(() => {
  // Dashboard translations now available
});

// React Suspense integration
<Suspense fallback={<Loading />}>
  <Dashboard />
</Suspense>
```

### TypeScript Integration

```typescript
// resources.d.ts - Type-safe keys
import common from './locales/en/common.json';

declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: 'common';
    resources: {
      common: typeof common;
    };
  }
}

// Now t('nonexistent') shows TypeScript error
```

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Hardcoded strings | Not translatable | Extract all user-facing text |
| String concatenation | Breaks translation context | Use interpolation `{name}` |
| Manual pluralisation | Wrong for many languages | Use ICU plural rules |
| Inline styles for RTL | Doesn't scale | Use CSS logical properties |
| Storing locale in URL only | Lost on navigation | Also persist to cookie/storage |
| No fallback locale | Blank text for missing keys | Always set `fallbackLng` |
| Silent English fallback on indexable non-English pages | Mixed-language output harms UX and can weaken locale SEO/AEO quality | Use locale-safe copy or fail build on missing keys for indexable routes |
| Loading all locales upfront | Slow initial load | Lazy load per namespace/locale |

## Operational Checklist

### Initial Setup

- REQUIRED: Choose i18n library based on decision tree
- REQUIRED: Set up directory structure for translations
- REQUIRED: Configure fallback locale chain
- REQUIRED: Set up locale detection strategy
- REQUIRED: Add TypeScript types for translation keys
- REQUIRED: Configure lazy loading for namespaces

### Translation Workflow

- REQUIRED: Set up string extraction (i18next-parser, formatjs, Lingui)
- REQUIRED: Integrate with a TMS when needed (Phrase, Lokalise, Crowdin, Locize)
- REQUIRED: Configure CI/CD for translation sync
- REQUIRED: Set up translation review process (glossary + style guide + QA gates)
- REQUIRED: Add missing key detection in development
- REQUIRED: Add hardcoded string detection for locale-routed pages
- REQUIRED: Verify metadata + JSON-LD locale parity with visible content
- REQUIRED: Add locale QA for mixed-language regressions on high-intent pages

### i18n Key Validation (Per-Change Gate)

When adding new `t()` / `useTranslations()` calls or new message keys:

1. Verify the key exists in the base locale file (e.g., `messages/en/*.json`).
2. Add the key to the base locale file before using it in code.
3. For multi-locale projects, add placeholder entries in all locale files or confirm the fallback chain handles missing keys gracefully.
4. Run the project's missing-key detection (e.g., `npm run build` or `next-intl` compile check) before committing.

Missing i18n keys cause blank text or fallback-language bleed on localized pages — a silent, user-facing regression.

### RTL Support

- REQUIRED: Use CSS logical properties (margin-inline-start)
- REQUIRED: Set `dir="rtl"` for RTL locales
- REQUIRED: Test with real RTL content (Arabic, Hebrew)
- REQUIRED: Handle bidirectional text (BiDi) in mixed strings
- REQUIRED: Mirror directional icons and images where appropriate

### Testing

- REQUIRED: Test pluralisation with 0, 1, 2, 5, 21 (language-specific)
- REQUIRED: Test date/number/currency formatting per locale
- REQUIRED: Test RTL layout in key screens/components
- REQUIRED: Test missing translation key handling (dev-only warnings)
- REQUIRED: Test locale switching and persistence (cookie/storage/url)

## Currency Check Protocol

When recommending libraries, versions, or tooling, verify what is current for the target ecosystem and project constraints. Prefer package registries and release notes over stale hard-coded numbers.

### Package versions (Node/npm)

```bash
npm view i18next version
npm view react-i18next version
npm view react-intl version
npm view vue-i18n version
npm view next-intl version
npm view @angular/localize version
npm view @lingui/core version
npm view typesafe-i18n version
```

### "Is X still recommended?" checks

- Check the project's last release date, open issues, and maintenance activity (GitHub releases/issues).
- Check framework compatibility (Next.js App Router/RSC, React 19, Vue 3, Angular current major).
- For bundle concerns, measure in the real app with a bundle analyzer instead of relying on published size claims.

## Ops Runbook: Large Locale Catalogs (LLM-Safe)

Use this when locale catalogs are too large for single reads, mixed-language UI appears, or missing keys are reported.

### 90-Second Triage

```bash
# 1) Confirm locale file layout
rg --files src/messages | sort

# 2) Detect oversized catalogs before reading
wc -l src/messages/en/*.json src/messages/*/*.json | sort -nr | head

# 3) Chunk reads for large files (avoid tool limits)
sed -n '1,200p' src/messages/en/landing.json
sed -n '201,400p' src/messages/en/landing.json
```

### Key Parity Check (Base vs Target Locale)

```bash
BASE=en
TARGET=ru

jq -r 'paths(scalars) | join(".")' src/messages/$BASE/*.json | sort -u > /tmp/$BASE.keys
jq -r 'paths(scalars) | join(".")' src/messages/$TARGET/*.json | sort -u > /tmp/$TARGET.keys

# Missing in target
comm -23 /tmp/$BASE.keys /tmp/$TARGET.keys

# Extra in target
comm -13 /tmp/$BASE.keys /tmp/$TARGET.keys
```

### Hardcoded UI String Sweep

```bash
# TSX/TS hardcoded literals (quick heuristic)
rg -n --pcre2 '"[A-Za-z][^"\n]{2,}"' src --glob '*.tsx' --glob '*.ts'

# JSX text nodes
rg -n --pcre2 '>[A-Za-z][^<]{2,}<' src --glob '*.tsx'
```

### CI Gate Pattern (No Mixed Language)

```bash
# Fail build if known missing-key sentinel appears
rg -n '__MISSING_I18N__|TODO_TRANSLATE' src/messages && exit 1 || true

# Optional: block English fallback on localized, indexable routes
rg -n 'fallback.*en|defaultLocale.*en' src/app src/lib
```

### Operational Rules

- Never read large locale files in one shot; always chunk.
- Use key diff first, translation pass second.
- Treat marketing/SEO locale key gaps as release blockers.
- Do not auto-insert machine translations without a tracked review pass.

