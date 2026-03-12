# Core Frontend Patterns

## Contents

- Pattern: Next.js 16 App Router Architecture
- Pattern: Server vs Client Components
- Pattern: TypeScript Component Props
- Pattern: Data Fetching & Server Actions
- Pattern: Form Handling with React Hook Form + Zod
- Pattern: Styling with Tailwind CSS & shadcn/ui
- Pattern: State Management
- Pattern: Performance Optimization
- Pattern: Accessibility (WCAG 2.2)
- Pattern: Testing
- Pattern: Frontend Security
- Component Type Selection
- State Management Selection
- Styling Approach
- Next.js 16 Migration Checklist (Dec 2025)
- Templates
- Resources

## Pattern: Next.js 16 App Router Architecture

**Use when:** Building Next.js applications with the modern App Router.

**Modern Features (Dec 2025):**
- **Turbopack** is now the default bundler (faster builds, hot module replacement)
- **proxy.ts replaces middleware.ts** - clarifies network boundary, runs on Node.js runtime
- **Enhanced ISR/SSR/SSG** for improved performance and flexibility
- **Parallel routes** and **intercepting routes** for advanced UI patterns
- **Partial prerendering** (PPR) for mixing static and dynamic content
- **Stable caching APIs**: `cacheLife`, `cacheTag`, `updateTag` (remove `unstable_` prefix)
- **Async Request APIs**: `cookies()`, `headers()`, `params`, `searchParams` are now async

**Migration Guide**: [Next.js 16 Upgrade](https://nextjs.org/docs/app/guides/upgrading/version-16)

**Structure:**
```
app/
|-- (auth)/                 # Route group (doesn't affect URL)
|   |-- login/
|   |   `-- page.tsx
|   `-- register/
|       `-- page.tsx
|-- (dashboard)/            # Route group with layout
|   |-- layout.tsx          # Shared dashboard layout
|   |-- page.tsx            # /dashboard
|   `-- settings/
|       `-- page.tsx        # /dashboard/settings
|-- api/                    # API routes
|   `-- users/
|       `-- route.ts        # /api/users
|-- layout.tsx              # Root layout
|-- page.tsx                # Home page (/)
|-- loading.tsx             # Loading UI
|-- error.tsx               # Error UI
`-- not-found.tsx           # 404 page

src/
|-- components/
|   |-- ui/                 # shadcn/ui components
|   |-- forms/              # Form components
|   |-- layouts/            # Layout components
|   `-- shared/             # Shared components
|-- lib/
|   |-- utils.ts            # Utilities
|   |-- api.ts              # API client
|   `-- hooks/              # Custom hooks
|-- types/
|   `-- index.ts            # Type definitions
`-- styles/
    `-- globals.css         # Global styles
```

**Checklist:**
- [ ] Use App Router (not Pages Router)
- [ ] Server Components by default
- [ ] Client Components only when needed ('use client')
- [ ] Route groups for organization
- [ ] Layouts for shared UI
- [ ] Loading and error boundaries
- [ ] Metadata for SEO

---

## Pattern: Server vs Client Components

**Use when:** Deciding between Server and Client Components.

**Production Context:** React Server Components (RSC) are production-ready and the default in Next.js 16. The best practice is server-first architecture: use Server Components by default, only add 'use client' when necessary.

For comprehensive patterns on Server Components, Client Components, composition strategies, and data fetching, see:

**Reference:** `references/fullstack-patterns.md` (Server vs Client Components section)

**When to Use Server Components (Default):**
- [OK] Data fetching from databases or APIs
- [OK] Accessing backend resources directly
- [OK] Keeping sensitive information on server (API keys, tokens)
- [OK] Reducing client-side JavaScript bundle
- [OK] SEO-critical content

**When to Use Client Components ('use client'):**
- [OK] Interactivity (onClick, onChange, event handlers)
- [OK] React hooks (useState, useEffect, useContext)
- [OK] Browser APIs (localStorage, window, navigator)
- [OK] Custom hooks
- [OK] Class components (legacy)

**Quick Example - Server Component:**
```tsx
// app/posts/page.tsx
// No 'use client' - this is a Server Component
import { prisma } from '@/lib/db';

export default async function PostsPage() {
 const posts = await prisma.post.findMany();

 return (
 <div>
 {posts.map(post => (
 <PostCard key={post.id} post={post} />
 ))}
 </div>
 );
}
```

**Quick Example - Client Component:**
```tsx
// components/post-card.tsx
'use client';

import { useState } from 'react';

export function PostCard({ post }: { post: Post }) {
 const [liked, setLiked] = useState(false);

 return (
 <div onClick={() => setLiked(!liked)}>
 <h2>{post.title}</h2>
 {liked && <span>Liked</span>}
 </div>
 );
}
```

**Decision Tree:**
- **Server Component** if: Fetching data, accessing backend resources, keeping sensitive info on server
- **Client Component** if: Using React hooks (useState, useEffect), event handlers, browser APIs, interactive features

**Checklist:**
- [ ] Default to Server Components
- [ ] Add 'use client' only when necessary
- [ ] Compose Client Components in Server Components
- [ ] Pass serializable props only

---

## Pattern: TypeScript Component Props

**Use when:** Defining component prop types with modern TypeScript patterns.

**Modern TypeScript Patterns:**
- **Strict mode is non-negotiable** - TypeScript has become the industry standard
- **The `satisfies` operator** (TypeScript 4.9+) for enforcing constraints while maintaining type inference
- **Template literal types** for dynamic string-based types (e.g., className patterns)
- **Discriminated unions** for component variants and state machines
- **`unknown` over `any`** for safer type handling

For comprehensive TypeScript patterns including generic components, extending HTML elements, discriminated unions, and type inference, see:

**Reference:** `references/fullstack-patterns.md` (TypeScript Patterns section)

**Quick Example - Basic Props:**
```tsx
interface ButtonProps {
 children: React.ReactNode;
 variant?: 'primary' | 'secondary' | 'ghost';
 size?: 'sm' | 'md' | 'lg';
 disabled?: boolean;
 onClick?: () => void;
}

export function Button({
 children,
 variant = 'primary',
 size = 'md',
 disabled,
 onClick
}: ButtonProps) {
 return <button>{children}</button>;
}
```

**Quick Example - Extending HTML Elements:**
```tsx
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
 label?: string;
 error?: string;
}

