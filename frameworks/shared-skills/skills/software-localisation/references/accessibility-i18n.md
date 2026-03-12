# Accessibility and Internationalisation

Patterns for building applications that are both accessible and multilingual. Covers screen reader behaviour across languages, ARIA in multilingual contexts, bidirectional text accessibility, dynamic type across scripts, keyboard navigation for RTL, and WCAG requirements for multilingual content.

---

## Why This Intersection Matters

Accessibility and internationalisation are often treated as separate concerns, but they interact in ways that can create compounding failures. An app that passes WCAG in English may be unusable with a screen reader in Arabic, or illegible in Hindi at larger font sizes. Testing each in isolation misses the overlap.

| Overlap Area | a11y Concern | i18n Concern | Combined Risk |
|-------------|-------------|-------------|---------------|
| Screen readers | Reading order, labels | RTL direction, language | Wrong reading order in RTL |
| Font scaling | Dynamic Type, zoom | Script height variance | Clipped text in tall scripts |
| Keyboard nav | Tab order, focus | RTL reversal | Backwards navigation in RTL |
| Forms | Labels, errors, ARIA | Translated messages | Untranslated error messages |
| Colour | Contrast ratios | Cultural colour meaning | Inaccessible + culturally wrong |

---

## Screen Readers and RTL Languages

### Screen Reader Behaviour by Platform

| Screen Reader | Platform | RTL Support | Notes |
|--------------|----------|-------------|-------|
| VoiceOver | iOS/macOS | Excellent | Follows `lang` and `dir` attributes accurately |
| NVDA | Windows | Good | Reads RTL correctly when `dir="rtl"` is set |
| JAWS | Windows | Good | Best when `lang` attribute matches content |
| TalkBack | Android | Good | Follows system language and `dir` attribute |
| Narrator | Windows | Adequate | Improving; test with each Windows update |

### Critical: The `lang` Attribute

Screen readers use the `lang` attribute to select the correct pronunciation engine. Missing or wrong `lang` causes Arabic text to be read with English phonetics.

```html
<!-- CORRECT: Language declared at document level -->
<html lang="ar" dir="rtl">

<!-- CORRECT: Inline language switch for mixed content -->
<p lang="ar">مرحبا <span lang="en">React</span> عالم</p>

<!-- WRONG: No lang attribute — screen reader guesses -->
<html>
  <body dir="rtl">...</body>
</html>
```

### hreflang for Alternate Language Links

```html
<!-- Help screen readers announce language alternatives -->
<link rel="alternate" hreflang="en" href="/en/about" />
<link rel="alternate" hreflang="ar" href="/ar/about" />
<link rel="alternate" hreflang="ja" href="/ja/about" />
<link rel="alternate" hreflang="x-default" href="/en/about" />
```

### VoiceOver Behaviour with RTL

VoiceOver on iOS and macOS:
- Reads right-to-left when `dir="rtl"` is set
- Swipe right moves to the **next** element (visually left in RTL)
- Numbers embedded in RTL text are read left-to-right (correct)
- Punctuation follows the base paragraph direction

```swift
// iOS: Set accessibility language explicitly
label.accessibilityLanguage = "ar"

// SwiftUI
Text("مرحبا بالعالم")
    .accessibilityLanguage(Locale(identifier: "ar"))
```

---

## ARIA Labels in Multiple Languages

### Translating ARIA Attributes

All ARIA text content must be translated. This includes `aria-label`, `aria-placeholder`, `aria-description`, and `aria-roledescription`.

```tsx
// WRONG: ARIA label hardcoded in English on Arabic page
<button aria-label="Close dialog">×</button>

// CORRECT: ARIA label translated
<button aria-label={t('dialog.close')}>×</button>
```

### Common ARIA Attributes Requiring Translation

| Attribute | Purpose | Translation Required |
|-----------|---------|---------------------|
| `aria-label` | Accessible name | Yes — always |
| `aria-placeholder` | Input placeholder | Yes — always |
| `aria-description` | Extended description | Yes — always |
| `aria-roledescription` | Custom role name | Yes — always |
| `aria-valuetext` | Slider/progress text | Yes — always |
| `aria-live` | Live region type | No — keyword value |
| `aria-expanded` | Expansion state | No — boolean |
| `role` | Element role | No — keyword value |

### Language-Specific ARIA Patterns

