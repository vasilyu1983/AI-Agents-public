# SonarQube Setup Guide

Complete guide to setting up SonarQube for code quality and technical debt management.

**Updated**: June 2026
**Target Docs**: SonarQube Server 2026.1 LTA and SonarQube Cloud

---

## Overview

SonarQube is an open-source platform for continuous inspection of code quality. It performs automatic reviews with static analysis to detect:

- Bugs
- Code smells
- Security vulnerabilities
- Technical debt
- Code coverage gaps

Current highlights (2026.1 LTA):

- **Sonar way for AI Code**: Built-in quality gate qualified for AI Code Assurance
- **Zero New Issues**: Stricter enforcement option to ensure no new issues enter codebase
- **Fudge Factor**: Relaxed conditions for small changes (<20 lines) to avoid over-enforcement
- **Quality Gate Recommendations**: Automatic suggestions when better configurations exist
- **MCP Server Integration**: AI agents (Claude Code, Cursor, Windsurf) can query issues and quality status via MCP
- **50% faster analysis** for JavaScript, TypeScript, Python, and Kotlin vs. 2025.x
- **Rust and Swift 6.2 full support**; C#14 / .NET 10 / Java 24 / Python 3.14 language support

---

## Installation Options

### Option 1: SonarQube Cloud (Hosted - Easiest)

**Best for**: Small teams, fast setup, and managed hosting

**Setup**:
1. Go to https://sonarcloud.io
2. Sign in with GitHub/Bitbucket/Azure DevOps
3. Import your repository
4. Follow integration steps below

---

### Option 2: Docker (Local Development)

**Best for**: Local development, private projects

```bash
# Start SonarQube locally.
# Pin an explicit supported image tag for your edition/version.
docker run -d --name sonarqube \
  -p 9000:9000 \
  -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true \
  sonarqube:<supported-tag>

# Wait 2-3 minutes for startup
# Access at http://localhost:9000
# Default credentials: admin/admin (change immediately)
```

---

### Option 3: Server Installation

**Best for**: Enterprise, on-premise deployment

1. **Requirements**:
   - Java 17 or 21
   - PostgreSQL, Microsoft SQL Server, or Oracle
   - 2GB RAM minimum (4GB recommended)

2. **Download**:
   ```bash
   # Download the current SonarQube Server ZIP for your edition/version
   # from the official install docs, then unzip it.
   wget <current-sonarqube-server-zip-url>
   unzip <current-sonarqube-server-zip>
   cd <current-sonarqube-server-dir>
   ```

3. **Configure Database** (conf/sonar.properties):
   ```properties
   sonar.jdbc.username=sonarqube
   sonar.jdbc.password=mypassword
   sonar.jdbc.url=jdbc:postgresql://localhost/sonarqube
   ```

4. **Start Server**:
   ```bash
   bin/linux-x86-64/sonar.sh start
   ```

5. **Access**: http://localhost:9000

---

## Project Configuration

### Step 1: Create Project

**In SonarQube UI**:
1. Click "Create Project"
2. Enter project key (e.g., `my-company_my-app`)
3. Set project name and visibility
4. Generate token (save it!)

---

### Step 2: Configure Project Properties

Create `sonar-project.properties` in project root:

