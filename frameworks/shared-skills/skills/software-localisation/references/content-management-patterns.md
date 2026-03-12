# Translation Content Management Patterns

Strategies for managing translation content at scale: translation memory, glossary management, context for translators, string key conventions, dynamic content, version control, linguistic QA, cost optimisation, and machine translation workflows.

---

## Overview

Translation management is an operational discipline, not just a file format problem. At scale, the difference between a well-managed translation pipeline and a chaotic one is measured in months of delay, thousands of dollars in rework, and degraded user experience. This reference covers the content management layer that sits between your codebase and your translators.

---

## Translation Memory (TM)

### How It Works

Translation Memory is a database of previously translated segments (source + target pairs). When a new string matches or partially matches an existing entry, the TM suggests the previous translation.

| Match Type | Definition | Typical Discount |
|-----------|-----------|-----------------|
| **100% match** | Exact same source text | 70-90% discount |
| **Context match (101%)** | Exact match + same surrounding context | 80-95% discount |
| **Fuzzy match (75-99%)** | Similar but not identical | 30-60% discount |
| **Repetition** | Same string appearing multiple times in the same batch | Same as 100% match |
| **No match (new)** | No prior translation exists | Full price |

### Leveraging TM for Cost Savings

```text
Strategy: Maximise reuse across projects

1. Maintain a master TM per language pair (en → de, en → ar, etc.)
2. Pre-translate new content against TM before sending to translators
3. Use TM across projects — "Save changes" translates the same everywhere
4. Clean TM periodically — remove outdated or low-quality entries
5. Import client/domain-specific TMs when onboarding a new vendor
```

### TM Quality Management

| Action | Frequency | Purpose |
|--------|-----------|---------|
| Export and back up TM | Monthly | Disaster recovery |
| Remove duplicate entries | Quarterly | Reduce noise in suggestions |
| Review low-rated segments | Quarterly | Improve future match quality |
| Merge project TMs into master | Per release | Centralise knowledge |
| Validate against glossary | Quarterly | Ensure term consistency |

### TM File Formats

| Format | Extension | Standard | Used By |
|--------|-----------|----------|---------|
| TMX | .tmx | LISA/OASIS | Most TMS, SDL Trados, memoQ |
| XLIFF | .xliff | OASIS | Apple, many TMS |
| TBX | .tbx | ISO 30042 | Terminology exchange |
| CSV | .csv | None | Simple import/export |

---

## Glossary Management

### Why Glossaries Matter

Without a glossary, different translators translate the same term differently. "Dashboard" might become "Armaturenbrett" in one place and "Übersicht" in another.

### Glossary Structure

| Field | Required | Example |
|-------|----------|---------|
| Source term | Yes | Dashboard |
| Target term | Yes | Tableau de bord (fr) |
| Part of speech | Recommended | Noun |
| Definition | Recommended | Main application overview page |
| Context | Recommended | Navigation, page title |
| Do Not Translate | Optional | TRUE (for brand names) |
| Notes | Optional | Always capitalised in UI |

### Example Glossary Entries

```json
[
  {
    "source": "Dashboard",
    "translations": {
      "de": "Dashboard",
      "fr": "Tableau de bord",
      "ja": "ダッシュボード",
      "ar": "لوحة المعلومات"
    },
    "pos": "noun",
    "definition": "Main application overview page showing key metrics",
    "doNotTranslate": false,
    "notes": "Always capitalised in UI context"
  },
  {
    "source": "API key",
    "translations": {
      "de": "API-Schlüssel",
      "fr": "Clé API",
      "ja": "APIキー",
      "ar": "مفتاح API"
    },
    "pos": "noun",
    "definition": "Authentication token for programmatic access",
    "doNotTranslate": false,
    "notes": "API is always in Latin characters"
  }
]
```

### Domain-Specific Terminology

| Domain | Example Terms | Challenge |
|--------|--------------|-----------|
| Finance | Invoice, credit, debit | Legal precision required |
| Healthcare | Diagnosis, prescription | Regulatory compliance |
| Legal | Terms of service, liability | Must match local legal language |
| Gaming | Achievement, quest, guild | Cultural adaptation needed |
| E-commerce | Cart, checkout, wishlist | Varies widely by market |

