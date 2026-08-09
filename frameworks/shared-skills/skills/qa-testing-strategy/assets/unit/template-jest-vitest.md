# Unit Testing Template: Jest / Vitest

Use this template for writing unit tests with Jest or Vitest for JavaScript/TypeScript projects.

## Framework Selection

**Jest** - Best for:
- React applications (built-in React Testing Library support)
- Projects already using Jest (migration cost)
- Teams needing extensive mocking capabilities
- Zero-config setup preference

**Vitest** - Best for:
- Vite-based projects (instant compatibility)
- Projects prioritizing speed (native ESM, parallel execution)
- TypeScript/JSX without transpilation
- Modern tooling (watch mode, UI mode)

## Test File Structure

### Basic Test Structure (AAA Pattern)

```typescript
// user.service.test.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest' // or '@jest/globals'
import { UserService } from './user.service'
import { DatabaseMock } from '../__mocks__/database.mock'

describe('UserService', () => {
  let service: UserService
  let dbMock: DatabaseMock

  beforeEach(() => {
    // Arrange: Setup for each test
    dbMock = new DatabaseMock()
    service = new UserService(dbMock)
  })

  afterEach(() => {
    // Cleanup after each test
    dbMock.clear()
  })

  describe('createUser', () => {
    it('should hash password before saving', async () => {
      // Arrange
      const userData = {
        email: 'test@example.com',
        password: 'PlainPassword123',
        name: 'Test User'
      }

      // Act
      const user = await service.createUser(userData)

      // Assert
      expect(user.password).not.toBe('PlainPassword123')
      expect(user.password).toMatch(/^\$2[aby]\$.{56}$/) // bcrypt pattern
      expect(user.email).toBe('test@example.com')
    })

    it('should throw error for duplicate email', async () => {
      // Arrange
      const userData = { email: 'test@example.com', password: 'pass', name: 'Test' }
      await service.createUser(userData)

      // Act & Assert
      await expect(service.createUser(userData))
        .rejects
        .toThrow('Email already exists')
    })

    it('should validate email format', async () => {
      // Arrange
      const invalidData = { email: 'invalid-email', password: 'pass', name: 'Test' }

      // Act & Assert
      await expect(service.createUser(invalidData))
        .rejects
        .toThrow('Invalid email format')
    })
  })

  describe('findUserById', () => {
    it('should return user when exists', async () => {
      // Arrange
      const user = await service.createUser({
        email: 'test@example.com',
        password: 'pass',
        name: 'Test User'
      })

      // Act
      const found = await service.findUserById(user.id)

      // Assert
      expect(found).toBeDefined()
      expect(found?.id).toBe(user.id)
      expect(found?.email).toBe('test@example.com')
    })

    it('should return null when user not found', async () => {
      // Act
      const found = await service.findUserById('non-existent-id')

      // Assert
      expect(found).toBeNull()
    })
  })
})
```

## Testing Edge Cases

```typescript
describe('Edge Cases', () => {
  describe('boundary values', () => {
    it('should handle minimum age', () => {
      expect(service.isAdult(18)).toBe(true)
      expect(service.isAdult(17)).toBe(false)
    })

    it('should handle maximum string length', () => {
      const maxName = 'a'.repeat(100)
      const tooLong = 'a'.repeat(101)

      expect(service.validateName(maxName)).toBe(true)
      expect(() => service.validateName(tooLong)).toThrow('Name too long')
    })
  })

  describe('null and undefined handling', () => {
    it('should handle null input', () => {
      expect(() => service.processData(null)).toThrow('Invalid input')
    })

    it('should handle undefined input', () => {
      expect(() => service.processData(undefined)).toThrow('Invalid input')
    })

    it('should handle empty string', () => {
      expect(() => service.processData('')).toThrow('Invalid input')
    })
  })

  describe('special characters', () => {
    it('should escape SQL injection attempts', () => {
      const malicious = "'; DROP TABLE users; --"
      expect(() => service.searchUsers(malicious)).not.toThrow()
    })

    it('should sanitize XSS attempts', () => {
      const xss = '<script>alert("XSS")</script>'
      const sanitized = service.sanitizeInput(xss)
      expect(sanitized).not.toContain('<script>')
    })
  })
})
```

## Mocking Dependencies

### Mock Functions

```typescript
import { vi } from 'vitest' // or jest.fn()

describe('Mocking', () => {
  it('should call external service', async () => {
    // Arrange
    const emailService = {
      send: vi.fn().mockResolvedValue({ success: true })
    }
    const service = new UserService(db, emailService)

    // Act
    await service.createUser({ email: 'test@example.com', password: 'pass', name: 'Test' })

    // Assert
    expect(emailService.send).toHaveBeenCalledTimes(1)
    expect(emailService.send).toHaveBeenCalledWith({
      to: 'test@example.com',
      subject: 'Welcome',
      template: 'welcome'
    })
  })

  it('should handle service failure gracefully', async () => {
    // Arrange
    const emailService = {
      send: vi.fn().mockRejectedValue(new Error('Email service down'))
    }
    const service = new UserService(db, emailService)

    // Act & Assert
    await expect(service.createUser({ email: 'test@example.com', password: 'pass', name: 'Test' }))
      .rejects
      .toThrow('Failed to send welcome email')
  })
})
```