```properties
# ============================================
# PROJECT IDENTIFICATION
# ============================================

sonar.projectKey=my-company_my-app
sonar.projectName=My Application
sonar.projectVersion=1.0.0

# ============================================
# SOURCE CODE LOCATION
# ============================================

# Source directories (comma-separated)
sonar.sources=src

# Test directories
sonar.tests=src/**/*.test.js,src/**/*.spec.js

# Exclusions (files to ignore)
sonar.exclusions=**/node_modules/**,**/dist/**,**/build/**,**/*.test.js

# Test coverage exclusions
sonar.coverage.exclusions=**/*.test.js,**/*.spec.js,**/mocks/**

# ============================================
# LANGUAGE CONFIGURATION
# ============================================

# Source encoding
sonar.sourceEncoding=UTF-8

# JavaScript/TypeScript
sonar.javascript.file.suffixes=.js,.jsx
sonar.typescript.file.suffixes=.ts,.tsx

# Python
# sonar.python.version=3.9

# Java
# sonar.java.binaries=target/classes

# ============================================
# CODE COVERAGE
# ============================================

# JavaScript/TypeScript with Jest
sonar.javascript.lcov.reportPaths=coverage/lcov.info
sonar.testExecutionReportPaths=coverage/test-reporter.xml

# Python with pytest-cov
# sonar.python.coverage.reportPaths=coverage.xml

# Java with JaCoCo
# sonar.coverage.jacoco.xmlReportPaths=target/site/jacoco/jacoco.xml

# ============================================
# QUALITY GATE SETTINGS
# ============================================

# Wait for quality gate result
sonar.qualitygate.wait=true
sonar.qualitygate.timeout=300

# ============================================
# QUALITY THRESHOLDS
# ============================================

# Code coverage minimum
sonar.coverage.threshold=80

# Duplicate code maximum (%)
sonar.cpd.exclusions=**/test/**
sonar.duplications.exclusions=**/test/**

# ============================================
# ANALYSIS PARAMETERS
# ============================================

# Branch name
sonar.branch.name=main

# Pull request analysis (if applicable)
# sonar.pullrequest.key=123
# sonar.pullrequest.branch=feature-branch
# sonar.pullrequest.base=main
```

---

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/sonarqube.yml`:

```yaml
name: SonarQube Analysis

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  sonarqube:
    name: SonarQube Scan
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Full history for better analysis

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run tests with coverage
        run: npm run test:coverage

      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@<pinned-version>
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}

      - name: SonarQube Quality Gate Check
        uses: sonarsource/sonarqube-quality-gate-action@<pinned-version>
        timeout-minutes: 5
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        with:
          scanMetadataReportFile: .scannerwork/report-task.txt

      - name: Fail if Quality Gate failed
        if: steps.sonarqube-quality-gate-check.outputs.quality-gate-status == 'FAILED'
        run: exit 1
```

**Setup Secrets**:
1. Go to repository Settings → Secrets
2. Add `SONAR_TOKEN` (from SonarQube)
3. Add `SONAR_HOST_URL` (for example `https://sonarcloud.io` or your self-hosted server URL)

---

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - sonarqube

test:
  stage: test
  script:
    - npm ci
    - npm run test:coverage
  artifacts:
    paths:
      - coverage/
    expire_in: 1 day

sonarqube:
  stage: sonarqube
  image: sonarsource/sonar-scanner-cli:latest
  variables:
    SONAR_USER_HOME: "${CI_PROJECT_DIR}/.sonar"
    GIT_DEPTH: "0"
  cache:
    key: "${CI_JOB_NAME}"
    paths:
      - .sonar/cache
  script:
    - sonar-scanner
      -Dsonar.qualitygate.wait=true
      -Dsonar.projectKey=$CI_PROJECT_PATH_SLUG
      -Dsonar.sources=src
      -Dsonar.host.url=$SONAR_HOST_URL
      -Dsonar.login=$SONAR_TOKEN
  allow_failure: false
  only:
    - main
    - merge_requests
