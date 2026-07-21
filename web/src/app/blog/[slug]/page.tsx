import Link from "next/link";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ArticleImage } from "@/components/ArticleImage";
import { getPost, getPostSlugs } from "@/lib/posts";
import { liquorNotice, siteConfig } from "@/lib/site-config";
import { coverForSlug } from "@/lib/visuals";

type Props = { params: Promise<{ slug: string }> };

export async function generateStaticParams() {
  return getPostSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  const post = getPost(slug);
  if (!post) return {};
  const cover = coverForSlug(slug);
  return {
    title: post.title,
    description: post.description,
    openGraph: {
      images: [{ url: cover.src, alt: cover.alt }],
    },
  };
}

export default async function BlogPostPage({ params }: Props) {
  const { slug } = await params;
  const post = getPost(slug);
  if (!post) notFound();

  const cover = coverForSlug(slug);

  return (
    <article>
      <div className="border-b border-line/70 bg-paper-deep/20">
        <div className="mx-auto max-w-4xl px-5 pt-12 pb-8">
          <p className="text-xs text-accent mb-4 tracking-wide uppercase">
            {post.category}
            {post.date ? ` · ${post.date}` : ""}
          </p>
          <h1 className="font-display text-3xl md:text-5xl leading-tight text-ink max-w-3xl">
            {post.title}
          </h1>
          <p className="mt-4 text-ink-soft leading-relaxed max-w-2xl">{post.description}</p>
        </div>
        <div className="mx-auto max-w-5xl px-5 pb-10">
          <ArticleImage
            src={cover.src}
            alt={cover.alt}
            caption={cover.caption}
            aspect="wide"
            priority
          />
        </div>
      </div>

      <div className="mx-auto max-w-3xl px-5 py-12">
        <div className="prose-qs">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{post.body}</ReactMarkdown>
        </div>
        <div className="mt-14 border-t border-line pt-6 space-y-4 text-sm text-ink-soft">
          <p className="text-[13px] leading-relaxed border border-line/70 bg-paper-deep/50 p-4 rounded-lg">
            {liquorNotice}
          </p>
          <p>
            편집: {siteConfig.author} ·{" "}
            <Link href="/editorial" className="underline hover:text-gold">
              편집 원칙
            </Link>
          </p>
          <p>
            <Link href="/blog" className="text-gold hover:underline">
              ← 이야기 목록
            </Link>
          </p>
        </div>
      </div>
    </article>
  );
}
