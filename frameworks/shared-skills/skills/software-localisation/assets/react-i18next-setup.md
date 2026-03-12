# React + i18next Complete Setup

Production-ready i18n setup for React applications with TypeScript, lazy loading, and namespace organisation.

---

## Project Structure

```text
src/
├── i18n/
│   ├── config.ts              # i18next configuration
│   ├── resources.d.ts         # TypeScript types
│   └── index.ts               # Export
├── locales/
│   ├── en/
│   │   ├── common.json        # Shared strings
│   │   ├── auth.json          # Authentication
│   │   ├── dashboard.json     # Dashboard
│   │   └── validation.json    # Form validation
│   ├── de/
│   │   └── ... (same structure)
│   └── ar/
│       └── ... (same structure)
├── components/
│   ├── LanguageSwitcher.tsx
│   └── ...
└── App.tsx
```

---

## Installation

```bash
npm install i18next react-i18next i18next-http-backend i18next-browser-languagedetector
```

---

## Configuration

### i18n/config.ts

```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import Backend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

export const supportedLngs = ['en', 'de', 'fr', 'ar'] as const;
export type SupportedLocale = (typeof supportedLngs)[number];

export const defaultNS = 'common';
export const namespaces = ['common', 'auth', 'dashboard', 'validation'] as const;

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    // Supported languages
    supportedLngs,
    fallbackLng: 'en',

    // Namespaces
    ns: namespaces,
    defaultNS,

    // Debug in development
    debug: process.env.NODE_ENV === 'development',

    // Interpolation
    interpolation: {
      escapeValue: false, // React already escapes
    },

    // Backend configuration
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },

    // Detection configuration
    detection: {
      order: ['querystring', 'cookie', 'localStorage', 'navigator', 'htmlTag'],
      lookupQuerystring: 'lang',
      lookupCookie: 'i18next',
      lookupLocalStorage: 'i18nextLng',
      caches: ['localStorage', 'cookie'],
    },

    // React specific
    react: {
      useSuspense: true,
    },
  });

export default i18n;
```

### i18n/resources.d.ts (TypeScript Types)

```typescript
import common from '../locales/en/common.json';
import auth from '../locales/en/auth.json';
import dashboard from '../locales/en/dashboard.json';
import validation from '../locales/en/validation.json';

declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: 'common';
    resources: {
      common: typeof common;
      auth: typeof auth;
      dashboard: typeof dashboard;
      validation: typeof validation;
    };
  }
}
```

### i18n/index.ts

```typescript
export { default } from './config';
export { supportedLngs, defaultNS, namespaces } from './config';
export type { SupportedLocale } from './config';
```

---

## Translation Files

### locales/en/common.json

```json
{
  "app_name": "My Application",
  "welcome": "Welcome, {{name}}!",
  "loading": "Loading...",
  "error": "An error occurred",
  "retry": "Try again",

  "nav": {
    "home": "Home",
    "dashboard": "Dashboard",
    "settings": "Settings",
    "logout": "Log out"
  },

  "actions": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit",
    "confirm": "Confirm"
  },

  "items_count": "{{count, number}} {{count, plural, one {item} other {items}}}"
}
```

### locales/en/auth.json

```json
{
  "login": {
    "title": "Sign In",
    "email_label": "Email Address",
    "email_placeholder": "Enter your email",
    "password_label": "Password",
    "password_placeholder": "Enter your password",
    "submit": "Sign In",
    "forgot_password": "Forgot password?",
    "no_account": "Don't have an account?",
    "sign_up_link": "Sign up"
  },

  "register": {
    "title": "Create Account",
    "name_label": "Full Name",
    "submit": "Create Account",
    "has_account": "Already have an account?",
    "sign_in_link": "Sign in"
  },

  "errors": {
    "invalid_credentials": "Invalid email or password",
    "email_in_use": "This email is already registered",
    "weak_password": "Password is too weak"
  }
}
```

### locales/en/validation.json

```json
{
  "required": "This field is required",
  "email": {
    "invalid": "Please enter a valid email address",
    "required": "Email is required"
  },
  "password": {
    "required": "Password is required",
    "min_length": "Password must be at least {{min}} characters",
    "mismatch": "Passwords do not match"
  },
  "name": {
    "required": "Name is required",
    "min_length": "Name must be at least {{min}} characters"
  }
}
```

---

## Components

### App.tsx

```tsx
import { Suspense } from 'react';
import { useTranslation } from 'react-i18next';
import './i18n';

function AppContent() {
  const { t, i18n } = useTranslation();

  // Set document direction for RTL languages
  const isRTL = ['ar', 'he', 'fa'].includes(i18n.language);

  return (
    <div dir={isRTL ? 'rtl' : 'ltr'}>
      <header>
        <h1>{t('app_name')}</h1>
        <LanguageSwitcher />
      </header>
      <main>
        {/* App content */}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <AppContent />
    </Suspense>
  );
}

function LoadingSpinner() {
  return <div className="loading">Loading...</div>;
}
```

### components/LanguageSwitcher.tsx

