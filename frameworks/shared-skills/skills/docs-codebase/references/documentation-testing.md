# Documentation Testing Guide

Comprehensive guide for testing technical documentation quality, accuracy, and usability.

---

## Why Test Documentation?

Documentation testing ensures:
- **Accuracy** - Code examples work as shown
- **Completeness** - All features are documented
- **Clarity** - Users can follow instructions
- **Maintainability** - Docs stay in sync with code
- **Accessibility** - Content is usable by all readers

---

## Testing Categories

### 1. Technical Accuracy Testing

**Verify code examples actually work:**

```bash
# Extract code blocks from documentation
grep -A 10 '```javascript' README.md > examples.js

# Run extracted code
node examples.js

# Automated example testing
npm install -g markdown-code-runner
markdown-code-runner README.md
```

**API Documentation Testing:**

```bash
# Test API endpoints from docs
curl -X GET "https://api.example.com/v1/users" \
  -H "Authorization: Bearer test-token"

# Expected: 200 OK with user list
# Actual: [verify against documentation]
```

**Setup Instructions Testing:**

```bash
# Fresh clone in isolated environment
docker run -it ubuntu:latest bash

# Follow documentation step-by-step
git clone https://github.com/username/repo.git
cd repo
# [Follow README.md installation steps...]

# Document any failures or unclear steps
```

---

### 2. Automated Linting

**Markdown Linting (markdownlint):**

```bash
# Install
npm install -g markdownlint-cli

# Run linter
markdownlint '**/*.md' --ignore node_modules

# With configuration
cat > .markdownlint.json << EOF
{
  "default": true,
  "MD013": { "line_length": 120 },
  "MD024": { "siblings_only": true },
  "MD033": false
}
EOF

markdownlint -c .markdownlint.json '**/*.md'
```

**Common Rules:**
- **MD001** - Header levels increment by 1
- **MD013** - Line length limit
- **MD024** - No duplicate headers
- **MD033** - No inline HTML
- **MD034** - No bare URLs

**Prose Linting (Vale):**

```bash
# Install Vale
brew install vale  # macOS
# or download from https://vale.sh/

# Initialize configuration
vale sync

# Create .vale.ini
cat > .vale.ini << EOF
StylesPath = styles
MinAlertLevel = suggestion

[*.md]
BasedOnStyles = Vale, Google
EOF

# Run Vale
vale docs/

# Output example:
# docs/api.md
#  15:6  warning  'utilize' is wordy. Consider     Vale.Wordiness
#               replacing with 'use'.
#  23:1  error    Use 'API' instead of 'api'.      Google.Acronyms
```

**Vale Style Packs:**
- **Vale** - Built-in style rules
- **Google** - Google Developer Style Guide
- **Microsoft** - Microsoft Writing Style Guide
- **write-good** - General writing quality

**Language Quality (write-good):**

```bash
# Install
npm install -g write-good

# Test documentation
write-good README.md

# Output:
# README.md
#   line 12: 'very' is wordy or unneeded
#   line 23: 'basically' is wordy or unneeded
#   line 45: 'obviously' is a weasel word
```

**Inclusive Language (alex):**

```bash
# Install
npm install -g alex

# Check for insensitive language
alex docs/

# Output:
# docs/README.md
#   12:5-12:9  warning  'guys' may be insensitive, use 'people' instead
```

---

### 3. Link Validation

**Check Broken Links:**

```bash
# Install markdown-link-check
npm install -g markdown-link-check

# Check single file
markdown-link-check README.md

# Check all markdown files
find . -name "*.md" -not -path "./node_modules/*" \
  -exec markdown-link-check {} \;
```

**GitHub Action for Link Checking:**

```yaml
# .github/workflows/links.yml
name: Check Links

on:
  push:
    branches: [main]
  pull_request:
    paths:
      - '**/*.md'

jobs:
  markdown-link-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: gaurav-nelson/github-action-markdown-link-check@v1
        with:
          use-quiet-mode: 'yes'
          use-verbose-mode: 'yes'
          config-file: '.markdown-link-check.json'
