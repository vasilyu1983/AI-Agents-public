# Remix / React Router v7 Best Practices & Patterns

Operational patterns for building full-stack React applications with Remix v2 and React Router v7. Covers the migration path from Remix to React Router, Vite integration, streaming, SPA mode, and production-ready patterns.

---

## Section Index

| Section | Lines | Use when |
|---------|-------|----------|
| Remix v2 vs React Router v7 | 30–78 | Transition, imports, choosing starting point |
| Vite Configuration | 79–139 | Setting up or migrating build tooling |
| Loader & Action Patterns | 140–236 | Server-side data fetching and mutations |
| clientLoader & clientAction | 237–318 | Client-side data, cache-first, offline |
| Form Patterns & Optimistic UI | 319–396 | Forms, progressive enhancement |
| Streaming & Deferred Data | 397–422 | Slow data sources, non-blocking rendering |
| Revalidation Control | 423–490 | Cache control, reducing refetches |
| Nested Routes & Layouts | 491–538 | Route hierarchy, shared layouts |
| SPA Mode | 539–571 | Deploying without a server |
| Resource Routes | 572–600 | API endpoints, file downloads, webhooks |
| Session & Auth Patterns | 601–637 | Cookie sessions, auth guards |
| Error Handling | 638–673 | Error boundaries |
| Performance Patterns | 674–703 | Prefetching, single fetch, code splitting |
| Testing Patterns | 704–752 | Loader/action unit tests |
| Anti-Patterns | 753–842 | Common mistakes with WHY |
| Decision Frameworks | 843–893 | When to use which pattern |

---

## Remix v2 vs React Router v7

### The Merger

Remix is merging into React Router. React Router v7 is effectively "Remix v3" — same team, same architecture, new package name. Understanding this is critical for import paths, documentation lookups, and long-term maintenance.

| Aspect | Remix v2 | React Router v7 |
|--------|----------|-----------------|
| Package | `@remix-run/node`, `@remix-run/react` | `react-router` (unified package) |
| Build tool | Remix compiler or Vite plugin | Vite plugin (only option) |
| Config file | `remix.config.js` or `vite.config.ts` | `vite.config.ts` with `reactRouter()` plugin |
| Route config | File-based (v2 flat routes) | File-based or `routes.ts` config |
| `json()` helper | Required for typed responses | Optional — return plain objects (single fetch) |
| Server runtime | `@remix-run/node`, `@remix-run/cloudflare` | `react-router` (adapters still exist) |
| Status | Maintenance mode | Active development |

### Import Migration Map

```typescript
// Remix v2 imports
import { json, redirect, defer } from '@remix-run/node';
import { useLoaderData, Form, useFetcher } from '@remix-run/react';
import type { LoaderFunctionArgs, ActionFunctionArgs } from '@remix-run/node';

// React Router v7 equivalents
import { redirect, data } from 'react-router';
import { useLoaderData, Form, useFetcher } from 'react-router';
import type { Route } from './+types/my-route';
// Note: json() is replaced by plain returns or data() for status/headers.
// defer() is replaced by returning promises directly (single fetch).
```

### When to Start New Projects

```text
New project in 2026?
  |
  +-- Use React Router v7 from the start
  |   - Vite-native, actively maintained
  |   - All new features land here
  |
  +-- Existing Remix v2 app?
      +-- Small/medium app -> migrate to RR7 (incremental, low risk)
      +-- Large app with custom compiler plugins -> plan migration, no rush
      +-- Remix v2 is stable and receives security patches
```

---

## Vite Configuration

### React Router v7 (New Projects)

```typescript
// vite.config.ts
import { reactRouter } from '@react-router/dev/vite';
import { defineConfig } from 'vite';
import tsconfigPaths from 'vite-tsconfig-paths';

export default defineConfig({
  plugins: [reactRouter(), tsconfigPaths()],
});
```

```typescript
// react-router.config.ts
import type { Config } from '@react-router/dev/config';

export default {
  ssr: true, // false for SPA mode
  async prerender() { return ['/', '/about', '/pricing']; },
} satisfies Config;
```

