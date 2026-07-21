"use client";

import { useState } from "react";
import type { TranslationSection, TranslationViews } from "@/lib/insights";

type Tab = "compare" | "researcher" | "plain" | "glossary";

const TABS: { id: Tab; label: string; desc: string }[] = [
  { id: "compare", label: "원문 대조", desc: "영문 · 직역 한국어 나란히" },
  { id: "researcher", label: "연구자 뷰", desc: "용어·맥락 중심 해석" },
  { id: "plain", label: "쉬운 설명", desc: "비전문 독자용 요약" },
  { id: "glossary", label: "용어집", desc: "핵심 EN↔KO 정리" },
];

type Props = {
  translations: TranslationViews;
};

function SectionBlock({
  label,
  en,
  ko,
}: {
  label: string;
  en: string;
  ko: string;
}) {
  return (
    <div className="border border-line/70 rounded-lg overflow-hidden mb-6">
      <div className="px-4 py-2 bg-paper-deep/60 border-b border-line/60 text-sm font-medium text-gold">
        {label}
      </div>
      <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-line/60">
        <div className="p-4">
          <p className="text-[10px] uppercase tracking-wider text-ink-soft mb-2">English</p>
          <p className="text-sm leading-relaxed text-ink-soft">{en}</p>
        </div>
        <div className="p-4 bg-paper-deep/20">
          <p className="text-[10px] uppercase tracking-wider text-accent mb-2">한국어</p>
          <p className="text-sm leading-relaxed text-ink">{ko}</p>
        </div>
      </div>
    </div>
  );
}

export function ResearchTranslationTabs({ translations }: Props) {
  const [tab, setTab] = useState<Tab>("compare");
  const sections = translations.sections || [];
  const glossary = translations.glossary || [];

  return (
    <section className="mb-12">
      <div className="mb-6">
        <p className="text-xs tracking-[0.16em] text-accent uppercase mb-2">Translation</p>
        <h2 className="font-display text-2xl text-gold">다각도 번역 보기</h2>
        {translations.titleKo ? (
          <p className="mt-2 text-sm text-ink-soft">
            제목(한): <span className="text-ink">{translations.titleKo}</span>
          </p>
        ) : null}
        <p className="mt-2 text-xs text-ink-soft">
          자동 번역·편집 정리입니다. 인용·법무 판단은 반드시 원문을 확인하세요.
        </p>
      </div>

      <div className="flex flex-wrap gap-2 mb-8">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`px-3 py-2 rounded-lg text-xs border transition-colors ${
              tab === t.id
                ? "border-gold text-gold bg-paper-deep/50"
                : "border-line/70 text-ink-soft hover:border-gold/50"
            }`}
          >
            <span className="font-medium">{t.label}</span>
            <span className="hidden sm:inline text-ink-soft ml-1">· {t.desc}</span>
          </button>
        ))}
      </div>

      {tab === "compare" &&
        sections.map((s: TranslationSection) => (
          <SectionBlock
            key={s.id}
            label={s.labelKo}
            en={s.en}
            ko={s.koLiteral}
          />
        ))}

      {tab === "researcher" &&
        sections.map((s: TranslationSection) => (
          <div key={s.id} className="mb-6 border border-line/70 rounded-lg p-4">
            <p className="text-sm font-medium text-gold mb-2">{s.labelKo}</p>
            <p className="text-sm leading-relaxed text-ink">{s.koResearcher}</p>
          </div>
        ))}

      {tab === "plain" &&
        sections.map((s: TranslationSection) => (
          <div key={s.id} className="mb-6 border border-line/70 rounded-lg p-4 bg-paper-deep/20">
            <p className="text-sm font-medium text-gold mb-2">{s.labelKo}</p>
            <p className="text-sm leading-relaxed text-ink">{s.koPlain}</p>
          </div>
        ))}

      {tab === "glossary" && (
        <div className="border border-line/70 rounded-lg overflow-hidden">
          {glossary.length === 0 ? (
            <p className="p-4 text-sm text-ink-soft">추출된 핵심 용어가 없습니다.</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-line/70 bg-paper-deep/40 text-left">
                  <th className="p-3 font-medium text-ink-soft">English</th>
                  <th className="p-3 font-medium text-ink-soft">한국어</th>
                  <th className="p-3 font-medium text-ink-soft hidden md:table-cell">설명</th>
                </tr>
              </thead>
              <tbody>
                {glossary.map((g) => (
                  <tr key={g.en} className="border-b border-line/50 last:border-0">
                    <td className="p-3 text-ink-soft">{g.en}</td>
                    <td className="p-3 text-gold font-medium">{g.ko}</td>
                    <td className="p-3 text-ink-soft hidden md:table-cell">{g.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </section>
  );
}
