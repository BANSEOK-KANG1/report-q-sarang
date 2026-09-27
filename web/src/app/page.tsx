import Link from "next/link";
import { HeroSection } from "@/components/HeroSection";
import { NetworkStrip } from "@/components/NetworkStrip";
import { PostCard } from "@/components/PostCard";
import { VisualGuide } from "@/components/VisualGuide";
import { getAllPosts } from "@/lib/posts";

const qLoveEvidenceUrl = "https://olove-research.kangbs2486.chatgpt.site/evidence";

export default function HomePage() {
  const posts = getAllPosts();
  const [featuredPost, ...restPosts] = posts;

  return (
    <div>
      <HeroSection />
      <VisualGuide />

      <section className="mx-auto max-w-6xl px-5 py-16 md:py-20 border-b border-line/70">
        <div className="grid gap-8 md:grid-cols-[1fr_auto] md:items-end">
          <div>
            <p className="text-xs tracking-[0.16em] text-accent uppercase mb-2">Q-LOVE Evidence Archive</p>
            <h2 className="font-display text-3xl md:text-4xl text-gold">연구 자료는 새 근거 아카이브에서 확인하세요</h2>
            <p className="mt-3 text-sm text-ink-soft max-w-2xl leading-7">
              사람 연구, 동물·세포 연구, 리뷰를 먼저 구분하고 원물·추출물·성분의 차이와
              각 논문의 한계를 함께 정리합니다. 연구 결과는 특정 판매 제품의 효능을 뜻하지 않습니다.
            </p>
          </div>
          <a
            href={qLoveEvidenceUrl}
            className="inline-flex items-center justify-center rounded-full border border-gold px-5 py-3 text-sm text-gold hover:bg-gold hover:text-paper transition-colors"
          >
            Q-LOVE 근거 수준 보기 →
          </a>
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
