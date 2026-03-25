import type { ProductListItem } from "@/entities/product";

export interface CartItem {
  id: number;
  product: ProductListItem;
  product_id: number;
  quantity: number;
  subtotal: string;
}

export interface CartResponse {
  items: CartItem[];
  total: string;
}
