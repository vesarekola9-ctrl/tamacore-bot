import type { TamaUsableItem } from "./use-item";

export interface TamaCatalogItem extends TamaUsableItem {
  name?: string;
  description?: string;
  price?: number;
  tags?: string[];
}

export interface TamaCatalogLike {
  items?: TamaCatalogItem[];
  updatedAt?: number;
  [key: string]: unknown;
}

function cloneItem(item: TamaCatalogItem): TamaCatalogItem {
  return {
    ...item,
    changes: Array.isArray(item.changes)
      ? item.changes.map((change) => ({ ...change }))
      : [],
    timedEffects: Array.isArray(item.timedEffects)
      ? item.timedEffects.map((effect) => ({ ...effect }))
      : [],
    tags: Array.isArray(item.tags) ? [...item.tags] : [],
  };
}

function isValidItem(item: unknown): item is TamaCatalogItem {
  if (!item || typeof item !== "object") return false;
  const value = item as Record<string, unknown>;

  return (
    typeof value.id === "string" &&
    value.id.length > 0 &&
    (value.kind === "food" || value.kind === "cosmetic")
  );
}

export function ensureCatalog(target: TamaCatalogLike): TamaCatalogItem[] {
  if (!Array.isArray(target.items)) {
    target.items = [];
  }

  target.items = target.items.filter(isValidItem).map(cloneItem);
  return target.items;
}

export function registerCatalogItems(
  target: TamaCatalogLike,
  items: TamaCatalogItem[],
  now = Date.now(),
): TamaCatalogItem[] {
  const current = ensureCatalog(target).map(cloneItem);
  const byId = new Map<string, TamaCatalogItem>();

  for (const item of current) {
    byId.set(item.id, cloneItem(item));
  }

  for (const item of items) {
    if (!isValidItem(item)) continue;
    byId.set(item.id, cloneItem(item));
  }

  target.items = Array.from(byId.values());
  target.updatedAt = now;
  return target.items.map(cloneItem);
}

export function listCatalogItems(target: TamaCatalogLike): TamaCatalogItem[] {
  return ensureCatalog(target).map(cloneItem);
}

export function getCatalogItem(
  target: TamaCatalogLike,
  itemId: string,
): TamaCatalogItem | undefined {
  const item = ensureCatalog(target).find((entry) => entry.id === itemId);
  return item ? cloneItem(item) : undefined;
}

export function hasCatalogItem(target: TamaCatalogLike, itemId: string): boolean {
  return ensureCatalog(target).some((entry) => entry.id === itemId);
}
