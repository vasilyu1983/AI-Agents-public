# Vue 3 + vue-i18n Complete Setup

Production-ready i18n setup for Vue 3 applications with Composition API, TypeScript, and lazy loading.

---

## Project Structure

```text
src/
├── i18n/
│   ├── index.ts              # vue-i18n configuration
│   └── types.ts              # TypeScript types
├── locales/
│   ├── en.json               # English translations
│   ├── de.json               # German translations
│   └── ar.json               # Arabic translations
├── composables/
│   └── useLocale.ts          # Locale utilities
├── components/
│   └── LanguageSwitcher.vue
└── App.vue
```

---

## Installation

```bash
npm install vue-i18n
```

---

## Configuration

### i18n/index.ts

```typescript
import { createI18n } from 'vue-i18n';
import type { I18nOptions } from 'vue-i18n';

// Import default locale eagerly
import en from '../locales/en.json';

export const SUPPORTED_LOCALES = ['en', 'de', 'fr', 'ar'] as const;
export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];

export const RTL_LOCALES: SupportedLocale[] = ['ar'];

// Lazy load other locales
const localeMessages: Record<string, () => Promise<{ default: Record<string, unknown> }>> = {
  de: () => import('../locales/de.json'),
  fr: () => import('../locales/fr.json'),
  ar: () => import('../locales/ar.json'),
};

export async function loadLocaleMessages(locale: SupportedLocale): Promise<void> {
  if (locale === 'en') return; // Already loaded

  const messages = await localeMessages[locale]();
  i18n.global.setLocaleMessage(locale, messages.default);
}

const options: I18nOptions = {
  legacy: false, // Use Composition API
  locale: 'en',
  fallbackLocale: 'en',
  messages: { en },
  missingWarn: process.env.NODE_ENV === 'development',
  fallbackWarn: process.env.NODE_ENV === 'development',
};

export const i18n = createI18n(options);

export default i18n;
```

### i18n/types.ts

```typescript
import type en from '../locales/en.json';

// Type-safe message keys
export type MessageSchema = typeof en;

declare module 'vue-i18n' {
  export interface DefineLocaleMessage extends MessageSchema {}
}
```

---

## Translation Files

### locales/en.json

```json
{
  "app": {
    "name": "My Application",
    "loading": "Loading..."
  },

  "nav": {
    "home": "Home",
    "dashboard": "Dashboard",
    "settings": "Settings",
    "logout": "Log out"
  },

  "auth": {
    "login": {
      "title": "Sign In",
      "email": "Email Address",
      "password": "Password",
      "submit": "Sign In",
      "forgot": "Forgot password?"
    },
    "register": {
      "title": "Create Account",
      "name": "Full Name",
      "submit": "Create Account"
    }
  },

  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit"
  },

  "messages": {
    "welcome": "Welcome, {name}!",
    "items": "{count} {count, plural, one {item} other {items}}"
  },

  "validation": {
    "required": "This field is required",
    "email": "Please enter a valid email",
    "minLength": "Must be at least {min} characters"
  }
}
```

### locales/de.json

```json
{
  "app": {
    "name": "Meine Anwendung",
    "loading": "Laden..."
  },

  "nav": {
    "home": "Startseite",
    "dashboard": "Dashboard",
    "settings": "Einstellungen",
    "logout": "Abmelden"
  },

  "auth": {
    "login": {
      "title": "Anmelden",
      "email": "E-Mail-Adresse",
      "password": "Passwort",
      "submit": "Anmelden",
      "forgot": "Passwort vergessen?"
    },
    "register": {
      "title": "Konto erstellen",
      "name": "Vollständiger Name",
      "submit": "Konto erstellen"
    }
  },

  "common": {
    "save": "Speichern",
    "cancel": "Abbrechen",
    "delete": "Löschen",
    "edit": "Bearbeiten"
  },

  "messages": {
    "welcome": "Willkommen, {name}!",
    "items": "{count} {count, plural, one {Artikel} other {Artikel}}"
  },

  "validation": {
    "required": "Dieses Feld ist erforderlich",
    "email": "Bitte geben Sie eine gültige E-Mail ein",
    "minLength": "Mindestens {min} Zeichen erforderlich"
  }
}
```

---

## Composables

### composables/useLocale.ts

