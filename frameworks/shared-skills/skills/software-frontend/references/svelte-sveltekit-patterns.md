# Svelte 5 + SvelteKit Best Practices & Patterns

Operational patterns for building production-ready Svelte and SvelteKit applications with runes reactivity.

---

## Contents

- Svelte 5 Runes (New Reactivity System)
- Universal Reactivity (Runes in .svelte.ts files)
- SvelteKit Patterns
- Component Patterns
- Performance Patterns
- Testing Patterns
- Common Patterns
- Migration from Svelte 4
- Resources

## Svelte 5 Runes (New Reactivity System)

### $state() - Reactive State

```svelte
<script lang="ts">
  // Reactive primitive
  let count = $state(0);

  // Reactive object
  let user = $state({
    name: 'John',
    age: 30
  });

  // Reactive array
  let todos = $state<Todo[]>([]);
</script>
```

### $derived() - Computed Values

```svelte
<script lang="ts">
  let count = $state(0);

  // Derived value (auto-updates)
  let doubled = $derived(count * 2);
  let isEven = $derived(count % 2 === 0);

  // Derived with complex logic
  let summary = $derived.by(() => {
    if (count === 0) return 'zero';
    if (count < 0) return 'negative';
    return 'positive';
  });
</script>
```

### $effect() - Side Effects

```svelte
<script lang="ts">
  let count = $state(0);

  // Run effect when count changes
  $effect(() => {
    console.log('Count is now:', count);
    document.title = `Count: ${count}`;
  });

  // Effect with cleanup
  $effect(() => {
    const interval = setInterval(() => {
      count++;
    }, 1000);

    return () => clearInterval(interval);
  });
</script>
```

### $props() - Component Props

```svelte
<script lang="ts">
  // Typed props with defaults
  let { title, count = 0, onUpdate }: {
    title: string;
    count?: number;
    onUpdate?: (value: number) => void;
  } = $props();

  // Or with interface
  interface Props {
    title: string;
    count?: number;
    onUpdate?: (value: number) => void;
  }

  let { title, count = 0, onUpdate }: Props = $props();
</script>
```

---

## Universal Reactivity (Runes in .svelte.ts files)

```typescript
// lib/stores/cart.svelte.ts
export function createCartStore() {
  let items = $state<CartItem[]>([]);

  // Computed
  let total = $derived(
    items.reduce((sum, item) => sum + item.price * item.quantity, 0)
  );

  let count = $derived(
    items.reduce((sum, item) => sum + item.quantity, 0)
  );

  return {
    get items() { return items; },
    get total() { return total; },
    get count() { return count; },

    addItem(item: CartItem) {
      const existing = items.find(i => i.id === item.id);
      if (existing) {
        existing.quantity++;
      } else {
        items.push({ ...item, quantity: 1 });
      }
    },

    removeItem(id: string) {
      items = items.filter(i => i.id !== id);
    },

    clear() {
      items = [];
    }
  };
}

// Export singleton
export const cart = createCartStore();
```

---

## SvelteKit Patterns

### Load Functions

```typescript
// +page.server.ts - Server-only
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, locals }) => {
  // Access server-side resources (database, env vars)
  const post = await db.post.findUnique({
    where: { slug: params.slug }
  });

  if (!post) {
    throw error(404, 'Post not found');
  }

  return { post };
};
```

```typescript
// +page.ts - Runs on both server and client
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, data }) => {
  // Use SvelteKit's fetch for SSR
  const comments = await fetch(`/api/posts/${data.post.id}/comments`).then(r => r.json());

  return {
    ...data,
    comments
  };
};
```

### Form Actions

```typescript
// +page.server.ts
import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { z } from 'zod';

const registerSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  name: z.string().min(2)
});

export const actions: Actions = {
  register: async ({ request, cookies }) => {
    const formData = await request.formData();
    const data = Object.fromEntries(formData);

    // Validate
    const result = registerSchema.safeParse(data);
    if (!result.success) {
      return fail(400, {
        errors: result.error.flatten().fieldErrors
      });
    }

    // Create user
    const user = await createUser(result.data);

    // Set session
    cookies.set('session', user.sessionToken, {
      path: '/',
      httpOnly: true,
      secure: true,
      sameSite: 'strict',
      maxAge: 60 * 60 * 24 * 7
    });

    throw redirect(303, '/dashboard');
  }
};
```

### Progressive Enhancement

