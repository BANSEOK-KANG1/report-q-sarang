import fs from "fs";
import path from "path";
import matter from "gray-matter";

export type BlogPost = {
  slug: string;
  title: string;
  description: string;
  date: string;
  category: string;
  keywords: string[];
  body: string;
};

function contentDir(): string {
  const candidates = [
    path.join(process.cwd(), "content", "blog"),
    path.join(process.cwd(), "..", "content", "blog"),
    path.join(process.cwd(), "web", "content", "blog"),
  ];
  for (const dir of candidates) {
    if (fs.existsSync(dir)) return dir;
  }
  return candidates[0];
}

function isPostFile(name: string): boolean {
  return (
    name.endsWith(".md") &&
    !["README.md", "PUBLISH_CHECKLIST.md"].includes(name)
  );
}

export function getAllPosts(): BlogPost[] {
  const dir = contentDir();
  if (!fs.existsSync(dir)) return [];
  const files = fs.readdirSync(dir).filter(isPostFile);
  const posts = files.map((file) => {
    const raw = fs.readFileSync(path.join(dir, file), "utf8");
    const { data, content } = matter(raw);
    let body = content.trim();
    // drop duplicate H1
    const lines = body.split("\n");
    if (lines[0]?.startsWith("# ")) {
      body = lines.slice(1).join("\n").trim();
    }
    return {
      slug: String(data.slug || file.replace(/\.md$/, "")),
      title: String(data.title || file),
      description: String(data.description || "").replace(/\*\*/g, ""),
      date: String(data.date || ""),
      category: String(data.category || "education"),
      keywords: Array.isArray(data.keywords) ? data.keywords.map(String) : [],
      body,
    } satisfies BlogPost;
  });
  return posts.sort((a, b) => (a.date < b.date ? 1 : -1));
}

export function getPost(slug: string): BlogPost | null {
  return getAllPosts().find((p) => p.slug === slug) ?? null;
}

export function getPostSlugs(): string[] {
  return getAllPosts().map((p) => p.slug);
}
