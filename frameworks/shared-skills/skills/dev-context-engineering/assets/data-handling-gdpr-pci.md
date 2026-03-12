# Data Handling Rules: GDPR and PCI DSS

> Copy this file to `.claude/rules/data-handling-gdpr-pci.md` in every repository.
> This is a MANDATORY rule file for organizations handling personal data or payment card data.

## Safe Data Categories

These categories are safe to include in agent context, code comments, specs, and plans:

- Code abstractions and design patterns
- Business logic descriptions (without real customer examples)
- Synthetic test data with clearly fake values
- Architecture diagrams and data flow descriptions
- API endpoint definitions and schemas
- Error codes and status definitions
- Configuration templates with placeholder values
- Performance metrics and SLAs (anonymized)

## Prohibited Data Categories

NEVER include any of the following in agent context, prompts, code, comments, commit messages, PR descriptions, specs, plans, or any file processed by AI agents:

### Personal Data (GDPR)
- Names, email addresses, phone numbers of real individuals
- Physical addresses, IP addresses, location data
- Dates of birth, national insurance numbers, passport numbers
- Financial account details (bank account numbers, sort codes)
- Health data, biometric data, genetic data
- Racial/ethnic origin, political opinions, religious beliefs
- Trade union membership, sexual orientation
- Any data that could identify a living individual directly or indirectly

### Payment Card Data (PCI DSS)
- Primary Account Numbers (PANs) — real or realistic-looking
- Cardholder names associated with card data
- Card expiry dates associated with card data
- CVV/CVC/CAV codes
- PIN blocks or encrypted PIN data
- Track data (magnetic stripe or chip equivalent)
- Service codes

### Credentials and Secrets
- API keys, tokens, passwords
- Database connection strings with credentials
- Private keys (SSL, SSH, GPG)
- OAuth client secrets
- Webhook signing secrets
- Encryption keys or key material

## Test Data Guidelines

When tests need data that resembles real data:

```
# Good: Clearly synthetic
name: "Test User Alpha"
email: "test-alpha@example.com"
card: "4242 4242 4242 4242" (Stripe test card)
phone: "+44 7700 900000" (Ofcom test range)

# Bad: Could be real
name: "John Smith"
email: "john.smith@gmail.com"
card: "4532 1234 5678 9012" (looks real)
phone: "+44 7911 123456" (could be real)
```

## Context Filtering Patterns

When AI agents work with code that processes sensitive data:

- Reference data by TYPE, not by VALUE: "the customer's email field" not "john@example.com"
- Use schema definitions instead of data samples
- Describe transformations abstractly: "hash the PAN before storage" not "hash 4532..."
- Link to data flow documentation rather than embedding data examples

## Incident Response

If sensitive data is accidentally committed:

1. **Do not push** if not yet pushed
2. Immediately notify the security team and DPO
3. Use `git filter-branch` or BFG Repo-Cleaner to remove from history
4. Rotate any exposed credentials immediately
5. Document the incident per operational resilience framework
6. Assess if a breach notification is required (72-hour GDPR window)
