export const metadata = { title: "편집 원칙" };

export default function EditorialPage() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-14">
      <h1 className="font-display text-4xl text-gold mb-8">편집 원칙</h1>
      <ul className="space-y-3 text-ink-soft leading-relaxed list-disc pl-5">
        <li>성분·균류 이름은 정확히, 효능은 단정하지 않습니다.</li>
        <li>질병·치료·예방 언어를 제품 소개에 쓰지 않습니다.</li>
        <li>학술 문헌은 “연구 주제로서 존재” 수준으로만 참조합니다.</li>
        <li>주류 콘텐츠로서 음주를 건강 행위처럼 설명하지 않습니다.</li>
        <li>발행 전 컴플라이언스 체크리스트를 확인합니다.</li>
      </ul>
    </div>
  );
}
