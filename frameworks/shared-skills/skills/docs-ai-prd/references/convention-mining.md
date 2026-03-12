# Convention Mining Guide

Techniques for identifying implicit coding conventions from an existing codebase.

---

## Quick Mining Process

```bash
# 1. File naming patterns
ls -la src/ | head -20
find src -name "*.ts" | xargs basename -a | sort | uniq -c | sort -rn | head -20

# 2. Function naming
grep -rh "^export function\|^function\|^const.*=" --include="*.ts" | head -30

# 3. Import patterns
grep -rh "^import" --include="*.ts" | sort | uniq -c | sort -rn | head -20

# 4. Class/interface naming
grep -rh "^export class\|^export interface\|^interface\|^class" --include="*.ts"

# 5. Comment patterns
grep -rh "// \|/\*\|TODO\|FIXME\|NOTE" --include="*.ts" | head -20
```

---

## Naming Convention Detection

### File Naming

| Pattern | Example | Detection |
|---------|---------|-----------|
| kebab-case | `user-service.ts` | `ls src \| grep -E "^[a-z]+-[a-z]+"` |
| camelCase | `userService.ts` | `ls src \| grep -E "^[a-z]+[A-Z]"` |
| PascalCase | `UserService.ts` | `ls src \| grep -E "^[A-Z][a-z]+"` |
| snake_case | `user_service.ts` | `ls src \| grep -E "^[a-z]+_[a-z]+"` |

```bash
# Detect dominant file naming pattern
find src -name "*.ts" -type f | xargs basename -a | \
  awk '{
    if (/^[a-z]+-[a-z]/) kebab++;
    else if (/^[a-z]+[A-Z]/) camel++;
    else if (/^[A-Z][a-z]+[A-Z]/) pascal++;
    else if (/^[a-z]+_[a-z]/) snake++;
  }
  END {
    print "kebab-case:", kebab;
    print "camelCase:", camel;
    print "PascalCase:", pascal;
    print "snake_case:", snake;
  }'
```

### Function/Variable Naming

```bash
# Extract function names
grep -roh "function [a-zA-Z_][a-zA-Z0-9_]*" --include="*.ts" | \
  sed 's/function //' | sort | uniq -c | sort -rn | head -20

# Extract const names
grep -roh "const [a-zA-Z_][a-zA-Z0-9_]*" --include="*.ts" | \
  sed 's/const //' | sort | uniq -c | sort -rn | head -20

# Detect pattern
# camelCase: starts lowercase, has uppercase
# SCREAMING_SNAKE: all uppercase with underscores
# PascalCase: starts uppercase
```

### Type/Interface Naming

```bash
# Find interfaces
grep -rh "^interface\|^export interface" --include="*.ts" | \
  sed 's/.*interface //' | sed 's/[<{ ].*//' | sort -u

# Check for I-prefix convention
grep -rh "^interface I[A-Z]" --include="*.ts" | wc -l
grep -rh "^interface [A-Z][a-z]" --include="*.ts" | wc -l

# Find types
grep -rh "^type\|^export type" --include="*.ts" | \
  sed 's/.*type //' | sed 's/[<= ].*//' | sort -u
```

---

## Code Organization Detection

### Directory Structure Patterns

```bash
# Get directory structure
tree -L 2 -d -I 'node_modules|dist|.git'

# Common patterns:
# By type: src/{controllers,services,models}/
# By feature: src/{user,order,payment}/
# By layer: src/{api,domain,infrastructure}/
```

### Import Organization

```bash
# Check import ordering
head -30 $(find src -name "*.ts" | head -5)

# Look for patterns:
# 1. External → Internal → Relative
# 2. Alphabetical
# 3. Grouped by type
```

### Export Patterns

```bash
# Barrel exports (index.ts)
find src -name "index.ts" -exec cat {} \;

# Named vs default exports
grep -rh "^export default" --include="*.ts" | wc -l
grep -rh "^export {" --include="*.ts" | wc -l
grep -rh "^export const\|^export function\|^export class" --include="*.ts" | wc -l
```

---

## Testing Convention Detection

### Test File Location

```bash
# Co-located tests
find src -name "*.test.ts" -o -name "*.spec.ts"

# Separate test directory
ls __tests__/ 2>/dev/null || ls test/ 2>/dev/null || ls tests/ 2>/dev/null

# Test file naming
find . -name "*.test.ts" | head -10
find . -name "*.spec.ts" | head -10
```

### Test Structure

```bash
# Describe/it pattern
grep -rh "describe\|it\|test\(" --include="*.test.ts" | head -20

# Test naming patterns
grep -rh "it\('" --include="*.test.ts" | sed "s/.*it('//" | sed "s/',.*//" | head -20
```

---

## Error Handling Patterns

```bash
# Custom error classes
grep -rh "class.*Error\|extends Error" --include="*.ts"

# Try-catch patterns
grep -rh "try {" --include="*.ts" | wc -l
grep -rh "catch (e" --include="*.ts" | wc -l

# Error throwing
grep -rh "throw new" --include="*.ts" | head -10
```

---

## Documentation Patterns

### Comment Styles

```bash
# JSDoc comments
grep -rh "/\*\*" --include="*.ts" | wc -l

# Single-line comments
grep -rh "^[[:space:]]*//" --include="*.ts" | wc -l

# TODO/FIXME patterns
grep -rh "TODO:\|FIXME:\|HACK:\|NOTE:" --include="*.ts"
```

### README Presence

```bash
# READMEs in subdirectories
find . -name "README.md" | head -20

# Check README content patterns
head -50 README.md
```

---

## TypeScript-Specific Patterns

### Type Annotations

```bash
# Function return types
grep -roh "): [A-Za-z<>\[\]|&]* {" --include="*.ts" | head -20

# Variable type annotations
grep -roh ": [A-Za-z<>\[\]]* =" --include="*.ts" | head -20

# Any usage (anti-pattern indicator)
grep -rh ": any" --include="*.ts" | wc -l
```

### Strict Mode

```bash
# Check tsconfig
cat tsconfig.json | jq '.compilerOptions.strict'
cat tsconfig.json | jq '.compilerOptions.strictNullChecks'
```

---

## Convention Documentation Template

After mining, document findings:

```markdown
## Conventions

### Naming

| Type | Convention | Examples |
|------|------------|----------|
| Files | [detected] | [examples from codebase] |
| Functions | [detected] | [examples] |
| Classes | [detected] | [examples] |
| Constants | [detected] | [examples] |
| Interfaces | [detected] | [examples] |

### File Organization

- Export pattern: [barrel/named/default]
- Import order: [external → internal → relative]
- Test location: [co-located/__tests__/tests/]

### Code Style

- [Detected linter]: [ESLint/Prettier config]
- Semicolons: [yes/no]
- Quotes: [single/double]
- Indentation: [2/4 spaces/tabs]

### Error Handling

- [Pattern detected from codebase]

### Documentation

- Comment style: [JSDoc/inline/none]
- README presence: [root only/per directory]
```

---

## Validation Checklist

After mining conventions:

- [ ] File naming pattern identified
- [ ] Function/variable naming documented
- [ ] Import/export patterns noted
- [ ] Test conventions documented
- [ ] Error handling pattern clear
- [ ] Linter/formatter config checked
- [ ] TypeScript strictness noted
- [ ] Documentation style identified
