# Next.js App Router + next-intl Complete Setup

Production-ready i18n setup for Next.js 14+ App Router with Server Components, TypeScript, and static generation.

---

## Project Structure

```text
├── app/
│   ├── [locale]/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   └── (auth)/
│   │       ├── login/
│   │       │   └── page.tsx
│   │       └── register/
│   │           └── page.tsx
│   ├── layout.tsx
│   └── not-found.tsx
├── messages/
│   ├── en.json
│   ├── de.json
│   └── ar.json
├── i18n/
│   ├── request.ts
│   ├── routing.ts
│   └── navigation.ts
├── middleware.ts
└── components/
    └── LanguageSwitcher.tsx
```

---

## Installation

```bash
npm install next-intl
```

---

## Configuration

### i18n/routing.ts

```typescript
import { defineRouting } from 'next-intl/routing';

export const routing = defineRouting({
  locales: ['en', 'de', 'fr', 'ar'],
  defaultLocale: 'en',
  localePrefix: 'always', // or 'as-needed'
});

export type Locale = (typeof routing.locales)[number];

export const RTL_LOCALES: Locale[] = ['ar'];
```

### i18n/request.ts

```typescript
import { getRequestConfig } from 'next-intl/server';
import { routing } from './routing';

export default getRequestConfig(async ({ requestLocale }) => {
  let locale = await requestLocale;

  // Validate locale
  if (!locale || !routing.locales.includes(locale as any)) {
    locale = routing.defaultLocale;
  }

  return {
    locale,
    messages: (await import(`../messages/${locale}.json`)).default,
  };
});
```

### i18n/navigation.ts

```typescript
import { createNavigation } from 'next-intl/navigation';
import { routing } from './routing';

export const { Link, redirect, usePathname, useRouter, getPathname } =
  createNavigation(routing);
```

### middleware.ts

```typescript
import createMiddleware from 'next-intl/middleware';
import { routing } from './i18n/routing';

export default createMiddleware(routing);

export const config = {
  matcher: [
    // Match all pathnames except for
    // - API routes
    // - _next (Next.js internals)
    // - Static files (images, etc.)
    '/((?!api|_next|.*\\..*).*)',
  ],
};
```

### next.config.js

```javascript
const createNextIntlPlugin = require('next-intl/plugin');

const withNextIntl = createNextIntlPlugin('./i18n/request.ts');

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Your other Next.js config
};

module.exports = withNextIntl(nextConfig);
```

---

## Translation Files

### messages/en.json

```json
{
  "Metadata": {
    "title": "My Application",
    "description": "Welcome to my application"
  },

  "Navigation": {
    "home": "Home",
    "dashboard": "Dashboard",
    "settings": "Settings",
    "logout": "Log out"
  },

  "Home": {
    "title": "Welcome",
    "description": "Get started with our platform",
    "cta": "Get Started"
  },

  "Dashboard": {
    "title": "Dashboard",
    "welcome": "Welcome back, {name}!",
    "stats": {
      "users": "{count, plural, one {# user} other {# users}}",
      "revenue": "Revenue: {amount, number, currency}"
    }
  },

  "Auth": {
    "login": {
      "title": "Sign In",
      "email": "Email Address",
      "password": "Password",
      "submit": "Sign In",
      "forgotPassword": "Forgot password?",
      "noAccount": "Don't have an account?",
      "signUp": "Sign up"
    },
    "register": {
      "title": "Create Account",
      "name": "Full Name",
      "submit": "Create Account"
    }
  },

  "Common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "loading": "Loading..."
  },

  "Errors": {
    "notFound": "Page not found",
    "serverError": "Something went wrong"
  }
}
```

### messages/de.json

```json
{
  "Metadata": {
    "title": "Meine Anwendung",
    "description": "Willkommen bei meiner Anwendung"
  },

  "Navigation": {
    "home": "Startseite",
    "dashboard": "Dashboard",
    "settings": "Einstellungen",
    "logout": "Abmelden"
  },

  "Home": {
    "title": "Willkommen",
    "description": "Starten Sie mit unserer Plattform",
    "cta": "Loslegen"
  },

  "Dashboard": {
    "title": "Dashboard",
    "welcome": "Willkommen zurück, {name}!",
    "stats": {
      "users": "{count, plural, one {# Benutzer} other {# Benutzer}}",
      "revenue": "Umsatz: {amount, number, currency}"
    }
  },

  "Auth": {
    "login": {
      "title": "Anmelden",
      "email": "E-Mail-Adresse",
      "password": "Passwort",
      "submit": "Anmelden",
      "forgotPassword": "Passwort vergessen?",
      "noAccount": "Noch kein Konto?",
      "signUp": "Registrieren"
    },
    "register": {
      "title": "Konto erstellen",
      "name": "Vollständiger Name",
      "submit": "Konto erstellen"
    }
  },

  "Common": {
    "save": "Speichern",
    "cancel": "Abbrechen",
    "delete": "Löschen",
    "loading": "Laden..."
  },

  "Errors": {
    "notFound": "Seite nicht gefunden",
    "serverError": "Etwas ist schief gelaufen"
  }
}
```

