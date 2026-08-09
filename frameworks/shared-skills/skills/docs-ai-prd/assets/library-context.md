# Library/Package CLAUDE.md Template

Template for reusable libraries and npm/pip/crate packages.

---

```markdown
# [Library Name]

[One-line description of what this library does]

## Overview

- **Type**: [npm package / pip package / cargo crate / go module]
- **Language**: [TypeScript / JavaScript / Python / Rust / Go]
- **Target**: [Browser / Node.js / Both / Universal]
- **Bundler**: [Rollup / esbuild / tsup / Vite / None]
- **Testing**: [Vitest / Jest / pytest / cargo test]

## Installation

```bash
# npm
npm install [package-name]

# yarn
yarn add [package-name]

# pnpm
pnpm add [package-name]
```

## Quick Start

```typescript
import { mainFunction } from '[package-name]';

// Basic usage
const result = mainFunction(input);

// With options
const result = mainFunction(input, {
  option1: true,
  option2: 'value',
});
```

## Architecture

### Directory Structure

```
src/
├── index.ts            # Main entry, public exports
├── core/               # Core functionality
│   ├── main.ts         # Main function
│   └── utils.ts        # Internal utilities
├── types/              # Type definitions
│   ├── index.ts        # Public types
│   └── internal.ts     # Internal types
└── __tests__/          # Tests
    └── main.test.ts

# Build outputs
dist/
├── index.js            # CommonJS
├── index.mjs           # ESM
├── index.d.ts          # Type declarations
└── index.min.js        # Minified (browser)
```

### Module Exports

```typescript
// package.json exports
{
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.mjs",
      "require": "./dist/index.js"
    },
    "./utils": {
      "types": "./dist/utils.d.ts",
      "import": "./dist/utils.mjs",
      "require": "./dist/utils.js"
    }
  }
}
```

## Public API

### Main Exports

```typescript
// Functions
export function mainFunction(input: Input, options?: Options): Output;
export function helperFunction(data: Data): Result;

// Classes
export class MainClass {
  constructor(config: Config);
  method1(): void;
  method2(arg: string): Promise<Result>;
}

// Types
export type Input = { ... };
export type Output = { ... };
export type Options = { ... };

// Constants
export const VERSION: string;
export const DEFAULT_OPTIONS: Options;
```

### Type Definitions

```typescript
// src/types/index.ts
export interface Options {
  /** Enable verbose logging */
  verbose?: boolean;
  /** Timeout in milliseconds */
  timeout?: number;
  /** Custom handler function */
  onEvent?: (event: Event) => void;
}

export interface Result {
  success: boolean;
  data?: unknown;
  error?: Error;
}
```

## Conventions

### Code Style

- Pure functions where possible
- No side effects in core logic
- Explicit return types on public API
- JSDoc comments on all exports

### Naming

| Type | Convention | Example |
|------|------------|---------|
| Public functions | camelCase | `parseConfig` |
| Internal functions | _camelCase | `_validateInput` |
| Types/Interfaces | PascalCase | `ConfigOptions` |
| Constants | SCREAMING_SNAKE | `DEFAULT_TIMEOUT` |

### Error Handling

```typescript
// Custom error class
export class LibraryError extends Error {
  constructor(
    message: string,
    public code: string,
    public cause?: Error
  ) {
    super(message);
    this.name = 'LibraryError';
  }
}

// Usage
throw new LibraryError(
  'Invalid configuration',
  'INVALID_CONFIG',
  originalError
);
```

## Key Files

| Purpose | Location | Notes |
|---------|----------|-------|
| Entry point | `src/index.ts` | All public exports |
| Types | `src/types/index.ts` | Public type definitions |
| Core logic | `src/core/` | Main functionality |
| Build config | `tsup.config.ts` | Build configuration |
| Package config | `package.json` | npm metadata, exports |

## Development

```bash
# Install dependencies
npm install

# Development (watch mode)
npm run dev

# Build
npm run build

# Test
npm test
npm run test:watch
npm run test:coverage

# Lint & Format
npm run lint
npm run format

# Type check
npm run typecheck

# Release
npm run release    # Bumps version, builds, publishes
```

## Testing

### Test Structure

```typescript
// src/__tests__/main.test.ts
import { mainFunction } from '../index';

describe('mainFunction', () => {
  it('handles basic input', () => {
    const result = mainFunction({ key: 'value' });
    expect(result.success).toBe(true);
  });

  it('throws on invalid input', () => {
    expect(() => mainFunction(null as any)).toThrow(LibraryError);
  });

  it('respects options', () => {
    const result = mainFunction(input, { timeout: 5000 });
    expect(result.timeout).toBe(5000);
  });
});
```

### Coverage Requirements

- Statements: > 90%
- Branches: > 85%
- Functions: > 90%
- Lines: > 90%

## Publishing

### Pre-publish Checklist

- [ ] All tests pass
- [ ] Types are correct
- [ ] CHANGELOG updated
- [ ] Version bumped
- [ ] README updated
- [ ] Examples work

### Versioning

- **patch**: Bug fixes, no API changes
- **minor**: New features, backward compatible
- **major**: Breaking changes

## Important Context

### Design Decisions

- **[Decision]**: [Why this approach was chosen]
- **[Trade-off]**: [What was sacrificed for what gain]

### Known Limitations

- [Limitation 1 and workaround]
- [Limitation 2 and planned fix]

### Browser Support

- Chrome 80+
- Firefox 78+
- Safari 13.1+
- Edge 80+
- Node.js 16+

## For AI Assistants

### When modifying:

- Maintain backward compatibility for minor/patch versions
- Add JSDoc comments to public API
- Update types when changing signatures
- Add tests for new functionality

### Avoid:

- Breaking changes without major version bump
- Side effects in core functions
- Dependencies with large bundle size
- Platform-specific code without fallbacks
```

---

## Discovery Commands

```bash
# Check entry points
cat package.json | jq '.main, .module, .exports'

# Find public exports
grep -r "export " --include="*.ts" src/index.ts

# Check bundle size
npm run build && du -h dist/
```
