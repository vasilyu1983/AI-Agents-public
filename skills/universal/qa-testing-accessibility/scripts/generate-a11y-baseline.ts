/**
 * generate-a11y-baseline.ts
 *
 * Crawls one or more URLs with axe-core via Playwright and writes a baseline
 * snapshot to `tests/a11y-baseline.json`.  Run whenever you want to reset or
 * refresh the baseline after a bulk remediation sprint.
 *
 * Usage:
 *   npx tsx scripts/generate-a11y-baseline.ts
 *
 * Environment variables:
 *   BASE_URL   – root URL to scan (default: http://localhost:3000)
 *   PATHS      – comma-separated paths to scan (default: /)
 *   OUT_FILE   – output path for the baseline JSON
 *               (default: tests/a11y-baseline.json)
 *   AXE_TAGS   – comma-separated axe tag set
 *               (default: wcag2a,wcag2aa,wcag21a,wcag21aa,wcag22aa)
 *
 * Example — scan three pages:
 *   BASE_URL=https://staging.example.com PATHS=/,/login,/dashboard \
 *     npx tsx scripts/generate-a11y-baseline.ts
 */

import { chromium, type Browser, type Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { writeFileSync, mkdirSync } from 'fs';
import { dirname } from 'path';

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const BASE_URL = process.env.BASE_URL ?? 'http://localhost:3000';
const PATHS = (process.env.PATHS ?? '/').split(',').map((p) => p.trim());
const OUT_FILE = process.env.OUT_FILE ?? 'tests/a11y-baseline.json';
const AXE_TAGS = (process.env.AXE_TAGS ?? 'wcag2a,wcag2aa,wcag21a,wcag21aa,wcag22aa')
  .split(',')
  .map((t) => t.trim());

function validateConfiguration(): void {
  let base: URL;
  try {
    base = new URL(BASE_URL);
  } catch {
    throw new Error('BASE_URL must be an absolute HTTP(S) URL');
  }
  if (!['http:', 'https:'].includes(base.protocol) || base.username || base.password || base.search || base.hash || /[\u0000-\u001f\u007f]/.test(BASE_URL)) {
    throw new Error('BASE_URL must use HTTP(S), without credentials, query, or fragment');
  }
  if (PATHS.some((path) => !path.startsWith('/') || path.startsWith('//') || path.includes('\\') || path.includes('#') || /[\u0000-\u001f\u007f]/.test(path) || new URL(path, base).origin !== base.origin)) {
    throw new Error('PATHS must contain non-empty root-relative paths without fragments or backslashes');
  }
  if (!OUT_FILE.trim()) throw new Error('OUT_FILE must not be empty');
  if (AXE_TAGS.some((tag) => !tag)) throw new Error('AXE_TAGS must contain non-empty tags');
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface BaselineEntry {
  id: string;
  impact: string | null;
  description: string;
  nodeCount: number;
  pages: string[];
  /** rule|path|target — the CI gate compares these, not nodeCount */
  fingerprints: string[];
  snapshotDate: string;
}

/**
 * Stable per-node key. Comparing node counts per rule lets one fixed node
 * hide one new node of the same rule; comparing fingerprints does not.
 * `target` is JSON-encoded because iframe/shadow-DOM targets are nested arrays.
 */
function fingerprint(ruleId: string, path: string, target: unknown): string {
  return `${ruleId}|${path}|${JSON.stringify(target)}`;
}

// ---------------------------------------------------------------------------
// Core
// ---------------------------------------------------------------------------

async function scanPage(page: Page, url: string, path: string): Promise<BaselineEntry[]> {
  const response = await page.goto(url, { waitUntil: 'networkidle' });
  if (!response || !response.ok()) {
    throw new Error(`Scan failed for ${path}: HTTP ${response?.status() ?? 'no response'}`);
  }

  const results = await new AxeBuilder({ page })
    .withTags(AXE_TAGS)
    .analyze();

  const snapshotDate = new Date().toISOString();

  return results.violations.map((v) => ({
    id: v.id,
    impact: v.impact ?? null,
    description: v.description,
    nodeCount: v.nodes.length,
    pages: [path],
    fingerprints: v.nodes.map((n) => fingerprint(v.id, path, n.target)),
    snapshotDate,
  }));
}

function mergeEntries(all: BaselineEntry[]): BaselineEntry[] {
  const map = new Map<string, BaselineEntry>();

  for (const entry of all) {
    const existing = map.get(entry.id);
    if (!existing) {
      map.set(entry.id, { ...entry });
    } else {
      existing.nodeCount += entry.nodeCount;
      existing.pages = Array.from(new Set([...existing.pages, ...entry.pages]));
      existing.fingerprints = [...existing.fingerprints, ...entry.fingerprints];
    }
  }

  return Array.from(map.values()).sort((a, b) => {
    // Sort by impact severity then rule ID for stable diffs
    const order = ['critical', 'serious', 'moderate', 'minor'];
    const aIdx = order.indexOf(a.impact ?? '');
    const bIdx = order.indexOf(b.impact ?? '');
    if (aIdx !== bIdx) return aIdx - bIdx;
    return a.id.localeCompare(b.id);
  });
}

async function generateBaseline(): Promise<void> {
  validateConfiguration();
  console.log(`Scanning ${PATHS.length} path(s) on ${BASE_URL}`);
  console.log(`axe tags: ${AXE_TAGS.join(', ')}`);

  let browser: Browser | undefined;

  try {
    browser = await chromium.launch();
    const page = await browser.newPage();

    const allEntries: BaselineEntry[] = [];

    for (const path of PATHS) {
      const url = new URL(path, BASE_URL).href;
      console.log(`  → ${url}`);
      const entries = await scanPage(page, url, path);
      console.log(`     ${entries.length} violation rule(s) found`);
      allEntries.push(...entries);
    }

    const baseline = mergeEntries(allEntries);

    mkdirSync(dirname(OUT_FILE), { recursive: true });
    writeFileSync(OUT_FILE, JSON.stringify(baseline, null, 2) + '\n');

    console.log(`\nBaseline written to ${OUT_FILE}`);
    console.log(`Total unique violation rules: ${baseline.length}`);

    const bySeverity = baseline.reduce<Record<string, number>>((acc, e) => {
      const key = e.impact ?? 'unknown';
      acc[key] = (acc[key] ?? 0) + 1;
      return acc;
    }, {});
    for (const [severity, count] of Object.entries(bySeverity)) {
      console.log(`  ${severity}: ${count}`);
    }
  } finally {
    await browser?.close();
  }
}

generateBaseline().catch((err) => {
  console.error('Baseline generation failed:', err);
  process.exit(1);
});
