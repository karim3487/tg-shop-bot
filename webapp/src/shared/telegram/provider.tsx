"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import type { WebApp, ThemeParams } from "telegram-web-app";

interface TelegramContextValue {
  twa: WebApp | null;
  isReady: boolean;
  themeParams: ThemeParams;
  viewportHeight: number;
}

const TelegramContext = createContext<TelegramContextValue>({
  twa: null,
  isReady: false,
  themeParams: {},
  viewportHeight: 0,
});

function applyTheme(params: ThemeParams): void {
  const root = document.documentElement;
  for (const [key, value] of Object.entries(params)) {
    if (value) root.style.setProperty(`--tg-theme-${key.replace(/_/g, "-")}`, value);
  }
}

export function TelegramProvider({ children }: { children: ReactNode }) {
  const [twa, setTwa] = useState<WebApp | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [themeParams, setThemeParams] = useState<ThemeParams>({});
  const [viewportHeight, setViewportHeight] = useState(0);

  useEffect(() => {
    // Safe: runs only after hydration on the client
    const webApp = window.Telegram?.WebApp ?? null;
    if (webApp) {
      webApp.ready();   // signals Telegram client to hide loading splash
      webApp.expand();  // full-height mode
      webApp.disableVerticalSwipes();
      applyTheme(webApp.themeParams);
      setThemeParams(webApp.themeParams);
      setViewportHeight(webApp.viewportStableHeight);
    }
    setTwa(webApp);
    setIsReady(true);
  }, []);

  useEffect(() => {
    if (!twa) return;

    const handleThemeChanged = () => {
      applyTheme(twa.themeParams);
      setThemeParams({ ...twa.themeParams });
    };

    const handleViewportChanged = ({ isStateStable }: { isStateStable: boolean }) => {
      if (isStateStable) setViewportHeight(twa.viewportStableHeight);
    };

    twa.onEvent("themeChanged", handleThemeChanged);
    twa.onEvent("viewportChanged", handleViewportChanged);

    return () => {
      twa.offEvent("themeChanged", handleThemeChanged);
      twa.offEvent("viewportChanged", handleViewportChanged);
    };
  }, [twa]);

  return (
    <TelegramContext.Provider value={{ twa, isReady, themeParams, viewportHeight }}>
      {children}
    </TelegramContext.Provider>
  );
}

export const useTelegram = () => useContext(TelegramContext);
