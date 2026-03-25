"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import type { TelegramWebApp } from "./types";

interface TelegramContextValue {
  twa: TelegramWebApp | null;
  isReady: boolean;
}

const TelegramContext = createContext<TelegramContextValue>({
  twa: null,
  isReady: false,
});

function applyTheme(params: TelegramWebApp["themeParams"]): void {
  const root = document.documentElement;
  // Fallback map in case the Telegram native client doesn't inject it automatically
  const map: Record<string, string | undefined> = {
    "--tg-theme-bg-color": params.bg_color,
    "--tg-theme-secondary-bg-color": params.secondary_bg_color,
    "--tg-theme-text-color": params.text_color,
    "--tg-theme-hint-color": params.hint_color,
    "--tg-theme-link-color": params.link_color,
    "--tg-theme-button-color": params.button_color,
    "--tg-theme-button-text-color": params.button_text_color,
  };
  for (const [key, value] of Object.entries(map)) {
    if (value) root.style.setProperty(key, value);
  }
}

export function TelegramProvider({ children }: { children: ReactNode }) {
  const [twa, setTwa] = useState<TelegramWebApp | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Safe: runs only after hydration on the client
    const webApp = window.Telegram?.WebApp ?? null;
    if (webApp) {
      webApp.ready();   // signals Telegram client to hide loading splash
      webApp.expand();  // full-height mode
      applyTheme(webApp.themeParams); // map to CSS variables
    }
    setTwa(webApp);
    setIsReady(true);
  }, []);

  return (
    <TelegramContext.Provider value={{ twa, isReady }}>
      {children}
    </TelegramContext.Provider>
  );
}

export const useTelegram = () => useContext(TelegramContext);
