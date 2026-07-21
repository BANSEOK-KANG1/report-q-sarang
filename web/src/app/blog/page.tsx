import { ArticleImage } from "@/components/ArticleImage";
import { PostCard } from "@/components/PostCard";
import { getAllPosts } from "@/lib/posts";
import { visuals } from "@/lib/visuals";

export const metadata = {
  title: "이야기",
};

export default function BlogPage() {
  const posts = getAllPosts();
  const hero = visuals.hero;

  return (
    <div>
      <section className="border-b border-line/70">
        <div className="mx-auto max-w-6xl px-5 py-12 md:py-16">
          <div className="grid gap-8 lg:grid-cols-[1fr_1.2fr] items-center">
            <header>
              <p className="text-xs tracking-[0.2em] text-accent mb-3 uppercase">Journal</p>
              <h1 className="font-display text-4xl md:text-5xl text-gold leading-tight">이야기</h1>
              <p className="mt-4 text-ink-soft max-w-xl leading-relaxed">
                코디세핀, Cordyceps militaris, 그리고 제왕충초 담금주 — 이름을 바르게 쓰는 글모음.
              </p>
            </header>
            <ArticleImage
              src={hero.src}
              alt={hero.alt}
              caption={hero.caption}
              aspect="wide"
              priority
            />
          </div>
        </div>
      </section>

      <div className="mx-auto max-w-6xl px-5 py-14">
        <div className="space-y-10">
          {posts.map((post, i) => (
            <PostCard key={post.slug} post={post} featured={i === 0} />
          ))}
        </div>
      </div>
    </div>
  );
}
