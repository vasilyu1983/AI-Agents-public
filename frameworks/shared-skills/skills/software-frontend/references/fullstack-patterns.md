# Full-Stack Integration Examples

Complete examples showing frontend and backend working together in Next.js applications.

## Contents

- Example 1: User Authentication
- Example 2: Blog Posts CRUD
- Example 3: Real-Time Data with Server Components
- Example 4: Server Actions for Mutations
- Example 5: tRPC - End-to-End Type-Safe APIs
- Key Patterns Summary
- Shared Utilities (Implementation Patterns)

---

## Overview

These examples demonstrate how to build full-stack features using:
- **Backend**: Node.js + Prisma + PostgreSQL (API routes or Server Components)
- **Frontend**: Next.js 16 + TypeScript + Tailwind CSS + shadcn/ui

Each example includes both frontend and backend code with shared TypeScript types.

---

# Example 1: User Authentication

Complete authentication system with JWT tokens.

## Backend: Authentication API

### Prisma Schema

```prisma
// prisma/schema.prisma
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  password  String
  name      String
  role      Role     @default(USER)
  isActive  Boolean  @default(true)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([email])
  @@map("users")
}

enum Role {
  USER
  ADMIN
}
```

### Shared Types

```typescript
// src/types/auth.ts
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'USER' | 'ADMIN';
}

export interface AuthResponse {
  user: User;
  token: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}
```

### Backend API Route

```typescript
// app/api/auth/login/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { prisma } from '@/lib/db';
import type { LoginRequest, AuthResponse } from '@/types/auth';

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

export async function POST(request: NextRequest) {
  try {
    const body: LoginRequest = await request.json();

    // Validate input
    const validatedData = loginSchema.parse(body);

    // Find user
    const user = await prisma.user.findUnique({
      where: { email: validatedData.email },
    });

    if (!user) {
      return NextResponse.json(
        { error: 'Invalid credentials' },
        { status: 401 }
      );
    }

    // Verify password
    const isValidPassword = await bcrypt.compare(
      validatedData.password,
      user.password
    );

    if (!isValidPassword) {
      return NextResponse.json(
        { error: 'Invalid credentials' },
        { status: 401 }
      );
    }

    // Check if user is active
    if (!user.isActive) {
      return NextResponse.json(
        { error: 'Account is deactivated' },
        { status: 403 }
      );
    }

    // Generate JWT token
    const token = jwt.sign(
      { userId: user.id, role: user.role },
      process.env.JWT_SECRET!,
      { expiresIn: '7d' }
    );

    // Prepare response
    const response: AuthResponse = {
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
      },
      token,
    };

    return NextResponse.json(response);
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation error', details: error.errors },
        { status: 400 }
      );
    }

    console.error('Login error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

### Register API Route

```typescript
// app/api/auth/register/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { prisma } from '@/lib/db';
import type { RegisterRequest, AuthResponse } from '@/types/auth';

const registerSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  name: z.string().min(2),
});

