# Angular 21 Standalone Components Starter Template

Production-ready template for building modern Angular applications with standalone components, zoneless change detection, signals, and TypeScript.

---

## Overview

This template provides a modern Angular 21 setup with:
- **Angular 21** - Latest Angular with zoneless change detection, esbuild, and standalone components
- **Signals** - Angular's fine-grained reactivity system
- **TypeScript** - Strict type safety
- **Standalone Components** - No NgModules required
- **Angular Material** or **PrimeNG** - UI component libraries
- **TailwindCSS** (optional) - Utility-first styling
- **RxJS** - Reactive programming
- **Jasmine + Karma** or **Jest** - Unit testing
- **Cypress** or **Playwright** - E2E testing

---

## Project Setup

### Initialize Project

```bash
# Install Angular CLI
npm install -g @angular/cli@latest

# Create new project (standalone components by default)
ng new my-app --routing --style=scss --standalone

cd my-app

# Add Angular Material
ng add @angular/material

# OR add PrimeNG
npm install primeng primeicons

# Add TailwindCSS (optional)
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init

# Add testing
# Jest (alternative to Jasmine)
ng add @briebug/jest-schematic

# Playwright for E2E
npm init playwright@latest
```

---

## Project Structure

```
my-app/
|-- src/
|   |-- app/
|   |   |-- app.component.ts         # Root component
|   |   |-- app.config.ts            # Application configuration
|   |   |-- app.routes.ts            # Route configuration
|   |   |-- core/                    # Core services (singleton)
|   |   |   |-- services/
|   |   |   |   |-- auth.service.ts
|   |   |   |   `-- api.service.ts
|   |   |   |-- guards/
|   |   |   |   `-- auth.guard.ts
|   |   |   `-- interceptors/
|   |   |       `-- auth.interceptor.ts
|   |   |-- shared/                  # Shared components/utilities
|   |   |   |-- components/
|   |   |   |   |-- button/
|   |   |   |   |   |-- button.component.ts
|   |   |   |   |   |-- button.component.html
|   |   |   |   |   |-- button.component.scss
|   |   |   |   |   `-- button.component.spec.ts
|   |   |   |   `-- header/
|   |   |   |-- directives/
|   |   |   |-- pipes/
|   |   |   `-- models/
|   |   |-- features/                # Feature modules
|   |   |   |-- auth/
|   |   |   |   |-- login/
|   |   |   |   |   |-- login.component.ts
|   |   |   |   |   `-- login.component.html
|   |   |   |   `-- register/
|   |   |   |-- dashboard/
|   |   |   `-- blog/
|   |   |       |-- blog-list/
|   |   |       |-- blog-detail/
|   |   |       `-- blog.service.ts
|   |   `-- layout/                  # Layout components
|   |       |-- main-layout/
|   |       `-- auth-layout/
|   |-- assets/                      # Static files
|   |-- environments/                # Environment configs
|   |   |-- environment.ts
|   |   `-- environment.prod.ts
|   |-- styles.scss                  # Global styles
|   |-- index.html
|   `-- main.ts                      # Bootstrap file
|-- angular.json                     # Angular CLI config
|-- tsconfig.json                    # TypeScript config
|-- tailwind.config.js               # Tailwind config (if used)
`-- package.json
```

---

## Configuration Files

### main.ts (Bootstrap)

```typescript
// src/main.ts
import { bootstrapApplication } from '@angular/platform-browser';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';
import { AppComponent } from './app/app.component';
import { routes } from './app/app.routes';
import { authInterceptor } from './app/core/interceptors/auth.interceptor';

bootstrapApplication(AppComponent, {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideAnimations(),
  ],
}).catch((err) => console.error(err));
```

### app.config.ts

```typescript
// src/app/app.config.ts
import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';
import { routes } from './app.routes';
import { authInterceptor } from './core/interceptors/auth.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideAnimations(),
  ],
};
```

### app.routes.ts

```typescript
// src/app/app.routes.ts
import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./features/home/home.component').then((m) => m.HomeComponent),
  },
  {
    path: 'login',
    loadComponent: () =>
      import('./features/auth/login/login.component').then(
        (m) => m.LoginComponent
      ),
  },
  {
    path: 'dashboard',
    loadComponent: () =>
      import('./features/dashboard/dashboard.component').then(
        (m) => m.DashboardComponent
      ),
    canActivate: [authGuard],
  },
  {
    path: 'blog',
    loadChildren: () =>
      import('./features/blog/blog.routes').then((m) => m.BLOG_ROUTES),
  },
  {
    path: '**',
    loadComponent: () =>
      import('./shared/components/not-found/not-found.component').then(
        (m) => m.NotFoundComponent
      ),
  },
];
```

### tsconfig.json

