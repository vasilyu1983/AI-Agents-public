# CLI Tool CLAUDE.md Template

Template for command-line applications and developer tools.

---

```markdown
# [CLI Name]

[One-line description of what this CLI tool does]

## Tech Stack

- **Language**: [TypeScript / Go / Rust / Python]
- **CLI Framework**: [Commander.js / yargs / oclif / cobra / clap / click]
- **Config**: [cosmiconfig / dotenv / viper / figment]
- **Output**: [chalk / ora / inquirer / lipgloss / rich]
- **Testing**: [Vitest / go test / cargo test / pytest]

## Installation

```bash
# npm global install
npm install -g [package-name]

# Or run via npx
npx [package-name] [command]

# Or build from source
git clone [repo]
cd [repo]
npm install && npm run build
npm link
```

## Architecture

[2-3 sentences describing the CLI architecture]

### Directory Structure

```
src/
├── cli.ts              # Entry point, command registration
├── commands/           # Command implementations
│   ├── init.ts
│   ├── build.ts
│   └── deploy.ts
├── lib/                # Shared utilities
│   ├── config.ts       # Configuration loading
│   ├── logger.ts       # Logging utilities
│   └── api.ts          # API client (if applicable)
├── prompts/            # Interactive prompts
├── assets/          # File templates
└── types/              # Type definitions
```

### Command Structure

```
[cli-name] <command> [subcommand] [options] [arguments]

Examples:
  [cli-name] init                    # Initialize project
  [cli-name] build --prod            # Build for production
  [cli-name] deploy staging          # Deploy to staging
```

## Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `init` | Initialize new project | `cli init --template basic` |
| `build` | Build project | `cli build --prod` |
| `deploy` | Deploy to environment | `cli deploy production` |
| `config` | Manage configuration | `cli config set key value` |
| `help` | Show help | `cli help [command]` |

### Command Options

```bash
# Global options (available on all commands)
--verbose, -v      # Verbose output
--quiet, -q        # Suppress output
--config, -c       # Config file path
--help, -h         # Show help

# Command-specific options
init:
  --template, -t   # Template to use
  --force, -f      # Overwrite existing

build:
  --prod           # Production build
  --watch, -w      # Watch mode
  --output, -o     # Output directory

deploy:
  --dry-run        # Preview changes
  --force          # Skip confirmations
```

## Configuration

### Config File Locations

Searched in order:
1. `.clirc` in current directory
2. `.clirc` in home directory
3. `cli.config.js` in current directory
4. Environment variables with `CLI_` prefix

### Config Schema

```typescript
// cli.config.js
export default {
  // Project settings
  projectName: 'my-project',
  outputDir: './dist',

  // Environment
  environment: 'development',

  // API settings (if applicable)
  apiUrl: 'https://api.example.com',
  apiKey: process.env.CLI_API_KEY,

  // Feature flags
  features: {
    experimentalFeature: false,
  },
};
```

### Environment Variables

```bash
CLI_CONFIG_PATH=/path/to/config    # Custom config location
CLI_API_KEY=your-api-key           # API authentication
CLI_VERBOSE=true                   # Enable verbose output
CLI_NO_COLOR=true                  # Disable colored output
```

## Conventions

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Configuration error |
| 4 | Network error |
| 5 | Permission denied |

### Output Formatting

```typescript
// Use structured output for programmatic use
if (options.json) {
  console.log(JSON.stringify(result, null, 2));
} else {
  console.log(chalk.green('[check]'), 'Operation successful');
}
```

### Error Handling

```typescript
// User-friendly errors
throw new UserError('Config file not found', {
  suggestion: 'Run `cli init` to create one',
  code: 'CONFIG_NOT_FOUND',
});
```

## Key Files

| Purpose | Location | Notes |
|---------|----------|-------|
| Entry point | `src/cli.ts` | Command registration |
| Config loader | `src/lib/config.ts` | cosmiconfig setup |
| Logger | `src/lib/logger.ts` | Chalk + ora |
| API client | `src/lib/api.ts` | HTTP requests |
| Types | `src/types/index.ts` | Shared types |

## Development

```bash
# Development with watch
npm run dev

# Build
npm run build

# Test locally
npm link
cli --help

# Run tests
npm test

# Release
npm version patch
npm publish
```

## Testing

### Unit Tests

```typescript
describe('init command', () => {
  it('creates project structure', async () => {
    await runCommand(['init', '--template', 'basic']);
    expect(fs.existsSync('package.json')).toBe(true);
  });
});
```

### Integration Tests

```bash
# Test CLI end-to-end
./tests/integration/run.sh
```

## Important Context

### Known Gotchas

- **Windows paths**: Use `path.resolve()` for cross-platform
- **TTY detection**: Check `process.stdout.isTTY` for interactive features
- **Signal handling**: Handle SIGINT for cleanup on Ctrl+C

### Performance

- Lazy-load heavy dependencies
- Use streaming for large files
- Cache config parsing

## For AI Assistants

### When modifying:

- Follow existing command structure
- Add help text for new options
- Update README with new commands
- Add tests for new functionality

### Avoid:

- Synchronous file operations for large files
- Hard-coded paths (use config)
- Console.log (use logger)
```

---

## Discovery Commands

```bash
# Find commands
find src -name "*.ts" -path "*/commands/*"

# Check CLI framework
cat package.json | jq '.dependencies' | grep -E "commander|yargs|oclif|meow"

# Find options/flags
grep -r "option\|flag\|argument" --include="*.ts" src/
```
