# Nuxt 4 + Vue 3 + Tailwind CSS Starter Template

Production-ready template for building full-stack web applications with Nuxt 4, Vue 3, TypeScript, and Tailwind CSS.

---

## Overview

This template provides a modern Nuxt 4 setup with:
- **Nuxt 4** - Progressive Vue.js framework with Nitro server engine
- **Vue 3** - Composition API with `<script setup>`
- **TypeScript** - Full type safety
- **Tailwind CSS** - Utility-first styling
- **Pinia** - Official Vue state management
- **Nuxt UI** or **shadcn-vue** - Component libraries
- **VueUse** - Composition utilities
- **Vitest** - Unit testing
- **Playwright** - E2E testing

---

## Project Setup

### Initialize Project

```bash
# Create Nuxt 4 project
npx nuxi@latest init my-app
cd my-app

# Install dependencies
npm install

# Add Tailwind CSS
npx nuxi@latest module add @nuxtjs/tailwindcss

# TypeScript support is built in (enable strict mode in `tsconfig.json`)

# Add UI components (choose one)
# Option A: Nuxt UI (recommended)
npx nuxi@latest module add @nuxt/ui

# Option B: shadcn-vue
npx nuxi@latest module add shadcn-nuxt
npx shadcn-vue@latest init

# Add state management
npm install pinia @pinia/nuxt

# Add VueUse
npm install @vueuse/nuxt @vueuse/core

# Add testing
npm install -D @nuxt/test-utils vitest @vue/test-utils happy-dom playwright
```

---

## Project Structure

```
my-app/
|-- .nuxt/                   # Build output (auto-generated)
|-- .output/                 # Production build
|-- app.vue                  # Root component
|-- nuxt.config.ts           # Nuxt configuration
|-- tsconfig.json            # TypeScript config
|-- tailwind.config.ts       # Tailwind config
|-- pages/                   # File-based routing
|   |-- index.vue            # Home page (/)
|   |-- about.vue            # About page (/about)
|   `-- blog/
|       |-- index.vue        # /blog
|       `-- [slug].vue       # /blog/:slug (dynamic route)
|-- layouts/                 # Layouts
|   |-- default.vue          # Default layout
|   `-- dashboard.vue        # Dashboard layout
|-- components/              # Auto-imported components
|   |-- ui/                  # UI components (shadcn-vue)
|   |-- AppHeader.vue        # Header component
|   `-- AppFooter.vue        # Footer component
|-- composables/             # Auto-imported composables
|   |-- useAuth.ts           # Auth composable
|   `-- useApi.ts            # API composable
|-- server/                  # Server directory (Nitro)
|   |-- api/                 # API routes
|   |   |-- users.get.ts     # GET /api/users
|   |   `-- users/
|   |       `-- [id].get.ts  # GET /api/users/:id
|   |-- middleware/          # Server middleware
|   `-- utils/               # Server utilities
|-- stores/                  # Pinia stores
|   |-- auth.ts              # Auth store
|   `-- cart.ts              # Cart store
|-- assets/                  # Uncompiled assets
|   `-- css/
|       `-- main.css         # Global CSS
|-- public/                  # Static files
|   |-- favicon.ico
|   `-- images/
`-- tests/                   # Tests
    |-- unit/
    `-- e2e/
```

---

## Configuration Files

### nuxt.config.ts

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxt/ui',           // or 'shadcn-nuxt'
    '@pinia/nuxt',
    '@vueuse/nuxt',
  ],

  typescript: {
    strict: true,
    typeCheck: true,
  },

  app: {
    head: {
      title: 'My Nuxt App',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'My awesome Nuxt 4 app' },
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
      ],
    },
  },

  // Runtime config (environment variables)
  runtimeConfig: {
    // Private keys (server-only)
    apiSecret: process.env.API_SECRET,

    // Public keys (exposed to client)
    public: {
      apiBase: process.env.API_BASE_URL || 'http://localhost:3000',
    },
  },

  // Nitro server configuration
  nitro: {
    preset: 'node-server',  // or 'vercel', 'netlify', etc.
  },
})
```

### tailwind.config.ts

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss'

export default <Partial<Config>>{
  content: [
    './components/**/*.{js,vue,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './plugins/**/*.{js,ts}',
    './app.vue',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
    },
  },
  plugins: [],
}
```

---

## Common Patterns

### Page with Data Fetching