export function Input({ label, error, ...props }: InputProps) {
 return (
 <div>
 {label && <label>{label}</label>}
 <input {...props} />
 {error && <span>{error}</span>}
 </div>
 );
}
```

**Checklist:**
- [ ] Use interfaces for props
- [ ] Provide default values where appropriate
- [ ] Extend HTML attributes when relevant
- [ ] Use generics for reusable components
- [ ] Export prop types for reuse

---

## Pattern: Data Fetching & Server Actions

**Use when:** Fetching data in Next.js 16.

For comprehensive data fetching patterns including Server Components, SWR/React Query, Server Actions, optimistic updates, and error handling, see:

**Reference:** `references/fullstack-patterns.md` (Data Fetching section)

**Quick Example - Server Component:**
```tsx
// app/posts/page.tsx
async function getPosts() {
 const res = await fetch('https://api.example.com/posts', {
 next: { revalidate: 3600 } // Revalidate every hour
 });
 return res.json();
}

export default async function PostsPage() {
 const posts = await getPosts();
 return <PostsList posts={posts} />;
}
```

**Quick Example - Server Actions:**
```tsx
// app/actions.ts
'use server';

export async function createPost(formData: FormData) {
 const title = formData.get('title') as string;

 await prisma.post.create({
 data: { title, content: '' }
 });

 revalidatePath('/posts');
}

// app/posts/new/page.tsx
import { createPost } from '@/app/actions';

