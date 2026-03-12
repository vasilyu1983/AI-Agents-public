# Vue.js + Nuxt Best Practices & Patterns (Nuxt 4)

Operational patterns for building production-ready Vue and Nuxt applications.

---

## Contents

- Vue 3 Composition API Patterns
- Nuxt 4 Patterns
  - Auto-imports
  - Data Fetching (useAsyncData, useFetch, $fetch)
  - Nitro Server Routes
  - Route Middleware
  - Plugins
  - Runtime Config
- State Management with Pinia
- Performance Optimization
- SEO Patterns
- Testing Patterns
- Common Mistakes to Avoid
- Resources

---

## Vue 3 Composition API Patterns

### Script Setup (Recommended)

```vue
<script setup lang="ts">
// Auto-imported in Nuxt — no need for explicit imports
const count = ref(0)
const doubled = computed(() => count.value * 2)

const increment = () => count.value++

// Props
interface Props {
  title: string
  count?: number
}
const props = withDefaults(defineProps<Props>(), {
  count: 0
})

// Emits
const emit = defineEmits<{
  update: [value: number]
  delete: [id: string]
}>()

// Lifecycle
onMounted(() => {
  console.log('Component mounted')
})
</script>
```

### Composables Pattern

```typescript
// composables/useCounter.ts
export const useCounter = (initialValue = 0) => {
  const count = ref(initialValue)
  const doubled = computed(() => count.value * 2)

  const increment = () => count.value++
  const decrement = () => count.value--
  const reset = () => { count.value = initialValue }

  return {
    count: readonly(count),
    doubled,
    increment,
    decrement,
    reset
  }
}
```

Keep composables focused on a single concern. Prefix with `use`. Nuxt auto-imports anything exported from `composables/` with a `use` prefix.

---

## Nuxt 4 Patterns

### Auto-imports

Nuxt auto-imports:
- Components from `components/`
- Composables from `composables/`
- Utils from `utils/`
- Vue APIs (`ref`, `computed`, `onMounted`, etc.)
- Nuxt APIs (`useAsyncData`, `useFetch`, `useHead`, `navigateTo`, etc.)

### Data Fetching

#### useAsyncData vs useFetch vs $fetch

| Method | Use When | SSR Hydrated |
|--------|----------|-------------|
| `useFetch` | Fetching from API routes, simplest option | Yes |
| `useAsyncData` | Custom fetching logic, more control over caching keys | Yes |
| `$fetch` | User-triggered actions (form submits, button clicks), server routes calling external APIs | No |

```typescript
// useFetch — convenient wrapper, SSR-safe
const { data, status, error, refresh } = await useFetch('/api/posts', {
  query: { page: 1 },
  headers: { 'Authorization': `Bearer ${token}` }
})

// useAsyncData — more control, custom fetching
const { data, pending, error, refresh } = await useAsyncData(
  'posts',                        // unique cache key
  () => $fetch('/api/posts'),
  { watch: [page] }               // re-fetch when page changes
)

// $fetch — for mutations and user-triggered actions (NOT SSR-hydrated)
async function createPost(body: CreatePostInput) {
  await $fetch('/api/posts', {
    method: 'POST',
    body
  })
  await refreshNuxtData('posts')  // invalidate the cached data
}
```

#### Error Handling

Always handle errors from data fetching — `useFetch` and `useAsyncData` don't throw by default.

```vue
<script setup lang="ts">
const { data: posts, error, status } = await useFetch('/api/posts')
</script>

<template>
  <div v-if="error">
    <p>Failed to load posts: {{ error.message }}</p>
    <button @click="refresh()">Retry</button>
  </div>
  <div v-else-if="status === 'pending'">
    <LoadingSkeleton />
  </div>
  <div v-else>
    <PostCard v-for="post in posts" :key="post.id" :post="post" />
  </div>
</template>
```

### Nitro Server Routes

Nuxt 4 uses Nitro as its server engine. Server routes live in `server/` and run on the server only.

#### API Routes