### Remix v2 with Vite (Migration Path)

```typescript
import { vitePlugin as remix } from '@remix-run/dev';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [
    remix({
      future: {
        v3_fetcherPersist: true, v3_relativeSplatPath: true,
        v3_throwAbortReason: true, v3_lazyRouteDiscovery: true,
        v3_singleFetch: true, // Opt into RR7 behaviors incrementally
      },
    }),
  ],
});
```

Environment variables: server-side uses `process.env.DATABASE_URL` (never exposed). Client-side uses `import.meta.env.VITE_PUBLIC_API_URL` (VITE_ prefix = public).

---

## Loader & Action Patterns

### Basic Loader (React Router v7)

```typescript
// app/routes/blog.$slug.tsx
import type { Route } from './+types/blog.$slug';
import { data } from 'react-router';

export async function loader({ params }: Route.LoaderArgs) {
  const post = await db.post.findUnique({ where: { slug: params.slug } });
  if (!post) throw data({ message: 'Post not found' }, { status: 404 });
  return { post }; // No json() needed — single fetch handles serialization
}

export default function BlogPost({ loaderData }: Route.ComponentProps) {
  return (
    <article>
      <h1>{loaderData.post.title}</h1>
      <div dangerouslySetInnerHTML={{ __html: loaderData.post.content }} />
    </article>
  );
}
```

### Parallel Data Loading

Use `Promise.all` for independent queries in a single loader. Await auth first (sequential dependency), then fire post + comments + recommendations in parallel.

### Action with Validation

```typescript
import { redirect, data } from 'react-router';
import { z } from 'zod';

const createPostSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  content: z.string().min(10, 'Content must be at least 10 characters'),
  categoryId: z.string().uuid(),
});

export async function action({ request }: Route.ActionArgs) {
  const user = await requireAuth(request);
  const formData = await request.formData();
  const result = createPostSchema.safeParse({
    title: formData.get('title'), content: formData.get('content'),
    categoryId: formData.get('categoryId'),
  });
  if (!result.success) {
    return data({ errors: result.error.flatten().fieldErrors }, { status: 400 });
  }
  const post = await db.post.create({ data: { ...result.data, authorId: user.id } });
  return redirect(`/blog/${post.slug}`);
}
```

### Multiple Actions (Intent Pattern)

```typescript
export async function action({ request }: Route.ActionArgs) {
  const formData = await request.formData();
  switch (formData.get('intent')) {
    case 'publish': return publishPost(formData);
    case 'draft':   return saveDraft(formData);
    case 'delete':  return deletePost(formData);
    default: throw data({ message: 'Unknown intent' }, { status: 400 });
  }
}
```

---

## clientLoader & clientAction

`clientLoader` and `clientAction` run in the browser. They enable cache-first strategies, reading from localStorage/IndexedDB, and combining server + client data without a full server round-trip.

### When to Use

| Pattern | Use `loader` (server) | Use `clientLoader` |
|---------|----------------------|-------------------|
| Database queries | Yes | No |
| Secrets / auth checks | Yes | No |
| Cache-first with fallback | Server as fallback | Client checks cache first |
| LocalStorage / IndexedDB reads | No | Yes |
| Combining server data + client data | Returns server portion | Merges both |
| Offline-capable routes | No | Yes |

### Cache-First Pattern

```typescript
// Server loader — fallback when cache misses
export async function loader({ params }: Route.LoaderArgs) {
  const product = await db.product.findUnique({ where: { id: params.id } });
  if (!product) throw data({ message: 'Not found' }, { status: 404 });
  return { product };
}

// Client loader — checks localStorage before calling server
export async function clientLoader({ params, serverLoader }: Route.ClientLoaderArgs) {
  const cached = localStorage.getItem(`product-${params.id}`);
  if (cached) {
    const parsed = JSON.parse(cached);
    if (Date.now() - parsed.cachedAt < 5 * 60 * 1000) return { product: parsed.data };
  }
  const serverData = await serverLoader();
  localStorage.setItem(`product-${params.id}`,
    JSON.stringify({ data: serverData.product, cachedAt: Date.now() }));
  return serverData;
}

clientLoader.hydrate = true as const; // Run before component renders
```

