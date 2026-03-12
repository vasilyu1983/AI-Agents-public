# Locale Handling

Production patterns for dates, numbers, currencies, and locale detection using the JavaScript Intl API.

**Reference**: [MDN Intl API](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl)

---

## Intl API Overview

The `Intl` object provides locale-sensitive string comparison, number formatting, and date/time formatting.

### Available Formatters

| Formatter | Purpose | Example |
|-----------|---------|---------|
| `Intl.DateTimeFormat` | Date and time | "January 1, 2025" |
| `Intl.NumberFormat` | Numbers, currency, percent | "$1,234.56" |
| `Intl.RelativeTimeFormat` | Relative time | "2 days ago" |
| `Intl.ListFormat` | Lists | "A, B, and C" |
| `Intl.PluralRules` | Plural categories | "one", "other" |
| `Intl.Collator` | String comparison | Locale-aware sorting |
| `Intl.Segmenter` | Text segmentation | Word/sentence boundaries |
| `Intl.DisplayNames` | Display names | "United States", "English" |

---

## Date and Time Formatting

### DateTimeFormat Basics

```typescript
const date = new Date('2025-01-15T14:30:00');

// Default format
new Intl.DateTimeFormat('en-US').format(date);
// "1/15/2025"

new Intl.DateTimeFormat('de-DE').format(date);
// "15.1.2025"

new Intl.DateTimeFormat('ja-JP').format(date);
// "2025/1/15"
```

### Date Styles

```typescript
const date = new Date('2025-01-15');

// Predefined styles
new Intl.DateTimeFormat('en-US', { dateStyle: 'full' }).format(date);
// "Wednesday, January 15, 2025"

new Intl.DateTimeFormat('en-US', { dateStyle: 'long' }).format(date);
// "January 15, 2025"

new Intl.DateTimeFormat('en-US', { dateStyle: 'medium' }).format(date);
// "Jan 15, 2025"

new Intl.DateTimeFormat('en-US', { dateStyle: 'short' }).format(date);
// "1/15/25"
```

### Time Styles

```typescript
const date = new Date('2025-01-15T14:30:45');

new Intl.DateTimeFormat('en-US', { timeStyle: 'full' }).format(date);
// "2:30:45 PM Eastern Standard Time"

new Intl.DateTimeFormat('en-US', { timeStyle: 'long' }).format(date);
// "2:30:45 PM EST"

new Intl.DateTimeFormat('en-US', { timeStyle: 'medium' }).format(date);
// "2:30:45 PM"

new Intl.DateTimeFormat('en-US', { timeStyle: 'short' }).format(date);
// "2:30 PM"
```

### Custom Date Components

```typescript
const options: Intl.DateTimeFormatOptions = {
  weekday: 'long',
  year: 'numeric',
  month: 'long',
  day: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  timeZoneName: 'short',
};

new Intl.DateTimeFormat('en-US', options).format(date);
// "Wednesday, January 15, 2025 at 02:30 PM EST"
```

### Timezone Handling

```typescript
const date = new Date('2025-01-15T14:30:00Z');

// Display in specific timezone
new Intl.DateTimeFormat('en-US', {
  timeZone: 'America/New_York',
  dateStyle: 'medium',
  timeStyle: 'short',
}).format(date);
// "Jan 15, 2025, 9:30 AM"

new Intl.DateTimeFormat('en-US', {
  timeZone: 'Europe/London',
  dateStyle: 'medium',
  timeStyle: 'short',
}).format(date);
// "Jan 15, 2025, 2:30 PM"

new Intl.DateTimeFormat('en-US', {
  timeZone: 'Asia/Tokyo',
  dateStyle: 'medium',
  timeStyle: 'short',
}).format(date);
// "Jan 15, 2025, 11:30 PM"
```

### React Hook for Dates

```typescript
// hooks/useFormattedDate.ts
import { useMemo } from 'react';
import { useLocale } from 'next-intl';

interface DateFormatOptions {
  style?: 'full' | 'long' | 'medium' | 'short';
  includeTime?: boolean;
  timeZone?: string;
}

export function useFormattedDate(date: Date | string, options: DateFormatOptions = {}) {
  const locale = useLocale();

  return useMemo(() => {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    const { style = 'medium', includeTime = false, timeZone } = options;

    const formatOptions: Intl.DateTimeFormatOptions = {
      dateStyle: style,
      ...(includeTime && { timeStyle: 'short' }),
      ...(timeZone && { timeZone }),
    };

    return new Intl.DateTimeFormat(locale, formatOptions).format(dateObj);
  }, [date, locale, options.style, options.includeTime, options.timeZone]);
}

// Usage
function EventDate({ date }: { date: string }) {
  const formattedDate = useFormattedDate(date, {
    style: 'long',
    includeTime: true,
    timeZone: 'UTC',
  });

  return <time dateTime={date}>{formattedDate}</time>;
}
```