export default function NewPostPage() {
 return (
 <form action={createPost}>
 <input name="title" required />
 <button type="submit">Create</button>
 </form>
 );
}
```

**Checklist:**
- [ ] Use Server Components for initial data
- [ ] Use SWR/React Query for client-side fetching
- [ ] Server Actions for mutations
- [ ] Implement loading states
- [ ] Handle errors gracefully
- [ ] Cache appropriately

---

## Pattern: Form Handling with React Hook Form + Zod

**Use when:** Building forms with validation.

For comprehensive form patterns including React Hook Form, Zod validation, Server Actions integration, file uploads, and multi-step forms, see:

**Reference:** `references/fullstack-patterns.md` (Forms section)

**Quick Example - React Hook Form + Zod:**
```tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const loginSchema = z.object({
 email: z.string().email('Invalid email'),
 password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginForm = z.infer<typeof loginSchema>;

export function LoginForm() {
 const {
 register,
 handleSubmit,
 formState: { errors, isSubmitting }
 } = useForm<LoginForm>({
 resolver: zodResolver(loginSchema),
 });

 const onSubmit = async (data: LoginForm) => {
 await fetch('/api/auth/login', {
 method: 'POST',
 body: JSON.stringify(data),
 });
 };

 return (
 <form onSubmit={handleSubmit(onSubmit)}>
 <div>
 <input {...register('email')} type="email" />
 {errors.email && <span>{errors.email.message}</span>}
 </div>

 <div>
 <input {...register('password')} type="password" />
 {errors.password && <span>{errors.password.message}</span>}
 </div>

 <button type="submit" disabled={isSubmitting}>
 {isSubmitting ? 'Logging in...' : 'Login'}
 </button>
 </form>
 );
}
```

**Checklist:**
- [ ] Client-side validation (Zod)
- [ ] Server-side validation (always)
- [ ] Loading states during submission
- [ ] Error display
- [ ] Accessibility (labels, ARIA)
- [ ] Type-safe form data

---

## Pattern: Styling with Tailwind CSS & shadcn/ui

**Use when:** Styling components with Tailwind and shadcn/ui.

For comprehensive styling patterns including Tailwind utilities, responsive design, dark mode, shadcn/ui customization, and animation, see:

**Reference:** `references/fullstack-patterns.md` (Styling section)

**Quick Example - Conditional Styles:**
```tsx
import { cn } from '@/lib/utils';

interface ButtonProps {
 variant?: 'primary' | 'secondary';
 size?: 'sm' | 'md' | 'lg';
}

export function Button({ variant = 'primary', size = 'md' }: ButtonProps) {
 return (
 <button
 className={cn(
 'rounded-lg font-medium transition-colors',
 variant === 'primary' && 'bg-blue-600 text-white hover:bg-blue-700',
 variant === 'secondary' && 'bg-gray-200 text-gray-900 hover:bg-gray-300',
 size === 'sm' && 'px-3 py-1.5 text-sm',
 size === 'md' && 'px-4 py-2 text-base',
 size === 'lg' && 'px-6 py-3 text-lg'
 )}
 >
 {children}
 </button>
 );
}
```

**Quick Example - shadcn/ui:**
```tsx
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';

export function MyComponent() {
 return (
 <Dialog>
 <DialogTrigger asChild>
 <Button variant="outline">Open Dialog</Button>
 </DialogTrigger>
 <DialogContent>
 <DialogHeader>
 <DialogTitle>Dialog Title</DialogTitle>
 </DialogHeader>
 <p>Dialog content</p>
 </DialogContent>
 </Dialog>
 );
}
```

**Checklist:**
- [ ] Use utility classes
- [ ] Responsive breakpoints (sm, md, lg, xl)
- [ ] Dark mode variants
- [ ] Hover/focus states
- [ ] Use cn() for conditional classes
- [ ] Install shadcn/ui components as needed

---

## Pattern: State Management

**Use when:** Managing application state in React applications.

**Modern State Management Landscape:**
- **You may not need a state management library** for most projects - React's built-in state often suffices
- **TanStack Query (React Query)** for server-state management and caching (replaces Redux in many cases)
- **Zustand** or **Recoil** for lightweight client state (Redux alternatives)
- **Built-in React state** (useState, useReducer, Context) for simple state logic
- **URL state** (useSearchParams) for shareable filters and views

For comprehensive state management patterns including local state, URL state, Zustand, React Context, and server state, see:

**Reference:** `references/fullstack-patterns.md` (State Management section)

**State Management Decision Tree:**
```
Is it server data? -> TanStack Query/SWR
Is it URL-sharable? -> useSearchParams
Is it global client state? -> Zustand/Recoil
Is it component-local? -> useState
Is it shared nearby? -> Props or Context
Is it complex state logic? -> useReducer
```

**Quick Example - URL State:**
```tsx
'use client';

import { useSearchParams, useRouter } from 'next/navigation';

export function SearchFilters() {
 const searchParams = useSearchParams();
 const router = useRouter();

 const filter = searchParams.get('filter') || 'all';

 const setFilter = (newFilter: string) => {
 const params = new URLSearchParams(searchParams);
 params.set('filter', newFilter);
 router.push(`?${params.toString()}`);
 };

 return (
 <select value={filter} onChange={(e) => setFilter(e.target.value)}>
 <option value="all">All</option>
 <option value="active">Active</option>
 </select>
 );
}
```

**Quick Example - Zustand:**
```tsx
// lib/store.ts
import { create } from 'zustand';

interface AuthStore {
 user: User | null;
 setUser: (user: User | null) => void;
 logout: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
 user: null,
 setUser: (user) => set({ user }),
 logout: () => set({ user: null }),
}));
```

**Checklist:**
- [ ] Local state for component-specific data
- [ ] URL state for shareable filters/views
- [ ] Zustand for global client state
- [ ] Context for passing server data to client
- [ ] Keep state as local as possible

---

## Pattern: Performance Optimization

**Use when:** Optimizing application performance.

**Modern Performance Features:**
- **Turbopack** - Default bundler in Next.js 16 (significantly faster than Webpack)
- **Enhanced ISR/SSR/SSG** - Improved incremental static regeneration and server-side rendering
- **React Server Components** - Reduce client-side JavaScript by default
- **Partial Prerendering (PPR)** - Mix static and dynamic content on the same page
- **Streaming with Suspense** - Progressive page rendering

For comprehensive performance patterns including Image optimization, code splitting, memoization, streaming, lazy loading, and bundle analysis, see:

**Reference:** `references/fullstack-patterns.md` (Performance section)

**Performance Checklist:**
- [ ] Use Server Components by default (reduces bundle size)
- [ ] Next.js Image component with priority for above-fold images
- [ ] Dynamic imports for heavy components
- [ ] Streaming with Suspense for gradual content loading
- [ ] Code splitting at route level (automatic with App Router)
- [ ] React.memo for expensive pure components
- [ ] useMemo/useCallback for expensive computations
- [ ] Bundle analysis (next bundle-analyzer)
- [ ] Edge deployment for global performance (Vercel Edge, Cloudflare Workers)

**Quick Example - Image Optimization:**
```tsx
import Image from 'next/image';

