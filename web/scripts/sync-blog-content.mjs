#!/usr/bin/env node
/** Sync ../content/blog into web/content/blog for Vercel (root=web). */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const src = path.join(__dirname, "..", "..", "content", "blog");
const dest = path.join(__dirname, "..", "content", "blog");

if (!fs.existsSync(src)) {
  console.log("[sync-blog] no ../content/blog, using existing web/content/blog");
  process.exit(0);
}

fs.mkdirSync(dest, { recursive: true });
for (const name of fs.readdirSync(src)) {
  if (!name.endsWith(".md")) continue;
  if (["README.md", "PUBLISH_CHECKLIST.md"].includes(name)) continue;
  fs.copyFileSync(path.join(src, name), path.join(dest, name));
}
console.log("[sync-blog] synced from", src, "->", dest);
