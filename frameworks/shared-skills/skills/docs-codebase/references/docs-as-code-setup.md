# Docs-as-Code Setup Guide

Comprehensive guide to implementing documentation-as-code workflows with version control, automated builds, and CI/CD integration.

## Table of Contents

- [What is Docs-as-Code?](#what-is-docs-as-code)
- [Benefits](#benefits)
- [Choosing a Tool](#choosing-a-tool)
- [MkDocs Setup](#mkdocs-setup)
- [Docusaurus Setup](#docusaurus-setup)
- [CI/CD Integration](#cicd-integration)
- [Repository Documentation Governance](#repository-documentation-governance)
- [Best Practices](#best-practices)

---

## What is Docs-as-Code?

**Docs-as-Code** is an approach that applies software development workflows to documentation:

- Documentation stored in version control (Git)
- Written in plain text (Markdown, reStructuredText)
- Reviewed via pull requests
- Built and deployed automatically
- Versioned alongside code

**Traditional docs:** Word/Confluence → Manual updates → Version confusion
**Docs-as-Code:** Markdown + Git → CI/CD → Automatic deployment

---

## Benefits

### For Documentation Teams

- **Version control:** Full history of changes
- **Collaboration:** Pull request reviews, suggestions
- **Branching:** Work on features independently
- **Automation:** Automatic builds and deploys

### For Developers

- **Familiar tools:** Git, Markdown, code editors
- **Inline updates:** Update docs with code changes
- **Code ownership:** Docs live near code
- **Single source of truth:** No separate wiki

### For Users

- **Always up-to-date:** Automatic deployments
- **Searchable:** Full-text search
- **Versioned:** View docs for specific versions
- **Fast:** Static site generation

---

## Choosing a Tool

| Tool | Language | Best For | Complexity |
|------|----------|----------|------------|
| **VitePress** | Vue/Node | Markdown-first docs with fast iteration and `llms.txt` support | Low |
| **Astro Starlight** | Astro/Node | Content-heavy product docs with strong IA | Medium |
| **MkDocs** | Python | Ops, internal, or Python-adjacent docs sites | Low |
| **Docusaurus** | React | Large versioned portals with custom UX needs | Medium |
| **Nextra** | Next.js | Teams already standardized on Next.js | Medium |
| **Mintlify / ReadMe** | Hosted | Managed developer portals and API docs | Low |
| **GitBook** | Hosted | Writer-led collaboration workflows | Low |

**Recommendation:**
- **Markdown-first docs with AI-readable output:** VitePress
- **Content-heavy docs on Astro stack:** Starlight
- **Ops / Python / internal platform docs:** MkDocs
- **Large multi-version product portal:** Docusaurus
- **Hosted developer portal:** Mintlify or ReadMe
- **Already on Next.js:** Nextra

Choose based on:

- your existing frontend/tooling stack
- whether you need built-in versioning
- whether hosted publishing is acceptable
- whether you want first-class AI-readable outputs such as `llms.txt`

---

## Repository Documentation Governance

Modern agent-readable repos need documentation placement rules as much as they need writing rules. The goal is to make the repo legible without creating a permanent pile of one-off Markdown files.

### Placement Matrix

| Location | Owns | Must Not Own |
|----------|------|--------------|
| `AGENTS.md` / `CLAUDE.md` | Hot execution policy, exact commands, hard constraints, pointers to deeper docs | Codebase catalog, reports, plans, inventories, duplicated docs |
| `README.md` | Navigation, setup entry point, short orientation | Every operational procedure or architecture detail |
| `docs/tech/` or `docs/architecture/` | Canonical technical and architecture docs | Temporary investigation notes |
| `docs/operations/` or `docs/runbooks/` | Operational procedures, incident steps, release steps | Product explanations or generic onboarding prose |
| `docs/api/` | API reference, contracts, examples | Product roadmap or debugging reports |
| `docs/specs/` or `docs/plans/` | Active specs and implementation plans | Permanent status truth after the work ships |
| `docs/reports/` | Time-bound analysis, audits, migration findings | Canonical architecture truth after integration |
| `docs/context/` or `context/` | Generated or compiled LLM context artifacts | Hand-authored source of truth without rebuild ownership |
| `.archive/` | Historical material excluded from normal context | Anything agents should normally read |
| `scripts/README.md` | Script-adjacent commands and maintenance workflow | Repo-wide onboarding or product docs |

### New Markdown Creation Test

Create a new Markdown file only when the answer to each question is yes:

1. Does no existing canonical doc already own this subject?
2. Is the target folder correct for the doc type?
3. Is the file linked from the relevant README, index, docs nav, or context hub?
4. Does the file have an owner or review path?
5. Does volatile content include `last_verified` or a refresh command?
6. Is there a lifecycle state for reports and plans: `active`, `pending-integration`, `integrated`, or `superseded`?
7. If generated, is the source artifact and rebuild command documented?

If the answer is no, update the closest canonical doc or leave the content in the task thread. Do not create root-level `SUMMARY.md`, `MIGRATION.md`, `OPTIMIZATION_NOTES.md`, or similar files unless the repo explicitly asks for that filename.

### Agent Context Pattern

For LLM-facing repo context:

- Keep the hot instruction layer short and precise.
- Put durable detail in canonical docs.
- Put large generated summaries in `docs/context/` or `context/`, built from structured artifacts.
- Keep raw evidence separate from compiled summaries.
- Prefer links and stable headings over duplicated prose.

This follows the April 2026 pattern from Codex, Claude, and Copilot guidance: instruction files are automatically loaded context, so they should contain focused, non-obvious rules and route agents to repo-local evidence instead of becoming all-purpose docs.

---

## MkDocs Setup

### Installation

```bash
# Install MkDocs
pip install mkdocs

# Install Material theme (recommended)
pip install mkdocs-material

# Verify installation
mkdocs --version
```

### Project Initialization

```bash
# Create new MkDocs project
mkdocs new my-project
cd my-project

# Project structure
my-project/
├── mkdocs.yml          # Configuration
└── docs/
    └── index.md        # Homepage
```

### Configuration (mkdocs.yml)

```yaml
site_name: My Project Documentation
site_url: https://docs.example.com
site_description: Comprehensive documentation for My Project
site_author: Your Name

# Theme configuration
theme:
  name: material
  palette:
    # Light mode
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    # Dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.sections
    - navigation.expand
    - navigation.top
    - search.suggest
    - search.highlight
    - content.code.copy
    - content.code.annotate

# Navigation
nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Quick Start: getting-started/quick-start.md
    - Configuration: getting-started/configuration.md
  - API Reference:
    - Authentication: api/authentication.md
    - Endpoints: api/endpoints.md
    - Webhooks: api/webhooks.md
  - Guides:
    - Deployment: guides/deployment.md
    - Best Practices: guides/best-practices.md
  - About:
    - Changelog: about/changelog.md
    - Contributing: about/contributing.md
    - License: about/license.md

# Markdown extensions
markdown_extensions:
  # Python Markdown
  - abbr
  - admonition
  - attr_list
  - def_list
  - footnotes
  - md_in_html
  - tables
  - toc:
      permalink: true

  # Python Markdown Extensions
  - pymdownx.arithmatex:
      generic: true
  - pymdownx.betterem
  - pymdownx.critic
  - pymdownx.details
  - pymdownx.emoji:
      emoji_index: !!python/name:materialx.emoji.twemoji
      emoji_generator: !!python/name:materialx.emoji.to_svg
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.inlinehilite
  - pymdownx.keys
  - pymdownx.mark
  - pymdownx.smartsymbols
  - pymdownx.snippets
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.tasklist:
      custom_checkbox: true

# Plugins
plugins:
  - search:
      lang: en
  - git-revision-date-localized:
      enable_creation_date: true
  - minify:
      minify_html: true

# Extra configuration
extra:
  version:
    provider: mike
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/username/repo
    - icon: fontawesome/brands/twitter
      link: https://twitter.com/username
    - icon: fontawesome/brands/discord
      link: https://discord.gg/invite

# Copyright
copyright: Copyright &copy; 2025 Your Company Name
```

### Creating Documentation

**docs/index.md:**
```markdown
# Welcome to My Project

This is the homepage of your documentation.

## Quick Links

- [Installation Guide](getting-started/installation.md)
- [API Reference](api/endpoints.md)
- [Contributing](about/contributing.md)

## Features

- Feature 1
- Feature 2
- Feature 3
```

### Build and Preview

```bash
# Serve locally (with live reload)
mkdocs serve

# Build static site
mkdocs build

# Output to dist/
# dist/
# ├── index.html
# ├── getting-started/
# ├── api/
# └── assets/
```

### Deployment

**GitHub Pages:**
```bash
# Deploy to gh-pages branch
mkdocs gh-deploy

# With custom domain
mkdocs gh-deploy --force
```

---

## Docusaurus Setup

### Installation

```bash
# Create new Docusaurus site
npx create-docusaurus@latest my-website classic

cd my-website

# Project structure
my-website/
├── docs/               # Documentation files
├── blog/               # Blog posts (optional)
├── src/
│   ├── components/     # React components
│   └── pages/          # Custom pages
├── static/             # Static assets
└── docusaurus.config.js  # Configuration
```

### Configuration (docusaurus.config.js)

```javascript
const config = {
  title: 'My Project',
  tagline: 'Awesome documentation for awesome project',
  url: 'https://docs.example.com',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',

  // GitHub Pages deployment
  organizationName: 'username',
  projectName: 'repo',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/username/repo/tree/main/',
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
        },
        blog: {
          showReadingTime: true,
          editUrl: 'https://github.com/username/repo/tree/main/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'My Project',
      logo: {
        alt: 'My Project Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'doc',
          docId: 'intro',
          position: 'left',
          label: 'Docs',
        },
        {to: '/blog', label: 'Blog', position: 'left'},
        {
          href: 'https://github.com/username/repo',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Getting Started',
              to: '/docs/intro',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'Discord',
              href: 'https://discord.gg/invite',
            },
            {
              label: 'Twitter',
              href: 'https://twitter.com/username',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} My Project`,
    },
    prism: {
      theme: require('prism-react-renderer/themes/github'),
      darkTheme: require('prism-react-renderer/themes/dracula'),
    },
    algolia: {
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_SEARCH_API_KEY',
      indexName: 'YOUR_INDEX_NAME',
    },
  },
};

module.exports = config;
```

### Versioning

```bash
# Create version snapshot
npm run docusaurus docs:version 1.0.0

# Structure
versioned_docs/
├── version-1.0.0/
│   └── intro.md
└── version-2.0.0/
    └── intro.md

versioned_sidebars/
└── version-1.0.0-sidebars.json
```

### Build and Deploy

```bash
# Build
npm run build

# Serve locally
npm run serve

# Deploy to GitHub Pages
GIT_USER=<username> npm run deploy
```

---

## CI/CD Integration

### GitHub Actions (MkDocs)

**.github/workflows/docs.yml:**
```yaml
name: Deploy Documentation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v5

      - uses: actions/setup-python@v6
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          pip install mkdocs-material
          pip install mkdocs-git-revision-date-localized-plugin
          pip install mkdocs-minify-plugin

      - name: Build documentation
        run: mkdocs build

      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./site
```

### GitHub Actions (Docusaurus)

**.github/workflows/deploy.yml:**
```yaml
name: Deploy Docusaurus

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v5

      - uses: actions/setup-node@v6
        with:
          node-version: 22
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Build website
        run: npm run build

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build
```

### Netlify

**netlify.toml:**
```toml
[build]
  command = "mkdocs build"
  publish = "site"

[build.environment]
  PYTHON_VERSION = "3.8"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Vercel

**vercel.json:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "framework": "docusaurus2"
}
```

---

## Best Practices

### 1. Keep Docs Near Code

```
project/
├── src/
├── tests/
└── docs/              # Documentation lives with code
    ├── api/
    ├── guides/
    └── index.md
```

### 2. Review Docs in Pull Requests

**Benefits:**
- Catch outdated information
- Ensure docs match code changes
- Improve documentation quality

**GitHub PR template:**
```markdown
## Documentation
- [ ] Documentation updated for this change
- [ ] New features documented
- [ ] Breaking changes documented in migration guide
```

### 3. Automate Linting

```yaml
# .github/workflows/docs-lint.yml
name: Lint Documentation

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - name: Lint Markdown
        uses: nosborn/github-action-markdown-cli@v3.2.0
        with:
          files: docs/

      - name: Check links
        uses: gaurav-nelson/github-action-markdown-link-check@v1
```

### 4. Use Branch Deployments

**Preview PRs:**
- Deploy docs on every PR
- Review changes before merging
- Catch broken links early

**Netlify Deploy Previews:**
- Automatic PR previews
- Comment with preview URL
- No configuration needed

### 5. Track Analytics

**Google Analytics:**
```javascript
// docusaurus.config.js
module.exports = {
  themeConfig: {
    gtag: {
      trackingID: 'G-XXXXXXXXXX',
    },
  },
};
```

**Plausible (privacy-friendly):**
```javascript
scripts: [
  {
    src: 'https://plausible.io/js/script.js',
    'data-domain': 'docs.example.com',
    defer: true,
  },
],
```

---

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Docusaurus Documentation](https://docusaurus.io/)
- [VitePress Documentation](https://vitepress.dev/)
- [VitePress llms.txt Guide](https://vitepress.dev/guide/llms)
- [Astro Starlight](https://starlight.astro.build/)
- [Write the Docs - Docs as Code](https://www.writethedocs.org/guide/docs-as-code/)
- [Diátaxis Framework](https://diataxis.fr/) - Documentation structure guide
