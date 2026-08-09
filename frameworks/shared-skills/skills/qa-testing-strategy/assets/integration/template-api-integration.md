# Integration Testing Template: API Integration Tests

Use this template for testing API integrations, service communication, and database interactions.

## Framework Selection

**Supertest + Jest/Vitest** - Best for:
- REST API testing with Express/Fastify
- HTTP request/response validation
- Middleware testing
- Integration with existing Jest/Vitest setup

**Playwright/Puppeteer** - Best for:
- Full-stack integration tests
- Browser-based API interactions
- Testing with real authentication flows
- Visual verification alongside API calls

**Testcontainers** - Best for:
- Testing with real databases (PostgreSQL, MongoDB, Redis)
- Message queue integration (RabbitMQ, Kafka)
- Isolated test environments
- CI/CD compatibility

## Basic API Integration Test

```typescript
// api/users.integration.test.ts
import request from 'supertest'
import { app } from '../app'
import { db } from '../database'
import { UserFactory } from '../test-factories/user.factory'

describe('User API Integration', () => {
  beforeAll(async () => {
    // Setup: Start test database
    await db.connect()
    await db.migrate.latest()
  })

  afterAll(async () => {
    // Teardown: Close connections
    await db.destroy()
  })

  beforeEach(async () => {
    // Reset database state before each test
    await db('users').truncate()
  })

  describe('POST /api/users', () => {
    it('should create user and return 201', async () => {
      // Arrange
      const userData = {
        email: 'test@example.com',
        password: 'SecurePass123!',
        name: 'Test User'
      }

      // Act
      const response = await request(app)
        .post('/api/users')
        .send(userData)
        .expect('Content-Type', /json/)
        .expect(201)

      // Assert
      expect(response.body).toMatchObject({
        id: expect.any(String),
        email: 'test@example.com',
        name: 'Test User'
      })
      expect(response.body.password).toBeUndefined() // Never return password

      // Verify database state
      const dbUser = await db('users').where({ id: response.body.id }).first()
      expect(dbUser).toBeDefined()
      expect(dbUser.email).toBe('test@example.com')
    })

    it('should return 409 for duplicate email', async () => {
      // Arrange
      const userData = { email: 'test@example.com', password: 'pass', name: 'Test' }
      await request(app).post('/api/users').send(userData)

      // Act
      const response = await request(app)
        .post('/api/users')
        .send(userData)
        .expect(409)

      // Assert
      expect(response.body.error).toBe('Email already exists')
    })

    it('should validate required fields', async () => {
      // Act
      const response = await request(app)
        .post('/api/users')
        .send({ email: 'test@example.com' }) // Missing password and name
        .expect(400)

      // Assert
      expect(response.body.errors).toContainEqual(
        expect.objectContaining({ field: 'password', message: expect.any(String) })
      )
      expect(response.body.errors).toContainEqual(
        expect.objectContaining({ field: 'name', message: expect.any(String) })
      )
    })
  })

  describe('GET /api/users/:id', () => {
    it('should return user by id', async () => {
      // Arrange
      const user = await UserFactory.createInDb(db)

      // Act
      const response = await request(app)
        .get(`/api/users/${user.id}`)
        .expect(200)

      // Assert
      expect(response.body).toMatchObject({
        id: user.id,
        email: user.email,
        name: user.name
      })
    })

    it('should return 404 for non-existent user', async () => {
      // Act
      const response = await request(app)
        .get('/api/users/non-existent-id')
        .expect(404)

      // Assert
      expect(response.body.error).toBe('User not found')
    })
  })

  describe('PUT /api/users/:id', () => {
    it('should update user', async () => {
      // Arrange
      const user = await UserFactory.createInDb(db)
      const updates = { name: 'Updated Name' }

      // Act
      const response = await request(app)
        .put(`/api/users/${user.id}`)
        .send(updates)
        .expect(200)

      // Assert
      expect(response.body.name).toBe('Updated Name')

      // Verify database state
      const dbUser = await db('users').where({ id: user.id }).first()
      expect(dbUser.name).toBe('Updated Name')
    })

    it('should not allow email update', async () => {
      // Arrange
      const user = await UserFactory.createInDb(db)

      // Act
      const response = await request(app)
        .put(`/api/users/${user.id}`)
        .send({ email: 'newemail@example.com' })
        .expect(400)

      // Assert
      expect(response.body.error).toContain('cannot change email')
    })
  })

  describe('DELETE /api/users/:id', () => {
    it('should soft delete user', async () => {
      // Arrange
      const user = await UserFactory.createInDb(db)

      // Act
      await request(app)
        .delete(`/api/users/${user.id}`)
        .expect(204)

      // Assert - User should still exist but be marked deleted
      const dbUser = await db('users').where({ id: user.id }).first()
      expect(dbUser.deleted_at).toBeDefined()
    })
  })
})
```

