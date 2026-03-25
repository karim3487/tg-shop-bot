// Skeleton shown by Next.js while the catalog route chunk + data loads.
export default function CatalogLoading() {
  return (
    <div className="flex flex-col gap-4 p-4 animate-pulse">
      {/* Category tabs row */}
      <div className="flex gap-2 overflow-hidden">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="h-8 rounded-full bg-[var(--tg-hint)]/20 shrink-0"
            style={{ width: `${60 + i * 10}px` }}
          />
        ))}
      </div>

      {/* Search bar */}
      <div className="h-10 rounded-xl bg-[var(--tg-hint)]/20" />

      {/* Product grid — 2 columns */}
      <div className="grid grid-cols-2 gap-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="flex flex-col gap-2">
            <div className="aspect-square rounded-xl bg-[var(--tg-hint)]/20" />
            <div className="h-4 rounded bg-[var(--tg-hint)]/20 w-3/4" />
            <div className="h-4 rounded bg-[var(--tg-hint)]/20 w-1/2" />
          </div>
        ))}
      </div>
    </div>
  );
}