### clientAction for Optimistic Writes

`clientAction` receives `serverAction` as a callback. Pattern: update local cache optimistically, call `await serverAction()`, rollback on failure with try/catch.

### Client-Only Data (No Server Loader)

For routes reading only from browser storage, export only `clientLoader` (no server loader). Set `clientLoader.hydrate = true` and export a `HydrateFallback` component for the loading state. The route is entirely client-side — no server round-trip.

---

## Form Patterns & Optimistic UI

### Form with Validation Feedback

```tsx
import { Form, useNavigation } from 'react-router';

export default function CreatePost({ actionData }: Route.ComponentProps) {
  const isSubmitting = useNavigation().state === 'submitting';
  return (
    <Form method="post">
      <fieldset disabled={isSubmitting}>
        <label htmlFor="title">Title</label>
        <input id="title" name="title" type="text" required />
        {actionData?.errors?.title && (
          <p className="error" role="alert">{actionData.errors.title[0]}</p>
        )}
        <label htmlFor="content">Content</label>
        <textarea id="content" name="content" rows={10} required />
        {actionData?.errors?.content && (
          <p className="error" role="alert">{actionData.errors.content[0]}</p>
        )}
        <button type="submit">{isSubmitting ? 'Creating...' : 'Create Post'}</button>
      </fieldset>
    </Form>
  );
}
```

### Optimistic UI with useFetcher

```tsx
import { useFetcher } from 'react-router';

function TodoItem({ todo }: { todo: Todo }) {
  const fetcher = useFetcher();
  const isToggling = fetcher.formData?.get('intent') === 'toggle';
  const optimisticDone = isToggling ? !todo.done : todo.done;
  if (fetcher.formData?.get('intent') === 'delete') return null; // Optimistic removal

  return (
    <li className={optimisticDone ? 'completed' : ''}>
      <span>{todo.text}</span>
      <fetcher.Form method="post" action="/todos">
        <input type="hidden" name="intent" value="toggle" />
        <input type="hidden" name="todoId" value={todo.id} />
        <button type="submit">{optimisticDone ? 'Undo' : 'Complete'}</button>
      </fetcher.Form>
    </li>
  );
}
```

Give each list item its own `useFetcher()` — toggling one item doesn't block others.

---

## Streaming & Deferred Data

### Returning Promises (React Router v7 / Single Fetch)

With single fetch, return promises directly — no `defer()` needed. Await critical data, return un-awaited promises for non-critical data:

```typescript
export async function loader({ request }: Route.LoaderArgs) {
  const user = await requireAuth(request);
  const profile = await db.user.findUnique({ where: { id: user.id } });
  return {
    profile,                                               // Renders immediately
    recentActivity: db.activity.findMany({ where: { userId: user.id }, take: 20 }),  // Streams in
    recommendations: recommendationService.getForUser(user.id),                      // Streams in
  };
}
```

In the component, wrap streamed data in `<Suspense fallback={<Skeleton />}><Await resolve={loaderData.field}>{(data) => <Component data={data} />}</Await></Suspense>`.

**Remix v2 legacy**: Use `defer()` from `@remix-run/node` and don't await slow promises. In RR7, just return promises directly — no `defer()` needed.

**Error handling in streams**: Pass `errorElement` prop to `<Await>` to render a graceful fallback instead of breaking the page when a streamed promise rejects.

---

## Revalidation Control

### shouldRevalidate

By default, all active loaders revalidate after every action and navigation. `shouldRevalidate` opts out when data hasn't changed.

```typescript
export function shouldRevalidate({
  currentUrl, nextUrl, formAction, formMethod, defaultShouldRevalidate,
}: ShouldRevalidateFunctionArgs) {
  if (nextUrl.pathname.startsWith('/blog')) return false; // Skip for blog nav
  if (formMethod === 'POST' && formAction === '/settings') return true;
  return defaultShouldRevalidate;
}

// Static data — never revalidate after initial load
export function shouldRevalidate() { return false; }
```

