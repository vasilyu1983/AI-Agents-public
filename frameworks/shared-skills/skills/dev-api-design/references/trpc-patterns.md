# tRPC Patterns

TypeScript-first RPC framework for end-to-end type safety without code generation.

---

## When to Use tRPC

### Decision Matrix

| Factor | Choose tRPC | Choose REST/GraphQL |
|--------|-------------|---------------------|
| **Stack** | TypeScript monorepo (frontend + backend) | Multi-language, polyglot teams |
| **Audience** | Internal tools, same-team consumption | Public APIs, third-party developers |
| **Type Safety** | End-to-end required, zero runtime errors | Schema-first is sufficient |
| **Bundle Size** | Performance critical (~3.5x smaller than GraphQL client) | Bundle size less critical |
| **Learning Curve** | Team knows TypeScript well | Team prefers REST conventions |
| **Multi-source** | Single data source | Multiple services to aggregate |

### tRPC Excels For

- Internal dashboards and admin panels
- TypeScript monorepos (Next.js, T3 Stack)
- Prototyping with fast iteration
- Teams wanting zero code generation
- Applications where type safety prevents bugs

### tRPC Not Recommended For

- Public APIs requiring broad language support
- Teams with non-TypeScript backends (Go, Python, Java)
- Complex multi-source data aggregation (use GraphQL)
- APIs requiring REST caching semantics

---

## Core Patterns

### Basic Router Setup

```typescript
// server/trpc.ts
import { initTRPC, TRPCError } from '@trpc/server';
import { z } from 'zod';

const t = initTRPC.context<Context>().create();

export const router = t.router;
export const publicProcedure = t.procedure;
export const protectedProcedure = t.procedure.use(authMiddleware);
```

### Procedure Types

```typescript
// server/routers/user.ts
import { router, publicProcedure, protectedProcedure } from '../trpc';
import { z } from 'zod';

export const userRouter = router({
  // Query (GET-like, idempotent)
  getById: publicProcedure
    .input(z.object({ id: z.string().uuid() }))
    .query(async ({ input, ctx }) => {
      return ctx.db.user.findUnique({ where: { id: input.id } });
    }),

  // Mutation (POST/PUT/DELETE-like, side effects)
  create: protectedProcedure
    .input(z.object({
      name: z.string().min(1).max(100),
      email: z.string().email(),
    }))
    .mutation(async ({ input, ctx }) => {
      return ctx.db.user.create({ data: input });
    }),

  // Subscription (WebSocket, real-time)
  onUpdate: protectedProcedure
    .input(z.object({ userId: z.string().uuid() }))
    .subscription(({ input }) => {
      return observable<User>((emit) => {
        const unsubscribe = subscribeToUserUpdates(input.userId, emit.next);
        return unsubscribe;
      });
    }),
});
```

### Input Validation with Zod

```typescript
// Reusable schemas
const paginationSchema = z.object({
  cursor: z.string().optional(),
  limit: z.number().min(1).max(100).default(20),
});

const userFilterSchema = z.object({
  status: z.enum(['active', 'inactive', 'pending']).optional(),
  role: z.enum(['admin', 'user', 'guest']).optional(),
});

// Use in procedure
list: publicProcedure
  .input(paginationSchema.merge(userFilterSchema))
  .query(async ({ input }) => {
    const { cursor, limit, status, role } = input;
    // Type-safe: input.status is 'active' | 'inactive' | 'pending' | undefined
  }),
```

---

## Authentication & Authorization

### Context with Auth

```typescript
// server/context.ts
import { inferAsyncReturnType } from '@trpc/server';
import { CreateNextContextOptions } from '@trpc/server/adapters/next';

export async function createContext({ req }: CreateNextContextOptions) {
  const session = await getSession(req);

  return {
    db: prisma,
    session,
    user: session?.user ?? null,
  };
}

export type Context = inferAsyncReturnType<typeof createContext>;
```

### Auth Middleware

```typescript
// server/middleware/auth.ts
import { TRPCError } from '@trpc/server';

export const authMiddleware = t.middleware(async ({ ctx, next }) => {
  if (!ctx.user) {
    throw new TRPCError({
      code: 'UNAUTHORIZED',
      message: 'You must be logged in',
    });
  }

  return next({
    ctx: {
      ...ctx,
      user: ctx.user, // Now non-null
    },
  });
});

// Role-based middleware
export const adminMiddleware = t.middleware(async ({ ctx, next }) => {
  if (ctx.user?.role !== 'admin') {
    throw new TRPCError({
      code: 'FORBIDDEN',
      message: 'Admin access required',
    });
  }
  return next({ ctx });
});

// Usage
export const adminProcedure = t.procedure
  .use(authMiddleware)
  .use(adminMiddleware);
```

---

## Error Handling

### tRPC Error Codes

| Code | HTTP Equivalent | Use When |
|------|-----------------|----------|
| `BAD_REQUEST` | 400 | Invalid input |
| `UNAUTHORIZED` | 401 | Not authenticated |
| `FORBIDDEN` | 403 | Authenticated but not allowed |
| `NOT_FOUND` | 404 | Resource doesn't exist |
| `CONFLICT` | 409 | Duplicate/conflict |
| `PRECONDITION_FAILED` | 412 | State mismatch |
| `TOO_MANY_REQUESTS` | 429 | Rate limited |
| `INTERNAL_SERVER_ERROR` | 500 | Server error |

