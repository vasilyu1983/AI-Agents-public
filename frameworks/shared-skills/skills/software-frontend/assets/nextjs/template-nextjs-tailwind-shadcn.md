# Frontend Engineering - Next.js 16 + Tailwind CSS + shadcn/ui Template

*Purpose: Production-grade web applications with Next.js 16 App Router, TypeScript, Tailwind CSS, and shadcn/ui components.*

---

# When to Use

Use this template when building:

- Modern web applications with SSR/SSG
- Full-stack applications (with API routes)
- Dashboard and admin interfaces
- SaaS products
- E-commerce platforms
- Marketing sites with dynamic content
- Progressive Web Apps (PWAs)

---

# TEMPLATE STARTS HERE

# 1. Project Overview

**Project Name:**
[Name]

**Description:**
[Brief description]

**Tech Stack:**
- [ ] Next.js 16.x (App Router, Turbopack default, proxy.ts)
- [ ] React 19.2.x
- [ ] TypeScript 5.9.x
- [ ] Tailwind CSS v4.x
- [ ] shadcn/ui (Radix UI primitives)
- [ ] Prisma 6.x (optional - if full-stack)
- [ ] PostgreSQL (optional - if full-stack)

**Team:**
- Owner: [Name]
- Frontend Lead: [Name]
- Designer: [Name]

**Timeline:**
- Start: [YYYY-MM-DD]
- MVP: [YYYY-MM-DD]
- Launch: [YYYY-MM-DD]

---

# 2. Project Setup

## 2.1 Initial Setup

```bash
# Create Next.js app with TypeScript and Tailwind
npx create-next-app@latest my-app --typescript --tailwind --app --eslint

cd my-app

# Install shadcn/ui
npx shadcn-ui@latest init

# Install additional dependencies
npm install zod react-hook-form @hookform/resolvers/zod
npm install zustand
npm install swr
npm install framer-motion
npm install date-fns
npm install lucide-react
npm install class-variance-authority clsx tailwind-merge

# Dev dependencies
npm install -D @types/node
npm install -D prettier prettier-plugin-tailwindcss
npm install -D vitest @testing-library/react @testing-library/jest-dom
npm install -D @playwright/test
```

## 2.2 Project Structure

```
my-app/
|-- app/
|   |-- (auth)/
|   |   |-- login/
|   |   |   `-- page.tsx
|   |   `-- register/
|   |       `-- page.tsx
|   |-- (dashboard)/
|   |   |-- layout.tsx
|   |   |-- page.tsx
|   |   |-- users/
|   |   |   |-- page.tsx
|   |   |   `-- [id]/
|   |   |       `-- page.tsx
|   |   `-- settings/
|   |       `-- page.tsx
|   |-- api/
|   |   |-- auth/
|   |   |   `-- route.ts
|   |   `-- users/
|   |       |-- route.ts
|   |       `-- [id]/
|   |           `-- route.ts
|   |-- layout.tsx
|   |-- page.tsx
|   |-- loading.tsx
|   |-- error.tsx
|   `-- not-found.tsx
|-- src/
|   |-- components/
|   |   |-- ui/              # shadcn/ui components
|   |   |   |-- button.tsx
|   |   |   |-- input.tsx
|   |   |   |-- dialog.tsx
|   |   |   `-- ...
|   |   |-- forms/
|   |   |   |-- login-form.tsx
|   |   |   `-- user-form.tsx
|   |   |-- layouts/
|   |   |   |-- header.tsx
|   |   |   |-- footer.tsx
|   |   |   `-- sidebar.tsx
|   |   `-- shared/
|   |       |-- loading.tsx
|   |       `-- error-boundary.tsx
|   |-- lib/
|   |   |-- utils.ts
|   |   |-- cn.ts
|   |   |-- api.ts
|   |   |-- auth.ts
|   |   |-- store.ts
|   |   `-- hooks/
|   |       |-- use-auth.ts
|   |       `-- use-toast.ts
|   |-- types/
|   |   `-- index.ts
|   |-- styles/
|   |   `-- globals.css
|   `-- providers/
|       |-- auth-provider.tsx
|       `-- theme-provider.tsx
|-- public/
|   |-- images/
|   `-- fonts/
|-- prisma/               # If using database
|   `-- schema.prisma
|-- tests/
|   |-- unit/
|   |-- integration/
|   `-- e2e/
|-- .env.example
|-- .env.local
|-- .eslintrc.json
|-- .prettierrc
|-- next.config.js
|-- tailwind.config.ts
|-- tsconfig.json
|-- components.json       # shadcn/ui config
|-- vitest.config.ts
`-- playwright.config.ts
```

---

# 3. Configuration Files

## 3.1 tailwind.config.ts

```ts
import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};