export async function POST(request: NextRequest) {
  try {
    const body: RegisterRequest = await request.json();

    // Validate input
    const validatedData = registerSchema.parse(body);

    // Check if user already exists
    const existingUser = await prisma.user.findUnique({
      where: { email: validatedData.email },
    });

    if (existingUser) {
      return NextResponse.json(
        { error: 'Email already registered' },
        { status: 409 }
      );
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(validatedData.password, 12);

    // Create user
    const user = await prisma.user.create({
      data: {
        email: validatedData.email,
        password: hashedPassword,
        name: validatedData.name,
      },
    });

    // Generate JWT token
    const token = jwt.sign(
      { userId: user.id, role: user.role },
      process.env.JWT_SECRET!,
      { expiresIn: '7d' }
    );

    // Prepare response
    const response: AuthResponse = {
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
      },
      token,
    };

    return NextResponse.json(response, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation error', details: error.errors },
        { status: 400 }
      );
    }

    console.error('Registration error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

## Frontend: Authentication UI

### Auth Store (Zustand)

```typescript
// lib/store/auth-store.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/types/auth';

interface AuthStore {
  user: User | null;
  token: string | null;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      setAuth: (user, token) => set({ user, token }),
      logout: () => set({ user: null, token: null }),
      isAuthenticated: () => get().token !== null,
    }),
    {
      name: 'auth-storage',
    }
  )
);
```

### Login Form Component

```typescript
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
import { useAuthStore } from '@/lib/store/auth-store';
import type { LoginRequest, AuthResponse } from '@/types/auth';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginForm() {
  const router = useRouter();
  const { setAuth } = useAuthStore();
  const [error, setError] = useState<string | null>(null);

  const form = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  async function onSubmit(data: LoginFormData) {
    try {
      setError(null);

      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data satisfies LoginRequest),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Login failed');
      }

      const authResponse: AuthResponse = await response.json();

      // Store auth data
      setAuth(authResponse.user, authResponse.token);

      // Redirect to dashboard
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

### Login Page

```typescript
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

### Protected Route Middleware

```typescript
// middleware.ts
import { NextRequest, NextResponse } from 'next/server';
import jwt from 'jsonwebtoken';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token')?.value;

  // Check if accessing protected route
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url));
    }

    try {
      // Verify token
      jwt.verify(token, process.env.JWT_SECRET!);
      return NextResponse.next();
    } catch (error) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*'],
};
```

---

# Example 2: Blog Posts CRUD

Complete CRUD operations with Server Components and Server Actions.

## Backend: Blog API

### Prisma Schema

```prisma
// prisma/schema.prisma
model Post {
  id        String   @id @default(cuid())
  title     String
  content   String
  excerpt   String?
  published Boolean  @default(false)
  authorId  String
  author    User     @relation(fields: [authorId], references: [id], onDelete: Cascade)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([authorId])
  @@index([published, createdAt])
  @@map("posts")
}
```

### Shared Types

```typescript
// src/types/post.ts
export interface Post {
  id: string;
  title: string;
  content: string;
  excerpt: string | null;
  published: boolean;
  authorId: string;
  author: {
    id: string;
    name: string;
    email: string;
  };
  createdAt: string;
  updatedAt: string;
}

export interface CreatePostInput {
  title: string;
  content: string;
  excerpt?: string;
  published?: boolean;
}

export interface UpdatePostInput extends Partial<CreatePostInput> {}

export interface PostsListResponse {
  posts: Post[];
  pagination: {
    page: number;
    pageSize: number;
    totalPages: number;
    totalPosts: number;
  };
}
```

### Backend API Routes

```typescript
// app/api/posts/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { prisma } from '@/lib/db';
import { getCurrentUser } from '@/lib/auth';
import type { CreatePostInput, PostsListResponse } from '@/types/post';

const createPostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1),
  excerpt: z.string().max(500).optional(),
  published: z.boolean().default(false),
});

// GET /api/posts - List posts with pagination
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const page = parseInt(searchParams.get('page') || '1');
    const pageSize = parseInt(searchParams.get('pageSize') || '10');
    const published = searchParams.get('published') === 'true';

    const skip = (page - 1) * pageSize;

    const [posts, totalPosts] = await Promise.all([
      prisma.post.findMany({
        where: published ? { published: true } : undefined,
        include: {
          author: {
            select: {
              id: true,
              name: true,
              email: true,
            },
          },
        },
        orderBy: { createdAt: 'desc' },
        skip,
        take: pageSize,
      }),
      prisma.post.count({
        where: published ? { published: true } : undefined,
      }),
    ]);

    const response: PostsListResponse = {
      posts: posts.map(post => ({
        ...post,
        createdAt: post.createdAt.toISOString(),
        updatedAt: post.updatedAt.toISOString(),
      })),
      pagination: {
        page,
        pageSize,
        totalPages: Math.ceil(totalPosts / pageSize),
        totalPosts,
      },
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Error fetching posts:', error);
    return NextResponse.json(
      { error: 'Failed to fetch posts' },
      { status: 500 }
    );
  }
}

// POST /api/posts - Create new post
export async function POST(request: NextRequest) {
  try {
    // Get authenticated user
    const user = await getCurrentUser(request);
    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const body: CreatePostInput = await request.json();

    // Validate input
    const validatedData = createPostSchema.parse(body);

    // Create post
    const post = await prisma.post.create({
      data: {
        ...validatedData,
        authorId: user.id,
      },
      include: {
        author: {
          select: {
            id: true,
            name: true,
            email: true,
          },
        },
      },
    });

    return NextResponse.json(
      {
        ...post,
        createdAt: post.createdAt.toISOString(),
        updatedAt: post.updatedAt.toISOString(),
      },
      { status: 201 }
    );
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation error', details: error.errors },
        { status: 400 }
      );
    }

    console.error('Error creating post:', error);
    return NextResponse.json(
      { error: 'Failed to create post' },
      { status: 500 }
    );
  }
}
```

```typescript
// app/api/posts/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { prisma } from '@/lib/db';
import { getCurrentUser } from '@/lib/auth';
import type { UpdatePostInput } from '@/types/post';

const updatePostSchema = z.object({
  title: z.string().min(1).max(200).optional(),
  content: z.string().min(1).optional(),
  excerpt: z.string().max(500).optional(),
  published: z.boolean().optional(),
});

// GET /api/posts/[id] - Get single post
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const post = await prisma.post.findUnique({
      where: { id: params.id },
      include: {
        author: {
          select: {
            id: true,
            name: true,
            email: true,
          },
        },
      },
    });

    if (!post) {
      return NextResponse.json(
        { error: 'Post not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      ...post,
      createdAt: post.createdAt.toISOString(),
      updatedAt: post.updatedAt.toISOString(),
    });
  } catch (error) {
    console.error('Error fetching post:', error);
    return NextResponse.json(
      { error: 'Failed to fetch post' },
      { status: 500 }
    );
  }
}

// PATCH /api/posts/[id] - Update post
export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // Get authenticated user
    const user = await getCurrentUser(request);
    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Check if post exists and user is author
    const existingPost = await prisma.post.findUnique({
      where: { id: params.id },
    });

    if (!existingPost) {
      return NextResponse.json(
        { error: 'Post not found' },
        { status: 404 }
      );
    }

    if (existingPost.authorId !== user.id && user.role !== 'ADMIN') {
      return NextResponse.json(
        { error: 'Forbidden' },
        { status: 403 }
      );
    }

    const body: UpdatePostInput = await request.json();

    // Validate input
    const validatedData = updatePostSchema.parse(body);

    // Update post
    const post = await prisma.post.update({
      where: { id: params.id },
      data: validatedData,
      include: {
        author: {
          select: {
            id: true,
            name: true,
            email: true,
          },
        },
      },
    });

    return NextResponse.json({
      ...post,
      createdAt: post.createdAt.toISOString(),
      updatedAt: post.updatedAt.toISOString(),
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation error', details: error.errors },
        { status: 400 }
      );
    }

    console.error('Error updating post:', error);
    return NextResponse.json(
      { error: 'Failed to update post' },
      { status: 500 }
    );
  }
}

// DELETE /api/posts/[id] - Delete post
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // Get authenticated user
    const user = await getCurrentUser(request);
    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Check if post exists and user is author
    const existingPost = await prisma.post.findUnique({
      where: { id: params.id },
    });

    if (!existingPost) {
      return NextResponse.json(
        { error: 'Post not found' },
        { status: 404 }
      );
    }

    if (existingPost.authorId !== user.id && user.role !== 'ADMIN') {
      return NextResponse.json(
        { error: 'Forbidden' },
        { status: 403 }
      );
    }

    // Delete post
    await prisma.post.delete({
      where: { id: params.id },
    });

    return NextResponse.json(
      { message: 'Post deleted successfully' },
      { status: 200 }
    );
  } catch (error) {
    console.error('Error deleting post:', error);
    return NextResponse.json(
      { error: 'Failed to delete post' },
      { status: 500 }
    );
  }
}
```

## Frontend: Blog UI

### Posts List (Server Component)

```typescript
// app/(dashboard)/posts/page.tsx
import { Suspense } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { PostCard } from '@/components/posts/post-card';
import { PostsSkeleton } from '@/components/posts/posts-skeleton';
import { Plus } from 'lucide-react';
import type { PostsListResponse } from '@/types/post';

async function getPosts(page: number = 1): Promise<PostsListResponse> {
  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/posts?page=${page}&published=true`,
    {
      next: { revalidate: 60 }, // Revalidate every minute
    }
  );

  if (!res.ok) {
    throw new Error('Failed to fetch posts');
  }

  return res.json();
}

