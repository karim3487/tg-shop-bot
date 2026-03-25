// Skeleton shown while the cart page loads.
export default function CartLoading() {
  return (
    <div className="flex flex-col gap-3 p-4 animate-pulse">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="flex gap-3 items-center">
          {/* Thumbnail */}
          <div className="w-16 h-16 rounded-xl bg-[var(--tg-hint)]/20 shrink-0" />
          <div className="flex flex-col gap-2 flex-1">
            {/* Product name */}
            <div className="h-4 rounded bg-[var(--tg-hint)]/20 w-3/4" />
            {/* Price */}
            <div className="h-4 rounded bg-[var(--tg-hint)]/20 w-1/3" />
          </div>
          {/* Quantity picker area */}
          <div className="w-24 h-8 rounded-xl bg-[var(--tg-hint)]/20 shrink-0" />
        </div>
      ))}

      {/* Divider + total */}
      <div className="h-px bg-[var(--tg-hint)]/20 mt-2" />
      <div className="flex justify-between">
        <div className="h-5 rounded bg-[var(--tg-hint)]/20 w-16" />
        <div className="h-5 rounded bg-[var(--tg-hint)]/20 w-24" />
      </div>
    </div>
  );
}