```typescript
import { computed, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import {
  SUPPORTED_LOCALES,
  RTL_LOCALES,
  loadLocaleMessages,
  type SupportedLocale,
} from '../i18n';

export function useLocale() {
  const { locale, availableLocales } = useI18n();

  const currentLocale = computed(() => locale.value as SupportedLocale);

  const isRTL = computed(() => RTL_LOCALES.includes(currentLocale.value));

  const setLocale = async (newLocale: SupportedLocale) => {
    if (!SUPPORTED_LOCALES.includes(newLocale)) {
      console.warn(`Locale ${newLocale} is not supported`);
      return;
    }

    // Load locale messages if not already loaded
    await loadLocaleMessages(newLocale);

    // Update locale
    locale.value = newLocale;

    // Persist preference
    localStorage.setItem('preferredLocale', newLocale);

    // Update document attributes
    document.documentElement.lang = newLocale;
    document.documentElement.dir = isRTL.value ? 'rtl' : 'ltr';
  };

  // Watch for locale changes
  watch(
    currentLocale,
    (newLocale) => {
      document.documentElement.lang = newLocale;
      document.documentElement.dir = RTL_LOCALES.includes(newLocale) ? 'rtl' : 'ltr';
    },
    { immediate: true }
  );

  return {
    currentLocale,
    isRTL,
    setLocale,
    supportedLocales: SUPPORTED_LOCALES,
    availableLocales,
  };
}
```

---

## Components

### main.ts

```typescript
import { createApp } from 'vue';
import App from './App.vue';
import i18n from './i18n';

const app = createApp(App);
app.use(i18n);
app.mount('#app');
```

### App.vue

```vue
<script setup lang="ts">
import { useLocale } from './composables/useLocale';
import LanguageSwitcher from './components/LanguageSwitcher.vue';

const { isRTL } = useLocale();
</script>

<template>
  <div :dir="isRTL ? 'rtl' : 'ltr'">
    <header>
      <h1>{{ $t('app.name') }}</h1>
      <LanguageSwitcher />
    </header>

    <main>
      <router-view />
    </main>
  </div>
</template>
```

### components/LanguageSwitcher.vue

```vue
<script setup lang="ts">
import { useLocale } from '../composables/useLocale';
import type { SupportedLocale } from '../i18n';

const { currentLocale, setLocale, supportedLocales } = useLocale();

const languageNames: Record<SupportedLocale, string> = {
  en: 'English',
  de: 'Deutsch',
  fr: 'Français',
  ar: 'العربية',
};

const handleChange = async (event: Event) => {
  const target = event.target as HTMLSelectElement;
  await setLocale(target.value as SupportedLocale);
};
</script>

<template>
  <select
    :value="currentLocale"
    @change="handleChange"
    aria-label="Select language"
  >
    <option v-for="locale in supportedLocales" :key="locale" :value="locale">
      {{ languageNames[locale] }}
    </option>
  </select>
</template>
```

---

## Usage Examples

### Basic Usage

```vue
<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
</script>

<template>
  <div>
    <h1>{{ t('auth.login.title') }}</h1>
    <p>{{ t('messages.welcome', { name: 'Alice' }) }}</p>
  </div>
</template>
```

### Pluralisation

```vue
<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { ref } from 'vue';

const { t } = useI18n();
const count = ref(5);
</script>

<template>
  <p>{{ t('messages.items', { count }) }}</p>
  <!-- Output: "5 items" -->
</template>
```

### Per-Component Messages

```vue
<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { t } = useI18n({
  useScope: 'local',
  messages: {
    en: {
      greeting: 'Hello from component!',
    },
    de: {
      greeting: 'Hallo von der Komponente!',
    },
  },
});
</script>

<template>
  <p>{{ t('greeting') }}</p>
</template>
```

### DateTime and Number Formatting

```vue
<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { d, n, locale } = useI18n();

const date = new Date();
const price = 1234.56;
</script>

<template>
  <div>
    <p>Date: {{ d(date, 'long') }}</p>
    <p>Price: {{ n(price, 'currency', { currency: 'EUR' }) }}</p>
  </div>
</template>
```

---

## Vue Router Integration

### router/index.ts

