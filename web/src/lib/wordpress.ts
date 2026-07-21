/** measuremkt.com WordPress REST (read-only, public). */

export type WpPost = {
  id: number;
  slug: string;
  title: string;
  excerpt: string;
  link: string;
  date: string;
};

const WP_REST =
  process.env.NEXT_PUBLIC_WP_REST_URL?.replace(/\/$/, "") ??
  "https://measuremkt.com/wp-json/wp/v2";

export async function fetchHubPosts(limit = 3): Promise<WpPost[]> {
  try {
    const res = await fetch(
      `${WP_REST}/posts?per_page=${limit}&_fields=id,slug,title,excerpt,link,date&orderby=date`,
      { next: { revalidate: 3600 } }
    );
    if (!res.ok) return [];
    const data = (await res.json()) as Array<{
      id: number;
      slug: string;
      title: { rendered: string };
      excerpt: { rendered: string };
      link: string;
      date: string;
    }>;
    return data.map((p) => ({
      id: p.id,
      slug: p.slug,
      title: stripHtml(p.title.rendered),
      excerpt: stripHtml(p.excerpt.rendered),
      link: p.link,
      date: p.date.slice(0, 10),
    }));
  } catch {
    return [];
  }
}

function stripHtml(html: string): string {
  return html.replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
}
