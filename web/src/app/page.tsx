import Link from "next/link";
import { HeroSection } from "@/components/HeroSection";
import { NetworkStrip } from "@/components/NetworkStrip";
import { PostCard } from "@/components/PostCard";
import { ResearchCard } from "@/components/ResearchCard";
import { VisualGuide } from "@/components/VisualGuide";
import { getAllInsights } from "@/lib/insights";
import { getAllPosts } from "@/lib/posts";

export default function HomePage() {
  const posts = getAllPosts();
  const insights = getAllInsights();
  const [featuredPost, ...restPosts] = posts;
  const [featuredInsight, ...restInsights] = insights;

  return (
    <div>
      <HeroSection />
      <VisualGuide />

      <section className="mx-auto max-w-6xl px-5 py-16 md:py-20 border-b border-line/70">
        <div className="flex items-end justify-between mb-10">
          <div>
            <p className="text-xs tracking-[0.16em] text-accent uppercase mb-2">Research</p>
            <h2 className="font-display text-3xl md:text-4xl text-gold">연구 인사이트</h2>
            <p className="mt-2 text-sm text-ink-soft max-w-xl">
              논문을 할머니도 읽기 쉽게 풀어 쓴 페이지 — GitHub 파이프라인 자동 갱신
            </p>
          </div>
          <Link href="/research" className="text-sm text-ink-soft hover:text-gold shrink-0">
            전체 보기 →
          </Link>
        </div>
        <div className="space-y-10">
          {featuredInsight ? <ResearchCard insight={featuredInsight} featured /> : null}
          {restInsights.slice(0, 3).map((item) => (
            <ResearchCard key={item.slug} insight={item} />
          ))}
        </div>
      </section>

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
          {featuredPost ? <PostCard post={featuredPost} featured /> : null}
          {restPosts.slice(0, 3).map((post) => (
            <PostCard key={post.slug} post={post} />
          ))}
        </div>
      </section>

      <NetworkStrip />
    </div>
  );
}
