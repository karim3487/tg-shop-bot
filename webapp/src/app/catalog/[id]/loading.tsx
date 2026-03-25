// Skeleton shown while the product detail page loads.
export default function ProductLoading() {
  return (
    <div className="flex flex-col animate-pulse">
      {/* Image gallery placeholder */}
      <div className="aspect-square w-full bg-[var(--tg-hint)]/20" />

      <div className="flex flex-col gap-3 p-4">
        {/* Title */}
        <div className="h-6 rounded bg-[var(--tg-hint)]/20 w-3/4" />
        {/* Price */}
        <div className="h-5 rounded bg-[var(--tg-hint)]/20 w-1/3" />

        {/* Description lines */}
        <div className="flex flex-col gap-2 mt-2">
          <div className="h-4 rounded bg-[var(--tg-hint)]/20 w-full" />
          <div className="h-4 rounded bg-[var(--tg-hint)]/20 w-5/6" />
          <div className="h-4 rounded bg-[var(--tg-hint)]/20 w-4/6" />
        </div>

        {/* Add-to-cart button area */}
        <div className="h-11 rounded-xl bg-[var(--tg-hint)]/20 mt-4" />
      </div>
    </div>
  );
}
