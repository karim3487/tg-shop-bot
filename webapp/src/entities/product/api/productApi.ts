import { request } from "@/shared/api/client";
import type {
  Category,
  ProductDetail,
  ProductFilters,
  ProductListItem,
} from "../model/types";

export const productKeys = {
  categories: () => ["categories"] as const,
  list: (filters: ProductFilters) => ["products", filters] as const,
  detail: (id: number) => ["products", id] as const,
  byCategory: (categoryId: number) =>
    ["products", "category", categoryId] as const,
};

export const productApi = {
  getCategories(): Promise<Category[]> {
    return request<Category[]>("/categories/");
  },

  getProducts(filters: ProductFilters = {}): Promise<ProductListItem[]> {
    const params = new URLSearchParams();
    if (filters.search) params.set("search", filters.search);
    if (filters.category != null)
      params.set("category", String(filters.category));
    const qs = params.toString();
    return request<ProductListItem[]>(`/products/${qs ? `?${qs}` : ""}`);
  },

  getProduct(id: number): Promise<ProductDetail> {
    return request<ProductDetail>(`/products/${id}/`);
  },

  getCategoryProducts(categoryId: number): Promise<ProductListItem[]> {
    return request<ProductListItem[]>(`/categories/${categoryId}/products/`);
  },
};
