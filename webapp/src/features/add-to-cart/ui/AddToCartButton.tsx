"use client";

import { useCallback } from "react";
import { useCartQuery, useAddToCartMutation, useRemoveFromCartMutation } from "@/entities/cart";
import { Button } from "@/shared/ui";
import type { ProductListItem } from "@/entities/product";

interface AddToCartButtonProps {
  product: ProductListItem;
}

export function AddToCartButton({ product }: AddToCartButtonProps) {
  const { data: cart } = useCartQuery();
  const { mutate: addToCart, isPending: isAdding } = useAddToCartMutation();
  const { mutate: removeFromCart, isPending: isRemoving } = useRemoveFromCartMutation();
  const isPending = isAdding || isRemoving;

  const cartItem = cart?.items.find((i) => i.product.id === product.id);
  const quantity = cartItem?.quantity ?? 0;

  const handleAdd = useCallback(() => {
    if (isPending) return;
    addToCart({ productId: product.id, quantity: quantity + 1, product });
  }, [isPending, addToCart, product, quantity]);

  const handleRemove = useCallback(() => {
    if (isPending || !cartItem) return;
    
    if (cartItem.quantity === 1) {
      removeFromCart(cartItem.id);
    } else {
      addToCart({ productId: product.id, quantity: quantity - 1, product });
    }
  }, [isPending, cartItem, removeFromCart, addToCart, product, quantity]);

  // When quantity is 0, show normal add to cart button
  if (quantity === 0) {
    return (
      <Button
        onClick={handleAdd}
        disabled={isPending}
        fullWidth
        className="text-sm py-2 rounded-full transition-transform active:scale-[0.98]"
      >
        {isPending ? "…" : "В корзину"}
      </Button>
    );
  }

  // Unified sleek pill container for adjusting quantity
  return (
    <div className="flex items-center justify-between rounded-full bg-[var(--tg-theme-button-color,var(--tg-button))]/10 px-1 py-1 mt-auto">
      {/* Minus Button */}
      <button
        onClick={handleRemove}
        disabled={isPending}
        aria-label="Уменьшить"
        className="flex h-7 w-7 items-center justify-center rounded-full text-[var(--tg-theme-button-color,var(--tg-button))] hover:bg-[var(--tg-theme-button-color,var(--tg-button))]/20 active:scale-[0.95] disabled:opacity-50 transition-all font-medium text-lg"
      >
        -
      </button>

      {/* Quantity Indicator */}
      <span className="text-sm font-semibold text-[var(--tg-theme-button-color,var(--tg-button))] px-2 min-w-[2rem] text-center">
        {quantity}
      </span>

      {/* Plus Button */}
      <button
        onClick={handleAdd}
        disabled={isPending}
        aria-label="Добавить"
        className="flex h-7 w-7 items-center justify-center rounded-full bg-[var(--tg-theme-button-color,var(--tg-button))] text-[var(--tg-theme-button-text-color,var(--tg-button-text))] active:scale-[0.95] disabled:opacity-50 transition-all font-medium text-lg leading-none"
      >
        +
      </button>
    </div>
  );
}