### Glossary Maintenance Workflow

```text
1. Extract new terms from each release's string diff
2. Review with subject matter experts (product, legal, domain)
3. Send to terminologist or senior translator for target language terms
4. Import approved terms into TMS glossary
5. Enable glossary enforcement in TMS (flag violations during translation)
6. Review glossary violations in QA step before release
```

---

## Context for Translators

### Why Context Reduces Rework

Translators working without context make assumptions that are often wrong. "Save" could mean "Save to disk" (Speichern) or "Save money" (Sparen) in German. Providing context eliminates round-trip corrections.

### Context Types

| Context Type | Format | When to Use |
|-------------|--------|-------------|
| Screenshots | PNG/URL | Always for UI strings |
| Description | Text | Always for ambiguous strings |
| Character limit | Number | Buttons, headers, labels |
| Placeholder example | Text | Interpolated strings |
| Gender context | Text | Gendered languages |
| Plural context | Text | Strings with count variables |

### Providing Context in Code

```typescript
// i18next: Use context and description in extraction config
// i18next-parser extracts these as developer comments
t('save_button', {
  // i18next-extract-mark-context-next-line description: "Button to save user profile changes"
  // i18next-extract-mark-context-next-line maxLength: 10
  defaultValue: 'Save',
});

// FormatJS: Use description in message descriptor
const messages = defineMessages({
  saveButton: {
    id: 'profile.save',
    defaultMessage: 'Save',
    description: 'Button to save user profile changes. Max 10 characters.',
  },
});
```

### Screenshot Automation

```typescript
// Generate translator screenshots in CI
// tests/translator-screenshots.spec.ts
import { test } from '@playwright/test';

const SCREENSHOT_TARGETS = [
  { page: '/settings', elements: ['save-button', 'cancel-button', 'settings-header'] },
  { page: '/dashboard', elements: ['metric-card', 'nav-item', 'search-input'] },
];

for (const target of SCREENSHOT_TARGETS) {
  test(`translator screenshots: ${target.page}`, async ({ page }) => {
    await page.goto(target.page);

    for (const elementId of target.elements) {
      const el = page.locator(`[data-testid="${elementId}"]`);
      await el.screenshot({
        path: `translator-context/${target.page.slice(1)}-${elementId}.png`,
      });
    }
  });
}
```

---

## String Key Naming Conventions

### Convention Comparison

| Convention | Example | Pros | Cons |
|-----------|---------|------|------|
| **Namespaced** | `auth.login.button` | Clear scope | Verbose |
| **Hierarchical** | `auth:login.submitButton` | Namespace separation | Mixed separators |
| **Semantic** | `action.save` | Reusable | Ambiguous without context |
| **Page-based** | `dashboard.metrics.title` | Easy to locate | Limits reuse |
| **Content hash** | `abc123` | No key conflicts | Unreadable |

### Recommended Convention

```text
{namespace}.{component}.{element}[.{variant}]

Examples:
  common.button.save
  common.button.cancel
  common.button.delete
  auth.login.title
  auth.login.emailLabel
  auth.login.emailPlaceholder
  auth.login.error.invalidCredentials
  dashboard.metrics.totalUsers
  dashboard.metrics.revenue.monthly
```

### Key Naming Rules

| Rule | Example | Rationale |
|------|---------|-----------|
| Use camelCase for segments | `auth.loginButton` | Consistent with JS conventions |
| Keep keys stable across releases | Never rename without migration | Breaks TM matching |
| No UI text in keys | `auth.login.title` not `auth.login.welcomeBack` | Text changes, keys should not |
| Group by feature, not page | `billing.invoice.title` | Enables code splitting |
| Prefix shared strings | `common.button.save` | Clear reuse intent |

---

## Handling Dynamic Content

### Content Types and Strategies

| Content Type | Translation Strategy | Update Frequency |
|-------------|---------------------|-----------------|
| UI strings | Standard i18n files | Per release |
| CMS content | TMS API integration | Per publish |
| User-generated | MT + moderation | Real-time |
| Legal/compliance | Certified translation | Per regulation change |
| Marketing | Creative translation | Per campaign |
| Transactional email | Template + variables | Per release |
| Help articles | Full translation | Per update |

