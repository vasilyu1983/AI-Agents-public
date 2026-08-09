# Convention Mining Guide

Techniques for identifying implicit coding conventions from an existing codebase.

---
## Table of Contents

- [Quick Mining Process](#quick-mining-process)
- [1. File naming patterns](#1-file-naming-patterns)
- [2. Function naming](#2-function-naming)
- [3. Import patterns](#3-import-patterns)
- [4. Class/interface naming](#4-classinterface-naming)
- [5. Comment patterns](#5-comment-patterns)
- [Naming Convention Detection](#naming-convention-detection)
- [File Naming](#file-naming)
- [Detect dominant file naming pattern](#detect-dominant-file-naming-pattern)
- [Function/Variable Naming](#functionvariable-naming)
- [Extract function names](#extract-function-names)
- [Extract const names](#extract-const-names)
- [Detect pattern](#detect-pattern)
- [camelCase: starts lowercase, has uppercase](#camelcase-starts-lowercase-has-uppercase)
- [SCREAMING_SNAKE: all uppercase with underscores](#screamingsnake-all-uppercase-with-underscores)
- [PascalCase: starts uppercase](#pascalcase-starts-uppercase)
- [Type/Interface Naming](#typeinterface-naming)
- [Find interfaces](#find-interfaces)
- [Check for I-prefix convention](#check-for-i-prefix-convention)
- [Find types](#find-types)
- [Code Organization Detection](#code-organization-detection)
- [Directory Structure Patterns](#directory-structure-patterns)
- [Get directory structure](#get-directory-structure)
- [Common patterns:](#common-patterns)
- [By type: src/{controllers,services,models}/](#by-type-srccontrollersservicesmodels)
- [By feature: src/{user,order,payment}/](#by-feature-srcuserorderpayment)
- [By layer: src/{api,domain,infrastructure}/](#by-layer-srcapidomaininfrastructure)
- [Import Organization](#import-organization)
- [Check import ordering](#check-import-ordering)
- [Look for patterns:](#look-for-patterns)
- [1. External → Internal → Relative](#1-external-→-internal-→-relative)
- [2. Alphabetical](#2-alphabetical)
- [3. Grouped by type](#3-grouped-by-type)
- [Export Patterns](#export-patterns)
- [Barrel exports (index.ts)](#barrel-exports-indexts)
- [Named vs default exports](#named-vs-default-exports)
- [Testing Convention Detection](#testing-convention-detection)
- [Test File Location](#test-file-location)
- [Co-located tests](#co-located-tests)
- [Separate test directory](#separate-test-directory)
- [Test file naming](#test-file-naming)
- [Test Structure](#test-structure)
- [Describe/it pattern](#describeit-pattern)
- [Test naming patterns](#test-naming-patterns)
- [Error Handling Patterns](#error-handling-patterns)
- [Custom error classes](#custom-error-classes)
- [Try-catch patterns](#try-catch-patterns)
- [Error throwing](#error-throwing)
- [Documentation Patterns](#documentation-patterns)
- [Comment Styles](#comment-styles)
- [JSDoc comments](#jsdoc-comments)
- [Single-line comments](#single-line-comments)
- [TODO/FIXME patterns](#todofixme-patterns)
- [README Presence](#readme-presence)
- [READMEs in subdirectories](#readmes-in-subdirectories)
- [Check README content patterns](#check-readme-content-patterns)
- [TypeScript-Specific Patterns](#typescript-specific-patterns)
- [Type Annotations](#type-annotations)
- [Function return types](#function-return-types)
- [Variable type annotations](#variable-type-annotations)
- [Any usage (anti-pattern indicator)](#any-usage-anti-pattern-indicator)
- [Strict Mode](#strict-mode)
- [Check tsconfig](#check-tsconfig)
- [Convention Documentation Template](#convention-documentation-template)
- [Conventions](#conventions)
- [Naming](#naming)
- [File Organization](#file-organization)
- [Code Style](#code-style)
- [Error Handling](#error-handling)
- [Documentation](#documentation)
- [Validation Checklist](#validation-checklist)


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
