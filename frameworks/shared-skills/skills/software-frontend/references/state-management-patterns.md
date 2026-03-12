# State Management Patterns for Modern Frontend

Patterns for managing state in modern frontend applications: server state vs client state, TanStack Query, Zustand, Jotai, and Redux Toolkit. Includes decision frameworks, performance optimization, and common anti-patterns.

---

## Table of Contents

1. [Server State vs Client State](#server-state-vs-client-state)
2. [TanStack Query (Server State)](#tanstack-query-server-state)
3. [Zustand (Client State)](#zustand-client-state)
4. [Jotai (Atomic State)](#jotai-atomic-state)
5. [Redux Toolkit (When Still Appropriate)](#redux-toolkit-when-still-appropriate)
6. [State Management Decision Framework](#state-management-decision-framework)
7. [Common Anti-Patterns](#common-anti-patterns)
8. [Performance Optimization](#performance-optimization)

---

## Server State vs Client State

### The Critical Distinction

| Characteristic | Server State | Client State |
|----------------|-------------|-------------|
| Source of truth | Remote server/database | User's browser |
| Persistence | Survives page refresh | Lost on refresh (unless persisted) |
| Shared | Multiple users see same data | Unique to this user session |
| Examples | User profiles, posts, products | UI state, form drafts, theme preference |
| Caching behavior | Stale-while-revalidate | Immediate updates |
| Synchronization | Must sync with server | Local only |

### Why This Matters

The single biggest state management mistake is treating server data as client state:

```text
WRONG: Fetch data -> store in Redux -> manually sync with server
  - You now have two sources of truth
  - You must handle cache invalidation, optimistic updates, retries
  - Redux store becomes a bad, incomplete copy of your database

RIGHT: Use TanStack Query for server data, Zustand for UI state
  - TanStack Query handles caching, revalidation, deduplication
  - Zustand handles only truly client-side state
  - Single source of truth for each category
```

### State Classification Guide

```text
User list from API          -> Server state  (TanStack Query)
Search filter text          -> URL state     (searchParams)
Current page number         -> URL state     (searchParams)
Shopping cart               -> Client state  (Zustand + persist)
Theme (dark/light)          -> Client state  (Zustand + persist)
Modal open/closed           -> Component state (useState)
Form input values           -> Component state (react-hook-form)
Authentication token        -> Client state  (Zustand + persist)
Notification toast queue    -> Client state  (Zustand)
Selected tab                -> URL or component state
```

---

## TanStack Query (Server State)

### Core Concepts

```typescript
// Setup: QueryClientProvider wraps your app
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,     // Data is fresh for 60 seconds
      gcTime: 5 * 60 * 1000,    // Garbage collect after 5 minutes
      retry: 3,                  // Retry failed requests 3 times
      refetchOnWindowFocus: true, // Refetch when tab regains focus
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
    </QueryClientProvider>
  );
}
```

### Query Keys: The Cache Address

```typescript
// Query keys must uniquely identify the data
// Think of them as cache keys

// Simple key
useQuery({ queryKey: ['users'], queryFn: fetchUsers });

// Parameterized key
useQuery({
  queryKey: ['users', userId],
  queryFn: () => fetchUser(userId),
});

// Complex key with filters
useQuery({
  queryKey: ['users', { role: 'admin', page: 2, sort: 'name' }],
  queryFn: () => fetchUsers({ role: 'admin', page: 2, sort: 'name' }),
});

// Key structure convention:
// ['entity', ...params]
// ['users']              -> all users
// ['users', 'list', { page: 1 }] -> paginated list
// ['users', 'detail', userId]     -> single user
```

### Caching and Invalidation

```typescript
// Automatic cache invalidation after mutation
const queryClient = useQueryClient();

const createUser = useMutation({
  mutationFn: (newUser: CreateUserInput) => api.createUser(newUser),
  onSuccess: () => {
    // Invalidate all queries starting with 'users'
    queryClient.invalidateQueries({ queryKey: ['users'] });
  },
});

// Targeted invalidation
queryClient.invalidateQueries({ queryKey: ['users', 'list'] });
// Does NOT invalidate ['users', 'detail', userId]

// Manual cache update (skip refetch)
queryClient.setQueryData(['users', 'detail', userId], updatedUser);
```

### Optimistic Updates

```typescript
const updateUser = useMutation({
  mutationFn: (data: UpdateUserInput) => api.updateUser(data),

  // Optimistic update: update UI immediately
  onMutate: async (newData) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: ['users', 'detail', newData.id] });

    // Snapshot previous value
    const previousUser = queryClient.getQueryData(
      ['users', 'detail', newData.id]
    );

    // Optimistically update cache
    queryClient.setQueryData(
      ['users', 'detail', newData.id],
      (old: User) => ({ ...old, ...newData })
    );

    // Return context for rollback
    return { previousUser };
  },

  // Rollback on error
  onError: (err, newData, context) => {
    if (context?.previousUser) {
      queryClient.setQueryData(
        ['users', 'detail', newData.id],
        context.previousUser
      );
    }
  },

  // Always refetch after success or error
  onSettled: (data, error, variables) => {
    queryClient.invalidateQueries({
      queryKey: ['users', 'detail', variables.id]
    });
  },
});
```

### Dependent Queries

```typescript
// Query that depends on another query's result
const { data: user } = useQuery({
  queryKey: ['user', userId],
  queryFn: () => fetchUser(userId),
});

const { data: projects } = useQuery({
  queryKey: ['projects', user?.organizationId],
  queryFn: () => fetchProjects(user!.organizationId),
  enabled: !!user?.organizationId,  // Only run when user data is available
});
```

### Infinite Queries (Pagination)

```typescript
const {
  data,
  fetchNextPage,
  hasNextPage,
  isFetchingNextPage,
} = useInfiniteQuery({
  queryKey: ['posts', 'infinite'],
  queryFn: ({ pageParam }) => fetchPosts({ cursor: pageParam, limit: 20 }),
  initialPageParam: undefined as string | undefined,
  getNextPageParam: (lastPage) => lastPage.nextCursor ?? undefined,
});

// Flatten all pages
const allPosts = data?.pages.flatMap(page => page.posts) ?? [];
```

---

## Zustand (Client State)

### Store Design

```typescript
import { create } from 'zustand';
import { persist, devtools } from 'zustand/middleware';

// Simple store
interface CounterStore {
  count: number;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
}

const useCounterStore = create<CounterStore>()(
  devtools((set) => ({
    count: 0,
    increment: () => set((state) => ({ count: state.count + 1 })),
    decrement: () => set((state) => ({ count: state.count - 1 })),
    reset: () => set({ count: 0 }),
  }))
);
```

### Slices Pattern (Large Stores)

```typescript
// Split large stores into slices
interface AuthSlice {
  user: User | null;
  token: string | null;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
}

interface UISlice {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

const createAuthSlice: StateCreator<
  AuthSlice & UISlice,
  [],
  [],
  AuthSlice
> = (set) => ({
  user: null,
  token: null,
  setAuth: (user, token) => set({ user, token }),
  logout: () => set({ user: null, token: null }),
});

const createUISlice: StateCreator<
  AuthSlice & UISlice,
  [],
  [],
  UISlice
> = (set) => ({
  sidebarOpen: true,
  theme: 'light',
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setTheme: (theme) => set({ theme }),
});

// Combine slices
const useAppStore = create<AuthSlice & UISlice>()(
  devtools(
    persist(
      (...a) => ({
        ...createAuthSlice(...a),
        ...createUISlice(...a),
      }),
      {
        name: 'app-storage',
        partialize: (state) => ({
          // Only persist these fields
          user: state.user,
          token: state.token,
          theme: state.theme,
        }),
      }
    )
  )
);
```

### Middleware

```typescript
// Persist to localStorage
const useStore = create<MyState>()(
  persist(
    (set) => ({ /* ... */ }),
    {
      name: 'my-store',           // localStorage key
      partialize: (state) => ({    // Only persist specific fields
        theme: state.theme,
        language: state.language,
      }),
      version: 1,                  // Schema version for migrations
      migrate: (persisted, version) => {
        // Handle store schema migrations
        if (version === 0) {
          return { ...persisted, newField: 'default' };
        }
        return persisted;
      },
    }
  )
);
```

### Selective Subscriptions

```typescript
// WRONG: Component re-renders on ANY store change
function Component() {
  const store = useAppStore();  // Subscribes to entire store
  return <div>{store.count}</div>;
}

// RIGHT: Subscribe to only what you need
function Component() {
  const count = useAppStore((state) => state.count);
  return <div>{count}</div>;
}

// RIGHT: Multiple selectors with shallow comparison
import { useShallow } from 'zustand/react/shallow';

function Component() {
  const { user, theme } = useAppStore(
    useShallow((state) => ({
      user: state.user,
      theme: state.theme,
    }))
  );
}
```

---

## Jotai (Atomic State)

### Core Concepts

```typescript
import { atom, useAtom, useAtomValue, useSetAtom } from 'jotai';

// Primitive atom
const countAtom = atom(0);

// Derived atom (computed from other atoms)
const doubleCountAtom = atom((get) => get(countAtom) * 2);

// Writable derived atom
const incrementAtom = atom(
  null,  // read value (null = write-only)
  (get, set) => {
    set(countAtom, get(countAtom) + 1);
  }
);

// Usage in components
function Counter() {
  const [count, setCount] = useAtom(countAtom);
  const doubleCount = useAtomValue(doubleCountAtom);  // Read-only
  const increment = useSetAtom(incrementAtom);          // Write-only

  return (
    <div>
      <p>Count: {count}, Double: {doubleCount}</p>
      <button onClick={increment}>+</button>
    </div>
  );
}
```

### Async Atoms

```typescript
// Async atom (fetches data)
const userAtom = atom(async (get) => {
  const userId = get(userIdAtom);
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
});

// Usage: Suspense-compatible
function UserProfile() {
  const user = useAtomValue(userAtom);  // Suspends until resolved
  return <div>{user.name}</div>;
}

// Wrap in Suspense boundary
<Suspense fallback={<Loading />}>
  <UserProfile />
</Suspense>
```

### When to Use Jotai vs Zustand

| Criterion | Jotai | Zustand |
|-----------|-------|---------|
| Mental model | Bottom-up (atoms compose) | Top-down (single store) |
| Best for | Highly granular, independent pieces of state | App-wide state with related actions |
| Re-renders | Minimal (atom-level) | Minimal (with selectors) |
| Async | Built-in (Suspense) | Manual |
| DevTools | jotai-devtools | zustand/devtools |
| Persistence | jotai-storage | zustand/persist |
| Learning curve | Lower (simple API) | Lower (simple API) |
| TypeScript | Excellent | Excellent |

---

## Redux Toolkit (When Still Appropriate)

### When Redux Still Makes Sense

- **Very large teams** (20+ developers) needing strict patterns and conventions
- **Complex client-side logic** with many interdependent state transitions
- **Existing Redux codebase** where migration cost exceeds benefit
- **Time-travel debugging** requirement (Redux DevTools)

### When to Avoid Redux

- New projects (use TanStack Query + Zustand instead)
- Small to medium teams
- Projects where most state is server data
- When the boilerplate-to-feature ratio is too high

### RTK Query (Redux Toolkit's Server State Solution)

```typescript
// RTK Query: similar to TanStack Query but Redux-integrated
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  tagTypes: ['Users', 'Posts'],
  endpoints: (builder) => ({
    getUsers: builder.query<User[], void>({
      query: () => '/users',
      providesTags: ['Users'],
    }),
    createUser: builder.mutation<User, CreateUserInput>({
      query: (body) => ({ url: '/users', method: 'POST', body }),
      invalidatesTags: ['Users'],
    }),
  }),
});

export const { useGetUsersQuery, useCreateUserMutation } = api;
```

---

## State Management Decision Framework

### Decision Tree

```text
What kind of state?
  |
  +-- Comes from API/server?
  |   +-- TanStack Query (caching, sync, deduplication)
  |   +-- RTK Query if already using Redux
  |
  +-- URL-representable? (filters, pagination, search)
  |   +-- URL searchParams (useSearchParams)
  |   +-- Next.js: searchParams in page props
  |
  +-- Global client state? (auth, theme, sidebar)
  |   +-- Zustand (simple, performant)
  |   +-- Jotai (if state is highly granular/atomic)
  |   +-- Redux Toolkit (only for large existing codebases)
  |
  +-- Component-local? (form state, toggle, hover)
  |   +-- useState / useReducer
  |   +-- react-hook-form (for forms)
  |
  +-- Shared between nearby components?
      +-- Lift state up (props)
      +-- Context (if prop drilling is excessive, low-frequency updates)
      +-- Zustand (if Context causes too many re-renders)
```

### Recommended Stack (2026)

| Layer | Tool | Purpose |
|-------|------|---------|
| Server state | TanStack Query v5 | API data caching and synchronization |
| Client state | Zustand | Auth, UI preferences, app-wide state |
| URL state | searchParams / nuqs | Filters, pagination, shareable state |
| Form state | react-hook-form + Zod | Form validation and management |
| Component state | useState / useReducer | Local UI state |

---

## Common Anti-Patterns

### 1. Storing Server Data in Global State

**Problem**: Fetching API data and storing it in Redux/Zustand, manually managing loading/error/cache states.

**Fix**: Use TanStack Query. It handles caching, deduplication, background refetching, and error/loading states.

### 2. Over-Fetching with useEffect

```typescript
// ANTI-PATTERN: Manual data fetching in useEffect
function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchUsers()
      .then(setUsers)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);
  // Problems: no caching, no dedup, no background refresh,
  // race conditions, manual loading/error state
}

// CORRECT: TanStack Query handles all of this
function UserList() {
  const { data: users, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: fetchUsers,
  });
}
```

### 3. Prop Drilling Global State

**Problem**: Passing auth/theme through 5+ levels of components.

**Fix**: Use Zustand or Context. But do not use Context for frequently-changing state (it re-renders all consumers).

### 4. Single Monolithic Store

**Problem**: One massive Redux store with 50 reducers managing everything from auth to form state.

**Fix**: Use the right tool for each state category (see decision framework above).

### 5. Stale State After Mutations

**Problem**: User creates a post, but the post list still shows old data.

**Fix**: Invalidate queries after mutations. TanStack Query makes this explicit with `invalidateQueries`.

### 6. Putting Derived State in the Store

```typescript
// ANTI-PATTERN: Storing computed values
const useStore = create((set) => ({
  items: [],
  filteredItems: [],  // This is derived from items + filter
  filter: '',
  setFilter: (filter) => set((state) => ({
    filter,
    filteredItems: state.items.filter(i => i.name.includes(filter)),
  })),
}));

// CORRECT: Compute derived values at render time
const useStore = create((set) => ({
  items: [],
  filter: '',
  setFilter: (filter) => set({ filter }),
}));

// In component:
const items = useStore((s) => s.items);
const filter = useStore((s) => s.filter);
const filteredItems = useMemo(
  () => items.filter(i => i.name.includes(filter)),
  [items, filter]
);
```

---

## Performance Optimization

### Memoization Strategies

| Technique | When to Use |
|-----------|-------------|
| `useMemo` | Expensive computations from state |
| `useCallback` | Callback props to memoized children |
| Zustand selectors | Subscribe to minimal state slice |
| Jotai atoms | Automatic granular subscriptions |
| React Compiler | Automatic memoization (Next.js 16+) |

### Selective Subscriptions (Zustand)

```typescript
// Each component only re-renders when its selected state changes
function UserName() {
  // Only re-renders when user.name changes
  const name = useAppStore((state) => state.user?.name);
  return <span>{name}</span>;
}

function ThemeToggle() {
  // Only re-renders when theme changes
  const theme = useAppStore((state) => state.theme);
  const setTheme = useAppStore((state) => state.setTheme);
  return <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
    {theme}
  </button>;
}
```

### Query Deduplication (TanStack Query)

```typescript
// These two components share the SAME query and fetch only once
function ComponentA() {
  const { data } = useQuery({ queryKey: ['users'], queryFn: fetchUsers });
  return <div>{data?.length} users</div>;
}

function ComponentB() {
  const { data } = useQuery({ queryKey: ['users'], queryFn: fetchUsers });
  return <ul>{data?.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
// Only ONE network request is made, result shared via cache
```

### React Compiler (Automatic Optimization)

```typescript
// With React Compiler (Next.js 16+), manual memoization is often unnecessary
// The compiler automatically memoizes components, values, and callbacks

// Before (manual optimization):
const MemoizedComponent = React.memo(function Component({ data }) {
  const processed = useMemo(() => expensiveComputation(data), [data]);
  const handleClick = useCallback(() => doSomething(data), [data]);
  return <div onClick={handleClick}>{processed}</div>;
});

// After (React Compiler handles it):
function Component({ data }) {
  const processed = expensiveComputation(data);
  const handleClick = () => doSomething(data);
  return <div onClick={handleClick}>{processed}</div>;
}
// Compiler inserts memoization automatically
```

---

## Cross-References

- [fullstack-patterns.md](fullstack-patterns.md) -- Server/client components and data fetching
- [operational-playbook.md](operational-playbook.md) -- Architecture patterns and security
- [testing-frontend-patterns.md](testing-frontend-patterns.md) -- Testing state management
- [performance-optimization.md](performance-optimization.md) -- Render optimization techniques
- [../../software-clean-code-standard/utilities/testing-utilities.md](../../software-clean-code-standard/utilities/testing-utilities.md) -- MSW for mocking API in state tests
