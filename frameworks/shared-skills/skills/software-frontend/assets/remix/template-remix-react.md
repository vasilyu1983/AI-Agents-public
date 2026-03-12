# Remix + React Starter Template

Full-stack React framework with server-side rendering, loaders, and actions.

---

## Overview

- **Remix** - Full-stack React framework
- **React 19** - Latest React
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **Prisma** - Database ORM
- **Vitest** - Testing

---

## Quick Start

```bash
npx create-remix@latest my-app
cd my-app
npm install

# Add TailwindCSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Add Prisma
npm install -D prisma
npm install @prisma/client
npx prisma init
```

---

## Project Structure

```
my-app/
|-- app/
|   |-- routes/
|   |   |-- _index.tsx           # Home route (/)
|   |   |-- login.tsx            # /login
|   |   |-- blog._index.tsx      # /blog
|   |   `-- blog.$slug.tsx       # /blog/:slug
|   |-- components/
|   |-- utils/
|   |-- root.tsx                 # Root component
|   `-- entry.client.tsx
|-- public/
`-- remix.config.js
```

---

## Core Patterns

### Route with Loader

```tsx
// app/routes/blog.$slug.tsx
import { json, type LoaderFunctionArgs } from '@remix-run/node';
import { useLoaderData } from '@remix-run/react';
import { prisma } from '~/utils/db.server';

export async function loader({ params }: LoaderFunctionArgs) {
  const post = await prisma.post.findUnique({
    where: { slug: params.slug },
  });

  if (!post) {
    throw new Response('Not Found', { status: 404 });
  }

  return json({ post });
}

export default function BlogPost() {
  const { post } = useLoaderData<typeof loader>();

  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.excerpt}</p>
      <div dangerouslySetInnerHTML={{ __html: post.content }} />
    </article>
  );
}
```

### Route with Action (Form)

```tsx
// app/routes/login.tsx
import { json, redirect, type ActionFunctionArgs } from '@remix-run/node';
import { Form, useActionData } from '@remix-run/react';
import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

export async function action({ request }: ActionFunctionArgs) {
  const formData = await request.formData();
  const email = formData.get('email');
  const password = formData.get('password');

  const result = loginSchema.safeParse({ email, password });

  if (!result.success) {
    return json(
      { errors: result.error.flatten().fieldErrors },
      { status: 400 }
    );
  }

  // Authenticate
  const user = await authenticateUser(result.data);

  if (!user) {
    return json(
      { errors: { email: 'Invalid credentials' } },
      { status: 401 }
    );
  }

  // Create session
  return redirect('/dashboard', {
    headers: {
      'Set-Cookie': await createUserSession(user.id),
    },
  });
}

export default function Login() {
  const actionData = useActionData<typeof action>();

  return (
    <Form method="post">
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          name="email"
          type="email"
          required
        />
        {actionData?.errors?.email && (
          <span className="error">{actionData.errors.email}</span>
        )}
      </div>

      <div>
        <label htmlFor="password">Password</label>
        <input
          id="password"
          name="password"
          type="password"
          required
        />
        {actionData?.errors?.password && (
          <span className="error">{actionData.errors.password}</span>
        )}
      </div>

      <button type="submit">Login</button>
    </Form>
  );
}
```

### Layout Route

```tsx
// app/routes/_layout.tsx
import { Outlet } from '@remix-run/react';

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white shadow">
        <nav className="container mx-auto px-4 py-4">
          {/* Navigation */}
        </nav>
      </header>

      <main className="flex-1">
        <Outlet />
      </main>

      <footer className="bg-gray-100 py-8">
        <div className="container mx-auto px-4 text-center">
          (c) 2025 My App
        </div>
      </footer>
    </div>
  );
}
```

---

## Key Features

**Loaders** - Fetch data on the server
**Actions** - Handle mutations on the server
**Form component** - Progressive enhancement
**Automatic revalidation** - Data stays fresh
**Optimistic UI** - Instant feedback

---

## Resources

- [Remix Docs](https://remix.run/docs)
- [Remix Examples](https://github.com/remix-run/examples)
