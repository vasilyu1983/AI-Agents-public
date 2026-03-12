# Framework-Specific i18n Implementation Guides

Production patterns for React, Vue, Angular, and Next.js internationalisation.

## React + i18next

Popular React i18n solution. Flexible, extensible, and well-maintained.

### Installation

```bash
npm install i18next react-i18next i18next-http-backend i18next-browser-languagedetector
```

### Configuration

```typescript
// src/i18n/config.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import Backend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    supportedLngs: ['en', 'de', 'fr', 'ar'],
    debug: process.env.NODE_ENV === 'development',

    // Namespace configuration
    ns: ['common', 'auth', 'dashboard', 'validation'],
    defaultNS: 'common',

    interpolation: {
      escapeValue: false, // React already escapes
    },

    // Backend configuration for lazy loading
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },

    // Detection order
    detection: {
      order: ['querystring', 'cookie', 'localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage', 'cookie'],
    },
  });

export default i18n;
```

### Hook Usage

```tsx
import { useTranslation } from 'react-i18next';

function UserGreeting({ user }: { user: User }) {
  const { t, i18n } = useTranslation();

  return (
    <div>
      <h1>{t('greeting', { name: user.name })}</h1>
      <p>{t('items_count', { count: user.itemCount })}</p>

      {/* Switch language */}
      <button onClick={() => i18n.changeLanguage('de')}>
        Deutsch
      </button>
    </div>
  );
}
```

### Trans Component (Rich Text)

```tsx
import { Trans } from 'react-i18next';

function TermsNotice() {
  return (
    <Trans i18nKey="terms_notice">
      By signing up, you agree to our <a href="/terms">Terms</a> and{' '}
      <a href="/privacy">Privacy Policy</a>.
    </Trans>
  );
}
```

```json
// locales/en/common.json
{
  "terms_notice": "By signing up, you agree to our <0>Terms</0> and <1>Privacy Policy</1>."
}
```

### Namespace Lazy Loading

```tsx
import { useTranslation } from 'react-i18next';
import { Suspense } from 'react';

function Dashboard() {
  // Load dashboard namespace on demand
  const { t } = useTranslation('dashboard');

  return <h1>{t('title')}</h1>;
}

// Wrap with Suspense
function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Dashboard />
    </Suspense>
  );
}
```

### TypeScript Types

```typescript
// src/i18n/resources.d.ts
import common from '../../public/locales/en/common.json';
import auth from '../../public/locales/en/auth.json';

declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: 'common';
    resources: {
      common: typeof common;
      auth: typeof auth;
    };
  }
}
```

---

## React + react-intl (FormatJS)

Enterprise-focused with native ICU support. Used by Yahoo, Mozilla, Dropbox.

### Installation

```bash
npm install react-intl
```

### Configuration

```tsx
// src/i18n/IntlProvider.tsx
import { IntlProvider } from 'react-intl';
import { useState, useEffect } from 'react';

const loadMessages = async (locale: string) => {
  switch (locale) {
    case 'de':
      return (await import('../locales/de.json')).default;
    case 'fr':
      return (await import('../locales/fr.json')).default;
    default:
      return (await import('../locales/en.json')).default;
  }
};

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocale] = useState('en');
  const [messages, setMessages] = useState<Record<string, string>>({});

  useEffect(() => {
    loadMessages(locale).then(setMessages);
  }, [locale]);

  return (
    <IntlProvider locale={locale} messages={messages}>
      {children}
    </IntlProvider>
  );
}
```

### Hook Usage

