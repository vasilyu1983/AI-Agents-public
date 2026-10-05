# Locale Handling

## Table of Contents

- [Formatting decisions and traps](#formatting-decisions-and-traps)
- [Temporal and Intl.DurationFormat](#temporal-and-intldurationformat)
- [Locale detection](#locale-detection)
- [vue-i18n v11 migration](#vue-i18n-v11-migration)

## Formatting Decisions and Traps

Use the locale selected for the request consistently in server and client rendering. Cache formatters by locale **and options**; a locale-only cache can reuse the wrong currency or time zone. Resolve API options from [ECMA-402](https://tc39.es/ecma402/) or the [Intl reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl) when implementing.

| Value | Decision | Failure to test |
|---|---|---|
| Timestamp | Store an instant; render with an explicit display time zone | Server/client defaults differ and hydration changes the date |
| Calendar date (birthday, invoice date) | Preserve a date-only value | Converting midnight UTC shifts the day in another zone |
| Money | Currency comes from the transaction, not the language | Locale does not determine USD versus EUR; rounding policy differs |
| Percent | NumberFormat receives a ratio | Passing 85 instead of 0.85 displays the wrong magnitude |
| Relative time | Define rounding and calendar boundaries separately | Fixed 30-day months and 24-hour days fail at month/DST boundaries |
| Lists or names | ListFormat/DisplayNames for the chosen locale | Comma concatenation and English names leak into localized UI |
| Sorting | Collator with explicit sensitivity | Code-unit ordering is not locale ordering; never use it for identifiers |
| Phones and addresses | Region-aware parser/schema | Intl is not a phone/address validator; language alone does not specify a country |

Do not snapshot incidental whitespace or punctuation across ICU/CLDR upgrades. Assert semantic parts, currency, time zone, supported locale resolution, and known date-boundary cases; visual snapshots cover layout separately.

## Temporal and Intl.DurationFormat

Before adopting Temporal, check support in every browser, Node/edge runtime, and SSR environment against [TC39's Temporal documentation](https://tc39.es/proposal-temporal/docs/). Feature-detect and use a compatible polyfill when required; pin it through the consuming application's dependency policy. Native browser availability does not establish server parity.

Choose `Temporal.Instant` for exact time, `Temporal.PlainDate` for a calendar date with no zone, and `Temporal.ZonedDateTime` when calendar arithmetic needs a named zone. Test DST gaps/overlaps and choose a disambiguation policy explicitly. Do not add a fixed millisecond day to implement “same local time tomorrow.”

[Intl.DurationFormat](https://tc39.es/ecma402/#durationformat-objects) formats duration fields; it does not compute elapsed time or relative calendar arithmetic. Feature-detect it separately from Temporal. If unavailable, use a tested polyfill or the application's localized duration messages; never silently concatenate English unit names.

```javascript
// Illustrative input; application owns feature detection and fallback.
if (typeof Intl.DurationFormat === 'function') {
  const formatter = new Intl.DurationFormat(locale, {style: 'short'});
  const label = formatter.format({hours: 1, minutes: 30});
}
```

## Locale Detection

An explicit supported URL/deep-link locale wins for its request. Only negotiate an unlocalized entry: authenticated preference, persisted choice, supported Accept-Language, then default. Use a maintained locale matcher instead of `startsWith`, which confuses distinct language tags. Validate persisted tags against the supported set, and handle disabled storage in browsers.

Do not access navigator/document in server code. Set the resolved locale before producing metadata or UI; retain it through navigation and shared links. Decide separately whether changing locale should update an account preference.

### Next.js Proxy Detection

```typescript
// proxy.ts
import { NextRequest, NextResponse } from 'next/server';
import Negotiator from 'negotiator';
import { match } from '@formatjs/intl-localematcher';

const locales = ['en', 'de', 'fr', 'ar'];
const defaultLocale = 'en';

function getLocale(request: NextRequest): string {
  // 1. Check cookie
  const cookieLocale = request.cookies.get('NEXT_LOCALE')?.value;
  if (cookieLocale && locales.includes(cookieLocale)) {
    return cookieLocale;
  }

  // 2. Negotiate from Accept-Language header
  const negotiator = new Negotiator({
    headers: { 'accept-language': request.headers.get('accept-language') || '' },
  });
  const languages = negotiator.languages();

  try {
    return match(languages, locales, defaultLocale);
  } catch {
    return defaultLocale;
  }
}

export function proxy(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  // Check if pathname already has locale
  const pathnameHasLocale = locales.some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  );

  if (pathnameHasLocale) return;

  // Redirect to locale-prefixed path
  const locale = getLocale(request);
  request.nextUrl.pathname = `/${locale}${pathname}`;
  return NextResponse.redirect(request.nextUrl);
}

export const config = {
  matcher: ['/((?!api|_next|.*\\..*).*)'],
};
```


Use `proxy.ts` from Next.js 16; older projects use `middleware.ts`. Check the [Proxy convention](https://nextjs.org/docs/app/getting-started/proxy) and installed next-intl integration before copying the example. Combine routing in the application's existing entry point, preserve explicit locales, and test excluded assets/API paths. Static exports need generated locale paths and cannot rely on request-time proxy negotiation.

## vue-i18n v11 Migration

Read the [v11 migration guide](https://vue-i18n.intlify.dev/guide/migration/breaking11) against the installed major. Legacy API mode and `v-t` are deprecated in v11; `tc`/`$tc` are dropped there. Prefer Composition API (`legacy: false`, `useI18n`) and `t` plural arguments. Replace `v-t` usage and use the documented `@intlify/vue-i18n/no-deprecated-v-t` lint rule.

Migrate a fixture first: test local versus global scope, locale reactivity, interpolation, plural choice, SSR hydration, and formatters. Do not treat the import upgrade as a complete migration or pass FormatJS ICU syntax directly to vue-i18n's own message grammar without a supported custom compiler.