```vue
<!-- pages/blog/[slug].vue -->
<script setup lang="ts">
// Route params are auto-typed
const route = useRoute()
const slug = route.params.slug

// useAsyncData for data fetching (SSR-friendly)
const { data: post, error } = await useAsyncData(
  `post-${slug}`,
  () => $fetch(`/api/posts/${slug}`)
)

// Handle not found
if (!post.value) {
  throw createError({
    statusCode: 404,
    message: 'Post not found',
  })
}

// SEO metadata
useSeoMeta({
  title: post.value.title,
  description: post.value.excerpt,
  ogImage: post.value.image,
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <article v-if="post">
      <h1 class="text-4xl font-bold mb-4">{{ post.title }}</h1>
      <p class="text-gray-600 mb-8">{{ post.excerpt }}</p>
      <div v-html="post.content" />
    </article>
  </div>
</template>
```

### Component with Composables

```vue
<!-- components/UserProfile.vue -->
<script setup lang="ts">
// Auto-imported composables
const { user, isAuthenticated, logout } = useAuth()
const { formatDate } = useFormatters()

// Component props
interface Props {
  showEmail?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  showEmail: false,
})

// Local state
const isEditing = ref(false)

// Computed
const displayName = computed(() =>
  user.value ? `${user.value.firstName} ${user.value.lastName}` : 'Guest'
)

// Methods
const handleLogout = async () => {
  await logout()
  navigateTo('/login')
}
</script>

<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-2xl font-bold">{{ displayName }}</h2>
      <button
        @click="handleLogout"
        class="text-red-600 hover:text-red-800"
      >
        Logout
      </button>
    </div>

    <div v-if="user">
      <p v-if="showEmail" class="text-gray-600">{{ user.email }}</p>
      <p class="text-sm text-gray-500">
        Member since {{ formatDate(user.createdAt) }}
      </p>
    </div>
  </div>
</template>
```

### Composable (Auto-imported)

```typescript
// composables/useAuth.ts
export const useAuth = () => {
  const user = useState<User | null>('user', () => null)
  const token = useCookie('auth_token')

  const isAuthenticated = computed(() => !!user.value)

  const login = async (credentials: LoginCredentials) => {
    const data = await $fetch('/api/auth/login', {
      method: 'POST',
      body: credentials,
    })

    user.value = data.user
    token.value = data.token
  }

  const logout = async () => {
    await $fetch('/api/auth/logout', { method: 'POST' })
    user.value = null
    token.value = null
  }

  const fetchUser = async () => {
    if (!token.value) return

    try {
      user.value = await $fetch('/api/auth/me')
    } catch (error) {
      token.value = null
    }
  }

  return {
    user: readonly(user),
    isAuthenticated,
    login,
    logout,
    fetchUser,
  }
}
```

### API Route (Server)

```typescript
// server/api/posts/index.get.ts
export default defineEventHandler(async (event) => {
  // Query parameters
  const query = getQuery(event)
  const page = Number(query.page) || 1
  const limit = Number(query.limit) || 10

  // Database query (example with Prisma)
  const posts = await prisma.post.findMany({
    skip: (page - 1) * limit,
    take: limit,
    orderBy: { createdAt: 'desc' },
  })

  const total = await prisma.post.count()

  return {
    data: posts,
    meta: {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit),
    },
  }
})
```

### API Route with Validation

```typescript
// server/api/posts/index.post.ts
import { z } from 'zod'

const postSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(10),
  published: z.boolean().default(false),
})

export default defineEventHandler(async (event) => {
  // Parse and validate body
  const body = await readBody(event)
  const result = postSchema.safeParse(body)

  if (!result.success) {
    throw createError({
      statusCode: 400,
      message: 'Validation failed',
      data: result.error.flatten(),
    })
  }

  // Create post
  const post = await prisma.post.create({
    data: result.data,
  })

  return post
})
```

