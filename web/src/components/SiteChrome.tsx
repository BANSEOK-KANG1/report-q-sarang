import Link from "next/link";
import { siteConfig, footerLegal, navItems, liquorNotice } from "@/lib/site-config";

export function SiteHeader() {
  return (
    <header className="border-b border-line/80 bg-paper/70 backdrop-blur sticky top-0 z-20">
      <nav className="mx-auto max-w-5xl px-5 h-16 flex items-center justify-between gap-4">
        <div className="shrink-0">
          <Link href="/" className="font-display font-bold tracking-tight text-xl text-ink leading-tight">
            {siteConfig.brandShort}
            <span className="text-accent"> · </span>
            <span className="text-gold">{siteConfig.brandSection}</span>
          </Link>
          <a
            href={siteConfig.parentUrl}
            className="block text-[10px] text-ink-soft hover:text-gold transition-colors mt-0.5"
          >
            ← {siteConfig.parentLabel}
          </a>
        </div>
        <div className="flex items-center gap-5 text-sm font-medium text-ink-soft">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className="hover:text-gold transition-colors">
              {item.label}
            </Link>
          ))}
        </div>
      </nav>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className="border-t border-line/80 mt-20 bg-paper-deep/60">
      <div className="mx-auto max-w-5xl px-5 py-10">
        <div className="grid gap-8 md:grid-cols-2">
          <div>
            <p className="font-display font-bold text-gold text-lg mb-2">{siteConfig.name}</p>
            <p className="text-xs text-ink-soft leading-relaxed max-w-md">{siteConfig.description}</p>
            <p className="text-xs text-ink-soft mt-3 leading-relaxed max-w-md">{liquorNotice}</p>
          </div>
          <div>
            <p className="font-display text-xs tracking-widest text-ink mb-3">정보</p>
            <ul className="flex flex-wrap gap-x-4 gap-y-2 text-xs text-ink-soft">
              {footerLegal.map((item) => (
                <li key={item.href}>
                  <Link href={item.href} className="hover:text-gold underline-offset-2 hover:underline">
                    {item.label}
                  </Link>
                </li>
              ))}
              <li>
                <a href={siteConfig.parentUrl} className="hover:text-gold underline-offset-2 hover:underline">
                  메인 사이트
                </a>
              </li>
            </ul>
            <p className="text-xs text-ink-soft mt-4">운영: {siteConfig.author}</p>
          </div>
        </div>
        <p className="mt-8 pt-6 border-t border-line/60 text-[11px] text-ink-soft">
          © {new Date().getFullYear()} {siteConfig.brandShort}.{" "}
          <a href={siteConfig.parentUrl} className="underline hover:text-gold">
            measuremkt.com
          </a>{" "}
          네트워크 · q-sarang.measuremkt.com
        </p>
      </div>
    </footer>
  );
}
