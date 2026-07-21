import { ResearchCard } from "@/components/ResearchCard";
import { getAllInsights } from "@/lib/insights";

export const metadata = {
  title: "연구 인사이트",
  description:
    "코디세핀·Cordyceps militaris 관련 학술 논문 전문 요약, 번역 정리, 인사이트 (교육·연구용)",
};

export default function ResearchPage() {
  const insights = getAllInsights();
  const [featured, ...rest] = insights;

  return (
    <div>
      <section className="border-b border-line/70 bg-paper-deep/20">
        <div className="mx-auto max-w-6xl px-5 py-12 md:py-16">
          <p className="text-xs tracking-[0.2em] text-accent mb-3 uppercase">Research · Evidence</p>
          <h1 className="font-display text-4xl md:text-5xl text-gold leading-tight">연구 인사이트</h1>
          <p className="mt-4 text-ink-soft max-w-2xl leading-relaxed">
            PubMed·OpenAlex·Europe PMC에서 수집한 논문을 **전문적으로 요약·번역 정리**한 페이지입니다.
            브랜드 블로그(이야기)와 달리, 논문 단위의 학술 인사이트를 다룹니다.
          </p>
          <p className="mt-3 text-sm text-ink-soft max-w-2xl leading-relaxed border-l-2 border-gold/50 pl-4">
            질병·효능 주장이 아닌 연구·교육 목적 자료입니다. Europe PMC · OpenAlex · Crossref API
            연동 시각 자료 포함.
          </p>
        </div>
      </section>

      <div className="mx-auto max-w-4xl px-5 py-14">
        <p className="text-sm text-ink-soft mb-10">
          총 <strong className="text-ink">{insights.length}</strong>편 · GitHub 파이프라인 자동 갱신
        </p>
        <div className="space-y-10">
          {featured ? <ResearchCard insight={featured} featured /> : null}
          {rest.map((item) => (
            <ResearchCard key={item.slug} insight={item} />
          ))}
        </div>
      </div>
    </div>
  );
}
