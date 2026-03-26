"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useClearCartMutation } from "@/entities/cart";
import { orderApi } from "@/entities/order";
import type { Order } from "@/entities/order";
import { ApiError } from "@/shared/api/client";
import { useTelegramUser, useHapticFeedback } from "@/shared/telegram/hooks";

// ─── Zod Schema ───────────────────────────────────────────────────────────────

const schema = z.object({
  full_name: z.string().min(2, "Введите полное имя"),
  address: z.string().min(5, "Введите адрес доставки"),
});

type FormValues = z.infer<typeof schema>;

// ─── Component ────────────────────────────────────────────────────────────────

interface CheckoutFormProps {
  onSuccess: (order: Order) => void;
  /** DOM id for the <form> — lets a parent trigger submit via requestSubmit() */
  formId?: string;
  /** Called whenever react-hook-form's isSubmitting flag changes */
  onSubmittingChange?: (submitting: boolean) => void;
}

export function CheckoutForm({ onSuccess, formId, onSubmittingChange }: CheckoutFormProps) {
  const queryClient = useQueryClient();
  const { mutateAsync: clearCart } = useClearCartMutation();
  const tgUser = useTelegramUser();
  const { notification } = useHapticFeedback();

  const {
    register,
    handleSubmit,
    setValue,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
  });

  const createOrderMutation = useMutation({
    mutationFn: (data: FormValues) => orderApi.createOrder(data),
    onSuccess: (order) => {
      notification("success");
      queryClient.invalidateQueries({ queryKey: ["cart"] });
      onSuccess(order);
    },
    onError: (err) => {
      notification("error");
      if (err instanceof ApiError) {
        if (err.status === 400) {
          mapDjangoErrors(err.body, setError);
          return;
        }
        if (err.status === 401 || err.status === 403) {
          setError("address", { message: "Сессия истекла. Пожалуйста, перезапустите приложение." });
          return;
        }
      }
      setError("address", { message: "Ошибка сервера. Попробуйте снова." });
    },
  });

  // Pre-populate full_name from the Telegram user profile
  useEffect(() => {
    if (!tgUser) return;
    const name = [tgUser.first_name, tgUser.last_name].filter(Boolean).join(" ");
    if (name) setValue("full_name", name);
  }, [tgUser, setValue]);

  useEffect(() => {
    onSubmittingChange?.(createOrderMutation.isPending || isSubmitting);
  }, [createOrderMutation.isPending, isSubmitting, onSubmittingChange]);

  const onSubmit = (data: FormValues) => {
    createOrderMutation.mutate(data);
  };

  return (
    <form id={formId} onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
      <Field label="Имя и фамилия" error={errors.full_name?.message}>
        <input
          {...register("full_name")}
          placeholder="Иван Иванов"
          autoComplete="name"
          className={inputCls(!!errors.full_name)}
        />
      </Field>

      <Field label="Адрес доставки" error={errors.address?.message}>
        <textarea
          {...register("address")}
          rows={3}
          placeholder="Город, улица, дом, квартира"
          autoComplete="street-address"
          className={inputCls(!!errors.address)}
        />
      </Field>
    </form>
  );
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function inputCls(hasError: boolean) {
  return [
    "w-full rounded-xl bg-tg-secondary-bg border py-3 px-4 text-[17px] text-tg-text outline-none transition-all duration-200 resize-none",
    "placeholder:text-tg-hint/60",
    hasError
      ? "border-red-500 bg-red-500/5 focus:border-red-500"
      : "border-transparent focus:border-tg-button focus:bg-tg-bg focus:ring-4 focus:ring-tg-button/10",
  ].join(" ");
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1.5 focus-within:text-tg-button transition-colors">
      <label className="text-[13px] font-semibold text-tg-hint uppercase tracking-wider pl-1">
        {label}
      </label>
      {children}
      {error && <p className="text-[13px] font-medium text-red-500 pl-1">{error}</p>}
    </div>
  );
}

/**
 * Maps Django REST Framework 400 field errors to react-hook-form.
 */
function mapDjangoErrors(
  body: string,
  setError: ReturnType<typeof useForm<FormValues>>["setError"],
) {
  let parsed: Record<string, string[]>;
  try {
    parsed = JSON.parse(body);
  } catch {
    return;
  }

  const fieldMap: Record<string, keyof FormValues> = {
    full_name: "full_name",
    address: "address",
  };

  for (const [djangoField, formField] of Object.entries(fieldMap)) {
    const messages = parsed[djangoField];
    if (messages?.length) {
      setError(formField, { message: messages[0] });
    }
  }

  const nonField = parsed["non_field_errors"] ?? parsed["detail"];
  if (nonField?.length) {
    setError("address", { message: String(nonField[0]) });
  }
}