Strategies: (1) `return false` for static data (site config, translations), (2) compare `searchParams` for pagination-only revalidation, (3) fall through to `defaultShouldRevalidate`.

### useRevalidator

Trigger manual revalidation from anywhere — useful for polling, websocket events, or after non-form mutations.

```tsx
import { useRevalidator } from 'react-router';

function LiveDashboard() {
  const revalidator = useRevalidator();
  useEffect(() => {
    const interval = setInterval(() => {
      if (revalidator.state === 'idle') revalidator.revalidate();
    }, 30_000);
    return () => clearInterval(interval);
  }, [revalidator]);

  return (
    <div>
      <DashboardContent />
      {revalidator.state === 'loading' && <span>Syncing...</span>}
    </div>
  );
}
```

For WebSockets, call `revalidator.revalidate()` on incoming messages instead of polling.

---

## Nested Routes & Layouts

### File-Based Route Structure

```text
app/routes/
+-- _index.tsx                    # /
+-- _auth.tsx                     # Layout for auth pages (no URL segment)
+-- _auth.login.tsx               # /login
+-- _auth.register.tsx            # /register
+-- dashboard.tsx                 # /dashboard (layout with <Outlet />)
+-- dashboard._index.tsx          # /dashboard (index content)
+-- dashboard.settings.tsx        # /dashboard/settings
+-- dashboard.projects.tsx        # /dashboard/projects (layout)
+-- dashboard.projects._index.tsx # /dashboard/projects
+-- dashboard.projects.$id.tsx    # /dashboard/projects/:id
+-- blog.$slug.tsx                # /blog/:slug (no parent layout)
```

### Layout Route with Outlet

```tsx
import { Outlet, NavLink } from 'react-router';

export default function DashboardLayout() {
  return (
    <div className="dashboard">
      <nav>
        <NavLink to="/dashboard" end>Overview</NavLink>
        <NavLink to="/dashboard/projects">Projects</NavLink>
        <NavLink to="/dashboard/settings">Settings</NavLink>
      </nav>
      <main><Outlet /></main>
    </div>
  );
}
```

### Route Config (React Router v7 Alternative)

RR7 supports `app/routes.ts` with `route()`, `layout()`, `index()` from `@react-router/dev/routes`. Useful for programmatic routing or when file-based conventions don't fit.

---

## SPA Mode

SPA mode generates a static `index.html` at build time with no server runtime. Use it when deploying to static hosting (GitHub Pages, S3, Netlify) or when SSR is unnecessary.

Set `ssr: false` in `react-router.config.ts`.

| Feature | SSR mode | SPA mode |
|---------|----------|----------|
| Server `loader`/`action` | Available | Not available |
| `clientLoader`/`clientAction` | Optional | Required for data/mutations |
| Initial HTML | Server-rendered | Static shell |
| SEO | Full SSR | Requires prerendering |
| Hosting | Node/edge server | Any static host |

In SPA mode, all data fetching uses `clientLoader`. Set `clientLoader.hydrate = true` and export `HydrateFallback`.

**SPA** = admin panels, internal tools, static hosting, no SEO. **SSR** = SEO, fast first paint, server-side auth, unified deploy.

---

## Resource Routes

Resource routes have no default component — JSON APIs, file downloads, webhooks. Export only `loader`/`action`.

```typescript
// app/routes/api.posts.ts
export async function loader({ request }: Route.LoaderArgs) {
  const url = new URL(request.url);
  const page = Number(url.searchParams.get('page')) || 1;
  const [posts, total] = await Promise.all([
    db.post.findMany({ skip: (page - 1) * 20, take: 20 }),
    db.post.count(),
  ]);
  return { posts, page, total };
}
// File downloads: return new Response(csv, { headers: { 'Content-Type': 'text/csv' } })
// Webhooks: export action, read request.text(), verify signature
```

---

## Session & Auth Patterns

