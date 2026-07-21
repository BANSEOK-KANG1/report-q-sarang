export const metadata = { title: "개인정보처리방침" };

export default function PrivacyPage() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-14">
      <h1 className="font-display text-4xl text-gold mb-8">개인정보처리방침</h1>
      <div className="space-y-4 text-ink-soft leading-relaxed text-sm">
        <p>본 사이트는 서비스 제공에 필요한 범위에서만 최소한의 정보를 처리합니다.</p>
        <p>문의 이메일로 연락 시, 응대 목적 외로 개인정보를 이용하지 않습니다.</p>
        <p>자세한 사항은 메인 사이트 정책을 참고할 수 있습니다.</p>
      </div>
    </div>
  );
}
