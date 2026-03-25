"use client";

import { useState, useEffect, useRef } from "react";

interface SearchBarProps {
  /** Called with the debounced search string (300ms delay) */
  onSearch: (value: string) => void;
  placeholder?: string;
  initialValue?: string;
}

export function SearchBar({
  onSearch,
  placeholder = "Поиск товаров…",
  initialValue = "",
}: SearchBarProps) {
  const [value, setValue] = useState(initialValue);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    timerRef.current = setTimeout(() => {
      onSearch(value.trim());
    }, 300);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [value, onSearch]);

  return (
    <div className="relative w-full">
      <svg
        className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--tg-theme-hint-color,var(--tg-hint))] pointer-events-none"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
      >
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>

      <input
        type="search"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-2xl bg-[var(--tg-theme-secondary-bg-color,var(--tg-secondary-bg,#f3f4f6))] py-2.5 pl-10 pr-10 text-sm text-[var(--tg-theme-text-color,var(--tg-text))] placeholder:text-[var(--tg-theme-hint-color,var(--tg-hint))] outline-none shadow-sm focus:ring-2 focus:ring-[var(--tg-theme-button-color,var(--tg-button))]/60 transition-all duration-200"
      />

      {value && (
        <button
          onClick={() => setValue("")}
          aria-label="Очистить поиск"
          className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[var(--tg-theme-hint-color,var(--tg-hint))] hover:text-[var(--tg-theme-text-color,var(--tg-text))] transition-colors active:scale-90"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      )}
    </div>
  );
}