export function Avatar({ src }: { src: string }) {
 return (
 <Image
 src={src}
 alt="Avatar"
 width={40}
 height={40}
 className="rounded-full"
 priority // For above-the-fold images
 />
 );
}
```

**Quick Example - Code Splitting:**
```tsx
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
 loading: () => <p>Loading...</p>,
 ssr: false, // Disable server-side rendering if not needed
});

export function Page() {
 return (
 <div>
 <HeavyComponent />
 </div>
 );
}
```

**Checklist:**
- [ ] Use Next.js Image component
- [ ] Dynamic imports for heavy components
- [ ] Memoize expensive calculations
- [ ] Use React.memo for pure components
- [ ] Streaming with Suspense
- [ ] Optimize bundle size

---

## Pattern: Accessibility (WCAG 2.2)

**Use when:** Ensuring accessible UI.

For comprehensive accessibility patterns including semantic HTML, ARIA attributes, keyboard navigation, focus management, and screen reader testing, see:

**Reference:** `references/fullstack-patterns.md` (Accessibility section)

**Quick Example - Semantic HTML:**
```tsx
export function Navigation() {
 return (
 <nav aria-label="Main navigation">
 <ul>
 <li><a href="/">Home</a></li>
 <li><a href="/about">About</a></li>
 </ul>
 </nav>
 );
}
```

**Quick Example - Keyboard Navigation:**
```tsx
'use client';

export function Dropdown() {
 const [isOpen, setIsOpen] = useState(false);

 return (
 <div
 role="button"
 tabIndex={0}
 onClick={() => setIsOpen(!isOpen)}
 onKeyDown={(e) => {
 if (e.key === 'Enter' || e.key === ' ') {
 setIsOpen(!isOpen);
 }
 }}
 >
 {/* Content */}
 </div>
 );
}
```

**Checklist:**
- [ ] Semantic HTML elements
- [ ] ARIA labels and roles
- [ ] Keyboard navigation support
- [ ] Focus management
- [ ] Color contrast (WCAG AA)
- [ ] Screen reader testing
- [ ] Alt text for images

---

## Pattern: Testing

**Use when:** Writing tests for frontend code.

For comprehensive testing patterns including Vitest, Testing Library, Playwright E2E, component testing, and integration testing, see:

**Reference:** `references/fullstack-patterns.md` (Testing section)

**Quick Example - Component Test:**
```tsx
// components/button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button } from './button';

