"use client";

import { useEffect } from "react";
import { useTelegram } from "./provider";

export function useMainButton(
  label: string,
  onClick: () => void,
  enabled = true,
  isLoading = false,
) {
  const { twa } = useTelegram();

  useEffect(() => {
    if (!twa) return;
    const btn = twa.MainButton;

    btn.setText(label);
    btn.onClick(onClick);

    if (enabled) {
      btn.show();
      // isLoading: show native Telegram spinner and disable tap
      if (isLoading) {
        btn.showProgress(false); // false → button becomes non-tappable during progress
      } else {
        btn.hideProgress();
        btn.enable();
      }
    } else {
      btn.hideProgress();
      btn.hide();
      btn.disable();
    }

    return () => {
      btn.offClick(onClick);
      btn.hideProgress();
      btn.hide();
    };
  }, [twa, label, onClick, enabled, isLoading]);
}

export function useBackButton(onBack: () => void) {
  const { twa } = useTelegram();

  useEffect(() => {
    if (!twa) return;
    const btn = twa.BackButton;

    btn.show();
    btn.onClick(onBack);

    return () => {
      btn.offClick(onBack);
      btn.hide();
    };
  }, [twa, onBack]);
}

export function useTelegramUser() {
  const { twa } = useTelegram();
  return twa?.initDataUnsafe?.user ?? null;
}
