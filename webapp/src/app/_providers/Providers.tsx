"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, ReactNode } from "react";
import { TelegramProvider } from "@/shared/telegram/provider";

export function Providers({ children }: { children: ReactNode }) {
  // useState ensures a new QueryClient is created per request in SSR,
  // not shared across users.
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // No SSR prefetching — all data requires client-side initData
            staleTime: 60_000,
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>
      <TelegramProvider>
          {children}
      </TelegramProvider>
    </QueryClientProvider>
  );
}
