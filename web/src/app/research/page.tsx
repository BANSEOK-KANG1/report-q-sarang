import { ResearchCard } from "@/components/ResearchCard";
import { getAllInsights } from "@/lib/insights";

export const metadata = {
  title: "연구 인사이트",
  description:
    "코디세핀·Cordyceps militaris 효능·생리활성 관련 학술 논문을 쉽게 정리 (교육·연구용, 제품 효능 주장 아님)",
};

export default function ResearchPage() {
  const insights = getAllInsights();
  const [featured, ...rest] = insights;

  return (
    <div>
      <section className="border-b border-line/70 bg-paper-deep/20">
        <div className="mx-auto max-w-6xl px-5 py-12 md:py-16">
          <p className="text-xs tracking-[0.2em] text-accent mb-3 uppercase">Research · Efficacy themes</p>
          <h1 className="font-display text-4xl md:text-5xl text-gold leading-tight">연구 인사이트</h1>
          <p className="mt-4 text-ink-soft max-w-2xl leading-relaxed">
            면역·피로·운동·항산화 등 **생리활성·효능 관련 주제**의 논문을 골라, 할머니도 읽기 쉽게
            풀어 쓴 페이지입니다. 제품 효능을 주장하지 않습니다.
          </p>
          <p className="mt-3 text-sm text-ink-soft max-w-2xl leading-relaxed border-l-2 border-gold/50 pl-4">
            질병·치료·진단과 무관한 연구·교육 자료입니다. 술·담금주가 몸에 좋다는 뜻이 아닙니다.
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
