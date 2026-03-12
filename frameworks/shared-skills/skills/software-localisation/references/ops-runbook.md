# Ops Runbook: Large Locale Catalogs (LLM-Safe)

Use this when locale catalogs are too large for single reads, mixed-language UI appears, or missing keys are reported.

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

## Operational Rules

- Never read large locale files in one shot; always chunk.
- Use key diff first, translation pass second.
- Treat marketing/SEO locale key gaps as release blockers.
- Do not auto-insert machine translations without a tracked review pass.
