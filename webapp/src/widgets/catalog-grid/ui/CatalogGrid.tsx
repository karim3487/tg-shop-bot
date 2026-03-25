"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { productApi, productKeys, ProductCard } from "@/entities/product";
import { useCartQuery } from "@/entities/cart";
import { AddToCartButton } from "@/features/add-to-cart";
import { CategoryTabs } from "@/features/filter-by-category";
import { SearchBar } from "@/features/search-products";
import { useMainButton } from "@/shared/telegram/hooks";
import { Spinner } from "@/shared/ui";

export function CatalogGrid() {
  const router = useRouter();
  const { data: cart } = useCartQuery();
  const items = cart?.items || [];
  const total = cart?.total || "0.00";
  const [search, setSearch] = useState("");
  const [parentCategoryId, setParentCategoryId] = useState<number | null>(null);
  const [subCategoryId, setSubCategoryId] = useState<number | null>(null);

  const cartLabel = `View Cart (${Number(total).toLocaleString("ru-RU", { style: "currency", currency: "RUB" })})`;
  const handleViewCart = useCallback(() => router.push("/cart"), [router]);
  useMainButton(cartLabel, handleViewCart, items.length > 0);

  const effectiveCategoryId = subCategoryId ?? parentCategoryId;

  const { data: products = [], isLoading } = useQuery({
    queryKey: productKeys.list({
      search: search || undefined,
      category: effectiveCategoryId ?? undefined,
    }),
    queryFn: () =>
      productApi.getProducts({
        search: search || undefined,
        category: effectiveCategoryId ?? undefined,
      }),
    staleTime: 60_000,
  });

  return (
    <div className="flex flex-col min-h-full">
      <div className="sticky top-0 z-20 bg-[var(--tg-theme-bg-color,var(--tg-bg))]/85 backdrop-blur-md pt-3 pb-2 flex flex-col gap-2">
        <div className="px-4">
          <SearchBar onSearch={setSearch} />
        </div>
        <div className="-mx-1">
          <CategoryTabs
            selectedParentId={parentCategoryId}
            selectedSubId={subCategoryId}
            onSelectParent={setParentCategoryId}
            onSelectSub={setSubCategoryId}
          />
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center py-16 flex-grow">
          <Spinner size={32} />
        </div>
      ) : products.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-[var(--tg-theme-hint-color,var(--tg-hint))] flex-grow">
          <span className="text-4xl mb-3">🔍</span>
          <p className="text-sm">Ничего не найдено</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 p-4 pb-24 items-stretch auto-rows-fr">
          {products.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              actionSlot={<AddToCartButton product={product} />}
            />
          ))}
        </div>
      )}
    </div>
  );
}
