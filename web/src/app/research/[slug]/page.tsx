import Link from "next/link";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getInsight, getInsightSlugs, studyTypeLabel } from "@/lib/insights";
import { liquorNotice, siteConfig } from "@/lib/site-config";

type Props = { params: Promise<{ slug: string }> };

export async function generateStaticParams() {
  return getInsightSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  const item = getInsight(slug);
  if (!item) return {};
  return {
    title: item.titleKo.slice(0, 80),
    description: item.description,
  };
}

export default async function ResearchDetailPage({ params }: Props) {
  const { slug } = await params;
  const item = getInsight(slug);
  if (!item) notFound();

  const sourceUrl =
    item.url || (item.doi ? `https://doi.org/${item.doi}` : "") ||
    (item.pmid ? `https://pubmed.ncbi.nlm.nih.gov/${item.pmid}/` : "");

  return (
    <article>
      <div className="border-b border-line/70 bg-paper-deep/20">
        <div className="mx-auto max-w-4xl px-5 pt-12 pb-10">
          <p className="text-xs text-accent mb-4 tracking-wide uppercase">
            Research · {studyTypeLabel(item.studyType)}
            {item.year ? ` · ${item.year}` : ""}
          </p>
          <h1 className="font-display text-2xl md:text-4xl leading-tight text-ink max-w-3xl">
            {item.titleKo}
          </h1>
          <p className="mt-4 text-sm text-ink-soft leading-relaxed">{item.description}</p>
          <div className="mt-6 flex flex-wrap gap-2 text-[11px]">
            {item.evidenceStrength ? (
              <span className="px-2 py-1 rounded border border-line/80 text-ink-soft">
                {item.evidenceStrength.replace(/_/g, " ")}
              </span>
            ) : null}
            {item.compound && item.compound !== "unclear" ? (
              <span className="px-2 py-1 rounded border border-line/80 text-ink-soft">
                {item.compound}
              </span>
            ) : null}
            {item.species && item.species !== "unclear" ? (
              <span className="px-2 py-1 rounded border border-line/80 text-ink-soft">
                {item.species.replace(/_/g, " ")}
              </span>
            ) : null}
          </div>
          {sourceUrl ? (
            <a
              href={sourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block mt-6 text-sm text-gold hover:underline"
            >
              원문 보기 (DOI/PubMed) ↗
            </a>
          ) : null}
        </div>
      </div>

      <div className="mx-auto max-w-3xl px-5 py-12">
        <div className="prose-qs">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{item.body}</ReactMarkdown>
        </div>
        <div className="mt-14 border-t border-line pt-6 space-y-4 text-sm text-ink-soft">
          <p className="text-[13px] leading-relaxed border border-line/70 bg-paper-deep/50 p-4 rounded-lg">
            {liquorNotice}
          </p>
          <p className="text-[13px] leading-relaxed border border-accent/30 bg-paper-deep/30 p-4 rounded-lg">
            본 페이지는 학술 문헌 요약·번역 정리 자료입니다. 제품 효능·효과를 의미하지 않으며,
            연구·교육 목적으로만 사용하세요.
          </p>
          <p>
            편집: {siteConfig.author} ·{" "}
            <Link href="/editorial" className="underline hover:text-gold">
              편집 원칙
            </Link>
          </p>
          <p>
            <Link href="/research" className="text-gold hover:underline">
              ← 연구 인사이트 목록
            </Link>
          </p>
        </div>
      </div>
    </article>
  );
}