export default config;
```

## 3.2 next.config.ts (Next.js 16)

```ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  images: {
    // 'domains' is deprecated - use remotePatterns instead
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'your-domain.com',
      },
    ],
    formats: ['image/avif', 'image/webp'],
  },
  // Turbopack is now default - remove --turbopack flags from scripts
  turbopack: {
    // Turbopack options (previously experimental.turbopack)
  },
  // If using proxy.ts and need URL normalization disabled
  // skipProxyUrlNormalize: true,
};

export default nextConfig;
```

## 3.3 proxy.ts (Next.js 16 - replaces middleware.ts)

```ts
// proxy.ts (root of project)
// NOTE: Runs on Node.js runtime (not Edge). Use middleware.ts if you need Edge.
import { NextRequest, NextResponse } from 'next/server';

export function proxy(request: NextRequest) {
  // Authentication check example
  const token = request.cookies.get('token');

  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Add custom headers
  const response = NextResponse.next();
  response.headers.set('x-custom-header', 'value');

  return response;
}

export const config = {
  matcher: [
    // Match all paths except static files and api routes
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
```

## 3.4 .env.example

```env
# App
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Database (if using Prisma)
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# Auth (if using NextAuth)
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-change-in-production

# APIs (if needed)
NEXT_PUBLIC_API_URL=http://localhost:3000/api
```

---

# 4. Root Layout

## 4.1 app/layout.tsx

```tsx
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from '@/providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: {
    default: 'My App',
    template: '%s | My App',
  },
  description: 'My Next.js application',
  keywords: ['next.js', 'react', 'typescript'],
  authors: [{ name: 'Your Name' }],
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://your-domain.com',
    siteName: 'My App',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
```

## 4.2 src/providers/index.tsx

```tsx
'use client';

import { ThemeProvider } from './theme-provider';
import { AuthProvider } from './auth-provider';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <AuthProvider>
        {children}
      </AuthProvider>
    </ThemeProvider>
  );
}
```

---

# 5. Common Components

## 5.1 Loading States

```tsx
// components/shared/loading.tsx
import { Loader2 } from 'lucide-react';

export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
    </div>
  );
}

export function LoadingSkeleton() {
  return (
    <div className="space-y-4">
      <div className="h-12 w-full animate-pulse rounded-lg bg-muted" />
      <div className="h-12 w-full animate-pulse rounded-lg bg-muted" />
      <div className="h-12 w-full animate-pulse rounded-lg bg-muted" />
    </div>
  );
}

// app/loading.tsx
import { LoadingSpinner } from '@/components/shared/loading';

export default function Loading() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <LoadingSpinner />
    </div>
  );
}
```

## 5.2 Error Handling

```tsx
// app/error.tsx
'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center">
      <h2 className="mb-4 text-2xl font-bold">Something went wrong!</h2>
      <p className="mb-4 text-muted-foreground">{error.message}</p>
      <Button onClick={reset}>Try again</Button>
    </div>
  );
}
```

## 5.3 Not Found

```tsx
// app/not-found.tsx
import Link from 'next/link';
import { Button } from '@/components/ui/button';

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center">
      <h1 className="mb-2 text-6xl font-bold">404</h1>
      <h2 className="mb-4 text-2xl">Page Not Found</h2>
      <p className="mb-8 text-muted-foreground">
        The page you're looking for doesn't exist.
      </p>
      <Button asChild>
        <Link href="/">Go Home</Link>
      </Button>
    </div>
  );
}
```

---

# 6. Authentication Example

## 6.1 Login Form Component

```tsx
// components/forms/login-form.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginForm = z.infer<typeof loginSchema>;

export function LoginForm() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  const form = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  async function onSubmit(data: LoginForm) {
    try {
      setError(null);

      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Login failed');
      }

      router.push('/dashboard');
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input
                  type="email"
                  placeholder="you@example.com"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input type="password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {error && (
          <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
            {error}
          </div>
        )}

        <Button
          type="submit"
          className="w-full"
          disabled={form.formState.isSubmitting}
        >
          {form.formState.isSubmitting ? 'Logging in...' : 'Login'}
        </Button>
      </form>
    </Form>
  );
}
```

## 6.2 Login Page

```tsx
// app/(auth)/login/page.tsx
import { Metadata } from 'next';
import Link from 'next/link';
import { LoginForm } from '@/components/forms/login-form';

