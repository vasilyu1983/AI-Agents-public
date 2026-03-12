# Vite + React + TypeScript Starter Template

Lightning-fast React development with Vite bundler.

---

## Overview

- **Vite** - Next-generation frontend tooling
- **React 19** - Latest React with hooks
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **React Router** - Client-side routing
- **TanStack Query** - Data fetching
- **Vitest** - Testing

---

## Quick Start

```bash
# Create project
npm create vite@latest my-app -- --template react-ts
cd my-app
npm install

# Add TailwindCSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Add React Router
npm install react-router-dom

# Add TanStack Query
npm install @tanstack/react-query

# Add testing
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

---

## Project Structure

```
my-app/
|-- src/
|   |-- components/
|   |-- pages/
|   |-- hooks/
|   |-- utils/
|   |-- App.tsx
|   |-- main.tsx
|   `-- index.css
|-- public/
|-- index.html
|-- vite.config.ts
`-- tailwind.config.js
```

---

## Core Patterns

### Component with Hooks

```tsx
// src/components/Counter.tsx
import { useState } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div className="counter">
      <h2>Count: {count}</h2>
      <button onClick={() => setCount(count + 1)}>+</button>
      <button onClick={() => setCount(count - 1)}>-</button>
      <button onClick={() => setCount(0)}>Reset</button>
    </div>
  );
}
```

### Data Fetching with TanStack Query

```tsx
// src/pages/BlogList.tsx
import { useQuery } from '@tanstack/react-query';

interface Post {
  id: number;
  title: string;
  excerpt: string;
}

async function fetchPosts(): Promise<Post[]> {
  const res = await fetch('https://api.example.com/posts');
  if (!res.ok) throw new Error('Failed to fetch');
  return res.json();
}

export function BlogList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['posts'],
    queryFn: fetchPosts,
  });

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <div className="grid gap-4">
      {data?.map((post) => (
        <article key={post.id} className="p-4 border rounded">
          <h2>{post.title}</h2>
          <p>{post.excerpt}</p>
        </article>
      ))}
    </div>
  );
}
```

### Custom Hook

```tsx
// src/hooks/useAuth.ts
import { useState, useEffect } from 'react';

interface User {
  id: number;
  name: string;
  email: string;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchUser(token).then(setUser).finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (credentials: { email: string; password: string }) => {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });
    const data = await res.json();
    setUser(data.user);
    localStorage.setItem('token', data.token);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('token');
  };

  return {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    logout,
  };
}
```

---

## Configuration

### vite.config.ts

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': '/src',
    },
  },
  server: {
    port: 3000,
  },
});
```

---

## Commands

```bash
npm run dev          # Start dev server (instant HMR)
npm run build        # Build for production
npm run preview      # Preview production build
npm run test         # Run tests
```

---

## Resources

- [Vite Docs](https://vitejs.dev/)
- [React Docs](https://react.dev/)
- [TanStack Query](https://tanstack.com/query/latest)
