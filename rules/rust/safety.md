---
paths:
  - "**/*.rs"
description: Panic, unsafe, SQL, and enum-match rules for Rust code.
owner: skills/universal/software-backend/SKILL.md
---
Extends common/errors.md.
- Never call `unwrap()` or `expect()` outside tests and states proven unreachable; propagate with `?` and add context.
- Put a `// SAFETY:` comment on every `unsafe` block that names each invariant it relies on.
- Bind SQL parameters (`.bind()`, `$1`); never build SQL with `format!`.
- Match business enums exhaustively, with no `_` arm.
- Enforce these in the project's CI with clippy (`unwrap_used`, `undocumented_unsafe_blocks`, `wildcard_enum_match_arm`) and `cargo audit` or `cargo deny`.
Why and procedure: skills/universal/software-backend/references/rust-best-practices.md#error-handling
