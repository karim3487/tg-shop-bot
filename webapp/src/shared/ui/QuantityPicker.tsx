"use client";

interface QuantityPickerProps {
  value: number;
  onIncrement: () => void;
  onDecrement: () => void;
  min?: number;
  max?: number;
}

export function QuantityPicker({
  value,
  onIncrement,
  onDecrement,
  min = 1,
  max = 99,
}: QuantityPickerProps) {
  return (
    <div className="flex items-center gap-1 bg-tg-secondary-bg rounded-full p-1 border border-tg-hint/10">
      <button
        onClick={onDecrement}
        disabled={value <= min}
        aria-label="Decrease quantity"
        className="flex h-7 w-7 items-center justify-center rounded-full bg-white/5 text-tg-text transition-all active:scale-90 active:bg-tg-hint/20 disabled:cursor-not-allowed disabled:opacity-30 disabled:active:scale-100"
      >
        −
      </button>
      <span className="min-w-[2.5ch] text-center text-[15px] font-semibold text-tg-text">
        {value}
      </span>
      <button
        onClick={onIncrement}
        disabled={value >= max}
        aria-label="Increase quantity"
        className="flex h-7 w-7 items-center justify-center rounded-full bg-tg-button text-tg-button-text transition-all active:scale-90 active:opacity-80 disabled:cursor-not-allowed disabled:opacity-30 disabled:active:scale-100"
      >
        +
      </button>
    </div>
  );
}
