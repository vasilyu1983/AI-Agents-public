#!/usr/bin/env node
import fs from "node:fs";
import process from "node:process";

async function main(argv) {
  if (argv.length < 2) {
    console.error("Usage: node scripts/docx_to_html.mjs <input.docx> <output.html>");
    process.exit(2);
  }

  const [inputPath, outputPath] = argv;

  let mammoth;
  try {
    mammoth = await import("mammoth");
  } catch (err) {
    console.error("Missing dependency: mammoth. Install with: npm i mammoth");
    process.exit(2);
  }

  const docxBuffer = fs.readFileSync(inputPath);
  const result = await mammoth.convertToHtml({ buffer: docxBuffer });
  const html = `<!doctype html><html><head><meta charset="utf-8"></head><body>${result.value}</body></html>`;

  fs.writeFileSync(outputPath, html, { encoding: "utf-8" });

  if (result.messages?.length) {
    for (const message of result.messages) console.error(String(message));
  }
}

main(process.argv.slice(2)).catch((err) => {
  console.error(String(err));
  process.exit(2);
});