describe('Button', () => {
 it('renders children', () => {
 render(<Button>Click me</Button>);
 expect(screen.getByText('Click me')).toBeInTheDocument();
 });

 it('calls onClick when clicked', () => {
 const onClick = vi.fn();
 render(<Button onClick={onClick}>Click</Button>);
 fireEvent.click(screen.getByText('Click'));
 expect(onClick).toHaveBeenCalledOnce();
 });
});
```

**Checklist:**
- [ ] Unit tests for utilities
- [ ] Component tests for UI
- [ ] E2E tests for critical flows
- [ ] Mock API calls
- [ ] Test accessibility
- [ ] 80%+ coverage for critical paths

---

## Pattern: Frontend Security

**Use when:** Building secure frontend applications.

**IMPORTANT:** For comprehensive security patterns, see the **software-security-patterns** skill which covers:
- XSS (Cross-Site Scripting) prevention and output encoding
- CSRF (Cross-Site Request Forgery) protection
- Content Security Policy (CSP) configuration
- Authentication & Authorization patterns
- Input validation and sanitization
- Secure data handling and storage

**Frontend-Specific Security:**
- **XSS Prevention**: React automatically escapes output, but be careful with `dangerouslySetInnerHTML`
- **CSP Headers**: Configure in Next.js config or middleware
- **Sanitize User Input**: Use DOMPurify for rich text, validate with Zod
- **Secure Storage**: Never store sensitive data in localStorage; use httpOnly cookies
- **HTTPS Only**: Enforce in production, use secure cookies
- **Dependency Scanning**: Regular `npm audit` and automated updates

**Quick Example - CSP in Next.js:**
```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY'
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  }
];

module.exports = {
  async headers() {
    return [{
      source: '/:path*',
      headers: securityHeaders,
    }];
  },
};
```

**Checklist:**
- [ ] CSP headers configured
- [ ] All user input sanitized
- [ ] No sensitive data in client-side storage
- [ ] HTTPS enforced in production
- [ ] Dependencies regularly scanned
- [ ] Authentication tokens in httpOnly cookies

---

# Quick Decision Tables

## Component Type Selection

| Need | Use |
|------|-----|
| Fetch data | Server Component |
| Interactivity (onClick, etc.) | Client Component |
| React hooks | Client Component |
| Browser APIs | Client Component |
| SEO-critical content | Server Component |
| Static content | Server Component |

---

## State Management Selection

| Scope | Solution |
|-------|----------|
| Single component | useState |
| Parent-child | Props |
| Nearby components | Context |
| Global (client) | Zustand |
| URL-based | useSearchParams |
| Server data | Server Component props |

---

## Styling Approach

| Use Case | Solution |
|----------|----------|
| Simple utility styling | Tailwind CSS |
| Conditional classes | cn() utility |
| Complex components | shadcn/ui |
| Animations | Tailwind transitions / Framer Motion |
| Dark mode | Tailwind dark: variants |

---

# Templates

Production-ready starter templates organized by framework:

**React-based Frameworks:**
- `assets/nextjs/template-nextjs-tailwind-shadcn.md` - Next.js 16 + App Router + Turbopack + shadcn/ui
- `assets/remix/template-remix-react.md` - Remix with loaders/actions + Prisma
- `assets/vite-react/template-vite-react-ts.md` - Vite + React 19 + TanStack Query

**Vue Ecosystem:**
- `assets/vue-nuxt/template-nuxt4-tailwind.md` - Nuxt 4 + Vue 3 + Nitro + Pinia

**Angular:**
- `assets/angular/template-angular21-standalone.md` - Angular 21 + Standalone Components + Signals

**Svelte:**
- `assets/svelte/template-sveltekit-runes.md` - SvelteKit + Svelte 5 Runes + Progressive Enhancement

Each template includes: project setup, structure, configuration files, common patterns, testing setup, and production checklist.

---

# Resources

**Framework-Specific Best Practices** (`references/`)
- `fullstack-patterns.md` - Universal patterns for all frameworks (Next.js focus):
  - Server vs Client Components, TypeScript patterns, data fetching, forms, styling, state management, performance, accessibility, testing

- `vue-nuxt-patterns.md` - Vue 3 + Nuxt 4 patterns:
  - Composition API, script setup, composables, useAsyncData vs useFetch, Pinia stores, auto-imports, SSR/SSG

- `angular-patterns.md` - Angular 21 patterns:
  - Standalone components, signals (signal, computed, effect), inject() function, reactive forms, OnPush, RxJS

- `svelte-sveltekit-patterns.md` - Svelte 5 + SvelteKit patterns:
  - Runes ($state, $derived, $effect, $props), load functions, form actions, progressive enhancement, snippets

- `remix-react-patterns.md` - Remix patterns:
  - Loaders vs actions, Form component, optimistic UI, sessions, error boundaries, defer for slow data

- `vite-react-patterns.md` - Vite + React patterns:
  - Vite configuration, React hooks, custom hooks, TanStack Query, React Router, lazy loading

**External Documentation:**
See [data/sources.json](../data/sources.json) for 110+ curated resources covering all frameworks (Next.js, Vue/Nuxt, Angular, Svelte, Remix, Vite).

---

## Next.js 16 Migration Checklist (Dec 2025)

**Breaking Changes Summary:**

| Change | Before (v15) | After (v16) | Action |
| ------ | ------------ | ----------- | ------ |
| Request Proxy | `middleware.ts` | `proxy.ts` | Rename file + function |
| Config Option | `skipMiddlewareUrlNormalize` | `skipProxyUrlNormalize` | Update next.config |
| Bundler | `--turbopack` flag | Default (no flag) | Remove flags from scripts |
| Request APIs | Sync | Async | Add `await` to cookies/headers/params |
| Parallel Routes | Implicit defaults | Explicit `default.js` | Add default.js to slots |
| Image `domains` | Supported | Deprecated | Use `remotePatterns` |
| Caching APIs | `unstable_` prefix | Stable | Remove prefix |

**Migration Commands:**

```bash
# Recommended: Run the codemod
npx @next/codemod@canary upgrade latest

