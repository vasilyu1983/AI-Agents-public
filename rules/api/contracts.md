---
paths:
  - "**/openapi*.yaml"
  - "**/openapi*.json"
  - "**/*.proto"
  - "**/*.graphql"
description: Breaking-change gate for API contract files.
owner: skills/universal/dev-api-design/SKILL.md
---
Extends common/dependencies.md.
- Run a schema-breaking diff in CI on every contract change: oasdiff for OpenAPI, `buf breaking` for protobuf, GraphQL Inspector for GraphQL.
- Treat that diff as a floor. Review semantic changes by hand, such as a narrowed enum or validation rule, or a changed field meaning.
Why and procedure: skills/universal/dev-api-design/SKILL.md#expert-judgment
