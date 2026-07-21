import Link from "next/link";
import { ArticleImage } from "@/components/ArticleImage";
import { coverForSlug } from "@/lib/visuals";
import type { BlogPost } from "@/lib/posts";

type Props = {
  post: BlogPost;
  featured?: boolean;
};

export function PostCard({ post, featured = false }: Props) {
  const cover = coverForSlug(post.slug);

  if (featured) {
    return (
      <article className="grid gap-6 md:grid-cols-[1.1fr_1fr] md:gap-10 items-center border-b border-line/70 pb-10">
        <Link href={`/blog/${post.slug}`} className="block">
          <ArticleImage
            src={cover.src}
            alt={cover.alt}
            aspect="video"
            priority
            className="md:min-h-[280px]"
          />
        </Link>
        <div>
          <p className="text-xs tracking-[0.14em] text-accent mb-3 uppercase">
            {post.category}
            {post.date ? ` · ${post.date}` : ""}
          </p>
          <Link href={`/blog/${post.slug}`}>
            <h3 className="font-display text-3xl md:text-4xl leading-tight hover:text-gold transition-colors">
              {post.title}
            </h3>
          </Link>
          <p className="mt-4 text-ink-soft leading-relaxed">{post.description}</p>
          <Link
            href={`/blog/${post.slug}`}
            className="inline-block mt-5 text-sm font-medium text-gold hover:underline"
          >
            읽기 →
          </Link>
        </div>
      </article>
    );
  }

  return (
    <article className="grid gap-4 md:grid-cols-[220px_1fr] border-b border-line/70 pb-8">
      <Link href={`/blog/${post.slug}`} className="block">
        <ArticleImage src={cover.src} alt={cover.alt} aspect="square" />
      </Link>
      <div>
        <p className="text-xs text-accent mb-2 tracking-wide uppercase">
          {post.category}
          {post.date ? ` · ${post.date}` : ""}
        </p>
        <Link href={`/blog/${post.slug}`}>
          <h3 className="font-display text-xl md:text-2xl leading-snug hover:text-gold transition-colors">
            {post.title}
          </h3>
        </Link>
        <p className="mt-2 text-sm text-ink-soft leading-relaxed line-clamp-3">
          {post.description}
        </p>
        <Link
          href={`/blog/${post.slug}`}
          className="inline-block mt-3 text-sm text-gold hover:underline"
        >
          읽기 →
        </Link>
      </div>
    </article>
  );
}
