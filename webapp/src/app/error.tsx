"use client";

import { useEffect } from "react";
import { ApiError } from "@/shared/api/client";

interface ErrorPageProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function GlobalError({ error, reset }: ErrorPageProps) {
  useEffect(() => {
    // Log to your observability stack — never crashes silently in prod
    console.error("[GlobalError]", error);
  }, [error]);

  const is401 = error instanceof ApiError && error.status === 401;

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-6 p-8 text-center bg-[var(--tg-bg)]">
      {is401 ? (
        <>
          <span className="text-5xl" aria-hidden>
            🔒
          </span>
          <h1 className="text-lg font-semibold text-[var(--tg-text)]">
            Откройте приложение в Telegram
          </h1>
          <p className="text-sm text-[var(--tg-hint)] max-w-xs">
            Это приложение работает только внутри Telegram. Перейдите по ссылке
            бота, чтобы открыть магазин.
          </p>
        </>
      ) : (
        <>
          <span className="text-5xl" aria-hidden>
            ⚠️
          </span>
          <h1 className="text-lg font-semibold text-[var(--tg-text)]">
            Что-то пошло не так
          </h1>
          <p className="text-sm text-[var(--tg-hint)] max-w-xs">
            Произошла непредвиденная ошибка. Попробуйте ещё раз.
          </p>
          <button
            onClick={reset}
            className="mt-2 px-6 py-2.5 rounded-xl text-sm font-medium
                       bg-[var(--tg-button)] text-[var(--tg-button-text)]
                       active:opacity-80 transition-opacity"
          >
            Попробовать снова
          </button>
        </>
      )}
    </div>
  );
}