---

## Number Formatting

### Basic Number Formatting

```typescript
const num = 1234567.89;

new Intl.NumberFormat('en-US').format(num);
// "1,234,567.89"

new Intl.NumberFormat('de-DE').format(num);
// "1.234.567,89"

new Intl.NumberFormat('fr-FR').format(num);
// "1 234 567,89"

new Intl.NumberFormat('ja-JP').format(num);
// "1,234,567.89"

new Intl.NumberFormat('ar-SA').format(num);
// "١٬٢٣٤٬٥٦٧٫٨٩" (Arabic numerals)
```

### Currency Formatting

```typescript
const price = 1234.56;

new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
}).format(price);
// "$1,234.56"

new Intl.NumberFormat('en-GB', {
  style: 'currency',
  currency: 'GBP',
}).format(price);
// "£1,234.56"

new Intl.NumberFormat('de-DE', {
  style: 'currency',
  currency: 'EUR',
}).format(price);
// "1.234,56 €"

new Intl.NumberFormat('ja-JP', {
  style: 'currency',
  currency: 'JPY',
}).format(1234);
// "¥1,234"
```

### Currency Display Options

```typescript
const amount = 1234.56;

// Symbol (default)
new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  currencyDisplay: 'symbol',
}).format(amount);
// "$1,234.56"

// Narrow symbol
new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  currencyDisplay: 'narrowSymbol',
}).format(amount);
// "$1,234.56"

// Code
new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  currencyDisplay: 'code',
}).format(amount);
// "USD 1,234.56"

// Name
new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  currencyDisplay: 'name',
}).format(amount);
// "1,234.56 US dollars"
```

### Percentage Formatting

```typescript
const ratio = 0.8567;

new Intl.NumberFormat('en-US', {
  style: 'percent',
}).format(ratio);
// "86%"

new Intl.NumberFormat('en-US', {
  style: 'percent',
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
}).format(ratio);
// "85.7%"
```

### Compact Notation

```typescript
const largeNum = 1234567;

new Intl.NumberFormat('en-US', {
  notation: 'compact',
}).format(largeNum);
// "1.2M"

new Intl.NumberFormat('en-US', {
  notation: 'compact',
  compactDisplay: 'long',
}).format(largeNum);
// "1.2 million"

new Intl.NumberFormat('de-DE', {
  notation: 'compact',
}).format(largeNum);
// "1,2 Mio."
```

### React Hook for Numbers

```typescript
// hooks/useFormattedNumber.ts
import { useMemo } from 'react';
import { useLocale } from 'next-intl';

type NumberStyle = 'decimal' | 'currency' | 'percent' | 'unit';

interface NumberFormatOptions {
  style?: NumberStyle;
  currency?: string;
  notation?: 'standard' | 'compact';
  minimumFractionDigits?: number;
  maximumFractionDigits?: number;
}

export function useFormattedNumber(value: number, options: NumberFormatOptions = {}) {
  const locale = useLocale();

  return useMemo(() => {
    return new Intl.NumberFormat(locale, options as Intl.NumberFormatOptions).format(value);
  }, [value, locale, JSON.stringify(options)]);
}

// Usage
function Price({ amount, currency = 'USD' }: { amount: number; currency?: string }) {
  const formatted = useFormattedNumber(amount, {
    style: 'currency',
    currency,
  });

  return <span className="price">{formatted}</span>;
}
```

---

## Relative Time Formatting

### Basic Relative Time

```typescript
const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });

rtf.format(-1, 'day'); // "yesterday"
rtf.format(0, 'day'); // "today"
rtf.format(1, 'day'); // "tomorrow"
rtf.format(-2, 'day'); // "2 days ago"
rtf.format(3, 'week'); // "in 3 weeks"
```

### Numeric vs Auto

```typescript
// numeric: 'always' (default)
const rtfNumeric = new Intl.RelativeTimeFormat('en', { numeric: 'always' });
rtfNumeric.format(-1, 'day'); // "1 day ago"

// numeric: 'auto'
const rtfAuto = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
rtfAuto.format(-1, 'day'); // "yesterday"
```

### Style Options

