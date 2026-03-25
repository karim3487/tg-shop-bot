"use client";

import type { OrderStatus } from "../model/types";

interface OrderStatusBadgeProps {
  status: OrderStatus;
  /** Human-readable label from Django's status_display field */
  displayText: string;
}

const STATUS_STYLES: Record<OrderStatus, string> = {
  pending:    "bg-yellow-100 text-yellow-800",
  paid:       "bg-blue-100   text-blue-800",
  processing: "bg-purple-100 text-purple-800",
  shipped:    "bg-indigo-100 text-indigo-800",
  delivered:  "bg-green-100  text-green-800",
  cancelled:  "bg-red-100    text-red-800",
};

export function OrderStatusBadge({ status, displayText }: OrderStatusBadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLES[status]}`}
    >
      {displayText}
    </span>
  );
}
