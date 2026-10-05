---
paths:
  - "**/routers/**/*.py"
  - "**/routes/**/*.py"
  - "**/api/**/*.py"
  - "**/*_api.py"
description: Async, response-model, CORS, and JWT rules for FastAPI handlers.
owner: skills/universal/software-backend/SKILL.md
---
Extends common/security.md.
- Never call `requests`, a sync DB session, `time.sleep`, or blocking file I/O inside an `async def` handler; use an async client, or `asyncio.to_thread` for unavoidable blocking work.
- Inject DB sessions and clients through `Depends`; never create them inside a handler.
- Give each endpoint that returns application data a `response_model` that leaves out password hashes, tokens, and internal auth state.
- Never combine a wildcard CORS origin with credentials.
- Verify JWT expiry, issuer, audience, and an allow-listed algorithm.
- Clear `app.dependency_overrides` after each test.
Why and procedure: skills/universal/software-backend/references/python-best-practices.md#fastapi-best-practices
