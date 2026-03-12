# Angular 21 Best Practices & Patterns

Operational patterns for production-ready Angular with standalone components, signals, and modern APIs (Angular 19–21).

---

## Section Index

| # | Section | Lines | Use When |
|---|---------|-------|----------|
| 1 | [Standalone Components](#standalone-components) | 26–55 | Scaffolding components or migrating from NgModules |
| 2 | [Signals & Reactive State](#signals--reactive-state) | 57–158 | Managing state, derived values, async data loading |
| 3 | [Signal Inputs, Outputs & Model](#signal-inputs-outputs--model) | 160–206 | Defining component APIs with signal-based I/O |
| 4 | [Dependency Injection](#dependency-injection) | 208–256 | Wiring services, HTTP clients, injection tokens |
| 5 | [Modern Template Syntax](#modern-template-syntax) | 258–325 | @if, @for, @switch, @let, @defer |
| 6 | [Forms](#forms) | 327–372 | Typed reactive forms and signal-based form patterns |
| 7 | [Routing & Navigation](#routing--navigation) | 374–424 | Lazy loading, view transitions, functional guards |
| 8 | [Change Detection](#change-detection) | 426–460 | OnPush vs zoneless, performance tuning |
| 9 | [Testing](#testing) | 462–521 | Unit testing components, services, signal inputs |
| 10 | [SSR & Hydration](#ssr--hydration) | 523–547 | Server-side rendering and hydration safety |
| 11 | [Anti-Patterns](#anti-patterns) | 549–592 | Reviewing code for common mistakes |
| 12 | [Migration Guide](#migration-guide) | 594–647 | Upgrading from older Angular patterns |

---

## Standalone Components

All components are standalone by default in Angular 21 (`standalone: true` is implicit).

```typescript
@Component({
  selector: 'app-user-profile',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [DatePipe, RouterLink],
  template: `
    @if (user(); as u) {
      <h2>{{ u.firstName }} {{ u.lastName }}</h2>
      <p>Joined {{ u.createdAt | date:'mediumDate' }}</p>
    } @else {
      <p>Loading profile…</p>
    }
  `,
})
export class UserProfileComponent {
  user = signal<User | null>(null);
  displayName = computed(() => {
    const u = this.user();
    return u ? `${u.firstName} ${u.lastName}` : 'Guest';
  });
}
```

Key rules: import only what the template uses (no `CommonModule`), always use `OnPush`, use signals for all component state.

---

## Signals & Reactive State

### Signals vs RxJS Decision

| Criterion | Signals | RxJS Observables |
|-----------|---------|-----------------|
| Synchronous state | Primary use | Overkill |
| Derived values | `computed()` — glitch-free | `combineLatest` — more boilerplate |
| Async HTTP | `resource()` / `rxResource()` | `HttpClient` returns Observable |
| Event streams (debounce, throttle) | Not designed for this | Core strength |
| Template binding | Direct — `{{ count() }}` | Requires `async` pipe |

**Rule of thumb**: Start with signals. Reach for RxJS when you need stream operators or Observable-based libraries.

### Writable Signals and computed()

```typescript
export class CartComponent {
  items = signal<CartItem[]>([]);
  promoCode = signal<string | null>(null);
  subtotal = computed(() => this.items().reduce((sum, i) => sum + i.price * i.quantity, 0));
  discount = computed(() => this.promoCode() === 'SAVE20' ? this.subtotal() * 0.2 : 0);
  total = computed(() => this.subtotal() - this.discount());

  addItem(item: CartItem) { this.items.update(current => [...current, item]); }
  removeItem(id: string) { this.items.update(current => current.filter(i => i.id !== id)); }
}
```

### linkedSignal — Derived State That Resets

Writable signal whose value resets when a source changes. Use for "selected item in list" patterns.

```typescript
export class ProductListComponent {
  products = signal<Product[]>([]);
  selectedProduct = linkedSignal(() => this.products()[0] ?? null);  // Resets on list change
  selectProduct(p: Product) { this.selectedProduct.set(p); }         // User can override
}
```

**`linkedSignal` vs `computed`**: `computed` = always deterministic. `linkedSignal` = resettable default the user can override.

### effect() — Side Effects Only

```typescript
constructor() {
  effect(() => document.documentElement.setAttribute('data-theme', this.theme()));
}
```

Never use `effect()` for state derivation — use `computed()`. Reserve for DOM manipulation, logging, localStorage sync.

### resource() — Async Data Loading

Signal-native replacement for manual subscribe-in-ngOnInit patterns.

```typescript
export class UserDetailComponent {
  userId = input.required<string>();
  userResource = resource({
    request: () => ({ id: this.userId() }),
    loader: async ({ request, abortSignal }) => {
      const res = await fetch(`/api/users/${request.id}`, { signal: abortSignal });
      if (!res.ok) throw new Error(`Failed to load user ${request.id}`);
      return res.json() as Promise<User>;
    },
  });
}
```

Template:

```html
@switch (userResource.status()) {
  @case ('loading') { <app-skeleton /> }
  @case ('error') { <app-error [message]="userResource.error()?.message" /> }
  @case ('resolved') {
    @let user = userResource.value()!;
    <h2>{{ user.name }}</h2>
  }
}
```

### rxResource() — Observable Integration

Use when the data source is an Observable (e.g., `HttpClient`).

```typescript
export class OrderListComponent {
  private http = inject(HttpClient);
  statusFilter = signal<OrderStatus>('pending');
  ordersResource = rxResource({
    request: () => ({ status: this.statusFilter() }),
    loader: ({ request }) => this.http.get<Order[]>('/api/orders', { params: { status: request.status } }),
  });
}
```

**`resource()` vs `rxResource()`**: `resource()` with `fetch()` for new code. `rxResource()` for existing Observable-based services.

---

## Signal Inputs, Outputs & Model

### input()

```typescript
export class ProductCardComponent {
  product = input.required<Product>();              // Required — enforced at call site
  showActions = input(true);                         // Optional with default
  size = input<'sm' | 'md' | 'lg'>('md', { alias: 'cardSize' });
  price = input.required({ transform: (v: number | string) => Number(v) });
}
```

### output()

```typescript
export class SearchBarComponent {
  query = signal('');
  search = output<string>();
  clear = output<void>();
  onSearch() { this.search.emit(this.query()); }
}
```

### model() — Two-Way Binding

Replaces `@Input() value` + `@Output() valueChange` with a single declaration.

```typescript
export class RatingComponent {
  value = model.required<number>();
  maxStars = input(5);
  setRating(star: number) { this.value.set(star + 1); }
}
// Parent: <app-rating [(value)]="review.rating" [maxStars]="10" />
```

### Migration Table

| Legacy | Modern | Notes |
|--------|--------|-------|
| `@Input() name: string` | `name = input.required<string>()` | Access via `this.name()` |
| `@Input() name = 'default'` | `name = input('default')` | Type inferred |
| `@Output() clicked = new EventEmitter<void>()` | `clicked = output<void>()` | `.emit()` same |
| `@Input() value` + `@Output() valueChange` | `value = model<T>()` | Single declaration |

---

## Dependency Injection

### inject() Function (Preferred)

```typescript
@Injectable({ providedIn: 'root' })
export class OrderService {
  private http = inject(HttpClient);
  private config = inject(APP_CONFIG);
  getOrders(status: OrderStatus) {
    return this.http.get<Order[]>(`${this.config.apiUrl}/orders`, { params: { status } });
  }
}
```

### HttpClient Error Handling

```typescript
@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  get<T>(url: string, params?: Record<string, string>): Observable<T> {
    return this.http.get<T>(url, { params }).pipe(
      retry({ count: 2, delay: 1000 }),
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) inject(Router).navigate(['/login']);
        return throwError(() => ({
          status: error.status,
          message: error.error?.message ?? 'An unexpected error occurred',
        }));
      }),
    );
  }
}
```

### Application Config

```typescript
export const appConfig: ApplicationConfig = {
  providers: [
    { provide: APP_CONFIG, useValue: { apiUrl: '/api', features: { darkMode: true } } },
    provideHttpClient(withInterceptors([authInterceptor])),
    provideRouter(routes, withViewTransitions()),
  ],
};
```

---

## Modern Template Syntax

### @if / @else

```html
@if (userResource.status() === 'loading') {
  <app-skeleton />
} @else if (userResource.value(); as user) {
  <app-user-card [user]="user" />
} @else {
  <p>No user found</p>
}
```

### @for with track

`track` is **required** and replaces the old `trackBy` function. Use a stable ID, never `$index` for dynamic lists.

```html
@for (order of orders(); track order.id) {
  <app-order-row [order]="order" (cancel)="cancelOrder(order.id)" />
} @empty {
  <p>No orders match your filters.</p>
}
```

### @let — Template Variable Binding

Declares a local variable to avoid repeated signal calls.

```html
@let user = currentUser();
@let plan = user?.subscription?.plan ?? 'free';
<h1>Welcome, {{ user?.name ?? 'Guest' }}</h1>
<span class="badge">{{ plan | titlecase }}</span>
```

### @defer — Lazy Loading Template Blocks

Lazy-loads a template section and its component dependencies on demand.

```html
@defer (on viewport) {
  <app-product-reviews [productId]="product().id" />
} @placeholder {
  <div class="h-64 bg-gray-100 animate-pulse"></div>
} @loading (minimum 300ms) {
  <app-spinner />
} @error {
  <p>Failed to load reviews.</p>
}

@defer (on interaction) {
  <app-heavy-chart [data]="analyticsData()" />
} @placeholder {
  <button>Show analytics</button>
}

@defer (on viewport; prefetch on idle) {
  <app-related-products [category]="product().category" />
} @placeholder {
  <app-skeleton-grid [count]="4" />
}
```

**`@defer` vs `loadComponent`**: `@defer` for parts of a page loading progressively. `loadComponent` in routes for page-level code splitting.

---

## Forms

### Typed Reactive Forms

```typescript
interface CheckoutForm {
  email: FormControl<string>;
  postalCode: FormControl<string>;
  agreeToTerms: FormControl<boolean>;
}

@Component({ imports: [ReactiveFormsModule] })
export class CheckoutComponent {
  private fb = inject(FormBuilder);
  form = this.fb.group<CheckoutForm>({
    email: this.fb.nonNullable.control('', [Validators.required, Validators.email]),
    postalCode: this.fb.nonNullable.control('', [Validators.required, Validators.pattern(/^\d{5}(-\d{4})?$/)]),
    agreeToTerms: this.fb.nonNullable.control(false, [Validators.requiredTrue]),
  });

  onSubmit() {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    const value = this.form.getRawValue();  // Fully typed
  }
}
```

### Signal-Based Forms (Simple Cases)

For search/filter inputs where reactive forms add unnecessary overhead:

```typescript
export class QuickSearchComponent {
  query = signal('');
  category = signal<string>('all');
  results = rxResource({
    request: () => ({ q: this.query(), cat: this.category() }),
    loader: ({ request }) => inject(HttpClient).get<SearchResult[]>('/api/search', { params: request }),
  });
}
// Template: <input [value]="query()" (input)="query.set($any($event.target).value)" />
```

**Decision**: `FormBuilder` for complex forms (cross-field validation, dynamic fields, form arrays). Signals for simple search/filter inputs.

---

## Routing & Navigation

### Lazy Loading Routes

```typescript
export const routes: Routes = [
  { path: '', loadComponent: () => import('./home.component').then(m => m.HomeComponent) },
  { path: 'orders', loadComponent: () => import('./order-list.component').then(m => m.OrderListComponent), canActivate: [authGuard] },
  { path: 'admin', loadChildren: () => import('./admin/admin.routes').then(m => m.ADMIN_ROUTES), canMatch: [adminGuard] },
];
```

### Functional Guards and Resolvers

```typescript
export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService), router = inject(Router);
  return auth.isAuthenticated() ? true : router.createUrlTree(['/login']);
};

export const orderResolver: ResolveFn<Order> = (route) =>
  inject(OrderService).getOrder(route.paramMap.get('id')!);
```

### View Transitions API

```typescript
providers: [provideRouter(routes, withViewTransitions())]
```

```css
::view-transition-old(root), ::view-transition-new(root) { animation-duration: 200ms; }
.product-image { view-transition-name: product-hero; }
```

### Navigation Loading Indicator

```typescript
export class AppComponent {
  private router = inject(Router);
  isNavigating = signal(false);
  constructor() {
    this.router.events.pipe(
      filter(e => e instanceof NavigationStart || e instanceof NavigationEnd || e instanceof NavigationCancel),
      takeUntilDestroyed(),
    ).subscribe(e => this.isNavigating.set(e instanceof NavigationStart));
  }
}
```

---

## Change Detection

### OnPush vs Zoneless

| Criterion | OnPush (with Zone.js) | Zoneless |
|-----------|----------------------|----------|
| Migration effort | Low — one line per component | Medium — audit all triggers |
| Third-party compat | Full | Some libraries need manual `markForCheck()` |
| Bundle size | None | Removes ~15 KB (Zone.js) |
| Recommended for | All projects today | New projects, performance-critical apps |

### OnPush (Current Best Practice)

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `@for (item of items(); track item.id) { <app-item-card [item]="item" /> }`,
})
export class ItemListComponent { items = signal<Item[]>([]); }
```

### Zoneless Setup

```typescript
providers: [provideExperimentalZonelessChangeDetection(), provideHttpClient(), provideRouter(routes)]
```

All state changes must flow through signals. Plain property mutations will not trigger re-renders:

```typescript
this.count.update(c => c + 1);  // Works — signal notifies the framework
this.count = this.count + 1;     // Broken in zoneless — no re-render
```

---

## Testing

### Component Test with Signals

```typescript
describe('CartComponent', () => {
  let component: CartComponent;
  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [CartComponent] }).compileComponents();
    component = TestBed.createComponent(CartComponent).componentInstance;
  });

  it('should compute total from items', () => {
    component.items.set([
      { id: '1', name: 'Widget', price: 10, quantity: 2 },
      { id: '2', name: 'Gadget', price: 25, quantity: 1 },
    ]);
    expect(component.total()).toBe(45);
  });
});
```

### Service Test with provideHttpClientTesting

`HttpClientTestingModule` is deprecated. Use `provideHttpClientTesting()`.

```typescript
describe('OrderService', () => {
  let service: OrderService;
  let httpMock: HttpTestingController;
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [OrderService, provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(OrderService);
    httpMock = TestBed.inject(HttpTestingController);
  });
  afterEach(() => httpMock.verify());

  it('should fetch orders by status', () => {
    const mock: Order[] = [{ id: '1', status: 'pending', total: 99.99, createdAt: '2026-01-15' }];
    service.getOrders('pending').subscribe(orders => expect(orders).toEqual(mock));
    httpMock.expectOne(r => r.url === '/api/orders' && r.params.get('status') === 'pending').flush(mock);
  });
});
```

### Testing Signal Inputs

```typescript
it('should display product name', async () => {
  await TestBed.configureTestingModule({ imports: [ProductCardComponent] }).compileComponents();
  const fixture = TestBed.createComponent(ProductCardComponent);
  fixture.componentRef.setInput('product', { id: '1', name: 'Wireless Keyboard', price: 79.99 });
  fixture.detectChanges();
  expect(fixture.nativeElement.textContent).toContain('Wireless Keyboard');
});
```

---

## SSR & Hydration

### Enabling SSR

```typescript
// app.config.server.ts
export const serverConfig = mergeApplicationConfig(appConfig, {
  providers: [provideServerRendering(), provideServerRoutesConfig(serverRoutes)],
});
```

### Hydration Safety Rules

1. **No `window`/`document`/`localStorage` during SSR.** Guard with `isPlatformBrowser(inject(PLATFORM_ID))`.

2. **Use `afterNextRender` for browser-only initialization** (chart libraries, DOM measurement):
```typescript
constructor() { afterNextRender(() => this.initChart()); }
```

3. **Avoid DOM mismatches.** Server HTML must match client initial render. For dynamic content (timestamps, random IDs), use `@defer (on idle)` or `afterNextRender`.

4. **`@defer` blocks are SSR-safe** — Angular renders `@placeholder` on server, hydrates deferred content on client.

---

## Anti-Patterns

**Mixing constructor DI and inject()** — `inject()` is the modern standard; pick one style.
```typescript
// BAD
constructor(private http: HttpClient) { this.router = inject(Router); }
// GOOD
private http = inject(HttpClient);
private router = inject(Router);
```

**Subscribing without cleanup** — leaked subscriptions cause memory leaks on destroyed components.
```typescript
// BAD
ngOnInit() { this.apiService.getData().subscribe(d => this.data.set(d)); }
// GOOD
ngOnInit() { this.apiService.getData().pipe(takeUntilDestroyed(this.destroyRef)).subscribe(d => this.data.set(d)); }
// BETTER
dataResource = rxResource({ loader: () => this.apiService.getData() });
```

**Using `$index` as track** — prevents DOM reuse on reorder, destroys component state.
```html
<!-- BAD --> @for (item of items(); track $index) { ... }
<!-- GOOD --> @for (item of items(); track item.id) { ... }
```

**Calling methods in templates** — runs on every CD cycle. Use `computed()` to memoize.
```html
<!-- BAD --> @for (item of getFilteredItems(); track item.id) { ... }
<!-- GOOD --> @for (item of filteredItems(); track item.id) { ... }
```

**effect() for state derivation** — creates reactive cycles, triggers framework warnings.
```typescript
// BAD
constructor() { effect(() => this.doubled.set(this.count() * 2)); }
// GOOD
doubled = computed(() => this.count() * 2);
```

**Importing CommonModule** — `@if`/`@for`/`@switch` replace structural directives. Import individual pipes only.

---

## Migration Guide

### NgModules to Standalone

```typescript
// BEFORE
@NgModule({ declarations: [MyComponent], imports: [CommonModule, FormsModule] })
export class MyModule {}
// AFTER
@Component({ imports: [FormsModule, DatePipe], template: `...` })
export class MyComponent {}
```

### @Input/@Output to Signal APIs

```typescript
// BEFORE
@Input() title = '';  @Output() titleChange = new EventEmitter<string>();
// AFTER
title = model('');  // [(title)]="parentTitle"
```

### HttpClientTestingModule to provideHttpClientTesting

```typescript
// BEFORE (deprecated)
TestBed.configureTestingModule({ imports: [HttpClientTestingModule] });
// AFTER
TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
```

### *ngIf/*ngFor to Modern Control Flow

```html
<!-- BEFORE -->
<div *ngIf="user$ | async as user">{{ user.name }}</div>
<li *ngFor="let item of items; trackBy: trackById">{{ item.name }}</li>
<!-- AFTER -->
@if (user(); as user) { <div>{{ user.name }}</div> }
@for (item of items(); track item.id) { <li>{{ item.name }}</li> }
```

### Manual Subscribe to resource()

```typescript
// BEFORE
ngOnInit() { this.http.get<User[]>('/api/users').pipe(takeUntilDestroyed(this.destroyRef))
  .subscribe({ next: u => { this.users = u; this.loading = false; }, error: e => { this.error = e; } }); }
// AFTER
usersResource = rxResource({ loader: () => this.http.get<User[]>('/api/users') });
// Access: usersResource.value(), usersResource.status(), usersResource.error()
```

---

## Performance Checklist

- [ ] `ChangeDetectionStrategy.OnPush` on every component
- [ ] Stable `track` in all `@for` loops (never `$index` for dynamic lists)
- [ ] Route-level code splitting with `loadComponent` / `loadChildren`
- [ ] `@defer` for below-the-fold and heavy components
- [ ] `computed()` for all derived values (no method calls in templates)
- [ ] `resource()` / `rxResource()` instead of manual subscribe+loading+error
- [ ] `takeUntilDestroyed()` on any remaining RxJS subscriptions
- [ ] Virtual scrolling (`@angular/cdk/scrolling`) for lists over 100 items
- [ ] SSR hydration verified — no `window`/`document` access in constructors
- [ ] Zoneless evaluated for new projects (removes Zone.js from bundle)

---

## Cross-References

- [state-management-patterns.md](state-management-patterns.md) — Server state vs client state decision framework
- [performance-optimization.md](performance-optimization.md) — Bundle analysis and render optimization
- [testing-frontend-patterns.md](testing-frontend-patterns.md) — Testing patterns across frameworks

---

## Resources

- [Angular Docs](https://angular.dev/)
- [Angular Signals](https://angular.dev/guide/signals)
- [Angular SSR](https://angular.dev/guide/ssr)
- [RxJS](https://rxjs.dev/)
- [Angular Material](https://material.angular.dev/)