async function PostsList({ page }: { page: number }) {
  const data = await getPosts(page);

  return (
    <div className="space-y-6">
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {data.posts.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          disabled={page === 1}
          asChild
        >
          <Link href={`/posts?page=${page - 1}`}>Previous</Link>
        </Button>

        <span className="text-sm text-muted-foreground">
          Page {data.pagination.page} of {data.pagination.totalPages}
        </span>

        <Button
          variant="outline"
          disabled={page >= data.pagination.totalPages}
          asChild
        >
          <Link href={`/posts?page=${page + 1}`}>Next</Link>
        </Button>
      </div>
    </div>
  );
}

export default function PostsPage({
  searchParams,
}: {
  searchParams: { page?: string };
}) {
  const page = parseInt(searchParams.page || '1');

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Blog Posts</h1>
          <p className="text-muted-foreground">
            Manage and publish your blog posts
          </p>
        </div>

        <Button asChild>
          <Link href="/posts/new">
            <Plus className="mr-2 h-4 w-4" />
            New Post
          </Link>
        </Button>
      </div>

      <Suspense fallback={<PostsSkeleton />}>
        <PostsList page={page} />
      </Suspense>
    </div>
  );
}
```

### Post Card Component

```typescript
// components/posts/post-card.tsx
import Link from 'next/link';
import { format } from 'date-fns';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { Post } from '@/types/post';