### Structured Errors

```typescript
// Throw with additional data
throw new TRPCError({
  code: 'BAD_REQUEST',
  message: 'Validation failed',
  cause: {
    field: 'email',
    issue: 'already_exists',
  },
});

// Error handler in client
const utils = trpc.useUtils();

const createUser = trpc.user.create.useMutation({
  onError: (error) => {
    if (error.data?.code === 'BAD_REQUEST') {
      const cause = error.cause as { field: string; issue: string };
      setFieldError(cause.field, cause.issue);
    }
  },
});
```

---

## Client Usage (React)

### Provider Setup

```typescript
// app/providers.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { httpBatchLink } from '@trpc/client';
import { trpc } from './trpc';

const queryClient = new QueryClient();
const trpcClient = trpc.createClient({
  links: [
    httpBatchLink({
      url: '/api/trpc',
      headers: () => ({
        authorization: getAuthToken(),
      }),
    }),
  ],
});

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <trpc.Provider client={trpcClient} queryClient={queryClient}>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </trpc.Provider>
  );
}
```

### Query and Mutation Hooks

```typescript
// components/UserProfile.tsx
function UserProfile({ userId }: { userId: string }) {
  // Query with type inference
  const { data: user, isLoading } = trpc.user.getById.useQuery({ id: userId });

  // Mutation with optimistic updates
  const utils = trpc.useUtils();
  const updateUser = trpc.user.update.useMutation({
    onMutate: async (newData) => {
      await utils.user.getById.cancel({ id: userId });
      const previous = utils.user.getById.getData({ id: userId });
      utils.user.getById.setData({ id: userId }, (old) => ({ ...old, ...newData }));
      return { previous };
    },
    onError: (err, newData, context) => {
      utils.user.getById.setData({ id: userId }, context?.previous);
    },
    onSettled: () => {
      utils.user.getById.invalidate({ id: userId });
    },
  });

  if (isLoading) return <Spinner />;

  // user is fully typed: { id: string, name: string, email: string, ... }
  return <div>{user?.name}</div>;
}
```

---

## Performance Patterns

### Batching

tRPC batches requests by default. Multiple queries in a component render into a single HTTP request.

```typescript
// These become ONE request
const user = trpc.user.getById.useQuery({ id: userId });
const posts = trpc.post.listByUser.useQuery({ userId });
const comments = trpc.comment.listByUser.useQuery({ userId });
```

### Prefetching

```typescript
// Prefetch on hover
function UserLink({ userId }: { userId: string }) {
  const utils = trpc.useUtils();

  return (
    <Link
      href={`/users/${userId}`}
      onMouseEnter={() => {
        utils.user.getById.prefetch({ id: userId });
      }}
    >
      View Profile
    </Link>
  );
}
```

### Server-Side Rendering (Next.js)

```typescript
// app/users/[id]/page.tsx
import { createServerSideHelpers } from '@trpc/react-query/server';

export default async function UserPage({ params }: { params: { id: string } }) {
  const helpers = createServerSideHelpers({
    router: appRouter,
    ctx: await createContext(),
  });

  // Prefetch on server
  await helpers.user.getById.prefetch({ id: params.id });

  return (
    <HydrationBoundary state={dehydrate(helpers.queryClient)}>
      <UserProfile userId={params.id} />
    </HydrationBoundary>
  );
}
```

---

## tRPC vs GraphQL vs REST

### Feature Comparison

| Feature | tRPC | GraphQL | REST |
|---------|------|---------|------|
| **Type Safety** | End-to-end (TypeScript) | With codegen | Manual/OpenAPI |
| **Bundle Size** | ~10KB | ~35KB+ | Varies |
| **Caching** | React Query | Apollo/urql cache | HTTP caching |
| **Code Generation** | None needed | Required for types | Optional |
| **Multi-source** | Limited | Excellent (resolvers) | Aggregation layer |
| **Public APIs** | Not recommended | Good | Best |
| **Learning Curve** | Low (TS devs) | Medium | Low |
| **Tooling** | VS Code autocomplete | Apollo DevTools, GraphiQL | Postman, OpenAPI |

### Migration Path

**GraphQL to tRPC** (TypeScript monorepo):
1. Keep GraphQL for mobile/external clients
2. Add tRPC for internal web dashboard
3. Share business logic between both

**REST to tRPC**:
1. Keep REST for public API
2. Use tRPC for internal services
3. Generate OpenAPI from tRPC if needed (experimental)

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Huge routers** | Hard to maintain | Split into domain routers |
| **Business logic in procedures** | Untestable | Extract to services |
| **No input validation** | Runtime errors | Always use Zod schemas |
| **Exposing DB models** | Leaky abstraction | Return DTOs |
| **No error boundaries** | Crashes app | Handle errors in UI |

---

## Resources

- [tRPC Documentation](https://trpc.io/docs)
- [T3 Stack (Next.js + tRPC)](https://create.t3.gg/)
- [tRPC + Prisma Example](https://github.com/trpc/examples-next-prisma-todomvc)
- [Zod Documentation](https://zod.dev/)