### Pinia Store

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = useCookie('auth_token')

  // Getters
  const isAuthenticated = computed(() => !!user.value)
  const userName = computed(() => user.value?.name || 'Guest')

  // Actions
  const login = async (credentials: LoginCredentials) => {
    const data = await $fetch('/api/auth/login', {
      method: 'POST',
      body: credentials,
    })

    user.value = data.user
    token.value = data.token
  }

  const logout = () => {
    user.value = null
    token.value = null
  }

  return {
    user,
    token,
    isAuthenticated,
    userName,
    login,
    logout,
  }
})
```

### Layout

```vue
<!-- layouts/default.vue -->
<script setup lang="ts">
const { user } = useAuth()
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <header class="bg-white shadow">
      <nav class="container mx-auto px-4 py-4">
        <div class="flex items-center justify-between">
          <NuxtLink to="/" class="text-xl font-bold">
            My App
          </NuxtLink>

          <div class="flex items-center gap-4">
            <NuxtLink to="/about">About</NuxtLink>
            <NuxtLink to="/blog">Blog</NuxtLink>

            <div v-if="user">
              <NuxtLink to="/dashboard">Dashboard</NuxtLink>
            </div>
            <div v-else>
              <NuxtLink to="/login">Login</NuxtLink>
            </div>
          </div>
        </div>
      </nav>
    </header>

    <main class="flex-1">
      <slot />
    </main>

    <footer class="bg-gray-100 py-8">
      <div class="container mx-auto px-4 text-center text-gray-600">
        (c) 2025 My App. All rights reserved.
      </div>
    </footer>
  </div>
</template>
```

---

## Testing

### Unit Test (Vitest)

```typescript
// tests/unit/composables/useAuth.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { useAuth } from '~/composables/useAuth'

describe('useAuth', () => {
  beforeEach(() => {
    // Reset state
  })

  it('should initialize with no user', () => {
    const { user, isAuthenticated } = useAuth()
    expect(user.value).toBeNull()
    expect(isAuthenticated.value).toBe(false)
  })

  it('should login successfully', async () => {
    const { login, user, isAuthenticated } = useAuth()

    await login({ email: 'test@example.com', password: 'password' })

    expect(user.value).toBeTruthy()
    expect(isAuthenticated.value).toBe(true)
  })
})
```

### E2E Test (Playwright)

```typescript
// tests/e2e/auth.test.ts
import { test, expect } from '@playwright/test'

test('user can login', async ({ page }) => {
  await page.goto('/')

  // Click login link
  await page.click('text=Login')

  // Fill form
  await page.fill('input[name="email"]', 'test@example.com')
  await page.fill('input[name="password"]', 'password')
  await page.click('button[type="submit"]')

  // Verify redirect
  await expect(page).toHaveURL('/dashboard')
  await expect(page.locator('text=Dashboard')).toBeVisible()
})
```

---

## Production Checklist

### Performance
- [ ] Enable image optimization with `<NuxtImg>` component
- [ ] Use `lazy` loading for below-fold content
- [ ] Implement route-level code splitting (automatic)
- [ ] Configure caching strategies in `nitro.config.ts`
- [ ] Use `<ClientOnly>` for client-only components

### SEO
- [ ] Configure `useSeoMeta()` for all pages
- [ ] Add `robots.txt` in `/public`
- [ ] Add `sitemap.xml` (use `@nuxtjs/sitemap` module)
- [ ] Configure Open Graph meta tags
- [ ] Enable server-side rendering (default)

### Security
- [ ] Use runtime config for sensitive data
- [ ] Implement CSRF protection for API routes
- [ ] Add rate limiting to API routes
- [ ] Configure CORS properly
- [ ] Use `httpOnly` cookies for auth tokens

### Deployment
- [ ] Set `NODE_ENV=production`
- [ ] Configure environment variables
- [ ] Run `npm run build` and test `.output/`
- [ ] Choose deployment preset (Vercel, Netlify, Node)
- [ ] Set up CI/CD pipeline

---

## Useful Commands

```bash
# Development
npm run dev              # Start dev server (localhost:3000)

# Build
npm run build            # Build for production
npm run preview          # Preview production build locally

# Testing
npm run test             # Run unit tests
npm run test:e2e         # Run E2E tests

# Type checking
npm run typecheck        # Check TypeScript types

# Linting
npm run lint             # Run ESLint
npm run lint:fix         # Fix ESLint errors
```

---

## Additional Resources

- [Nuxt Documentation](https://nuxt.com/docs)
- [Vue 3 Documentation](https://vuejs.org/)
- [Nuxt UI](https://ui.nuxt.com/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [VueUse](https://vueuse.org/)
- [Nitro Documentation](https://nitro.unjs.io/)

---

## Notes

- **Auto-imports**: Components, composables, and Vue APIs are auto-imported
- **TypeScript**: Full type safety with strict mode enabled
- **SSR by default**: Pages render on the server for better SEO and performance
- **API routes**: Built-in server with Nitro engine
- **File-based routing**: Pages automatically become routes
