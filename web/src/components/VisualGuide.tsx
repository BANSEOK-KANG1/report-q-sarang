import { ArticleImage } from "@/components/ArticleImage";
import { visuals } from "@/lib/visuals";

const cards = [
  {
    key: "militaris" as const,
    title: "제왕충초란",
    body: "학명 Cordyceps militaris. 동충하초와 다른 종이며, 이름을 정확히 쓰는 것이 출발점입니다.",
  },
  {
    key: "cordycepin" as const,
    title: "코디세핀",
    body: "연구에서 자주 언급되는 성분 이름입니다. 논문은 ‘연구 주제’로만 다루고, 효능으로 바꿔 쓰지 않습니다.",
  },
  {
    key: "damgeumju" as const,
    title: "담금의 장면",
    body: "큐사랑 제왕충초 담금주는 자리와 취향의 이야기입니다. 약처럼 말하지 않는 편집 원칙을 따릅니다.",
  },
];

export function VisualGuide() {
  return (
    <section className="border-b border-line/70 bg-paper-deep/30">
      <div className="mx-auto max-w-6xl px-5 py-16 md:py-20">
        <div className="max-w-2xl mb-12">
          <p className="text-xs tracking-[0.18em] text-accent uppercase mb-3">Visual Guide</p>
          <h2 className="font-display text-3xl md:text-4xl text-gold leading-tight">
            제왕충초를 보는 세 가지 시선
          </h2>
          <p className="mt-4 text-ink-soft leading-relaxed">
            균류의 형태, 성분의 이름, 담금의 장면 — 각각 다른 질문에 답합니다.
            과장 없이 이름을 선명하게 남기기 위한 시각 자료입니다.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-3">
          {cards.map(({ key, title, body }) => {
            const v = visuals[key];
            return (
              <article
                key={key}
                className="rounded-lg border border-line/70 bg-paper/40 p-4 md:p-5"
              >
                <ArticleImage src={v.src} alt={v.alt} aspect="square" />
                <h3 className="font-display text-xl text-ink mt-5 mb-2">{title}</h3>
                <p className="text-sm text-ink-soft leading-relaxed">{body}</p>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
