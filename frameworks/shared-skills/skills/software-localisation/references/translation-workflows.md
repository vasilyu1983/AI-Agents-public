# Translation Workflows

Production patterns for string extraction, TMS integration, and CI/CD pipelines.

---

## String Extraction

### i18next-parser

Extract translation keys from React, Vue, and TypeScript codebases.

```bash
npm install -D i18next-parser
```

```javascript
// i18next-parser.config.js
module.exports = {
  locales: ['en', 'de', 'fr', 'ar'],
  output: 'public/locales/$LOCALE/$NAMESPACE.json',
  input: ['src/**/*.{ts,tsx,js,jsx}'],

  // Key extraction patterns
  lexers: {
    tsx: ['JsxLexer'],
    ts: ['JavascriptLexer'],
  },

  // Namespace from file path
  namespaceSeparator: ':',
  keySeparator: '.',

  // Keep existing translations
  keepRemoved: false,

  // Sort keys alphabetically
  sort: true,

  // Default value for new keys
  defaultValue: (locale, namespace, key) => {
    return locale === 'en' ? key : '';
  },
};
```

```bash
# Run extraction
npx i18next-parser

# Watch mode
npx i18next-parser --watch
```

### FormatJS CLI (@formatjs/cli)

Extract and compile ICU messages for react-intl.

```bash
npm install -D @formatjs/cli
```

```bash
# Extract messages
npx formatjs extract 'src/**/*.tsx' \
  --out-file lang/en.json \
  --id-interpolation-pattern '[sha512:contenthash:base64:6]' \
  --format simple

# Compile for production (AST)
npx formatjs compile lang/en.json \
  --out-file compiled-lang/en.json \
  --ast
```

### Lingui CLI

Extract and compile for LinguiJS.

```bash
# Extract messages
npx lingui extract

# Compile catalogs
npx lingui compile

# Extract and compile
npx lingui extract && npx lingui compile
```

---

## Translation Management Systems (TMS)

### Phrase Integration

Enterprise TMS with GitHub/GitLab sync.

```yaml
# .phrase.yml
phrase:
  access_token: ${PHRASE_ACCESS_TOKEN}
  project_id: your-project-id
  push:
    sources:
      - file: ./public/locales/en/*.json
        params:
          locale_id: en
          file_format: simple_json
  pull:
    targets:
      - file: ./public/locales/<locale_name>/<tag>.json
        params:
          file_format: simple_json
```

```bash
# Push source strings
phrase push

# Pull translations
phrase pull

# Install CLI
brew install phrase-cli
```

**GitHub Action:**

```yaml
# .github/workflows/phrase-sync.yml
name: Phrase Sync
on:
  push:
    branches: [main]
    paths:
      - 'public/locales/en/**'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Push to Phrase
        uses: phrase/phrase-cli-action@v2
        with:
          command: push
        env:
          PHRASE_ACCESS_TOKEN: ${{ secrets.PHRASE_ACCESS_TOKEN }}
```

### Lokalise Integration

Developer-friendly TMS with Figma plugin.

```bash
# Install CLI
npm install -g @lokalise/cli
```

```yaml
# lokalise.yml
lokalise:
  token: ${LOKALISE_API_TOKEN}
  project_id: your-project-id

upload:
  file: ./public/locales/en/*.json
  lang_iso: en
  replace_modified: true
  convert_placeholders: true

download:
  format: json
  dest: ./public/locales/%LANG_ISO%/
  export_empty_as: skip
  placeholder_format: icu
```

```bash
# Push source
lokalise2 file upload --config lokalise.yml

# Pull translations
lokalise2 file download --config lokalise.yml
```

**GitHub Action:**

```yaml
# .github/workflows/lokalise-sync.yml
name: Lokalise Sync
on:
  push:
    branches: [main]
    paths:
      - 'public/locales/en/**'

jobs:
  upload:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Upload to Lokalise
        uses: lokalise/lokalise-upload-action@v1
        with:
          api_token: ${{ secrets.LOKALISE_API_TOKEN }}
          project_id: ${{ secrets.LOKALISE_PROJECT_ID }}
          file: public/locales/en/common.json
          lang_iso: en
```

### Crowdin Integration

Community-focused with open source free tier.

