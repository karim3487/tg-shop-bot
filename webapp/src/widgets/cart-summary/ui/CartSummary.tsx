"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { CartItemRow, useCartQuery, useAddToCartMutation, useRemoveFromCartMutation } from "@/entities/cart";
import { useMainButton, useBackButton } from "@/shared/telegram/hooks";
import { Spinner } from "@/shared/ui";

export function CartSummary() {
  const router = useRouter();
  const { data: cart, isLoading } = useCartQuery();
  const { mutate: addToCart } = useAddToCartMutation();
  const { mutate: removeFromCart } = useRemoveFromCartMutation();

  const items = cart?.items || [];
  const total = cart?.total || "0.00";

  const handleBack = useCallback(() => router.back(), [router]);
  const handleCheckout = useCallback(() => router.push("/checkout"), [router]);

  useBackButton(handleBack);
  useMainButton("Proceed to Checkout", handleCheckout, items.length > 0);

  const handleIncrement = useCallback(
    (itemId: number) => {
      const item = items.find((i) => i.id === itemId);
      if (!item) return;
      addToCart({ productId: item.product.id, quantity: item.quantity + 1, product: item.product });
    },
    [items, addToCart],
  );

  const handleDecrement = useCallback(
    (itemId: number) => {
      const item = items.find((i) => i.id === itemId);
      if (!item || item.quantity <= 1) return;
      addToCart({ productId: item.product.id, quantity: item.quantity - 1, product: item.product });
    },
    [items, addToCart],
  );

  const handleRemove = useCallback(
    (itemId: number) => {
      removeFromCart(itemId);
    },
    [removeFromCart],
  );

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-16">
        <Spinner size={32} />
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-tg-hint">
        <span className="text-5xl mb-4">🛒</span>
        <p className="text-[17px] font-medium text-tg-text">Корзина пуста</p>
        <p className="text-[15px] mt-1 text-tg-hint text-center max-w-[200px]">
          Добавьте товары из каталога, чтобы оформить заказ
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col pb-24 bg-tg-bg min-h-screen">
      <div className="flex flex-col mb-4">
        {items.map((item) => (
          <CartItemRow
            key={item.id}
            item={item}
            onIncrement={() => handleIncrement(item.id)}
            onDecrement={() => handleDecrement(item.id)}
            onRemove={() => handleRemove(item.id)}
          />
        ))}
      </div>
      <div className="flex items-center justify-between px-4 py-4 bg-tg-bg border-t border-tg-hint/20">
        <span className="text-[17px] font-medium text-tg-text">Итого</span>
        <span className="text-xl font-bold text-tg-text">
          {Number(total).toLocaleString("ru-RU", { style: "currency", currency: "RUB" })}
        </span>
      </div>
    </div>
  );
}