```

**Link Check Configuration (.markdown-link-check.json):**

```json
{
  "ignorePatterns": [
    {
      "pattern": "^http://localhost"
    },
    {
      "pattern": "^https://example.com"
    }
  ],
  "timeout": "20s",
  "retryOn429": true,
  "retryCount": 3,
  "fallbackRetryDelay": "30s"
}
```

---

### 4. Spelling and Grammar

**Spell Checking (cspell):**

```bash
# Install
npm install -g cspell

# Check spelling
cspell "docs/**/*.md"

# Custom dictionary (.cspell.json)
cat > .cspell.json << EOF
{
  "version": "0.2",
  "language": "en",
  "words": [
    "fastify",
    "postgres",
    "redis",
    "webhook"
  ],
  "ignoreRegExpList": [
    "/```[\\s\\S]*?```/g",
    "/`[^`]*`/g"
  ]
}
EOF
```

**Grammar Checking:**

```bash
# Using LanguageTool (requires Java)
# Download from https://languagetool.org/

# Check grammar
languagetool -l en-US README.md
```

---

### 5. Accessibility Testing

**Readability Scoring:**

```bash
# Install textstat
pip install textstat

# Check readability (Python)
python << EOF
import textstat

with open('README.md', 'r') as f:
    text = f.read()

print(f"Flesch Reading Ease: {textstat.flesch_reading_ease(text)}")
print(f"Grade Level: {textstat.flesch_kincaid_grade(text)}")
# Target: Grade 8-10 for technical docs
EOF
```

**Flesch Reading Ease Scale:**

- 90-100: Very Easy (5th grade)
- 80-89: Easy (6th grade)
- 70-79: Fairly Easy (7th grade)
- 60-69: Standard (8th-9th grade) **Target for technical docs**
- 50-59: Fairly Difficult (10th-12th grade)
- 30-49: Difficult (College)
- 0-29: Very Difficult (Graduate)

**Alt Text Validation:**

```bash
# Check for images without alt text
grep -n "!\[" docs/**/*.md | grep "!\[\]"

# Should return empty (all images should have alt text)
```

**Heading Structure:**

```bash
# Verify proper heading hierarchy
grep -E "^#{1,6} " docs/README.md | sed 's/\(#*\).*/\1/' | cat -n
```

---

### 5a. WCAG 3.0 Preview (January 2026)

WCAG 3.0 is in Working Draft status (expected completion 2027-2028). Key changes relevant to documentation:

**From Pass/Fail to Outcome Scoring:**

WCAG 3.0 uses a 0-4 scale instead of binary pass/fail:

- **0**: Very poor (critical barrier)
- **1**: Poor (significant barrier)
- **2**: Fair (some barriers)
- **3**: Good (minor issues)
- **4**: Excellent (fully accessible)

**New Structure:**

```text
WCAG 2.x: Principles → Guidelines → Success Criteria
WCAG 3.0: Guidelines → Outcomes → Methods → How-To Guides
```

**Functional Categories:**

WCAG 3.0 expands disability coverage with functional categories:

- Vision (blindness, low vision, color blindness)
- Hearing (deafness, hard of hearing)
- Motor (limited fine motor, limited gross motor)
- Cognitive (memory, attention, language, learning)
- Speech (non-verbal, speech impairments)

**Documentation-Specific Considerations:**

```markdown
## WCAG 3.0 Documentation Checklist (Preview)

### Content Structure
- [ ] Logical heading hierarchy (supports screen readers)
- [ ] Table headers properly marked (scope attributes)
- [ ] Lists use semantic markup (ul/ol, not manual bullets)
- [ ] Code blocks have language identification

### Cognitive Accessibility
- [ ] Plain language used (avoid jargon without definitions)
- [ ] Consistent navigation patterns
- [ ] Clear error messages with recovery steps
- [ ] Chunked content (short paragraphs, bullet points)

