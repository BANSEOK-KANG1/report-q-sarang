import { getAllPosts } from "@/lib/posts";
import { siteConfig } from "@/lib/site-config";

export const dynamic = "force-static";

function escapeXml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

export async function GET() {
  const siteUrl = siteConfig.url.replace(/\/$/, "");
  const posts = getAllPosts();

  const staticPages = [
    { path: "/", changefreq: "weekly", priority: "1.0" },
    { path: "/blog", changefreq: "weekly", priority: "0.95" },
    { path: "/about", changefreq: "monthly", priority: "0.5" },
    { path: "/editorial", changefreq: "monthly", priority: "0.4" },
    { path: "/privacy", changefreq: "monthly", priority: "0.3" },
    { path: "/contact", changefreq: "monthly", priority: "0.4" },
  ];

  const urls = [
    ...staticPages.map(
      (page) =>
        `<url><loc>${escapeXml(siteUrl)}${page.path === "/" ? "/" : page.path}</loc><changefreq>${page.changefreq}</changefreq><priority>${page.priority}</priority></url>`,
    ),
    ...posts.map((post) => {
      const lastmod = post.date ? `<lastmod>${escapeXml(post.date)}</lastmod>` : "";
      return `<url><loc>${escapeXml(siteUrl)}/blog/${escapeXml(post.slug)}</loc>${lastmod}<changefreq>monthly</changefreq><priority>0.85</priority></url>`;
    }),
  ].join("\n");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>`;

  return new Response(xml, {
    headers: { "Content-Type": "application/xml; charset=utf-8" },
  });
}