```tsx
import { useIntl, FormattedMessage, FormattedNumber, FormattedDate } from 'react-intl';

function ProductCard({ product }: { product: Product }) {
  const intl = useIntl();

  return (
    <div>
      {/* Simple message */}
      <FormattedMessage id="product.title" defaultMessage="Product Details" />

      {/* With interpolation */}
      <FormattedMessage
        id="product.stock"
        defaultMessage="{count, plural, one {# item} other {# items}} in stock"
        values={{ count: product.stock }}
      />

      {/* Currency formatting */}
      <FormattedNumber
        value={product.price}
        style="currency"
        currency="USD"
      />

      {/* Date formatting */}
      <FormattedDate
        value={product.createdAt}
        year="numeric"
        month="long"
        day="numeric"
      />

      {/* Imperative API */}
      <input
        placeholder={intl.formatMessage({ id: 'search.placeholder' })}
      />
    </div>
  );
}
```

### Message Extraction

```bash
# Extract messages to JSON
npx formatjs extract 'src/**/*.tsx' --out-file lang/en.json --id-interpolation-pattern '[sha512:contenthash:base64:6]'

# Compile messages (for production)
npx formatjs compile lang/en.json --out-file compiled-lang/en.json
```

---

## Vue 3 + vue-i18n

Native Vue integration with Composition API support.

### Installation

```bash
npm install vue-i18n
```

### Configuration

```typescript
// src/i18n/index.ts
import { createI18n } from 'vue-i18n';

// Type-safe messages
type MessageSchema = typeof import('../locales/en.json');

const i18n = createI18n<[MessageSchema], 'en' | 'de' | 'fr'>({
  legacy: false, // Use Composition API
  locale: 'en',
  fallbackLocale: 'en',
  messages: {
    en: () => import('../locales/en.json'),
    de: () => import('../locales/de.json'),
    fr: () => import('../locales/fr.json'),
  },
});

export default i18n;
```

### Composition API Usage

```vue
<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { t, locale, availableLocales } = useI18n();

const switchLocale = (newLocale: string) => {
  locale.value = newLocale;
};
</script>

<template>
  <div>
    <h1>{{ t('welcome') }}</h1>
    <p>{{ t('items_count', { count: 5 }) }}</p>

    <!-- Language switcher -->
    <select v-model="locale">
      <option v-for="l in availableLocales" :key="l" :value="l">
        {{ l }}
      </option>
    </select>
  </div>
</template>
```

### Per-Component Messages

```vue
<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { t } = useI18n({
  messages: {
    en: {
      title: 'User Profile',
      edit: 'Edit Profile',
    },
    de: {
      title: 'Benutzerprofil',
      edit: 'Profil bearbeiten',
    },
  },
});
</script>

<template>
  <div>
    <h1>{{ t('title') }}</h1>
    <button>{{ t('edit') }}</button>
  </div>
</template>
```

### Lazy Loading with Vue Router

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import i18n from '../i18n';

const routes = [
  {
    path: '/:locale',
    children: [
      {
        path: 'dashboard',
        component: () => import('../views/Dashboard.vue'),
        beforeEnter: async (to) => {
          const locale = to.params.locale as string;
          if (!i18n.global.availableLocales.includes(locale)) {
            return `/${i18n.global.locale.value}/dashboard`;
          }
          // Load locale messages
          await loadLocaleMessages(locale);
          i18n.global.locale.value = locale;
        },
      },
    ],
  },
];
```

---

## Angular + @angular/localize

First-party solution with AOT compilation support.

### Installation

```bash
ng add @angular/localize
```

### Template Usage

```html
<!-- app.component.html -->
<h1 i18n="@@welcomeTitle">Welcome to our application</h1>

<p i18n="@@itemsCount">{itemCount, plural,
  =0 {No items}
  =1 {One item}
  other {{{itemCount}} items}
}</p>

<!-- With description for translators -->
<p i18n="User greeting|A friendly greeting to the user@@userGreeting">
  Hello, {{ userName }}!
</p>
```

### Extract and Build

```bash
# Extract messages
ng extract-i18n --output-path src/locale

# Build for specific locale
ng build --localize

