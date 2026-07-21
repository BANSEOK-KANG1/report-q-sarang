import Link from "next/link";
import { HeroSection } from "@/components/HeroSection";
import { NetworkStrip } from "@/components/NetworkStrip";
import { PostCard } from "@/components/PostCard";
import { VisualGuide } from "@/components/VisualGuide";
import { getAllPosts } from "@/lib/posts";

export default function HomePage() {
  const posts = getAllPosts();
  const [featured, ...rest] = posts;

  return (
    <div>
      <HeroSection />
      <VisualGuide />

      <section className="mx-auto max-w-6xl px-5 py-16 md:py-20">
        <div className="flex items-end justify-between mb-10">
          <div>
            <p className="text-xs tracking-[0.16em] text-accent uppercase mb-2">Journal</p>
            <h2 className="font-display text-3xl md:text-4xl text-gold">최신 이야기</h2>
          </div>
          <Link href="/blog" className="text-sm text-ink-soft hover:text-gold">
            전체 보기 →
          </Link>
        </div>

        <div className="space-y-12">
          {featured ? <PostCard post={featured} featured /> : null}
          {rest.slice(0, 3).map((post) => (
            <PostCard key={post.slug} post={post} />
          ))}
        </div>
      </section>

      <NetworkStrip />
    </div>
  );
}