```yaml
# crowdin.yml
project_id: your-project-id
api_token: ${CROWDIN_API_TOKEN}
base_path: .
base_url: https://api.crowdin.com

preserve_hierarchy: true

files:
  - source: /public/locales/en/*.json
    translation: /public/locales/%two_letters_code%/%original_file_name%
    type: json
```

```bash
# Install CLI
npm install -g @crowdin/cli

# Upload sources
crowdin upload sources

# Download translations
crowdin download
```

**GitHub Action:**

```yaml
# .github/workflows/crowdin.yml
name: Crowdin Sync
on:
  push:
    branches: [main]

jobs:
  synchronize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Crowdin Sync
        uses: crowdin/github-action@v1
        with:
          upload_sources: true
          download_translations: true
          create_pull_request: true
        env:
          CROWDIN_PROJECT_ID: ${{ secrets.CROWDIN_PROJECT_ID }}
          CROWDIN_PERSONAL_TOKEN: ${{ secrets.CROWDIN_PERSONAL_TOKEN }}
```

---

## CI/CD Pipelines

### GitHub Actions: Full Workflow

```yaml
# .github/workflows/i18n.yml
name: i18n Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # 1. Validate translations
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Extract and check for new keys
        run: |
          npx i18next-parser
          git diff --exit-code public/locales/en/ || echo "::warning::New translation keys detected"

      - name: Validate ICU syntax
        run: npx formatjs compile-folder public/locales/en --ast

      - name: Check for missing translations
        run: node scripts/check-translations.js

  # 2. Push to TMS (main branch only)
  push-translations:
    runs-on: ubuntu-latest
    needs: validate
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Push to Phrase
        uses: phrase/phrase-cli-action@v2
        with:
          command: push
        env:
          PHRASE_ACCESS_TOKEN: ${{ secrets.PHRASE_ACCESS_TOKEN }}

  # 3. Pull translations (scheduled)
  pull-translations:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    steps:
      - uses: actions/checkout@v4

      - name: Pull from Phrase
        uses: phrase/phrase-cli-action@v2
        with:
          command: pull
        env:
          PHRASE_ACCESS_TOKEN: ${{ secrets.PHRASE_ACCESS_TOKEN }}

      - name: Create PR with translations
        uses: peter-evans/create-pull-request@v5
        with:
          title: '[i18n] Update translations'
          commit-message: 'chore(i18n): update translations from Phrase'
          branch: i18n/update-translations
          labels: i18n, automated
```

### Translation Validation Script

```javascript
// scripts/check-translations.js
const fs = require('fs');
const path = require('path');

const localesDir = './public/locales';
const sourceLocale = 'en';
const targetLocales = ['de', 'fr', 'ar'];

const sourceFiles = fs.readdirSync(path.join(localesDir, sourceLocale));
const issues = [];

for (const file of sourceFiles) {
  const sourcePath = path.join(localesDir, sourceLocale, file);
  const sourceKeys = Object.keys(JSON.parse(fs.readFileSync(sourcePath, 'utf8')));

  for (const locale of targetLocales) {
    const targetPath = path.join(localesDir, locale, file);

    if (!fs.existsSync(targetPath)) {
      issues.push(`Missing file: ${locale}/${file}`);
      continue;
    }

    const targetKeys = Object.keys(JSON.parse(fs.readFileSync(targetPath, 'utf8')));
    const missingKeys = sourceKeys.filter((key) => !targetKeys.includes(key));

    if (missingKeys.length > 0) {
      issues.push(`${locale}/${file}: Missing ${missingKeys.length} keys`);
      missingKeys.forEach((key) => console.log(`  - ${key}`));
    }
  }
}

if (issues.length > 0) {
  console.error('\nFAIL Translation issues found:');
  issues.forEach((issue) => console.error(`  - ${issue}`));
  process.exit(1);
} else {
  console.log('PASS All translations complete');
}
```

### GitLab CI Pipeline

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - sync

variables:
  NODE_VERSION: '20'

validate-i18n:
  stage: validate
  image: node:${NODE_VERSION}
  script:
    - npm ci
    - npx i18next-parser
    - node scripts/check-translations.js
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

push-to-tms:
  stage: sync
  image: node:${NODE_VERSION}
  script:
    - npm install -g phrase-cli
    - phrase push
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      changes:
        - public/locales/en/**/*
```

---

## Git Workflow Patterns

### Branch-Based Translation Workflow

```text
main
├── feature/add-checkout-flow
│   └── Extract new keys -> Push to TMS
│
└── i18n/update-translations (automated)
    └── Pull from TMS -> Create PR