```tsx
// Navigation landmark with translated label
<nav aria-label={t('nav.main')}>
  {/* ... */}
</nav>

// Form with translated error messages
<input
  aria-invalid={hasError}
  aria-errormessage={hasError ? 'email-error' : undefined}
/>
<span id="email-error" role="alert" lang={locale}>
  {t('form.email.invalid')}
</span>

// Live region announces in the correct language
<div aria-live="polite" lang={locale}>
  {statusMessage}
</div>
```

---

## Bidirectional Text Accessibility

### BiDi Marks and Isolation

When mixing LTR and RTL text, use Unicode BiDi marks or the `<bdi>` element to prevent garbled reading order.

| Mark | Unicode | Purpose |
|------|---------|---------|
| LRM | U+200E | Forces left-to-right at insertion point |
| RLM | U+200F | Forces right-to-left at insertion point |
| LRI | U+2066 | Left-to-right isolate (start) |
| RLI | U+2067 | Right-to-left isolate (start) |
| PDI | U+2069 | Pop directional isolate (end) |

### HTML bdi Element

```html
<!-- User-generated content with unknown direction -->
<p lang="ar">
  المستخدم <bdi>@john_doe</bdi> أرسل رسالة
</p>

<!-- Without bdi: @john_doe may display incorrectly in RTL context -->
```

### Screen Reader Impact

Screen readers interpret BiDi marks as direction changes. Excessive or incorrect marks cause:
- Pauses and stuttering during reading
- Wrong reading order for numbers and punctuation
- Confusion when navigating by character

```typescript
// CORRECT: Use CSS direction isolation instead of Unicode marks when possible
// CSS approach is cleaner for screen readers
function UserMention({ username }: { username: string }) {
  return (
    <bdi className="inline-block" dir="ltr">
      @{username}
    </bdi>
  );
}
```

### ICU Messages and BiDi

```text
// ICU messages with mixed-direction interpolation
// Use Unicode isolates around interpolated values
"greeting": "مرحبا \u2068{name}\u2069!"
```

---

## Dynamic Type and Font Scaling Across Scripts

### Script Height Variance

Different scripts have different natural heights and line spacing requirements. A font size that works for Latin may clip Devanagari or be tiny in CJK.

| Script | Baseline Height | Ascender/Descender | Min Line Height |
|--------|----------------|-------------------|-----------------|
| Latin | 1x | Moderate | 1.4-1.5 |
| Arabic | 1.1-1.3x | Tall ascenders | 1.6-1.8 |
| Devanagari | 1.2-1.4x | Headline + descenders | 1.7-2.0 |
| CJK | 1x (square) | Uniform | 1.5-1.7 |
| Thai | 1.3-1.5x | Tall stacking marks | 1.8-2.0 |

### iOS Dynamic Type with Multilingual Fonts

```swift
// Use system font — it automatically selects the correct script variant
let label = UILabel()
label.font = UIFont.preferredFont(forTextStyle: .body)
label.adjustsFontForContentSizeCategory = true

// For custom fonts, provide script-specific variants
extension UIFont {
    static func customFont(
        forTextStyle style: UIFont.TextStyle,
        locale: Locale
    ) -> UIFont {
        let metrics = UIFontMetrics(forTextStyle: style)
        let baseFont: UIFont

        switch locale.script?.scriptCode {
        case "Arab":
            baseFont = UIFont(name: "CustomArabic", size: 17)!
        case "Deva":
            baseFont = UIFont(name: "CustomDevanagari", size: 17)!
        default:
            baseFont = UIFont(name: "CustomLatin", size: 16)!
        }

        return metrics.scaledFont(for: baseFont)
    }
}
```

### CSS Font Scaling for Multilingual

```css
/* Base responsive text */
body {
  font-size: clamp(1rem, 1rem + 0.5vw, 1.25rem);
  line-height: 1.5;
}

/* Arabic needs more line height */
:lang(ar), :lang(fa), :lang(ur) {
  line-height: 1.8;
  font-size: 1.1em; /* Slightly larger for readability */
}

/* Devanagari needs even more */
:lang(hi), :lang(mr), :lang(ne) {
  line-height: 2.0;
}

/* CJK: uniform height, tighter letter spacing */
:lang(ja), :lang(zh), :lang(ko) {
  line-height: 1.7;
  letter-spacing: 0.02em;
}
```

---

## Colour and Contrast Across Cultural Contexts

