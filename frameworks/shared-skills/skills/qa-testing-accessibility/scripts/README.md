# Scripts

Runnable utilities for the `qa-testing-accessibility` skill.

## generate-a11y-baseline.ts

Crawls one or more application URLs with axe-core via Playwright and writes a
baseline snapshot (`tests/a11y-baseline.json`) that the CI gate can compare
against. Use this to establish an initial baseline on a legacy codebase, or to
refresh it after a bulk remediation sprint.

### Prerequisites

Install the required packages in your project:

```bash
npm install --save-dev @playwright/test @axe-core/playwright tsx
npx playwright install chromium
```

> `tsx` is used to execute TypeScript directly without a separate compile step.
> If your project already has `ts-node` or a similar runner, use that instead.

### Run

```bash
npx tsx scripts/generate-a11y-baseline.ts
```

By default the script hits `http://localhost:3000/` and writes to
`tests/a11y-baseline.json`. Start your dev server before running.

### Environment Variables

| Variable   | Default                       | Description                                          |
|------------|-------------------------------|------------------------------------------------------|
| `BASE_URL` | `http://localhost:3000`       | Root URL to scan                                     |
| `PATHS`    | `/`                           | Comma-separated paths to scan (e.g. `/,/login`)      |
| `OUT_FILE` | `tests/a11y-baseline.json`    | Output path for the baseline JSON                    |
| `AXE_TAGS` | `wcag2a,wcag2aa,wcag22aa`     | Comma-separated axe tag set                          |

### Example — scan multiple pages against staging

```bash
BASE_URL=https://staging.example.com \
  PATHS=/,/login,/dashboard \
  OUT_FILE=tests/a11y-baseline.json \
  npx tsx scripts/generate-a11y-baseline.ts
```

### Output format

The script writes a JSON array of violation records:

```json
[
  {
    "id": "color-contrast",
    "impact": "serious",
    "description": "Elements must meet minimum color contrast ratio thresholds",
    "nodeCount": 12,
    "pages": ["/", "/login"],
    "snapshotDate": "2026-04-27T10:00:00.000Z"
  }
]
```

### Commit and version-control the baseline

Commit `tests/a11y-baseline.json` alongside your tests. The CI gate (see
`references/ci-accessibility-gates.md`) uses it to block only *new* violations,
not pre-existing ones.

### Reduce the baseline over time

- Review the baseline monthly.
- Fix violations grouped by impact (critical first, then serious).
- Re-run this script after each remediation sprint to shrink the baseline.
- Track baseline size as a team metric — a baseline that grows is a regression signal.