### Visual Accessibility
- [ ] Sufficient color contrast (4.5:1 for text)
- [ ] Information not conveyed by color alone
- [ ] Alt text for all images and diagrams
- [ ] Responsive design for zoom/magnification

### Interactive Elements
- [ ] Keyboard accessible (all interactive elements)
- [ ] Focus indicators visible
- [ ] Skip links for navigation
```

**Current Recommendation:**

Continue using WCAG 2.2 as the baseline. Monitor WCAG 3.0 Working Drafts for planning.

**Resources:**

- WCAG 3.0 Working Draft: https://www.w3.org/TR/wcag-3.0/
- WCAG 3 Introduction: https://www.w3.org/WAI/standards-guidelines/wcag/wcag3-intro/

---

### 5b. AI-Powered Documentation Linting (January 2026)

AI tools now offer advanced documentation quality checks beyond traditional linting.

**AI Linting Capabilities:**

- Write rules in plain English (not regex)
- Context-aware suggestions
- Automated broken link detection
- Style guide enforcement with explanations
- Terminology consistency checking

**ReadMe.com AI Linting (January 2026):**

```yaml
# Example AI linting rules in plain English
rules:
  - "Use active voice instead of passive voice"
  - "Define technical terms on first use"
  - "Include code examples for all API endpoints"
  - "Keep sentences under 25 words"
  - "Avoid jargon without explanation"
```

**Mintlify AI Features:**

```bash
# Mintlify automatically:
# - Checks for broken links
# - Suggests content improvements
# - Validates code examples
# - Ensures consistent terminology

mintlify check --ai-lint
```

**AI Docs Audit Workflow:**

```text
1. Run automated linting (markdownlint, Vale)
2. Run AI-powered audit (Mintlify, ReadMe)
3. Review AI suggestions
4. Apply improvements
5. Human final review
```

**Comparison: Traditional vs AI Linting:**

| Feature | Traditional (Vale) | AI-Powered |
|---------|-------------------|------------|
| Rule definition | Regex/YAML | Plain English |
| Context awareness | Limited | High |
| False positives | Common | Fewer |
| Custom rules | Complex | Simple |
| Learning | Static | Adaptive |

**Best Practices:**

- Use traditional linting for consistent, rule-based checks
- Use AI linting for context-aware suggestions
- Always human-review AI suggestions before applying
- Combine both for comprehensive coverage

---

### 6. Completeness Testing

**Coverage Checklist:**

```markdown
## Documentation Coverage Checklist

### Code Coverage
- [ ] All public APIs documented
- [ ] All configuration options explained
- [ ] All CLI commands documented
- [ ] All environment variables listed

### Example Coverage
- [ ] "Hello World" example provided
- [ ] Advanced usage examples included
- [ ] Error handling examples shown
- [ ] Edge cases documented

### Process Coverage
- [ ] Installation steps complete
- [ ] Development setup documented
- [ ] Deployment process explained
- [ ] Troubleshooting guide provided

### Reference Coverage
- [ ] API reference complete
- [ ] Configuration reference complete
- [ ] Error code reference available
- [ ] Changelog maintained
```

**API Documentation Audit:**

```bash
# List all exported functions
grep -r "export function" src/ | cut -d: -f2 | sort

# List documented functions
grep -r "^### " docs/api.md | sed 's/### //' | sort

# Find undocumented functions (compare both lists)
comm -23 <(grep -r "export function" src/ | cut -d: -f2 | sort) \
         <(grep -r "^### " docs/api.md | sed 's/### //' | sort)
```

---

### 7. Consistency Testing

**Terminology Consistency:**

```bash
# Check for inconsistent terms
# Bad: "log in" vs "login" vs "sign in"

grep -rn "log in\|login\|sign in" docs/

# Create a terminology guide
cat > TERMINOLOGY.md << EOF
# Terminology Guide