### CMS Integration Patterns

```typescript
// Pattern: CMS webhook triggers translation
// Contentful → Webhook → TMS → Translated → Publish

// Contentful webhook handler
export async function handleContentUpdate(entry: ContentfulEntry) {
  const sourceLocale = 'en-US';
  const targetLocales = ['de', 'fr', 'ja', 'ar'];

  // Extract translatable fields
  const translatableFields = extractTranslatableFields(entry);

  // Send to TMS via API
  await tmsClient.createTranslationJob({
    sourceLocale,
    targetLocales,
    content: translatableFields,
    callbackUrl: `${API_URL}/webhooks/translation-complete`,
    context: {
      contentType: entry.sys.contentType.sys.id,
      entryId: entry.sys.id,
      screenshot: `${CMS_PREVIEW_URL}/${entry.sys.id}`,
    },
  });
}
```

### Legal and Compliance Content

```text
Legal translation requirements:
1. Use certified/sworn translators (not general translators)
2. Maintain version history with effective dates
3. Back-translation for verification (translate back to source, compare)
4. Legal review in target jurisdiction
5. Store signed-off versions separately from general translations
6. Track regulatory changes per market
```

---

## Version Control for Translations

### Branching Strategies

| Strategy | How It Works | Best For |
|----------|-------------|----------|
| **Release-based** | Translations branch with code release | Fixed release cycles |
| **Continuous** | Translations merged to main continuously | Continuous deployment |
| **Feature-branch** | New strings on feature branch, translated before merge | Feature teams |

### Release-Based Workflow

```text
1. Feature development on feature branches
   └─ New strings added with default English values

2. Strings extracted at release branch cut
   └─ npx i18next-parser → diff shows new/changed keys

3. New keys sent to TMS for translation
   └─ Translators work from branch snapshot

4. Translations returned and committed to release branch
   └─ PR with translated files

5. Release ships with complete translations
   └─ Missing keys blocked by CI check

6. Hotfix: emergency strings get expedited translation
   └─ Use MT + human review for speed
```

### Git Workflow for Translation Files

```bash
# .gitattributes — mark translation files for merge strategy
locales/**/*.json merge=ours  # Prefer local changes (TMS is source of truth)

# Alternatively, exclude translation files from normal diff
locales/**/*.json linguist-generated=true
```

---

## Quality Assurance

### Linguistic QA Tools

| Tool | Type | What It Checks |
|------|------|---------------|
| Xbench | Desktop | Consistency, glossary, formatting, untranslated |
| Verifika | Desktop | Similar to Xbench, CAT integration |
| QA Distiller | Desktop | Advanced QA rules, regex |
| TMS built-in QA | Cloud | Most TMS have basic QA (Phrase, Lokalise, Crowdin) |
| Custom scripts | CI | Project-specific rules |

### QA Check Categories

| Check | What It Detects | Severity |
|-------|----------------|----------|
| Untranslated segments | Source text left as-is | Critical |
| Glossary violations | Wrong term used | High |
| Placeholder mismatch | `{name}` missing in target | Critical |
| Punctuation consistency | Missing period, extra space | Medium |
| Number formatting | Wrong decimal/thousand separator | High |
| Tag integrity | Missing/broken HTML tags | Critical |
| Length violation | Exceeds character limit | High |
| Consistency | Same source, different target | Medium |

### In-Context Review

```text
In-context review workflow:
1. Deploy translated build to staging/preview environment
2. Provide reviewers with locale-specific URLs
3. Reviewers flag issues directly in context (screenshot + annotation)
4. Issues routed back to translators with visual context
5. Fixes verified in next preview build
```

### Back-Translation

Back-translation is the process of translating the target text back into the source language by an independent translator. It is used for:
- Legal and medical content verification
- Detecting meaning shifts that a bilingual reviewer might miss
- Compliance requirements in regulated industries

---

## Cost Optimisation

### Reuse Rate Benchmarks

| Reuse Rate | Assessment | Action |
|-----------|-----------|--------|
| < 20% | Low | Review key naming, check for duplicate strings |
| 20-40% | Average | Standardise common UI patterns |
| 40-60% | Good | Healthy codebase with shared components |
| 60-80% | Excellent | Strong design system, stable UI |
| > 80% | Exceptional | Mature product with incremental updates |

