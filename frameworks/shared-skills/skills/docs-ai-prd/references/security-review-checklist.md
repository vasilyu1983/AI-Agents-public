# AI-Assisted Development Security Checklist

Purpose: security checklist for coding-agent workflows and AI product specs.

Last verified: 2026-03-13

## Table of Contents

- [1. Boundary Setup Before Development](#1-boundary-setup-before-development)
- [2. Threat Model The Workflow](#2-threat-model-the-workflow)
- [3. Prompt And Context Hygiene](#3-prompt-and-context-hygiene)
- [4. Generated Code Review Checklist](#4-generated-code-review-checklist)
- [5. Tool Use Safeguards](#5-tool-use-safeguards)
- [6. Dependency And Supply-Chain Checks](#6-dependency-and-supply-chain-checks)
- [7. AI Feature Review Checks](#7-ai-feature-review-checks)
- [8. Release Gates](#8-release-gates)
- [9. Incident Readiness](#9-incident-readiness)
- [Useful References](#useful-references)

## 1. Boundary Setup Before Development

- [ ] Define which files, services, and environments the agent may access
- [ ] Configure the tool's deny / ignore / allowlist surface using official docs
- [ ] Exclude secrets, credentials, customer data, and production configs
- [ ] Separate read-only exploration from mutating actions
- [ ] Require approval for destructive commands, migrations, and external side effects

## 2. Threat Model The Workflow

Cover at least:
- [ ] Prompt injection from user-provided content
- [ ] Data exfiltration through prompts, logs, or tool output
- [ ] Unsafe tool invocation or autonomous side effects
- [ ] Insecure generated code
- [ ] Dependency supply-chain risk
- [ ] Excessive logging of sensitive content

## 3. Prompt And Context Hygiene

- [ ] Treat user-provided text and third-party docs as untrusted input
- [ ] Prefer file paths and canonical docs over copy-pasting sensitive code
- [ ] Do not paste secrets, tokens, or incident data into prompts
- [ ] Label untrusted content clearly when it must be analyzed
- [ ] Keep approvals explicit when the agent can call tools

## 4. Generated Code Review Checklist

- [ ] Authentication and authorization are correct
- [ ] Inputs are validated and normalized
- [ ] Queries are parameterized
- [ ] Output encoding / escaping is correct
- [ ] Error handling does not leak sensitive details
- [ ] Rate limiting, retries, and backoff are appropriate
- [ ] Sensitive operations are logged safely and auditable
- [ ] Feature flags or kill switches exist where needed

High-risk areas requiring extra review:
- auth flows
- file uploads
- shell execution
- database migrations
- payment or identity workflows
- AI systems with autonomous side effects

## 5. Tool Use Safeguards

- [ ] The workflow documents what the agent may execute without approval
- [ ] Commands with side effects require explicit approval or tightly scoped automation
- [ ] Network access is limited to approved domains where possible
- [ ] Tool outputs are reviewed before applying irreversible changes
- [ ] Production writes are separated from planning and testing

## 6. Dependency And Supply-Chain Checks

- [ ] Review new dependencies before adding them
- [ ] Run dependency audits after agent-generated dependency changes
- [ ] Verify package legitimacy and maintenance status
- [ ] Keep lockfiles committed and updated
- [ ] Prefer well-maintained packages over obscure transitive additions

## 7. AI Feature Review Checks

Use this when the product itself contains AI behavior.

- [ ] Prompt injection and tool misuse risks are documented
- [ ] Data retention and vendor data use are documented
- [ ] Eval datasets are owned, versioned, and access-controlled
- [ ] Monitoring covers unsafe output, drift, and abuse
- [ ] Rollback triggers and kill switch owner are defined
- [ ] Autonomous side effects have approval boundaries and audit trails

## 8. Release Gates

Do not release until:
- [ ] required tests pass
- [ ] security review findings are resolved or accepted explicitly
- [ ] monitoring and alerting are defined
- [ ] secrets scanning has run
- [ ] rollback path is documented

## 9. Incident Readiness

- [ ] Incident severity levels are defined
- [ ] Ownership is named
- [ ] Logging policy avoids storing sensitive prompt or customer data unnecessarily
- [ ] Alert thresholds are documented
- [ ] Containment and rollback steps are known before launch

## Useful References

- OWASP GenAI security guidance
- NIST AI RMF 1.0
- NIST Generative AI Profile
- OWASP Cheat Sheet Series
- language/framework-specific AppSec standards already used by the repo

Use the exact URLs from `data/sources.json` when citing external guidance.