## Authentication Integration Tests

```typescript
describe('Authentication Flow', () => {
  let authToken: string

  describe('POST /api/auth/login', () => {
    it('should authenticate user and return token', async () => {
      // Arrange
      const user = await UserFactory.createInDb(db, { password: 'TestPass123!' })

      // Act
      const response = await request(app)
        .post('/api/auth/login')
        .send({ email: user.email, password: 'TestPass123!' })
        .expect(200)

      // Assert
      expect(response.body).toMatchObject({
        token: expect.any(String),
        user: {
          id: user.id,
          email: user.email
        }
      })

      authToken = response.body.token
    })

    it('should reject invalid credentials', async () => {
      // Arrange
      const user = await UserFactory.createInDb(db, { password: 'TestPass123!' })

      // Act
      const response = await request(app)
        .post('/api/auth/login')
        .send({ email: user.email, password: 'WrongPassword' })
        .expect(401)

      // Assert
      expect(response.body.error).toBe('Invalid credentials')
    })

    it('should lock account after 5 failed attempts', async () => {
      // Arrange
      const user = await UserFactory.createInDb(db, { password: 'TestPass123!' })

      // Act - 5 failed attempts
      for (let i = 0; i < 5; i++) {
        await request(app)
          .post('/api/auth/login')
          .send({ email: user.email, password: 'WrongPassword' })
      }

      // Act - 6th attempt should be locked
      const response = await request(app)
        .post('/api/auth/login')
        .send({ email: user.email, password: 'TestPass123!' }) // Even correct password
        .expect(423)

      // Assert
      expect(response.body.error).toContain('Account locked')
    })
  })

  describe('Protected Routes', () => {
    it('should allow access with valid token', async () => {
      // Arrange
      const user = await UserFactory.createInDb(db)
      const token = await generateAuthToken(user)

      // Act
      const response = await request(app)
        .get('/api/users/me')
        .set('Authorization', `Bearer ${token}`)
        .expect(200)

      // Assert
      expect(response.body.id).toBe(user.id)
    })

    it('should reject invalid token', async () => {
      // Act
      const response = await request(app)
        .get('/api/users/me')
        .set('Authorization', 'Bearer invalid-token')
        .expect(401)

      // Assert
      expect(response.body.error).toBe('Invalid token')
    })

    it('should reject expired token', async () => {
      // Arrange
      const user = await UserFactory.createInDb(db)
      const expiredToken = await generateAuthToken(user, { expiresIn: '-1h' })

      // Act
      const response = await request(app)
        .get('/api/users/me')
        .set('Authorization', `Bearer ${expiredToken}`)
        .expect(401)

      // Assert
      expect(response.body.error).toContain('expired')
    })
  })
})
```

## Database Integration Tests

```typescript
import { PostgreSqlContainer } from '@testcontainers/postgresql'

describe('Database Integration', () => {
  let container: PostgreSqlContainer
  let testDb: Database

  beforeAll(async () => {
    // Start PostgreSQL container
    container = await new PostgreSqlContainer('postgres:15')
      .withDatabase('test_db')
      .withUsername('test_user')
      .withPassword('test_pass')
      .start()

    // Connect to test database
    testDb = await connectToDatabase({
      host: container.getHost(),
      port: container.getPort(),
      database: container.getDatabase(),
      username: container.getUsername(),
      password: container.getPassword()
    })

    // Run migrations
    await testDb.migrate.latest()
  }, 60000) // Increased timeout for container startup

  afterAll(async () => {
    await testDb.destroy()
    await container.stop()
  })

  describe('Transaction Handling', () => {
    it('should commit transaction on success', async () => {
      // Act
      await testDb.transaction(async (trx) => {
        await trx('users').insert({ email: 'test@example.com', name: 'Test' })
        await trx('profiles').insert({ user_email: 'test@example.com', bio: 'Test bio' })
      })

      // Assert
      const user = await testDb('users').where({ email: 'test@example.com' }).first()
      const profile = await testDb('profiles').where({ user_email: 'test@example.com' }).first()

      expect(user).toBeDefined()
      expect(profile).toBeDefined()
    })

    it('should rollback transaction on error', async () => {
      // Act
      await expect(
        testDb.transaction(async (trx) => {
          await trx('users').insert({ email: 'test@example.com', name: 'Test' })
          throw new Error('Simulated error')
        })
      ).rejects.toThrow()

      // Assert - User should not exist
      const user = await testDb('users').where({ email: 'test@example.com' }).first()
      expect(user).toBeUndefined()
    })
  })

  describe('Complex Queries', () => {
    it('should perform join queries', async () => {
      // Arrange
      await testDb('users').insert([
        { id: '1', email: 'user1@example.com', name: 'User 1' },
        { id: '2', email: 'user2@example.com', name: 'User 2' }
      ])
      await testDb('posts').insert([
        { id: '1', user_id: '1', title: 'Post 1' },
        { id: '2', user_id: '1', title: 'Post 2' },
        { id: '3', user_id: '2', title: 'Post 3' }
      ])

      // Act
      const results = await testDb('users')
        .select('users.name', testDb.raw('COUNT(posts.id) as post_count'))
        .leftJoin('posts', 'users.id', 'posts.user_id')
        .groupBy('users.id')
        .orderBy('post_count', 'desc')

      // Assert
      expect(results).toHaveLength(2)
      expect(results[0]).toMatchObject({ name: 'User 1', post_count: '2' })
      expect(results[1]).toMatchObject({ name: 'User 2', post_count: '1' })
    })
  })
})
```

