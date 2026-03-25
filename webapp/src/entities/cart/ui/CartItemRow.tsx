"use client";

import Image from "next/image";
import { QuantityPicker } from "@/shared/ui";
import type { CartItem } from "../model/types";

interface CartItemRowProps {
  item: CartItem;
  /** Called when user clicks + */
  onIncrement: () => void;
  /** Called when user clicks − (parent decides whether to remove or decrement) */
  onDecrement: () => void;
  /** Called when user clicks the trash icon */
  onRemove: () => void;
}

export function CartItemRow({ item, onIncrement, onDecrement, onRemove }: CartItemRowProps) {
  return (
    <div className="flex gap-3 px-4 py-3 active:bg-black/5 dark:active:bg-white/5 transition-colors relative">
      {/* Thumbnail */}
      <div className="relative h-14 w-14 flex-shrink-0 rounded-xl overflow-hidden bg-tg-secondary-bg">
        {item.product.thumbnail ? (
          <Image
            src={item.product.thumbnail.url}
            alt={item.product.name}
            fill
            unoptimized
            className="object-cover"
            sizes="56px"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-tg-hint">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <polyline points="21 15 16 10 5 21" />
            </svg>
          </div>
        )}
      </div>

      {/* Info Container */}
      <div className="flex flex-1 flex-col justify-center min-w-0 border-b border-tg-hint/20 pb-3 -mb-3">
        <div className="flex items-start justify-between gap-2">
          <p className="text-[17px] -mt-1 font-medium text-tg-text line-clamp-2 leading-tight">
            {item.product.name}
          </p>
          <button
            onClick={onRemove}
            aria-label="Удалить товар"
            className="flex-shrink-0 p-1 text-tg-hint hover:text-red-500 transition-colors"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex items-center justify-between mt-2">
          <p className="text-[15px] font-semibold text-tg-text">
            {Number(item.product.price).toLocaleString("ru-RU")} ₽
          </p>
          <QuantityPicker
            value={item.quantity}
            onIncrement={onIncrement}
            onDecrement={onDecrement}
          />
          <p className="text-sm font-bold text-[var(--tg-text)]">
            {Number(item.subtotal).toLocaleString("ru-RU")} ₽
          </p>
        </div>
      </div>
    </div>
  );
}