```typescript
// long (default)
new Intl.RelativeTimeFormat('en', { style: 'long' }).format(-3, 'month');
// "3 months ago"

// short
new Intl.RelativeTimeFormat('en', { style: 'short' }).format(-3, 'month');
// "3 mo. ago"

// narrow
new Intl.RelativeTimeFormat('en', { style: 'narrow' }).format(-3, 'month');
// "3mo ago"
```

### Smart Relative Time Function

```typescript
function getRelativeTime(date: Date, locale: string = 'en'): string {
  const now = new Date();
  const diffMs = date.getTime() - now.getTime();
  const diffSec = Math.round(diffMs / 1000);
  const diffMin = Math.round(diffSec / 60);
  const diffHour = Math.round(diffMin / 60);
  const diffDay = Math.round(diffHour / 24);
  const diffWeek = Math.round(diffDay / 7);
  const diffMonth = Math.round(diffDay / 30);
  const diffYear = Math.round(diffDay / 365);

  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });

  if (Math.abs(diffSec) < 60) return rtf.format(diffSec, 'second');
  if (Math.abs(diffMin) < 60) return rtf.format(diffMin, 'minute');
  if (Math.abs(diffHour) < 24) return rtf.format(diffHour, 'hour');
  if (Math.abs(diffDay) < 7) return rtf.format(diffDay, 'day');
  if (Math.abs(diffWeek) < 4) return rtf.format(diffWeek, 'week');
  if (Math.abs(diffMonth) < 12) return rtf.format(diffMonth, 'month');
  return rtf.format(diffYear, 'year');
}

// Usage
getRelativeTime(new Date(Date.now() - 3600000)); // "1 hour ago"
getRelativeTime(new Date(Date.now() + 86400000 * 2)); // "in 2 days"
```

---

## List Formatting

### Basic List Formatting

```typescript
const fruits = ['Apple', 'Banana', 'Cherry'];

// Conjunction (and)
new Intl.ListFormat('en', { type: 'conjunction' }).format(fruits);
// "Apple, Banana, and Cherry"

// Disjunction (or)
new Intl.ListFormat('en', { type: 'disjunction' }).format(fruits);
// "Apple, Banana, or Cherry"

// Unit (no conjunction)
new Intl.ListFormat('en', { type: 'unit' }).format(fruits);
// "Apple, Banana, Cherry"
```

### Locale Variations

```typescript
const items = ['A', 'B', 'C'];

new Intl.ListFormat('en').format(items);
// "A, B, and C"

new Intl.ListFormat('de').format(items);
// "A, B und C"

new Intl.ListFormat('fr').format(items);
// "A, B et C"

new Intl.ListFormat('ja').format(items);
// "A、B、C"
```

---

## Display Names

### Language Names

```typescript
const dn = new Intl.DisplayNames('en', { type: 'language' });

dn.of('en'); // "English"
dn.of('de'); // "German"
dn.of('zh-Hans'); // "Simplified Chinese"
dn.of('ja'); // "Japanese"
```

### Region Names

```typescript
const dn = new Intl.DisplayNames('en', { type: 'region' });

dn.of('US'); // "United States"
dn.of('GB'); // "United Kingdom"
dn.of('DE'); // "Germany"
dn.of('JP'); // "Japan"
```

### Currency Names

```typescript
const dn = new Intl.DisplayNames('en', { type: 'currency' });

dn.of('USD'); // "US Dollar"
dn.of('EUR'); // "Euro"
dn.of('GBP'); // "British Pound"
dn.of('JPY'); // "Japanese Yen"
```

---

## Locale Detection

### Browser Detection

```typescript
function detectBrowserLocale(): string {
  // 1. navigator.languages (array, preferred)
  if (navigator.languages?.length) {
    return navigator.languages[0];
  }

  // 2. navigator.language (single value)
  if (navigator.language) {
    return navigator.language;
  }

  // 3. Fallback
  return 'en-US';
}
```

### Detection Strategy