### Cultural Colour Associations

| Colour | Western | East Asian | Middle Eastern | South Asian |
|--------|---------|------------|----------------|-------------|
| Red | Danger, stop | Luck, prosperity | Danger | Purity (vermillion) |
| White | Purity, clean | Death, mourning | Purity | Death, mourning |
| Green | Nature, go | Youth | Islam, paradise | Fertility |
| Black | Death, formal | Power | Death | Evil |
| Yellow | Caution | Imperial, sacred | Happiness | Sacred (saffron) |

### Contrast Requirements Are Universal

WCAG contrast ratios apply regardless of script or language:

| Level | Normal Text | Large Text | UI Components |
|-------|------------|------------|---------------|
| AA | 4.5:1 | 3:1 | 3:1 |
| AAA | 7:1 | 4.5:1 | 4.5:1 |

```css
/* Test contrast with different scripts — some fonts render thinner */
/* Arabic calligraphic fonts may need higher contrast than Latin */
.arabic-body {
  color: #1a1a1a; /* Darker than typical #333 for thin strokes */
  background: #ffffff;
  /* Contrast ratio: 16.3:1 — well above AA */
}
```

---

## Keyboard Navigation for RTL Interfaces

### Tab Order in RTL

The DOM order determines tab order, not visual order. In RTL layouts where CSS changes visual position, tab order may become confusing.

```html
<!-- DOM order matches visual RTL order -->
<nav dir="rtl">
  <!-- Tab: right → left (matches RTL visual flow) -->
  <a href="/ar/home">الرئيسية</a>      <!-- Tab 1: rightmost -->
  <a href="/ar/about">عن الموقع</a>    <!-- Tab 2 -->
  <a href="/ar/contact">اتصل بنا</a>   <!-- Tab 3: leftmost -->
</nav>
```

### Arrow Key Behaviour

| Key | LTR Context | RTL Context |
|-----|-------------|-------------|
| Left Arrow | Previous item | Next item |
| Right Arrow | Next item | Previous item |
| Home | First item | First item (rightmost) |
| End | Last item | Last item (leftmost) |

```typescript
// Handle arrow keys in RTL-aware component
function handleKeyDown(event: KeyboardEvent, isRTL: boolean) {
  const forward = isRTL ? 'ArrowLeft' : 'ArrowRight';
  const backward = isRTL ? 'ArrowRight' : 'ArrowLeft';

  switch (event.key) {
    case forward:
      focusNext();
      break;
    case backward:
      focusPrevious();
      break;
  }
}
```

---

## Form Labels and Error Messages in Localised Contexts

### Label Association

```tsx
// Always use explicit label association — never rely on visual proximity
<div>
  <label htmlFor="email">{t('form.email.label')}</label>
  <input
    id="email"
    type="email"
    dir="ltr" // Email addresses are always LTR
    aria-describedby="email-hint"
    aria-errormessage={errors.email ? 'email-error' : undefined}
    aria-invalid={!!errors.email}
  />
  <span id="email-hint">{t('form.email.hint')}</span>
  {errors.email && (
    <span id="email-error" role="alert">
      {t(errors.email.messageKey)}
    </span>
  )}
</div>
```

### Error Message Translation Patterns

```typescript
// WRONG: Hardcoded error messages in validation schema
const schema = z.object({
  email: z.string().email('Invalid email address'),
});

// CORRECT: Use message keys, translate at render time
const schema = z.object({
  email: z.string().email({ message: 'form.email.invalid' }),
});

// In component
{errors.email && (
  <span role="alert">{t(errors.email.message)}</span>
)}
```

---

## Input Method Editor (IME) Accessibility

### IME for CJK Languages

CJK input requires an Input Method Editor that converts keystrokes into characters through a composition window.

| Platform | IME | Languages |
|----------|-----|-----------|
| macOS/iOS | Built-in | Japanese, Chinese, Korean |
| Windows | Microsoft IME, Google IME | Japanese, Chinese, Korean |
| Android | Gboard, Samsung Keyboard | CJK + Indic scripts |
| Linux | IBus, Fcitx | CJK + Indic scripts |

### Composition Events

