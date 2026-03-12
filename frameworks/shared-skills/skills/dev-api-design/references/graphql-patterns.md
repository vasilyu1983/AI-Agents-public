# GraphQL Schema Design Patterns

Comprehensive guide to designing production-grade GraphQL APIs with best practices and common patterns.

---

## What is GraphQL?

GraphQL is a **query language for APIs** that allows clients to request exactly the data they need. Unlike REST, where each endpoint returns a fixed structure, GraphQL lets clients specify their data requirements.

**Key Advantages:**
- [TARGET] **Precise data fetching** - No over-fetching or under-fetching
- [PACKAGE] **Single request** - Fetch multiple resources in one query
- [REFRESH] **Strongly typed** - Schema-driven with type safety
- [LAUNCH] **Evolvable** - Add fields without versioning
- [TOOLS] **Developer experience** - Self-documenting with introspection

---

## Basic Schema Structure

```graphql
# Type definitions
type Query {
  user(id: ID!): User
  users(limit: Int, offset: Int): [User!]!
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
}

type User {
  id: ID!
  email: String!
  name: String!
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  author: User!
}

# Input types for mutations
input CreateUserInput {
  email: String!
  name: String!
}

# Payload types for mutations
type CreateUserPayload {
  user: User
  errors: [Error!]
}
```

---

## Core Patterns

### 1. Connection Pattern (Pagination)

**Problem:** Efficiently paginate through large lists.

**Solution:** Relay-style connections with edges and cursors.

