# Contributing Guide Standards

Comprehensive guide for creating CONTRIBUTING.md files that help contributors understand how to participate in your project effectively.

## What Is a Contributing Guide?

A **CONTRIBUTING.md** file explains how others can contribute to your project, including development setup, coding standards, and submission process.

**Purpose**:
- Onboard contributors quickly
- Set clear expectations
- Maintain code quality
- Reduce maintainer burden
- Foster community growth

**Location**: `CONTRIBUTING.md` in repository root

## Essential Contributing Guide Structure

### 1. Welcome Message

**Set a welcoming tone**:

```markdown
# Contributing to [Project Name]

Thank you for your interest in contributing to [Project Name]! We welcome contributions from everyone, whether you're fixing a typo, reporting a bug, or implementing a new feature.

This guide will help you get started quickly and ensure your contributions can be merged smoothly.

## Quick Links

- [Code of Conduct](CODE_OF_CONDUCT.md) - Be respectful and inclusive
- [Issue Tracker](https://github.com/user/repo/issues) - Report bugs or request features
- [Discussions](https://github.com/user/repo/discussions) - Ask questions or share ideas
- [Roadmap](docs/ROADMAP.md) - See what we're working on
```

### 2. Ways to Contribute

**List different contribution types**:

```markdown
## Ways to Contribute

We appreciate all contributions, including:

### Code Contributions
- 🐛 **Bug fixes** - Fix existing issues
- [SPARKLE] **New features** - Implement requested features
- [FAST] **Performance improvements** - Optimize existing code
- ♿ **Accessibility improvements** - Make the project more accessible

### Non-Code Contributions
- [NOTE] **Documentation** - Improve README, guides, or API docs
- [WEB] **Translations** - Translate docs or UI to other languages
- [DESIGN] **Design** - Improve UI/UX, create graphics
- [TEST] **Testing** - Write tests, report bugs
- [COMMENT] **Community** - Answer questions, help other contributors
-  **Advocacy** - Blog posts, talks, tutorials about the project

**First-time contributors**: Look for issues labeled [`good first issue`](https://github.com/user/repo/labels/good%20first%20issue).
```

### 3. Getting Started (Development Setup)

**Provide step-by-step setup instructions**:

```markdown
## Getting Started

### Prerequisites

Before you begin, ensure you have:

- **Node.js 24+ LTS** ([download](https://nodejs.org/))
- **Git** ([download](https://git-scm.com/downloads))
- **PostgreSQL 18+** (optional, for database features)
- **Code editor** (we recommend [VS Code](https://code.visualstudio.com/))

### Local Development Setup

1. **Fork the repository**

   Click the "Fork" button on GitHub to create your own copy.

2. **Clone your fork**

   ```bash
   git clone https://github.com/YOUR_USERNAME/project.git
   cd project
   ```

3. **Add upstream remote**

   ```bash
   git remote add upstream https://github.com/original/project.git
   ```

4. **Install dependencies**

   ```bash
   npm install
   ```

5. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Initialize database** (if applicable)

   ```bash
   npm run db:migrate
   npm run db:seed
   ```

7. **Run development server**

   ```bash
   npm run dev
   ```

   The app should now be running at `http://localhost:3000`.