```

### Monorepo Pattern

```yaml
# turbo.json (Turborepo)
{
  "pipeline": {
    "i18n:extract": {
      "dependsOn": ["^build"],
      "outputs": ["public/locales/**"]
    },
    "i18n:push": {
      "dependsOn": ["i18n:extract"]
    }
  }
}
```

```bash
# Extract from all packages
turbo run i18n:extract

# Push to TMS
turbo run i18n:push
```

### Pre-commit Hook

```bash
# .husky/pre-commit
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

# Extract and stage new translation keys
npx i18next-parser
git add public/locales/en/
```

---

## Missing Key Detection

### Development Warning

```typescript
// i18n/config.ts (i18next)
i18n.init({
  // ...
  saveMissing: process.env.NODE_ENV === 'development',
  missingKeyHandler: (lng, ns, key, fallbackValue) => {
    console.warn(` Missing translation: [${lng}] ${ns}:${key}`);

    // Optional: Send to logging service
    if (process.env.SENTRY_DSN) {
      Sentry.captureMessage(`Missing i18n key: ${key}`, {
        level: 'warning',
        extra: { locale: lng, namespace: ns },
      });
    }
  },
});
```

### Production Fallback Strategy

```typescript
i18n.init({
  fallbackLng: {
    'de-AT': ['de', 'en'],
    'de-CH': ['de', 'en'],
    'zh-TW': ['zh-Hant', 'zh', 'en'],
    default: ['en'],
  },

  // Return key as fallback (debugging)
  returnEmptyString: false,

  // Custom fallback value
  parseMissingKeyHandler: (key) => {
    return `WARNING: ${key}`;
  },
});
```

---

## Translation File Organisation

### Namespace Strategy

```text
locales/
├── en/
│   ├── common.json       # 50-100 keys: buttons, errors, nav
│   ├── auth.json         # 30-50 keys: login, register
│   ├── dashboard.json    # 100+ keys: dashboard-specific
│   ├── validation.json   # 20-40 keys: form validation
│   ├── emails.json       # Email templates (if needed)
│   └── legal.json        # Terms, privacy (rarely changes)
└── de/
    └── ... (mirror structure)
```

### Key Naming Conventions

```json
{
  // Feature.component.element pattern
  "auth.login.title": "Sign In",
  "auth.login.email_label": "Email Address",
  "auth.login.submit_button": "Sign In",
  "auth.login.forgot_password_link": "Forgot password?",

  // Action-based for buttons
  "common.actions.save": "Save",
  "common.actions.cancel": "Cancel",
  "common.actions.delete": "Delete",

  // Error messages with context
  "validation.email.required": "Email is required",
  "validation.email.invalid": "Please enter a valid email",
  "validation.password.min_length": "Password must be at least {min} characters"
}
```

### Avoid

```json
{
  // FAIL Too generic
  "button1": "Click here",

  // FAIL Hardcoded values
  "items_5": "You have 5 items",

  // FAIL Concatenation-dependent
  "hello": "Hello",
  "world": "World",
  // Used as: t('hello') + ' ' + t('world') FAIL
}
```

---

## TMS Selection Guide

| TMS | Best For | Pricing | Key Features |
|-----|----------|---------|--------------|
| **Phrase** | Enterprise, large teams | $$$ | GitHub sync, CLI, over-the-air |
| **Lokalise** | Dev-focused teams | $$ | Figma plugin, branching, AI |
| **Crowdin** | Open source, community | $ - Free tier | Crowdsourcing, 600+ integrations |
| **Transifex** | API-first workflows | $$ | String detection, webhooks |
| **POEditor** | Small teams | $ | Simple UI, reasonable pricing |
| **Locize** | i18next projects | $$ | Real-time sync, versioning |

### Decision Criteria

1. **Team size**: Solo/small -> POEditor; Enterprise -> Phrase
2. **Budget**: Free tier needed -> Crowdin; Cost-flexible -> Lokalise
3. **i18n library**: i18next ecosystem -> Locize; Any -> Phrase/Lokalise
4. **Workflow**: Community translations -> Crowdin; Professional -> Phrase
5. **Integrations**: Figma-heavy -> Lokalise; GitHub-first -> Phrase/Crowdin

---

## AI-Powered Translation (2026)

AI is reshaping localization workflows beyond basic machine translation. Modern approaches use multiple AI engines, agentic automation, and deep CI/CD integration.

### Consensus-Based Translation

Multiple independent AI engines verify translations, reducing errors by ~22%.

```text
Translation Request
    │
    ├─ Engine 1 (GPT-4) ──────┐
    ├─ Engine 2 (Claude) ─────┼─ Consensus Check -> Final Translation
    ├─ Engine 3 (Gemini) ─────┘
    │
    └─ If disagreement -> Human review queue
