# Pagination, Filtering & Sorting Patterns

This guide provides production-ready patterns for implementing pagination, filtering, and sorting in RESTful APIs.

---

## Pagination Strategies

**Use when:** Returning large collections of data to avoid performance issues and improve user experience.

---

## Strategy 1: Offset-Based Pagination (Simple)

**Best for:** Static datasets, reporting, admin interfaces

**Pros:**
- Simple to implement
- Easy to understand
- Jump to any page
- Total count available

**Cons:**
- Performance degrades with large offsets
- Data inconsistency if records added/deleted during pagination
- Not ideal for real-time feeds

### Request Pattern

```
GET /api/v1/users?limit=20&offset=40
```

**Query Parameters:**
- `limit` - Number of items per page (default: 20, max: 100)
- `offset` - Number of items to skip

### Response Format

```json
{
  "data": [
    {
      "id": "41",
      "email": "user41@example.com",
      "name": "User 41"
    },
    {
      "id": "42",
      "email": "user42@example.com",
      "name": "User 42"
    }
  ],
  "meta": {
    "total": 1500,
    "limit": 20,
    "offset": 40,
    "hasMore": true
  },
  "links": {
    "first": "/api/v1/users?limit=20&offset=0",
    "prev": "/api/v1/users?limit=20&offset=20",
    "next": "/api/v1/users?limit=20&offset=60",
    "last": "/api/v1/users?limit=20&offset=1480"
  }
}
```

### Implementation Examples

**SQL (PostgreSQL):**
```sql
SELECT * FROM users
ORDER BY created_at DESC
LIMIT 20 OFFSET 40;
```

**FastAPI (Python):**
```python
@app.get("/api/v1/users")
async def list_users(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    users = result.scalars().all()

    total = await db.scalar(select(func.count(User.id)))

    return {
        "data": users,
        "meta": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "hasMore": offset + limit < total
        }
    }
```

---

## Strategy 2: Cursor-Based Pagination (Recommended)

**Best for:** Real-time feeds, social media, infinite scroll, large datasets

**Pros:**
- Consistent results even when data changes
- Excellent performance (uses indexed columns)
- No duplicate or missing items
- Scalable to billions of records

**Cons:**
- Can't jump to arbitrary page
- Slightly more complex implementation
- Total count expensive to compute

### Request Pattern

```
GET /api/v1/users?limit=20&cursor=eyJpZCI6MTIzLCJjcmVhdGVkQXQiOiIyMDI1LTAxLTE1In0=
```

**Query Parameters:**
- `limit` - Number of items to return
- `cursor` - Base64-encoded cursor (opaque to client)

### Response Format

```json
{
  "data": [
    {
      "id": "124",
      "email": "user124@example.com",
      "createdAt": "2025-01-15T10:30:00Z"
    }
  ],
  "meta": {
    "nextCursor": "eyJpZCI6MTQ0LCJjcmVhdGVkQXQiOiIyMDI1LTAxLTE1VDEyOjAwOjAwWiJ9",
    "prevCursor": "eyJpZCI6MTA0LCJjcmVhdGVkQXQiOiIyMDI1LTAxLTE1VDA5OjAwOjAwWiJ9",
    "hasMore": true
  }
}
```

### Cursor Structure

**Encode cursor as JSON:**
```json
{
  "id": 123,
  "createdAt": "2025-01-15T10:00:00Z"
}
```

**Base64 encode to produce:**
```
eyJpZCI6MTIzLCJjcmVhdGVkQXQiOiIyMDI1LTAxLTE1VDEwOjAwOjAwWiJ9
```

### Implementation Examples

**SQL (PostgreSQL):**
```sql
-- First page (no cursor)
SELECT * FROM users
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- Next page (with cursor)
SELECT * FROM users
WHERE (created_at, id) < ('2025-01-15 10:00:00', 123)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

**FastAPI (Python):**
```python
import base64
import json
from typing import Optional

