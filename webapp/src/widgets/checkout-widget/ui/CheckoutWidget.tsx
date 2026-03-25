"use client";

import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { CheckoutForm } from "@/features/place-order";
import { useBackButton, useMainButton } from "@/shared/telegram/hooks";
import { useTelegram } from "@/shared/telegram/provider";
import { orderApi } from "@/entities/order";
import type { Order } from "@/entities/order";

const FORM_ID = "checkout-form";

export function CheckoutWidget() {
  const router = useRouter();
  const { twa } = useTelegram();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isPaying, setIsPaying] = useState(false);
  const [order, setOrder] = useState<Order | null>(null);

  const handleBack = useCallback(() => router.back(), [router]);
  const handleClose = useCallback(() => {
    if (twa) twa.close();
    else router.push("/catalog");
  }, [twa, router]);

  const handlePaid = useCallback(async () => {
    if (!order) return;
    setIsPaying(true);
    try {
      await orderApi.markPaid(order.id);
    } finally {
      setIsPaying(false);
    }
    handleClose();
  }, [order, handleClose]);

  const triggerSubmit = useCallback(() => {
    const form = document.getElementById(FORM_ID) as HTMLFormElement | null;
    form?.requestSubmit();
  }, []);

  const handleOrderSuccess = useCallback((order: Order) => {
    setIsSubmitting(false);
    setOrder(order);
  }, []);

  // Payment stub screen: back button does nothing, main button closes the app
  useBackButton(order ? () => {} : handleBack);
  useMainButton(
    order ? "Я оплатил(а)" : "Place Order / Pay",
    order ? handlePaid : triggerSubmit,
    true,
    order ? isPaying : isSubmitting,
  );

  if (order) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] px-6 text-center gap-4">
        <span className="text-5xl">🧾</span>
        <h2 className="text-[20px] font-bold text-tg-text">
          Заказ #{order.id} оформлен
        </h2>
        <p className="text-[15px] text-tg-hint leading-relaxed">
          После оплаты нажмите кнопку ниже — мы получим уведомление и обработаем ваш заказ.
        </p>
        <div className="w-full rounded-2xl bg-tg-secondary-bg px-5 py-4 text-left">
          <p className="text-[13px] text-tg-hint uppercase font-semibold tracking-wider mb-1">
            Сумма к оплате
          </p>
          <p className="text-[28px] font-extrabold text-tg-text">
            {Number(order.total_price).toLocaleString("ru-RU", {
              style: "currency",
              currency: "RUB",
            })}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 pb-24">
      <CheckoutForm
        formId={FORM_ID}
        onSuccess={handleOrderSuccess}
        onSubmittingChange={setIsSubmitting}
      />
    </div>
  );
}
