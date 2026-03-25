"use client";

import { useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { productApi, productKeys, ProductImageGallery } from "@/entities/product";
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

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-16">
        <Spinner size={32} />
      </div>
    );
  }

  if (isError || !product) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-tg-hint">
        <p className="text-[17px]">Продукт не найден</p>
      </div>
    );
  }

  // Adapt ProductDetail to ProductListItem shape required by AddToCartButton
  const productListItem: ProductListItem = {
    id: product.id,
    name: product.name,
    price: product.price,
    category: product.category.id,
    category_name: product.category.name,
    thumbnail: product.images[0] ?? null,
  };

  return (
    <div className="flex flex-col pb-24 bg-tg-bg min-h-screen">
      <ProductImageGallery images={product.images} productName={product.name} />
      <div className="p-4 space-y-4">
        <div className="flex items-start justify-between gap-3">
          <h1 className="text-2xl font-bold text-tg-text leading-tight tracking-tight">
            {product.name}
          </h1>
          <span className="text-xl font-bold text-tg-button whitespace-nowrap mt-0.5">
            {Number(product.price).toLocaleString("ru-RU", {
              style: "currency",
              currency: "RUB",
            })}
          </span>
        </div>
        {product.description && (
          <p className="text-[15px] text-tg-hint leading-relaxed">{product.description}</p>
        )}
        <div className="pt-2">
          <AddToCartButton product={productListItem} />
        </div>
      </div>
    </div>
  );
}