```typescript
// server/api/posts/index.get.ts — handles GET /api/posts
export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const page = Number(query.page) || 1
  const limit = Number(query.limit) || 20

  const posts = await prisma.post.findMany({
    skip: (page - 1) * limit,
    take: limit,
    orderBy: { createdAt: 'desc' }
  })

  return posts
})

// server/api/posts/index.post.ts — handles POST /api/posts
export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  // Validate with Zod
  const parsed = createPostSchema.safeParse(body)
  if (!parsed.success) {
    throw createError({
      statusCode: 400,
      message: 'Validation failed',
      data: parsed.error.flatten()
    })
  }

  const post = await prisma.post.create({
    data: parsed.data
  })

  setResponseStatus(event, 201)
  return post
})

// server/api/posts/[id].get.ts — handles GET /api/posts/:id
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')

  const post = await prisma.post.findUnique({ where: { id } })
  if (!post) {
    throw createError({ statusCode: 404, message: 'Post not found' })
  }

  return post
})
```

File naming convention: `[method].ts` suffix determines the HTTP method. `index.get.ts` handles GET, `index.post.ts` handles POST, etc.

#### Server Middleware

Server middleware runs on every request before route handlers. Use for auth verification, logging, CORS.

```typescript
// server/middleware/auth.ts
export default defineEventHandler(async (event) => {
  // Skip auth for public routes
  const publicPaths = ['/api/auth/login', '/api/auth/register']
  if (publicPaths.some(p => event.path?.startsWith(p))) return

  // Only protect /api/ routes
  if (!event.path?.startsWith('/api/')) return

  const token = getHeader(event, 'authorization')?.replace('Bearer ', '')
  if (!token) {
    throw createError({ statusCode: 401, message: 'Unauthorized' })
  }

  try {
    const user = verifyJwt(token)
    event.context.auth = user
  } catch {
    throw createError({ statusCode: 401, message: 'Invalid token' })
  }
})
```

Access auth context in route handlers via `event.context.auth`.

#### Server Utils

Shared utilities in `server/utils/` are auto-imported in server routes.

```typescript
// server/utils/db.ts
import { PrismaClient } from '@prisma/client'

let prisma: PrismaClient

export function usePrisma() {
  if (!prisma) {
    prisma = new PrismaClient()
  }
  return prisma
}
```

### Route Middleware

Route middleware runs on the client (and server during SSR) before navigating to a page. Use for auth guards and redirects.

```typescript
// middleware/auth.global.ts — runs on every route
export default defineNuxtRouteMiddleware((to) => {
  const { isAuthenticated } = useAuth()

  const publicPages = ['/', '/login', '/register']
  if (!publicPages.includes(to.path) && !isAuthenticated.value) {
    return navigateTo('/login')
  }
})

// middleware/guest.ts — named middleware, opt-in per page
export default defineNuxtRouteMiddleware(() => {
  const { isAuthenticated } = useAuth()

  if (isAuthenticated.value) {
    return navigateTo('/dashboard')
  }
})
```

Apply named middleware on a page:

```vue
<!-- pages/login.vue -->
<script setup lang="ts">
definePageMeta({
  middleware: 'guest',
  layout: 'auth'
})
</script>
```

### Plugins

Plugins run once when the app initializes. Use for registering global utilities, third-party libraries, or injecting helpers.

```typescript
// plugins/api.ts
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()

  const api = $fetch.create({
    baseURL: config.public.apiBase,
    onRequest({ options }) {
      const token = useCookie('auth-token')
      if (token.value) {
        options.headers.set('Authorization', `Bearer ${token.value}`)
      }
    },
    onResponseError({ response }) {
      if (response.status === 401) {
        navigateTo('/login')
      }
    }
  })

  return {
    provide: { api }
  }
})
```

Access via `const { $api } = useNuxtApp()` in components and composables.

### Runtime Config

Use `useRuntimeConfig()` for environment-specific values. Public values are exposed to the client; private values stay server-side.

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  runtimeConfig: {
    // Server-only (not exposed to client)
    jwtSecret: process.env.JWT_SECRET,
    databaseUrl: process.env.DATABASE_URL,

    // Client-exposed (prefixed with public)
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || '/api',
      appName: 'My App'
    }
  }
})
```

```typescript
// In server routes — full config available
const config = useRuntimeConfig()
console.log(config.jwtSecret)       // server-only value
console.log(config.public.apiBase)  // public value