```typescript
import { createRouter, createWebHistory } from 'vue-router';
import { loadLocaleMessages, SUPPORTED_LOCALES, i18n } from '../i18n';
import type { SupportedLocale } from '../i18n';

const routes = [
  {
    path: '/:locale',
    beforeEnter: async (to) => {
      const locale = to.params.locale as SupportedLocale;

      // Validate locale
      if (!SUPPORTED_LOCALES.includes(locale)) {
        return `/${i18n.global.locale.value}`;
      }

      // Load locale if not already loaded
      await loadLocaleMessages(locale);
      i18n.global.locale.value = locale;
    },
    children: [
      { path: '', name: 'home', component: () => import('../views/Home.vue') },
      { path: 'dashboard', name: 'dashboard', component: () => import('../views/Dashboard.vue') },
    ],
  },
  {
    path: '/',
    redirect: () => `/${i18n.global.locale.value}`,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
```

### Locale-Aware Navigation

```vue
<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';

const router = useRouter();
const { locale } = useI18n();

const navigateTo = (path: string) => {
  router.push(`/${locale.value}${path}`);
};
</script>

<template>
  <nav>
    <a @click="navigateTo('/')">{{ $t('nav.home') }}</a>
    <a @click="navigateTo('/dashboard')">{{ $t('nav.dashboard') }}</a>
  </nav>
</template>
```

---

## Form Validation with VeeValidate

```vue
<script setup lang="ts">
import { useForm, useField } from 'vee-validate';
import { useI18n } from 'vue-i18n';
import * as yup from 'yup';

const { t } = useI18n();

// Create schema with translated messages
const schema = yup.object({
  email: yup
    .string()
    .required(t('validation.required'))
    .email(t('validation.email')),
  password: yup
    .string()
    .required(t('validation.required'))
    .min(8, t('validation.minLength', { min: 8 })),
});

const { handleSubmit } = useForm({ validationSchema: schema });
const { value: email, errorMessage: emailError } = useField('email');
const { value: password, errorMessage: passwordError } = useField('password');

const onSubmit = handleSubmit((values) => {
  console.log(values);
});
</script>

<template>
  <form @submit="onSubmit">
    <div>
      <label>{{ t('auth.login.email') }}</label>
      <input v-model="email" type="email" />
      <span v-if="emailError" class="error">{{ emailError }}</span>
    </div>

    <div>
      <label>{{ t('auth.login.password') }}</label>
      <input v-model="password" type="password" />
      <span v-if="passwordError" class="error">{{ passwordError }}</span>
    </div>

    <button type="submit">{{ t('auth.login.submit') }}</button>
  </form>
</template>
```

---

## Vite Configuration

### vite.config.ts

```typescript
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueI18n from '@intlify/vite-plugin-vue-i18n';
import { resolve } from 'path';

export default defineConfig({
  plugins: [
    vue(),
    vueI18n({
      include: resolve(__dirname, './src/locales/**'),
      strictMessage: false,
    }),
  ],
});
```

---

## Testing

### Test Setup

```typescript
// test/setup.ts
import { config } from '@vue/test-utils';
import { createI18n } from 'vue-i18n';
import en from '../src/locales/en.json';

const i18n = createI18n({
  legacy: false,
  locale: 'en',
  messages: { en },
});

config.global.plugins = [i18n];
```

### Component Test

```typescript
// components/LanguageSwitcher.spec.ts
import { mount } from '@vue/test-utils';
import { createI18n } from 'vue-i18n';
import LanguageSwitcher from './LanguageSwitcher.vue';

const i18n = createI18n({
  legacy: false,
  locale: 'en',
  messages: { en: {}, de: {} },
});

describe('LanguageSwitcher', () => {
  it('renders language options', () => {
    const wrapper = mount(LanguageSwitcher, {
      global: { plugins: [i18n] },
    });

    const options = wrapper.findAll('option');
    expect(options.length).toBeGreaterThan(0);
  });
});
```

---

## Checklist

- REQUIRED: Install vue-i18n
- REQUIRED: Create i18n configuration with Composition API
- REQUIRED: Set up TypeScript types
- REQUIRED: Create locale JSON files
- REQUIRED: Create `useLocale` composable
- REQUIRED: Add LanguageSwitcher component
- REQUIRED: Handle RTL direction
- REQUIRED: Integrate with Vue Router (if routing locales)
- REQUIRED: Configure Vite plugin (if using i18n resource transforms)
- REQUIRED: Set up test configuration