# Manual: Rename middleware to proxy
mv middleware.ts proxy.ts

# Update package.json scripts (remove --turbopack flags)
# Before: "dev": "next dev --turbopack"
# After:  "dev": "next dev"
```

**Async Request APIs Migration:**

```typescript
// Before (Next.js 15)
export default function Page({ params }) {
  const slug = params.slug;
  return <div>{slug}</div>;
}

// After (Next.js 16)
export default async function Page(props) {
  const { slug } = await props.params;
  return <div>{slug}</div>;
}

// cookies() and headers() also require await
import { cookies, headers } from 'next/headers';

// Before
const cookieStore = cookies();
const headersList = headers();

// After
const cookieStore = await cookies();
const headersList = await headers();
```

**proxy.ts vs middleware.ts:**

```typescript
// proxy.ts - New convention (Node.js runtime)
export function proxy(request: NextRequest) {
  // Auth, rewrites, redirects
  return NextResponse.next();
}

// middleware.ts - Keep using if you need Edge Runtime
export function middleware(request: NextRequest) {
  // Edge-first logic
  return NextResponse.next();
}
export const config = { runtime: 'edge' };
```

**Image Configuration Update:**

```typescript
// next.config.ts
const nextConfig: NextConfig = {
  images: {
    // DEPRECATED - remove 'domains'
    // domains: ['example.com'],

    // USE INSTEAD
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'example.com',
        pathname: '/images/**',
      },
    ],
    // New defaults in v16
    minimumCacheTTL: 14400, // Changed from 60s to 4 hours
    qualities: [75], // Changed from all qualities
  },
};
```

**Parallel Routes - Add default.js:**

```tsx
// app/@modal/default.tsx
import { notFound } from 'next/navigation';

export default function Default() {
  notFound(); // or return null
}
```

**New Caching APIs (stable):**

```typescript
// Remove 'unstable_' prefix
import { cacheLife, cacheTag, updateTag, refresh } from 'next/cache';

// revalidateTag with cache profiles
revalidateTag('article-123', 'max');

// updateTag for read-your-writes consistency
await updateTag('user-profile');

// refresh() to immediately refresh client router
refresh();
```

---

# END
```