interface PostCardProps {
  post: Post;
}

export function PostCard({ post }: PostCardProps) {
  return (
    <Card className="flex flex-col">
      <CardHeader>
        <div className="mb-2 flex items-center justify-between">
          <Badge variant={post.published ? 'default' : 'secondary'}>
            {post.published ? 'Published' : 'Draft'}
          </Badge>
          <span className="text-xs text-muted-foreground">
            {format(new Date(post.createdAt), 'MMM d, yyyy')}
          </span>
        </div>
        <CardTitle className="line-clamp-2">
          <Link
            href={`/posts/${post.id}`}
            className="hover:underline"
          >
            {post.title}
          </Link>
        </CardTitle>
        <CardDescription className="line-clamp-3">
          {post.excerpt || post.content.slice(0, 150) + '...'}
        </CardDescription>
      </CardHeader>

      <CardFooter className="mt-auto">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>By {post.author.name}</span>
        </div>
      </CardFooter>
    </Card>
  );
}
```

### Create Post Form

```typescript
// components/forms/post-form.tsx
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
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { useAuthStore } from '@/lib/store/auth-store';
import type { CreatePostInput, Post } from '@/types/post';

const postSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  content: z.string().min(1, 'Content is required'),
  excerpt: z.string().max(500).optional(),
  published: z.boolean().default(false),
});

type PostFormData = z.infer<typeof postSchema>;

interface PostFormProps {
  post?: Post;
  mode: 'create' | 'edit';
}

export function PostForm({ post, mode }: PostFormProps) {
  const router = useRouter();
  const { token } = useAuthStore();
  const [error, setError] = useState<string | null>(null);

  const form = useForm<PostFormData>({
    resolver: zodResolver(postSchema),
    defaultValues: {
      title: post?.title || '',
      content: post?.content || '',
      excerpt: post?.excerpt || '',
      published: post?.published || false,
    },
  });

  async function onSubmit(data: PostFormData) {
    try {
      setError(null);

      const url = mode === 'create'
        ? '/api/posts'
        : `/api/posts/${post?.id}`;

      const method = mode === 'create' ? 'POST' : 'PATCH';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data satisfies CreatePostInput),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to save post');
      }

      const savedPost: Post = await response.json();

      // Redirect to post or posts list
      router.push(`/posts/${savedPost.id}`);
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
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Title</FormLabel>
              <FormControl>
                <Input placeholder="Enter post title" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="excerpt"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Excerpt (optional)</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Short summary of the post"
                  rows={3}
                  {...field}
                />
              </FormControl>
              <FormDescription>
                Brief summary shown in post listings
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="content"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Content</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Write your post content here"
                  rows={10}
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="published"
          render={({ field }) => (
            <FormItem className="flex items-center justify-between rounded-lg border p-4">
              <div className="space-y-0.5">
                <FormLabel className="text-base">
                  Publish post
                </FormLabel>
                <FormDescription>
                  Make this post visible to everyone
                </FormDescription>
              </div>
              <FormControl>
                <Switch
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
              </FormControl>
            </FormItem>
          )}
        />

        {error && (
          <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
            {error}
          </div>
        )}

        <div className="flex gap-4">
          <Button
            type="submit"
            disabled={form.formState.isSubmitting}
          >
            {form.formState.isSubmitting
              ? 'Saving...'
              : mode === 'create'
              ? 'Create Post'
              : 'Update Post'}
          </Button>

          <Button
            type="button"
            variant="outline"
            onClick={() => router.back()}
          >
            Cancel
          </Button>
        </div>
      </form>
    </Form>
  );
}
```

### Create Post Page

```typescript
// app/(dashboard)/posts/new/page.tsx
import { Metadata } from 'next';
import { PostForm } from '@/components/forms/post-form';

export const metadata: Metadata = {
  title: 'New Post',
  description: 'Create a new blog post',
};

export default function NewPostPage() {
  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Create New Post</h1>
        <p className="text-muted-foreground">
          Write and publish a new blog post
        </p>
      </div>

      <PostForm mode="create" />
    </div>
  );
}
```

---

# Example 3: Real-Time Data with Server Components

Using Server Components to eliminate API calls.

## Backend: Direct Database Access

```typescript
// lib/db/posts.ts
import { prisma } from './prisma';
import { cache } from 'react';