```

---

### Jenkins

Install SonarQube Scanner plugin, then add to Jenkinsfile:

```groovy
pipeline {
  agent any

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Test') {
      steps {
        sh 'npm ci'
        sh 'npm run test:coverage'
      }
    }

    stage('SonarQube Analysis') {
      steps {
        withSonarQubeEnv('SonarQube') {
          sh 'sonar-scanner'
        }
      }
    }

    stage('Quality Gate') {
      steps {
        timeout(time: 5, unit: 'MINUTES') {
          waitForQualityGate abortPipeline: true
        }
      }
    }
  }
}
```

---

## Quality Gates (2026.1 LTA)

Quality Gates define minimum quality standards for code to pass.

**Reference**: [SonarQube Quality Gates Documentation](https://docs.sonarsource.com/sonarqube-server/2026.1/instance-administration/analysis-functions/quality-gates)

SonarQube 2026.1 LTA adds MCP server integration so AI agents (Claude Code, Cursor, Windsurf) can query quality and security insights directly. Analysis is up to 50% faster for JavaScript, TypeScript, Python, and Kotlin versus 2025.x.

### Built-in Quality Gates

SonarQube 2026.1 LTA provides two useful built-in quality gates:

| Quality Gate | Use Case |
| ------------ | -------- |
| **Sonar way** | Default for all projects (recommended) |
| **Sonar way for AI Code** | Projects containing AI-generated code (stricter) |

### Sonar way (Default)

**Conditions** (fail if any breached on new code):

- Number of issues > 0 (enforces zero new issues)
- Reliability Rating worse than A
- Security Rating worse than A
- Maintainability Rating worse than A
- Security Hotspots Reviewed < 100%
- Coverage < 80% (configurable)
- Duplicated Lines (%) > 3% (configurable)

### Sonar way for AI Code

**Additional conditions** for AI-generated code:

- All conditions from Sonar way
- Stricter enforcement on security and reliability
- Enhanced detection of AI-generated anti-patterns
- Required for AI Code Assurance qualification

**When to use**: Projects using GitHub Copilot, Cursor, Claude Code, or other AI coding assistants should consider this quality gate.

### Zero New Issues Strategy

The most effective quality gate strategy is **zero new issues**:

```
Condition: Number of issues > 0 → FAIL

Why: Prevents ALL technical debt from entering new code.
Rating conditions (A) still allow some issues to slip through.
```

### Custom Quality Gate

**Create in SonarQube UI**:

1. Quality Gates → Create
2. Start from "Sonar way" template (auto-copied)
3. Add/modify conditions:

```text
Conditions on New Code:
- Number of issues > 0 (strictest, recommended)
- Coverage < 80%
- Duplicated Lines (%) > 3%
- Security Hotspots Reviewed < 100%

Conditions on Overall Code (legacy projects):
- Technical Debt Ratio > 5%
- Code Smells > 100
- Bugs > 0
- Vulnerabilities > 0
```

### Fudge Factor

For small changes (<20 lines), SonarQube relaxes coverage and duplication checks to avoid over-enforcement. This is enabled by default.

**Behavior**: Coverage and duplication conditions are ignored until new code reaches 20+ lines.

---

## Analyzing Results

### Metrics Explained

**Reliability**:
- **Bugs**: Code that will likely fail in production
- **Reliability Rating**: A (0 bugs) to E (many bugs)

**Security**:
- **Vulnerabilities**: Security flaws
- **Security Hotspots**: Security-sensitive code to review
- **Security Rating**: A (0 vulnerabilities) to E (many)

**Maintainability**:
- **Code Smells**: Maintainability issues
- **Technical Debt**: Time to fix all code smells
- **Maintainability Rating**: A (<5% debt ratio) to E (>50%)

**Coverage**:
- **Coverage**: % of code covered by tests
- **Line Coverage**: % of lines executed
- **Branch Coverage**: % of branches (if/else) covered

**Duplication**:
- **Duplicated Lines**: % of duplicated code
- **Duplicated Blocks**: Number of duplicate blocks

**Size**:
- **Lines of Code**: Total lines (excluding comments/blank lines)
- **Statements**: Number of statements
- **Functions**: Number of functions
- **Classes**: Number of classes

---

## Best Practices

### 1. Focus on New Code

**Why**: Can't fix everything at once

**How**:
- Set strict quality gates for new code
- Allow legacy code to have more issues
- Gradually improve old code with Boy Scout Rule

### 2. Fix Blocker/Critical Issues First

**Priority Order**:
1. Blocker bugs/vulnerabilities
2. Critical bugs/vulnerabilities
3. Major bugs
4. Code smells (by debt)

### 3. Aim for "Clean as You Code"

**Principle**: All new code meets quality standards

**Practice**:
- Quality gate on new code only
- Fix issues before merging
- Don't accumulate new debt

### 4. Regular Debt Reduction

**Schedule**:
- Review debt in normal planning cadence
- Time-box focused cleanup when hotspots materially slow delivery
- Treat debt work as capacity planning, not a universal fixed percentage

### 5. Monitor Trends

**Watch for**:
- Increasing debt ratio
- Decreasing coverage
- Rising bug count
- Growing duplications

---

## Troubleshooting

### Analysis Fails

**Issue**: Analysis doesn't complete

**Solutions**:
- Check SonarQube logs
- Verify token permissions
- Ensure correct project key
- Check network connectivity

### No Coverage Data

**Issue**: Coverage shows 0%

**Solutions**:
- Verify test script generates coverage
- Check `sonar.javascript.lcov.reportPaths` path
- Ensure coverage file exists before scan
- Run tests before SonarQube scan

### Quality Gate Always Passes

**Issue**: Even bad code passes

**Solutions**:
- Check quality gate configuration
- Verify conditions are set
- Ensure quality gate is assigned to project
- Check for exclusions hiding issues

---

## Advanced Configuration

### Multi-Module Projects

```properties
# Parent module
sonar.projectKey=my-company_my-monorepo
sonar.modules=module1,module2,module3