```json
{
  "compileOnSave": false,
  "compilerOptions": {
    "baseUrl": "./",
    "outDir": "./dist/out-tsc",
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "sourceMap": true,
    "declaration": false,
    "downlevelIteration": true,
    "experimentalDecorators": true,
    "moduleResolution": "node",
    "importHelpers": true,
    "target": "ES2022",
    "module": "ES2022",
    "useDefineForClassFields": false,
    "lib": ["ES2022", "dom"],
    "paths": {
      "@app/*": ["src/app/*"],
      "@core/*": ["src/app/core/*"],
      "@shared/*": ["src/app/shared/*"],
      "@features/*": ["src/app/features/*"]
    }
  },
  "angularCompilerOptions": {
    "enableI18nLegacyMessageIdFormat": false,
    "strictInjectionParameters": true,
    "strictInputAccessModifiers": true,
    "strictTemplates": true
  }
}
```

---

## Common Patterns

### Standalone Component with Signals

```typescript
// src/app/features/counter/counter.component.ts
import { Component, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-counter',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="counter">
      <h2>Counter: {{ count() }}</h2>
      <p>Double: {{ doubleCount() }}</p>
      <button (click)="increment()">+</button>
      <button (click)="decrement()">-</button>
      <button (click)="reset()">Reset</button>
    </div>
  `,
  styles: [`
    .counter {
      text-align: center;
      padding: 2rem;
    }
    button {
      margin: 0 0.5rem;
      padding: 0.5rem 1rem;
    }
  `],
})
export class CounterComponent {
  // Signal for reactive state
  count = signal(0);

  // Computed signal (derived state)
  doubleCount = computed(() => this.count() * 2);

  increment() {
    this.count.update(value => value + 1);
  }

  decrement() {
    this.count.update(value => value - 1);
  }

  reset() {
    this.count.set(0);
  }
}
```

### Component with HTTP Service

```typescript
// src/app/features/blog/blog-list/blog-list.component.ts
import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BlogService } from '../blog.service';
import { Blog } from '@shared/models/blog.model';

@Component({
  selector: 'app-blog-list',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="blog-list">
      <h1>Blog Posts</h1>

      @if (loading()) {
        <p>Loading...</p>
      }

      @if (error()) {
        <p class="error">{{ error() }}</p>
      }

      @if (blogs().length > 0) {
        <div class="grid">
          @for (blog of blogs(); track blog.id) {
            <article class="blog-card">
              <h2>{{ blog.title }}</h2>
              <p>{{ blog.excerpt }}</p>
              <a [routerLink]="['/blog', blog.id]">Read more</a>
            </article>
          }
        </div>
      }
    </div>
  `,
  styles: [`
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 2rem;
    }
    .blog-card {
      padding: 1.5rem;
      border: 1px solid #ddd;
      border-radius: 8px;
    }
  `],
})
export class BlogListComponent implements OnInit {
  blogs = signal<Blog[]>([]);
  loading = signal(false);
  error = signal<string | null>(null);

  constructor(private blogService: BlogService) {}

  ngOnInit() {
    this.loadBlogs();
  }

  loadBlogs() {
    this.loading.set(true);
    this.blogService.getBlogs().subscribe({
      next: (data) => {
        this.blogs.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('Failed to load blogs');
        this.loading.set(false);
      },
    });
  }
}
```

### Service with Signals

```typescript
// src/app/core/services/auth.service.ts
import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { User } from '@shared/models/user.model';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly API_URL = 'https://api.example.com';

  // Signals for reactive state
  private userSignal = signal<User | null>(null);
  private tokenSignal = signal<string | null>(null);

  // Computed signals
  user = this.userSignal.asReadonly();
  isAuthenticated = computed(() => !!this.userSignal());

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    this.loadFromStorage();
  }

  login(credentials: { email: string; password: string }): Observable<any> {
    return this.http.post(`${this.API_URL}/auth/login`, credentials).pipe(
      tap((response: any) => {
        this.userSignal.set(response.user);
        this.tokenSignal.set(response.token);
        localStorage.setItem('token', response.token);
      })
    );
  }

  logout() {
    this.userSignal.set(null);
    this.tokenSignal.set(null);
    localStorage.removeItem('token');
    this.router.navigate(['/login']);
  }

  private loadFromStorage() {
    const token = localStorage.getItem('token');
    if (token) {
      this.tokenSignal.set(token);
      this.fetchCurrentUser().subscribe();
    }
  }

  private fetchCurrentUser(): Observable<User> {
    return this.http.get<User>(`${this.API_URL}/auth/me`).pipe(
      tap((user) => this.userSignal.set(user))
    );
  }
}
```

### Route Guard (Functional)

```typescript
// src/app/core/guards/auth.guard.ts
import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '@core/services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }

  // Redirect to login
  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url },
  });
};
```

### HTTP Interceptor (Functional)

```typescript
// src/app/core/interceptors/auth.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '@core/services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = localStorage.getItem('token');

  if (token) {
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  return next(req);
};
```

### Reactive Form with Validation

```typescript
// src/app/features/auth/login/login.component.ts
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '@core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="login-container">
      <h1>Login</h1>
      <form [formGroup]="loginForm" (ngSubmit)="onSubmit()">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            type="email"
            formControlName="email"
            [class.error]="email?.invalid && email?.touched"
          />
          @if (email?.invalid && email?.touched) {
            <span class="error-message">
              @if (email?.errors?.['required']) {
                Email is required
              }
              @if (email?.errors?.['email']) {
                Invalid email format
              }
            </span>
          }
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            type="password"
            formControlName="password"
            [class.error]="password?.invalid && password?.touched"
          />
          @if (password?.invalid && password?.touched) {
            <span class="error-message">
              Password must be at least 8 characters
            </span>
          }
        </div>

        <button type="submit" [disabled]="loginForm.invalid || submitting">
          {{ submitting ? 'Logging in...' : 'Login' }}
        </button>

        @if (error) {
          <p class="error">{{ error }}</p>
        }
      </form>
    </div>
  `,
  styles: [`
    .form-group {
      margin-bottom: 1rem;
    }
    input.error {
      border-color: red;
    }
    .error-message {
      color: red;
      font-size: 0.875rem;
    }
  `],
})
export class LoginComponent {
  loginForm = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
  });

  submitting = false;
  error: string | null = null;

  // Getters for form controls
  get email() {
    return this.loginForm.get('email');
  }

  get password() {
    return this.loginForm.get('password');
  }

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmit() {
    if (this.loginForm.invalid) return;

    this.submitting = true;
    this.error = null;

    this.authService.login(this.loginForm.getRawValue()).subscribe({
      next: () => {
        this.submitting = false;
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.submitting = false;
        this.error = 'Login failed. Please check your credentials.';
      },
    });
  }
}
```

### Custom Pipe

```typescript
// src/app/shared/pipes/date-ago.pipe.ts
import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'dateAgo',
  standalone: true,
})
export class DateAgoPipe implements PipeTransform {
  transform(value: Date | string): string {
    const date = new Date(value);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)} days ago`;

    return date.toLocaleDateString();
  }
}
```