// In components — only public config
const config = useRuntimeConfig()
console.log(config.public.apiBase)  // works
// config.jwtSecret — undefined on client
```

---

## State Management with Pinia

### Setup Store (Recommended in Nuxt 4)

Use the Composition API syntax for stores — it's consistent with composables and easier to type.

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = useCookie('auth-token')  // SSR-safe via useCookie

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  async function login(credentials: LoginInput) {
    const response = await $fetch<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: credentials
    })
    user.value = response.user
    token.value = response.token
  }

  function logout() {
    user.value = null
    token.value = null
    navigateTo('/login')
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      user.value = await $fetch<User>('/api/users/me')
    } catch {
      logout()
    }
  }

  return { user, token, isAuthenticated, login, logout, fetchUser }
})
```

### SSR Hydration

`@pinia/nuxt` handles Pinia SSR hydration automatically — state created during server rendering is serialized and hydrated on the client. No manual setup needed.

Key rules:
- Use `useCookie()` (not `localStorage`) for values that must survive SSR (tokens, preferences). `useCookie` is SSR-safe; `localStorage` is not.
- Use `useState()` for simple cross-component state that should hydrate but doesn't need a full store.
- Don't call `$fetch` in store initialization — use `callOnce()` or trigger fetching from a plugin/page.

```typescript
// plugins/auth.server.ts — fetch user on server during SSR
export default defineNuxtPlugin(async () => {
  const auth = useAuthStore()
  await auth.fetchUser()
})
```

---

## Performance Optimization

### Lazy Loading Components

```vue
<script setup lang="ts">
// Lazy-load heavy components — Nuxt auto-prefixes with 'Lazy'
// Just add 'Lazy' prefix to component name in template
</script>

<template>
  <!-- Loaded immediately -->
  <AppHeader />

  <!-- Lazy-loaded when visible / needed -->
  <LazyHeavyChart :data="chartData" />

  <!-- With Suspense for loading state -->
  <Suspense>
    <LazyExpensiveWidget />
    <template #fallback>
      <LoadingSkeleton />
    </template>
  </Suspense>
</template>
```

### Virtual Scrolling

```vue
<script setup lang="ts">
import { useVirtualList } from '@vueuse/core'

const { list, containerProps, wrapperProps } = useVirtualList(
  largeArray,
  { itemHeight: 50 }
)
</script>

<template>
  <div v-bind="containerProps" style="height: 400px">
    <div v-bind="wrapperProps">
      <div v-for="{ data, index } in list" :key="index">
        {{ data }}
      </div>
    </div>
  </div>
</template>
```

### NuxtIsland (Partial Hydration)

Use `<NuxtIsland>` to render components on the server without sending their JavaScript to the client. Ideal for static content blocks on otherwise interactive pages.

```vue
<template>
  <!-- This component renders on the server only — zero client JS -->
  <NuxtIsland name="StaticFooter" />

  <!-- With props -->
  <NuxtIsland name="ProductCard" :props="{ product }" />
</template>
```

The island component must be in `components/islands/` or have a `.server.vue` suffix.

### Payload Optimization

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  experimental: {
    payloadExtraction: true  // extract shared payloads for prerendered pages
  }
})
```

---

## SEO Patterns

### useSeoMeta (Preferred for Social Meta)

`useSeoMeta` provides a flat, type-safe API for SEO meta tags — simpler than `useHead` for common cases.

```vue
<script setup lang="ts">
const { data: post } = await useFetch(`/api/posts/${route.params.slug}`)

useSeoMeta({
  title: () => post.value?.title,
  description: () => post.value?.excerpt,
  ogTitle: () => post.value?.title,
  ogDescription: () => post.value?.excerpt,
  ogImage: () => post.value?.image,
  twitterCard: 'summary_large_image'
})
</script>
```

### useHead (For Full Control)

Use `useHead` when you need link tags, scripts, or non-meta head elements.

```vue
<script setup lang="ts">
useHead({
  title: post.value?.title,
  link: [
    { rel: 'canonical', href: `https://example.com/blog/${route.params.slug}` }
  ],
  script: [
    { type: 'application/ld+json', innerHTML: JSON.stringify(structuredData) }
  ]
})
</script>
```

### Sitemap

```bash
npx nuxi module add @nuxtjs/sitemap
```

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  site: { url: 'https://example.com' },
  sitemap: {
    sources: ['/api/__sitemap__/urls']  // dynamic routes
  }
})
```

---

## Testing Patterns

### Component Test

