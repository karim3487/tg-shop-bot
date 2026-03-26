"use client";

import { useCallback, useEffect } from "react";
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

type ImpactStyle = "light" | "medium" | "heavy" | "rigid" | "soft";
type NotificationType = "error" | "success" | "warning";

export function useHapticFeedback() {
  const { twa } = useTelegram();

  const impact = useCallback(
    (style: ImpactStyle = "medium") => {
      twa?.HapticFeedback?.impactOccurred(style);
    },
    [twa],
  );

  const notification = useCallback(
    (type: NotificationType) => {
      twa?.HapticFeedback?.notificationOccurred(type);
    },
    [twa],
  );

  const selectionChanged = useCallback(() => {
    twa?.HapticFeedback?.selectionChanged();
  }, [twa]);

  return { impact, notification, selectionChanged };
}
