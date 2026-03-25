import { request } from "@/shared/api/client";
import type { CreateOrderPayload, Order } from "../model/types";

export const orderApi = {
  createOrder(payload: CreateOrderPayload): Promise<Order> {
    return request<Order>("/orders/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  getOrders(): Promise<Order[]> {
    return request<Order[]>("/orders/");
  },

  getOrder(id: number): Promise<Order> {
    return request<Order>(`/orders/${id}/`);
  },

  markPaid(id: number): Promise<Order> {
    return request<Order>(`/orders/${id}/`, { method: "PATCH" });
  },
};