```typescript
interface LocaleDetectionOptions {
  supportedLocales: string[];
  defaultLocale: string;
  cookieName?: string;
  queryParam?: string;
}

function detectLocale(options: LocaleDetectionOptions): string {
  const { supportedLocales, defaultLocale, cookieName = 'NEXT_LOCALE', queryParam = 'lang' } = options;

  // 1. URL query parameter
  if (typeof window !== 'undefined') {
    const urlParams = new URLSearchParams(window.location.search);
    const urlLocale = urlParams.get(queryParam);
    if (urlLocale && supportedLocales.includes(urlLocale)) {
      return urlLocale;
    }
  }

  // 2. Cookie
  if (typeof document !== 'undefined') {
    const cookieMatch = document.cookie.match(new RegExp(`${cookieName}=([^;]+)`));
    if (cookieMatch && supportedLocales.includes(cookieMatch[1])) {
      return cookieMatch[1];
    }
  }

  // 3. localStorage
  if (typeof localStorage !== 'undefined') {
    const storedLocale = localStorage.getItem('preferredLocale');
    if (storedLocale && supportedLocales.includes(storedLocale)) {
      return storedLocale;
    }
  }

  // 4. Browser preference
  const browserLocales = navigator.languages || [navigator.language];
  for (const browserLocale of browserLocales) {
    // Exact match
    if (supportedLocales.includes(browserLocale)) {
      return browserLocale;
    }
    // Language-only match (en-US -> en)
    const lang = browserLocale.split('-')[0];
    const langMatch = supportedLocales.find((l) => l.startsWith(lang));
    if (langMatch) {
      return langMatch;
    }
  }

  // 5. Default
  return defaultLocale;
}
```

### Next.js Middleware Detection

```typescript
// middleware.ts
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

export function middleware(request: NextRequest) {
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

---

## Locale-Aware Utilities

### Sorting

```typescript
const names = ['Ångström', 'Zebra', 'Äpfel', 'Apple'];

// Default (wrong for non-English)
names.sort();
// ["Apple", "Zebra", "Äpfel", "Ångström"] FAIL

// Locale-aware
names.sort(new Intl.Collator('de').compare);
// ["Äpfel", "Ångström", "Apple", "Zebra"] PASS

// Case-insensitive
names.sort(new Intl.Collator('en', { sensitivity: 'base' }).compare);
```

### Phone Number Formatting

```typescript
// Use libphonenumber-js for proper phone formatting
import { parsePhoneNumber } from 'libphonenumber-js';

const phone = parsePhoneNumber('+12025551234');
phone.formatInternational(); // "+1 202 555 1234"
phone.formatNational(); // "(202) 555-1234"
```

### Address Formatting

Address formats vary significantly by country. Use a library like `@googlemaps/addressvalidation` or format manually:

```typescript
interface Address {
  street: string;
  city: string;
  state?: string;
  postalCode: string;
  country: string;
}

function formatAddress(address: Address, country: string): string {
  switch (country) {
    case 'US':
      return `${address.street}\n${address.city}, ${address.state} ${address.postalCode}`;
    case 'DE':
      return `${address.street}\n${address.postalCode} ${address.city}`;
    case 'JP':
      return `〒${address.postalCode}\n${address.state}${address.city}${address.street}`;
    default:
      return `${address.street}\n${address.city} ${address.postalCode}`;
  }
}
```

---

## Best Practices

### Always Use Intl APIs

```typescript
// FAIL Manual formatting
const price = '$' + amount.toFixed(2);

// PASS Intl formatting
const price = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
}).format(amount);
```

### Cache Formatter Instances

```typescript
// FAIL Creating new formatter each render
function formatDate(date: Date) {
  return new Intl.DateTimeFormat('en-US').format(date);
}

// PASS Cache formatter
const dateFormatter = new Intl.DateTimeFormat('en-US');
function formatDate(date: Date) {
  return dateFormatter.format(date);
}

// PASS Or use a cache map for multiple locales
const formatters = new Map<string, Intl.DateTimeFormat>();

function getDateFormatter(locale: string): Intl.DateTimeFormat {
  if (!formatters.has(locale)) {
    formatters.set(locale, new Intl.DateTimeFormat(locale));
  }
  return formatters.get(locale)!;
}
```

### Handle Timezone Consistently

```typescript
// Store dates in UTC (ISO 8601)
const storedDate = '2025-01-15T14:30:00Z';

// Display in user's timezone
new Intl.DateTimeFormat('en-US', {
  timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  dateStyle: 'medium',
  timeStyle: 'short',
}).format(new Date(storedDate));
```

### Test with Multiple Locales

```typescript
const testLocales = ['en-US', 'de-DE', 'ar-SA', 'ja-JP', 'he-IL'];

testLocales.forEach((locale) => {
  describe(`Locale: ${locale}`, () => {
    it('formats currency correctly', () => {
      const formatted = new Intl.NumberFormat(locale, {
        style: 'currency',
        currency: 'USD',
      }).format(1234.56);

      expect(formatted).toBeTruthy();
      expect(formatted.length).toBeGreaterThan(0);
    });
  });
});
```
