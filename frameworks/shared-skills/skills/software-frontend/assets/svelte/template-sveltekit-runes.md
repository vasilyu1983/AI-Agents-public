# SvelteKit + Svelte 5 Runes Starter Template

Production-ready template for building modern full-stack applications with SvelteKit and Svelte 5 runes reactivity.

---

## Overview

- **SvelteKit** - Full-stack Svelte framework with SSR/SSG
- **Svelte 5** - Latest with runes-based reactivity
- **TypeScript** - Type safety
- **TailwindCSS** - Utility-first styling
- **Prisma** or **Drizzle** - Database ORM
- **Vitest** - Unit testing
- **Playwright** - E2E testing

---

## Quick Start

```bash
# Create project
npm create svelte@latest my-app
cd my-app
npm install

# Add TailwindCSS
npx svelte-add@latest tailwindcss
npm install

# Add Prisma
npm install -D prisma
npm install @prisma/client
npx prisma init

# Testing
npm install -D vitest @testing-library/svelte
npm init playwright@latest
```

---

## Project Structure

```
my-app/
|-- src/
|   |-- lib/
|   |   |-- components/          # Reusable components
|   |   |-- server/              # Server-only code
|   |   `-- stores/              # Svelte stores
|   |-- routes/
|   |   |-- +page.svelte         # Home (/)
|   |   |-- +layout.svelte       # Root layout
|   |   |-- blog/
|   |   |   |-- +page.svelte     # /blog
|   |   |   `-- [slug]/
|   |   |       |-- +page.svelte # /blog/:slug
|   |   |       `-- +page.server.ts
|   |   `-- api/
|   |       `-- posts/
|   |           `-- +server.ts   # API route
|   |-- app.html                 # HTML template
|   `-- app.css                  # Global styles
|-- static/                      # Static assets
|-- svelte.config.js
|-- vite.config.ts
`-- tailwind.config.ts
```

---

## Core Patterns

### Component with Runes

```svelte
<!-- src/lib/components/Counter.svelte -->
<script lang="ts">
  // Reactive state with $state()
  let count = $state(0);

  // Derived state with $derived()
  let doubled = $derived(count * 2);

  function increment() {
    count += 1;
  }

  function decrement() {
    count -= 1;
  }
</script>

<div class="counter">
  <h2>Count: {count}</h2>
  <p>Doubled: {doubled}</p>
  <button onclick={increment}>+</button>
  <button onclick={decrement}>-</button>
</div>

<style>
  .counter {
    text-align: center;
    padding: 2rem;
  }
</style>
```

### Page with Data Loading

```svelte
<!-- src/routes/blog/[slug]/+page.svelte -->
<script lang="ts">
  import type { PageData } from './$types';

  // Props with $props()
  let { data }: { data: PageData } = $props();

  // Reactive variables
  let liked = $state(false);
</script>

<article>
  <h1>{data.post.title}</h1>
  <p>{data.post.excerpt}</p>
  <div>{@html data.post.content}</div>

  <button onclick={() => liked = !liked}>
    {liked ? 'Liked' : 'Like'}
  </button>
</article>
```

```typescript
// src/routes/blog/[slug]/+page.server.ts
import type { PageServerLoad } from './$types';
import { prisma } from '$lib/server/prisma';

export const load: PageServerLoad = async ({ params }) => {
  const post = await prisma.post.findUnique({
    where: { slug: params.slug },
  });

  if (!post) {
    throw error(404, 'Post not found');
  }

  return { post };
};
```

### Form Actions

```svelte
<!-- src/routes/login/+page.svelte -->
<script lang="ts">
  import { enhance } from '$app/forms';
  import type { ActionData } from './$types';

  let { form }: { form: ActionData } = $props();
</script>

<form method="POST" use:enhance>
  <input
    name="email"
    type="email"
    placeholder="Email"
    required
  />
  {#if form?.errors?.email}
    <span class="error">{form.errors.email}</span>
  {/if}

  <input
    name="password"
    type="password"
    placeholder="Password"
    required
  />
  {#if form?.errors?.password}
    <span class="error">{form.errors.password}</span>
  {/if}

  <button type="submit">Login</button>

  {#if form?.success}
    <p class="success">Login successful!</p>
  {/if}
</form>
```