# Serve specific locale
ng serve --configuration=de
```

### angular.json Configuration

```json
{
  "projects": {
    "my-app": {
      "i18n": {
        "sourceLocale": "en-US",
        "locales": {
          "de": "src/locale/messages.de.xlf",
          "fr": "src/locale/messages.fr.xlf"
        }
      },
      "architect": {
        "build": {
          "configurations": {
            "de": {
              "localize": ["de"]
            },
            "fr": {
              "localize": ["fr"]
            }
          }
        }
      }
    }
  }
}
```

### Runtime Locale Switching (with ngx-translate)

For runtime switching, use ngx-translate alongside @angular/localize:

```bash
npm install @ngx-translate/core @ngx-translate/http-loader
```

```typescript
// app.module.ts
import { TranslateModule, TranslateLoader } from '@ngx-translate/core';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';

export function HttpLoaderFactory(http: HttpClient) {
  return new TranslateHttpLoader(http, './assets/i18n/', '.json');
}

@NgModule({
  imports: [
    TranslateModule.forRoot({
      defaultLanguage: 'en',
      loader: {
        provide: TranslateLoader,
        useFactory: HttpLoaderFactory,
        deps: [HttpClient],
      },
    }),
  ],
})
export class AppModule {}
```

---

## Next.js App Router + next-intl

Modern i18n for Next.js 13+ App Router with Server Components support.

### Installation

```bash
npm install next-intl
```

### Configuration

```typescript
// i18n/request.ts
import { getRequestConfig } from 'next-intl/server';
import { notFound } from 'next/navigation';

const locales = ['en', 'de', 'fr'];

export default getRequestConfig(async ({ locale }) => {
  if (!locales.includes(locale as string)) notFound();

  return {
    messages: (await import(`../messages/${locale}.json`)).default,
  };
});
```

```typescript
// middleware.ts
import createMiddleware from 'next-intl/middleware';

export default createMiddleware({
  locales: ['en', 'de', 'fr'],
  defaultLocale: 'en',
  localePrefix: 'always', // or 'as-needed'
});

export const config = {
  matcher: ['/', '/(de|en|fr)/:path*'],
};
```

### Directory Structure

```text
app/
├── [locale]/
│   ├── layout.tsx
│   ├── page.tsx
│   └── dashboard/
│       └── page.tsx
├── layout.tsx
└── not-found.tsx
messages/
├── en.json
├── de.json
└── fr.json
```

### Server Component Usage

```tsx
// app/[locale]/page.tsx
import { useTranslations } from 'next-intl';
import { getTranslations } from 'next-intl/server';

// For Server Components
export async function generateMetadata({ params: { locale } }) {
  const t = await getTranslations({ locale, namespace: 'Metadata' });
  return { title: t('title') };
}

// Client or Server Component
export default function Home() {
  const t = useTranslations('Home');

  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('description')}</p>
    </div>
  );
}
```

### Client Component Usage

```tsx
'use client';

import { useTranslations, useLocale } from 'next-intl';
import { useRouter, usePathname } from 'next/navigation';

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const switchLocale = (newLocale: string) => {
    const newPath = pathname.replace(`/${locale}`, `/${newLocale}`);
    router.push(newPath);
  };

  return (
    <select value={locale} onChange={(e) => switchLocale(e.target.value)}>
      <option value="en">English</option>
      <option value="de">Deutsch</option>
      <option value="fr">Français</option>
    </select>
  );
}
```

### Static Generation

```typescript
// app/[locale]/page.tsx
export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'de' }, { locale: 'fr' }];
}
```

### Static Rendering with setRequestLocale (2026 Pattern)

By default, next-intl opts into dynamic rendering when `useTranslations` is used in Server Components. To enable static rendering, use `setRequestLocale`:

```typescript
// app/[locale]/page.tsx
import { useTranslations } from 'next-intl';
import { setRequestLocale } from 'next-intl/server';

type Props = {
  params: { locale: string };
};

