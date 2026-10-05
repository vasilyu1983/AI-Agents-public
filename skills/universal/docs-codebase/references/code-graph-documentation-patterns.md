# Code Graph Documentation Patterns

When a repo ships a code graph, document it as a small canonical set:

- JSON schema for inputs and outputs
- generation command
- validation command
- one Markdown report
- optional HTML or Mermaid views

Rules:

- keep raw graph JSON in `graphs/`
- keep validation output in `reports/`
- keep one human-readable canonical report path
- do not duplicate the same graph summary across many docs
- mark parser support and unsupported-language behavior explicitly
