---
paths:
  - "**/*.ts"
  - "**/*.tsx"
description: Trust-boundary typing rules for TypeScript code.
owner: skills/universal/software-security-appsec/SKILL.md
---
Extends common/security.md.
- Type external input (request bodies, parsed JSON, `catch` variables) as `unknown`, then narrow it or parse it with a schema.
- Parse untrusted JSON with a schema before you merge it into another object; a deep merge or `Object.assign` with a `__proto__` key can rewrite prototypes.
- Enforce these in the project's CI with `strict` in tsconfig and `@typescript-eslint/no-explicit-any`.
Why and procedure: skills/universal/software-security-appsec/references/input-validation.md#pattern-2-data-type-validation
