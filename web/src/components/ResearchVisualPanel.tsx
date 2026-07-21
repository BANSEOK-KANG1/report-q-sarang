import { ArticleImage } from "@/components/ArticleImage";
import type { PaperApiMeta, PaperFigure } from "@/lib/insights";

type Props = {
  visuals: PaperFigure[];
  apiMeta: PaperApiMeta | null;
};

function Stat({ label, value }: { label: string; value: string | number | null }) {
  if (value == null || value === "") return null;
  return (
    <div className="rounded-lg border border-line/70 bg-paper-deep/40 px-4 py-3">
      <p className="text-[10px] uppercase tracking-wider text-ink-soft mb-1">{label}</p>
      <p className="font-display text-xl text-gold">{value}</p>
    </div>
  );
}

export function ResearchVisualPanel({ visuals, apiMeta }: Props) {
  const concepts = (apiMeta?.concepts || []).slice(0, 6);
  const keywords = (apiMeta?.keywords || []).slice(0, 8);
  const apis = apiMeta?.apis || {};

  return (
    <section className="mb-12 space-y-10">
      <div>
        <p className="text-xs tracking-[0.16em] text-accent uppercase mb-2">Visual · API</p>
        <h2 className="font-display text-2xl text-gold">시각 자료 · 학술 메타데이터</h2>
        <p className="mt-2 text-sm text-ink-soft">
          Europe PMC · OpenAlex · Crossref API에서 수집한 원문 Figure 및 연구 맥락 정보
        </p>
      </div>

      {visuals.length > 0 ? (
        <div className="grid gap-8 md:grid-cols-2">
          {visuals.map((fig) => (
            <ArticleImage
              key={fig.src}
              src={fig.src}
              alt={fig.caption}
              caption={fig.caption}
              aspect="video"
            />
          ))}
        </div>
      ) : (
        <p className="text-sm text-ink-soft border border-line/60 rounded-lg p-4 bg-paper-deep/30">
          OA 전문 Figure를 API로 가져올 수 없는 논문입니다. 아래 개념·키워드·인용 메타데이터를
          참고하세요.
        </p>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Stat label="인용 수 (OpenAlex)" value={apiMeta?.citedByCount ?? null} />
        <Stat label="참고문헌 수" value={apiMeta?.referenceCount ?? null} />
        <Stat label="OA 상태" value={apiMeta?.oaStatus || null} />
        <Stat label="출판사" value={apiMeta?.publisher ? apiMeta.publisher.slice(0, 20) : null} />
      </div>

      {concepts.length > 0 ? (
        <div>
          <h3 className="text-sm font-medium text-ink mb-3">연구 개념 (OpenAlex)</h3>
          <div className="flex flex-wrap gap-2">
            {concepts.map((c) => (
              <span
                key={c.name}
                className="text-xs px-3 py-1.5 rounded-full border border-gold/30 text-ink-soft"
                title={`관련도 ${(c.score * 100).toFixed(0)}%`}
              >
                {c.name}
                <span className="text-gold ml-1">{(c.score * 100).toFixed(0)}%</span>
              </span>
            ))}
          </div>
        </div>
      ) : null}

      {keywords.length > 0 ? (
        <div>
          <h3 className="text-sm font-medium text-ink mb-3">키워드 (Europe PMC)</h3>
          <div className="flex flex-wrap gap-2">
            {keywords.map((kw) => (
              <span
                key={kw}
                className="text-xs px-2.5 py-1 rounded border border-line/70 text-ink-soft"
              >
                {kw}
              </span>
            ))}
          </div>
        </div>
      ) : null}

      <div className="flex flex-wrap gap-2 text-[10px] uppercase tracking-wide text-ink-soft">
        {apis.europepmc ? (
          <span className="px-2 py-1 border border-line/60 rounded">Europe PMC</span>
        ) : null}
        {apis.openalex ? (
          <span className="px-2 py-1 border border-line/60 rounded">OpenAlex</span>
        ) : null}
        {apis.crossref ? (
          <span className="px-2 py-1 border border-line/60 rounded">Crossref</span>
        ) : null}
        {apiMeta?.fetchedAt ? (
          <span className="px-2 py-1 text-accent">갱신 {apiMeta.fetchedAt}</span>
        ) : null}
      </div>
    </section>
  );
}
