"use client";

import { useCallback, useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import useEmblaCarousel from "embla-carousel-react";
import Image from "next/image";
import { productApi, productKeys } from "@/entities/product";
import type { ProductListItem } from "@/entities/product";
import { AddToCartButton } from "@/features/add-to-cart";
import { useBackButton } from "@/shared/telegram/hooks";
import { Spinner } from "@/shared/ui";

interface ProductDetailProps {
  productId: number;
}

export function ProductDetail({ productId }: ProductDetailProps) {
  const router = useRouter();
  const handleBack = useCallback(() => router.back(), [router]);
  useBackButton(handleBack);

  const { data: product, isLoading, isError } = useQuery({
    queryKey: productKeys.detail(productId),
    queryFn: () => productApi.getProduct(productId),
    staleTime: 60_000,
  });

  const sorted = [...(product?.images ?? [])].sort((a, b) => a.order - b.order);

  const [emblaRef, emblaApi] = useEmblaCarousel({ loop: false });
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (!emblaApi) return;
    const onSelect = () => setCurrentIndex(emblaApi.selectedScrollSnap());
    emblaApi.on("select", onSelect);
    return () => { emblaApi.off("select", onSelect); };
  }, [emblaApi]);

  if (isLoading) {
    return (
      <div className="flex flex-col min-h-screen bg-tg-bg">
        {/* Skeleton image */}
        <div className="w-full aspect-square bg-tg-secondary-bg animate-pulse shrink-0" />
        {/* Skeleton content */}
        <div className="relative -mt-5 z-10 rounded-t-3xl bg-tg-bg flex-1 px-4 pt-6 space-y-4">
          <div className="h-5 w-24 rounded-full bg-tg-secondary-bg animate-pulse" />
          <div className="h-7 w-3/4 rounded-lg bg-tg-secondary-bg animate-pulse" />
          <div className="h-7 w-1/3 rounded-lg bg-tg-secondary-bg animate-pulse" />
          <div className="space-y-2 pt-2">
            <div className="h-4 w-full rounded bg-tg-secondary-bg animate-pulse" />
            <div className="h-4 w-5/6 rounded bg-tg-secondary-bg animate-pulse" />
            <div className="h-4 w-4/6 rounded bg-tg-secondary-bg animate-pulse" />
          </div>
        </div>
        <div className="flex justify-center pb-8">
          <Spinner size={24} />
        </div>
      </div>
    );
  }

  if (isError || !product) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-3 px-6 text-center">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-tg-hint">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        <p className="text-tg-hint text-[15px]">Товар не найден</p>
      </div>
    );
  }

  const productListItem: ProductListItem = {
    id: product.id,
    name: product.name,
    price: product.price,
    category: product.category.id,
    category_name: product.category.name,
    thumbnail: sorted[0] ?? null,
  };

  const formattedPrice = Number(product.price).toLocaleString("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0,
  });

  return (
    <div className="flex flex-col min-h-screen bg-tg-bg">

      {/* ── Carousel ─────────────────────────────────────────── */}
      <div className="relative w-full aspect-square bg-tg-secondary-bg shrink-0">
        {sorted.length > 0 ? (
          <>
            <div className="overflow-hidden h-full" ref={emblaRef}>
              <div className="flex h-full touch-pan-y">
                {sorted.map((img, i) => (
                  <div key={img.id} className="relative flex-[0_0_100%] h-full">
                    <Image
                      src={img.url}
                      alt={`${product.name} — фото ${i + 1}`}
                      fill
                      unoptimized
                      className="object-cover select-none"
                      sizes="100vw"
                      priority={i === 0}
                      draggable={false}
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Counter badge */}
            {sorted.length > 1 && (
              <div className="absolute top-3 right-3 bg-black/50 backdrop-blur-sm text-white text-xs font-semibold px-2.5 py-1 rounded-full tabular-nums pointer-events-none">
                {currentIndex + 1} / {sorted.length}
              </div>
            )}

            {/* Bottom gradient + dots */}
            {sorted.length > 1 && (
              <div className="absolute inset-x-0 bottom-0 h-16 flex items-end justify-center pb-3 bg-gradient-to-t from-black/30 to-transparent pointer-events-none">
                <div className="flex gap-1.5 pointer-events-auto">
                  {sorted.map((_, i) => (
                    <button
                      key={i}
                      onClick={() => emblaApi?.scrollTo(i)}
                      aria-label={`Фото ${i + 1}`}
                      className={`h-1.5 rounded-full transition-all duration-300 cursor-pointer ${
                        i === currentIndex ? "w-5 bg-white" : "w-1.5 bg-white/55"
                      }`}
                    />
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-tg-hint">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <polyline points="21 15 16 10 5 21" />
            </svg>
          </div>
        )}
      </div>

      {/* ── Content card ─────────────────────────────────────── */}
      <div className="relative -mt-5 z-10 rounded-t-3xl bg-tg-bg flex-1 flex flex-col">
        {/* Drag handle */}
        <div className="flex justify-center pt-3 pb-2">
          <div className="w-9 h-1 rounded-full bg-tg-hint/25" />
        </div>

        <div className="px-4 pt-1 pb-32 flex flex-col gap-4">

          {/* Category badge */}
          <div>
            <span className="inline-flex items-center text-xs font-semibold text-tg-button bg-tg-button/10 px-3 py-1 rounded-full">
              {product.category.name}
            </span>
          </div>

          {/* Name + Price */}
          <div className="flex items-start justify-between gap-4">
            <h1 className="text-[22px] font-bold text-tg-text leading-tight tracking-tight flex-1">
              {product.name}
            </h1>
            <div className="text-right shrink-0">
              <p className="text-[24px] font-extrabold text-tg-button leading-none">
                {formattedPrice}
              </p>
            </div>
          </div>

          {/* Divider */}
          {product.description && (
            <div className="h-px bg-tg-hint/10" />
          )}

          {/* Description */}
          {product.description && (
            <div className="space-y-2">
              <h2 className="text-[11px] font-bold text-tg-hint uppercase tracking-widest">
                Описание
              </h2>
              <p className="text-[15px] text-tg-text leading-[1.65]">
                {product.description}
              </p>
            </div>
          )}

        </div>
      </div>

      {/* ── Sticky CTA ───────────────────────────────────────── */}
      <div className="fixed bottom-0 left-0 right-0 z-20 px-4 pb-[max(1.5rem,env(safe-area-inset-bottom))] pt-3 bg-tg-bg/90 backdrop-blur-md border-t border-tg-hint/10">
        <AddToCartButton product={productListItem} />
      </div>
    </div>
  );
}