```graphql
type Query {
  users(
    first: Int
    after: String
    last: Int
    before: String
  ): UserConnection!
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

**Query Example:**
```graphql
query {
  users(first: 20, after: "cursor123") {
    edges {
      node {
        id
        name
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

**Why this pattern?**
- Stable pagination (cursor-based, not offset)
- Works with real-time data (items can be added/removed)
- Supports bidirectional pagination

---

### 2. Input Object Pattern

**Problem:** Group related input fields for mutations.

**Solution:** Use input types instead of multiple arguments.

```graphql
# BAD: Bad - Too many arguments
type Mutation {
  createUser(
    email: String!
    name: String!
    password: String!
    phoneNumber: String
    address: String
  ): User!
}

# GOOD: Good - Input object
input CreateUserInput {
  email: String!
  name: String!
  password: String!
  phoneNumber: String
  address: String
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
}
```

**Benefits:**
- Easier to extend without breaking changes
- Clear separation of concerns
- Better documentation

---

### 3. Payload Pattern

**Problem:** Return errors alongside data.

**Solution:** Wrap responses in payload types.

```graphql
type CreateUserPayload {
  user: User           # Nullable (null if error)
  errors: [Error!]     # Empty if success
  clientMutationId: String  # For client-side request tracking
}

type Error {
  field: String        # Which field caused error
  message: String!     # Human-readable message
  code: ErrorCode!     # Machine-readable code
}

enum ErrorCode {
  VALIDATION_ERROR
  DUPLICATE_EMAIL
  UNAUTHORIZED
  SERVER_ERROR
}
```

**Mutation Example:**
```graphql
mutation {
  createUser(input: {
    email: "user@example.com"
    name: "John Doe"
  }) {
    user {
      id
      email
    }
    errors {
      field
      message
      code
    }
  }
}
```

**Response (Error):**
```json
{
  "data": {
    "createUser": {
      "user": null,
      "errors": [
        {
          "field": "email",
          "message": "Email already registered",
          "code": "DUPLICATE_EMAIL"
        }
      ]
    }
  }
}
```

---

### 4. Interface Pattern

**Problem:** Share common fields across multiple types.

**Solution:** Use interfaces for polymorphism.

```graphql
interface Node {
  id: ID!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type User implements Node {
  id: ID!
  createdAt: DateTime!
  updatedAt: DateTime!
  email: String!
  name: String!
}

type Post implements Node {
  id: ID!
  createdAt: DateTime!
  updatedAt: DateTime!
  title: String!
  content: String!
}

type Query {
  node(id: ID!): Node
  nodes(ids: [ID!]!): [Node!]!
}
```

**Query with Inline Fragments:**
```graphql
query {
  node(id: "user-123") {
    id
    ... on User {
      email
      name
    }
    ... on Post {
      title
    }
  }
}
```

---

### 5. Union Types Pattern

**Problem:** Return different types from same field.

**Solution:** Use unions for heterogeneous results.

```graphql
union SearchResult = User | Post | Comment

type Query {
  search(query: String!): [SearchResult!]!
}

query {
  search(query: "graphql") {
    __typename
    ... on User {
      id
      name
    }
    ... on Post {
      id
      title
    }
    ... on Comment {
      id
      text
    }
  }
}
```

---

### 6. Enum Pattern

**Problem:** Restrict field values to specific set.

**Solution:** Use enums for fixed options.

```graphql
enum UserStatus {
  ACTIVE
  INACTIVE
  SUSPENDED
}

enum SortOrder {
  ASC
  DESC
}

type User {
  id: ID!
  status: UserStatus!
}

type Query {
  users(
    status: UserStatus
    sortBy: String
    sortOrder: SortOrder
  ): [User!]!
}
```

---

### 7. Custom Scalar Pattern

**Problem:** Built-in scalars (String, Int, Boolean) are insufficient.

**Solution:** Define custom scalars for specific types.

```graphql
scalar DateTime
scalar Email
scalar URL
scalar JSON

type User {
  id: ID!
  email: Email!         # Validates email format
  avatar: URL           # Validates URL format
  createdAt: DateTime!  # ISO 8601 date-time
  metadata: JSON        # Arbitrary JSON data
}
```

**Resolver Implementation (Node.js):**
```javascript
import { GraphQLScalarType } from 'graphql';

const DateTimeScalar = new GraphQLScalarType({
  name: 'DateTime',
  description: 'ISO 8601 date-time string',
  serialize(value) {
    return value.toISOString();  // Send to client
  },
  parseValue(value) {
    return new Date(value);      // Receive from client
  }
});
```

---

### 8. Directive Pattern

**Problem:** Add metadata to schema elements.

**Solution:** Use directives for cross-cutting concerns.

```graphql
directive @auth(requires: Role!) on FIELD_DEFINITION
directive @deprecated(reason: String!) on FIELD_DEFINITION
directive @rateLimit(limit: Int!, window: Int!) on FIELD_DEFINITION

enum Role {
  ADMIN
  USER
}

type Mutation {
  deleteUser(id: ID!): Boolean! @auth(requires: ADMIN)
  createPost(input: CreatePostInput!): Post! @rateLimit(limit: 10, window: 60)
}

type User {
  phone: String @deprecated(reason: "Use phoneNumber instead")
  phoneNumber: String
}
```

---

### 9. DataLoader Pattern (N+1 Problem)

**Problem:** N+1 queries when fetching related data.

```graphql
query {
  posts {
    id
    title
    author {      # Separate query for each post!
      name
    }
  }
}
```

**Solution:** Batch requests with DataLoader.

```javascript
import DataLoader from 'dataloader';

// Batch function
const batchUsers = async (userIds) => {
  const users = await User.findAll({ where: { id: userIds } });
  // Return in same order as input
  return userIds.map(id => users.find(u => u.id === id));
};

const userLoader = new DataLoader(batchUsers);

// Resolver
const resolvers = {
  Post: {
    author: (post, args, context) => {
      return context.userLoader.load(post.authorId);  // Batched!
    }
  }
};
```

**Result:** 2 queries instead of N+1
```sql
SELECT * FROM posts;
SELECT * FROM users WHERE id IN (1, 2, 3, 4, 5);  -- Batched!
```

---

## Schema Design Best Practices

### 1. Use Nullable vs Non-Nullable Strategically

```graphql
type User {
  id: ID!              # GOOD: Non-null (always present)
  email: String!       # GOOD: Non-null (required field)
  phoneNumber: String  # GOOD: Nullable (optional field)
  posts: [Post!]!      # GOOD: Non-null array, non-null items (empty array if no posts)
}
```

**Guidelines:**
- Use `!` for fields that are **always** present
- Avoid `!` if field might fail to load (better to return null than error)
- For lists: `[Post!]!` is safer than `[Post]` (no nulls in array)

### 2. Avoid Over-Nesting

```graphql
# BAD: Bad - Too deeply nested
type Query {
  user(id: ID!): User
}

type User {
  organization: Organization
}

type Organization {
  teams: [Team!]!
}

type Team {
  members: [User!]!
}

type User {
  manager: User
}

# Leads to queries like:
query {
  user(id: "1") {
    organization {
      teams {
        members {
          manager {
            manager {
              manager {  # Too deep!
```

**Solution:** Use depth limiting.

```javascript
// graphql-depth-limit
import depthLimit from 'graphql-depth-limit';

const server = new ApolloServer({
  schema,
  validationRules: [depthLimit(5)]  // Max 5 levels
});
```

### 3. Implement Query Complexity Analysis

```javascript
import { createComplexityLimitRule } from 'graphql-validation-complexity';

const server = new ApolloServer({
  validationRules: [
    createComplexityLimitRule(1000, {
      scalarCost: 1,
      objectCost: 10,
      listFactor: 20
    })
  ]
});
```

### 4. Use Consistent Naming

**Queries:**
- `user` - Single resource
- `users` - List of resources
- `allUsers` - All without filters

**Mutations:**
- `createUser` - Create
- `updateUser` - Update
- `deleteUser` - Delete

**Payloads:**
- `CreateUserPayload`
- `UpdateUserPayload`

**Inputs:**
- `CreateUserInput`
- `UpdateUserInput`

### 5. Deprecate, Don't Remove

```graphql
type User {
  phone: String @deprecated(reason: "Use phoneNumber instead")
  phoneNumber: String
}
```

**Benefits:**
- Clients have time to migrate
- No breaking changes
- Introspection shows deprecations

---

## GraphQL vs REST Comparison

| Aspect | REST | GraphQL |
|--------|------|---------|
| **Endpoints** | Multiple (`/users`, `/posts`) | Single (`/graphql`) |
| **Data Fetching** | Fixed structure | Client-specified fields |
| **Over-fetching** | Common | None |
| **Under-fetching** | Requires multiple requests | Single request |
| **Versioning** | Required | Optional (evolving schema) |
| **Caching** | HTTP caching (URL-based) | Complex (normalized cache) |
| **Learning Curve** | Low | Medium |
| **Tooling** | Mature | Good (GraphiQL, Apollo) |
| **Real-time** | WebSockets/SSE | Subscriptions (built-in) |

---

## Real-World GraphQL Subscriptions

**Problem:** Push real-time updates to clients.

**Solution:** Use subscriptions for pub/sub.

```graphql
type Subscription {
  userCreated: User!
  postUpdated(postId: ID!): Post!
}

# Client subscribes
subscription {
  userCreated {
    id
    name
    email
  }
}
```

**Server Implementation (Node.js with Apollo):**
```javascript
import { PubSub } from 'graphql-subscriptions';

const pubsub = new PubSub();

const resolvers = {
  Subscription: {
    userCreated: {
      subscribe: () => pubsub.asyncIterator(['USER_CREATED'])
    }
  },
  Mutation: {
    createUser: async (parent, { input }) => {
      const user = await User.create(input);

      // Publish event
      pubsub.publish('USER_CREATED', { userCreated: user });

      return { user };
    }
  }
};
```

---

## Security Best Practices

### 1. Authentication

```javascript
const resolvers = {
  Query: {
    me: (parent, args, context) => {
      if (!context.user) {
        throw new AuthenticationError('Not authenticated');
      }
      return context.user;
    }
  }
};
```

### 2. Authorization (Field-Level)

```javascript
const resolvers = {
  User: {
    email: (user, args, context) => {
      // Only user themselves or admins can see email
      if (context.user.id !== user.id && context.user.role !== 'ADMIN') {
        return null;
      }
      return user.email;
    }
  }
};
```

### 3. Rate Limiting

```javascript
import { createRateLimitDirective } from 'graphql-rate-limit';

const rateLimitDirective = createRateLimitDirective({
  identifyContext: (ctx) => ctx.user.id
});

const schema = makeExecutableSchema({
  typeDefs,
  schemaDirectives: {
    rateLimit: rateLimitDirective
  }
});
```

### 4. Query Timeouts

```javascript
const server = new ApolloServer({
  schema,
  context: ({ req }) => ({
    user: getUserFromToken(req.headers.authorization),
    timeout: setTimeout(() => {
      throw new Error('Query timeout');
    }, 5000)  // 5 second timeout
  })
});
```

---

## Testing GraphQL APIs

### Unit Tests (Resolvers)

```javascript
import { createUser } from './resolvers';

describe('createUser', () => {
  it('creates user with valid input', async () => {
    const input = { email: 'test@example.com', name: 'Test' };
    const result = await createUser(null, { input }, { user: adminUser });

    expect(result.user.email).toBe('test@example.com');
    expect(result.errors).toHaveLength(0);
  });

  it('returns error for duplicate email', async () => {
    const input = { email: 'existing@example.com', name: 'Test' };
    const result = await createUser(null, { input }, { user: adminUser });

    expect(result.user).toBeNull();
    expect(result.errors[0].code).toBe('DUPLICATE_EMAIL');
  });
});
```

### Integration Tests

```javascript
import { createTestClient } from 'apollo-server-testing';

const { query, mutate } = createTestClient(server);

it('creates and fetches user', async () => {
  const CREATE_USER = gql`
    mutation CreateUser($input: CreateUserInput!) {
      createUser(input: $input) {
        user {
          id
          email
        }
      }
    }
  `;

  const result = await mutate({
    mutation: CREATE_USER,
    variables: { input: { email: 'new@example.com', name: 'New User' } }
  });

  expect(result.data.createUser.user.email).toBe('new@example.com');
});
```

---

## Tools & Resources

**Servers:**
- [Apollo Server](https://www.apollographql.com/docs/apollo-server/) (Node.js)
- [GraphQL Yoga](https://github.com/dotansimha/graphql-yoga) (Node.js)
- [Graphene](https://graphene-python.org/) (Python)
- [graphql-java](https://www.graphql-java.com/) (Java)

**Clients:**
- [Apollo Client](https://www.apollographql.com/docs/react/) (React, Vue, Angular)
- [urql](https://formidable.com/open-source/urql/) (React, Svelte)
- [Relay](https://relay.dev/) (React)

**Tools:**
- [GraphiQL](https://github.com/graphql/graphiql) - Interactive IDE
- [Apollo Studio](https://studio.apollographql.com/) - Schema registry, metrics
- [GraphQL Inspector](https://graphql-inspector.com/) - Schema diff, validation

**Resources:**
- [GraphQL Spec](https://spec.graphql.org/)
- [GraphQL Best Practices](https://graphql.org/learn/best-practices/)
- [Apollo Docs](https://www.apollographql.com/docs/)
