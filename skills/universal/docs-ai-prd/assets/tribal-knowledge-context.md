# Tribal Knowledge Context Template

Template for documenting implicit knowledge and decisions in CLAUDE.md.

---

```markdown
## Important Context

### Technical Decisions

#### [Decision Title - e.g., "Why PostgreSQL over MongoDB"]

**Context**: [What problem were you solving?]

**Decision**: [What did you choose?]

**Alternatives considered**: [What else was evaluated?]

**Trade-offs**: [What did you gain/lose?]

**Date**: [When was this decided?]

**Reference**: [Link to ADR, RFC, or discussion if available]

---

#### [Decision Title - e.g., "Auth0 for Authentication"]

**Context**: [Problem statement]

**Decision**: [Solution chosen]

**Alternatives considered**: [Options evaluated]

**Trade-offs**: [Pros/cons]

**Date**: [Decision date]

---

### Known Gotchas

- **[Component/Feature]**: [Non-obvious behavior or issue]
  - Workaround: [How to handle it]

- **[API/Function]**: [Unexpected behavior]
  - Example: `UserService.create()` triggers async email - don't await in tests

- **[Integration]**: [External service quirk]
  - Note: [How to deal with it]

### Historical Context

#### Migrations

- **[Date]**: Migrated from [X] to [Y]
  - Reason: [Why the change]
  - Legacy: [Any remaining legacy code/patterns]

#### Deprecated Patterns

- **[Pattern name]**: [Why deprecated]
  - Old way: [How it used to work]
  - New way: [Current approach]
  - Migration status: [Complete/In progress/Not started]

### Why Things Are the Way They Are

- **[File/Directory]**: [Why it's structured this way]
- **[Unusual pattern]**: [Historical reason or constraint]
- **[Naming choice]**: [Context for non-obvious names]

### Things That Look Wrong But Aren't

- **[Code pattern]**: [Why it's intentional]
- **[Configuration]**: [Why it's set this way]
- **[Dependency version]**: [Why pinned to specific version]

### External Dependencies

- **[Service name]**: [Special handling required]
  - Rate limits: [Limits to be aware of]
  - Quirks: [API oddities]

### Performance Considerations

- **[Component]**: [Performance characteristic]
  - Bottleneck: [What causes slowdowns]
  - Optimization: [Current approach]

### Security Notes

- **[Area]**: [Security consideration]
  - Reason: [Why it matters]
  - Mitigation: [How it's handled]
```

---

## How to Gather Tribal Knowledge

### Git History Mining

```bash
# Find commits explaining "why"
git log --all --oneline --grep="because\|reason\|workaround\|hack\|fix"

# Find commits about decisions
git log --all --oneline --grep="migrate\|switch\|replace\|remove"

# Find significant refactors
git log --all --oneline --grep="refactor\|restructure\|reorganize"
```

### Code Comment Mining

```bash
# Find explanatory comments
grep -r "NOTE:\|TODO:\|HACK:\|FIXME:\|XXX:" --include="*.ts" --include="*.js"

# Find "why" comments
grep -r "because\|workaround\|legacy\|deprecated" --include="*.ts"
```

### Documentation Sources

- README files in subdirectories
- ADRs (Architecture Decision Records)
- Wiki pages
- Slack/Discord discussions
- PR descriptions and comments
- Issue tracker discussions

## Usage

1. Interview team members about "why" questions
2. Mine git history for decision context
3. Document gotchas as you encounter them
4. Update when things change