- Use "log in" (verb) and "login" (noun/adjective)
- Use "API" not "api" or "Api"
- Use "JavaScript" not "Javascript" or "javascript"
EOF
```

**Style Consistency:**

```bash
# Check code block language tags
grep -n '```' README.md | grep -v '```bash\|```javascript\|```python'

# All code blocks should have language specified
```

---

### 8. Freshness Testing

**Check for Outdated Content:**

```bash
# Find files not updated in 6+ months
find docs/ -name "*.md" -type f -mtime +180 -ls

# Version mentions (check if outdated)
grep -rn "Node.js 14\|Node.js 16" docs/

# Dates in documentation
grep -rn "202[0-3]" docs/
```

**Update Frequency:**

```bash
# Check last commit date for each doc
for file in docs/**/*.md; do
  last_update=$(git log -1 --format="%ai" -- "$file")
  echo "$file: $last_update"
done
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/docs-quality.yml
name: Documentation Quality

on:
  pull_request:
    paths:
      - 'docs/**'
      - '*.md'

jobs:
  lint-markdown:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Lint Markdown
        uses: articulate/actions-markdownlint@v1
        with:
          config: .markdownlint.json
          files: '**/*.md'
          ignore: node_modules

  check-links:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check Links
        uses: gaurav-nelson/github-action-markdown-link-check@v1

  spell-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Spell Check
        uses: streetsidesoftware/cspell-action@v2
        with:
          files: "**/*.md"

  test-code-examples:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Extract and Test Code Examples
        run: |
          npm install -g markdown-code-runner
          markdown-code-runner docs/**/*.md
```

---

## Manual Testing Checklist

### Pre-Release Documentation Review

```markdown
## Documentation QA Checklist

### Technical Accuracy
- [ ] All code examples compile/run
- [ ] All commands execute successfully
- [ ] All URLs are accessible
- [ ] All screenshots are current
- [ ] Version numbers are correct

### Clarity and Usability
- [ ] Prerequisites are clear
- [ ] Installation steps are complete
- [ ] First-time users can follow successfully
- [ ] Common questions are addressed
- [ ] Error messages are explained

### Completeness
- [ ] New features are documented
- [ ] Breaking changes are highlighted
- [ ] Migration guides provided (if needed)
- [ ] Changelog updated
- [ ] API reference is complete

### Quality
- [ ] No spelling errors
- [ ] No grammar errors
- [ ] Consistent terminology
- [ ] Proper heading hierarchy
- [ ] Alt text for all images

### Maintainability
- [ ] Docs are in version control
- [ ] Clear ownership documented
- [ ] Update process defined
- [ ] Automated tests pass
```

---

## Testing Tools Summary

| Tool | Purpose | Command |
|------|---------|---------|
| **markdownlint** | Markdown syntax/style | `markdownlint '**/*.md'` |
| **Vale** | Prose quality + style guides | `vale docs/` |
| **write-good** | Writing quality | `write-good README.md` |
| **alex** | Inclusive language | `alex docs/` |
| **cspell** | Spell checking | `cspell "docs/**/*.md"` |
| **markdown-link-check** | Broken links | `markdown-link-check README.md` |
| **textstat** | Readability scoring | Python library |
| **doctoc** | Table of contents | `doctoc README.md` |

---

## Best Practices

### 1. Test Documentation Like Code

```bash
# Treat docs as first-class citizens
.
├── .github/
│   └── workflows/
│       ├── tests.yml        # Code tests
│       └── docs.yml         # Doc tests [OK]
├── src/
├── tests/
└── docs/
    └── tests/               # Documentation tests [OK]
        ├── test-examples.sh
        └── verify-links.sh
```

### 2. Document the "Why", Not Just the "What"

```markdown
<!-- [FAIL] Bad - Only explains WHAT -->
## Configuration

Set `MAX_CONNECTIONS` to 100.

<!-- GOOD - Explains WHY -->
## Configuration

Set `MAX_CONNECTIONS` to 100.

