import Link from "next/link";
import type { ResearchInsight } from "@/lib/insights";
import { studyTypeLabel } from "@/lib/insights";

type Props = {
  insight: ResearchInsight;
  featured?: boolean;
};

function Badges({ insight }: { insight: ResearchInsight }) {
  return (
    <div className="flex flex-wrap gap-2 mt-3">
      {insight.year ? (
        <span className="text-[10px] tracking-wide uppercase px-2 py-0.5 rounded border border-line/80 text-ink-soft">
          {insight.year}
        </span>
      ) : null}
      {insight.studyType ? (
        <span className="text-[10px] tracking-wide uppercase px-2 py-0.5 rounded border border-gold/40 text-gold">
          {studyTypeLabel(insight.studyType)}
        </span>
      ) : null}
      {insight.evidenceStrength ? (
        <span className="text-[10px] tracking-wide uppercase px-2 py-0.5 rounded border border-line/80 text-ink-soft">
          {insight.evidenceStrength.replace(/_/g, " ")}
        </span>
      ) : null}
    </div>
  );
}

export function ResearchCard({ insight, featured = false }: Props) {
  if (featured) {
    return (
      <article className="border-b border-line/70 pb-10">
        <p className="text-xs tracking-[0.14em] text-accent mb-3 uppercase">Featured · Research</p>
        <Link href={`/research/${insight.slug}`}>
          <h3 className="font-display text-2xl md:text-3xl leading-snug hover:text-gold transition-colors">
            {insight.titleKo}
          </h3>
        </Link>
        <Badges insight={insight} />
        <p className="mt-4 text-ink-soft leading-relaxed line-clamp-4">{insight.description}</p>
        <Link
          href={`/research/${insight.slug}`}
          className="inline-block mt-5 text-sm font-medium text-gold hover:underline"
        >
          전문 요약 읽기 →
        </Link>
      </article>
    );
  }

  return (
    <article className="border-b border-line/70 pb-8">
      <Link href={`/research/${insight.slug}`}>
        <h3 className="font-display text-lg md:text-xl leading-snug hover:text-gold transition-colors">
          {insight.titleKo}
        </h3>
      </Link>
      <Badges insight={insight} />
      <p className="mt-2 text-sm text-ink-soft leading-relaxed line-clamp-2">{insight.description}</p>
      <Link
        href={`/research/${insight.slug}`}
        className="inline-block mt-3 text-sm text-gold hover:underline"
      >
        요약 보기 →
      </Link>
    </article>
  );
}
