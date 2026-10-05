# Contributing to [Project Name]

Thank you for your interest in contributing! We welcome contributions from everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

This project adheres to the `CODE_OF_CONDUCT.md`. By participating, you are expected to uphold this code. Please report unacceptable behavior to [conduct@example.com](mailto:conduct@example.com).

## Getting Started

### Prerequisites

Before you begin, ensure you have:

- [Node.js](https://nodejs.org/) 18.0 or higher
- [Git](https://git-scm.com/)
- A GitHub account
- Familiarity with JavaScript/TypeScript
- Basic understanding of the project architecture

### Finding Issues to Work On

- **Good first issues**: Check issues labeled [`good first issue`](https://github.com/username/repo/labels/good%20first%20issue)
- **Help wanted**: Issues labeled [`help wanted`](https://github.com/username/repo/labels/help%20wanted) are open for contribution
- **Bug fixes**: Look for issues labeled [`bug`](https://github.com/username/repo/labels/bug)

## Development Setup

### 1. Fork the Repository

Fork the repository to your GitHub account by clicking the "Fork" button.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/project-name.git
cd project-name
```

### 3. Add Upstream Remote

```bash
git remote add upstream https://github.com/original-owner/project-name.git
```

### 4. Install Dependencies

```bash
npm install
```

### 5. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

**Branch naming conventions:**
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring
- `test/description` - Test improvements

### 6. Run Development Server

```bash
npm run dev
```

The application will be available at http://localhost:3000

### 7. Run Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check if the issue already exists.

**When filing a bug report, include:**

- **Title**: Clear, descriptive summary
- **Description**: Detailed description of the issue
- **Steps to Reproduce**: Step-by-step instructions
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Node.js version, browser (if applicable)
- **Screenshots**: If applicable
- **Logs**: Relevant error messages or logs

**Bug Report Template:**

```markdown
## Description
A clear description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g., macOS 13.0]
- Node.js: [e.g., 18.16.0]
- Browser: [e.g., Chrome 115]

## Additional Context
Any other context, screenshots, or logs.
```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please create an issue with:

- **Clear title**: Concise description of the enhancement
- **Use case**: Why this enhancement would be useful
- **Detailed description**: How it should work
- **Mockups/Examples**: If applicable

### Submitting Code Changes

1. **Create or find an issue**: Ensure there's an issue for your change
2. **Discuss your approach**: Comment on the issue before starting work
3. **Fork and create a branch**: Follow the branching guidelines
4. **Make your changes**: Write code following our standards
5. **Write tests**: Add tests for new functionality
6. **Update documentation**: Update relevant docs
7. **Run tests and linters**: Ensure all checks pass
8. **Commit your changes**: Use conventional commit messages
9. **Push to your fork**: `git push origin feature/your-feature`
10. **Open a Pull Request**: From your fork to the main repository

## Coding Standards

### JavaScript/TypeScript Style

We follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript) with some modifications.

**Key Points:**

- Use 2 spaces for indentation
- Use single quotes for strings
- Always use semicolons
- Use camelCase for variables and functions
- Use PascalCase for classes and types
- Use UPPER_SNAKE_CASE for constants
- Prefer `const` over `let`, avoid `var`
- Use arrow functions for anonymous functions
- Use template literals for string interpolation

**Example:**

```javascript
// Good
const getUserName = (user) => {
  return user.firstName + ' ' + user.lastName;
};

const MAX_RETRY_COUNT = 3;

// Bad
var get_user_name = function(user) {
  return user.firstName + " " + user.lastName
}

const maxRetryCount = 3;
```

### Linting and Formatting

Run ESLint and Prettier before committing:

```bash
# Lint code
npm run lint

# Fix linting errors automatically
npm run lint:fix

# Format code
npm run format

# Type check (TypeScript)
npm run type-check
```

**Pre-commit hook automatically runs these checks.**

### TypeScript Guidelines

- Use strict type checking
- Avoid `any` type (use `unknown` if type is truly unknown)
- Define interfaces for all object shapes
- Use type guards for type narrowing
- Document complex types with JSDoc comments

**Example:**

```typescript
// Good
interface User {
  id: string;
  name: string;
  email: string;
}

function getUser(id: string): User | null {
  // implementation
}

// Bad
function getUser(id: any): any {
  // implementation
}
```

### File and Folder Structure

```
src/
├── api/            # API routes and controllers
├── models/         # Database models
├── services/       # Business logic
├── utils/          # Helper functions
├── types/          # TypeScript type definitions
└── __tests__/      # Test files (co-located with source)
```

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `build`: Build system or dependency changes
- `ci`: CI configuration changes
- `chore`: Other changes that don't modify src or test files

### Scope

Optional, indicates the area of the codebase (e.g., `auth`, `api`, `ui`).

### Subject

- Use imperative mood ("add" not "added")
- Don't capitalize first letter
- No period at the end
- Limit to 50 characters

### Body

- Optional, provides additional context
- Wrap at 72 characters
- Explain what and why, not how

### Footer

- Optional, references issues or breaking changes
- Use `Closes #123` to auto-close issues
- Use `BREAKING CHANGE:` for breaking changes

### Examples

```
feat(auth): add OAuth2 authentication

Implements OAuth2 authorization code flow with Google and GitHub providers.
Includes token refresh and secure storage.

Closes #123
```

```
fix(api): handle null response from database

Adds null check before accessing user.email property to prevent TypeError.

Fixes #456
```

```
docs: update API documentation for v2 endpoints

BREAKING CHANGE: v1 endpoints are deprecated and will be removed in next major release
```

## Pull Request Process

### Before Submitting

- [ ] Create an issue if one doesn't exist
- [ ] Fork the repository
- [ ] Create a feature branch
- [ ] Write code following our standards
- [ ] Add tests for new functionality
- [ ] Update documentation
- [ ] Run tests: `npm test`
- [ ] Run linter: `npm run lint`
- [ ] Ensure type checking passes: `npm run type-check`
- [ ] Commit with conventional commit messages
- [ ] Rebase on latest `main` if needed

### PR Title and Description

**Title Format:**
```
<type>(<scope>): <short summary>
```

**Description Template:**
```markdown
## Description
Brief description of changes

## Related Issue
Closes #123

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] All tests pass locally
- [ ] Added tests for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added and passing

## Screenshots (if applicable)
```

### Review Process

1. **Automated checks**: CI must pass (tests, linting, type checking)
2. **Code review**: At least one maintainer approval required
3. **Discussion**: Address reviewer feedback
4. **Approval**: Once approved, a maintainer will merge

### After PR is Merged

1. Delete your feature branch
2. Pull latest main: `git pull upstream main`
3. Thank the reviewers!

## Testing Guidelines

### Writing Tests

- **Unit tests**: Test individual functions and modules
- **Integration tests**: Test interactions between components
- **E2E tests**: Test complete user workflows

### Test Structure

```javascript
describe('Feature Name', () => {
  describe('functionName', () => {
    it('should do something specific', () => {
      // Arrange
      const input = 'test';

      // Act
      const result = functionName(input);

      // Assert
      expect(result).toBe('expected output');
    });

    it('should handle edge cases', () => {
      expect(() => functionName(null)).toThrow();
    });
  });
});
```

### Test Coverage

- Aim for >80% code coverage
- All new features must include tests
- Bug fixes should include regression tests

```bash
# Check coverage
npm run test:coverage

# View HTML report
open coverage/index.html
```

## Documentation

### Code Documentation

- Add JSDoc comments for public APIs
- Explain complex logic with inline comments
- Keep comments up-to-date with code changes

### User Documentation

- Update README.md for user-facing changes
- Add examples to docs/ folder
- Update API documentation for endpoint changes

### Writing Good Documentation

- Use clear, concise language
- Include code examples
- Explain the "why" not just the "what"
- Keep documentation DRY (Don't Repeat Yourself)

## Community

### Getting Help

- **Discord**: https://discord.gg/project-name
- **GitHub Discussions**: https://github.com/username/repo/discussions
- **Stack Overflow**: Tag with `project-name`

### Recognition

Contributors are recognized in:

- `CONTRIBUTORS.md`
- GitHub contributor graph
- Release notes

## License

By contributing, you agree that your contributions will be licensed under the project's `LICENSE`.

---

**Questions?** Feel free to ask in [GitHub Discussions](https://github.com/username/repo/discussions) or on [Discord](https://discord.gg/project-name).

**Thank you for contributing!** [CELEBRATE]