### Cost Reduction Strategies

| Strategy | Savings | Trade-off |
|----------|---------|-----------|
| **Pre-translate with TM** | 30-60% | Requires TM maintenance |
| **Reuse common strings** | 10-20% | Needs string deduplication discipline |
| **Batch translations** | 10-15% | Delays vs continuous delivery |
| **MT + post-editing** | 40-60% | Quality depends on language pair |
| **Tiered quality** | 20-40% | Marketing = creative; UI = standard; legal = certified |
| **Reduce source word count** | Variable | Shorter strings = lower cost + better UX |

### Batch vs Continuous Translation

| Approach | Latency | Cost | Best For |
|----------|---------|------|----------|
| **Batch** (weekly/bi-weekly) | 3-7 days | Lower per-word (volume discount) | Fixed release cycles |
| **Continuous** (per-commit) | 1-24 hours | Higher per-word | Continuous deployment |
| **Hybrid** | 1-3 days | Moderate | Most teams |

---

## Machine Translation + Human Review (MTPE)

### MTPE Quality Tiers

| Tier | Process | Use Case | Quality |
|------|---------|----------|---------|
| **Raw MT** | Machine only | Internal, developer docs | Low-medium |
| **Light PE** | MT + quick human scan | Help articles, low-visibility UI | Medium |
| **Full PE** | MT + thorough human review | Product UI, marketing | High |
| **Creative** | Human from scratch | Brand, legal, marketing headlines | Highest |

### MT Engine Comparison

| Engine | Strengths | Weaknesses | Integration |
|--------|-----------|------------|-------------|
| Google Translate API | Wide language coverage | Variable quality for rare pairs | REST API, TMS plugins |
| DeepL API | European language quality | Limited language coverage | REST API, TMS plugins |
| AWS Translate | Good for technical content | Fewer languages than Google | AWS SDK, TMS plugins |
| Azure Translator | Microsoft ecosystem | Variable quality | REST API, TMS plugins |
| Custom NMT | Domain-specific quality | Training data required | Self-hosted or cloud |

### MTPE Workflow

```text
1. Extract new strings (CI/CD)
2. Pre-translate with TM (100% and fuzzy matches)
3. Run MT on remaining new strings
4. Route to human reviewers:
   - 100% TM matches → skip review (unless quality flag)
   - Fuzzy matches → review required
   - MT output → full post-edit
   - Creative/legal → human translation from scratch
5. QA checks (automated + human)
6. Commit translated files
7. In-context review on staging
8. Release
```

### Cost Model Example

```text
Scenario: 10,000 new words per month, 10 target languages

Without MTPE:
  10,000 words × 10 languages × $0.12/word = $12,000/month

With MTPE (assuming 40% TM match, 40% MT+PE, 20% human):
  TM matches: 4,000 × 10 × $0.02 = $800
  MT + PE:    4,000 × 10 × $0.06 = $2,400
  Human:      2,000 × 10 × $0.12 = $2,400
  Total:      $5,600/month (53% savings)
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| No translation memory | Paying to translate the same string twice | Set up TM from day one |
| No glossary | Inconsistent terminology across screens | Create and enforce glossary |
| Sending strings without context | Rework rate of 20-30% | Attach screenshots and descriptions |
| Key names based on English text | Keys change when text changes, breaking TM | Use semantic, stable key names |
| Translating everything at the same quality tier | Overspending on low-visibility content | Tier content by quality requirement |
| No in-context review | Translations that look wrong in the UI | Deploy to preview environment for review |
| Ignoring TM maintenance | Stale/incorrect suggestions | Clean TM quarterly |
| Manual translation file management | Merge conflicts, lost translations | Use TMS with API integration |

---

## Cross-References

- [translation-workflows.md](translation-workflows.md) — CI/CD pipelines, string extraction, TMS integration
- [icu-message-format.md](icu-message-format.md) — Plural rules, select, number/date formatting
- [testing-i18n.md](testing-i18n.md) — Missing translation CI detection, visual regression
- [framework-guides.md](framework-guides.md) — Framework-specific i18n setup
- [rtl-support.md](rtl-support.md) — RTL support patterns
