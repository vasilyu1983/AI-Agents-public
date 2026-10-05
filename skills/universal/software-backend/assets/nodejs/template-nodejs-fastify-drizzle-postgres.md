# Backend Engineering - Node.js + Fastify + Drizzle + PostgreSQL Template

*Purpose: SQL-first TypeScript backend for teams that want Fastify ergonomics, Drizzle migrations, and explicit database access.*

---

# When to Use

Use this template when building:

- TypeScript REST APIs with PostgreSQL
- Services that need explicit SQL-like queries
- Node.js backends that may later move some routes to edge-friendly code
- CRUD-heavy SaaS APIs with moderate complexity

Prefer this over Prisma when query control and migration transparency matter more than schema-DSL convenience.

---

# TEMPLATE STARTS HERE

# 1. Project Overview

**Tech Stack:**
- [ ] Node.js 24 Active LTS (or org-approved LTS)
- [ ] TypeScript
- [ ] Fastify
- [ ] Drizzle ORM + Drizzle Kit
- [ ] PostgreSQL
- [ ] Redis (optional)
- [ ] Vitest + Supertest

**Project Name:** `{{project_name}}`

---

# 2. Project Structure

```text
project-root/
|-- src/
|   |-- app.ts
|   |-- server.ts
|   |-- db/
|   |   |-- client.ts
|   |   |-- schema.ts
|   |   `-- queries/
|   |       `-- users.ts
|   |-- routes/
|   |   |-- health.ts
|   |   `-- users.ts
|   |-- plugins/
|   |   |-- env.ts
|   |   `-- problem-details.ts
|   `-- lib/
|       `-- problem.ts
|-- drizzle/
|   `-- 0001_init.sql
|-- tests/
|   `-- users.test.ts
|-- package.json
|-- tsconfig.json
|-- drizzle.config.ts
|-- .env.example
`-- docker-compose.yml
```

---

# 3. Dependencies

## package.json

```json
{
  "name": "your-api",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/server.ts",
    "build": "tsc -p tsconfig.json",
    "start": "node dist/server.js",
    "test": "vitest run",
    "db:generate": "drizzle-kit generate",
    "db:migrate": "drizzle-kit migrate"
  },
  "dependencies": {
    "@fastify/sensible": "^6.0.3",
    "@fastify/type-provider-typebox": "^5.0.0",
    "drizzle-orm": "^0.44.0",
    "fastify": "^5.2.1",
    "pg": "^8.14.1",
    "pino": "^9.6.0",
    "typebox": "^0.34.8",
    "zod": "^3.24.2"
  },
  "devDependencies": {
    "drizzle-kit": "^0.31.0",
    "@types/node": "^24.0.0",
    "supertest": "^7.0.0",
    "tsx": "^4.19.3",
    "typescript": "^5.8.2",
    "vitest": "^3.0.8"
  }
}
```

## .env.example

```env
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/app
LOG_LEVEL=info
```

---

# 4. Database Layer

## drizzle.config.ts

```ts
import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./src/db/schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: {
    url: process.env.DATABASE_URL ?? "",
  },
});
```

## src/db/schema.ts

```ts
import { pgTable, text, timestamp, uuid } from "drizzle-orm/pg-core";

export const users = pgTable("users", {
  id: uuid("id").defaultRandom().primaryKey(),
  email: text("email").notNull().unique(),
  fullName: text("full_name").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});
```

## src/db/client.ts

```ts
import { drizzle } from "drizzle-orm/node-postgres";
import pg from "pg";

const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
  idleTimeoutMillis: 30_000,
});

export const db = drizzle(pool);
export { pool };
```

## src/db/queries/users.ts

```ts
import { eq } from "drizzle-orm";

import { db } from "../client.js";
import { users } from "../schema.js";

export async function listUsers() {
  return db.select().from(users).orderBy(users.createdAt);
}

export async function createUser(input: { email: string; fullName: string }) {
  const [user] = await db.insert(users).values(input).returning();
  return user;
}

