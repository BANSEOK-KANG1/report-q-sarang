/** Q-Sarang site — same measuremkt subdomain pattern as sports/football. */
export const siteConfig = {
  name: process.env.SITE_NAME ?? "큐사랑 · 제왕충초",
  brandShort: process.env.SITE_BRAND_SHORT ?? "큐사랑",
  brandSection: process.env.SITE_BRAND_SECTION ?? "제왕충초",
  tagline: process.env.SITE_TAGLINE ?? "이름을 담되, 약처럼 말하지 않기",
  description:
    process.env.SITE_DESCRIPTION ??
    "큐사랑 제왕충초 담금주 — 코디세핀과 Cordyceps militaris를 객관적으로 소개하는 브랜드 콘텐츠.",
  url: process.env.SITE_URL ?? "https://q-sarang.measuremkt.com",
  parentUrl: process.env.SITE_PARENT_URL ?? "https://measuremkt.com",
  parentLabel: process.env.SITE_PARENT_LABEL ?? "측정하는 마케터",
  author: process.env.SITE_AUTHOR ?? "강반석",
  contactEmail: process.env.SITE_CONTACT_EMAIL ?? "kangbs2486@gmail.com",
};

export const navItems = [
  { href: "/", label: "홈" },
  { href: "/research", label: "연구 인사이트" },
  { href: "/blog", label: "이야기" },
  { href: "/about", label: "소개" },
] as const;

export const footerLegal = [
  { href: "/about", label: "소개" },
  { href: "/editorial", label: "편집 원칙" },
  { href: "/privacy", label: "개인정보" },
  { href: "/contact", label: "문의" },
] as const;

export const liquorNotice =
  "본 사이트는 주류 브랜드 콘텐츠입니다. 질병의 예방·치료·진단과 무관하며, 음주가 건강에 도움이 된다는 의미가 아닙니다. 미성년자 음주 금지.";