```

**Benefits**:
- Higher accuracy than single-engine MT
- Automatic flagging of uncertain translations
- Reduced post-editing workload

### AI Translation Tools

| Tool | Type | Best For |
|------|------|----------|
| **i18n-ai-translate** | CLI | i18next JSON with ChatGPT/Gemini/Claude |
| **i18nexus** | Platform | React/Next.js with AI management |
| **Phrase Language AI** | Enterprise | Large-scale AI translation |
| **Locize** | i18next-native | Real-time AI-assisted translation |

### i18n-ai-translate Example

```bash
# Install
npm install -g i18n-ai-translate

# Translate single file
i18n-ai-translate --input locales/en/common.json --output locales/de/common.json --target de --provider openai

# Translate entire directory
i18n-ai-translate --input locales/en --output locales/de --target de --provider anthropic
```

**Features**:
- Preserves file structure (clean Git diffs)
- Keeps variables intact (`{name}`, `{{count}}`)
- Supports ChatGPT, Gemini, Claude, or local Ollama

### CI/CD AI Translation Pipeline

```yaml
# .github/workflows/ai-translate.yml
name: AI Translation
on:
  push:
    branches: [main]
    paths:
      - 'locales/en/**'

jobs:
  translate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install AI translator
        run: npm install -g i18n-ai-translate

      - name: Detect new keys
        id: detect
        run: |
          git diff HEAD~1 --name-only -- locales/en/ > changed_files.txt
          echo "files=$(cat changed_files.txt | tr '\n' ' ')" >> $GITHUB_OUTPUT

      - name: AI translate new keys
        if: steps.detect.outputs.files != ''
        run: |
          for lang in de fr es; do
            i18n-ai-translate \
              --input locales/en \
              --output locales/$lang \
              --target $lang \
              --provider openai \
              --only-missing
          done
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: Create PR with translations
        uses: peter-evans/create-pull-request@v5
        with:
          title: '[i18n] AI-generated translations for review'
          commit-message: 'chore(i18n): AI-translate new keys'
          branch: i18n/ai-translations
          labels: i18n, ai-generated, needs-review
```

### Agentic Translation Workflows

AI agents automate the full translation lifecycle:

```text
1. Extract -> Agent detects new strings in code
2. Translate -> AI generates translations per locale
3. Review -> Agent routes to human reviewers
4. Integrate -> Agent commits approved translations
5. Monitor -> Agent tracks translation coverage
```

**TMS platforms with AI agents** (2025-2026):
- Phrase: AI workflow automation
- Lokalise: AI-assisted QA and review
- Crowdin: AI translation suggestions
- Smartling: Agentic content adaptation

### Best Practices for AI Translation

| Practice | Why |
|----------|-----|
| Always flag AI translations for review | Catch context errors |
| Use `--only-missing` flag | Don't overwrite human translations |
| Set up domain-specific glossaries | Improve technical accuracy |
| Monitor translation quality metrics | Track AI performance over time |
| Keep humans in the loop | Final approval for production |

### When to Use AI vs Human Translation

| Content Type | AI Suitability | Recommendation |
|--------------|----------------|----------------|
| UI strings | High | AI + light review |
| Marketing copy | Medium | AI draft + human polish |
| Legal/compliance | Low | Human translation |
| Technical docs | High | AI + technical review |
| User-generated content | High | AI-only acceptable |

---

## Edge Translation (On-Device)

Emerging in 2025-2026: on-device translation for offline-first apps.

```typescript
// Example: On-device translation with Web AI
if ('translation' in navigator) {
  const translator = await navigator.translation.createTranslator({
    sourceLanguage: 'en',
    targetLanguage: 'de',
  });

  const translated = await translator.translate('Hello, world!');
  // "Hallo, Welt!" - no network request
}
```

**Current status**:
- Chrome Origin Trial for Translation API
- Safari exploring similar APIs
- Useful for: privacy-sensitive apps, offline-first, low-latency requirements
