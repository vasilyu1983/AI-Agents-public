# Modern Software Architecture Patterns

Comprehensive guide to contemporary architecture patterns based on industry trends and practices.

## Table of Contents

- [Top Architecture Patterns](#top-architecture-patterns)
- [1. Microservices Architecture](#1-microservices-architecture)
- [Add a mesh only when the policy/traffic/telemetry benefits justify it.](#add-a-mesh-only-when-the-policytraffictelemetry-benefits-justify-it)
- [Prefer no mesh for small systems, Linkerd for simplicity, and Istio/Cilium](#prefer-no-mesh-for-small-systems-linkerd-for-simplicity-and-istiocilium)
- [when you need advanced traffic policy or platform-level security controls.](#when-you-need-advanced-traffic-policy-or-platform-level-security-controls)
- [2. Event-Driven Architecture (EDA)](#2-event-driven-architecture-eda)
- [3. Serverless Architecture](#3-serverless-architecture)
- [4. Layered (N-Tier) Architecture](#4-layered-n-tier-architecture)
- [5. Hexagonal Architecture (Ports & Adapters)](#5-hexagonal-architecture-ports-&-adapters)
- [6. CQRS (Command Query Responsibility Segregation)](#6-cqrs-command-query-responsibility-segregation)
- [7. Modular Monolith](#7-modular-monolith)
- [8. Micro-Frontend Architecture](#8-micro-frontend-architecture)
- [Nginx routes different paths to different apps](#nginx-routes-different-paths-to-different-apps)
- [9. Service Mesh Architecture](#9-service-mesh-architecture)
- [Virtual Service (traffic routing)](#virtual-service-traffic-routing)
- [Circuit breaker](#circuit-breaker)
- [10. Edge Computing Architecture](#10-edge-computing-architecture)
- [11. Cell-Based Architecture](#11-cell-based-architecture)
- [Architecture Selection Decision Tree](#architecture-selection-decision-tree)
- [Modular Monolith vs. Microservices: Explicit Gates (2026 Default)](#modular-monolith-vs-microservices-explicit-gates-2026-default)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
- [1. Distributed Monolith](#1-distributed-monolith)
- [2. God Service](#2-god-service)
- [3. Anemic Domain Model](#3-anemic-domain-model)
- [4. Chatty APIs](#4-chatty-apis)
- [Resources](#resources)

## Top Architecture Patterns

### 1. Microservices Architecture

**When to use**:
- Multiple independent teams
- Need independent deployment and scaling
- Different technologies for different services
- Clear bounded contexts
- You have already ruled out a modular monolith as the simpler option

**Structure**:
```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Service   │  │   Service   │  │   Service   │
│     A       │  │      B      │  │      C      │
│  (Node.js)  │  │   (Python)  │  │    (Go)     │
└─────────────┘  └─────────────┘  └─────────────┘
      │                 │                 │
      └─────────────────┴─────────────────┘
                       │
              ┌────────▼────────┐
              │  API Gateway    │
              │  (Kong/Nginx)   │
              └─────────────────┘
```

**Best practices**:
- **Service discovery**: Use Kubernetes DNS, Consul, or a service-mesh registry (avoid unmaintained options such as Netflix Eureka for net-new builds)
- **API Gateway**: Single entry point, authentication, rate limiting
- **Communication**: REST for synchronous, message queues for async
- **Data**: Each service owns its database (no shared DB)
- **Deployment**: Containerization (Docker) + orchestration (Kubernetes)

**Challenges**:
- Distributed system complexity
- Network latency and failures
- Data consistency across services
- Testing and debugging
- Operational overhead

**Mitigation**:
```yaml
# Add a mesh only when the policy/traffic/telemetry benefits justify it.
# Prefer no mesh for small systems, Linkerd for simplicity, and Istio/Cilium
# when you need advanced traffic policy or platform-level security controls.
```

### 2. Event-Driven Architecture (EDA)

**When to use**:
- Real-time data processing
- Asynchronous workflows
- Decoupled systems
- High scalability requirements

**When NOT to introduce it (2026 expert default)**:
- The workflow needs immediate, strongly consistent confirmation to the caller (e.g., "did the payment succeed?") — a synchronous call with a clear timeout is simpler to reason about and debug than an event round trip.
- The team does not yet have distributed tracing, DLQ monitoring, and consumer-lag alerting in place. Async failures are silent by default; without this observability baseline, EDA converts visible synchronous errors into invisible ones.
- The system has one writer and one reader for a given fact — a direct call or a simple outbox-backed write is lower-overhead than a broker, schema registry, and consumer-group topology.
- The team is small (roughly under 5-8 engineers) and has not yet operated a message broker in production; the operational tax (partitioning, rebalancing, schema evolution, poison-message handling) is a common source of outages that outweighs the decoupling benefit at this scale.
- Ordering and exactly-once-like guarantees are assumed rather than designed for — if nobody has explicitly decided the idempotency and ordering strategy, defaulting to synchronous calls avoids a whole class of duplicate/out-of-order bugs until the team is ready to own them.

**Structure**:
```
┌──────────┐       ┌──────────────┐       ┌──────────┐
│ Producer │──────▶│ Event Broker │──────▶│ Consumer │
│          │       │ (Kafka/RabbitMQ)     │          │
└──────────┘       └──────────────┘       └──────────┘
                          │
                          ├──────▶ Consumer 2
                          └──────▶ Consumer 3
```

**Event patterns**:

**Event Notification**:
```json
{
  "eventType": "OrderPlaced",
  "orderId": "12345",
  "timestamp": "2023-06-15T10:30:00Z"
}
```

**Event-Carried State Transfer**:
```json
{
  "eventType": "OrderPlaced",
  "orderId": "12345",
  "customer": {"id": "C123", "name": "John"},
  "items": [{"id": "P456", "qty": 2}],
  "total": 99.99,
  "timestamp": "2023-06-15T10:30:00Z"
}
```

**Event Sourcing**:
```json
[
  {"event": "OrderCreated", "orderId": "12345", "seq": 1},
  {"event": "ItemAdded", "orderId": "12345", "itemId": "P456", "seq": 2},
  {"event": "OrderPaid", "orderId": "12345", "amount": 99.99, "seq": 3}
]
```

**Best practices**:
- **Idempotency**: Handle duplicate events gracefully
- **Schema evolution**: Use versioned event schemas
- **Error handling**: Dead letter queues for failed events
- **Monitoring**: Track event lag and processing times
- **Ordering**: Use partition keys for ordered processing

**Offset commit and contract safety**:
- Changing offset commit semantics (e.g., from "commit in finally" to "commit only after durable outcome") is a runtime contract change even if public APIs stay the same. Make new behavior explicitly opt-in.
- For shared infrastructure packages consumed by many services, lock the backward-compatibility rule before implementation starts. Additive configuration or a new registration path is safer than a semantic flip of existing defaults.
- Retry/DLQ topics increase cost through extra partitions, write/read traffic, and retention — not just from topic existence. Under topic-based schema strategy, publishing the same payload to retry and DLQ topics can multiply schema subjects. Use a shared retry/DLQ envelope or store original bytes plus metadata headers to limit schema sprawl.

**Tools**:
- Apache Kafka - High-throughput distributed streaming
- RabbitMQ - Flexible message broker
- AWS EventBridge - Serverless event bus
- Google Pub/Sub - Global messaging service

### 3. Serverless Architecture

**When to use**:
- Variable/unpredictable load
- Event-driven workloads
- Rapid development and deployment
- Cost optimization (pay per use)

**Structure**:
```
┌─────────┐      ┌──────────────┐      ┌─────────┐
│  Event  │─────▶│   Function   │─────▶│  Store  │
│ Source  │      │ (Lambda/CF)  │      │ (DynamoDB)
└─────────┘      └──────────────┘      └─────────┘

Event Sources:
- API Gateway (HTTP)
- S3 (file upload)
- DynamoDB Streams
- EventBridge (scheduled)
- SQS/SNS (messaging)
```

**Best practices**:
- **Cold start mitigation**: Keep functions warm with provisioned concurrency
- **Stateless design**: Use external state stores (Redis, DynamoDB)
- **Granular functions**: Single responsibility (≤300 LOC)
- **Resource limits**: Configure memory and timeout appropriately
- **Observability**: Use X-Ray, CloudWatch, or DataDog

**Example - AWS Lambda**:
```javascript
// Optimized function structure
export const handler = async (event) => {
  // Input validation
  const { userId, action } = JSON.parse(event.body);

  // Business logic
  const result = await processUserAction(userId, action);

  // Response
  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(result)
  };
};

// Keep external connections alive (outside handler)
const db = initDatabase();
```

**Cost optimization**:
- Use ARM-based functions (Graviton) - roughly 20% lower on-demand price than comparable x86, and up to ~40% better price-performance depending on workload and generation; verify current figures against AWS's Graviton pricing/price-performance pages before committing to a savings estimate
- Right-size memory allocation
- Use step functions for orchestration
- Implement caching to reduce invocations

### 4. Layered (N-Tier) Architecture

**When to use**:
- Monolithic applications
- Clear separation of concerns needed
- Team familiar with traditional patterns
- Moderate complexity

**Classic layers**:
```
┌──────────────────────────┐
│  Presentation Layer      │  ← Controllers, Views, API endpoints
├──────────────────────────┤
│  Business Logic Layer    │  ← Services, Domain models
├──────────────────────────┤
│  Data Access Layer       │  ← Repositories, ORM
├──────────────────────────┤
│  Database Layer          │  ← PostgreSQL, MongoDB
└──────────────────────────┘
```

**Dependency rule**: Outer layers depend on inner layers only

**Example structure**:
```
src/
├── controllers/          # HTTP request handlers
│   └── userController.js
├── services/            # Business logic
│   └── userService.js
├── repositories/        # Data access
│   └── userRepository.js
├── models/              # Domain models
│   └── user.js
└── database/            # DB configuration
    └── connection.js
```

**Best practices**:
- **Dependency injection**: Pass dependencies, don't hardcode
- **Interface segregation**: Define clear contracts between layers
- **Error propagation**: Handle errors at appropriate layer
- **Transaction management**: Handle at service layer

### 5. Hexagonal Architecture (Ports & Adapters)

**When to use**:
- Need high testability
- Multiple interfaces (REST, GraphQL, CLI)
- Business logic must be technology-agnostic
- Long-term maintainability priority

**Structure**:
```
        ┌─────────────────────────┐
        │   Application Core      │
        │   (Business Logic)      │
        │                         │
        │  ┌─────────────────┐    │
        │  │  Domain Model   │    │
        │  └─────────────────┘    │
        └────────┬──────┬──────────┘
                 │      │
    ┌────────────┘      └────────────┐
    │                                 │
┌───▼──────┐                   ┌─────▼────┐
│  Ports   │                   │  Ports   │
│ (Input)  │                   │ (Output) │
└───┬──────┘                   └─────┬────┘
    │                                 │
┌───▼──────────┐             ┌────────▼─────┐
│   Adapters   │             │   Adapters   │
│ REST, GraphQL│             │ DB, External │
└──────────────┘             └──────────────┘
```

**Implementation**:
```typescript
// Core domain (technology-agnostic)
interface UserRepository {
  findById(id: string): Promise<User>;
  save(user: User): Promise<void>;
}

class UserService {
  constructor(private userRepo: UserRepository) {}

  async activateUser(id: string): Promise<User> {
    const user = await this.userRepo.findById(id);
    user.activate();  // Business logic
    await this.userRepo.save(user);
    return user;
  }
}

// Adapters (technology-specific)
class PostgresUserRepository implements UserRepository {
  async findById(id: string): Promise<User> {
    const row = await db.query('SELECT * FROM users WHERE id = $1', [id]);
    return User.fromDatabase(row);
  }

  async save(user: User): Promise<void> {
    await db.query('UPDATE users SET ...', user.toDatabase());
  }
}

class RestAdapter {
  constructor(private userService: UserService) {}

  async handleActivateUser(req, res) {
    const user = await this.userService.activateUser(req.params.id);
    res.json(user);
  }
}
```

### 6. CQRS (Command Query Responsibility Segregation)

**When to use**:
- Read and write patterns are very different
- High read:write ratio
- Complex reporting requirements
- Need independent scaling of reads and writes

**Structure**:
```
           ┌─────────────┐
           │   Command   │
           │   (Write)   │
           └──────┬──────┘
                  │
        ┌─────────▼──────────┐
        │  Write Database    │
        │  (Normalized)      │
        └─────────┬──────────┘
                  │ (sync/async)
        ┌─────────▼──────────┐
        │   Read Database    │
        │  (Denormalized)    │
        └─────────┬──────────┘
                  │
           ┌──────▼──────┐
           │    Query    │
           │    (Read)   │
           └─────────────┘
```

**Example**:
```typescript
// Command (Write)
class CreateOrderCommand {
  constructor(
    public customerId: string,
    public items: OrderItem[]
  ) {}
}

class OrderCommandHandler {
  async handle(cmd: CreateOrderCommand) {
    const order = new Order(cmd.customerId, cmd.items);
    await writeDb.orders.save(order);

    // Publish event for read model update
    await eventBus.publish(new OrderCreatedEvent(order));
  }
}

// Query (Read)
class GetCustomerOrdersQuery {
  constructor(public customerId: string) {}
}

class OrderQueryHandler {
  async handle(query: GetCustomerOrdersQuery) {
    // Read from optimized read model
    return await readDb.customerOrders.find({
      customerId: query.customerId
    });
  }
}

// Event handler to sync read model
class OrderCreatedEventHandler {
  async handle(event: OrderCreatedEvent) {
    // Update denormalized read model
    await readDb.customerOrders.insert({
      customerId: event.customerId,
      orderId: event.orderId,
      total: event.total,
      // ... optimized for reads
    });
  }
}
```

### 7. Modular Monolith

**When to use**:
- Team size 5-30 developers
- Want clear boundaries without microservices overhead
- Need faster development than microservices
- Shared domain concepts across modules

**Structure**:
```
monolith/
├── modules/
│   ├── orders/
│   │   ├── api/          # Public interface
│   │   ├── domain/       # Business logic (private)
│   │   └── infrastructure/ # DB, external services (private)
│   ├── payments/
│   │   ├── api/
│   │   ├── domain/
│   │   └── infrastructure/
│   └── shipping/
│       ├── api/
│       ├── domain/
│       └── infrastructure/
└── shared/
    ├── database/
    └── messaging/
```

**Module boundaries**:
```typescript
// orders/api/OrdersModule.ts (public API)
export class OrdersModule {
  static async createOrder(data: CreateOrderDTO): Promise<Order> {
    // Implementation hidden
  }

  static async getOrder(id: string): Promise<Order> {
    // Implementation hidden
  }
}

// payments/PaymentsService.ts
import { OrdersModule } from '../orders/api/OrdersModule';

class PaymentsService {
  async processPayment(orderId: string) {
    // Use public API only, no direct access to orders internals
    const order = await OrdersModule.getOrder(orderId);
    // ...
  }
}
```

**Advantages over microservices**:
- Single deployment (simpler CI/CD)
- No network latency between modules
- Shared transactions possible
- Easier refactoring (can extract to microservice later)

### 8. Micro-Frontend Architecture

**When to use**:
- Multiple teams working on different features
- Different technology stacks for different parts
- Independent deployment of UI components
- Large-scale front-end applications

**Approaches**:

**A) Server-side composition (SSR)**:
```nginx
# Nginx routes different paths to different apps
location /products {
  proxy_pass http://products-frontend:3000;
}
location /checkout {
  proxy_pass http://checkout-frontend:3001;
}
```

**B) Build-time composition (Module Federation)**:
```javascript
// Webpack Module Federation
module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'products',
      filename: 'remoteEntry.js',
      exposes: {
        './ProductList': './src/components/ProductList'
      },
      shared: ['react', 'react-dom']
    })
  ]
};

// Host app imports remote component
const ProductList = React.lazy(() => import('products/ProductList'));
```

**C) Runtime composition (Single-SPA)**:
```javascript
import { registerApplication, start } from 'single-spa';

registerApplication({
  name: 'products',
  app: () => import('./products/main.js'),
  activeWhen: location => location.pathname.startsWith('/products')
});

registerApplication({
  name: 'checkout',
  app: () => import('./checkout/main.js'),
  activeWhen: '/checkout'
});

start();
```

### 9. Service Mesh Architecture

**When to use**:
- Microservices at scale (10+ services)
- Need advanced traffic management
- Security and observability are critical
- Polyglot microservices
- Shared connectivity policy is hard to enforce with libraries alone

**Structure**:
```
Service A ──▶ Mesh data plane
               │                    ──▶ Mesh data plane ──▶ Service B
               └─ Control Plane
                      │
                      ├─ Traffic management
                      ├─ Security (mTLS / identity)
                      └─ Observability
```

**Features**:
- **Traffic management**: Load balancing, circuit breaking, retries
- **Security**: Mutual TLS, authorization policies
- **Observability**: Distributed tracing, metrics, logging
- **Topologies**: Sidecar, ambient, or eBPF-assisted depending on platform needs

**Example - Istio**:
```yaml
# Virtual Service (traffic routing)
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
    - reviews
  http:
  - match:
    - headers:
        user-agent:
          regex: '.*Chrome.*'
    route:
    - destination:
        host: reviews
        subset: v2
  - route:
    - destination:
        host: reviews
        subset: v1

# Circuit breaker
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews
spec:
  host: reviews
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 1
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
```

### 10. Edge Computing Architecture

**When to use**:
- Need ultra-low latency
- IoT applications
- Content delivery
- Real-time processing

**Structure**:
```
┌─────────────────────────────────────────┐
│         Cloud (Central)                 │
│  - Data aggregation                     │
│  - ML model training                    │
│  - Long-term storage                    │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼──────┐    ┌─────▼────┐
│  Edge    │    │  Edge    │
│  Node 1  │    │  Node 2  │
│ - Process│    │ - Process│
│ - Cache  │    │ - Cache  │
│ - Filter │    │ - Filter │
└───┬──────┘    └─────┬────┘
    │                 │
┌───▼──┐          ┌───▼──┐
│  IoT │          │  IoT │
│Device│          │Device│
└──────┘          └──────┘
```

**Use cases**:
- CDN edge workers (Cloudflare Workers, Lambda@Edge)
- Smart city sensors
- Industrial IoT
- Autonomous vehicles

**Example - Cloudflare Worker** (ES module format; the legacy `addEventListener('fetch')` Service Worker syntax is deprecated):
```javascript
export default {
  async fetch(request, env, ctx) {
    // Process at edge (near user)
    const cache = caches.default;
    let response = await cache.match(request);

    if (!response) {
      // Fetch from origin if not cached
      response = await fetch(request);
      // Cache at edge without blocking the response
      ctx.waitUntil(cache.put(request, response.clone()));
    }

    return response;
  },
};
```

### 11. Cell-Based Architecture

**What it is**: partition the entire system — compute, data, and often the control plane — into independent, identically-shaped "cells," each serving a bounded subset of traffic or tenants (by customer ID hash, region, or shard key). A router/gateway layer directs each request to exactly one cell; cells do not share fate. This is distinct from a service mesh or plain sharding: the unit of isolation is the whole request path (all services + data a request touches), not just the database or just the network layer.

**When to use (a narrow niche, not a general-purpose default)**:
- Blast-radius containment is a hard requirement — a single cell failing must not be able to take down other tenants' traffic (common in regulated multi-tenant SaaS, and used internally by AWS for services where a regional outage is unacceptable).
- The system already has enough scale that a single shared fleet has caused correlated, whole-system incidents (bad deploys, noisy-neighbor resource contention, cascading retries) more than once.
- Compliance or data-residency rules require hard per-tenant or per-region data isolation that cell boundaries can enforce structurally.

**When NOT to use**:
- Team or system is still at the stage of deciding modular monolith vs. microservices — cell-based architecture is a scaling pattern layered *on top of* an already-decomposed, already-operated set of services, not a starting point.
- The operational cost of running N independent copies of the full stack (each cell needs its own deploy pipeline, monitoring, and capacity headroom) has not been justified by an actual blast-radius incident or a compliance requirement.
- A simpler mitigation (bulkheads, per-tenant rate limiting, or a few availability-zone-level shards) already meets the isolation requirement.

**Trade-off to state explicitly**: cells trade efficiency (each cell needs spare capacity, and hot cells cannot always borrow headroom from cold ones) for isolation. This is a deliberate reliability investment, not a free scaling win — verify current vendor guidance (e.g., AWS's own writing on cell-based architecture and shuffle sharding) before committing, since routing and rebalancing tooling in this space is still evolving.

## Architecture Selection Decision Tree

```
Start: What are you building?

├─ Simple CRUD app
│  └─ Use: Layered Architecture
│
├─ Need independent team scaling?
│  ├─ Yes → Need independent deployments?
│  │  ├─ Yes → Use: Microservices
│  │  └─ No → Use: Modular Monolith
│  └─ No → Use: Layered or Hexagonal
│
├─ Event-driven requirements?
│  ├─ Primary pattern → Use: Event-Driven Architecture
│  └─ Secondary pattern → Add messaging to chosen architecture
│
├─ Unpredictable/variable load?
│  └─ Use: Serverless
│
├─ Different read/write patterns?
│  └─ Use: CQRS + Event Sourcing
│
└─ Multiple UI teams?
   └─ Use: Micro-Frontends
```

### Modular Monolith vs. Microservices: Explicit Gates (2026 Default)

The 2026 expert default is **modular monolith first**. Move to microservices only when at least one gate below is clearly true — not on the assumption that a growing team will eventually need them:

| Gate | Threshold that justifies splitting out a service |
|---|---|
| Team size | A module has its own dedicated team of roughly 6+ engineers who are blocked by shared-deploy coordination with other modules |
| Release cadence | The module needs to ship multiple times a day while the rest of the system ships weekly, and the coupling of the shared deploy is the actual blocker (not just a preference) |
| Operational maturity | The org already runs CI/CD, on-call, centralized observability (traces/metrics/logs), and incident response for at least one production service — microservices multiply the number of these operational surfaces, so add a service only once the org can operate the first one well |
| Scale profile | The module has a measurably different scale or resource profile (e.g., GPU-bound inference vs. CPU-bound CRUD) that makes shared scaling wasteful |
| Trust/compliance boundary | The module crosses a hard security, PCI, or data-residency boundary that argues for physical isolation, not just logical isolation |

If none of these are true, keep the module inside the modular monolith. This is not a permanent choice — bounded contexts with clean module boundaries (see the module-boundary example above) are what make a later extraction cheap, so the real investment is in boundary discipline, not in choosing microservices early.

**A cautionary real-world data point (not a universal rule).** In March 2023, Amazon's Prime Video team publicly described moving their *audio/video quality monitoring service* from a distributed, Lambda/Step-Functions-based microservices design to a monolithic application running on a single ECS task, reporting a 90% cost reduction (AWS Compute Blog, "Scaling up the Prime Video audio/video monitoring service and reducing costs by 90%," March 2023). The bottleneck was orchestration and inter-service data-passing overhead (S3 as intermediate storage between steps) hitting a hard scaling ceiling at roughly 5% of target load. Two caveats matter before citing this as evidence for a general "microservices are bad" argument: (1) it describes one specific, high-throughput, low-per-request-value monitoring workload inside Prime Video, not a company-wide architectural reversal — most of Prime Video's other services remained distributed; (2) the actual root cause was a specific anti-pattern (using object storage as a synchronous hand-off between orchestration steps at very high frequency), which is a narrower lesson than "monolith beats microservices." Use it as a reminder to validate the *coordination and data-passing* costs of a distributed design against the actual request volume, not as a blanket argument either way.

## Anti-Patterns to Avoid

### 1. Distributed Monolith
Microservices that are tightly coupled:
```
[FAIL] Service A calls Service B, which calls Service C, which calls Service A
[OK] Use message queues or events to decouple
```

### 2. God Service
One service that does everything:
```
[FAIL] UserOrderPaymentShippingService
[OK] UserService, OrderService, PaymentService, ShippingService
```

### 3. Anemic Domain Model
Models with no behavior, just getters/setters:
```typescript
[FAIL] // Anemic
class Order {
  items: OrderItem[];
  getItems() { return this.items; }
  setItems(items) { this.items = items; }
}

[OK] // Rich domain model
class Order {
  private items: OrderItem[];

  addItem(item: OrderItem) {
    this.validateItem(item);
    this.items.push(item);
    this.recalculateTotal();
  }

  canBeCancelled(): boolean {
    return this.status === 'pending' && !this.isPaid;
  }
}
```

**DDD tactical-pattern cargo-culting (a common cause of anemic models).** Teams often adopt DDD's tactical vocabulary — Entity, Value Object, Aggregate, Repository — without adopting the strategic discipline that gives those patterns meaning (bounded contexts, ubiquitous language shared with domain experts, invariant-protecting aggregate boundaries). The result looks like DDD but behaves like an anemic model with extra ceremony: "Aggregates" that are really just ORM entities, "Repositories" that leak persistence concerns, and a "ubiquitous language" that only the engineering team uses. Symptoms: aggregate boundaries drawn around database tables rather than transactional invariants; domain services that just orchestrate CRUD; no involvement from domain experts in naming or modeling sessions. Fix: start from the invariants that must hold true within a transaction (that defines the aggregate boundary), and validate the model's vocabulary with actual domain experts before treating the tactical patterns as done.

### 4. Chatty APIs
Too many network calls:
```
[FAIL] GET /users/1, GET /users/1/orders, GET /orders/1/items
[OK] GET /users/1?include=orders.items
```

## Resources

- Martin Fowler - Architecture Patterns
- Microsoft Azure - Architecture Center
- AWS - Well-Architected Framework
- Google Cloud - Architecture Framework
- Microservices.io - Pattern catalog