@app.get("/api/v1/users")
async def list_users(
    limit: int = Query(20, le=100),
    cursor: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(User).order_by(User.created_at.desc(), User.id.desc())

    if cursor:
        cursor_data = json.loads(base64.b64decode(cursor))
        cursor_id = cursor_data["id"]
        cursor_created_at = cursor_data["createdAt"]

        query = query.where(
            or_(
                User.created_at < cursor_created_at,
                and_(
                    User.created_at == cursor_created_at,
                    User.id < cursor_id
                )
            )
        )

    result = await db.execute(query.limit(limit))
    users = result.scalars().all()

    next_cursor = None
    if len(users) == limit:
        last_user = users[-1]
        next_cursor = base64.b64encode(
            json.dumps({
                "id": last_user.id,
                "createdAt": last_user.created_at.isoformat()
            }).encode()
        ).decode()

    return {
        "data": users,
        "meta": {
            "nextCursor": next_cursor,
            "hasMore": next_cursor is not None
        }
    }
```

---

## Strategy 3: Page-Based Pagination

**Best for:** UI with page numbers, user-friendly navigation

### Request Pattern

```
GET /api/v1/users?page=3&per_page=20
```

### Response Format

```json
{
  "data": [...],
  "meta": {
    "currentPage": 3,
    "perPage": 20,
    "totalPages": 75,
    "totalCount": 1500,
    "hasNextPage": true,
    "hasPrevPage": true
  },
  "links": {
    "first": "/api/v1/users?page=1&per_page=20",
    "prev": "/api/v1/users?page=2&per_page=20",
    "next": "/api/v1/users?page=4&per_page=20",
    "last": "/api/v1/users?page=75&per_page=20"
  }
}
```

---

## Filtering Patterns

**Use when:** Clients need to narrow down results based on specific criteria.

### Query Parameter Filtering

**Basic equality:**
```
GET /api/v1/users?status=active
GET /api/v1/users?role=admin
GET /api/v1/users?status=active&role=admin
```

**Comparison operators:**
```
GET /api/v1/users?created_after=2025-01-01
GET /api/v1/users?created_before=2025-12-31
GET /api/v1/users?age_gt=18
GET /api/v1/users?age_lte=65
```

**Pattern matching:**
```
GET /api/v1/users?email_contains=@example.com
GET /api/v1/users?name_startswith=John
GET /api/v1/users?name_endswith=Smith
```

**In/Not in:**
```
GET /api/v1/users?status_in=active,pending
GET /api/v1/users?role_not_in=guest,banned
```

### Filter Operator Conventions

| Suffix | Meaning | Example |
|--------|---------|---------|
| (none) | Exact match | `?status=active` |
| `_gt` | Greater than | `?age_gt=18` |
| `_gte` | Greater than or equal | `?age_gte=18` |
| `_lt` | Less than | `?price_lt=100` |
| `_lte` | Less than or equal | `?price_lte=100` |
| `_contains` | Contains substring | `?email_contains=@gmail` |
| `_startswith` | Starts with | `?name_startswith=John` |
| `_endswith` | Ends with | `?name_endswith=Smith` |
| `_in` | In list | `?status_in=active,pending` |
| `_not_in` | Not in list | `?role_not_in=guest,banned` |

### Advanced Filtering with JSON

For complex filters, use POST with filter JSON:

```http
POST /api/v1/users/search
Content-Type: application/json

{
  "filter": {
    "and": [
      { "status": { "eq": "active" } },
      { "age": { "gte": 18, "lte": 65 } },
      {
        "or": [
          { "role": { "eq": "admin" } },
          { "role": { "eq": "moderator" } }
        ]
      }
    ]
  },
  "limit": 20,
  "cursor": "..."
}
```

---

## Sorting Patterns

**Use when:** Clients need ordered results.

### Single Field Sort

```
GET /api/v1/users?sort=created_at         # Ascending
GET /api/v1/users?sort=-created_at        # Descending (prefix with -)
```

### Multi-Field Sort

```
GET /api/v1/users?sort=name,-created_at
# Sort by name ascending, then by created_at descending
```

### Sort Direction Conventions

| Pattern | Direction | Example |
|---------|-----------|---------|
| `?sort=field` | Ascending | `?sort=name` |
| `?sort=-field` | Descending | `?sort=-created_at` |
| `?sort=field1,field2` | Multi-field | `?sort=name,-age` |

### Alternative Sort Syntax

**Explicit direction:**
```
GET /api/v1/users?sort_by=created_at&order=desc
```

**Array format:**
```
GET /api/v1/users?sort[]=name:asc&sort[]=created_at:desc
```

---

## Combining Pagination, Filtering & Sorting

**Full example:**
```
GET /api/v1/users?status=active&role=admin&sort=-created_at&limit=20&cursor=eyJpZCI6MTIzfQ
```

**Response:**
```json
{
  "data": [
    {
      "id": "124",
      "email": "admin@example.com",
      "status": "active",
      "role": "admin",
      "createdAt": "2025-01-15T10:30:00Z"
    }
  ],
  "meta": {
    "nextCursor": "eyJpZCI6MTQ0fQ",
    "hasMore": true,
    "filters": {
      "status": "active",
      "role": "admin"
    },
    "sort": "-created_at"
  }
}
```

---

## Pagination Best Practices

### Default Limits

```python
# Always enforce max limits
limit: int = Query(20, le=100)  # Default 20, max 100
```

### Include Metadata

```json
{
  "meta": {
    "total": 1500,         // Total count (optional, expensive)
    "limit": 20,           // Items per page
    "offset": 40,          // Current offset
    "hasMore": true,       // More results available
    "nextCursor": "...",   // Cursor for next page
    "prevCursor": "..."    // Cursor for previous page
  }
}
```

### Provide Navigation Links

```json
{
  "links": {
    "first": "/api/v1/users?limit=20&offset=0",
    "prev": "/api/v1/users?limit=20&offset=20",
    "next": "/api/v1/users?limit=20&offset=60",
    "last": "/api/v1/users?limit=20&offset=1480",
    "self": "/api/v1/users?limit=20&offset=40"
  }
}
```

### Consistent Ordering

```sql
-- Always include tiebreaker for consistent pagination
ORDER BY created_at DESC, id DESC
```

---

## Performance Optimization

### Index Filter & Sort Columns

```sql
-- Create indexes on filtered/sorted columns
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
CREATE INDEX idx_users_status_created_at ON users(status, created_at DESC);
```

### Avoid COUNT(*) for Large Tables

```python
# BAD: Expensive for millions of records
total = await db.scalar(select(func.count(User.id)))

# GOOD: Cache total count or skip it
# Only provide "hasMore" flag instead
```

### Use Covering Indexes

```sql
-- Index covers all selected columns (no table lookup needed)
CREATE INDEX idx_users_covering ON users(status, created_at DESC)
INCLUDE (id, email, name);
```

---

## Checklist

- [ ] **Default limits enforced** (e.g., max 100 items per page)
- [ ] **Pagination metadata included** (`hasMore`, `nextCursor`)
- [ ] **Filter operators documented** (e.g., `_gt`, `_contains`)
- [ ] **Sort fields validated** (only allow sorting on indexed columns)
- [ ] **Cursor pagination for real-time feeds**
- [ ] **Offset pagination for static reports**
- [ ] **Consistent ordering** (include tiebreaker like `id`)
- [ ] **Indexes on filter/sort columns**
- [ ] **Max limit enforced** (prevent abuse)
- [ ] **Navigation links provided** (`first`, `prev`, `next`, `last`)

---

## Common Anti-Patterns

### BAD: No Default Limit

```
# Bad - Returns all records
GET /api/v1/users
```

```
# Good - Default limit enforced
GET /api/v1/users?limit=20
```

---

### BAD: No Ordering

```sql
-- Bad - Non-deterministic results
SELECT * FROM users LIMIT 20;
```

```sql
-- Good - Consistent ordering
SELECT * FROM users ORDER BY created_at DESC, id DESC LIMIT 20;
```

---

### BAD: Exposing Database IDs in Cursors

```
# Bad - Leaks database structure
GET /api/v1/users?cursor=123
```

```
# Good - Opaque base64-encoded cursor
GET /api/v1/users?cursor=eyJpZCI6MTIzfQ
```

---

## Decision Matrix: Which Pagination Strategy?

| Use Case | Strategy | Reason |
|----------|----------|--------|
| Social media feed | Cursor-based | Real-time, consistent results |
| Admin dashboard | Offset-based | Jump to pages, total count needed |
| Infinite scroll | Cursor-based | Performance, no duplicate items |
| Report with page numbers | Page-based | User-friendly navigation |
| Large dataset (millions of rows) | Cursor-based | Offset degrades with large offsets |
| Small dataset (<1000 rows) | Offset-based | Simpler, sufficient performance |

---

## Related Resources

- **[restful-design-patterns.md](restful-design-patterns.md)** - RESTful API fundamentals
- **[api-design-best-practices.md](api-design-best-practices.md)** - Comprehensive design guide
- **[error-handling-patterns.md](error-handling-patterns.md)** - Error responses for invalid filters/sorts
- **[openapi-guide.md](openapi-guide.md)** - Documenting pagination parameters