**Why:** The default of 10 causes connection pool exhaustion under load.
Our production workload typically requires 50-80 concurrent connections,
so 100 provides a safety margin while avoiding resource waste.
```

### 3. Keep Examples Testable

```javascript
// BAD: Bad - Pseudo-code that won't run
const user = await fetchUser()
// ... handle result

// GOOD: Good - Complete, runnable example
const { Client } = require('@yourorg/sdk')

async function example() {
  const client = new Client({ apiKey: process.env.API_KEY })

  try {
    const user = await client.users.fetch('123')
    console.log('User:', user.email)
  } catch (error) {
    console.error('Failed to fetch user:', error.message)
    process.exit(1)
  }
}

example()
```

### 4. Update Docs With Code Changes

```bash
# Git hook to remind about docs
# .git/hooks/pre-commit

#!/bin/bash
if git diff --cached --name-only | grep -q "^src/"; then
  if ! git diff --cached --name-only | grep -q "^docs/"; then
    echo "[WARNING]  Warning: You modified code but not documentation"
    echo "   Consider updating docs/ if needed"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      exit 1
    fi
  fi
fi
```

### 5. Version Documentation With Code

```bash
# Tag docs with releases
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Maintain versioned docs (for breaking changes)
docs/
├── v1.0/
├── v2.0/
└── latest/ -> v2.0/
```

---

## Metrics and Monitoring

### Documentation Health Dashboard

Track these metrics:

```markdown
## Documentation Health Metrics

### Freshness
- **Last Updated**: [Date]
- **Files >6 months old**: 3 / 47 (6%)
- **Status**: [GREEN] Healthy

### Quality
- **Broken Links**: 0
- **Spelling Errors**: 2
- **Readability Score**: 65 (8th grade) [OK]
- **Status**: [GREEN] Healthy

### Coverage
- **Documented APIs**: 94 / 98 (96%)
- **Code Examples**: 89 / 98 (91%)
- **Status**: [YELLOW] Needs Improvement

### Accuracy
- **Failing Examples**: 0 / 45 (0%)
- **User-Reported Issues**: 2 open
- **Status**: [GREEN] Healthy
```

---

## Common Issues and Fixes

### Issue: Code Examples Fail After Updates

**Solution:** Add automated testing

```bash
# Extract code blocks and test them
cat > test-docs.sh << 'EOF'
#!/bin/bash
set -e

echo "Testing README examples..."
grep -A 20 '```bash' README.md | sed '/```/d' | bash

echo "Testing API docs..."
node test-api-examples.js

echo "[OK] All doc examples passed"
EOF

chmod +x test-docs.sh
./test-docs.sh
```

### Issue: Documentation Drift

**Solution:** CI checks that fail the build

```yaml
- name: Verify API Docs Match Code
  run: |
    npm run generate-api-docs
    git diff --exit-code docs/api.md
```

### Issue: Inconsistent Terminology

**Solution:** Create terminology glossary + Vale rules

```yaml
# styles/Vocab/accept.txt (Vale custom vocabulary)
API
JavaScript
PostgreSQL
webhook
```

---

## Resources

### Tools
- **Vale**: https://vale.sh/
- **markdownlint**: https://github.com/DavidAnson/markdownlint
- **write-good**: https://github.com/btford/write-good
- **cspell**: https://github.com/streetsidesoftware/cspell
- **markdown-link-check**: https://github.com/tcort/markdown-link-check

### Style Guides
- **Google Developer Docs**: https://developers.google.com/style
- **Microsoft Style Guide**: https://learn.microsoft.com/en-us/style-guide/
- **Write the Docs**: https://www.writethedocs.org/guide/

### Testing Frameworks
- **Doctest (Python)**: https://docs.python.org/3/library/doctest.html
- **JSDoc + Jest**: https://jestjs.io/docs/configuration#testmatch-arraystring

---

> **Success Criteria:** Documentation is accurate, clear, complete, maintainable, and provides value to users with minimal confusion or support tickets.