export async function findUserByEmail(email: string) {
  return db.query.users.findFirst({ where: eq(users.email, email) });
}
```

---

# 5. HTTP Layer

## src/lib/problem.ts

```ts
export class Problem extends Error {
  constructor(
    public readonly status: number,
    public readonly type: string,
    public readonly title: string,
    public readonly detail: string,
  ) {
    super(detail);
  }
}
```

## src/app.ts

```ts
import Fastify from "fastify";

import { registerHealthRoutes } from "./routes/health.js";
import { registerUserRoutes } from "./routes/users.js";
import { Problem } from "./lib/problem.js";

export function buildApp() {
  const app = Fastify({
    logger: { level: process.env.LOG_LEVEL ?? "info" },
    requestTimeout: 30_000,
  });

  app.setErrorHandler((error, request, reply) => {
    if (error instanceof Problem) {
      return reply.status(error.status).type("application/problem+json").send({
        type: error.type,
        title: error.title,
        status: error.status,
        detail: error.detail,
        instance: request.url,
      });
    }

    request.log.error({ err: error }, "Unhandled request failure");
    return reply.status(500).type("application/problem+json").send({
      type: "https://api.example.com/problems/internal",
      title: "Internal Server Error",
      status: 500,
      detail: "An unexpected error occurred.",
      instance: request.url,
    });
  });

  registerHealthRoutes(app);
  registerUserRoutes(app);
  return app;
}
```

## src/routes/users.ts

```ts
import type { FastifyInstance } from "fastify";
import { z } from "zod";

import { Problem } from "../lib/problem.js";
import { createUser, findUserByEmail, listUsers } from "../db/queries/users.js";

const createUserSchema = z.object({
  email: z.string().email(),
  fullName: z.string().min(2).max(120),
});

export function registerUserRoutes(app: FastifyInstance) {
  app.get("/users", async () => listUsers());

  app.post("/users", async (request, reply) => {
    const input = createUserSchema.parse(request.body);

    if (await findUserByEmail(input.email)) {
      throw new Problem(
        409,
        "https://api.example.com/problems/email-conflict",
        "Conflict",
        "A user with this email already exists.",
      );
    }

    const user = await createUser(input);
    return reply.code(201).send(user);
  });
}
```

## src/routes/health.ts

```ts
import type { FastifyInstance } from "fastify";

export function registerHealthRoutes(app: FastifyInstance) {
  app.get("/health/live", async () => ({ status: "ok" }));
}
```

## src/server.ts

```ts
import { buildApp } from "./app.js";

const app = buildApp();
await app.listen({ port: Number(process.env.PORT ?? 3000), host: "0.0.0.0" });
```

---

# 6. Tests

## tests/users.test.ts

```ts
import request from "supertest";
import { beforeAll, afterAll, describe, expect, it } from "vitest";

import { buildApp } from "../src/app.js";

const app = buildApp();

beforeAll(async () => {
  await app.ready();
});

afterAll(async () => {
  await app.close();
});

describe("users routes", () => {
  it("returns 201 when a user is created", async () => {
    const response = await request(app.server)
      .post("/users")
      .send({ email: "test@example.com", fullName: "Test User" });

    expect(response.status).toBe(201);
    expect(response.body.email).toBe("test@example.com");
  });
});
```

---

# 7. Operational Notes

- Keep Problem Details consistent for all handler failures.
- Add per-route auth and rate limiting before exposing mutating routes publicly.
- Use `drizzle-kit` migrations as reviewed SQL, not ad-hoc schema drift.
- Prefer explicit column selection on read-heavy endpoints.
- Add OpenTelemetry and correlation IDs before production launch.

---

# END

**Next Steps**
1. Run `npm install`.
2. Copy `.env.example` to `.env`.
3. Start Postgres.
4. Generate migrations with `npm run db:generate`.
5. Apply migrations with `npm run db:migrate`.
6. Start the API with `npm run dev`.
