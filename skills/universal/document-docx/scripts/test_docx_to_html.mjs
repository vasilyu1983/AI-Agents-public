import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import path from "node:path";
import test from "node:test";

const script = path.join(import.meta.dirname, "docx_to_html.mjs");

test("unknown conversion option fails before document processing", () => {
  const result = spawnSync(process.execPath, [script, "input.docx", "output.html", "--sanitize"], {
    encoding: "utf8",
  });
  assert.equal(result.status, 2);
  assert.match(result.stderr, /Unknown option: --sanitize/);
});