# Module 1
module1.sonar.projectName=Module 1
module1.sonar.sources=packages/module1/src
module1.sonar.tests=packages/module1/tests

# Module 2
module2.sonar.projectName=Module 2
module2.sonar.sources=packages/module2/src
module2.sonar.tests=packages/module2/tests
```

### Branch Analysis

```properties
# Long-lived branches
sonar.branch.name=develop
sonar.branch.target=main

# Pull request analysis
sonar.pullrequest.key=123
sonar.pullrequest.branch=feature-xyz
sonar.pullrequest.base=main
```

### Custom Rules

Create custom rules using SonarQube plugin API (Java):
1. Create Maven project
2. Implement `JavaCheck` interface
3. Build JAR
4. Upload to SonarQube

---

## Maintenance

### Regular Tasks

**Weekly**:
- Review new issues
- Check quality gate status
- Monitor coverage trends

**Monthly**:
- Update quality gates
- Review custom rules
- Clean up old branches

**Quarterly**:
- SonarQube version upgrade
- Plugin updates
- Performance tuning

---

## Resources

- **Official Docs (2026.1 LTA)**: [SonarQube Server 2026.1](https://docs.sonarsource.com/sonarqube-server/2026.1/)
- **Quality Gates Guide**: [Quality Gates Documentation](https://docs.sonarsource.com/sonarqube-server/2026.1/instance-administration/analysis-functions/quality-gates)
- **Installation Requirements**: [Server Host Requirements](https://docs.sonarsource.com/sonarqube-server/2026.1/setup-and-upgrade/installation-requirements/server-host)
- **Database Support**: [Installing the Database](https://docs.sonarsource.com/sonarqube-server/2026.1/server-installation/installing-the-database)
- **SonarQube Cloud**: [sonarcloud.io](https://sonarcloud.io/)
- **Rules Reference**: [rules.sonarsource.com](https://rules.sonarsource.com/)
- **Community**: [community.sonarsource.com](https://community.sonarsource.com/)
- **GitHub**: [SonarSource/sonarqube](https://github.com/SonarSource/sonarqube)

---

## Quick Reference

### Common Commands

```bash
# Local analysis
sonar-scanner

# With custom properties
sonar-scanner -Dsonar.projectKey=my-project

# With token
sonar-scanner -Dsonar.login=my-token

# Verbose output
sonar-scanner -X
```

### Docker Commands

```bash
# Start
docker run -d --name sonarqube -p 9000:9000 sonarqube:<supported-tag>

# Stop
docker stop sonarqube

# Restart
docker restart sonarqube

# Logs
docker logs -f sonarqube

# Remove
docker rm -f sonarqube
```