8. **Run tests to verify setup**

   ```bash
   npm test
   ```

   All tests should pass. If not, see [Troubleshooting](#troubleshooting).

### Troubleshooting Setup

**Port already in use**:
```bash
# Change port in .env
PORT=3001
```

**Database connection fails**:
```bash
# Verify PostgreSQL is running
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux
```

**Tests failing**:
```bash
# Ensure Node.js version is correct
node --version  # Should be 24+ LTS or 25+ Current

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```
```

### 4. Development Workflow

**Explain the contribution workflow**:

```markdown
## Development Workflow

### 1. Create a Branch

Create a feature branch from `main`:

```bash
git checkout main
git pull upstream main
git checkout -b feature/your-feature-name
```

**Branch naming conventions**:
- `feature/` - New features (e.g., `feature/oauth-login`)
- `fix/` - Bug fixes (e.g., `fix/memory-leak`)
- `docs/` - Documentation (e.g., `docs/api-guide`)
- `refactor/` - Code refactoring (e.g., `refactor/auth-service`)
- `test/` - Test additions (e.g., `test/user-controller`)

### 2. Make Changes

- Write code following our [Code Style Guidelines](#code-style)
- Add tests for new features or bug fixes
- Update documentation if needed
- Keep commits focused and atomic

### 3. Test Your Changes

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run specific test file
npm test -- user.test.js

# Check test coverage
npm run test:coverage
```

**Coverage requirements**: Maintain 80%+ overall coverage.

### 4. Commit Your Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic changes)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:

```bash
# Simple commit
git commit -m "feat(auth): add OAuth2 support"

# Commit with body
git commit -m "fix(api): resolve race condition in order processing

The order processing queue had a race condition when multiple
workers tried to process the same order. Added distributed locking
with Redis to ensure only one worker processes each order.

Fixes #456"

# Breaking change
git commit -m "feat(api)!: change response format to REST standard

BREAKING CHANGE: API responses now follow REST format with data/meta
wrapper. Update client code to access response.data instead of
response directly."
```

**Commit message guidelines**:
- Use imperative mood ("add feature" not "added feature")
- Keep subject line under 72 characters
- Reference issue numbers (`Fixes #123`, `Closes #456`)
- Explain WHY, not WHAT (code shows what)

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Open a Pull Request

1. Go to your fork on GitHub
2. Click "Compare & pull request"
3. Fill out the PR template:
   - **Title**: Clear, descriptive (e.g., "Add OAuth2 authentication")
   - **Description**: What changed and why
   - **Issue reference**: Closes #123
   - **Screenshots**: For UI changes
   - **Testing**: How you tested the changes
   - **Breaking changes**: List any breaking changes

**Pull Request Checklist**:

Before submitting, verify:

- [ ] Code follows style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] Commit messages follow Conventional Commits
- [ ] Branch is up-to-date with `main`
- [ ] No merge conflicts
- [ ] PR description is complete
```

### 5. Code Style Guidelines

**Define coding standards**:

```markdown
## Code Style Guidelines

### JavaScript/TypeScript

We use **ESLint** and **Prettier** for code formatting.

**Run linter**:
```bash
npm run lint        # Check for issues
npm run lint:fix    # Auto-fix issues
npm run format      # Format with Prettier
```

**Style rules**:
- Use `const` for variables that don't change
- Use `let` for variables that change
- Avoid `var`
- Use arrow functions for callbacks
- Use async/await instead of .then()
- Use template literals for string interpolation
- Prefer named exports over default exports

**Naming conventions**:
```typescript
// camelCase for variables and functions
const userName = 'John';
function getUserData() {}

// PascalCase for classes and types
class UserController {}
interface UserData {}

// UPPERCASE for constants
const MAX_RETRIES = 3;
const API_BASE_URL = 'https://api.example.com';

// kebab-case for file names
user-controller.ts
api-client.ts
```

### Python

Follow **PEP 8** style guide.

**Run linter**:
```bash
black .              # Format code
flake8 .             # Check style
mypy .               # Type checking
```

**Style rules**:
- Use 4 spaces for indentation
- Maximum line length: 88 characters (Black default)
- Use type hints for function parameters and returns
- Use docstrings for all public functions/classes
- Use snake_case for functions and variables
- Use PascalCase for classes

### Testing

**Test structure** (AAA pattern):
```javascript
describe('UserController', () => {
  it('should create user with valid data', async () => {
    // Arrange - Set up test data
    const userData = {
      email: 'test@example.com',
      name: 'John Doe'
    };

    // Act - Execute the operation
    const user = await createUser(userData);

    // Assert - Verify the outcome
    expect(user.email).toBe('test@example.com');
    expect(user.id).toBeDefined();
  });
});
```

**Test naming**:
- Describe what the test does, not implementation details
- Use "should" format: `should return 404 when user not found`
- Group related tests with `describe` blocks

**Coverage requirements**:
- Overall: 80%+
- New features: 90%+
- Critical paths (auth, payments): 100%
```

### 6. Code Review Process

**Explain review expectations**:

```markdown
## Code Review Process

### What Reviewers Look For

- **Correctness**: Does the code work as intended?
- **Tests**: Are there tests? Do they cover edge cases?
- **Documentation**: Is code documented? README updated?
- **Style**: Follows project style guidelines?
- **Performance**: Are there obvious performance issues?
- **Security**: Any security vulnerabilities?
- **Breaking changes**: Are breaking changes justified and documented?

### Responding to Review Feedback

- Be open to feedback - reviews help improve code quality
- Ask questions if feedback is unclear
- Make requested changes in new commits (don't force-push)
- Respond to each comment (thumbs up, "Done", or explain why not)
- Re-request review after addressing feedback

### Review Timeline

- **First review**: Within 2 business days
- **Follow-up reviews**: Within 1 business day
- **Merge**: After approval from 2 maintainers

**No response after 7 days**: PR may be closed for inactivity.

### After PR is Merged

- Delete your feature branch (GitHub will prompt you)
- Update your local repository:
  ```bash
  git checkout main
  git pull upstream main
  ```

Thank you for your contribution! [CELEBRATE]
```

### 7. Reporting Issues

**Guide users on reporting bugs**:

```markdown
## Reporting Issues

### Before Creating an Issue

1. **Search existing issues**: Your issue may already be reported
2. **Check documentation**: Answer might be in docs or FAQ
3. **Verify with latest version**: Bug may be fixed in newer version

### Bug Reports

**Use the bug report template** and include:

- **Description**: What happened vs what you expected
- **Steps to reproduce**: Minimal steps to reproduce the bug
- **Environment**: OS, Node.js version, browser (if applicable)
- **Error messages**: Full error messages and stack traces
- **Screenshots**: For visual bugs

**Example**:

```markdown
**Description**:
User login fails with "Invalid token" error even with correct credentials.

**Steps to Reproduce**:
1. Go to /login
2. Enter email: user@example.com
3. Enter password: correct_password
4. Click "Login"
5. See error: "Invalid token"

**Environment**:
- OS: macOS 14.0
- Browser: Chrome 120
- Node.js: 24.11.0

**Error message**:
```
Error: Invalid token
    at verifyToken (auth.js:45)
    at loginUser (user-controller.js:23)
```

**Expected**: Successful login and redirect to dashboard
**Actual**: Error message shown, no login
```

### Feature Requests

**Use the feature request template** and include:

- **Problem**: What problem does this solve?
- **Proposed solution**: How should it work?
- **Alternatives**: Other solutions you've considered
- **Use case**: Real-world scenario where this helps

### Security Vulnerabilities

**Do NOT open public issues for security vulnerabilities.**

Instead, email security@example.com with:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if known)

We aim to respond within 48 hours.
```

### 8. Community Guidelines

**Reference Code of Conduct**:

```markdown
## Community Guidelines

### Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).

**In summary**:
- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on what's best for the community
- Show empathy towards others

**Unacceptable behavior**:
- Harassment or discrimination
- Trolling or inflammatory comments
- Personal attacks
- Spam or self-promotion
- Publishing others' private information

**Reporting**: Email conduct@example.com to report violations.

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions, ideas, general discussion
- **Discord**: Real-time chat with maintainers and contributors
- **Twitter**: [@projectname](https://twitter.com/projectname) for announcements

### Getting Help

**Questions about the project**:
- Check [documentation](https://docs.example.com)
- Search [GitHub Discussions](https://github.com/user/repo/discussions)
- Ask in [Discord #help channel](https://discord.gg/example)

**Questions about contributing**:
- Read this guide thoroughly
- Ask in [Discord #contributors channel](https://discord.gg/example)
- Tag maintainers in GitHub Discussions
```

### 9. Recognition

**Acknowledge contributors**:

```markdown
## Recognition

### Contributors

All contributors are recognized in:
- [Contributors page](https://github.com/user/repo/graphs/contributors)
- Release notes (for significant contributions)
- [CHANGELOG.md](CHANGELOG.md) (for features and fixes)

### Becoming a Maintainer

Active contributors may be invited to become maintainers.

**Criteria**:
- Consistent high-quality contributions over 3+ months
- Deep understanding of codebase
- Helpful in reviews and discussions
- Alignment with project values

**Responsibilities**:
- Review pull requests
- Triage issues
- Mentor new contributors
- Make architectural decisions
```

## Complete CONTRIBUTING.md Example

See [assets/project-management/contributing-template.md](../assets/project-management/contributing-template.md) for a complete, copy-paste ready template.

## Contributing Guide Checklist

**Before publishing CONTRIBUTING.md**:

- [ ] Welcome message included
- [ ] Ways to contribute listed (code and non-code)
- [ ] Development setup instructions complete and tested
- [ ] Branch naming conventions defined
- [ ] Commit message format specified (Conventional Commits)
- [ ] Pull request process explained
- [ ] Code style guidelines documented
- [ ] Test requirements stated
- [ ] Code review process described
- [ ] Issue reporting guidelines included
- [ ] Security vulnerability reporting process
- [ ] Code of Conduct linked
- [ ] Communication channels listed
- [ ] Recognition/acknowledgment section
- [ ] All links work correctly

## CONTRIBUTING.md Anti-Patterns

**BAD: Avoid**:

- **No setup instructions** - Contributors can't get started
- **Vague requirements** - "Write good code" isn't actionable
- **Intimidating tone** - Discourages contributions
- **Outdated info** - Setup instructions that don't work
- **No examples** - Hard to understand commit format
- **Missing links** - Links to issue tracker, docs, etc.
- **Only for code** - Ignores non-code contributions

## Tools for Contributing Guides

**Templates**:
- GitHub's default CONTRIBUTING.md template
- [Contributor Covenant](https://www.contributor-covenant.org/)
- [All Contributors](https://allcontributors.org/) - Recognize all contributions

**Automation**:
- **All Contributors Bot**: Automatically add contributors to README
- **Semantic Release**: Auto-generate changelogs from commits
- **PR Templates**: Auto-populate PR descriptions

## Examples of Great Contributing Guides

**Open Source Projects**:
- **React**: https://github.com/facebook/react/blob/main/CONTRIBUTING.md
- **Next.js**: https://github.com/vercel/next.js/blob/canary/contributing.md
- **Vue.js**: https://github.com/vuejs/vue/blob/dev/.github/CONTRIBUTING.md
- **Typescript**: https://github.com/microsoft/TypeScript/blob/main/CONTRIBUTING.md

## Contributing Guide Success Criteria

**A great contributing guide enables contributors to**:

1. [OK] Set up development environment in < 15 minutes
2. [OK] Understand how to create a pull request
3. [OK] Know code style requirements
4. [OK] Write commit messages in correct format
5. [OK] Find communication channels
6. [OK] Report bugs effectively
7. [OK] Understand code of conduct

**Quality metrics**:
- Time to first contribution: < 30 minutes
- PR rejection rate due to guidelines: < 10%
- Contributor retention: > 40% return contributors
- Setup issues: < 5% of new contributors report setup problems