```typescript
// app/utils/session.server.ts
import { createCookieSessionStorage, redirect } from 'react-router';

const sessionStorage = createCookieSessionStorage({
  cookie: {
    name: '__session',
    secure: process.env.NODE_ENV === 'production',
    secrets: [process.env.SESSION_SECRET!],
    sameSite: 'lax', path: '/', maxAge: 60 * 60 * 24 * 7, httpOnly: true,
  },
});

export async function requireAuth(request: Request) {
  const session = await sessionStorage.getSession(request.headers.get('Cookie'));
  const userId = session.get('userId');
  if (!userId) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirectTo', new URL(request.url).pathname);
    throw redirect(loginUrl.toString());
  }
  return db.user.findUniqueOrThrow({ where: { id: userId } });
}

export async function createUserSession(userId: string, redirectTo: string) {
  const session = await sessionStorage.getSession();
  session.set('userId', userId);
  return redirect(redirectTo, {
    headers: { 'Set-Cookie': await sessionStorage.commitSession(session) },
  });
}
```

---

## Error Handling

### Route-Level Error Boundary

```tsx
import { isRouteErrorResponse, useRouteError } from 'react-router';

export function ErrorBoundary() {
  const error = useRouteError();
  if (isRouteErrorResponse(error)) {
    return (
      <div className="error-page">
        <h1>{error.status}</h1>
        <p>{error.data?.message || error.statusText}</p>
      </div>
    );
  }
  console.error('Unexpected error:', error);
  return <div className="error-page"><h1>Something went wrong</h1></div>;
}
```

**Expected errors** (404, 403, 400): `throw data({ message }, { status: 404 })` — user-facing. **Unexpected errors** (DB failures, bugs): log for debugging, never expose stack traces.

---

## Performance Patterns

### Link Prefetching

```tsx
<Link to="/post" prefetch="intent">Read</Link>   {/* On hover — good default */}
<Link to="/dash" prefetch="render">Dash</Link>    {/* On render — high priority */}
<Link to="/item" prefetch="viewport">Item</Link>  {/* When visible — link-heavy pages */}
<Link to="/terms" prefetch="none">Terms</Link>    {/* Rarely clicked */}
```

### Single Fetch (React Router v7)

Default in RR7: batches all active loader calls into one HTTP request (`GET /dashboard.data`) during client-side navigations. Use `shouldRevalidate` to exclude unchanged loaders from the batch.

### Code Splitting

Routes are automatically code-split — each route module loads only when navigated to. For non-route code, use `await import('heavy-library')` inside handlers.

---

## Testing Patterns

### Loader Unit Test

```typescript
import { describe, it, expect, vi } from 'vitest';
import { loader } from './blog.$slug';

describe('blog post loader', () => {
  it('returns post for valid slug', async () => {
    vi.mocked(db.post.findUnique).mockResolvedValue(
      { id: '1', slug: 'hello', title: 'Hello', content: '<p>Hi</p>' });
    const result = await loader({
      request: new Request('http://localhost/blog/hello'),
      params: { slug: 'hello' }, context: {},
    });
    expect(result.post.title).toBe('Hello');
  });

  it('throws 404 for unknown slug', async () => {
    vi.mocked(db.post.findUnique).mockResolvedValue(null);
    await expect(
      loader({ request: new Request('http://localhost/blog/x'), params: { slug: 'x' }, context: {} })
    ).rejects.toMatchObject({ status: 404 });
  });
});
```

**Action tests**: Same pattern — build `FormData`, create `Request` with `method: 'POST'`, call `action({ request, params, context })`. Assert redirect (302) for success, 400 for validation failures.

**Integration tests**: Use `createRoutesStub` from `react-router` with a mock loader and `initialEntries` to render the full loader-to-component pipeline.

---

## Anti-Patterns

### 1. Fetching Data in useEffect Instead of Loaders

```typescript
// BAD
function ProductPage() {
  const [product, setProduct] = useState(null);
  useEffect(() => {
    fetch(`/api/products/${id}`).then(r => r.json()).then(setProduct);
  }, [id]);
}
```

**Why this is wrong:** You lose server rendering, streaming, parallel data loading, automatic revalidation after mutations, and error boundaries. The component renders empty on first paint, then fetches — a waterfall. Loaders run before the component mounts and integrate with the router's data lifecycle.

