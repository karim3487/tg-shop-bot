"use client";

import Image from "next/image";
import { useState } from "react";
import type { ProductImage } from "../model/types";

interface ProductImageGalleryProps {
  images: ProductImage[];
  productName: string;
}

export function ProductImageGallery({ images, productName }: ProductImageGalleryProps) {
  const [current, setCurrent] = useState(0);

  const sorted = [...images].sort((a, b) => a.order - b.order);

  if (sorted.length === 0) {
    return (
      <div className="w-full aspect-square rounded-xl bg-[var(--tg-hint)]/10 flex items-center justify-center">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--tg-hint)" strokeWidth="1">
          <rect x="3" y="3" width="18" height="18" rx="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <polyline points="21 15 16 10 5 21" />
        </svg>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="relative w-full aspect-square rounded-xl overflow-hidden bg-[var(--tg-hint)]/10">
        <Image
          src={sorted[current].url}
          alt={`${productName} — фото ${current + 1}`}
          fill
          unoptimized // MinIO URLs are served directly; skip Next.js proxy to avoid Docker networking issues
          className="object-cover"
          sizes="100vw"
          priority={current === 0}
        />

        {sorted.length > 1 && (
          <>
            <button
              onClick={() => setCurrent((c) => Math.max(0, c - 1))}
              disabled={current === 0}
              aria-label="Предыдущее фото"
              className="absolute left-2 top-1/2 -translate-y-1/2 flex h-9 w-9 items-center justify-center rounded-full bg-black/40 text-white text-lg leading-none disabled:opacity-0 transition-opacity"
            >
              ‹
            </button>
            <button
              onClick={() => setCurrent((c) => Math.min(sorted.length - 1, c + 1))}
              disabled={current === sorted.length - 1}
              aria-label="Следующее фото"
              className="absolute right-2 top-1/2 -translate-y-1/2 flex h-9 w-9 items-center justify-center rounded-full bg-black/40 text-white text-lg leading-none disabled:opacity-0 transition-opacity"
            >
              ›
            </button>
          </>
        )}
      </div>

      {sorted.length > 1 && (
        <div className="flex justify-center gap-1.5">
          {sorted.map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrent(i)}
              aria-label={`Фото ${i + 1}`}
              className={`h-1.5 rounded-full transition-all duration-200 ${
                i === current
                  ? "w-5 bg-[var(--tg-button)]"
                  : "w-1.5 bg-[var(--tg-hint)]"
              }`}
            />
          ))}
        </div>
      )}
    </div>
  );
}