```svelte
<!-- +page.svelte -->
<script lang="ts">
  import { enhance } from '$app/forms';
  import type { ActionData } from './$types';

  let { form }: { form: ActionData } = $props();

  let submitting = $state(false);
</script>

<form method="POST" action="?/register" use:enhance={() => {
  submitting = true;

  return async ({ update }) => {
    await update();
    submitting = false;
  };
}}>
  <input name="email" type="email" required />
  {#if form?.errors?.email}
    <span class="error">{form.errors.email}</span>
  {/if}

  <button type="submit" disabled={submitting}>
    {submitting ? 'Submitting...' : 'Register'}
  </button>
</form>
```

---

## Component Patterns

### Snippets (Reusable Template Fragments)

```svelte
<script lang="ts">
  let items = $state([1, 2, 3, 4, 5]);

  // Define snippet
  {#snippet itemCard(item: number)}
    <div class="card">
      <h3>Item {item}</h3>
      <p>Value: {item * 2}</p>
    </div>
  {/snippet}
</script>

<div class="grid">
  {#each items as item}
    {@render itemCard(item)}
  {/each}
</div>
```

### Event Handlers (New Syntax)

```svelte
<script lang="ts">
  let count = $state(0);

  function handleClick() {
    count++;
  }

  function handleInput(event: Event) {
    const target = event.target as HTMLInputElement;
    console.log(target.value);
  }
</script>

<!-- Use onclick, onsubmit, etc. (no on: prefix) -->
<button onclick={handleClick}>
  Click me ({count})
</button>

<input oninput={handleInput} />
```

---

## Performance Patterns

### Lazy Loading

```svelte
<script lang="ts">
  let showChart = $state(false);
  let ChartComponent = $state<any>(null);

  async function loadChart() {
    ChartComponent = (await import('./HeavyChart.svelte')).default;
    showChart = true;
  }
</script>

<button onclick={loadChart}>Load Chart</button>

{#if showChart && ChartComponent}
  <svelte:component this={ChartComponent} />
{/if}
```

### Virtual Lists

```svelte
<script lang="ts">
  import { VirtualList } from 'svelte-virtual';

  let items = $state(Array.from({ length: 10000 }, (_, i) => i));
</script>

<VirtualList items={items} let:item height="400px" itemHeight={50}>
  <div class="item">Item {item}</div>
</VirtualList>
```

---

## Testing Patterns

### Component Test

```typescript
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import Counter from './Counter.svelte';

describe('Counter', () => {
  it('increments on button click', async () => {
    render(Counter);

    const button = screen.getByText('+');
    await fireEvent.click(button);

    expect(screen.getByText(/Count: 1/)).toBeInTheDocument();
  });
});
```

---

## Common Patterns

### Loading States

```svelte
<script lang="ts">
  let { data } = $props();

  let posts = $derived(data.posts);
  let loading = $derived(data.loading);
  let error = $derived(data.error);
</script>

{#if loading}
  <p>Loading...</p>
{:else if error}
  <p class="error">Error: {error.message}</p>
{:else}
  <ul>
    {#each posts as post}
      <li>{post.title}</li>
    {/each}
  </ul>
{/if}
```

### Optimistic UI

```svelte
<script lang="ts">
  import { enhance } from '$app/forms';

  let todos = $state([]);
  let optimisticTodo = $state<Todo | null>(null);

  let displayTodos = $derived(
    optimisticTodo ? [...todos, optimisticTodo] : todos
  );
</script>

<form method="POST" use:enhance={() => {
  optimisticTodo = { id: crypto.randomUUID(), text: 'New todo' };

  return async ({ update }) => {
    await update();
    optimisticTodo = null;
  };
}}>
  <input name="text" />
  <button>Add</button>
</form>

<ul>
  {#each displayTodos as todo}
    <li class:optimistic={todo === optimisticTodo}>
      {todo.text}
    </li>
  {/each}
</ul>
```

---

## Migration from Svelte 4

Key changes:
- `let` -> `$state()`
- `$:` reactive statements -> `$derived()`
- `export let prop` -> `let { prop } = $props()`
- `on:click` -> `onclick`

---

## Resources

- [Svelte 5 Docs](https://svelte.dev/)
- [SvelteKit Docs](https://kit.svelte.dev/)
- [Runes Guide](https://svelte.dev/blog/runes)
- [Svelte Society](https://sveltesociety.dev/)