---

## App Structure

### app/layout.tsx

```tsx
import { ReactNode } from 'react';

type Props = {
  children: ReactNode;
};

// Root layout without locale-specific content
export default function RootLayout({ children }: Props) {
  return children;
}
```

### app/[locale]/layout.tsx

```tsx
import { ReactNode } from 'react';
import { NextIntlClientProvider } from 'next-intl';
import { getMessages, setRequestLocale } from 'next-intl/server';
import { routing, RTL_LOCALES } from '@/i18n/routing';
import type { Locale } from '@/i18n/routing';
import Navigation from '@/components/Navigation';

type Props = {
  children: ReactNode;
  params: { locale: string };
};

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export default async function LocaleLayout({ children, params: { locale } }: Props) {
  setRequestLocale(locale);
  const messages = await getMessages();
  const isRTL = RTL_LOCALES.includes(locale as Locale);

  return (
    <html lang={locale} dir={isRTL ? 'rtl' : 'ltr'}>
      <body>
        <NextIntlClientProvider messages={messages}>
          <Navigation />
          <main>{children}</main>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

### app/[locale]/page.tsx

```tsx
import { useTranslations } from 'next-intl';
import { setRequestLocale } from 'next-intl/server';
import { Link } from '@/i18n/navigation';

type Props = {
  params: { locale: string };
};

export default function HomePage({ params: { locale } }: Props) {
  setRequestLocale(locale);
  const t = useTranslations('Home');

  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('description')}</p>
      <Link href="/dashboard">{t('cta')}</Link>
    </div>
  );
}
```

### app/[locale]/dashboard/page.tsx

```tsx
import { useTranslations } from 'next-intl';
import { setRequestLocale, getTranslations } from 'next-intl/server';

type Props = {
  params: { locale: string };
};

// Generate metadata
export async function generateMetadata({ params: { locale } }: Props) {
  const t = await getTranslations({ locale, namespace: 'Dashboard' });
  return {
    title: t('title'),
  };
}

export default function DashboardPage({ params: { locale } }: Props) {
  setRequestLocale(locale);
  const t = useTranslations('Dashboard');

  const stats = {
    users: 1234,
    revenue: 50000,
  };

  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('welcome', { name: 'Alice' })}</p>

      <div className="stats">
        <p>{t('stats.users', { count: stats.users })}</p>
        <p>
          {t('stats.revenue', {
            amount: stats.revenue,
            currency: 'USD',
          })}
        </p>
      </div>
    </div>
  );
}
```

### app/not-found.tsx

```tsx
'use client';

import { useTranslations } from 'next-intl';

export default function NotFound() {
  const t = useTranslations('Errors');

  return (
    <div>
      <h1>404</h1>
      <p>{t('notFound')}</p>
    </div>
  );
}
```

---

## Components

### components/Navigation.tsx

```tsx
import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import LanguageSwitcher from './LanguageSwitcher';

export default function Navigation() {
  const t = useTranslations('Navigation');

  return (
    <nav>
      <Link href="/">{t('home')}</Link>
      <Link href="/dashboard">{t('dashboard')}</Link>
      <Link href="/settings">{t('settings')}</Link>
      <LanguageSwitcher />
    </nav>
  );
}
```

### components/LanguageSwitcher.tsx

```tsx
'use client';

import { useLocale } from 'next-intl';
import { useRouter, usePathname } from '@/i18n/navigation';
import { routing, type Locale } from '@/i18n/routing';

const languageNames: Record<Locale, string> = {
  en: 'English',
  de: 'Deutsch',
  fr: 'Français',
  ar: 'العربية',
};

export default function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const newLocale = event.target.value as Locale;
    router.replace(pathname, { locale: newLocale });
  };

  return (
    <select value={locale} onChange={handleChange} aria-label="Select language">
      {routing.locales.map((loc) => (
        <option key={loc} value={loc}>
          {languageNames[loc]}
        </option>
      ))}
    </select>
  );
}
```

---

## Server Components vs Client Components

### Server Component (Default)

```tsx
// app/[locale]/products/page.tsx
import { useTranslations } from 'next-intl';
import { setRequestLocale } from 'next-intl/server';

export default function ProductsPage({ params: { locale } }: Props) {
  setRequestLocale(locale);
  const t = useTranslations('Products');

  // Can fetch data directly
  // const products = await fetchProducts();

  return <h1>{t('title')}</h1>;
}
```

### Client Component

```tsx
'use client';

import { useTranslations } from 'next-intl';
import { useState } from 'react';

export default function Counter() {
  const t = useTranslations('Counter');
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>{t('count', { count })}</p>
      <button onClick={() => setCount(count + 1)}>{t('increment')}</button>
    </div>
  );
}
```

---

## Server Actions

### With Translations

```tsx
'use server';

