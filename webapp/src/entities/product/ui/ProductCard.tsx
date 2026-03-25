"use client";

import Image from "next/image";
import type { ReactNode } from "react";
import type { ProductListItem } from "../model/types";

interface ProductCardProps {
  product: ProductListItem;
  /** Slot for AddToCartButton — keeps entity free of feature imports */
  actionSlot?: ReactNode;
  onClick?: () => void;
}

export function ProductCard({ product, actionSlot, onClick }: ProductCardProps) {
  return (
    <div
      className="flex flex-col h-full rounded-2xl overflow-hidden bg-[var(--tg-theme-bg-color,var(--tg-bg))] shadow-sm active:scale-[0.98] transition-all duration-200 border border-[var(--tg-theme-hint-color,var(--tg-hint))]/10"
      onClick={onClick}
    >
      <div className="relative w-full aspect-square bg-[var(--tg-theme-secondary-bg-color,var(--tg-secondary-bg,#f3f4f6))]">
        {product.thumbnail ? (
          <Image
            src={product.thumbnail.url}
            alt={product.name}
            fill
            unoptimized // MinIO URLs are served directly; skip Next.js proxy to avoid Docker networking issues
            className="object-cover absolute inset-0"
            sizes="(max-width: 640px) 50vw, 33vw"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-[var(--tg-theme-hint-color,var(--tg-hint))]">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <polyline points="21 15 16 10 5 21" />
            </svg>
          </div>
        )}
      </div>

      <div className="p-3.5 flex flex-col gap-1.5 flex-grow">
        <p className="text-sm font-medium text-[var(--tg-theme-text-color,var(--tg-text))] tracking-tight leading-snug line-clamp-2">
          {product.name}
        </p>
        <div className="mt-auto pt-1 flex flex-col gap-2">
          <p className="text-lg font-extrabold text-[var(--tg-theme-text-color,var(--tg-text))]">
            {Number(product.price).toLocaleString("ru-RU")} ₽
          </p>
          {actionSlot && (
            // Stop click from bubbling to the card's onClick
            <div onClick={(e) => e.stopPropagation()}>{actionSlot}</div>
          )}
        </div>
      </div>
    </div>
  );
}
