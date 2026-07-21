import Link from "next/link";
import { siteConfig } from "@/lib/site-config";
import { fetchHubPosts } from "@/lib/wordpress";

export async function NetworkStrip() {
  const posts = await fetchHubPosts(3);

  return (
    <section className="border-t border-line/70 bg-paper-deep/40">
      <div className="mx-auto max-w-6xl px-5 py-12 md:py-14">
        <div className="grid gap-10 md:grid-cols-[1fr_1.2fr] items-start">
          <div>
            <p className="text-xs tracking-[0.16em] text-accent uppercase mb-2">Network</p>
            <h2 className="font-display text-2xl text-gold">measuremkt 네트워크</h2>
            <p className="mt-3 text-sm text-ink-soft leading-relaxed">
              큐사랑 · 제왕충초는{" "}
              <a href={siteConfig.parentUrl} className="text-gold underline">
                {siteConfig.parentLabel}
              </a>
              와 같은 네트워크에서 운영됩니다. 측정·데이터 가이드는 메인 사이트에서,
              브랜드 이야기는 이곳에서 읽을 수 있습니다.
            </p>
            <div className="mt-5 flex flex-wrap gap-3 text-sm">
              <a
                href={siteConfig.parentUrl}
                className="border border-line px-4 py-2 text-ink-soft hover:border-gold hover:text-gold transition-colors"
              >
                메인 사이트 →
              </a>
              <a
                href="https://sports.measuremkt.com/"
                className="border border-line px-4 py-2 text-ink-soft hover:border-gold hover:text-gold transition-colors"
              >
                스포츠 →
              </a>
            </div>
          </div>

          {posts.length > 0 ? (
            <div>
              <p className="text-xs text-ink-soft mb-4">메인 사이트 최신 글</p>
              <ul className="space-y-4">
                {posts.map((post) => (
                  <li key={post.id} className="border-b border-line/60 pb-4 last:border-0">
                    <a
                      href={post.link}
                      className="font-medium text-ink hover:text-gold transition-colors leading-snug"
                    >
                      {post.title}
                    </a>
                    <p className="mt-1 text-xs text-ink-soft line-clamp-2">{post.excerpt}</p>
                  </li>
                ))}
              </ul>
              <Link
                href={siteConfig.parentUrl}
                className="inline-block mt-4 text-sm text-gold hover:underline"
              >
                measuremkt.com 더 보기 →
              </Link>
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}
