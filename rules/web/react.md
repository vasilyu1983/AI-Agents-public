---
paths:
  - "**/*.tsx"
  - "**/*.jsx"
description: URL, env, server-action, and effect rules for React code.
owner: skills/universal/software-frontend/SKILL.md
---
Extends common/security.md.
- Allow only `http:`, `https:`, and `mailto:` in an `href` or `src` built from user data; do not rely on React to block `javascript:` URLs.
- Treat `NEXT_PUBLIC_*`, `VITE_*`, `REACT_APP_*`, and `EXPO_PUBLIC_*` values as public; never put a secret in them.
- Authenticate, authorise, and schema-parse input in each `"use server"` action; a client-side route guard is not access control.
- Never import a server-only module (database client, secret) into a Client Component; mark it with `import "server-only"`.
- Return a cleanup from each effect that subscribes, sets a timer, or fetches (`AbortController`).
- Enforce `react-hooks/rules-of-hooks` and `react-hooks/exhaustive-deps` in the project's CI.
Why and procedure: skills/universal/software-frontend/references/operational-playbook.md#pattern-frontend-security