```typescript
import { mountSuspended } from '@nuxt/test-utils/runtime'
import { describe, it, expect } from 'vitest'
import Counter from '~/components/Counter.vue'

describe('Counter', () => {
  it('increments count on button click', async () => {
    const wrapper = await mountSuspended(Counter)

    await wrapper.find('button').trigger('click')

    expect(wrapper.text()).toContain('Count: 1')
  })

  it('renders with default props', async () => {
    const wrapper = await mountSuspended(Counter, {
      props: { initialCount: 5 }
    })

    expect(wrapper.text()).toContain('Count: 5')
  })
})
```

### Composable Test

```typescript
import { describe, it, expect } from 'vitest'
import { useCounter } from '~/composables/useCounter'

describe('useCounter', () => {
  it('starts with initial value', () => {
    const { count } = useCounter(10)
    expect(count.value).toBe(10)
  })

  it('increments and decrements', () => {
    const { count, increment, decrement } = useCounter(0)
    increment()
    expect(count.value).toBe(1)
    decrement()
    expect(count.value).toBe(0)
  })
})
```

### Server Route Test

```typescript
import { describe, it, expect } from 'vitest'
import { $fetch, setup } from '@nuxt/test-utils'

describe('POST /api/posts', async () => {
  await setup({ server: true })

  it('creates a post with valid data', async () => {
    const post = await $fetch('/api/posts', {
      method: 'POST',
      body: { title: 'Test', content: 'Hello world' }
    })

    expect(post.id).toBeDefined()
    expect(post.title).toBe('Test')
  })

  it('returns 400 for invalid data', async () => {
    const error = await $fetch('/api/posts', {
      method: 'POST',
      body: {}
    }).catch(e => e)

    expect(error.statusCode).toBe(400)
  })
})
```

### Pinia Store Test

```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useCartStore } from '~/stores/cart'

describe('useCartStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('adds items to cart', () => {
    const cart = useCartStore()
    cart.addItem({ id: '1', name: 'Widget', price: 10, quantity: 1 })

    expect(cart.itemCount).toBe(1)
    expect(cart.total).toBe(10)
  })

  it('increments quantity for duplicate items', () => {
    const cart = useCartStore()
    cart.addItem({ id: '1', name: 'Widget', price: 10, quantity: 1 })
    cart.addItem({ id: '1', name: 'Widget', price: 10, quantity: 1 })

    expect(cart.itemCount).toBe(2)
    expect(cart.items).toHaveLength(1)
  })
})
```

---

## Common Mistakes to Avoid

**Don't destructure reactive objects — you lose reactivity:**
```typescript
// Bad — count is now a plain number
const { count } = reactive({ count: 0 })

// Good — use ref or keep the reactive object intact
const count = ref(0)
const state = reactive({ count: 0 })
```

**Don't use reactive() for primitives:**
```typescript
// Bad — reactive only works with objects
const count = reactive(0)

// Good
const count = ref(0)
```

**Don't call $fetch directly in setup without useFetch/useAsyncData — it fires twice (server + client):**
```typescript
// Bad — runs on server during SSR, then again on client hydration
const data = await $fetch('/api/posts')

// Good — SSR-hydrated, runs once
const { data } = await useFetch('/api/posts')
```

**Don't use localStorage in setup — it breaks SSR:**
```typescript
// Bad — localStorage doesn't exist on server
const theme = ref(localStorage.getItem('theme'))

// Good — useCookie is SSR-safe
const theme = useCookie('theme', { default: () => 'light' })

// Also good — guard with process.client
const theme = ref('light')
if (import.meta.client) {
  theme.value = localStorage.getItem('theme') || 'light'
}
```

**Don't forget unique keys for useAsyncData:**
```typescript
// Bad — colliding keys cause stale data
const { data: a } = await useAsyncData('data', () => $fetch('/api/a'))
const { data: b } = await useAsyncData('data', () => $fetch('/api/b'))

// Good — unique keys per data source
const { data: a } = await useAsyncData('users', () => $fetch('/api/a'))
const { data: b } = await useAsyncData('posts', () => $fetch('/api/b'))
```

**Don't mutate props directly:**
```typescript
// Bad
props.count++

// Good — emit an event for the parent to handle
emit('update:count', props.count + 1)
```

---

## Resources

- [Vue 3 Docs](https://vuejs.org/)
- [Nuxt 4 Docs](https://nuxt.com/docs)
- [Pinia Docs](https://pinia.vuejs.org/)
- [VueUse](https://vueuse.org/)
- [Nitro Docs](https://nitro.build/)
- [@nuxt/test-utils](https://nuxt.com/docs/getting-started/testing)
