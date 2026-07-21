import Image from "next/image";
import Link from "next/link";
import { siteConfig } from "@/lib/site-config";
import { visuals } from "@/lib/visuals";

export function HeroSection() {
  const hero = visuals.hero;

  return (
    <section className="relative overflow-hidden border-b border-line">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(196,120,58,0.2),_transparent_55%)]" />
      <div className="relative mx-auto max-w-6xl px-5 py-14 md:py-20">
        <div className="grid gap-10 lg:grid-cols-[1fr_1.05fr] lg:gap-14 items-center">
          <div>
            <p className="rise-in text-xs md:text-sm tracking-[0.2em] text-gold uppercase mb-4">
              {siteConfig.brandShort}
            </p>
            <h1 className="rise-in rise-in-delay-1 font-display text-4xl md:text-6xl lg:text-7xl leading-[1.08] text-ink">
              {siteConfig.brandSection}
            </h1>
            <p className="rise-in rise-in-delay-2 mt-5 text-base md:text-lg text-ink-soft max-w-xl leading-[1.85]">
              {siteConfig.tagline}
            </p>
            <div className="rise-in rise-in-delay-2 mt-8 flex flex-wrap gap-3">
              <Link
                href="/blog"
                className="bg-accent text-paper font-medium text-sm px-6 py-3 hover:bg-gold hover:text-paper-deep transition-colors"
              >
                이야기 읽기
              </Link>
              <a
                href={siteConfig.parentUrl}
                className="border border-line text-sm px-6 py-3 text-ink-soft hover:border-gold hover:text-gold transition-colors"
              >
                {siteConfig.parentLabel}
              </a>
            </div>
          </div>

          <div className="rise-in rise-in-delay-2 relative">
            <div className="relative aspect-[4/3] overflow-hidden rounded-xl border border-line/80 shadow-[0_24px_80px_rgba(0,0,0,0.45)]">
              <Image
                src={hero.src}
                alt={hero.alt}
                fill
                priority
                sizes="(max-width: 1024px) 100vw, 50vw"
                className="object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-paper-deep/80 via-paper-deep/10 to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 p-5 md:p-6">
                <p className="text-[11px] tracking-[0.16em] text-gold uppercase mb-1">
                  Cordyceps militaris
                </p>
                <p className="text-sm text-ink-soft leading-relaxed">{hero.caption}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
