import { siteConfig } from "@/lib/site-config";

export const metadata = { title: "문의" };

export default function ContactPage() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-14">
      <h1 className="font-display text-4xl text-gold mb-8">문의</h1>
      <p className="text-ink-soft leading-relaxed">
        이메일:{" "}
        <a href={`mailto:${siteConfig.contactEmail}`} className="text-gold underline">
          {siteConfig.contactEmail}
        </a>
      </p>
    </div>
  );
}
