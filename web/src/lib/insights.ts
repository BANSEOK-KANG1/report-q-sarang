import fs from "fs";
import path from "path";
import matter from "gray-matter";

export type PaperFigure = {
  type: string;
  src: string;
  caption: string;
  source: string;
};

export type PaperConcept = {
  name: string;
  score: number;
  level?: number;
};

export type PaperApiMeta = {
  keywords: string[];
  meshTerms: string[];
  concepts: PaperConcept[];
  citedByCount: number | null;
  referenceCount: number | null;
  publisher: string;
  journal: string;
  oaStatus: string;
  oaUrl: string;
  apis: Record<string, boolean>;
  fetchedAt: string;
};

export type TranslationSection = {
  id: string;
  labelKo: string;
  en: string;
  koLiteral: string;
  koResearcher: string;
  koPlain: string;
};

export type GlossaryEntry = {
  en: string;
  ko: string;
  note: string;
};

export type EasyReadSection = {
  id: string;
  label: string;
  text: string;
};

export type EasyReadSummary = {
  headline: string;
  whatIsThis: string;
  whatTheyDid: string;
  whatTheyFound: string;
  goodToKnow: string[];
  sections: EasyReadSection[];
};

export type TranslationViews = {
  titleKo: string;
  glossary: GlossaryEntry[];
  sections: TranslationSection[];
  easyRead: EasyReadSummary | null;
  full: {
    en: string;
    koLiteral: string;
    koResearcher: string;
    koPlain: string;
  } | null;
};

export type ResearchInsight = {
  slug: string;
  title: string;
  titleKo: string;
  description: string;
  date: string;
  year: number | null;
  studyType: string;
  evidenceStrength: string;
  species: string;
  compound: string;
  doi: string;
  pmid: string;
  pmcid: string;
  url: string;
  riskFlags: string[];
  visuals: PaperFigure[];
  apiMeta: PaperApiMeta | null;
  translations: TranslationViews | null;
  body: string;
};

function contentDir(): string {
  const candidates = [
    path.join(process.cwd(), "content", "research"),
    path.join(process.cwd(), "..", "content", "research"),
    path.join(process.cwd(), "web", "content", "research"),
  ];
  for (const dir of candidates) {
    if (fs.existsSync(dir)) return dir;
  }
  return candidates[0];
}

function isInsightFile(name: string): boolean {
  return name.endsWith(".md") && !["README.md"].includes(name);
}

const STUDY_TYPE_LABEL: Record<string, string> = {
  rct: "RCT",
  systematic_review: "체계적 고찰",
  meta_analysis: "메타분석",
  review_narrative: "리뷰",
  animal: "전임상",
  in_vitro: "in vitro",
  observational_human: "관찰연구",
};

export function studyTypeLabel(studyType: string): string {
  return STUDY_TYPE_LABEL[studyType] || studyType || "연구";
}

function parseEasyRead(raw: Record<string, unknown> | undefined): EasyReadSummary | null {
  if (!raw) return null;
  const sections = Array.isArray(raw.sections)
    ? raw.sections.map((s) => {
        const item = s as Record<string, unknown>;
        return {
          id: String(item.id || ""),
          label: String(item.label || ""),
          text: String(item.text || ""),
        };
      })
    : [];
  const goodToKnow = Array.isArray(raw.good_to_know)
    ? raw.good_to_know.map(String)
    : [];
  if (!raw.headline && !raw.what_is_this) return null;
  return {
    headline: String(raw.headline || ""),
    whatIsThis: String(raw.what_is_this || ""),
    whatTheyDid: String(raw.what_they_did || ""),
    whatTheyFound: String(raw.what_they_found || ""),
    goodToKnow,
    sections,
  };
}

