# Vite + React Best Practices & Patterns

Operational patterns for building fast React applications with Vite.

---

## Contents

- Why Vite?
- Project Setup Best Practices
- React Patterns
- Data Fetching with TanStack Query
- Routing with React Router
- Performance Optimization
- Environment Variables
- Testing
- Build Optimization
- Best Practices Checklist
- Common Pitfalls
- Resources

## Why Vite?

- **Instant server start** - No bundling in development
- **Lightning-fast HMR** - Updates in <50ms
- **Optimized builds** - Rollup for production
- **Native ESM** - Leverage browser modules
- **Plugin ecosystem** - React, TypeScript, PWA, etc.

---

## Project Setup Best Practices

### Recommended Stack (Use Latest + Lockfile)

```json
{
  "dependencies": {
    "react": "latest",
    "react-dom": "latest",
    "react-router-dom": "latest",
    "@tanstack/react-query": "latest"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "latest",
    "vite": "latest",
    "typescript": "latest",
    "vitest": "latest",
    "@testing-library/react": "latest"
  }
}
```

### vite.config.ts

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@utils': path.resolve(__dirname, './src/utils')
    }
  },

  server: {
    port: 3000,
    open: true
  },

  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom']
        }
      }
    }
  }
});
```

---

## React Patterns

### Component Structure

```tsx
// src/components/UserCard.tsx
import { useState } from 'react';

interface UserCardProps {
  name: string;
  email: string;
  avatar?: string;
  onEdit?: () => void;
}

export function UserCard({ name, email, avatar, onEdit }: UserCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className="user-card"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {avatar && <img src={avatar} alt={name} />}
      <h3>{name}</h3>
      <p>{email}</p>
      {isHovered && onEdit && (
        <button onClick={onEdit}>Edit</button>
      )}
    </div>
  );
}
```

### Custom Hooks

```typescript
// src/hooks/useLocalStorage.ts
import { useState, useEffect } from 'react';

export function useLocalStorage<T>(key: string, initialValue: T) {
  // Initialize state from localStorage
  const [value, setValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  // Update localStorage when value changes
  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  }, [key, value]);

  return [value, setValue] as const;
}
```

Usage:
```tsx
function App() {
  const [theme, setTheme] = useLocalStorage('theme', 'light');

  return (
    <div className={theme}>
      <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
        Toggle Theme
      </button>
    </div>
  );
}
```

---

## Data Fetching with TanStack Query

### Setup

```tsx
// src/main.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,  // 5 minutes
      retry: 3,
      refetchOnWindowFocus: false
    }
  }
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>
);
```

### Query Hook

```typescript
// src/hooks/usePosts.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

interface Post {
  id: number;
  title: string;
  content: string;
}

async function fetchPosts(): Promise<Post[]> {
  const res = await fetch('https://api.example.com/posts');
  if (!res.ok) throw new Error('Failed to fetch posts');
  return res.json();
}

async function createPost(newPost: Omit<Post, 'id'>): Promise<Post> {
  const res = await fetch('https://api.example.com/posts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(newPost)
  });
  if (!res.ok) throw new Error('Failed to create post');
  return res.json();
}

export function usePosts() {
  return useQuery({
    queryKey: ['posts'],
    queryFn: fetchPosts
  });
}

export function useCreatePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createPost,
    onSuccess: () => {
      // Invalidate and refetch posts
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    }
  });
}
```

Usage:
```tsx
function BlogList() {
  const { data: posts, isLoading, error } = usePosts();
  const createPost = useCreatePost();

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <div>
      <button
        onClick={() => createPost.mutate({ title: 'New Post', content: '...' })}
        disabled={createPost.isPending}
      >
        Create Post
      </button>

      {posts?.map(post => (
        <article key={post.id}>
          <h2>{post.title}</h2>
        </article>
      ))}
    </div>
  );
}
```

---

## Routing with React Router

### Setup

```tsx
// src/main.tsx
import { BrowserRouter } from 'react-router-dom';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>
);
```

### Route Configuration

```tsx
// src/App.tsx
import { Routes, Route, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';

// Lazy load routes
const Home = lazy(() => import('./pages/Home'));
const Blog = lazy(() => import('./pages/Blog'));
const BlogPost = lazy(() => import('./pages/BlogPost'));
const Dashboard = lazy(() => import('./pages/Dashboard'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/blog" element={<Blog />} />
        <Route path="/blog/:slug" element={<BlogPost />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}
```

### Protected Routes

```tsx
// src/components/ProtectedRoute.tsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return <div>Loading...</div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  return <>{children}</>;
}
```

---

## Performance Optimization

### Code Splitting

```tsx
import { lazy, Suspense } from 'react';

// Lazy load components
const HeavyComponent = lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HeavyComponent />
    </Suspense>
  );
}
```

### Memoization

```tsx
import { useMemo, useCallback, memo } from 'react';

// Memoize expensive calculations
function ExpensiveComponent({ items }: { items: Item[] }) {
  const total = useMemo(() => {
    return items.reduce((sum, item) => sum + item.price, 0);
  }, [items]);

  const handleClick = useCallback(() => {
    console.log('Clicked!');
  }, []);

  return <div>Total: {total}</div>;
}

// Memo for pure components
export const MemoizedComponent = memo(ExpensiveComponent);
```

---

## Environment Variables

```typescript
// .env
VITE_API_URL=https://api.example.com
VITE_APP_TITLE=My App
```

```typescript
// Access with import.meta.env
const apiUrl = import.meta.env.VITE_API_URL;
const appTitle = import.meta.env.VITE_APP_TITLE;
```

---

## Testing

### Component Test

```typescript
// src/components/Counter.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Counter } from './Counter';

describe('Counter', () => {
  it('renders initial count', () => {
    render(<Counter />);
    expect(screen.getByText(/Count: 0/)).toBeInTheDocument();
  });

  it('increments on button click', () => {
    render(<Counter />);
    const button = screen.getByRole('button', { name: /increment/i });
    fireEvent.click(button);
    expect(screen.getByText(/Count: 1/)).toBeInTheDocument();
  });
});
```

---

## Build Optimization

### Analyze Bundle

```bash
npm install -D rollup-plugin-visualizer
```

```typescript
// vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    react(),
    visualizer({ open: true })
  ]
});
```

### Reduce Bundle Size

```typescript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            return 'vendor';
          }
        }
      }
    },
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true
      }
    }
  }
});
```

---

## Best Practices Checklist

- [ ] Use TypeScript for type safety
- [ ] Lazy load routes and heavy components
- [ ] Use TanStack Query for server state
- [ ] Implement error boundaries
- [ ] Configure path aliases (@/)
- [ ] Use environment variables for config
- [ ] Analyze bundle size regularly
- [ ] Write tests for critical components
- [ ] Use memo/useMemo/useCallback wisely
- [ ] Configure HMR properly

---

## Common Pitfalls

[FAIL] **Don't:**
- Use CRA (deprecated) - use Vite instead
- Forget to memoize expensive computations
- Over-use useEffect
- Store server state in useState
- Ignore bundle size

[OK] **Do:**
- Use Vite for fast development
- Leverage TanStack Query for data fetching
- Lazy load routes
- Use proper TypeScript types
- Monitor performance with Lighthouse

---

## Resources

- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
- [TanStack Query](https://tanstack.com/query/latest)
- [React Router](https://reactrouter.com/)
- [Vitest](https://vitest.dev/)
