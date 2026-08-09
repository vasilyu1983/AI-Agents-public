#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const SECURITY_WARNING =
  "Security warning: Mammoth does not sanitize HTML or links from untrusted DOCX input. Sanitize before rendering or storing the output.";

function usage() {
  console.error(
    [
      "Usage:",
      "  node scripts/docx_to_html.mjs <input.docx> <output.html> [--style-map file.txt] [--extract-images-dir dir]",
      "",
      "Options:",
      "  --style-map <file>         Mammoth style-map file to control HTML mappings",
      "  --extract-images-dir <dir> Write extracted images to this directory and link them relatively",
    ].join("\n"),
  );
}

function parseArgs(argv) {
  const positional = [];
  let styleMapPath = null;
  let extractImagesDir = null;

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--style-map") {
      styleMapPath = argv[index + 1];
      index += 1;
    } else if (arg === "--extract-images-dir") {
      extractImagesDir = argv[index + 1];
      index += 1;
    } else {
      positional.push(arg);
    }
  }

  if (!styleMapPath && argv.includes("--style-map")) {
    throw new Error("Missing value for --style-map");
  }
  if (!extractImagesDir && argv.includes("--extract-images-dir")) {
    throw new Error("Missing value for --extract-images-dir");
  }
  if (positional.length < 2) {
    usage();
    process.exit(2);
  }

  return {
    inputPath: positional[0],
    outputPath: positional[1],
    styleMapPath,
    extractImagesDir,
  };
}

function extensionFromContentType(contentType) {
  const mapping = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/svg+xml": "svg",
    "image/tiff": "tiff",
    "image/bmp": "bmp",
    "image/webp": "webp",
    "image/x-emf": "emf",
    "image/x-wmf": "wmf",
  };
  return mapping[contentType] || "bin";
}

async function main(argv) {
  const { inputPath, outputPath, styleMapPath, extractImagesDir } = parseArgs(argv);

  let mammoth;
  try {
    mammoth = await import("mammoth");
  } catch (err) {
    console.error("Missing dependency: mammoth. Install with: npm i mammoth");
    process.exit(2);
  }

  if (!fs.existsSync(inputPath)) {
    throw new Error(`Input not found: ${inputPath}`);
  }

  const options = {};

  if (styleMapPath) {
    if (!fs.existsSync(styleMapPath)) {
      throw new Error(`Style-map file not found: ${styleMapPath}`);
    }
    const styleMap = fs
      .readFileSync(styleMapPath, "utf-8")
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter((line) => line && !line.startsWith("#"));
    options.styleMap = styleMap;
  }

  if (extractImagesDir) {
    const absoluteImagesDir = path.resolve(extractImagesDir);
    const absoluteOutputPath = path.resolve(outputPath);
    const outputDir = path.dirname(absoluteOutputPath);
    fs.mkdirSync(absoluteImagesDir, { recursive: true });

    let imageCount = 0;
    options.convertImage = mammoth.images.imgElement(async (image) => {
      imageCount += 1;
      const extension = extensionFromContentType(image.contentType);
      const fileName = `image-${String(imageCount).padStart(3, "0")}.${extension}`;
      const absoluteImagePath = path.join(absoluteImagesDir, fileName);
      const base64 = await image.read("base64");
      fs.writeFileSync(absoluteImagePath, Buffer.from(base64, "base64"));

      let relativePath = path.relative(outputDir, absoluteImagePath);
      if (!relativePath) {
        relativePath = fileName;
      }
      relativePath = relativePath.split(path.sep).join("/");
      return { src: relativePath };
    });
  }

  const docxBuffer = fs.readFileSync(inputPath);
  const result = await mammoth.convertToHtml({ buffer: docxBuffer }, options);

  const html = [
    "<!doctype html>",
    "<html>",
    "<head>",
    '  <meta charset="utf-8">',
    '  <meta name="generator" content="mammoth.js">',
    "</head>",
    "<body>",
    `<!-- ${SECURITY_WARNING} -->`,
    result.value,
    "</body>",
    "</html>",
    "",
  ].join("\n");

  fs.writeFileSync(outputPath, html, { encoding: "utf-8" });

  console.error(SECURITY_WARNING);

  if (result.messages?.length) {
    for (const message of result.messages) {
      console.error(String(message));
    }
  }
}

main(process.argv.slice(2)).catch((err) => {
  console.error(String(err));
  process.exit(2);
});
