# Cultural Design Patterns

Design patterns for international products across Western, Eastern, RTL, and regional markets.

**Last Updated**: January 2026
**References**: [W3C Internationalization](https://www.w3.org/International/), [Nielsen Norman Group - International UX](https://www.nngroup.com/articles/international-ux/), [Baymard Institute - International E-commerce](https://baymard.com/)

---

## Quick Reference: Regional Patterns

| Region | Layout | Information Density | Color Caution | Payment |
|--------|--------|---------------------|---------------|---------|
| Western (US/EU) | Minimal, whitespace | Low-medium | Red = error/danger | Card, PayPal |
| East Asia (CN/JP/KR) | Dense, information-rich | High | White = death/mourning | WeChat Pay, Alipay |
| Middle East (MENA) | RTL layout | Medium | Green = sacred | Cash on delivery |
| South Asia | Colorful, busy | High | Saffron = sacred | UPI, mobile wallets |
| Latin America | Warm, expressive | Medium | Yellow varies | Installments common |

---

## Right-to-Left (RTL) Languages

**Languages**: Arabic, Hebrew, Persian/Farsi, Urdu, Pashto

### Layout Mirroring

**What Flips**
```css
/* RTL base styles */
[dir="rtl"] {
  /* Text and inline elements */
  direction: rtl;
  text-align: right; /* Start position */

  /* Layout */
  /* Flexbox and Grid auto-flip with dir="rtl" */
}

/* Logical properties (preferred) */
.container {
  /* Instead of margin-left, use: */
  margin-inline-start: 1rem;

  /* Instead of padding-right, use: */
  padding-inline-end: 1rem;

  /* Instead of border-left, use: */
  border-inline-start: 2px solid;
}
```

**What Does NOT Flip**
| Element | Rule |
|---------|------|
| Phone numbers | Always LTR (+1-555-0123) |
| Dates with numbers | LTR (25/01/2026) |
| Code/technical | Always LTR |
| Brand logos | Usually don't flip |
| Media playback controls | Play arrow = forward (universal) |
| Progress bars | Direction = progress direction |

### Icon Direction

| Icon Type | Flip? | Example |
|-----------|-------|---------|
| Arrows (back/forward) | Yes | Back arrow points right in RTL |
| Checkmarks | No | Universal symbol |
| Search | No | Magnifying glass universal |
| User/profile | No | Human figure universal |
| Chat bubbles | Yes | Tail points to speaker |
| Quote marks | Yes | "text" becomes «text» |
| Lists/bullets | Yes | Bullets on right |
| Progress indicators | Yes | Start from right |
| Sliders | Yes | Min on right, max on left |

### RTL Implementation Checklist

```
LAYOUT:
- [ ] dir="rtl" on html or body element
- [ ] lang attribute correct (ar, he, fa, ur)
- [ ] CSS uses logical properties (inline-start/end)
- [ ] Flexbox/Grid auto-flip with direction
- [ ] Scrollbars on left side (browser handles)

CONTENT:
- [ ] Text aligned to start (right in RTL)
- [ ] Numbers in correct direction (LTR within RTL)
- [ ] Currency symbol position (varies by locale)
- [ ] Date format localized

ICONS:
- [ ] Directional icons flipped
- [ ] Non-directional icons unchanged
- [ ] Icon + text alignment correct

FORMS:
- [ ] Labels on right of inputs
- [ ] Error messages aligned right
- [ ] Dropdown arrows flip
- [ ] Calendar week starts on correct day
```

### Bidirectional Text (Bidi)

```html
<!-- Mixed LTR and RTL content -->
<p dir="rtl">
  النص العربي
  <span dir="ltr">English text</span>
  المزيد من العربية
</p>

<!-- Use unicode bidi controls for complex cases -->
<p dir="rtl">
  سعر المنتج:
  <bdo dir="ltr">$99.99</bdo>
</p>
```

---

## East Asian Markets (China, Japan, Korea)

### China (Simplified Chinese)

**Design Characteristics**
| Aspect | Pattern |
|--------|---------|
| Information density | High - users expect comprehensive info |
| Visual style | Red/gold for prosperity, rich imagery |
| Navigation | Tab-heavy, feature-rich homepages |
| Trust signals | Licenses, certifications prominent |
| Social proof | User counts, reviews essential |

**Color Symbolism**
```
RED: Lucky, prosperous, celebratory
  - Use for: CTAs, promotions, holidays
  - Avoid for: Errors (use yellow/orange)

WHITE: Death, mourning
  - Avoid for: Celebrations, packaging
  - OK for: Clean UI backgrounds

GOLD/YELLOW: Wealth, royalty
  - Use for: Premium, VIP features

GREEN: Health, harmony, growth
  - Use for: Success, nature, health products

BLACK: Power, authority
  - Use for: Luxury, professional
```

**Platform Integration**
```
REQUIRED for China:
- WeChat integration (login, pay, share)
- Alipay payment
- Phone number login (vs email)
- QR code everything
- Mini-program consideration

AVOID:
- Facebook, Google, Twitter references
- Foreign payment methods only
- Email-only registration
```

**UI Patterns**
- Floating customer service button
- Real-time visitor counts ("52 people viewing")
- Countdown timers for promotions
- Dense product grids with lots of info
- Video in product pages common

### Japan

**Design Characteristics**
| Aspect | Pattern |
|--------|---------|
| Visual style | Clean but detailed, anime influence OK |
| Quality signals | Manufacturing details, materials |
| Service | Extensive, polite, formal |
| Text density | High - thorough explanations |
| Kawaii culture | Cute characters for any brand |

**Cultural Considerations**
```
AESTHETICS:
- Attention to detail critical
- Seasonal themes expected (cherry blossom, fall leaves)
- Cute characters acceptable for professional brands
- Clean, organized layouts valued

COMMUNICATION:
- Formal language (keigo) for businesses
- Indirect communication style
- Apologies expected for any inconvenience
- Detailed instructions appreciated

NUMBERS:
- 4 (shi) sounds like "death" - avoid
- 7 (nana) is lucky
- Price ending in ¥00 or ¥80 common
```

**Date/Time**
```
Format: YYYY年MM月DD日
Example: 2026年01月09日

Time: 24-hour common
Era dating: Still used (Reiwa 8 = 2026)
Week start: Sunday (traditionally), Monday (business)
```

### Korea

**Design Characteristics**
| Aspect | Pattern |
|--------|---------|
| Trend sensitivity | K-wave influence, modern aesthetics |
| Speed | Fast loading critical |
| Age verification | Required for many services (19+) |
| Identity | Real-name system (KISA) |
| Messaging | KakaoTalk dominant |

**Platform Requirements**
```
KOREA-SPECIFIC:
- KakaoTalk login/share
- Naver integration
- Korean won (₩) formatting
- Real-name identity verification
- Age verification system
- Mobile-first (high smartphone usage)
```

---

## Middle East & North Africa (MENA)

### Regional Patterns

**Design Characteristics**
| Aspect | Pattern |
|--------|---------|
| Layout | RTL primary (Arabic) |
| Color | Green highly respected |
| Imagery | Modest dress, family-oriented |
| Payment | Cash on delivery popular |
| Time | Weekend = Friday-Saturday (varies) |

**Color Symbolism**
```
GREEN: Sacred in Islam, prosperity
  - Use for: Trust, success, nature
  - Handle respectfully

BLUE: Protection, calm
  - Safe choice for most uses

WHITE: Purity, cleanliness
  - Good for backgrounds

GOLD: Luxury, prestige
  - Use for premium features

RED: Caution - varies by context
  - Not universally negative
```

**Calendar Considerations**
```
ISLAMIC CALENDAR:
- Hijri dates for religious contexts
- Show both Gregorian and Hijri when relevant
- Ramadan UI considerations (night activity spike)
- Friday = main prayer day (reduced business hours)

REGIONAL WEEKENDS:
- UAE, Saudi: Friday-Saturday
- Israel: Saturday (Shabbat)
- Turkey: Saturday-Sunday (Western)
```

**Content Sensitivity**
```
IMAGERY:
- Modest dress in photos
- Family-friendly content
- Religious symbols with respect
- Local faces and scenarios

AVOID:
- Alcohol imagery (many countries)
- Pork products
- Left-hand gestures in icons
- Political content
```

---

## South Asia (India, Pakistan, Bangladesh)

### India

**Design Characteristics**
| Aspect | Pattern |
|--------|---------|
| Visual style | Colorful, festive, busy |
| Language | English + Hindi + regional |
| Price sensitivity | Value emphasis, EMI options |
| Mobile | Mobile-first, low bandwidth |
| Trust | COD, brand reputation |

**Color Symbolism**
```
SAFFRON: Sacred, auspicious
  - Use respectfully

RED: Marriage, fertility, prosperity
  - Positive connotations

WHITE: Mourning in some contexts
  - Avoid for celebrations

GREEN: Islam, nature, prosperity
  - Positive

YELLOW: Knowledge, learning
  - Good for education

BLUE: Trust, calm (Krishna association)
  - Safe professional choice
```

**Localization Requirements**
```
LANGUAGE:
- English + Hindi at minimum
- Regional languages by market (Tamil, Bengali, etc.)
- Script support: Devanagari, Tamil, etc.

NUMBERS:
- Indian numbering: 1,00,000 (1 lakh) vs 100,000
- Crore = 10 million

PAYMENT:
- UPI dominant (PhonePe, GPay, Paytm)
- Cash on delivery still popular
- EMI options expected for >₹5000
```

**Festival Calendar**
```
MAJOR (Pan-Indian):
- Diwali (October/November) - biggest
- Holi (March) - color festival
- Independence Day (August 15)

REGIONAL:
- Durga Puja (Bengal)
- Pongal (Tamil Nadu)
- Onam (Kerala)
- Eid (Muslim community)
```

---

## Latin America

### Regional Patterns

**Design Characteristics**
| Aspect | Pattern |
|--------|---------|
| Visual style | Warm colors, expressive |
| Language | Spanish (varies) + Portuguese (Brazil) |
| Payment | Installments (parcelamento) |
| Trust | Local brands, cash options |
| Social | WhatsApp dominant |

**Country Variations**
```
BRAZIL:
- Portuguese (different from Portugal)
- Boleto payment essential
- CPF number required
- High social media usage
- PIX instant payment (2020+)

MEXICO:
- Mexican Spanish (different vocabulary)
- OXXO cash payment
- Telcel carrier billing
- Strong US influence
- SPEI bank transfers

ARGENTINA:
- Currency volatility awareness
- Mercado Pago dominant
- High inflation pricing
- Installment culture
```

**Trust Signals**
```
ESSENTIAL:
- Local phone number
- Local address (even virtual)
- Spanish/Portuguese customer service
- WhatsApp support
- Cash payment options
- Installment options
```

---

## Western Markets (US/EU)

### North America

**Design Characteristics**
| Aspect | Pattern |
|--------|---------|
| Visual style | Clean, minimal, efficient |
| Information | Progressive disclosure |
| Privacy | CCPA compliance |
| Payment | Card, Apple/Google Pay |
| Speed | Fast loading expected |

**US vs Canada**
```
DIFFERENCES:
- Units: Imperial (US) vs Metric (Canada)
- French requirement in Canada (Quebec)
- Privacy: CCPA (CA) vs PIPEDA (Canada)
- Currency: USD vs CAD
- Date: MM/DD/YYYY (US) vs DD/MM/YYYY (Canada, sometimes)
```

### European Union

**Design Characteristics**
| Aspect | Pattern |
|--------|---------|
| Privacy | GDPR strict compliance |
| Accessibility | EAA 2025 requirements |
| Languages | Per-country localization |
| Payment | SEPA, local methods |
| Consumer rights | Strong protections |

**GDPR UI Requirements**
```
REQUIRED:
- Cookie consent banner
- Privacy policy accessible
- Data export capability
- Account deletion option
- Consent separate from T&C
- No pre-checked opt-ins

UI PATTERNS:
- Cookie banner with granular controls
- "Do Not Sell" link (CCPA-like for some)
- Data request form
- Unsubscribe in every email
```

**Country Specifics**
| Country | Language | Currency | Payment |
|---------|----------|----------|---------|
| Germany | German | EUR | SEPA, PayPal, Klarna |
| France | French | EUR | Carte Bancaire |
| UK | English | GBP | Card, PayPal |
| Netherlands | Dutch | EUR | iDEAL (90% of online) |
| Poland | Polish | PLN | BLIK, Przelewy24 |

---

## Implementation Guide

### Locale Detection & Switching

```typescript
interface LocaleConfig {
  // Display
  language: string;        // ISO 639-1 (en, zh, ar)
  region: string;          // ISO 3166-1 (US, CN, SA)
  direction: 'ltr' | 'rtl';

  // Formatting
  dateFormat: string;      // 'MM/DD/YYYY', 'DD.MM.YYYY', etc.
  timeFormat: '12h' | '24h';
  numberFormat: string;    // '1,234.56', '1.234,56', '1 234,56'
  currency: string;        // ISO 4217

  // Calendar
  weekStart: 0 | 1 | 6;    // Sunday=0, Monday=1, Saturday=6
  calendar: 'gregorian' | 'islamic' | 'japanese';
}
```

### Content Localization Checklist

```
TEXT:
- [ ] Translated by native speakers (not just tools)
- [ ] Cultural adaptation (not literal translation)
- [ ] Local idioms and expressions
- [ ] Appropriate formality level
- [ ] Text expansion room (German ~30% longer)

DATES & NUMBERS:
- [ ] Date format localized
- [ ] Number separators correct
- [ ] Currency symbol and position
- [ ] Units (metric vs imperial)
- [ ] Phone number format

IMAGERY:
- [ ] Local faces and scenarios
- [ ] Culturally appropriate dress
- [ ] Local landmarks/settings
- [ ] Color symbolism checked
- [ ] Hand gestures verified

LEGAL:
- [ ] Privacy policy localized
- [ ] Terms for local jurisdiction
- [ ] Age verification where required
- [ ] Consumer rights compliance
```

### Payment Method Matrix

| Region | Primary | Secondary | Cash |
|--------|---------|-----------|------|
| US | Card | PayPal, Apple Pay | No |
| EU | SEPA | PayPal, local | No |
| China | WeChat Pay | Alipay | No |
| Japan | Credit card | Konbini, PayPay | Yes (konbini) |
| India | UPI | Cards, wallets | COD |
| Brazil | PIX | Boleto, card | Boleto |
| MENA | Card | Cash on delivery | COD |
| LatAm | Installments | Local methods | Yes |

---

## Testing Across Cultures

### Localization Testing

```
FUNCTIONAL:
- All text displays correctly
- RTL layout renders properly
- Date/time/currency formatted
- Links to local content work
- Payment methods functional

LINGUISTIC:
- No truncation of translated text
- No mixed language fragments
- Appropriate tone/formality
- No cultural faux pas

CULTURAL:
- Imagery appropriate
- Colors acceptable
- Symbols universal or adapted
- Navigation intuitive for culture
```

### Cultural Review Checklist

- [ ] Native speaker review
- [ ] Cultural consultant for sensitive markets
- [ ] Legal compliance per jurisdiction
- [ ] Payment methods tested with real transactions
- [ ] Customer support in local language available

---

## Related Resources

- [Demographic-Inclusive Design](demographic-inclusive-design.md) - Age-specific patterns
- [WCAG Accessibility](wcag-accessibility.md) - Accessibility standards
- [Design Systems](design-systems.md) - Building scalable systems
