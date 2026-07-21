"use client";

import { useState } from "react";
import type { TranslationSection, TranslationViews } from "@/lib/insights";

type Tab = "plain" | "compare" | "researcher" | "glossary";

const TABS: { id: Tab; label: string }[] = [
  { id: "plain", label: "쉬운 설명" },
  { id: "compare", label: "원문 대조" },
  { id: "researcher", label: "연구자용" },
  { id: "glossary", label: "용어집" },
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
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState<Tab>("plain");
  const sections = translations.sections || [];
  const glossary = translations.glossary || [];

  return (
    <section className="mb-12">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between gap-4 px-4 py-3 rounded-lg border border-line/70 bg-paper-deep/30 hover:border-gold/40 transition-colors text-left"
      >
        <div>
          <p className="text-xs text-ink-soft uppercase tracking-wide">참고</p>
          <p className="text-sm font-medium text-ink">원문 · 번역 · 용어집 펼치기</p>
        </div>
        <span className="text-gold text-lg shrink-0">{open ? "−" : "+"}</span>
      </button>

      {open ? (
        <div className="mt-6 pt-2">
          <p className="text-xs text-ink-soft mb-4">
            위 「쉬운 정리」가 메인입니다. 아래는 원문과 대조·번역 참고용입니다.
          </p>

          <div className="flex flex-wrap gap-2 mb-6">
            {TABS.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setTab(t.id)}
                className={`px-3 py-1.5 rounded-lg text-xs border transition-colors ${
                  tab === t.id
                    ? "border-gold text-gold bg-paper-deep/50"
                    : "border-line/70 text-ink-soft hover:border-gold/50"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {tab === "plain" &&
            sections.map((s: TranslationSection) => (
              <div key={s.id} className="mb-4 border border-line/70 rounded-lg p-4">
                <p className="text-sm font-medium text-gold mb-2">{s.labelKo}</p>
                <p className="text-sm leading-relaxed text-ink">{s.koPlain}</p>
              </div>
            ))}

          {tab === "compare" &&
            sections.map((s: TranslationSection) => (
              <SectionBlock key={s.id} label={s.labelKo} en={s.en} ko={s.koLiteral} />
            ))}

          {tab === "researcher" &&
            sections.map((s: TranslationSection) => (
              <div key={s.id} className="mb-4 border border-line/70 rounded-lg p-4">
                <p className="text-sm font-medium text-gold mb-2">{s.labelKo}</p>
                <p className="text-sm leading-relaxed text-ink">{s.koResearcher}</p>
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
        </div>
      ) : null}
    </section>
  );
}