// Cache the database query for the request lifecycle
export const getPosts = cache(async (published?: boolean) => {
  return prisma.post.findMany({
    where: published !== undefined ? { published } : undefined,
    include: {
      author: {
        select: {
          id: true,
          name: true,
          email: true,
        },
      },
    },
    orderBy: { createdAt: 'desc' },
  });
});

export const getPost = cache(async (id: string) => {
  return prisma.post.findUnique({
    where: { id },
    include: {
      author: {
        select: {
          id: true,
          name: true,
          email: true,
        },
      },
    },
  });
});
```

## Frontend: Server Component (No API Call!)

```typescript
// app/(public)/blog/page.tsx
import { Suspense } from 'react';
import { getPosts } from '@/lib/db/posts';
import { PostCard } from '@/components/posts/post-card';
import { PostsSkeleton } from '@/components/posts/posts-skeleton';

async function BlogPosts() {
  // Direct database access in Server Component
  const posts = await getPosts(true); // Only published posts

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {posts.map((post) => (
        <PostCard
          key={post.id}
          post={{
            ...post,
            createdAt: post.createdAt.toISOString(),
            updatedAt: post.updatedAt.toISOString(),
          }}
        />
      ))}
    </div>
  );
}

export default function BlogPage() {
  return (
    <div className="container py-12">
      <h1 className="mb-8 text-4xl font-bold">Blog</h1>

      <Suspense fallback={<PostsSkeleton />}>
        <BlogPosts />
      </Suspense>
    </div>
  );
}

// Static generation at build time
export const revalidate = 3600; // Revalidate every hour
```

---

# Example 4: Server Actions for Mutations

Using Server Actions to avoid API routes for mutations.

## Server Actions

```typescript
// app/actions/posts.ts
'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { z } from 'zod';
import { prisma } from '@/lib/db';
import { getCurrentUser } from '@/lib/auth';

const createPostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1),
  excerpt: z.string().max(500).optional(),
  published: z.boolean().default(false),
});

export async function createPost(formData: FormData) {
  // Get authenticated user
  const user = await getCurrentUser();
  if (!user) {
    throw new Error('Unauthorized');
  }

  // Parse and validate form data
  const data = {
    title: formData.get('title') as string,
    content: formData.get('content') as string,
    excerpt: formData.get('excerpt') as string,
    published: formData.get('published') === 'on',
  };

  const validatedData = createPostSchema.parse(data);

  // Create post
  const post = await prisma.post.create({
    data: {
      ...validatedData,
      authorId: user.id,
    },
  });

  // Revalidate relevant paths
  revalidatePath('/posts');
  revalidatePath('/blog');

  // Redirect to new post
  redirect(`/posts/${post.id}`);
}

export async function updatePost(id: string, formData: FormData) {
  // Get authenticated user
  const user = await getCurrentUser();
  if (!user) {
    throw new Error('Unauthorized');
  }

  // Check ownership
  const existingPost = await prisma.post.findUnique({
    where: { id },
  });

  if (!existingPost) {
    throw new Error('Post not found');
  }

  if (existingPost.authorId !== user.id && user.role !== 'ADMIN') {
    throw new Error('Forbidden');
  }

  // Parse and validate form data
  const data = {
    title: formData.get('title') as string,
    content: formData.get('content') as string,
    excerpt: formData.get('excerpt') as string,
    published: formData.get('published') === 'on',
  };

  const validatedData = createPostSchema.parse(data);

  // Update post
  await prisma.post.update({
    where: { id },
    data: validatedData,
  });

  // Revalidate relevant paths
  revalidatePath('/posts');
  revalidatePath(`/posts/${id}`);
  revalidatePath('/blog');

  // Redirect to updated post
  redirect(`/posts/${id}`);
}

export async function deletePost(id: string) {
  // Get authenticated user
  const user = await getCurrentUser();
  if (!user) {
    throw new Error('Unauthorized');
  }

  // Check ownership
  const existingPost = await prisma.post.findUnique({
    where: { id },
  });

  if (!existingPost) {
    throw new Error('Post not found');
  }

  if (existingPost.authorId !== user.id && user.role !== 'ADMIN') {
    throw new Error('Forbidden');
  }

  // Delete post
  await prisma.post.delete({
    where: { id },
  });

  // Revalidate and redirect
  revalidatePath('/posts');
  revalidatePath('/blog');
  redirect('/posts');
}

export async function togglePublishPost(id: string) {
  // Get authenticated user
  const user = await getCurrentUser();
  if (!user) {
    throw new Error('Unauthorized');
  }

  // Check ownership
  const existingPost = await prisma.post.findUnique({
    where: { id },
  });

  if (!existingPost) {
    throw new Error('Post not found');
  }

  if (existingPost.authorId !== user.id && user.role !== 'ADMIN') {
    throw new Error('Forbidden');
  }

  // Toggle published status
  await prisma.post.update({
    where: { id },
    data: {
      published: !existingPost.published,
    },
  });

  // Revalidate paths
  revalidatePath('/posts');
  revalidatePath(`/posts/${id}`);
  revalidatePath('/blog');
}
```

## Frontend: Form with Server Action

```typescript
// components/forms/post-form-action.tsx
'use client';

