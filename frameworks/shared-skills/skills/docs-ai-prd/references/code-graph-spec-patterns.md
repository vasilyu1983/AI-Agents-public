# Code Graph Spec Patterns

Use this pattern when the deliverable includes a generated code graph.

## Required Decisions

- supported languages
- parser strategy per language
- node types and edge relations
- output paths
- validation checks
- query expectations
- unsupported-language fallback

## Minimum Acceptance Criteria

- one canonical JSON schema for the code profile
- one canonical JSON schema for the graph
- deterministic generation command
- deterministic validation command
- documented blast-radius query
- explicit confidence and fallback rules

## V1 Template

1. Problem and user of the graph
2. Repository scope
3. Supported languages and exclusions
4. Output contract (`code-profiles/`, `graphs/`, `reports/`)
5. Node and edge ontology
6. Validation checks
7. Acceptance criteria
