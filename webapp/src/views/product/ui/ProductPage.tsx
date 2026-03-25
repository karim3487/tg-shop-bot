"use client";

import { ProductDetail } from "@/widgets/product-detail";

interface ProductPageProps {
  productId: number;
}

export function ProductPage({ productId }: ProductPageProps) {
  return <ProductDetail productId={productId} />;
}