---

## Testing

### Component Test (Jasmine)

```typescript
// src/app/features/counter/counter.component.spec.ts
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CounterComponent } from './counter.component';

describe('CounterComponent', () => {
  let component: CounterComponent;
  let fixture: ComponentFixture<CounterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CounterComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CounterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should increment count', () => {
    component.increment();
    expect(component.count()).toBe(1);
  });

  it('should decrement count', () => {
    component.decrement();
    expect(component.count()).toBe(-1);
  });

  it('should reset count', () => {
    component.count.set(5);
    component.reset();
    expect(component.count()).toBe(0);
  });

  it('should compute double count', () => {
    component.count.set(5);
    expect(component.doubleCount()).toBe(10);
  });
});
```

### Service Test

```typescript
// src/app/core/services/auth.service.spec.ts
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { AuthService } from './auth.service';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [AuthService],
    });
    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should login and set user', () => {
    const mockResponse = {
      user: { id: 1, email: 'test@example.com' },
      token: 'fake-token',
    };

    service.login({ email: 'test@example.com', password: 'password' }).subscribe();

    const req = httpMock.expectOne('https://api.example.com/auth/login');
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);

    expect(service.user()).toEqual(mockResponse.user);
    expect(service.isAuthenticated()).toBe(true);
  });
});
```

---

## Production Checklist

### Performance
- [ ] Enable production mode in `environment.prod.ts`
- [ ] Use `OnPush` change detection for performance-critical components
- [ ] Lazy load feature modules with `loadChildren`
- [ ] Optimize bundle size with tree-shaking
- [ ] Use trackBy in `@for` loops

### Build Configuration
- [ ] Run `ng build --configuration production`
- [ ] Enable AOT compilation (enabled by default)
- [ ] Enable build optimization
- [ ] Configure budget limits in `angular.json`

### Security
- [ ] Sanitize user input to prevent XSS
- [ ] Use HTTP interceptors for auth tokens
- [ ] Implement CSRF protection
- [ ] Configure Content Security Policy
- [ ] Use environment variables for sensitive data

### Testing
- [ ] Maintain 80%+ test coverage
- [ ] Run E2E tests before deployment
- [ ] Test accessibility with axe-core

---

## Useful Commands

```bash
# Development
ng serve                         # Start dev server (localhost:4200)
ng serve --open                  # Start and open browser

# Generate
ng generate component my-component --standalone
ng generate service my-service
ng generate guard my-guard --functional
ng generate pipe my-pipe --standalone

# Build
ng build                         # Development build
ng build --configuration production  # Production build

# Testing
ng test                          # Run unit tests
ng e2e                           # Run E2E tests

# Linting
ng lint                          # Run ESLint
```

---

## Additional Resources

- [Angular Documentation](https://angular.dev/)
- [Angular Signals Guide](https://angular.dev/guide/signals)
- [Angular Material](https://material.angular.io/)
- [PrimeNG](https://primeng.org/)
- [RxJS Documentation](https://rxjs.dev/)

---

## Notes

- **Standalone components are the default** in Angular 21
- **Zoneless change detection is the default** in Angular 21 - no more Zone.js overhead
- **Esbuild is the default bundler** - faster builds than Webpack
- **Signals provide fine-grained reactivity** - use for local state
- **Use `@if`, `@for`, `@switch`** instead of `*ngIf`, `*ngFor`, `*ngSwitch`
- **Functional guards and interceptors** are the modern approach
- **Lazy loading with `loadComponent`** for better performance
