import type { EasyReadSummary } from "@/lib/insights";

type Props = {
  easyRead: EasyReadSummary;
  titleKo?: string;
};

export function ResearchEasyRead({ easyRead, titleKo }: Props) {
  return (
    <section className="mb-12 rounded-xl border-2 border-gold/30 bg-paper-deep/25 overflow-hidden">
      <div className="px-5 py-4 md:px-8 md:py-5 border-b border-gold/20 bg-paper-deep/40">
        <p className="text-xs tracking-[0.18em] text-accent uppercase mb-1">쉬운 정리</p>
        <h2 className="font-display text-2xl md:text-3xl text-gold leading-snug">
          할머니도 읽는 논문 요약
        </h2>
        {titleKo ? (
          <p className="mt-2 text-base md:text-lg text-ink leading-relaxed">{titleKo}</p>
        ) : null}
      </div>

      <div className="px-5 py-6 md:px-8 md:py-8 space-y-8">
        <div>
          <p className="text-lg md:text-xl leading-relaxed text-ink font-medium">
            {easyRead.headline}
          </p>
        </div>

        <div className="space-y-6">
          <Block title="이 글은 무엇인가요?" text={easyRead.whatIsThis} />
          <Block title="연구팀이 한 일" text={easyRead.whatTheyDid} />
          <Block title="알게 된 것" text={easyRead.whatTheyFound} />
        </div>

        {easyRead.sections.length > 0 ? (
          <div className="space-y-4 pt-2">
            <p className="text-sm font-medium text-gold">조금 더 나눠 보면</p>
            {easyRead.sections.map((s) => (
              <div
                key={s.id}
                className="rounded-lg border border-line/60 bg-paper/50 px-4 py-3"
              >
                <p className="text-sm font-medium text-ink mb-1">{s.label}</p>
                <p className="text-[15px] leading-relaxed text-ink-soft">{s.text}</p>
              </div>
            ))}
          </div>
        ) : null}

        <div className="rounded-lg border border-accent/40 bg-paper-deep/30 px-4 py-4">
          <p className="text-sm font-medium text-gold mb-3">꼭 알아두실 점</p>
          <ul className="space-y-2 text-[15px] leading-relaxed text-ink-soft list-disc pl-5">
            {easyRead.goodToKnow.map((line) => (
              <li key={line}>
                <PlainBold text={line} />
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

function Block({ title, text }: { title: string; text: string }) {
  return (
    <div>
      <p className="text-sm font-medium text-gold mb-2">{title}</p>
      <p className="text-[15px] md:text-base leading-relaxed text-ink">{text}</p>
    </div>
  );
}

function PlainBold({ text }: { text: string }) {
  const parts = text.split(/\*\*(.*?)\*\*/g);
  return (
    <>
      {parts.map((part, i) =>
        i % 2 === 1 ? (
          <strong key={i} className="text-ink font-medium">
            {part}
          </strong>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
}