export default function HomePage({ params: { locale } }: Props) {
  // Enable static rendering for this page
  setRequestLocale(locale);

  const t = useTranslations('Home');

  return (
    <main>
      <h1>{t('title')}</h1>
      <p>{t('description')}</p>
    </main>
  );
}

// Required for static generation
export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'de' }, { locale: 'fr' }];
}
```

**Important**: Call `setRequestLocale` at the very top of your page/layout components, before any hooks.

### Layout with Static Rendering

```typescript
// app/[locale]/layout.tsx
import { NextIntlClientProvider } from 'next-intl';
import { getMessages, setRequestLocale } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { hasLocale } from 'next-intl';

const locales = ['en', 'de', 'fr'];

type Props = {
  children: React.ReactNode;
  params: { locale: string };
};

export default async function LocaleLayout({ children, params: { locale } }: Props) {
  // Validate locale
  if (!hasLocale(locales, locale)) {
    notFound();
  }

  // Enable static rendering
  setRequestLocale(locale);

  const messages = await getMessages();

  return (
    <html lang={locale}>
      <body>
        <NextIntlClientProvider messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}
```

### React Server Components Best Practices

With RSC (Next.js 13+), i18n moves to the server for better performance:

```typescript
// Server Component - no client JS for translations
export default async function ProductPage({ params: { locale, id } }: Props) {
  setRequestLocale(locale);

  const t = useTranslations('Product');
  const product = await getProduct(id);

  return (
    <div>
      <h1>{t('title', { name: product.name })}</h1>
      <p>{t('price', { amount: product.price })}</p>
    </div>
  );
}
```

**Benefits of server-side i18n**:

- No translation flicker (content rendered before HTML reaches browser)
- Smaller client bundle (no i18n runtime shipped)
- Better SEO (fully translated HTML)
- Faster Time to First Byte

---

## LinguiJS (Minimal Bundle)

Bundle-conscious option with ICU syntax support.

### Installation

```bash
npm install @lingui/core @lingui/react @lingui/cli @lingui/babel-plugin-lingui-macro
```

### Configuration

```javascript
// lingui.config.ts
export default {
  locales: ['en', 'de', 'fr'],
  sourceLocale: 'en',
  catalogs: [
    {
      path: '<rootDir>/src/locales/{locale}/messages',
      include: ['src'],
    },
  ],
  format: 'po',
};
```

### Usage with Macros

```tsx
import { Trans, Plural, t } from '@lingui/macro';
import { useLingui } from '@lingui/react';

function ProductList({ products }: { products: Product[] }) {
  const { i18n } = useLingui();

  return (
    <div>
      {/* Tagged template literal */}
      <h1>{t`Product Catalog`}</h1>

      {/* Trans component */}
      <Trans>Welcome to our store</Trans>

      {/* Pluralisation */}
      <Plural
        value={products.length}
        one="# product"
        other="# products"
      />

      {/* Imperative */}
      <input placeholder={t(i18n)`Search products...`} />
    </div>
  );
}
```

### Extract and Compile

```bash
# Extract messages
npx lingui extract

# Compile for production
npx lingui compile
```

---

## Framework Comparison Summary

| Feature | react-i18next | react-intl | vue-i18n | @angular/localize | next-intl | LinguiJS |
|---------|--------------|------------|----------|-------------------|-----------|----------|
| Bundle Cost (relative) | Medium | Medium | Medium | Built-in | Low-Medium | Low |
| ICU Native | Plugin | Yes | Yes | Yes | Yes | Yes |
| Lazy Loading | Native | Manual | Native | AOT | Native | Native |
| TypeScript | Good | Good | Excellent | Native | Excellent | Excellent |
| SSR Support | Yes | Yes | Yes | Yes | Excellent | Yes |
| Extraction CLI | Yes | Yes | Yes | Yes | Yes | Yes |
| TMS Integration | Excellent | Good | Good | Limited | Good | Good |
