// LEGACY: only needed on Playwright < 1.52. Since 1.52, use the built-in
// `failOnFlakyTests` config option instead — see SKILL.md Defaults and
// references/playwright-ci.md "Fail CI on Rerun-Pass Flakes".

// Playwright custom reporter: fail CI if any test passes on retry (rerun-pass).
// Usage (example):
//   // playwright.config.ts
//   reporter: [
//     ['html', { open: 'never' }],
//     ['./playwright/fail-on-flaky-reporter.js'],
//   ],
//
// Notes:
// - Add retries in CI (e.g., retries: 2) to collect traces, but still fail on rerun-pass.
// - Keep artifacts (trace/video/screenshot) to debug the flake quickly.
//
// Reporter API: https://playwright.dev/docs/test-reporters

class FailOnFlakyReporter {
  constructor() {
    this._rerunPasses = [];
  }

  onTestEnd(test, result) {
    if (result.status === 'passed' && result.retry > 0) {
      const titlePath = typeof test.titlePath === 'function' ? test.titlePath() : [test.title];
      this._rerunPasses.push({
        test: titlePath.join(' > '),
        retry: result.retry,
      });
    }
  }

  async onEnd() {
    if (this._rerunPasses.length === 0) return;

    // Override the runner result; setting process.exitCode alone can be overwritten.

    console.error('\nFlaky tests detected (passed on retry):');
    for (const item of this._rerunPasses) {
      console.error(`- ${item.test} (retry=${item.retry})`);
    }
    console.error('Fix root cause; do not silence with weaker assertions.');
    return { status: 'failed' };
  }
}

module.exports = FailOnFlakyReporter;
