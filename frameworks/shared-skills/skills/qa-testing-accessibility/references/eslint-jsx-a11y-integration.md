# eslint-plugin-jsx-a11y Integration

How to wire `eslint-plugin-jsx-a11y` into a React/JSX project for static
accessibility linting, with CI enforcement via `--max-warnings=0`.

## Table of Contents

- [Install](#install)
- [Recommended Config (Flat Config)](#recommended-config-flat-config)
- [Legacy .eslintrc Config](#legacy-eslintrc-config)
- [Custom Rule Set](#custom-rule-set)
- [CI Integration](#ci-integration)
- [Rule Coverage vs axe-core](#rule-coverage-vs-axe-core)

---

## Install

```bash
npm install --save-dev eslint eslint-plugin-jsx-a11y
```

Peer dependencies vary by ESLint version. The plugin supports ESLint 8 and 9
(flat config). Verify compatibility at
[github.com/jsx-eslint/eslint-plugin-jsx-a11y](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y).

---

## Recommended Config (Flat Config)

ESLint 9+ uses flat config (`eslint.config.js` or `eslint.config.mjs`).

```js
// eslint.config.js
import jsxA11y from 'eslint-plugin-jsx-a11y';

export default [
  // Apply recommended rules to all JSX/TSX files
  {
    files: ['**/*.{jsx,tsx}'],
    plugins: {
      'jsx-a11y': jsxA11y,
    },
    rules: {
      ...jsxA11y.flatConfigs.recommended.rules,
    },
  },
];
```

The `recommended` rule set enables all rules at `error` level that have
consistent, low-false-positive detection. See the full rule list at
[github.com/jsx-eslint/eslint-plugin-jsx-a11y#supported-rules](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y#supported-rules).

---

## Legacy .eslintrc Config

For projects still on ESLint 8 with `.eslintrc.js` or `.eslintrc.json`:

```json
{
  "extends": [
    "plugin:jsx-a11y/recommended"
  ],
  "plugins": [
    "jsx-a11y"
  ]
}
```

---

## Custom Rule Set

Override individual rules when the recommended level is too strict or too
lenient for your project:

```js
// eslint.config.js — selective overrides on top of recommended
import jsxA11y from 'eslint-plugin-jsx-a11y';

export default [
  {
    files: ['**/*.{jsx,tsx}'],
    plugins: { 'jsx-a11y': jsxA11y },
    rules: {
      // Start from recommended
      ...jsxA11y.flatConfigs.recommended.rules,

      // Downgrade to warn during an incremental rollout
      'jsx-a11y/no-autofocus': 'warn',

      // Upgrade to error if your design system requires it
      'jsx-a11y/anchor-has-content': 'error',

      // Disable if your icon-button pattern uses title attributes
      // and you have a project-wide component wrapping it safely
      // 'jsx-a11y/control-has-associated-label': 'off',
    },
  },
];
```

> Tip: Prefer keeping rules at `error` and add inline `eslint-disable` comments
> with a justification rather than project-wide downgrades. This keeps the
> intent visible in code review.

---

## CI Integration

### Zero-Warning Gate

Run ESLint with `--max-warnings=0` so any accessibility warning fails the build:

```bash
npx eslint 'src/**/*.{jsx,tsx}' --max-warnings=0
```

### GitHub Actions Step

```yaml
- name: Lint accessibility (jsx-a11y)
  run: npx eslint 'src/**/*.{jsx,tsx}' --max-warnings=0
```

Add after your install step. No separate server or browser required — this is a
static analysis pass that runs in seconds.

### Incremental Rollout on Legacy Codebases

For large codebases with many existing violations:

1. Run with `--max-warnings=9999` to get a baseline count without blocking.
2. Fix violations in batches (critical rules first: `alt-text`, `label`,
   `interactive-supports-focus`).
3. Tighten the threshold each sprint: `--max-warnings=200`, then `100`, then `0`.
4. Track the warning count trend in CI artefacts.

```bash
# Output warning count to CI log for tracking
npx eslint 'src/**/*.{jsx,tsx}' --format json | \
  node -e "
    const r = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
    const w = r.reduce((n,f)=>n+f.warningCount,0);
    console.log('jsx-a11y warnings:', w);
  "
```

---

## Rule Coverage vs axe-core

`eslint-plugin-jsx-a11y` is a **static** analysis tool — it runs at build time
on JSX source code. axe-core is a **runtime** tool — it runs against rendered
DOM in a browser.

| Capability | jsx-a11y | axe-core |
|------------|----------|----------|
| Runs without a browser | Yes | No |
| Catches JSX prop errors (e.g. missing `alt`) | Yes | Yes (rendered) |
| Catches dynamic content issues | No | Yes |
| Catches color contrast failures | No | Yes |
| Catches ARIA state errors at runtime | No | Yes |
| CI stage | PR lint step (fast) | PR E2E or component test |

Use both: jsx-a11y for fast feedback during development and PR linting, axe-core
for runtime verification in component and E2E tests.