function parseTranslations(data: Record<string, unknown>): TranslationViews | null {
  const raw = data.translations as Record<string, unknown> | undefined;
  if (!raw) return null;
  const sections = Array.isArray(raw.sections)
    ? raw.sections.map((s) => {
        const item = s as Record<string, unknown>;
        return {
          id: String(item.id || ""),
          labelKo: String(item.label_ko || ""),
          en: String(item.en || ""),
          koLiteral: String(item.ko_literal || ""),
          koResearcher: String(item.ko_researcher || ""),
          koPlain: String(item.ko_plain || ""),
        };
      })
    : [];
  const glossary = Array.isArray(raw.glossary)
    ? raw.glossary.map((g) => {
        const item = g as Record<string, unknown>;
        return {
          en: String(item.en || ""),
          ko: String(item.ko || ""),
          note: String(item.note || ""),
        };
      })
    : [];
  const fullRaw = raw.full as Record<string, unknown> | undefined;
  const full = fullRaw
    ? {
        en: String(fullRaw.en || ""),
        koLiteral: String(fullRaw.ko_literal || ""),
        koResearcher: String(fullRaw.ko_researcher || ""),
        koPlain: String(fullRaw.ko_plain || ""),
      }
    : null;
  return {
    titleKo: String(raw.title_ko || data.title_ko || ""),
    glossary,
    sections,
    easyRead: parseEasyRead(raw.easy_read as Record<string, unknown> | undefined),
    full,
  };
}

function parseApiMeta(data: Record<string, unknown>): PaperApiMeta | null {
  const raw = data.api_meta as Record<string, unknown> | undefined;
  if (!raw) return null;
  const concepts = Array.isArray(raw.concepts)
    ? raw.concepts.map((c) => {
        const item = c as Record<string, unknown>;
        return {
          name: String(item.name || ""),
          score: Number(item.score || 0),
          level: item.level != null ? Number(item.level) : undefined,
        };
      })
    : [];
  return {
    keywords: Array.isArray(raw.keywords) ? raw.keywords.map(String) : [],
    meshTerms: Array.isArray(raw.mesh_terms) ? raw.mesh_terms.map(String) : [],
    concepts,
    citedByCount: raw.cited_by_count != null ? Number(raw.cited_by_count) : null,
    referenceCount: raw.reference_count != null ? Number(raw.reference_count) : null,
    publisher: String(raw.publisher || ""),
    journal: String(raw.journal || ""),
    oaStatus: String(raw.oa_status || ""),
    oaUrl: String(raw.oa_url || ""),
    apis: (raw.apis as Record<string, boolean>) || {},
    fetchedAt: String(raw.fetched_at || ""),
  };
}

function parseVisuals(data: Record<string, unknown>): PaperFigure[] {
  if (!Array.isArray(data.visuals)) return [];
  return data.visuals.map((v) => {
    const item = v as Record<string, unknown>;
    return {
      type: String(item.type || "figure"),
      src: String(item.src || ""),
      caption: String(item.caption || ""),
      source: String(item.source || ""),
    };
  });
}

export function getAllInsights(): ResearchInsight[] {
  const dir = contentDir();
  if (!fs.existsSync(dir)) return [];
  const files = fs.readdirSync(dir).filter(isInsightFile);
  const items = files.map((file) => {
    const raw = fs.readFileSync(path.join(dir, file), "utf8");
    const { data, content } = matter(raw);
    let body = content.trim();
    const lines = body.split("\n");
    if (lines[0]?.startsWith("# ")) {
      body = lines.slice(1).join("\n").trim();
    }
    return {
      slug: String(data.slug || file.replace(/\.md$/, "")),
      title: String(data.title || file),
      titleKo: String(data.title_ko || data.title || file),
      description: String(data.description || "").replace(/\*\*/g, ""),
      date: String(data.date || ""),
      year: data.year != null ? Number(data.year) : null,
      studyType: String(data.study_type || ""),
      evidenceStrength: String(data.evidence_strength || ""),
      species: String(data.species || ""),
      compound: String(data.compound || ""),
      doi: String(data.doi || ""),
      pmid: String(data.pmid || ""),
      pmcid: String(data.pmcid || ""),
      url: String(data.url || ""),
      riskFlags: Array.isArray(data.risk_flags) ? data.risk_flags.map(String) : [],
      visuals: parseVisuals(data as Record<string, unknown>),
      apiMeta: parseApiMeta(data as Record<string, unknown>),
      translations: parseTranslations(data as Record<string, unknown>),
      body,
    } satisfies ResearchInsight;
  });
  return items.sort((a, b) => {
    const ya = a.year ?? 0;
    const yb = b.year ?? 0;
    if (ya !== yb) return yb - ya;
    return a.title.localeCompare(b.title, "ko");
  });
}

export function getInsight(slug: string): ResearchInsight | null {
  return getAllInsights().find((i) => i.slug === slug) ?? null;
}

export function getInsightSlugs(): string[] {
  return getAllInsights().map((i) => i.slug);
}

export function coverForInsight(insight: ResearchInsight): PaperFigure | null {
  return insight.visuals[0] ?? null;
}