import { getTranslations } from 'next-intl/server';

export async function submitForm(formData: FormData) {
  const t = await getTranslations('Validation');

  const email = formData.get('email') as string;

  if (!email) {
    return { error: t('required') };
  }

  // Process form...
  return { success: true };
}
```

---

## Static Generation

### Generate All Locale Paths

```tsx
// app/[locale]/blog/[slug]/page.tsx
import { routing } from '@/i18n/routing';

export async function generateStaticParams() {
  const posts = await fetchAllPosts();

  return routing.locales.flatMap((locale) =>
    posts.map((post) => ({
      locale,
      slug: post.slug,
    }))
  );
}
```

---

## API Routes with i18n

```tsx
// app/api/messages/route.ts
import { getTranslations } from 'next-intl/server';
import { NextRequest } from 'next/server';

export async function GET(request: NextRequest) {
  const locale = request.headers.get('Accept-Language')?.split(',')[0] || 'en';
  const t = await getTranslations({ locale, namespace: 'API' });

  return Response.json({
    message: t('welcome'),
  });
}
```

---

## SEO and Metadata

### Dynamic Metadata

```tsx
// app/[locale]/layout.tsx
import { getTranslations } from 'next-intl/server';
import { routing } from '@/i18n/routing';

export async function generateMetadata({ params: { locale } }: Props) {
  const t = await getTranslations({ locale, namespace: 'Metadata' });

  return {
    title: {
      default: t('title'),
      template: `%s | ${t('title')}`,
    },
    description: t('description'),
    alternates: {
      languages: Object.fromEntries(
        routing.locales.map((loc) => [loc, `/${loc}`])
      ),
    },
  };
}
```

### Hreflang Tags

Next-intl automatically generates hreflang tags. For custom control:

### Locale Purity for SEO Pages (Critical)

For indexable locale routes, avoid mixed-language rendering:

- Do not use English fallback strings in non-English metadata or body copy.
- Keep `title`, `description`, breadcrumbs, and JSON-LD in the same locale.
- If a key is missing, fail CI or use locale-safe neutral copy (not English fragments).
- Validate rendered HTML for locale consistency before deploy.

```tsx
// app/[locale]/layout.tsx
export async function generateMetadata({ params: { locale } }: Props) {
  const baseUrl = 'https://example.com';

  return {
    alternates: {
      canonical: `${baseUrl}/${locale}`,
      languages: {
        en: `${baseUrl}/en`,
        de: `${baseUrl}/de`,
        fr: `${baseUrl}/fr`,
        ar: `${baseUrl}/ar`,
        'x-default': `${baseUrl}/en`,
      },
    },
  };
}
```

---

## Environment Variables

```env
# .env.local
NEXT_PUBLIC_DEFAULT_LOCALE=en
```

```typescript
// i18n/routing.ts
export const routing = defineRouting({
  locales: ['en', 'de', 'fr', 'ar'],
  defaultLocale: process.env.NEXT_PUBLIC_DEFAULT_LOCALE || 'en',
});
```

---

## Testing

### Test Setup

```typescript
// jest.setup.ts
import { NextIntlClientProvider } from 'next-intl';

const messages = require('./messages/en.json');

global.renderWithIntl = (ui: React.ReactElement) => {
  return render(
    <NextIntlClientProvider locale="en" messages={messages}>
      {ui}
    </NextIntlClientProvider>
  );
};
```

### Component Test

```typescript
// components/LanguageSwitcher.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { NextIntlClientProvider } from 'next-intl';
import LanguageSwitcher from './LanguageSwitcher';

const messages = {};

describe('LanguageSwitcher', () => {
  it('renders language options', () => {
    render(
      <NextIntlClientProvider locale="en" messages={messages}>
        <LanguageSwitcher />
      </NextIntlClientProvider>
    );

    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });
});
```

---

## Deployment

### Vercel

next-intl works out of the box with Vercel. Middleware runs at the edge for fast locale detection.

### Static Export

For static export, use `localePrefix: 'always'` and generate all locale paths:

```javascript
// next.config.js
module.exports = withNextIntl({
  output: 'export',
  trailingSlash: true,
});
```

---

## Checklist

- REQUIRED: Install next-intl
- REQUIRED: Create routing configuration
- REQUIRED: Set up request configuration
- REQUIRED: Add middleware for locale detection
- REQUIRED: Update `next.config.js`
- REQUIRED: Create message files for each locale
- REQUIRED: Set up `[locale]` directory structure
- REQUIRED: Create LanguageSwitcher component
- REQUIRED: Handle RTL languages
- REQUIRED: Add metadata with translations
- REQUIRED: Set up hreflang tags (if SEO requirements apply)
- REQUIRED: Prevent mixed-language output on locale-routed pages
- REQUIRED: Avoid silent English fallback for indexable non-English content
- REQUIRED: Include JSON-LD locale parity checks in QA
- REQUIRED: Configure static generation (if applicable)
- REQUIRED: Set up testing utilities
