# Cookbook: Multimodal Assembly

This cookbook is for assistants that work across docs, screenshots, files,
tables, and tool outputs.

## Pattern

- request carries pointers
- loader returns typed artifacts
- formatter emits short projections
- bundle stays within text and artifact budgets

## Projection defaults

- documents -> title + short excerpt + source/evidence IDs
- images -> OCR/summary + metadata
- tool outputs -> selected fields only
- tables -> key metrics or rows, not raw exports

## Guardrails

- keep raw payloads out of the bundle
- preserve provenance after projection
- cap artifact count separately from token count
- move heavy artifact reasoning to P11 sub-agents when needed

## Verification

- mixed-modality requests stay under budget
- wrong-scope artifact loads fail fast
- projections stay readable and auditable after compression