```tsx
import { useTranslation } from 'react-i18next';
import { supportedLngs, SupportedLocale } from '../i18n';

const languageNames: Record<SupportedLocale, string> = {
  en: 'English',
  de: 'Deutsch',
  fr: 'Français',
  ar: 'العربية',
};

export function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    i18n.changeLanguage(event.target.value);
  };

  return (
    <select
      value={i18n.language}
      onChange={handleChange}
      aria-label="Select language"
    >
      {supportedLngs.map((lng) => (
        <option key={lng} value={lng}>
          {languageNames[lng]}
        </option>
      ))}
    </select>
  );
}
```

### Namespace-Specific Hook Usage

```tsx
import { useTranslation } from 'react-i18next';

// Dashboard component - loads dashboard namespace
function Dashboard() {
  const { t } = useTranslation('dashboard');

  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('welcome_message')}</p>
    </div>
  );
}

// Auth component - loads auth namespace
function LoginForm() {
  const { t } = useTranslation('auth');
  const { t: tValidation } = useTranslation('validation');

  return (
    <form>
      <h1>{t('login.title')}</h1>
      <input
        type="email"
        placeholder={t('login.email_placeholder')}
        aria-label={t('login.email_label')}
      />
      {/* Validation messages from validation namespace */}
      <span className="error">{tValidation('email.invalid')}</span>
    </form>
  );
}
```

### Trans Component for Rich Text

```tsx
import { Trans } from 'react-i18next';

function TermsNotice() {
  return (
    <p>
      <Trans i18nKey="terms_notice" ns="common">
        By continuing, you agree to our <a href="/terms">Terms of Service</a> and{' '}
        <a href="/privacy">Privacy Policy</a>.
      </Trans>
    </p>
  );
}
```

```json
// common.json
{
  "terms_notice": "By continuing, you agree to our <0>Terms of Service</0> and <1>Privacy Policy</1>."
}
```

---

## Lazy Loading

### Load Namespace on Demand

```tsx
import { useTranslation } from 'react-i18next';
import { Suspense, lazy } from 'react';

// Lazy load dashboard component
const Dashboard = lazy(() => import('./Dashboard'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Dashboard />
    </Suspense>
  );
}

// Dashboard.tsx
function Dashboard() {
  // This will automatically load 'dashboard' namespace
  const { t, ready } = useTranslation('dashboard');

  if (!ready) return <Loading />;

  return <h1>{t('title')}</h1>;
}
```

### Preload Namespaces

```tsx
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

function App() {
  const { i18n } = useTranslation();

  useEffect(() => {
    // Preload namespaces for better UX
    i18n.loadNamespaces(['dashboard', 'settings']);
  }, [i18n]);

  return <AppContent />;
}
```

---

## Form Validation Integration

### With React Hook Form

```tsx
import { useForm } from 'react-hook-form';
import { useTranslation } from 'react-i18next';

interface LoginFormData {
  email: string;
  password: string;
}

function LoginForm() {
  const { t } = useTranslation('validation');
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>();

  const onSubmit = (data: LoginFormData) => {
    console.log(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input
        {...register('email', {
          required: t('email.required'),
          pattern: {
            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
            message: t('email.invalid'),
          },
        })}
        type="email"
      />
      {errors.email && <span>{errors.email.message}</span>}

      <input
        {...register('password', {
          required: t('password.required'),
          minLength: {
            value: 8,
            message: t('password.min_length', { min: 8 }),
          },
        })}
        type="password"
      />
      {errors.password && <span>{errors.password.message}</span>}

      <button type="submit">Submit</button>
    </form>
  );
}
```

---

## Testing

### Test Setup

```typescript
// test/i18n-test-config.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

i18n.use(initReactI18next).init({
  lng: 'en',
  fallbackLng: 'en',
  ns: ['common', 'auth'],
  defaultNS: 'common',
  resources: {
    en: {
      common: require('../locales/en/common.json'),
      auth: require('../locales/en/auth.json'),
    },
  },
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
```

### Component Test

```tsx
// components/LanguageSwitcher.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { I18nextProvider } from 'react-i18next';
import i18n from '../test/i18n-test-config';
import { LanguageSwitcher } from './LanguageSwitcher';

describe('LanguageSwitcher', () => {
  it('switches language', async () => {
    render(
      <I18nextProvider i18n={i18n}>
        <LanguageSwitcher />
      </I18nextProvider>
    );

    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'de' } });

    expect(i18n.language).toBe('de');
  });
});
```

---

## Build Configuration

### Vite

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate i18n into its own chunk
          i18n: ['i18next', 'react-i18next'],
        },
      },
    },
  },
});
```

### Copy Locales to Build

```json
// package.json
{
  "scripts": {
    "build": "vite build && cp -r public/locales dist/locales"
  }
}
```

---

## Checklist

- REQUIRED: Install dependencies
- REQUIRED: Create i18n configuration
- REQUIRED: Set up TypeScript types
- REQUIRED: Create namespace JSON files
- REQUIRED: Add LanguageSwitcher component
- REQUIRED: Wrap app with Suspense (if using i18next-http-backend)
- REQUIRED: Handle RTL direction
- REQUIRED: Configure lazy loading
- REQUIRED: Set up test configuration
- REQUIRED: Configure build to include locales