## External Service Integration Tests

```typescript
import { WireMock } from 'wiremock'

describe('External Service Integration', () => {
  let wireMock: WireMock

  beforeAll(async () => {
    // Start WireMock server for stubbing external APIs
    wireMock = new WireMock({ host: 'localhost', port: 8080 })
    await wireMock.start()
  })

  afterAll(async () => {
    await wireMock.stop()
  })

  beforeEach(async () => {
    await wireMock.resetAll()
  })

  describe('Payment Service Integration', () => {
    it('should process payment successfully', async () => {
      // Arrange - Stub external payment API
      await wireMock.stub({
        request: {
          method: 'POST',
          url: '/api/payments'
        },
        response: {
          status: 200,
          jsonBody: {
            transactionId: 'TX123456',
            status: 'approved'
          }
        }
      })

      const order = await OrderFactory.createInDb(db)

      // Act
      const response = await request(app)
        .post(`/api/orders/${order.id}/pay`)
        .send({ amount: 100, currency: 'USD' })
        .expect(200)

      // Assert
      expect(response.body).toMatchObject({
        transactionId: 'TX123456',
        status: 'approved'
      })

      // Verify WireMock received request
      const requests = await wireMock.getRequests()
      expect(requests).toHaveLength(1)
      expect(requests[0].body).toContain('amount')
    })

    it('should handle payment service timeout', async () => {
      // Arrange - Stub with delay
      await wireMock.stub({
        request: {
          method: 'POST',
          url: '/api/payments'
        },
        response: {
          status: 200,
          fixedDelayMilliseconds: 10000 // 10 second delay
        }
      })

      const order = await OrderFactory.createInDb(db)

      // Act
      const response = await request(app)
        .post(`/api/orders/${order.id}/pay`)
        .send({ amount: 100, currency: 'USD' })
        .expect(504)

      // Assert
      expect(response.body.error).toContain('timeout')
    })

    it('should retry on service failure', async () => {
      // Arrange - First call fails, second succeeds
      await wireMock.stub({
        request: {
          method: 'POST',
          url: '/api/payments'
        },
        response: {
          status: 500
        }
      })

      setTimeout(async () => {
        await wireMock.resetAll()
        await wireMock.stub({
          request: {
            method: 'POST',
            url: '/api/payments'
          },
          response: {
            status: 200,
            jsonBody: { transactionId: 'TX123456', status: 'approved' }
          }
        })
      }, 1000)

      const order = await OrderFactory.createInDb(db)

      // Act
      const response = await request(app)
        .post(`/api/orders/${order.id}/pay`)
        .send({ amount: 100, currency: 'USD' })
        .expect(200)

      // Assert
      expect(response.body.transactionId).toBe('TX123456')

      // Verify retries happened
      const requests = await wireMock.getRequests()
      expect(requests.length).toBeGreaterThan(1)
    })
  })
})
```

## Message Queue Integration Tests