### 2. Using useState for Server-Fetched Data

```typescript
// BAD
export default function Dashboard({ loaderData }) {
  const [posts, setPosts] = useState(loaderData.posts);
  // Now you have TWO copies of the data — loaderData and posts state
}
```

**Why this is wrong:** You create a divergent copy that won't update when the router revalidates. After a mutation, `loaderData.posts` updates but `posts` state stays stale. Use `loaderData` directly — it's already reactive.

### 3. Calling json() in React Router v7 with Single Fetch

```typescript
// UNNECESSARY in React Router v7
return json({ post }); // Works but adds overhead

// CORRECT — plain return
return { post }; // Single fetch serializes this automatically
```

**Why:** `json()` serializes to JSON and sets headers. With single fetch, the framework uses turbo-stream encoding which supports Date, Set, Map, and other types that JSON cannot represent. Using `json()` forces JSON serialization and loses these benefits. Use `data()` only when you need to set status codes or custom headers.

### 4. Sequential Loader Waterfall

```typescript
// BAD — posts and comments wait for each other
const posts = await getPosts(user.id);
const comments = await getComments(user.id);

// CORRECT — parallel + streaming
return { user, posts: getPosts(user.id), comments: getComments(user.id) };
```

**Why:** Independent queries should use `Promise.all`. Non-critical data should be returned as unwrapped promises for streaming.

### 5. Skipping shouldRevalidate on Static Data

**Why this is wrong:** Without `shouldRevalidate`, every navigation re-fetches all active loaders — even rarely-changing data (site config, translations). Export `shouldRevalidate() { return false; }` for static root loaders.

### 6. Using window.location for Navigation

```typescript
window.location.href = '/dashboard'; // BAD — full reload, destroys state
navigate('/dashboard');               // CORRECT — client-side transition
```

**Why:** `window.location` destroys React trees, cached data, and client state. Use `useNavigate()` in components or `throw redirect()` from loaders/actions.

---

## Decision Frameworks

### Loader vs clientLoader

```text
Where should this data come from?
  |
  +-- Database, secrets, or auth-gated?
  |   -> Server loader (secure, no client exposure)
  |
  +-- Browser storage (localStorage, IndexedDB)?
  |   -> clientLoader only
  |
  +-- External API that the client can call directly?
  |   +-- Needs caching/offline? -> clientLoader with cache-first
  |   +-- No caching needed? -> Server loader (hides API keys, reduces CORS)
  |
  +-- Combination of server + client data?
      -> Both: clientLoader calls serverLoader() then merges local data
```

### SSR vs SPA vs Prerendering

| Criterion | SSR | SPA Mode | Prerendering |
|-----------|-----|----------|-------------|
| SEO | Full support | Limited | Full support |
| First paint | Fast (streamed HTML) | Slower (JS must load) | Fastest (static HTML) |
| Dynamic content | Yes | Yes | Build-time only |
| Hosting | Node/edge server | Any static host | Any static host |
| Auth-gated content | Server-side checks | Client-side checks | Not suitable |
| Use case | Marketing, e-commerce, blogs | Admin panels, dashboards | Docs, landing pages |

### When to Use Form vs useFetcher

| Scenario | Use `<Form>` | Use `useFetcher` |
|----------|-------------|-----------------|
| Full-page form submission | Yes | No |
| Navigation after submit (redirect) | Yes | Possible but not typical |
| Inline edit (no navigation) | No | Yes |
| Multiple independent mutations on one page | No | Yes (one fetcher per item) |
| File upload with progress | Either | Either |
| Optimistic UI on list items | No | Yes |

---

## Cross-References

- [state-management-patterns.md](state-management-patterns.md) -- Client state solutions alongside Remix server state
- [fullstack-patterns.md](fullstack-patterns.md) -- Server/client component architecture
- [performance-optimization.md](performance-optimization.md) -- General frontend performance techniques
- [testing-frontend-patterns.md](testing-frontend-patterns.md) -- Testing strategies and tooling
