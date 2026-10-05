# External Input Normalization Boundary

Use this pattern when incidents involve malformed external identifiers (domains, URLs, names, IDs) causing downstream failures.

## Problem Pattern

Upstream values are accepted without validation, then treated as canonical technical inputs (for example, display name parsed as domain), causing:
- DNS/network failures
- misleading retries/timeouts
- noisy logs that hide root cause

## Boundary Strategy

1. **Classify** incoming value type.
2. **Normalize** into canonical representation.
3. **Validate** against strict rules for that type.
4. **Route** invalid values to skip/error bucket with reason code.
5. **Proceed** with valid subset only.

## Example Rules

- `domain`: punycode-safe host, contains dot, allowed TLD pattern
- `url`: absolute URL with allowed scheme and host
- `uuid`: strict UUID parse
- `slug`: lowercase + dash format

## Logging Requirements

Log structured fields:
- `input_type`
- `raw_value` (redacted if sensitive)
- `normalized_value`
- `validation_status`
- `validation_error_code`

## Verification

- Add tests for valid/invalid boundary values.
- Confirm invalid values no longer trigger downstream network calls.
- Confirm skip metrics are visible in monitoring.
