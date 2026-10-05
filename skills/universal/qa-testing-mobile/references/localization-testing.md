# Mobile Localization Testing

Use this reference when the app ships multiple locales or consumes backend-served localized content.

## Recommended Layers

1. **Catalog coverage**
   - Verify referenced keys exist in every supported locale.
   - Run this as a fast unit or build-time check.
   - Treat generated catalogs and exported resources as part of the test input, not only source files.

2. **Locale layout smoke**
   - Run a thin UI smoke pass in a few high-signal locales.
   - Typical picks: one long-string locale, one non-Latin locale, and one RTL locale when supported.
   - Keep full locale sweeps for release-candidate or scheduled runs.

3. **Backend-served localized content**
   - If APIs return localized prose, verify the non-English path explicitly.
   - Check both transport-level locale selection and user-visible rendering.
   - Do not assume client-side string coverage proves backend localization quality.

4. **Tier or variant parity**
   - If localization quality differs by tier, region, or feature flag, sample each variant deliberately.
   - Cache and fallback behavior are common failure points.

## Selector Rules

- Do not use localized display strings as primary selectors.
- Prefer stable accessibility identifiers or test tags.
- Use visible-text assertions only when the purpose of the test is to verify user-facing copy.
- For vision-based tools, give the tool explicit anchors whenever possible because locale changes can destabilize visual matching.

## Typical Release Questions

- Are all supported locales loading valid resources?
- Do the highest-risk screens still fit and remain usable in long-string and RTL cases?
- Does backend-served content honor the requested locale?
- Do push, deep link, onboarding, and paywall flows preserve locale consistently after relaunch or upgrade?
