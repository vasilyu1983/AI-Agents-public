# Pull Request Template with AI Disclosure

> Copy this file to `.github/pull_request_template.md` in every repository.

```markdown
## Summary

<!-- Brief description of what this PR does and why -->

## Changes

<!-- Bulleted list of changes -->

-

## AI Involvement Disclosure

### AI Tools Used
<!-- Check all that apply -->
- [ ] Claude Code
- [ ] Codex
- [ ] Cursor
- [ ] GitHub Copilot
- [ ] Other: ___
- [ ] No AI tools used

### AI Role
<!-- Check all that apply -->
- [ ] Generated code
- [ ] Reviewed/analyzed code
- [ ] Generated tests
- [ ] Assisted debugging
- [ ] Generated documentation
- [ ] Planned implementation

### Files Primarily AI-Generated
<!-- List files where >50% of the code was AI-generated, or write "None" -->

-

### Human Verification Checklist
<!-- All boxes must be checked before merge approval -->
- [ ] I have read and understand all AI-generated code in this PR
- [ ] I have verified the code works as intended (ran tests, manual testing)
- [ ] I have reviewed for security concerns (injection, auth, data exposure)
- [ ] I have checked compliance with coding standards and architecture patterns
- [ ] I have verified no sensitive data (PII, credentials, card data) is included
- [ ] I have confirmed the code does not introduce unintended side effects

## Test Plan

<!-- How was this tested? -->

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] No testing needed (docs/config only)

## Compliance
<!-- For changes to auth/, payments/, crypto/, compliance/ directories -->
- [ ] Security review requested (if applicable)
- [ ] Compliance review requested (if applicable)
- [ ] N/A — no security-critical changes
```
