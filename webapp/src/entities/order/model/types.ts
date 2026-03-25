export type OrderStatus =
  | "pending"
  | "paid"
  | "processing"
  | "shipped"
  | "delivered"
  | "cancelled";

export interface OrderItem {
  id: number;
  product_name: string;
  price: string;
  quantity: number;
  subtotal: string;
}

export interface Order {
  id: number;
  full_name: string;
  phone: string;
  address: string;
  status: OrderStatus;
  status_display: string;
  total_price: string;
  items: OrderItem[];
  created_at: string;
}

export interface CreateOrderPayload {
  full_name: string;
  phone?: string;
  address: string;
}
