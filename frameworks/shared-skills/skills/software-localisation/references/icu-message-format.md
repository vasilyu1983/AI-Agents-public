# ICU Message Format

Production patterns for pluralisation, select statements, and locale-aware formatting.

**Reference**: [ICU Message Format Specification](https://unicode-org.github.io/icu/userguide/format_parse/messages/)

**Status (Jan 2026)**: ICU MessageFormat 2.0 was finalized in March 2025 but remains in **technology preview** in ICU 78. Java implementation is more mature (core API at "draft" status), C++ is still catching up. For production use, continue with MessageFormat 1.0 syntax documented below. See [MessageFormat 2.0 docs](https://unicode-org.github.io/icu/userguide/format_parse/messages/mf2.html) for the new syntax when ready.

---

## Core Syntax

### Simple Interpolation

```text
Hello, {name}!
```

```typescript
// i18next
t('greeting', { name: 'Alice' }) // "Hello, Alice!"

// react-intl
<FormattedMessage id="greeting" values={{ name: 'Alice' }} />
```

### Variable Types

| Type | Syntax | Example |
|------|--------|---------|
| String | `{name}` | `Hello, {name}` |
| Number | `{count, number}` | `{count, number}` -> "1,234" |
| Date | `{date, date}` | `{date, date, medium}` -> "Jan 1, 2025" |
| Time | `{time, time}` | `{time, time, short}` -> "3:45 PM" |
| Plural | `{count, plural, ...}` | See below |
| Select | `{gender, select, ...}` | See below |
| Selectordinal | `{position, selectordinal, ...}` | See below |

---

## Pluralisation

### Basic Plural

```text
{count, plural,
  one {# item}
  other {# items}
}
```

| Count | Output |
|-------|--------|
| 0 | "0 items" |
| 1 | "1 item" |
| 2 | "2 items" |
| 100 | "100 items" |

### CLDR Plural Categories

Different languages have different plural rules:

| Language | Categories | Example |
|----------|------------|---------|
| English | one, other | 1 item, 2 items |
| French | one, other | 1 élément, 2 éléments |
| Russian | one, few, many, other | 1 товар, 2 товара, 5 товаров, 21 товар |
| Arabic | zero, one, two, few, many, other | Complex rules |
| Japanese | other (only) | No plural forms |
| Polish | one, few, many, other | 1 plik, 2 pliki, 5 plików |

### Complete Plural Example

```text
{count, plural,
  =0 {No messages}
  one {# message}
  other {# messages}
}
```

```json
// locales/en/common.json
{
  "messages_count": "{count, plural, =0 {No messages} one {# message} other {# messages}}"
}

// locales/ru/common.json
{
  "messages_count": "{count, plural, =0 {Нет сообщений} one {# сообщение} few {# сообщения} many {# сообщений} other {# сообщения}}"
}
```

### Exact Match (=N)

```text
{count, plural,
  =0 {Cart is empty}
  =1 {One item in cart}
  =2 {A pair of items}
  other {# items in cart}
}
```

**Rule**: `=N` takes precedence over category keywords.

---

## Select Statements

### Gender Selection

```text
{gender, select,
  male {He liked your post}
  female {She liked your post}
  other {They liked your post}
}
```

### Category Selection

```text
{type, select,
  error {An error occurred: {message}}
  warning {Warning: {message}}
  info {Info: {message}}
  other {{message}}
}
```

### Nested Select + Plural

```text
{gender, select,
  male {{count, plural,
    one {He has # new message}
    other {He has # new messages}
  }}
  female {{count, plural,
    one {She has # new message}
    other {She has # new messages}
  }}
  other {{count, plural,
    one {They have # new message}
    other {They have # new messages}
  }}
}
```

**Best Practice**: Place `select` on the outside, `plural` on the inside.

---

## Selectordinal (Ordinal Numbers)

For ordinal positions: 1st, 2nd, 3rd, 4th...

```text
{position, selectordinal,
  one {#st place}
  two {#nd place}
  few {#rd place}
  other {#th place}
}
```

| Position | Output |
|----------|--------|
| 1 | "1st place" |
| 2 | "2nd place" |
| 3 | "3rd place" |
| 4 | "4th place" |
| 21 | "21st place" |

---

## Number Formatting

### Basic Number

```text
Price: {price, number}
```

Output: "Price: 1,234.56" (locale-aware)

### Currency

```text
{price, number, currency}
```

**Note**: Currency code must be passed separately in most libraries.

```typescript
// react-intl
<FormattedNumber value={99.99} style="currency" currency="USD" />
// Output: "$99.99"

// i18next with Intl
new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
}).format(99.99);
```

### Percentage

```text
{ratio, number, percent}
```

```typescript
// 0.75 -> "75%"
```

### Custom Number Formats

```text
{value, number, ::currency/EUR unit-width-narrow}
```

**Skeleton syntax** (advanced):
- `::currency/EUR` - Currency with EUR
- `::percent scale/100` - Percentage scaled
- `::compact-short` - "1.2K"

---

## Date and Time Formatting

### Date Styles

```text
{date, date, short}   // 1/1/25
{date, date, medium}  // Jan 1, 2025
{date, date, long}    // January 1, 2025
{date, date, full}    // Wednesday, January 1, 2025
```

### Time Styles

```text
{time, time, short}   // 3:45 PM
{time, time, medium}  // 3:45:30 PM
{time, time, long}    // 3:45:30 PM EST
{time, time, full}    // 3:45:30 PM Eastern Standard Time
```

### Custom Date/Time

```text
{date, date, ::yyyy-MM-dd}  // 2025-01-01
{date, date, ::EEEE}        // Wednesday
{date, date, ::MMM}         // Jan
```

### Relative Time

```typescript
// Use Intl.RelativeTimeFormat directly
const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });

rtf.format(-1, 'day'); // "yesterday"
rtf.format(2, 'hour'); // "in 2 hours"
rtf.format(-3, 'week'); // "3 weeks ago"
```

---

## Escaping Special Characters

### Apostrophe Handling

```text
// Single quote escapes syntax characters
'{name}' -> "{name}" (literal braces)

// Double apostrophe for literal apostrophe
It''s working -> "It's working"

// Recommended: Use curly apostrophe (U+2019)
It's working -> "It's working" (no escaping needed)
```

### When to Escape

| Character | Escape | Example |
|-----------|--------|---------|
| `{` | `'{'` | `'{' is a brace` |
| `}` | `'}'` | `'}' is a brace` |
| `'` | `''` | `It''s a test` |
| `#` (in plural) | `'#'` | `'#' is a hash` |

### Best Practice

Use curly quotes for human-readable text:
- `'` (U+2019) instead of `'` (U+0027)
- Avoids ICU escaping issues
- Better typography

---

## Translator-Friendly Patterns

### Full Sentences in Sub-messages

```text
// FAIL Fragments (hard to translate)
{count, plural, one {item} other {items}}
// Translator sees: "item" and "items" without context

// PASS Complete sentences
{count, plural,
  one {You have # item in your cart}
  other {You have # items in your cart}
}
// Translator sees full context
```

### Avoid Concatenation

```text
// FAIL Concatenation (breaks in other languages)
"welcome": "Welcome",
"to_site": "to our site"
// Used as: t('welcome') + ' ' + t('to_site')

// PASS Single key
"welcome_message": "Welcome to our site"
```

### Context Comments

```json
// With description for translators
{
  "items_count": {
    "message": "{count, plural, one {# item} other {# items}}",
    "description": "Count of items in shopping cart"
  }
}
```

---

## Library-Specific Implementation

### react-intl (FormatJS)

```tsx
import { FormattedMessage, FormattedPlural } from 'react-intl';

// ICU in message
<FormattedMessage
  id="items_count"
  defaultMessage="{count, plural, one {# item} other {# items}}"
  values={{ count: 5 }}
/>

// FormattedPlural component
<FormattedPlural
  value={count}
  one="# item"
  other="# items"
/>
```

### i18next

```typescript
// Enable ICU format
import i18n from 'i18next';
import ICU from 'i18next-icu';

i18n.use(ICU).init({
  // ...
});

// JSON file
{
  "items_count": "{count, plural, one {# item} other {# items}}"
}

// Usage
t('items_count', { count: 5 }) // "5 items"
```

### vue-i18n

```typescript
import { createI18n } from 'vue-i18n';

const i18n = createI18n({
  // ...
  messageCompiler: (message, locale) => {
    // Custom ICU compiler if needed
  },
});
```

```vue
<template>
  {{ $t('items_count', { count: 5 }) }}
</template>
```

### LinguiJS

```tsx
import { Plural, Trans } from '@lingui/macro';

<Plural
  value={count}
  one="# item"
  other="# items"
/>

// Or inline
<Trans>
  {count, plural, one {# item} other {# items}}
</Trans>
```

---

## Common Patterns

### Zero Handling

```text
{count, plural,
  =0 {No items}
  one {# item}
  other {# items}
}
```

### Range Plurals

```text
{count, plural,
  =0 {No results}
  one {# result}
  =2 {A couple of results}
  few {A few results (#)}
  other {# results}
}
```

### Nested with HTML (react-intl)

```tsx
<FormattedMessage
  id="welcome_user"
  defaultMessage="Welcome, <bold>{name}</bold>!"
  values={{
    name: user.name,
    bold: (chunks) => <strong>{chunks}</strong>,
  }}
/>
```

```json
{
  "welcome_user": "Welcome, <bold>{name}</bold>!"
}
```

---

## Validation and Linting

### FormatJS CLI

```bash
# Validate ICU syntax
npx formatjs compile messages/en.json --ast

# Extract and validate
npx formatjs extract 'src/**/*.tsx' --out-file messages/en.json --throws
```

### ESLint Plugin

```bash
npm install -D eslint-plugin-formatjs
```

```javascript
// .eslintrc.js
module.exports = {
  plugins: ['formatjs'],
  rules: {
    'formatjs/enforce-default-message': 'error',
    'formatjs/enforce-placeholders': 'error',
    'formatjs/no-multiple-whitespaces': 'error',
    'formatjs/no-offset': 'error',
  },
};
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| `{count} item(s)` | Wrong for most languages | Use `{count, plural, ...}` |
| String concatenation | Word order varies | Single ICU message |
| `choice` argument | Deprecated, limited | Use `plural` instead |
| Hardcoded plural rules | English-centric | Use CLDR categories |
| Missing `other` clause | Required fallback | Always include `other` |
| Nesting `plural` outside `select` | Complex, error-prone | `select` outside, `plural` inside |

---

## Testing ICU Messages

### Unit Tests

```typescript
import { createIntl, createIntlCache } from 'react-intl';

const cache = createIntlCache();
const intl = createIntl({ locale: 'en', messages: {} }, cache);

describe('ICU messages', () => {
  it('handles plural correctly', () => {
    const message = '{count, plural, one {# item} other {# items}}';

    expect(intl.formatMessage({ id: 'test', defaultMessage: message }, { count: 0 })).toBe(
      '0 items'
    );

    expect(intl.formatMessage({ id: 'test', defaultMessage: message }, { count: 1 })).toBe(
      '1 item'
    );

    expect(intl.formatMessage({ id: 'test', defaultMessage: message }, { count: 5 })).toBe(
      '5 items'
    );
  });
});
```

### Snapshot Testing

```typescript
import messages from '../messages/en.json';

describe('Message syntax', () => {
  Object.entries(messages).forEach(([key, message]) => {
    it(`${key} is valid ICU`, () => {
      expect(() => new IntlMessageFormat(message, 'en')).not.toThrow();
    });
  });
});
```