### Mock Modules

```typescript
// Vitest module mocking
vi.mock('../services/payment.service', () => ({
  PaymentService: vi.fn().mockImplementation(() => ({
    processPayment: vi.fn().mockResolvedValue({ transactionId: 'TX123' })
  }))
}))

// Jest module mocking
jest.mock('../services/payment.service', () => ({
  PaymentService: jest.fn().mockImplementation(() => ({
    processPayment: jest.fn().mockResolvedValue({ transactionId: 'TX123' })
  }))
}))
```

## Snapshot Testing

```typescript
describe('Snapshot Testing', () => {
  it('should match user profile snapshot', () => {
    const user = service.getUserProfile('user-123')
    expect(user).toMatchSnapshot()
  })

  it('should match inline snapshot', () => {
    const config = service.getConfig()
    expect(config).toMatchInlineSnapshot(`
      {
        "apiUrl": "https://api.example.com",
        "timeout": 5000,
        "retries": 3
      }
    `)
  })
})
```

## Test Data Factories

```typescript
// test-factories/user.factory.ts
import { faker } from '@faker-js/faker'

export class UserFactory {
  static create(overrides: Partial<User> = {}): User {
    return {
      id: faker.string.uuid(),
      email: faker.internet.email(),
      name: faker.person.fullName(),
      age: faker.number.int({ min: 18, max: 80 }),
      createdAt: faker.date.past(),
      ...overrides
    }
  }

  static createMany(count: number, overrides: Partial<User> = {}): User[] {
    return Array.from({ length: count }, () => this.create(overrides))
  }

  static createAdmin(): User {
    return this.create({ role: 'admin', permissions: ['read', 'write', 'delete'] })
  }
}

// Usage in tests
describe('UserService', () => {
  it('should process batch of users', () => {
    const users = UserFactory.createMany(10)
    const result = service.processBatch(users)
    expect(result.processed).toBe(10)
  })

  it('should grant admin access', () => {
    const admin = UserFactory.createAdmin()
    expect(service.hasPermission(admin, 'delete')).toBe(true)
  })
})
```

## Async Testing

```typescript
describe('Async Operations', () => {
  it('should resolve promise', async () => {
    const result = await service.fetchData()
    expect(result).toBeDefined()
  })

  it('should reject promise', async () => {
    await expect(service.fetchInvalidData()).rejects.toThrow('Not found')
  })

  it('should timeout after delay', async () => {
    vi.useFakeTimers()
    const promise = service.delayedOperation()
    vi.advanceTimersByTime(5000)
    await expect(promise).resolves.toBe('completed')
    vi.useRealTimers()
  })
})
```

## Coverage Configuration

### Vitest (vite.config.ts)

```typescript
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    coverage: {
      provider: 'v8', // or 'istanbul'
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        '**/node_modules/**',
        '**/dist/**',
        '**/*.test.ts',
        '**/*.config.ts',
        '**/types/**'
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80
      }
    }
  }
})
```

### Jest (jest.config.js)

```javascript
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.test.{ts,tsx}',
    '!src/**/__mocks__/**'
  ],
  coverageThresholds: {
    global: {
      lines: 80,
      functions: 80,
      branches: 80,
      statements: 80
    },
    './src/services/': {
      lines: 90,
      functions: 90,
      branches: 90,
      statements: 90
    }
  },
  coverageReporters: ['text', 'lcov', 'html']
}
```

## Best Practices Checklist

- [ ] Use descriptive test names (what is being tested + expected outcome)
- [ ] Follow AAA pattern (Arrange, Act, Assert)
- [ ] Test one thing per test
- [ ] Use factories for test data (avoid magic values)
- [ ] Mock external dependencies (APIs, databases)
- [ ] Test edge cases and error conditions
- [ ] Keep tests independent (no shared state)
- [ ] Use beforeEach/afterEach for setup/cleanup
- [ ] Aim for 80%+ coverage on business logic
- [ ] Run tests in parallel where possible
- [ ] Use snapshot testing sparingly (for stable output only)

## Common Pitfalls

[FAIL] **Testing implementation details**:
```typescript
// Bad
expect(service.internalHelperMethod()).toBe(true)

// Good
expect(service.publicMethod()).toBe(expectedResult)
```

[FAIL] **Shared mutable state**:
```typescript
// Bad
let sharedUser: User
beforeAll(() => {
  sharedUser = createUser() // Shared across tests
})

// Good
let user: User
beforeEach(() => {
  user = createUser() // Fresh for each test
})
```

[FAIL] **Not cleaning up after tests**:
```typescript
// Bad
afterEach(() => {
  // No cleanup
})

// Good
afterEach(() => {
  vi.clearAllMocks()
  dbMock.clear()
})
```

## Running Tests

```bash
# Vitest
npm run test              # Run once
npm run test:watch        # Watch mode
npm run test:ui           # UI mode
npm run test:coverage     # With coverage

# Jest
npm test                  # Run once
npm test -- --watch       # Watch mode
npm test -- --coverage    # With coverage
npm test -- UserService   # Run specific file
```

## Related Resources

See [../../references/comprehensive-testing-guide.md](../../references/comprehensive-testing-guide.md) for complete testing guide across all layers.
