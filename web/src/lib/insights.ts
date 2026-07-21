import fs from "fs";
import path from "path";
import matter from "gray-matter";

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
  url: string;
  riskFlags: string[];
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
      url: String(data.url || ""),
      riskFlags: Array.isArray(data.risk_flags) ? data.risk_flags.map(String) : [],
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
