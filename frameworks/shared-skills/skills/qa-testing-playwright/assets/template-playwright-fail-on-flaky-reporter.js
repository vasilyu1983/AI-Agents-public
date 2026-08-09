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

  onEnd() {
    if (this._rerunPasses.length === 0) return;

    // Ensure the run fails, while still allowing CI to upload artifacts.
    process.exitCode = 1;

    console.error('\nFlaky tests detected (passed on retry):');
    for (const item of this._rerunPasses) {
      console.error(`- ${item.test} (retry=${item.retry})`);
    }
    console.error('Fix root cause; do not silence with weaker assertions.');
  }
}

module.exports = FailOnFlakyReporter;
