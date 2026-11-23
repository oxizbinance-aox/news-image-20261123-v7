import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// News Image 23 November 2026 — v7 entrypoint.
// The program is deterministic and offline: it copies the pre-rendered
// broadsheet (entry.png, drawn by draw_news23_v7.py) to the output dir,
// then verifies the copy meets the competition limits (<=1 MiB, 1024x1024).
const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? join(here, "out");
mkdirSync(outDir, { recursive: true });

const src = join(here, "entry.png");
if (!existsSync(src)) {
  throw new Error("entry.png missing next to main.ts");
}
const bytes = readFileSync(src);
if (bytes.length > 1_048_576) {
  throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB limit`);
}
// PNG header: width/height are big-endian uint32 at offsets 16/20.
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width > 1024 || height > 1024) {
  throw new Error(`entry.png is ${width}x${height}, over the 1024x1024 limit`);
}
const dest = join(outDir, "entry.png");
copyFileSync(src, dest);
const digest = createHash("sha256").update(readFileSync(dest)).digest("hex");
console.log(`wrote entry.png to ${outDir} (${bytes.length} bytes, ${width}x${height}, sha256 ${digest})`);
