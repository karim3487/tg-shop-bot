import { request } from "@/shared/api/client";
import type { CartResponse } from "../model/types";

export const cartApi = {
  getCart(): Promise<CartResponse> {
    return request<CartResponse>("/cart/");
  },

  addItem(productId: number, quantity: number): Promise<CartResponse> {
    return request<CartResponse>("/cart/", {
      method: "POST",
      body: JSON.stringify({ product_id: productId, quantity }),
    });
  },

  removeItem(itemId: number): Promise<CartResponse> {
    return request<CartResponse>(`/cart/${itemId}/`, {
      method: "DELETE",
    });
  },

  clearCart(): Promise<void> {
    return request<void>("/cart/", {
      method: "DELETE",
    });
  },
};