```typescript
import { RabbitMQContainer } from '@testcontainers/rabbitmq'
import amqp from 'amqplib'

describe('Message Queue Integration', () => {
  let container: RabbitMQContainer
  let connection: amqp.Connection
  let channel: amqp.Channel

  beforeAll(async () => {
    // Start RabbitMQ container
    container = await new RabbitMQContainer().start()

    // Connect to RabbitMQ
    connection = await amqp.connect(container.getAmqpUrl())
    channel = await connection.createChannel()
  }, 60000)

  afterAll(async () => {
    await channel.close()
    await connection.close()
    await container.stop()
  })

  describe('Order Processing Queue', () => {
    it('should publish and consume messages', async () => {
      // Arrange
      const queueName = 'order_processing'
      await channel.assertQueue(queueName, { durable: false })

      const orderData = {
        orderId: '123',
        userId: 'user-456',
        total: 99.99
      }

      // Act - Publish message
      channel.sendToQueue(queueName, Buffer.from(JSON.stringify(orderData)))

      // Assert - Consume message
      const message = await new Promise<any>((resolve) => {
        channel.consume(queueName, (msg) => {
          if (msg) {
            resolve(JSON.parse(msg.content.toString()))
            channel.ack(msg)
          }
        })
      })

      expect(message).toMatchObject(orderData)
    })

    it('should handle message rejection and retry', async () => {
      // Arrange
      const queueName = 'order_processing_retry'
      await channel.assertQueue(queueName, { durable: true })
      await channel.assertQueue(`${queueName}_dlq`, { durable: true })

      const invalidOrder = { orderId: 'invalid' }
      channel.sendToQueue(queueName, Buffer.from(JSON.stringify(invalidOrder)))

      // Act - Consumer rejects invalid message
      let attempts = 0
      await new Promise<void>((resolve) => {
        channel.consume(queueName, (msg) => {
          if (msg) {
            attempts++
            if (attempts < 3) {
              channel.nack(msg, false, true) // Requeue
            } else {
              channel.sendToQueue(`${queueName}_dlq`, msg.content) // Dead letter
              channel.ack(msg)
              resolve()
            }
          }
        })
      })

      // Assert
      expect(attempts).toBe(3)
    })
  })
})
```

## Best Practices Checklist

- [ ] Test the entire request/response cycle (not just business logic)
- [ ] Use real database instances (Testcontainers) for accuracy
- [ ] Reset database state between tests (truncate or transactions)
- [ ] Test authentication and authorization flows
- [ ] Verify database state after operations (not just API responses)
- [ ] Stub external services (WireMock, MSW) for reliability
- [ ] Test error scenarios (timeouts, retries, failures)
- [ ] Test transaction rollbacks and commits
- [ ] Use factories for complex test data setup
- [ ] Test message queue processing (if applicable)
- [ ] Validate response headers and status codes
- [ ] Test rate limiting and throttling
- [ ] Verify side effects (emails sent, events published)

## Common Pitfalls

[FAIL] **Using in-memory databases for integration tests**:
```typescript
// Bad - SQLite in-memory doesn't match production PostgreSQL
const db = new SQLite(':memory:')

// Good - Use Testcontainers with real PostgreSQL
const container = await new PostgreSqlContainer('postgres:15').start()
```

[FAIL] **Not cleaning up between tests**:
```typescript
// Bad - Tests interfere with each other
beforeAll(async () => {
  await db.seed.run() // Only runs once
})

// Good - Fresh state for each test
beforeEach(async () => {
  await db('users').truncate()
})
```

[FAIL] **Testing external APIs directly**:
```typescript
// Bad - Tests depend on external service availability
await fetch('https://api.stripe.com/v1/charges')

// Good - Stub external services
await wireMock.stub({ ... })
```

## Configuration

### package.json

```json
{
  "scripts": {
    "test:integration": "vitest run --config vitest.integration.config.ts",
    "test:integration:watch": "vitest --config vitest.integration.config.ts"
  },
  "devDependencies": {
    "@testcontainers/postgresql": "^10.0.0",
    "@testcontainers/rabbitmq": "^10.0.0",
    "supertest": "^6.3.3",
    "wiremock": "^3.0.0"
  }
}
```

### vitest.integration.config.ts

```typescript
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    include: ['**/*.integration.test.ts'],
    testTimeout: 30000, // Longer timeout for containers
    hookTimeout: 60000, // Container startup can be slow
    globalSetup: './test/integration-setup.ts',
    pool: 'forks', // Isolation for database tests
    poolOptions: {
      forks: {
        singleFork: false // Run tests in parallel
      }
    }
  }
})
```

## Related Resources

See [../../references/comprehensive-testing-guide.md](../../references/comprehensive-testing-guide.md) for complete testing guide across all layers.