import { useFormState, useFormStatus } from 'react-dom';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { createPost, updatePost } from '@/app/actions/posts';
import type { Post } from '@/types/post';

function SubmitButton({ mode }: { mode: 'create' | 'edit' }) {
  const { pending } = useFormStatus();

  return (
    <Button type="submit" disabled={pending}>
      {pending
        ? 'Saving...'
        : mode === 'create'
        ? 'Create Post'
        : 'Update Post'}
    </Button>
  );
}

interface PostFormActionProps {
  post?: Post;
  mode: 'create' | 'edit';
}

export function PostFormAction({ post, mode }: PostFormActionProps) {
  const action = mode === 'create'
    ? createPost
    : updatePost.bind(null, post!.id);

  const [state, formAction] = useFormState(action, null);

  return (
    <form action={formAction} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="title">Title</Label>
        <Input
          id="title"
          name="title"
          defaultValue={post?.title}
          required
          placeholder="Enter post title"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="excerpt">Excerpt (optional)</Label>
        <Textarea
          id="excerpt"
          name="excerpt"
          defaultValue={post?.excerpt || ''}
          rows={3}
          placeholder="Short summary of the post"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="content">Content</Label>
        <Textarea
          id="content"
          name="content"
          defaultValue={post?.content}
          required
          rows={10}
          placeholder="Write your post content here"
        />
      </div>

      <div className="flex items-center space-x-2">
        <Switch
          id="published"
          name="published"
          defaultChecked={post?.published}
        />
        <Label htmlFor="published">Publish post</Label>
      </div>

      {state?.error && (
        <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
          {state.error}
        </div>
      )}

      <div className="flex gap-4">
        <SubmitButton mode={mode} />
        <Button type="button" variant="outline">
          Cancel
        </Button>
      </div>
    </form>
  );
}
```

---

# Example 5: tRPC - End-to-End Type-Safe APIs

tRPC eliminates REST/GraphQL boilerplate with full TypeScript type safety from backend to frontend.

## Why tRPC in 2026?

| Approach | Boilerplate | Type Safety | Runtime Validation |
|----------|-------------|-------------|-------------------|
| REST + fetch | High (manual types) | Manual | Manual |
| GraphQL | Medium (codegen) | Generated | Schema-based |
| **tRPC** | **Minimal** | **Automatic** | **Zod built-in** |

**Best for**: Full-stack TypeScript apps where you control both client and server.

## Backend: tRPC Router Setup

### Installation

```bash
npm install @trpc/server @trpc/client @trpc/react-query @tanstack/react-query zod
```

### tRPC Initialization

```typescript
// server/trpc/trpc.ts
import { initTRPC, TRPCError } from '@trpc/server';
import { Context } from './context';
import superjson from 'superjson';

const t = initTRPC.context<Context>().create({
  transformer: superjson,
  errorFormatter({ shape }) {
    return shape;
  },
});

export const router = t.router;
export const publicProcedure = t.procedure;

// Protected procedure - requires authentication
export const protectedProcedure = t.procedure.use(async ({ ctx, next }) => {
  if (!ctx.user) {
    throw new TRPCError({ code: 'UNAUTHORIZED' });
  }
  return next({ ctx: { ...ctx, user: ctx.user } });
});
```

### Context Setup

```typescript
// server/trpc/context.ts
import { inferAsyncReturnType } from '@trpc/server';
import { FetchCreateContextFnOptions } from '@trpc/server/adapters/fetch';
import { prisma } from '@/lib/db';
import { verifyToken } from '@/lib/auth';

export async function createContext({ req }: FetchCreateContextFnOptions) {
  const token = req.headers.get('authorization')?.replace('Bearer ', '');
  const user = token ? await verifyToken(token) : null;

  return { prisma, user };
}

export type Context = inferAsyncReturnType<typeof createContext>;
```

### Define Routers

```typescript
// server/trpc/routers/post.ts
import { z } from 'zod';
import { router, publicProcedure, protectedProcedure } from '../trpc';
import { TRPCError } from '@trpc/server';

