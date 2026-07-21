#!/usr/bin/env node
/** Sync ../content/{blog,research} into web/content for Vercel (root=web). */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.join(__dirname, "..", "..");

const SYNC_DIRS = [
  {
    name: "blog",
    src: path.join(repoRoot, "content", "blog"),
    dest: path.join(__dirname, "..", "content", "blog"),
    skip: ["README.md", "PUBLISH_CHECKLIST.md"],
  },
  {
    name: "research",
    src: path.join(repoRoot, "content", "research"),
    dest: path.join(__dirname, "..", "content", "research"),
    skip: ["README.md"],
  },
];

for (const { name, src, dest, skip } of SYNC_DIRS) {
  if (!fs.existsSync(src)) {
    console.log(`[sync-content] no ${src}, skipping ${name}`);
    continue;
  }
  fs.mkdirSync(dest, { recursive: true });
  let n = 0;
  for (const file of fs.readdirSync(src)) {
    if (!file.endsWith(".md")) continue;
    if (skip.includes(file)) continue;
    fs.copyFileSync(path.join(src, file), path.join(dest, file));
    n += 1;
  }
  console.log(`[sync-content] ${name}: ${n} files ${src} -> ${dest}`);
}
