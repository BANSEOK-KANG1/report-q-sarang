import { ArticleImage } from "@/components/ArticleImage";
import { siteConfig } from "@/lib/site-config";
import { visuals } from "@/lib/visuals";

export const metadata = { title: "소개" };

export default function AboutPage() {
  const militaris = visuals.militaris;
  const damgeumju = visuals.damgeumju;

  return (
    <div className="mx-auto max-w-4xl px-5 py-14">
      <h1 className="font-display text-4xl md:text-5xl text-gold mb-8">소개</h1>

      <div className="grid gap-10 md:grid-cols-2 items-start mb-12">
        <div className="space-y-5 text-ink-soft leading-relaxed">
          <p>
            <strong className="text-ink">{siteConfig.name}</strong>은{" "}
            <a href={siteConfig.parentUrl} className="text-gold underline">
              {siteConfig.parentLabel}
            </a>
            네트워크의 브랜드 콘텐츠 사이트입니다.
          </p>
          <p>
            제왕충초 담금주와 코디세핀·<em>Cordyceps militaris</em> 이야기를
            과장 없이 정리합니다. 건강·질병 효능을 단정하지 않습니다.
          </p>
          <p>운영: {siteConfig.author}</p>
        </div>
        <ArticleImage
          src={militaris.src}
          alt={militaris.alt}
          caption={militaris.caption}
          aspect="square"
        />
      </div>

      <section className="border-t border-line/70 pt-10">
        <h2 className="font-display text-2xl text-gold mb-4">시각 자료에 대해</h2>
        <p className="text-ink-soft leading-relaxed mb-8">
          사이트의 이미지는 균류의 형태, 성분 이름, 담금의 장면을 구분해 보여 줍니다.
          연구·효능을 암시하는 광고 이미지가 아니라, 이름을 선명하게 남기기 위한 편집 자료입니다.
        </p>
        <ArticleImage
          src={damgeumju.src}
          alt={damgeumju.alt}
          caption={damgeumju.caption}
          aspect="video"
        />
      </section>
    </div>
  );
}
