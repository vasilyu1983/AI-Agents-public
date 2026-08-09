# Ops Runbook: Large Locale Catalogs (LLM-Safe)

Use this when locale catalogs are too large for single reads, mixed-language UI appears, or missing keys are reported.

## Table of Contents

- [90-Second Triage](#90-second-triage)
- [1) Confirm locale file layout](#1-confirm-locale-file-layout)
- [2) Detect oversized catalogs before reading](#2-detect-oversized-catalogs-before-reading)
- [3) Chunk reads for large files (avoid tool limits)](#3-chunk-reads-for-large-files-avoid-tool-limits)
- [Key Parity Check (Base vs Target Locale)](#key-parity-check-base-vs-target-locale)
- [Missing in target](#missing-in-target)
- [Extra in target](#extra-in-target)
- [Hardcoded UI String Sweep](#hardcoded-ui-string-sweep)
- [TSX/TS hardcoded literals (quick heuristic)](#tsxts-hardcoded-literals-quick-heuristic)
- [JSX text nodes](#jsx-text-nodes)
- [CI Gate Pattern (No Mixed Language)](#ci-gate-pattern-no-mixed-language)
- [Fail build if known missing-key sentinel appears](#fail-build-if-known-missing-key-sentinel-appears)
- [Optional: block English fallback on localized, indexable routes](#optional-block-english-fallback-on-localized-indexable-routes)
- [Locale Purity Rules](#locale-purity-rules)
- [Engine Output i18n (`_i18n` Metadata Pattern)](#engine-output-i18n-i18n-metadata-pattern)
- [Locale Propagation](#locale-propagation)
- [Duplicate JSON Key Detection](#duplicate-json-key-detection)
- [Operational Rules](#operational-rules)

## 90-Second Triage

```bash
# 1) Confirm locale file layout
rg --files src/messages | sort

# 2) Detect oversized catalogs before reading
wc -l src/messages/en/*.json src/messages/*/*.json | sort -nr | head

# 3) Chunk reads for large files (avoid tool limits)
sed -n '1,200p' src/messages/en/landing.json
sed -n '201,400p' src/messages/en/landing.json
```

## Key Parity Check (Base vs Target Locale)

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

## Hardcoded UI String Sweep

```bash
# TSX/TS hardcoded literals (quick heuristic)
rg -n --pcre2 '"[A-Za-z][^"\n]{2,}"' src --glob '*.tsx' --glob '*.ts'

# JSX text nodes
rg -n --pcre2 '>[A-Za-z][^<]{2,}<' src --glob '*.tsx'
```

## CI Gate Pattern (No Mixed Language)

```bash
# Fail build if known missing-key sentinel appears
rg -n '__MISSING_I18N__|TODO_TRANSLATE' src/messages && exit 1 || true

# Optional: block English fallback on localized, indexable routes
rg -n 'fallback.*en|defaultLocale.*en' src/app src/lib
```

## Locale Purity Rules

- Marketing and SEO pages are release blockers when target-locale keys are missing.
- Do not inject English fragments into non-English metadata, breadcrumbs, JSON-LD, or body copy.
- If fallback is unavoidable on non-indexed product UI, use telemetry and a follow-up fix ticket.

## Engine Output i18n (`_i18n` Metadata Pattern)

Use this when server-generated content must stay cacheable while the UI remains localised.

- Engine emits `_i18n: { key, params }` alongside the fallback text.
- Client resolves `_i18n ? t(key, params) : fallbackText`.
- Old cached payloads without `_i18n` degrade gracefully.
- Prefer one cached response plus client-side resolution over duplicating server payloads per locale.

| Pattern | Status | Why |
|---------|--------|-----|
| `{ text: "Neptune trine Jupiter", _i18n: { key: "transits.neptune_trine", params: { p1: "Neptune", p2: "Jupiter" } } }` | PASS | Client resolves per locale; server caches once |
| `{ text_en: "...", text_ru: "...", text_de: "..." }` | FAIL | Cache and payload bloat per locale |
| `t(meaning.theme)` | FAIL | Raw engine output is not a stable translation key |
| `t.has('meanings.4.theme') ? t('meanings.4.theme') : meaning.theme` | PASS | Graceful fallback when a key is missing |

## Locale Propagation

Every commit adding base-locale keys must propagate to target locales.

```bash
jq -r 'paths(scalars) | join(".")' messages/en/*.json | sort -u > /tmp/en.keys
for locale in ar de es fr hi it ja ko pt-BR ru tr vi zh; do
  jq -r 'paths(scalars) | join(".")' messages/$locale/*.json | sort -u > /tmp/$locale.keys
  echo "=== $locale missing ==="
  comm -23 /tmp/en.keys /tmp/$locale.keys | head -20
done
```

- Diff all locales before translating.
- Batch missing keys by namespace/file instead of discovering one gap at a time.
- Use placeholder or approved fallback values when external translation connectors are unavailable.

## Duplicate JSON Key Detection

Large locale catalogs can silently drop duplicated keys because JSON uses last-writer-wins semantics.

```bash
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

## Operational Rules

- Never read large locale files in one shot; always chunk.
- Use key diff first, translation pass second.
- Treat marketing/SEO locale key gaps as release blockers.
- Do not auto-insert machine translations without a tracked review pass.
