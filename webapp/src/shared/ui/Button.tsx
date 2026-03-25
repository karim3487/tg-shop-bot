"use client";

import { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
  fullWidth?: boolean;
}

export function Button({
  variant = "primary",
  fullWidth = false,
  className = "",
  children,
  disabled,
  ...props
}: ButtonProps) {
  const base =
    "inline-flex items-center justify-center rounded-xl px-4 py-3 text-[17px] font-semibold transition-all duration-200 active:scale-[0.98] active:opacity-80 disabled:cursor-not-allowed disabled:opacity-40 disabled:active:scale-100";

  const variants = {
    primary: "bg-tg-button text-tg-button-text",
    secondary:
      "bg-tg-secondary-bg text-tg-text border border-tg-hint/20",
  };

  return (
    <button
      disabled={disabled}
      className={`${base} ${variants[variant]} ${fullWidth ? "w-full" : ""} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
