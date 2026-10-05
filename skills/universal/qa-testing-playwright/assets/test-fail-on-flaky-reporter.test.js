// Run with node --test assets/test-fail-on-flaky-reporter.test.js.
const assert = require('node:assert/strict');
const { test } = require('node:test');
const Reporter = require('./template-playwright-fail-on-flaky-reporter.js');

test('rerun-pass overrides an otherwise passed runner result', async () => {
  const reporter = new Reporter();
  reporter.onTestEnd({ titlePath: () => ['checkout'] }, { status: 'passed', retry: 1 });
  const result = await reporter.onEnd({ status: 'passed' });
  assert.equal(result?.status, 'failed');
});

test('first-attempt passes leave the runner result unchanged', async () => {
  const reporter = new Reporter();
  reporter.onTestEnd({ title: 'checkout' }, { status: 'passed', retry: 0 });
  assert.equal(await reporter.onEnd({ status: 'passed' }), undefined);
});

test('failed retries leave the runner failure unchanged', async () => {
  const reporter = new Reporter();
  reporter.onTestEnd({ title: 'checkout' }, { status: 'failed', retry: 1 });
  assert.equal(await reporter.onEnd({ status: 'failed' }), undefined);
});
