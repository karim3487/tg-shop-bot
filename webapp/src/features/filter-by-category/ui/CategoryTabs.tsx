"use client";

import { useQuery } from "@tanstack/react-query";
import { productApi, productKeys } from "@/entities/product";
import { useHapticFeedback } from "@/shared/telegram/hooks";

interface CategoryTabsProps {
  selectedParentId: number | null;
  selectedSubId: number | null;
  onSelectParent: (id: number | null) => void;
  onSelectSub: (id: number | null) => void;
}

export function CategoryTabs({
  selectedParentId,
  selectedSubId,
  onSelectParent,
  onSelectSub,
}: CategoryTabsProps) {
  const { selectionChanged } = useHapticFeedback();

  const { data: categories = [], isLoading } = useQuery({
    queryKey: productKeys.categories(),
    queryFn: productApi.getCategories,
    staleTime: 5 * 60_000,
  });

  const selectedParent = categories.find((c) => c.id === selectedParentId);
  const subcategories = selectedParent?.children ?? [];

  if (isLoading) {
    return (
      <div className="flex gap-2.5 overflow-x-auto pb-2 pt-1 px-4 scrollbar-none">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="h-9 w-24 flex-shrink-0 rounded-full bg-[var(--tg-theme-hint-color,var(--tg-hint))]/20 animate-pulse"
          />
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-1">
      {/* Parent categories */}
      <div className="flex gap-2.5 overflow-x-auto pb-1 pt-1 px-4 scrollbar-none">
        <Tab
          label="Все"
          isActive={selectedParentId === null}
          onClick={() => {
            selectionChanged();
            onSelectParent(null);
            onSelectSub(null);
          }}
        />
        {categories.map((cat) => (
          <Tab
            key={cat.id}
            label={cat.name}
            isActive={selectedParentId === cat.id}
            onClick={() => {
              selectionChanged();
              onSelectParent(cat.id);
              onSelectSub(null);
            }}
          />
        ))}
      </div>

      {/* Subcategories row */}
      {subcategories.length > 0 && (
        <div className="flex gap-2 overflow-x-auto pb-2 px-4 scrollbar-none">
          {subcategories.map((sub) => (
            <SubTab
              key={sub.id}
              label={sub.name}
              isActive={selectedSubId === sub.id}
              onClick={() => {
                selectionChanged();
                onSelectSub(selectedSubId === sub.id ? null : sub.id);
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function Tab({
  label,
  isActive,
  onClick,
}: {
  label: string;
  isActive: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex-shrink-0 rounded-full px-5 py-2 text-sm font-medium transition-all active:scale-[0.96] ${
        isActive
          ? "bg-[var(--tg-theme-button-color,var(--tg-button))] text-[var(--tg-theme-button-text-color,var(--tg-button-text))] shadow-sm"
          : "bg-[var(--tg-theme-secondary-bg-color,var(--tg-secondary-bg,#f3f4f6))] text-[var(--tg-theme-text-color,var(--tg-text))] hover:bg-[var(--tg-theme-secondary-bg-color,var(--tg-secondary-bg,#e5e7eb))]/80 border border-[var(--tg-theme-hint-color,var(--tg-hint))]/5"
      }`}
    >
      {label}
    </button>
  );
}

function SubTab({
  label,
  isActive,
  onClick,
}: {
  label: string;
  isActive: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex-shrink-0 rounded-full px-4 py-1.5 text-xs font-medium transition-all active:scale-[0.96] ${
        isActive
          ? "bg-[var(--tg-theme-button-color,var(--tg-button))]/20 text-[var(--tg-theme-button-color,var(--tg-button))] border border-[var(--tg-theme-button-color,var(--tg-button))]/30"
          : "bg-[var(--tg-theme-secondary-bg-color,var(--tg-secondary-bg,#f3f4f6))]/60 text-[var(--tg-theme-hint-color,var(--tg-hint))] border border-[var(--tg-theme-hint-color,var(--tg-hint))]/15"
      }`}
    >
      {label}
    </button>
  );
}
