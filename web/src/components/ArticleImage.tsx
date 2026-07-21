import Image from "next/image";
import { cn } from "@/lib/cn";

type Props = {
  src: string;
  alt: string;
  caption?: string;
  className?: string;
  priority?: boolean;
  aspect?: "video" | "wide" | "square" | "portrait";
};

const aspectClass = {
  video: "aspect-[16/10]",
  wide: "aspect-[21/9]",
  square: "aspect-square",
  portrait: "aspect-[3/4]",
};

export function ArticleImage({
  src,
  alt,
  caption,
  className,
  priority = false,
  aspect = "video",
}: Props) {
  return (
    <figure className={cn("group", className)}>
      <div
        className={cn(
          "relative overflow-hidden rounded-lg border border-line/80 bg-paper-deep",
          aspectClass[aspect]
        )}
      >
        <Image
          src={src}
          alt={alt}
          fill
          priority={priority}
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 960px"
          className="object-cover transition-transform duration-700 group-hover:scale-[1.03]"
        />
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-paper-deep/70 via-transparent to-transparent" />
      </div>
      {caption ? (
        <figcaption className="mt-3 text-xs leading-relaxed text-ink-soft">
          {caption}
        </figcaption>
      ) : null}
    </figure>
  );
}