export const metadata: Metadata = {
  title: 'Login',
  description: 'Login to your account',
};

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold">Welcome back</h1>
          <p className="mt-2 text-muted-foreground">
            Login to your account to continue
          </p>
        </div>

        <div className="rounded-lg border bg-card p-8">
          <LoginForm />
        </div>

        <p className="text-center text-sm text-muted-foreground">
          Don't have an account?{' '}
          <Link
            href="/register"
            className="font-medium text-primary hover:underline"
          >
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}
```

---

# 7. Dashboard Layout

## 7.1 Dashboard Layout with Sidebar

```tsx
// app/(dashboard)/layout.tsx
import { Header } from '@/components/layouts/header';
import { Sidebar } from '@/components/layouts/sidebar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Header />
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
```

## 7.2 Sidebar Component

```tsx
// components/layouts/sidebar.tsx
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Home, Users, Settings } from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Users', href: '/dashboard/users', icon: Users },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex w-64 flex-col border-r bg-card">
      <div className="p-6">
        <h1 className="text-2xl font-bold">My App</h1>
      </div>

      <nav className="flex-1 space-y-1 px-3">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
```

## 7.3 Header Component

```tsx
// components/layouts/header.tsx
'use client';

import { useAuth } from '@/lib/hooks/use-auth';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { User } from 'lucide-react';

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="flex h-16 items-center justify-between border-b px-6">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold">Dashboard</h2>
      </div>

      <div className="flex items-center gap-4">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <User className="h-5 w-5" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>
              {user?.name || 'User'}
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Profile</DropdownMenuItem>
            <DropdownMenuItem>Settings</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={logout}>
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
```

---

# 8. Data Fetching Example

## 8.1 Server Component with Data Fetching

```tsx
// app/(dashboard)/users/page.tsx
import { Suspense } from 'react';
import { LoadingSkeleton } from '@/components/shared/loading';
import { UserCard } from '@/components/users/user-card';

async function getUsers() {
  const res = await fetch('https://api.example.com/users', {
    next: { revalidate: 3600 }, // Revalidate every hour
  });

  if (!res.ok) {
    throw new Error('Failed to fetch users');
  }

  return res.json();
}

async function UsersList() {
  const users = await getUsers();

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {users.map((user: User) => (
        <UserCard key={user.id} user={user} />
      ))}
    </div>
  );
}

export default function UsersPage() {
  return (
    <div>
      <h1 className="mb-6 text-3xl font-bold">Users</h1>
      <Suspense fallback={<LoadingSkeleton />}>
        <UsersList />
      </Suspense>
    </div>
  );
}
```

## 8.2 Client Component with SWR

```tsx
// components/users/user-list-client.tsx
'use client';

import useSWR from 'swr';
import { UserCard } from './user-card';
import { LoadingSkeleton } from '@/components/shared/loading';

const fetcher = (url: string) => fetch(url).then((r) => r.json());

export function UserListClient() {
  const { data: users, error, isLoading } = useSWR('/api/users', fetcher);

  if (error) {
    return <div>Failed to load users</div>;
  }

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {users.map((user: User) => (
        <UserCard key={user.id} user={user} />
      ))}
    </div>
  );
}
```

---

# 9. Utilities

## 9.1 cn() Utility

```ts
// lib/utils.ts
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

## 9.2 API Client

```ts
// lib/api.ts
class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

export async function fetcher<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new APIError(response.status, error.message || 'API Error');
  }

  return response.json();
}
```

---

# 10. Testing

## 10.1 Component Test

```tsx
// components/ui/button.test.tsx
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

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click</Button>);
    expect(screen.getByText('Click')).toBeDisabled();
  });
});
```

## 10.2 E2E Test

```ts
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test('user can login', async ({ page }) => {
  await page.goto('/login');

  await page.fill('input[name="email"]', 'user@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  await expect(page).toHaveURL('/dashboard');
  await expect(page.locator('text=Welcome back')).toBeVisible();
});
```

---

# 11. Production Checklist

## 11.1 Performance
- [ ] Image optimization (Next/Image)
- [ ] Code splitting (dynamic imports)
- [ ] Bundle size analysis
- [ ] Lazy loading components
- [ ] Route prefetching
- [ ] Static generation where possible
- [ ] API response caching

## 11.2 SEO
- [ ] Metadata for all pages
- [ ] Open Graph tags
- [ ] Twitter cards
- [ ] Sitemap generation
- [ ] robots.txt
- [ ] Semantic HTML

## 11.3 Accessibility
- [ ] Keyboard navigation
- [ ] Screen reader support
- [ ] ARIA labels
- [ ] Color contrast (WCAG AA)
- [ ] Focus indicators
- [ ] Alt text for images

## 11.4 Security
- [ ] Environment variables secure
- [ ] CSP headers
- [ ] CORS configuration
- [ ] Input validation
- [ ] XSS prevention
- [ ] CSRF protection

## 11.5 Monitoring
- [ ] Error tracking (Sentry)
- [ ] Analytics (Google Analytics, Plausible)
- [ ] Performance monitoring
- [ ] User feedback system

---

# END

This template provides a production-ready foundation for Next.js 16 applications. Customize based on specific project requirements.