export const postRouter = router({
  // Public: Get all published posts
  list: publicProcedure
    .input(z.object({
      page: z.number().default(1),
      pageSize: z.number().default(10),
    }))
    .query(async ({ ctx, input }) => {
      const posts = await ctx.prisma.post.findMany({
        where: { published: true },
        include: { author: { select: { id: true, name: true } } },
        orderBy: { createdAt: 'desc' },
        skip: (input.page - 1) * input.pageSize,
        take: input.pageSize,
      });
      return posts;
    }),

  // Public: Get single post by ID
  byId: publicProcedure
    .input(z.string())
    .query(async ({ ctx, input }) => {
      const post = await ctx.prisma.post.findUnique({
        where: { id: input },
        include: { author: { select: { id: true, name: true, email: true } } },
      });
      if (!post) throw new TRPCError({ code: 'NOT_FOUND' });
      return post;
    }),

  // Protected: Create post
  create: protectedProcedure
    .input(z.object({
      title: z.string().min(1).max(200),
      content: z.string().min(1),
      excerpt: z.string().max(500).optional(),
      published: z.boolean().default(false),
    }))
    .mutation(async ({ ctx, input }) => {
      return ctx.prisma.post.create({
        data: { ...input, authorId: ctx.user.id },
      });
    }),

  // Protected: Update post
  update: protectedProcedure
    .input(z.object({
      id: z.string(),
      title: z.string().min(1).max(200).optional(),
      content: z.string().min(1).optional(),
      excerpt: z.string().max(500).optional(),
      published: z.boolean().optional(),
    }))
    .mutation(async ({ ctx, input }) => {
      const { id, ...data } = input;

      // Check ownership
      const post = await ctx.prisma.post.findUnique({ where: { id } });
      if (!post) throw new TRPCError({ code: 'NOT_FOUND' });
      if (post.authorId !== ctx.user.id && ctx.user.role !== 'ADMIN') {
        throw new TRPCError({ code: 'FORBIDDEN' });
      }

      return ctx.prisma.post.update({ where: { id }, data });
    }),

  // Protected: Delete post
  delete: protectedProcedure
    .input(z.string())
    .mutation(async ({ ctx, input }) => {
      const post = await ctx.prisma.post.findUnique({ where: { id: input } });
      if (!post) throw new TRPCError({ code: 'NOT_FOUND' });
      if (post.authorId !== ctx.user.id && ctx.user.role !== 'ADMIN') {
        throw new TRPCError({ code: 'FORBIDDEN' });
      }

      await ctx.prisma.post.delete({ where: { id: input } });
      return { success: true };
    }),
});
```

### Root Router

```typescript
// server/trpc/routers/_app.ts
import { router } from '../trpc';
import { postRouter } from './post';
import { userRouter } from './user';

export const appRouter = router({
  post: postRouter,
  user: userRouter,
});

export type AppRouter = typeof appRouter;
```

### Next.js API Route Handler

```typescript
// app/api/trpc/[trpc]/route.ts
import { fetchRequestHandler } from '@trpc/server/adapters/fetch';
import { appRouter } from '@/server/trpc/routers/_app';
import { createContext } from '@/server/trpc/context';

const handler = (req: Request) =>
  fetchRequestHandler({
    endpoint: '/api/trpc',
    req,
    router: appRouter,
    createContext,
  });

export { handler as GET, handler as POST };
```

## Frontend: tRPC Client Setup

### Provider Setup

```typescript
// lib/trpc/client.ts
import { createTRPCReact } from '@trpc/react-query';
import type { AppRouter } from '@/server/trpc/routers/_app';

export const trpc = createTRPCReact<AppRouter>();
```

```typescript
// lib/trpc/provider.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { httpBatchLink } from '@trpc/client';
import { useState } from 'react';
import { trpc } from './client';
import superjson from 'superjson';
import { useAuthStore } from '@/lib/store/auth-store';

export function TRPCProvider({ children }: { children: React.ReactNode }) {
  const { token } = useAuthStore();

  const [queryClient] = useState(() => new QueryClient());
  const [trpcClient] = useState(() =>
    trpc.createClient({
      links: [
        httpBatchLink({
          url: '/api/trpc',
          transformer: superjson,
          headers() {
            return token ? { authorization: `Bearer ${token}` } : {};
          },
        }),
      ],
    })
  );

  return (
    <trpc.Provider client={trpcClient} queryClient={queryClient}>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </trpc.Provider>
  );
}
```

### Usage in Components

```typescript
// components/posts/posts-list-trpc.tsx
'use client';

import { trpc } from '@/lib/trpc/client';
import { PostCard } from './post-card';
import { Skeleton } from '@/components/ui/skeleton';

