/** Visual assets and per-post cover mapping */

export type VisualKey =
  | "hero"
  | "damgeumju"
  | "militaris"
  | "cordycepin"
  | "research"
  | "regulatory";

export const visuals: Record<
  VisualKey,
  { src: string; alt: string; caption: string }
> = {
  hero: {
    src: "/images/hero-cordyceps.png",
    alt: "Cordyceps militaris 자실체 클로즈업",
    caption: "제왕충초(Cordyceps militaris) — 브랜드 시각 자료",
  },
  damgeumju: {
    src: "/images/damgeumju-still-life.png",
    alt: "담금주와 제왕충초 원료가 함께 놓인 정물",
    caption: "담금의 장면 — 효능 표현이 아닌, 자리와 취향의 이야기",
  },
  militaris: {
    src: "/images/militaris-botanical.png",
    alt: "Cordyceps militaris 식물 도해 스타일",
    caption: "학명과 종을 구분할 때 참고하는 시각",
  },
  cordycepin: {
    src: "/images/cordycepin-abstract.png",
    alt: "코디세핀 성분을 연상하는 추상 이미지",
    caption: "성분 이름을 소개할 때 쓰는 비문학적 비주얼",
  },
  research: {
    src: "/images/militaris-botanical.png",
    alt: "연구·문헌 맥락 이미지",
    caption: "논문은 ‘연구 주제’로만 다룹니다",
  },
  regulatory: {
    src: "/images/cordycepin-abstract.png",
    alt: "규제·맥락 안내 이미지",
    caption: "오해 없이 읽기 위한 안내",
  },
};

export const postCovers: Record<string, VisualKey> = {
  "what-is-cordycepin": "cordycepin",
  "cordyceps-militaris-basics": "militaris",
  "how-to-read-cordycepin-research": "research",
  "fda-mfds-context": "regulatory",
  "qsarang-jewang-damgeumju": "damgeumju",
};

export function coverForSlug(slug: string): (typeof visuals)[VisualKey] {
  const key = postCovers[slug] ?? "hero";
  return visuals[key];
}
