---
paths:
  - "**/*.tsx"
  - "**/*.jsx"
  - "**/*.html"
  - "**/*.vue"
description: DOM injection and browser-storage rules for web UI files.
owner: skills/universal/software-frontend/SKILL.md
---
Extends common/security.md.
- Never pass untrusted data to `innerHTML`, `dangerouslySetInnerHTML`, or `v-html`; sanitise rich text first, for example with DOMPurify.
- Never store sensitive data in `localStorage`; use httpOnly cookies.
- Never embed secrets or tokens in HTML.
- Enforce these in the project's CI with lint rules, such as eslint `react/no-danger`.
Why and procedure: skills/universal/software-frontend/references/operational-playbook.md#pattern-frontend-security