export function PostsListTRPC() {
  // Full type inference - posts is Post[] automatically
  const { data: posts, isLoading, error } = trpc.post.list.useQuery({
    page: 1,
    pageSize: 10,
  });

  if (isLoading) return <Skeleton className="h-64" />;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {posts?.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
    </div>
  );
}
```

```typescript
// components/forms/create-post-trpc.tsx
'use client';

import { trpc } from '@/lib/trpc/client';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const createPostSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(1),
  excerpt: z.string().max(500).optional(),
  published: z.boolean().default(false),
});

type CreatePostInput = z.infer<typeof createPostSchema>;

export function CreatePostTRPC() {
  const router = useRouter();
  const utils = trpc.useUtils();

  const { register, handleSubmit, formState: { errors } } = useForm<CreatePostInput>({
    resolver: zodResolver(createPostSchema),
  });

  // Type-safe mutation with automatic error handling
  const createPost = trpc.post.create.useMutation({
    onSuccess: (post) => {
      // Invalidate posts list cache
      utils.post.list.invalidate();
      router.push(`/posts/${post.id}`);
    },
  });

  const onSubmit = (data: CreatePostInput) => {
    createPost.mutate(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <Input {...register('title')} placeholder="Title" />
      {errors.title && <p className="text-destructive">{errors.title.message}</p>}

      <Textarea {...register('content')} placeholder="Content" rows={10} />
      {errors.content && <p className="text-destructive">{errors.content.message}</p>}

      <Button type="submit" disabled={createPost.isPending}>
        {createPost.isPending ? 'Creating...' : 'Create Post'}
      </Button>

      {createPost.error && (
        <p className="text-destructive">{createPost.error.message}</p>
      )}
    </form>
  );
}
```

## tRPC vs REST API Comparison

```typescript
// FAIL REST: Manual types, no type safety
const res = await fetch('/api/posts');
const posts: Post[] = await res.json(); // Hope this matches!

// PASS tRPC: Automatic types, full type safety
const { data: posts } = trpc.post.list.useQuery({ page: 1 });
// posts is automatically typed as Post[] from backend
```

## When to Use tRPC

| Use Case | tRPC | REST/GraphQL |
|----------|------|--------------|
| Full-stack TypeScript | PASS Best | OK |
| Public API for third parties | FAIL | PASS REST |
| Mobile app + web | FAIL | PASS REST/GraphQL |
| Complex queries/subscriptions | OK | PASS GraphQL |
| Rapid prototyping | PASS Best | Slower |

**Key insight**: tRPC shines when you control both client and server in TypeScript. For public APIs or non-TypeScript clients, use REST or GraphQL.

---

# Key Patterns Summary

## Type Sharing
[OK] Define types once in `src/types/`
[OK] Import in both frontend and backend
[OK] Use `satisfies` for type checking

## Data Fetching
[OK] **Server Components**: Direct database access (no API)
[OK] **Client Components**: SWR or React Query with API routes
[OK] **Server Actions**: For mutations without API routes

## Authentication
[OK] Store token in Zustand + localStorage
[OK] Send token in `Authorization` header
[OK] Verify token in API routes and Server Actions
[OK] Use middleware for protected routes

## Validation
[OK] **Client-side**: Zod + React Hook Form
[OK] **Server-side**: Always validate with Zod
[OK] Share schemas between client and server

## Error Handling
[OK] **API Routes**: Return proper HTTP status codes
[OK] **Forms**: Display validation errors clearly
[OK] **Server Components**: Use error boundaries
[OK] **Server Actions**: Throw errors, caught by error boundaries

## Performance
[OK] **Server Components**: Fetch data server-side
[OK] **Caching**: Use `cache()` for database queries
[OK] **Revalidation**: `revalidatePath()` after mutations
[OK] **Streaming**: Use Suspense for incremental loading

---

# Shared Utilities (Implementation Patterns)

For cross-cutting implementation concerns, reference these centralized utilities:

- [error-handling.md](../../software-clean-code-standard/utilities/error-handling.md) - Effect Result types, correlation IDs
- [config-validation.md](../../software-clean-code-standard/utilities/config-validation.md) - Zod 3.24+, Valibot for client validation
- [logging-utilities.md](../../software-clean-code-standard/utilities/logging-utilities.md) - Structured logging patterns
- [testing-utilities.md](../../software-clean-code-standard/utilities/testing-utilities.md) - Vitest, MSW v2, factories, fixtures
- [observability-utilities.md](../../software-clean-code-standard/utilities/observability-utilities.md) - OpenTelemetry SDK, tracing, metrics
- [auth-utilities.md](../../software-clean-code-standard/utilities/auth-utilities.md) - jose JWT for frontend auth flows

---

# END

These examples demonstrate production-ready full-stack patterns for Next.js applications using both skills together.