```typescript
// src/routes/login/+page.server.ts
import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

export const actions: Actions = {
  default: async ({ request, cookies }) => {
    const formData = await request.formData();
    const email = formData.get('email');
    const password = formData.get('password');

    const result = loginSchema.safeParse({ email, password });

    if (!result.success) {
      return fail(400, {
        errors: result.error.flatten().fieldErrors,
      });
    }

    // Authenticate user
    const user = await authenticateUser(result.data);

    if (!user) {
      return fail(401, {
        errors: { email: 'Invalid credentials' },
      });
    }

    // Set session
    cookies.set('session', user.sessionToken, {
      path: '/',
      httpOnly: true,
      secure: true,
      sameSite: 'strict',
      maxAge: 60 * 60 * 24 * 7, // 1 week
    });

    throw redirect(303, '/dashboard');
  },
};
```

### API Route

```typescript
// src/routes/api/posts/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { prisma } from '$lib/server/prisma';

export const GET: RequestHandler = async ({ url }) => {
  const page = Number(url.searchParams.get('page')) || 1;
  const limit = Number(url.searchParams.get('limit')) || 10;

  const posts = await prisma.post.findMany({
    skip: (page - 1) * limit,
    take: limit,
    orderBy: { createdAt: 'desc' },
  });

  const total = await prisma.post.count();

  return json({
    data: posts,
    meta: { page, limit, total },
  });
};

export const POST: RequestHandler = async ({ request }) => {
  const body = await request.json();

  const post = await prisma.post.create({
    data: body,
  });

  return json(post, { status: 201 });
};
```

### Universal Reactive Store

```typescript
// src/lib/stores/auth.svelte.ts
// Runes work in .ts files with .svelte.ts extension
export function createAuthStore() {
  let user = $state<User | null>(null);
  let token = $state<string | null>(null);

  // Computed
  let isAuthenticated = $derived(!!user);

  return {
    get user() { return user; },
    get token() { return token; },
    get isAuthenticated() { return isAuthenticated; },

    login(newUser: User, newToken: string) {
      user = newUser;
      token = newToken;
    },

    logout() {
      user = null;
      token = null;
    },
  };
}

// Export singleton
export const authStore = createAuthStore();
```

Usage:
```svelte
<script lang="ts">
  import { authStore } from '$lib/stores/auth.svelte';
</script>

<div>
  {#if authStore.isAuthenticated}
    <p>Welcome, {authStore.user?.name}!</p>
    <button onclick={() => authStore.logout()}>Logout</button>
  {:else}
    <a href="/login">Login</a>
  {/if}
</div>
```

---

## Testing

### Component Test

```typescript
// src/lib/components/Counter.test.ts
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import Counter from './Counter.svelte';

describe('Counter', () => {
  it('renders initial count', () => {
    render(Counter);
    expect(screen.getByText(/Count: 0/)).toBeInTheDocument();
  });

  it('increments count', async () => {
    render(Counter);
    const button = screen.getByText('+');
    await fireEvent.click(button);
    expect(screen.getByText(/Count: 1/)).toBeInTheDocument();
  });
});
```

---

## Production Checklist

- [ ] Configure adapter for deployment (`@sveltejs/adapter-vercel`, `adapter-node`, etc.)
- [ ] Enable prerendering for static pages
- [ ] Optimize images with `enhanced:img`
- [ ] Set up environment variables
- [ ] Configure CSP headers
- [ ] Run `npm run build` and test

---

## Commands

```bash
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build
npm run test         # Run tests
```

---

## Resources

- [SvelteKit Docs](https://kit.svelte.dev/)
- [Svelte 5 Runes](https://svelte.dev/blog/runes)
- [Svelte Tutorial](https://learn.svelte.dev/)