```typescript
// Handle IME composition correctly
function SearchInput({ onSearch }: { onSearch: (q: string) => void }) {
  const [isComposing, setIsComposing] = useState(false);

  return (
    <input
      onCompositionStart={() => setIsComposing(true)}
      onCompositionEnd={(e) => {
        setIsComposing(false);
        onSearch(e.currentTarget.value);
      }}
      onKeyDown={(e) => {
        // Do NOT trigger search on Enter during IME composition
        if (e.key === 'Enter' && !isComposing) {
          onSearch(e.currentTarget.value);
        }
      }}
      onChange={(e) => {
        // Do not trigger live search during composition
        if (!isComposing) {
          onSearch(e.target.value);
        }
      }}
    />
  );
}
```

### Indic Script IME Considerations

Indic scripts (Devanagari, Tamil, Bengali, etc.) use transliteration-based IMEs where Latin keystrokes produce native script characters.

- Composition may produce multiple characters from a single keystroke
- Conjunct characters (ligatures) form during composition
- Cursor position may jump as ligatures form
- `maxLength` on inputs may be unreliable (one visual character = multiple Unicode code points)

```typescript
// Use grapheme-aware length counting for Indic scripts
function graphemeLength(text: string): number {
  const segmenter = new Intl.Segmenter(undefined, { granularity: 'grapheme' });
  return [...segmenter.segment(text)].length;
}

// Instead of: input.maxLength = 50
// Use: validation with grapheme count
if (graphemeLength(value) > 50) {
  setError(t('form.maxLength', { max: 50 }));
}
```

---

## WCAG Requirements for Multilingual Content

### WCAG 3.1: Language of Page and Parts

| Criterion | Level | Requirement |
|-----------|-------|-------------|
| 3.1.1 Language of Page | A | `lang` attribute on `<html>` element |
| 3.1.2 Language of Parts | AA | `lang` attribute on elements in a different language |
| 3.1.3 Unusual Words | AAA | Mechanism to identify jargon/idioms |
| 3.1.4 Abbreviations | AAA | Mechanism to identify abbreviations |
| 3.1.5 Reading Level | AAA | Supplemental content for complex text |
| 3.1.6 Pronunciation | AAA | Mechanism for pronunciation (ruby text for CJK) |

### Implementation Checklist

```html
<!-- 3.1.1: Language of page -->
<html lang="ar" dir="rtl">

<!-- 3.1.2: Language of parts -->
<p lang="ar">هذا النص بالعربية <span lang="en">with English</span> مرة أخرى</p>

<!-- 3.1.6: Ruby annotation for CJK pronunciation -->
<ruby lang="ja">
  漢字 <rp>(</rp><rt>かんじ</rt><rp>)</rp>
</ruby>
```

### Automated WCAG Checking Per Locale

```typescript
// tests/wcag-i18n.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const LOCALES = ['en', 'ar', 'ja', 'de'];

for (const locale of LOCALES) {
  test(`WCAG 3.1 compliance: ${locale}`, async ({ page }) => {
    await page.goto(`/${locale}/dashboard`);

    // Check lang attribute
    const lang = await page.locator('html').getAttribute('lang');
    expect(lang).toBe(locale);

    // Run axe for language-related rules
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .withRules(['html-has-lang', 'html-lang-valid', 'valid-lang'])
      .analyze();

    expect(results.violations).toHaveLength(0);
  });
}
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Missing `lang` attribute | Screen reader uses wrong pronunciation | Set `lang` on `<html>` and on inline language switches |
| Untranslated ARIA labels | Screen reader reads English on Arabic page | Translate all `aria-label`, `aria-description` |
| Fixed line-height for all scripts | Devanagari/Arabic text clips | Use script-aware line-height values |
| Ignoring IME composition events | Search triggers on every keystroke during CJK input | Check `isComposing` before acting on input |
| Same contrast ratio for all scripts | Thin Arabic strokes become illegible | Test contrast with actual script samples |
| Hardcoded tab order | Confusing navigation in RTL | Let DOM order match visual order |
| Missing `<bdi>` for user content | Garbled display of mixed-direction text | Wrap user-generated content in `<bdi>` |

---

## Cross-References

- [rtl-support.md](rtl-support.md) — CSS logical properties, Tailwind RTL, icon mirroring
- [testing-i18n.md](testing-i18n.md) — i18n test matrix, visual regression, pseudo-localisation
- [icu-message-format.md](icu-message-format.md) — Plural rules, select, formatting
- [locale-handling.md](locale-handling.md) — Date, number, currency formatting by locale
- [framework-guides.md](framework-guides.md) — Framework-specific i18n setup
